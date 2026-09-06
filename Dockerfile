# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl ca-certificates unzip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# The default/public image must be buildable without private-repository
# credentials. Private Design-DNA remains optional and is installed only by a
# separate trusted build path that can supply a build-time secret without
# leaking it into image metadata or runtime environment variables.

COPY . .
RUN mkdir -p /app/data/users /app/data/shared \
    && python -m compileall -q core multimind_reflex ui utils database

# Persistence topology belongs to the deployment host rather than the generic
# image. /app/data remains available for the current SQLite/fallback runtime;
# a host may mount durable storage there when that deployment requires it.
EXPOSE 3000 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/_health', timeout=3).read()" || exit 1

CMD ["reflex", "run", "--env", "prod"]
