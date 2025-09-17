from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DB_URL,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    isolation_level="READ COMMITTED"
    )
SessionLocal = sessionmaker(bind=engine, future=True)

def init_db():
    with engine.begin() as conn:
        ddl = open("app/schemas.sql", "r", encoding="utf-8").read()
        for stmt in filter(None, map(str.strip, ddl.split(";"))):
            if stmt:
                conn.execute(text(stmt))