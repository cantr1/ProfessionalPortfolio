from db import create_task_db, complete_task_db, init_db, engine, get_task_db, fail_task_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Depends
from redis.asyncio import Redis
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Dict, Any
from deps import get_db
import os
import logging
import uuid
import json

load_dotenv()

redis_server = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
log_path = os.getenv("LOG_PATH")

app = FastAPI()

# Suppress repetitive watchfiles logs unless actual errors
logging.getLogger("watchfiles").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_path,
    filemode='a'
)


class TaskCreate(BaseModel):
    value: str


class TaskComplete(BaseModel):
    task_id: str
    output: Dict[str, Any]


@app.on_event("startup")
async def startup():
    global redis
    redis = Redis(host=redis_server,
                  port=redis_port,
                  decode_responses=True)
    await init_db(engine)

    logging.info("======== API Started ========")


@app.post("/create_task")
async def create_task(kv: TaskCreate, db: AsyncSession = Depends(get_db)):
    logging.info(f"Recieved Task - ({kv.value})")
    task_id = str(uuid.uuid4())
    logging.info(f"Generating Task ID# ({task_id})")
    task = {
        "id": task_id,
        "value": kv.value
    }
    logger.info("Adding task to SQL Database")
    await create_task_db(db, task['id'], task['value'])
    logger.info("Task logged to SQL database")
    logger.info("Adding task to Redis queue")
    await redis.rpush("task_queue", json.dumps(task))
    logger.info(f"Task Queued: {task['id']}: {task['value']}")
    return {"task_id": task["id"]}


@app.post("/task/next")
async def get_task():
    logging.info("Task Requested")
    task_json = await redis.lpop("task_queue")

    if task_json is None:
        logger.info("No active tasks found")
        return {"message": "no tasks"}

    task = json.loads(task_json)
    logger.info(f"Task Accepted - {task['id']}")

    return task


@app.get("/task/{task_id}")
async def get_data(task_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Database query for Task ID# = ({task_id})")
    task = await get_task_db(db, task_id)

    if not task:
        logger.warning("Task not found")
        return {"error": "task not found"}

    return task


@app.post("/complete_task")
async def complete_task(kv: TaskComplete, db: AsyncSession = Depends(get_db)):
    # Check for failure
    if "failed" in kv.output['test_status']:
        logger.warning(f"Task failed: {kv.task_id}")
        await fail_task_db(db, kv.task_id)
        return {"message": "Task marked as failed"}
    logging.info(f"Task reported complete: (ID#: {kv.task_id})")
    logger.info("Updating SQL database with completed task")
    await complete_task_db(db, kv.task_id, kv.output)
    logger.info("Task updated in SQL database")
    return {"message": "Task updated"}


@app.on_event("shutdown")
async def shutdown():
    await redis.close()
