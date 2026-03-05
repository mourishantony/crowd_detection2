FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD sh -c "gunicorn app:app --bind 0.0.0.0:${PORT:-5000}"