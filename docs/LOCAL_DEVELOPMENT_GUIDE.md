# LUMINALEARN AI — MASTER LOCAL DEVELOPMENT & DEPLOYMENT GUIDE

> **Project Aurora | Single Source of Truth (SSOT)**  
> **Document Version:** 1.0.0  
> **Classification:** Technical Handbook & Developer Onboarding Protocol  
> **Status:** Approved Baseline  

---

## 🏛️ Executive Summary & Setup Architecture

This document provides complete, step-by-step instructions to configure, run, test, and troubleshoot **LuminaLearn AI** (*Project Aurora*) from scratch on a new developer workstation. 

Following this guide allows a developer to clone the enterprise monorepo, set up environment variables, run PostgreSQL and Redis, launch the FastAPI microservice backend and Next.js 14 frontend, enable local Wi-Fi network access across mobile devices, and run the end-to-end verification test suite.

```
+---------------------------------------------------------------------------------------------------+
|                                LOCAL DEVELOPMENT ARCHITECTURE                                     |
|                                                                                                   |
|  [DEVELOPER / LOCAL DEVICE] (Browser: http://localhost:3000 | Wi-Fi: http://192.168.x.x:3000)     |
|           │                                                                                       |
|           ▼                                                                                       |
|  [NEXT.JS 14 FRONTEND] (React 18 / TypeScript / Tailwind CSS / Zustand) - Port 3000               |
|           │                                                                                       |
|           ▼  (HTTPS / REST APIs / WebSockets / OAuth2 Bearer Tokens)                               |
|  [FASTAPI BACKEND API] (Python 3.11+ / Async SQLAlchemy / Pydantic v2) - Port 8000               |
|           │                                                                                       |
|           ├─────────────────────────────────────────┐                                             |
|           ▼                                         ▼                                             |
|  [POSTGRESQL 16 DATABASE]                  [REDIS 7 CACHE & TOKEN STORE]                          |
|  (Port 5432: Users, Mastery, Onboarding)   (Port 6379: Sessions, Refresh Tokens, Password Resets) |
+---------------------------------------------------------------------------------------------------+
```

---

## 1. 🛠️ Software Prerequisites

Ensure your development machine has the following tools installed with compatible version locks:

| Software / Tool | Recommended Version | Minimum Version | Purpose |
| :--- | :---: | :---: | :--- |
| **Node.js** | `v20.12.x LTS` | `v18.17.x` | Next.js Frontend runtime engine |
| **npm** | `v10.5.x` | `v9.x` | JavaScript package manager |
| **Python** | `3.11.8` | `3.11.0` | FastAPI backend & domain evaluation engine |
| **PostgreSQL** | `16.2` | `15.0` | Relational database (ACID) |
| **Redis** | `7.2.x` | `6.2.x` | In-memory session cache & token store |
| **Docker Desktop**| `v26.0.0+` | `v24.0.0` | Multi-container dev orchestration |
| **Git** | `v2.44.0+` | `v2.30.0` | Version control system |
| **VS Code** | Latest | Latest | Primary IDE |

### Recommended VS Code Extensions
- **Python** (`ms-python.python`)
- **Pylance** (`ms-python.vscode-pylance`)
- **Ruff** (`charliermarsh.ruff`)
- **ESLint** (`dbaeumer.vscode-eslint`)
- **Prettier** (`esbenp.prettier-vscode`)
- **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`)

---

## 2. 🔐 Environment Variables Configuration

Central environment management is controlled via `.env` files.

### 2.1 Central `.env.example` Parameter Reference

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `"LuminaLearn AI"` | Official project branding |
| `ENVIRONMENT` | `"development"` | Environment state (`development` / `production`) |
| `DEBUG` | `true` | Enables FastAPI auto-reload and verbose logging |
| `BACKEND_HOST` | `"0.0.0.0"` | Listens on all IPv4 interfaces (allows local LAN access) |
| `BACKEND_PORT` | `8000` | FastAPI server port |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins for frontend requests |
| `SECRET_KEY` | `32+ Byte Key` | Cryptographic secret for signing JWT tokens |
| `ALGORITHM` | `"HS256"` | JWT HMAC hashing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token lifespan |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifespan |
| `POSTGRES_SERVER` | `"localhost"` | PostgreSQL hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | `"lumina_admin"` | Database username |
| `POSTGRES_PASSWORD` | `"lumina_dev_password_2026"` | Database user password |
| `POSTGRES_DB` | `"luminalearn_db"` | Primary database name |
| `REDIS_HOST` | `"localhost"` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |

---

### 2.2 Sample Local Configuration Files

#### **A. Backend Configuration (`backend/.env`)**
Create `backend/.env` in the root of the project:
```ini
PROJECT_NAME="LuminaLearn AI"
ENVIRONMENT="development"
DEBUG=true
LOG_LEVEL="DEBUG"

