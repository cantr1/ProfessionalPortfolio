from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from pydantic import BaseModel
from dotenv import load_dotenv
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


class KV(BaseModel):
    key: str
    value: str


@app.on_event("startup")
async def startup():
    global redis
    redis = Redis(host=redis_server,
                  port=redis_port,
                  decode_responses=True)

    logging.info("======== API Started ========")


@app.post("/create_task")
async def create_task(kv: KV):
    if kv.key == "task":
        logging.info(f"Recieved Task - ({kv.value})")
        task_id = str(uuid.uuid4())
        logging.info(f"Generating Task ID# ({task_id})")
        task = {
            "id": task_id,
            "value": kv.value
        }
        await redis.rpush("task_queue", json.dumps(task))
        logger.info(f"Task Created: {task["id"]}: {task["value"]}")
        return {"task_id": task["id"]}


@app.get("/get_task")
async def get_task():
    logging.info("Task Requested")
    task_json = await redis.lpop("task_queue")

    if task_json is None:
        logger.info("No active tasks found")
        return {"message": "no tasks"}

    task = json.loads(task_json)
    logger.info(f"Task Accepted - {task['id']}")

    return task


@app.post("/complete_task")
async def complete_task(kv: KV):
    pass


@app.on_event("shutdown")
async def shutdown():
    await redis.close()
