import json
import os
from sqlmodel import SQLModel, Session
from database import engine, init_db
# Import all models to register them with SQLModel
from models import Application, ApplicationSymptom, ApplicationPurpose, ApplicationDependency

def seed_db():
    print("Initializing Database (enabling pgvector extension)...")
    init_db()

    print("Creating all tables via SQLModel...")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully.")

    seed_file_path = "../dummy_seed_data.json"
    if not os.path.exists(seed_file_path):
        print(f"Seed file not found at {seed_file_path}")
        return

    print("Seeding database from dummy_seed_data.json...")
    with Session(engine) as session:
        try:
            with open(seed_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. Seed applications
            for app_data in data.get("applications", []):
                # Using merge or checking existing to be safe
                existing = session.get(Application, app_data["id"])
                if not existing:
                    app = Application(
                        id=app_data["id"],
                        name=app_data["name"],
                        description=app_data["description"],
                        owning_team=app_data["owning_team"],
                        contact=app_data["contact"]
                    )
                    session.add(app)
            session.commit()
            print("Applications seeded.")

            # 2. Seed purposes
            for purp_data in data.get("application_purposes", []):
                purpose = ApplicationPurpose(
                    application_id=purp_data["application_id"],
                    purpose_text=purp_data["purpose_text"],
                    embedding=[0.0] * 1024
                )
                session.add(purpose)

            # 3. Seed symptoms
            for sym_data in data.get("application_symptoms", []):
                symptom = ApplicationSymptom(
                    application_id=sym_data["application_id"],
                    symptom_text=sym_data["symptom_text"],
                    embedding=[0.0] * 1024
                )
                session.add(symptom)

            # 4. Seed dependencies
            for dep_data in data.get("application_dependencies", []):
                dep = ApplicationDependency(
                    source_app_id=dep_data["source_app_id"],
                    dependent_app_id=dep_data["dependent_app_id"],
                    dependency_nature=dep_data["dependency_nature"]
                )
                session.add(dep)

            session.commit()
            print("Purposes, Symptoms, and Dependencies seeded successfully!")
        except Exception as e:
            session.rollback()
            print(f"Error during seeding: {e}")
            raise e

if __name__ == "__main__":
    seed_db()
