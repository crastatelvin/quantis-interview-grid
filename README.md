<div align="center">

# 🌌 QUANTIS INTERVIEW GRID

### Immersive AI Interview Simulation Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.x-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-3D_UI-black?style=for-the-badge&logo=three.js)](https://threejs.org/)
[![Groq](https://img.shields.io/badge/Groq-LLM_API-000000?style=for-the-badge)](https://groq.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge)](https://www.sqlalchemy.org/)

<br/>

> **Quantis Interview Grid** transforms a job description into a role-specific interview simulation with dynamic questions, voice interaction, structured scoring, rich performance analytics, and personalized preparation resources.

<br/>

![3D Interface](https://img.shields.io/badge/Immersive-3D%20Interview%20UI-blue?style=for-the-badge) ![Voice Mode](https://img.shields.io/badge/Voice-STT%20%2B%20TTS-purple?style=for-the-badge) ![Scoring Engine](https://img.shields.io/badge/Scoring-Structured%20Analytics-00b894?style=for-the-badge)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Application Preview](#-application-preview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Security Notes](#-security-notes)

---

## 🧠 Overview

Quantis is designed to feel like a real interview environment, not a static demo.

Core goals:
- Generate context-aware questions based on JD + interview type
- Support both typed and voice-assisted answer workflows
- Evaluate interview quality across weighted dimensions
- Produce actionable reports with metrics and preparation resources
- Persist user history for repeat practice and progress tracking

---

## 💻 Application Preview

> Screenshots are currently referenced from local workspace assets.  
> For GitHub rendering, place these images under `docs/screenshots/` and update paths.

<br/>
<br/>

<img width="1366" alt="Quantis Landing" src="C:\Users\Administrator\.cursor\projects\c-Users-Administrator-Desktop-New-folder\assets\c__Users_Administrator_AppData_Roaming_Cursor_User_workspaceStorage_735ba85a0b914dd8a8fa01d93bdb27c9_images_af318aa4-53f0-4c92-b61c-509b9a8dadea-889c58f6-76e9-4433-bb17-f13708af093d.png" />

<br/><br/>

<img width="1366" alt="Quantis Interview Screen" src="C:\Users\Administrator\.cursor\projects\c-Users-Administrator-Desktop-New-folder\assets\c__Users_Administrator_AppData_Roaming_Cursor_User_workspaceStorage_735ba85a0b914dd8a8fa01d93bdb27c9_images_22c49adf-2982-4e32-98e6-5058e15c32ae-2ba35784-fbb7-40f1-8b8b-f8d8522b0d9d.png" />

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Dynamic Role-Based Questions** | Uses JD analysis + interview type to generate realistic prompts |
| 🌌 **Immersive 3D UI** | Live Three.js scene, glass panels, animated score visuals |
| 🎙️ **Voice Interview Mode** | STT input, TTS question playback, live transcript capture |
| 📊 **Structured Scoring** | Relevance, clarity, depth, structure, confidence |
| 📄 **Final Report Intelligence** | Metrics, hiring likelihood, next steps, prep resources |
| 🔐 **Auth & History** | Register/login, stored runs, run detail retrieval |
| 📎 **Resume Gap Analysis** | Resume vs JD fit score, missing skills, action plan |
| 📈 **Observability** | Prometheus metrics endpoint + summary API |
| 🔄 **Resilient LLM Calls** | Retry/backoff + circuit breaker behavior for Groq calls |
| 🗄️ **Session Persistence** | DB-backed sessions with optional Redis cache fast-path |

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                 React 3D Interview UI                       │
│  setup • interview • report • auth/history • voice mode     │
└───────────────┬─────────────────────────────────────────────┘
                │ HTTP + Browser Voice APIs
┌───────────────▼─────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│                                                             │
│  /auth/*, /history*   identity + run history                │
│  /setup               JD analysis + question generation     │
│  /evaluate            answer capture (per-question)         │
│  /report              full scoring + final insights         │
│  /resume-gap-analysis resume/JD fit + action plan           │
│  /metrics             Prometheus scrape endpoint            │
│  /observability/*     request latency and error summaries   │
└───────────────┬─────────────────────────────────────────────┘
                │
      ┌─────────▼─────────┐          ┌────────────────────────┐
      │ SQLAlchemy (DB)   │          │ Groq API (LLM provider)│
      │ sessions/users/runs│         │ structured AI responses│
      └─────────┬─────────┘          └────────────────────────┘
                │
      ┌─────────▼─────────┐
      │ Redis Cache       │
      │ optional hot reads│
      └───────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Framer Motion, Recharts |
| 3D / Visuals | Three.js, `@react-three/fiber`, `@react-three/drei` |
| Backend | FastAPI, Pydantic, Uvicorn |
| AI | Groq (OpenAI-compatible API) |
| Persistence | SQLAlchemy + SQLite/Postgres |
| Cache | Redis (optional) |
| Auth | JWT (`PyJWT`), password hashing (`passlib`) |
| Observability | `prometheus-client` |
| Migrations | Alembic |
| Testing | Pytest |

---

## 📁 Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── db.py
│   │   ├── repositories/
│   │   └── services/
│   │       ├── ai_client.py
│   │       ├── interview_service.py
│   │       ├── auth_service.py
│   │       ├── history_service.py
│   │       └── cache.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   └── styles/
│   └── package.json
├── bootstrap.ps1
├── Makefile
└── README.md
```

---

## 🚀 Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- Groq API key

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic -c alembic.ini upgrade head
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

---

## 💻 Usage

1. Open `http://localhost:3000`
2. Select interview type + add JD text (or drop file)
3. Enter simulation and answer all questions
4. Generate report with metrics and prep guidance
5. Optional: sign in to save and review historical runs

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/auth/register` | Register account |
| POST | `/auth/login` | Login and receive JWT |
| GET | `/history` | List user interview runs |
| GET | `/history/{run_id}` | Detailed run data |
| POST | `/setup` | Create session + questions |
| POST | `/evaluate` | Record answer for a question |
| POST | `/report` | Compute final scored report |
| POST | `/resume-gap-analysis` | Resume/JD fit analysis |
| GET | `/metrics` | Prometheus metrics |
| GET | `/observability/summary` | Authenticated latency/error summary |

---

## ⚙️ Configuration

Set values in `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile
CORS_ORIGINS=http://localhost:3000
SESSION_TTL_MINUTES=120
DATABASE_URL=sqlite:///./quantis_interview_grid.db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=change_me_to_32_plus_chars
JWT_EXPIRE_HOURS=72
```

---

## 🧪 Testing

```bash
cd backend
python -m pytest tests

cd ../frontend
npm run build
```

---

## 🔒 Security Notes

- Use a strong `JWT_SECRET` (32+ chars) for production.
- Redis is optional; fallback works without it.

---

## 📜 License

This project is currently private/portfolio-oriented.  
Add your preferred open-source license (MIT/Apache-2.0) in `LICENSE` before broad public reuse.

---

<div align="center">

Built with ❤️ by [Crasta Telvin](https://github.com/crastatelvin)

⭐ Star this repo if you find it useful!

</div>

