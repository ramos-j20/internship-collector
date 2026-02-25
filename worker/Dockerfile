FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (e.g., Playwright requirements if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# If Playwright is used, install browsers
RUN playwright install chromium --with-deps

COPY . .

CMD ["celery", "-A", "src.worker.app", "worker", "--loglevel=info"]
