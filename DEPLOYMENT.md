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

Wait for the web container to finish running migrations, creating user groups, and collecting static files:
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

---

## Database Backup and Restore

### Automate daily backups

Add this to your crontab (`crontab -e`) to back up every day at 2am and keep the last 30 days:

```bash
0 2 * * * cd /path/to/sawaliram && docker exec sawaliram-postgres-1 pg_dump -U admin sawaliram > backups/backup_$(date +\%Y\%m\%d).sql && find backups/ -name "*.sql" -mtime +30 -delete
```

Create the backups folder first:
```bash
mkdir -p /path/to/sawaliram/backups
```

### Create a backup (custom format — recommended for large databases)

```bash
docker exec sawaliram-postgres-1 pg_dump -U admin -Fc sawaliram > backup_$(date +%Y%m%d_%H%M%S).dump
```

The `-Fc` flag creates a compressed binary format that is smaller and restores faster than plain SQL.

### Restore from a backup

**On the same server:**
```bash
docker cp backup_20240417_143000.dump sawaliram-postgres-1:/tmp/backup.dump
docker exec sawaliram-postgres-1 pg_restore -U admin -d sawaliram -j 4 /tmp/backup.dump
docker exec sawaliram-postgres-1 rm /tmp/backup.dump
```

The `-j 4` flag runs 4 parallel restore jobs — increase this number on servers with more CPU cores.

**When migrating to a new server:**

1. Copy the backup file to the new server:
```bash
scp backup_20240417_143000.dump user@new-server:/path/to/sawaliram/
```

2. On the new server, start only the database first:
```bash
docker compose -f docker-compose.prod.yml up -d postgres
```

3. Wait a few seconds for Postgres to initialise, then restore:
```bash
docker cp backup_20240417_143000.dump sawaliram-postgres-1:/tmp/backup.dump
docker exec sawaliram-postgres-1 pg_restore -U admin -d sawaliram -j 4 /tmp/backup.dump
docker exec sawaliram-postgres-1 rm /tmp/backup.dump
```

4. Start the rest of the stack:
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Back up uploaded files

The submitted Excel files in the `uploads/` volume should also be backed up:

```bash
docker run --rm \
  -v sawaliram_uploads:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/uploads_$(date +%Y%m%d).tar.gz -C /data .
```

To restore uploads on a new server:
```bash
docker run --rm \
  -v sawaliram_uploads:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/uploads_20240417.tar.gz -C /data
```
