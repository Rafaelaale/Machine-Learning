FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --timeout 180 --retries 5 \
    pandas==2.2.3 \
    xgboost-cpu==3.2.0 \
    "scikit-learn>=1.5,<1.8" \
    kfp==2.15.0 \
    "pyarrow>=15,<16"

COPY src/ /app/src/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1