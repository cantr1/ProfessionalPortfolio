import asyncio
import aiohttp
import time
import json
from logging import Logger

async def check_target(session, target: dict, logger: Logger) -> None:
    """Send one async request and log result"""
    start = time.perf_counter()
    async with session.get(target["url"], timeout=5) as resp:
        latency = time.perf_counter() - start
        logger.info(f"{target['name']} responded {resp.status} in {latency:.2f}s")
        print(f"{target['name']} responded {resp.status} in {latency:.2f}s")
  

async def monitor_targets(config_file: str, logger: Logger) -> None:
    """Load hosts.json and run all checks concurrently"""
    with open(config_file, "r") as f:
        config = json.load(f)
    targets = config["targets"]

    logger.info(f"Starting multi-host test with {len(targets)} targets")

    async with aiohttp.ClientSession() as session:
        tasks = [check_target(session, t, logger) for t in targets]
        await asyncio.gather(*tasks)
    
    logger.info("Finished multi-host test")
