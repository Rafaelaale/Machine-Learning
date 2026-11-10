FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim AS final

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . /app/

EXPOSE 5000 5001 5002 5003

CMD ["python", "app.py"]
