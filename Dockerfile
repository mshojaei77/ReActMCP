FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt

COPY servers ./servers

# Exa MCP server over stdio. Supply EXA_API_KEY at runtime.
ENTRYPOINT ["python", "servers/exa_web_search.py"]
