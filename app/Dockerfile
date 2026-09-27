# Scientific Data Platform — Python app container
# Contains the USGS ingestion script and the Streamlit dashboard.
FROM python:3.13-slim

WORKDIR /app

# Install dependencies first so rebuilds stay fast when code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (also bind-mounted during development via docker-compose.yml).
COPY . .

EXPOSE 8501

# Default: run the dashboard. Override with:
#   docker compose run --rm app python ingest.py
CMD ["streamlit", "run", "dashboard.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]