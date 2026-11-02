# Production image: one container serving the whole app (scripts/start.mjs, docs/DEPLOYMENT.md).
# Build context is the repository root:
#   docker build -t luminalearn .
FROM node:24-bookworm-slim AS web

WORKDIR /web

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
# NEXT_PUBLIC_* values are compiled into the browser bundle, so they must exist at build time.
ARG NEXT_PUBLIC_GOOGLE_CLIENT_ID=""
ENV NEXT_PUBLIC_GOOGLE_CLIENT_ID=$NEXT_PUBLIC_GOOGLE_CLIENT_ID
# The voice WebSocket rewrite is fixed at build time; the API runs beside the web server.
ENV BACKEND_URL=http://127.0.0.1:8001 \
    NEXT_OUTPUT=standalone \
    NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM python:3.11-slim-bookworm AS final

ENV ENVIRONMENT=production \
    DEBUG=false \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

WORKDIR /srv

COPY backend/requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt && rm requirements-prod.txt

# Create non-root user (appuser UID 10001) for security compliance
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh appuser

COPY --from=web /usr/local/bin/node /usr/local/bin/node
# Fails the build, not the deploy, if this base image lacks a library Node needs.
RUN node --version

COPY backend/app backend/app
COPY ai ai
COPY ml ml
COPY content content
COPY scripts/start.mjs scripts/seed_academic_content.py scripts/subject_content.py scripts/

# Compiled ahead of time so a free instance's slow CPU doesn't spend each wake-up on it.
RUN python -m compileall -q backend ai ml scripts

# The web server writes its cache under .next, so it owns its own directory.
COPY --from=web --chown=appuser:appgroup /web/.next/standalone frontend/
COPY --from=web --chown=appuser:appgroup /web/.next/static frontend/.next/static
COPY --from=web --chown=appuser:appgroup /web/public frontend/public

USER appuser

EXPOSE 10000

CMD ["node", "scripts/start.mjs"]
