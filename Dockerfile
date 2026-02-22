FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends can-utils iproute2 && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY bridge/ bridge/

RUN pip install --no-cache-dir .

ENV CLAWARM_HOST=0.0.0.0
ENV CLAWARM_PORT=8420

EXPOSE 8420

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8420/')" || exit 1

CMD ["clawarm-bridge"]
