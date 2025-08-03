FROM python:3.11.5-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        python3-dev \
        python3-setuptools \
        tesseract-ocr \
        libgl1 \
        make \
        gcc \
        poppler-utils

RUN adduser --disabled-password --gecos "" user && \
    chown -R user:user /app
USER user

COPY . /app

EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port 8000