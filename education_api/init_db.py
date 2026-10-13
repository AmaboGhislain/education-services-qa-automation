
from education_api.database import Base, engine
from education_api import models  # Register the database models


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_db()