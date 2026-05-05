from sqlalchemy.orm import DeclarativeBase

from app.config import settings


DATABASE_URL = settings.database_url

class Base(DeclarativeBase):
    pass
