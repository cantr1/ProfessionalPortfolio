# 🌐 Professional Portfolio - Kelly Cantrell  

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 
![MQTT](https://img.shields.io/badge/MQTT-660066?style=for-the-badge&logo=eclipse-mosquitto&logoColor=white) 
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) 
![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=for-the-badge&logo=ansible&logoColor=white) 
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white) 
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)  

---

Welcome to my portfolio! 🚀  
This repository is where I showcase projects that highlight some of the cool things I've built in my spare time. I am always looking for opportunities to expand my knowledge, and programming has been something I have come to really enjoy. Software engineering can be incredibly complex, and I only now feel like I've started to get some real skills. As such, if you see anything that looks off, wrong, or just downright silly, please feel free to point it out.  

Right now, this portfolio is **under construction 🏗️**, but my goal is to build several projects that demonstrate my skills across coding, automation, and infrastructure.  

---

## Projects  

### 🪙 **Blockchain Emulator with MQTT Integration**  
- 🐍 Built in **Python**  
- 🔗 Simulates a blockchain with transaction & mining features  
- 📡 Uses **MQTT** for real-time blockchain updates  
- 💻 CLI app for flexible interaction with the chain  
- 🐳 Containerized applications

This project blends Python development, messaging systems, and containerization, showing my ability to work across both software and infrastructure layers.  

### 🔨 **Bash Anvil – Automated Server Deployment with Semaphore**  
- 🐚 Built with **Bash** for automation and testing  
- 📦 Integrated with **Semaphore** for CI/CD playbook deployment  
- 🔒 Includes **Linux hardening** and **audit checks**  
- 🧪 Features a custom **Bash testing framework** with color-coded results  
- ⚡ Automates **end-to-end server setup**, from dependencies to monitoring
- 🐍 Built a **Python** script to collect system data and report to **MQTT**     

This project demonstrates my ability to design repeatable infrastructure automation, blending  
scripting, orchestration, and security practices into a single workflow. 

### 🔨 **Go Helper – Server Monitoring with Go**  
- 🦫 Built with **Go** for write once, deploy everywhere 
- 📡 Integrated with **MQTT** for real time telemetry  
- 💻 **Nginx** interface showing status information  

This project highlights my ability to create tools, not just scripts. This is critical in any real DevOps / Engineering environment, as although scripts are a big part of software, tools are what make or break workflows.

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