BACKEND_HOST="0.0.0.0"
BACKEND_PORT=8000
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://192.168.1.50:3000"]

SECRET_KEY="DEV_SUPER_SECRET_KEY_CHANGE_IN_PROD_MIN_32_BYTES"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

POSTGRES_SERVER="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="lumina_admin"
POSTGRES_PASSWORD="lumina_dev_password_2026"
POSTGRES_DB="luminalearn_db"

REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_PASSWORD=""
```

#### **B. Frontend Configuration (`frontend/.env.local`)**
Create `frontend/.env.local`:
```ini
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
```

---

## 3. 📦 Dependency Installation

### 3.1 Backend Setup (Python Virtual Environment)

1. Open terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a clean Python 3.11 virtual environment:
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

3. Upgrade `pip` and install all required dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### 3.2 Frontend Setup (Node.js & npm)

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node modules:
   ```bash
   npm install
   ```

---

## 4. 🗄️ Database Setup (PostgreSQL 16)

### Step 1: Create Database & User
Run the following SQL commands using `psql` or your database manager (pgAdmin, DBeaver):

```sql
-- Connect to PostgreSQL as superuser (postgres)
CREATE USER lumina_admin WITH PASSWORD 'lumina_dev_password_2026';
CREATE DATABASE luminalearn_db OWNER lumina_admin;
GRANT ALL PRIVILEGES ON DATABASE luminalearn_db TO lumina_admin;
```

### Step 2: Initialize DDL Schema
Apply the master schema from [`database/schema.sql`](file:///c:/Users/Sudar/OneDrive/Desktop/LUMINALEARN%20AI/database/schema.sql):

```bash
# Executing via psql command line:
psql -U lumina_admin -d luminalearn_db -h localhost -f database/schema.sql
```

### Step 3: Verify Schema Creation
Confirm all core tables have been instantiated:

```sql
\c luminalearn_db;
\dt

-- Expected Table Output:
--  1. users
--  2. knowledge_nodes
--  3. mastery_scores
--  4. learning_sessions
--  5. telemetry_logs
--  6. onboarding_profiles
```

---

## 5. 🔴 Redis Setup (In-Memory Session & Token Cache)

### 5.1 Starting Redis Service

- **macOS (Homebrew)**:
  ```bash
  brew services start redis
  ```
- **Linux (systemd)**:
  ```bash
  sudo systemctl start redis
  ```
- **Windows (Docker)**:
  ```bash
  docker run -d --name lumina-redis -p 6379:6379 redis:7-alpine
  ```

### 5.2 Testing Connection
Verify Redis is accepting connections:
```bash
redis-cli ping
# Output: PONG
```

---

## 6. 🐳 Docker & Docker Compose Setup

If you prefer to run the entire stack inside containers without installing local PostgreSQL or Redis:

### Launch Development Stack:
```bash
docker-compose -f docker/docker-compose.dev.yml up --build -d
```

### Useful Docker Management Commands:
- **View Container Logs**:
  ```bash
  docker-compose -f docker/docker-compose.dev.yml logs -f
  ```
- **Check Status**:
  ```bash
  docker-compose -f docker/docker-compose.dev.yml ps
  ```
- **Stop Stack**:
  ```bash
  docker-compose -f docker/docker-compose.dev.yml down
  ```

---

## 7. ⚡ Running the Backend Microservice

1. Activate your virtual environment inside `/backend`:
   ```bash
   cd backend
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   ```

2. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Expected Console Output**:
   ```
   INFO:     Will watch for changes in these directories: ['/path/to/LUMINALEARN AI/backend']
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process [PID] using StatReload
   INFO:     Application startup complete.
   ```

4. **Verification Links**:
   - **Health Endpoint**: `http://localhost:8000/api/v1/health`
   - **Swagger Interactive API Documentation**: `http://localhost:8000/docs`

---

## 8. 🎨 Running the Frontend Web App

1. Open terminal inside `/frontend`:
   ```bash
   cd frontend
   ```

2. Launch Next.js development server:
   ```bash
   npm run dev
   ```

3. **Expected Console Output**:
   ```
     ▲ Next.js 14.2.1
     - Local:        http://localhost:3000
     - Network:      http://0.0.0.0:3000

    ✓ Ready in 1.4s
   ```

4. Open your browser and navigate to `http://localhost:3000`.

---

## 9. 📱 Local Network Access (Wi-Fi & LAN Deployment)

You can access LuminaLearn AI from smartphones, tablets, or other laptops connected to the same Wi-Fi network.

### Step 1: Find Your Computer's Local IP Address
- **Windows (Command Prompt / PowerShell)**:
  ```cmd
  ipconfig
  # Look for "IPv4 Address", e.g., 192.168.1.50
  ```
- **macOS / Linux**:
  ```bash
  ifconfig | grep "inet "
  # Or: ip a
  ```

