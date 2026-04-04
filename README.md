# PerzAI

### One AI, Infinite Personas.

**A professional, RAG-powered Persona Engine built with a focus on modularity and precision control.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![HTMX](https://img.shields.io/badge/HTMX-3366CC?style=for-the-badge&logo=htmx&logoColor=white)](https://htmx.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

---

## 📊 Repository Analytics

## ✨ Features

- 🧠 **Multi-Persona RAG:** Build distinct AI entities, each with its own independent Knowledge Base.
- 📂 **Smart Ingestion:** Seamlessly upload and embed `.pdf`, `.docx`, `.xlsx`, and `.txt` documents.
- 🎛️ **Personality Cores:** Custom system prompts for every persona to define unique behavioral constraints.
- 🌿 **Botanical Professional UI:** A high-contrast, premium light-mode interface designed for long-term focus.
- ⚡ **Lightweight Power:** Built on a "No-Framework" frontend philosophy using **HTMX** for a reactive SPA feel without the JS bloat.

---

## 🚀 Quick Start

### 1. Setup Environment

Clone the repository and prepare your configuration:

```bash
git clone https://github.com/fuzail1011/PerzAI.git
cd PerzAI
cp .env.example .env
```

### Method A: Direct Execution (Virtual Environment)

Run the application directly on your local machine using the integrated launch script:

1. **Create and activate a virtual environment:**

   ```bash
   # Create venv inside the project folder
   python3 -m venv venv

   # Activate on MacOS/Linux
   source venv/bin/activate

   # Activate on Windows
   .\venv\Scripts\activate
   ```

2. **Install requirements:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   python launch.py
   ```

---

### Method B: Docker Deployment

Use Docker Compose for a fully isolated environment including the Database and Vector Store:

1. **Initial Build:**
   Run this command the first time to build images and start services:

   ```bash
   docker compose up --build
   ```

2. **Stopping the Application:**
   To stop the containers while keeping your data persistent:

   ```bash
   docker compose down
   ```

3. **Subsequent Starts:**
   After the initial build, you can simply start the app with:
   ```bash
   docker compose up
   ```
