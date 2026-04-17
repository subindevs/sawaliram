# Deployment Guide

## Prerequisites

- A Linux server (Ubuntu 22.04 recommended)
- Docker and Docker Compose installed
- Domain name pointing to the server's IP address
- Port 80 and 443 open on the firewall

### Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

---

## First-Time Deployment

### 1. Clone the repository

```bash
git clone https://github.com/sawaliram/sawaliram.git
cd sawaliram
git checkout deploy/production
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Edit `.env` and fill in all values:

```
DOMAIN=sawaliram.org
DJANGO_SECRET_KEY=<a long random string, at least 50 characters>
DJANGO_ENV=production
DB_PASSWORD=<a strong database password>
GOOGLE_SECRET_KEY=<reCAPTCHA secret key>
GOOGLE_SITE_KEY=<reCAPTCHA site key>
```

To generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3. Start the backend services

```bash
docker compose -f docker-compose.prod.yml up -d postgres rabbitmq memcached web
```

Wait for the web container to finish running migrations and collecting static files:
```bash
docker logs -f django-sawaliram-app
```

Wait until you see `Booting worker with pid` before continuing.

### 4. Obtain SSL certificate

```bash
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path /var/www/certbot \
  --email your@email.com \
  --agree-tos --no-eff-email \
  -d sawaliram.org -d www.sawaliram.org
```

### 5. Start Nginx

```bash
docker compose -f docker-compose.prod.yml up -d nginx
```

The site is now live at `https://sawaliram.org`.

### 6. Create an admin account

```bash
docker exec django-sawaliram-app python manage.py shell -c "
from sawaliram_auth.models import User
User.objects.create_superuser(email='your@email.com', password='yourpassword')
"
```

---

## Updating the Application

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build web
```

Nginx and the databases don't need to be restarted unless their configuration changed.

---

## Useful Commands

### View logs
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Web app only
docker logs -f django-sawaliram-app
```

### Restart the web app
```bash
docker compose -f docker-compose.prod.yml restart web
```

### Stop everything
```bash
docker compose -f docker-compose.prod.yml down
```

### Run a Django management command
```bash
docker exec django-sawaliram-app python manage.py <command>
```

### Access the database
```bash
docker exec -it sawaliram-postgres-1 psql -U admin -d sawaliram
```

---

## SSL Certificate Renewal

Certbot automatically renews certificates every 12 hours. To manually force a renewal:

```bash
docker compose -f docker-compose.prod.yml run --rm certbot renew
docker compose -f docker-compose.prod.yml restart nginx
```

---

## Data Persistence

All important data is stored in Docker named volumes and survives container restarts:

| Volume | Contents |
|---|---|
| `sawaliram_db` | PostgreSQL database |
| `sawaliram_uploads` | Submitted Excel files |
| `sawaliram_static` | Collected static files |
| `sawaliram_certbot_conf` | SSL certificates |

To back up the database:
```bash
docker exec sawaliram-postgres-1 pg_dump -U admin sawaliram > backup.sql
```

To restore:
```bash
cat backup.sql | docker exec -i sawaliram-postgres-1 psql -U admin -d sawaliram
```
