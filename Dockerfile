FROM python:3.11-slim

# Install runtime libraries needed by pillow-heif (HEIC/HEIF image support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    libgomp1 \
    libde265-dev \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD sh -c "gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 300"