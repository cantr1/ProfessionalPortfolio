from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import select
from dotenv import load_dotenv
from models import Task
from base import Base
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


async def create_task_db(db: AsyncSession, task_id: str, input_value: str):
    task = Task(id=task_id, input=input_value, status="pending")
    db.add(task)
    await db.commit()


async def get_task_db(db: AsyncSession, task_id: str):
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    return result.scalar_one_or_none()


async def complete_task_db(db: AsyncSession, task_id: str, output_value: str):
    task = await get_task_db(db, task_id)
    if not task:
        return None

    task.output = output_value
    task.status = "completed"
    await db.commit()
    return task
