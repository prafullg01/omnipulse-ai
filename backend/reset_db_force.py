"""Reset and reseed the database without confirmation."""
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import Base, engine
from app.database.seed import seed_database

def reset_database():
    """Drop all tables and recreate them."""
    print("=" * 60)
    print("Dropping all tables...")
    print("=" * 60)
    Base.metadata.drop_all(bind=engine)
    
    print("\n" + "=" * 60)
    print("Creating all tables...")
    print("=" * 60)
    Base.metadata.create_all(bind=engine)
    
    print("\n" + "=" * 60)
    print("Database reset complete!")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("Seeding database with demo data...")
    print("=" * 60)
    seed_database()

if __name__ == "__main__":
    reset_database()