### Step 2: Configure Environment for LAN
Suppose your local IP is `192.168.1.50`:

1. Update `backend/.env`:
   ```ini
   BACKEND_CORS_ORIGINS=["http://localhost:3000","http://192.168.1.50:3000"]
   ```

2. Update `frontend/.env.local`:
   ```ini
   NEXT_PUBLIC_API_URL="http://192.168.1.50:8000/api/v1"
   ```

3. Start Frontend bound to all hosts:
   ```bash
   npm run dev -- -H 0.0.0.0
   ```

### Step 3: Access URLs from Any Device on the Network:
- **Mobile / Tablet Frontend URL**: `http://192.168.1.50:3000`
- **Backend API URL**: `http://192.168.1.50:8000/docs`

---

## 10. 🧪 Comprehensive End-to-End Testing Checklist

| Step | Feature / Component | Test Procedure | Expected Result | Pass / Fail |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Health Check** | Navigate to `http://localhost:8000/api/v1/health` | Returns status 200 with `"status": "healthy"` | `[ PASS ]` |
| 2 | **Database Integrity** | Execute `SELECT count(*) FROM users;` in PostgreSQL | Returns valid count without syntax error | `[ PASS ]` |
| 3 | **Redis Connectivity** | Run `redis-cli ping` | Returns `PONG` | `[ PASS ]` |
| 4 | **Student Register** | Register via `http://localhost:3000/register/student` | Creates user record with VARK preference | `[ PASS ]` |
| 5 | **Teacher Register** | Register via `http://localhost:3000/register/teacher` | Creates teacher user record in database | `[ PASS ]` |
| 6 | **Login & JWT** | Log in with registered email & password | Issues JWT Access & Refresh Tokens | `[ PASS ]` |
| 7 | **Forgot Password** | Submit email on `http://localhost:3000/forgot-password` | Generates reset token in Redis | `[ PASS ]` |
| 8 | **Onboarding Wizard** | Complete 7-step wizard on `http://localhost:3000/onboarding` | Saves onboarding choices in Postgres | `[ PASS ]` |
| 9 | **Diagnostic Quiz** | Complete 10 diagnostic assessment items | Evaluates score %, strengths & weak areas | `[ PASS ]` |
| 10 | **Roadmap View** | View profile & study targets summary page | Displays custom weekly study targets | `[ PASS ]` |
| 11 | **User Logout** | Click Logout or invoke `/api/v1/auth/logout` | Revokes refresh token & clears session | `[ PASS ]` |

---

## 11. 🚨 Common Errors & Troubleshooting Guide

### 1. Port 3000 or 8000 Already in Use
- **Symptom**: `Error: listen EADDRINUSE: address already in use :::3000` or `[Errno 98] Address already in use`.
- **Fix**: Identify and terminate the blocking process:
  - **Windows**:
    ```powershell
    netstat -ano | findstr :8000
    taskkill /PID <PID_NUMBER> /F
    ```
  - **macOS / Linux**:
    ```bash
    lsof -i :8000
    kill -9 <PID_NUMBER>
    ```

### 2. CORS Error (Blocked by CORS Policy)
- **Symptom**: Browser console error: `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`.
- **Fix**: Open `backend/app/core/config.py` or `backend/.env` and ensure `BACKEND_CORS_ORIGINS` includes your frontend origin URL (e.g., `["http://localhost:3000"]`). Restart Uvicorn.

### 3. PostgreSQL Connection Refused
- **Symptom**: `asyncpg.exceptions.CannotConnectNowError` or `ConnectionRefusedError`.
- **Fix**: Verify PostgreSQL service is active:
  ```bash
  pg_isready -h localhost -p 5432
  ```
  Check `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` credentials in `backend/.env`.

### 4. Redis Connection Error
- **Symptom**: `redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379`.
- **Fix**: Ensure Redis server is started (`redis-server` or `docker start lumina-redis`). Note that if Redis is offline during dev, AuthService handles session fallbacks gracefully.

### 5. `npm` or `python` Command Not Recognized (Windows)
- **Symptom**: `'npm' is not recognized as an internal or external command`.
- **Fix**: Ensure Node.js and Python are added to system `PATH` variables. Restart your terminal session after updating environment variables.

---

## 12. ✅ Final Operations Sign-Off Checklist

- [x] Master architecture and tech stack locked.
- [x] Single source of truth (SSOT) documentation up to date.
- [x] Database DDL schema verified (`database/schema.sql`).
- [x] Backend FastAPI microservice runnable with auto-reload.
- [x] Frontend Next.js 14 web client runnable.
- [x] Authentication Module fully verified (JWT, Argon2, Refresh Tokens).
- [x] Student Onboarding & 10-Question Diagnostic Assessment runnable.
- [x] Local Wi-Fi network cross-device access operational.
