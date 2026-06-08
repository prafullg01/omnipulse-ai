"""Reset and reseed the database."""
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import Base, engine
from app.database.seed import seed_database

def reset_database():
    """Drop all tables and recreate them."""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete!")
    print("\nSeeding database with fresh data...")
    seed_database()

if __name__ == "__main__":
    confirm = input("This will DELETE all existing data. Continue? (yes/no): ")
    if confirm.lower() == "yes":
        reset_database()
    else:
        print("Cancelled.")
