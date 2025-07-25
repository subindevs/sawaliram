# syntax=docker/dockerfile:1
FROM python:3.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Create static, media, and uploads directories
RUN mkdir -p /app/staticfiles /app/media /app/uploads

# Collect static files (can also be run via docker-compose)
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "core.wsgi", "--bind", "0.0.0.0:8000", "--log-file", "-"] 