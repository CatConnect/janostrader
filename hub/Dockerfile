# ── Stage 1: build React frontend ────────────────────────────────────────────
FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
# output em /frontend/dist

# ── Stage 2: Python hub ───────────────────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app/hub

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY hub/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hub/ .
COPY --from=frontend /frontend/dist/ ./static/

EXPOSE 3000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
