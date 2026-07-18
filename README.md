# 🌐 Professional Portfolio - Kelly Cantrell  

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 
![MQTT](https://img.shields.io/badge/MQTT-660066?style=for-the-badge&logo=eclipse-mosquitto&logoColor=white) 
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) 
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white) 

---

Welcome to my portfolio! 🚀  
This repository is where I showcase projects that highlight some of the cool things I've built in my spare time. I am always looking for opportunities to expand my knowledge, and programming has been something I have come to really enjoy. Software engineering can be incredibly complex, and I only now feel like I've started to get some real skills. As such, if you see anything that looks off, wrong, or just downright silly, please feel free to point it out.  

Right now, this portfolio is **under construction 🏗️**, but my goal is to build several projects that demonstrate my skills across backend development, software design, testing, automation, and infrastructure.  

---

## Projects  

### 🔨 **ChessPy – Chess Movement Engine with Python**  
- 🐍 Built with **Python** and the standard `unittest` framework
- ♟️ Models chess movement rules for pawns, rooks, knights, bishops, queens, and kings
- 🧩 Uses the **Strategy design pattern** to separate piece behavior from board state
- 🧪 Includes focused tests for movement validation, board setup, path blocking, captures, and pawn rules
- 💻 Provides a simple terminal gameplay loop using chess-style coordinates

This project demonstrates my ability to use design patterns intentionally, not just academically. The goal was to practice separating domain behavior from stateful board operations while building a test suite around a rule-heavy problem space.

### 🔨 **Go Helper – Server Monitoring with Go**  
- 🦫 Built with **Go** for write once, deploy everywhere 
- 📡 Integrated with **MQTT** for real time telemetry  
- 💻 **Nginx** interface showing status information  

This project highlights my ability to create tools, not just scripts. This is critical in any real DevOps / Engineering environment, as although scripts are a big part of software, tools are what make or break workflows.

### 🔨 **FitByte – Fitness Tracker with Go and PostgreSQL**  
- 🦫 Built with **Go** using the standard `net/http` package
- 🗄️ Uses **PostgreSQL**, SQL migrations, and `sqlc` generated database code
- 🔐 Includes user creation, Argon2id password hashing, JWT access tokens, and refresh tokens
- 🌐 Serves a static web client for tracking sleep, exercise, and meditation sessions

This project demonstrates my ability to build a full-stack application with persistent data, authentication, and a small browser-based client. It also gave me practice designing backend workflows around tokens, database queries, and authenticated API routes.

### 🔨 **GoYoga – Yoga Class Booking App with Go and PostgreSQL**  
- 🦫 Built with **Go** using the standard `net/http` package
- 🗄️ Uses **PostgreSQL**, Goose-style migrations, and `sqlc` generated database code
- 🔐 Includes Argon2id password hashing, JWT access tokens, and database-backed refresh tokens
- 🧘 Supports student accounts, instructor accounts, class session creation, and class registration
- 🌐 Serves a plain HTML/CSS/JavaScript frontend for login, signup, calendar browsing, and registration

This project demonstrates my ability to model a real booking workflow across users, instructors, sessions, and registrations. It also gave me practice thinking through role-based authorization, domain rules, and how backend API design connects to a simple browser client.

### 🔨 **Task Forge – Distributed Task System with Python API**  
- 🐍 Built with Python + FastAPI for an async task API
- ⚡ Redis-backed FIFO queue for task dispatch
- 🗄️ PostgreSQL + SQLAlchemy (async) for durable task state
- 🧵 External worker processes poll, execute, and report results
- 📦 Tasks transition through pending → completed / failed states
- 🔁 Designed for horizontal scaling (multiple workers, multiple nodes)
- 🐳 Containerized with Docker / Docker Compose 

This project demonstrates my ability to build distributed systems, not just APIs. The goal of this project was to combine API's with databases to create a backend system similar to real world systems. As in the real world, I wanted to have the workers do something real, so I wrote a pretty simple web scraper to report data back to the API, which is then written to the SQL database.

---

## 💡 Notes  

- Each project will include **code**, **docs**, and (where possible) **containerized deployments**.   
