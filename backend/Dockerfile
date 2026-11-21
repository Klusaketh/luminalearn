# Multi-Stage Build for LuminaLearn AI FastAPI Backend
# Build context is the repository root: the backend imports the shared ai/ and ml/ packages.
#   docker build -f backend/Dockerfile -t luminalearn-backend .
FROM python:3.11-slim as builder

WORKDIR /srv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim as final

WORKDIR /srv/backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user (appuser UID 10001) for security compliance
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh appuser

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY backend /srv/backend
COPY ai /srv/ai
COPY ml /srv/ml
# The course catalog (content/) and its sync script, so a fresh database starts with every subject.
COPY content /srv/content
COPY scripts/seed_academic_content.py scripts/subject_content.py /srv/scripts/

RUN chown -R appuser:appgroup /srv
USER appuser

EXPOSE 8000

# Sync the catalog first (idempotent: it only creates or refreshes records), then serve.
CMD ["sh", "-c", "python /srv/scripts/seed_academic_content.py && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
