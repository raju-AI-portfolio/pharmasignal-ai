from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment variable
# In local mode this points to our Docker PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pharma:localdev@localhost:5432/pharmasignal"
)

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Returns a database session.
    Used by FastAPI endpoints to get a DB connection.
    Always closes the session when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()