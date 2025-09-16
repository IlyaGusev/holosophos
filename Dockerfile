FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY holosophos /app/holosophos
RUN pip install --no-cache-dir .

EXPOSE 5055
ENV PHOENIX_URL=http://phoenix:6006 \
    PHOENIX_PROJECT_NAME=holosophos \
    ACADEMIA_MCP_URL=http://academia:5056/mcp \
    CODEARKT_EXECUTOR_URL=http://executor:8000

CMD ["python", "-m", "holosophos.server", "--port", "5055"]
