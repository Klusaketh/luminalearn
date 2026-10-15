#!/usr/bin/env bg
# ==============================================================================
# LuminaLearn AI — Local Developer Environment Bootstrap Script
# ==============================================================================

set -e

echo "🚀 Bootstrapping LuminaLearn AI Developer Environment..."

# 1. Check for .env file
if [ ! -f .env ]; then
    echo "📋 Copying .env.example to .env..."
    cp .env.example .env
fi

# 2. Setup Backend Virtual Environment
echo "🐍 Setting up Python Virtual Environment in backend/..."
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate || source .venv/Scripts/activate
pip install poetry
poetry install
cd ..

# 3. Setup Frontend Node Modules
echo "📦 Installing Node dependencies in frontend/..."
cd frontend
npm install
cd ..

# 4. Launch Docker Stack
echo "🐳 Launching local Docker Compose infrastructure stack..."
docker-compose -f docker/docker-compose.dev.yml up -d --build

echo "✅ LuminaLearn AI environment successfully bootstrapped!"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000/docs"
