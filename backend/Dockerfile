FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# In case we haven't generated requirements.txt yet, we can create an empty one
RUN touch requirements.txt && pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Add execution permissions for the entrypoint script
RUN chmod +x /app/entrypoint.sh
