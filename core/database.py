from sqlmodel import create_engine, SQLModel

from core.config import settings

# The connect_args are needed for SQLite to allow multiple threads
# (which happens when using background tasks or multiple workers).
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    """
    Creates the database and all tables defined by SQLModel metadata.
    """
    print("Creating database and tables...")
    SQLModel.metadata.create_all(engine)
    print("Database and tables created successfully.")