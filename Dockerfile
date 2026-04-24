FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Copy source
COPY . .

# Railway injects $PORT at runtime
CMD uvicorn backend_api:app --host 0.0.0.0 --port ${PORT:-8000}
