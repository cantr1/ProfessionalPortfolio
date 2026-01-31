from fastapi import FastAPI
from redis.asyncio import Redis
from pydantic import BaseModel
import os

redis_server = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDDIS_PORT")

app = FastAPI()


class KV(BaseModel):
    key: str
    value: str


@app.on_event("startup")
async def startup():
    global redis
    redis = Redis(host=redis_server,
                  port=redis_port,
                  decode_responses=True)


@app.get("/")
async def root():
    """Just a way to quickly check API connectivity"""
    return {"message": "Hello, Python!"}


@app.post("/set")
async def set_key(kv: KV):
    await redis.set(kv.key, kv.value)
    return {"ok": True}

@app.get("/get/{key}")
async def get_key(kv: KV):
    value = await redis.get(kv.key)
    return {"value": value}


@app.on_event("shutdown")
async def shutdown():
    await redis.close()
