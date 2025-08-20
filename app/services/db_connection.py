from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.db_model import Base
from app.config.constants import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    Base.metadata.create_all(bind=engine)
