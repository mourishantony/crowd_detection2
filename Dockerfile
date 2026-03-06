FROM python:3.11-slim

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD sh -c "gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 300"