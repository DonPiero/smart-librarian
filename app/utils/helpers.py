from typing import Callable
from app.services.db_connection import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bots: dict[int, Callable] = {}

