from fastapi import FastAPI
import json
import asyncio
from async_monitor import monitor_targets
from logging import Logger

app = FastAPI(title="FastAPI_Project", description="Uptime monitor API")

@app.get("/status")
async def get_status():
    """Return the current status of all hosts from hosts.json"""
    with open("./hosts.json", "r") as f:
        config = json.load(f)
    return {"targets": config["targets"]}

@app.post("/run")
async def run_monitor():
    """Run an async check on all targets and return summary"""
    from main import generate_logger  # reuse existing logger
    logger: Logger = generate_logger()
    await monitor_targets("./hosts.json", logger)
    with open("./actions.log", "r") as f:
        logs = f.read().splitlines()
    return {"message": "Scan complete"}, logs
