# Scientific Data Platform — city generator (simulated city, Phase 0).
# Generates the fictional grid city into the dedicated `city-db` container.
FROM python:3.13-slim

WORKDIR /citygen

# Install dependencies first so rebuilds stay fast when code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (also bind-mounted during development via docker-compose.yml).
COPY . .

# One-shot, idempotent generator — overridden via:
#   docker compose run --rm citygen python generate.py ...
CMD ["python", "generate.py"]