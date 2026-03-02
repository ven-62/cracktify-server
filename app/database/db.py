from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from config import Config

# DATABASE CONFIGURATION
DB_HOST = Config.DB_HOST
DB_USER = Config.DB_USER
DB_PASSWORD = Config.DB_PASSWORD
DB_NAME = Config.DB_NAME
DB_PORT = Config.DB_PORT


def create_db_engine():
    """Try MySQL first, fallback to PostgreSQL if it fails"""

    # MySQL connection URL
    mysql_url = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # PostgreSQL connection URL
    postgres_url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    try:
        engine = create_engine(
            mysql_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
            future=True
        )
        # Force a real connection test
        with engine.connect():
            print("Connected to MySQL")
        return engine

    except SQLAlchemyError as e:
        print(f"MySQL connection failed: {e}")
        print("Falling back to PostgreSQL...")

        engine = create_engine(
            postgres_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
            future=True
        )

        # Test PostgreSQL connection
        with engine.connect():
            print("Connected to PostgreSQL")

        return engine


# Create engine
engine = create_db_engine()

# Session and Base
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    """Get a database session for FastAPI dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()