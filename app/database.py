from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = f"mysql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL) # this engine is used to establish a connection with mysql
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # this sessionmaker is used to talk with mysql (queries)

Base = declarative_base() # All the model classes will be extended with Base class, so that table can be created in database.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()