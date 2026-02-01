# Task Forge

**Task Forge** is a lightweight distributed task queue and worker system built from first principles using Python.  
It cleanly separates **task submission**, **task execution**, and **task persistence** into composable components.

Think *Celery-lite* — but explicit, understandable, and infrastructure-focused.

---

## 🧠 Architecture Overview

Task Forge is composed of four core parts:

1. **API Service (FastAPI)**
   - Accepts new tasks
   - Persists task metadata in PostgreSQL
   - Enqueues tasks in Redis (FIFO)

2. **Queue (Redis)**
   - Acts as a fast, ephemeral task broker
   - Ensures FIFO task delivery
   - No long-term state stored here

3. **Database (Postgres)**
    - Database acts as the source of truth
    - Track pass/failure of tasks
    - Allows for trend analysis

4. **Workers (Python processes)**
   - Poll Redis for tasks
   - Execute task logic (e.g. web scraping)
   - Report results back to the API
   - Update task state in PostgreSQL


---

## ✨ Features

- Async **FastAPI** backend  
- **Redis FIFO queue** using `RPUSH` / `LPOP`  
- **PostgreSQL** for durable task state  
- **Async SQLAlchemy** models and sessions  
- External **stateless workers**  
- Task lifecycle tracking:
  - `pending`
  - `completed`
  - `failed`
- Designed for **horizontal scaling**
- Fully containerized with **Docker Compose**

---

## 🧪 Example Task: Web Scraping Worker

Current worker implementation:
- Receives a URL as task input
- Fetches the page
- Extracts:
  - HTTP status code
  - Page title
  - Meta description (if present)
- Reports structured output back to the API
- Gracefully handles failures

---

## 📡 API Endpoints

### Create a Task
POST /create_task
```
{
  "value": "https://example.com"
}
```

### Fetch Next Task
POST /task/next
Returns:
```
{
  "id": "uuid",
  "value": "https://example.com"
}
```

### Complete a Task
POST /complete_task
```
{
  "task_id": "uuid",
  "output": {
    "status_code": 200,
    "title": "Example",
    "description": "..."
  }
}
```

### Query Task Status
GET /task/{task_id}


### 🐳 Running with Docker Compose
docker compose up --build


Services:

- api – FastAPI application
- redis – task queue
- postgres – persistent task store

Workers can run:

- On the same host
- On separate VMs
- In containers
- As systemd services

### 📌 Why This Project Exists

Task Forge demonstrates:

- Distributed system fundamentals

- Queue-based workloads

- Async Python

- Clean API / worker separation

This is not just a toy — it’s a deliberate, minimal system that mirrors patterns used in production task processors.