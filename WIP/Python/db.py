from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
                f"@{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_async_engine(
    DATABASE_URL,
    echo=False)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False)


async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Base(DeclarativeBase):
    pass
