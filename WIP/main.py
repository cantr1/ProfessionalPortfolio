from fastapi import FastAPI
from redis.asyncio import Redis
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging

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

    logging.info("==== API Started ====")


@app.get("/")
async def root():
    """Just a way to quickly check API connectivity"""
    logging.info("Connectivity Confirmed - API Accepting Requests")
    return {"message": "Hello, Python!"}


@app.post("/set")
async def set_key(kv: KV):
    await redis.set(kv.key, kv.value)
    logging.info(f"Set Method Called - ({kv.key}: {kv.value})")
    return {"ok": True}


@app.get("/get/{key}")
async def get_key(kv: KV):
    value = await redis.get(kv.key)
    logging.info(f"Get Method Called on ({kv.key}) - Returning {value})")
    return {"value": value}


@app.on_event("shutdown")
async def shutdown():
    await redis.close()
