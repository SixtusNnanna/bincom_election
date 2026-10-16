import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"ssl": "true"}
)

SESSIONLOCAL = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)


def get_db():
    db = SESSIONLOCAL()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    pass
