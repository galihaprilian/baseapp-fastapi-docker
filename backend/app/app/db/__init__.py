from sqlalchemy import create_engine, MetaData
from databases import Database

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
database = Database(settings.SQLALCHEMY_DATABASE_URI)
metadata = MetaData()
