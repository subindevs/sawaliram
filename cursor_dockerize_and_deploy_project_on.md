# Dockerize and deploy project on Ubuntu
_Exported on 7/22/2025 at 18:47:01 GMT+5:30 from Cursor (1.2.2)_

---

**User**

Take a look at all the files in the folder. I want to dockerize and run this project on my ubuntu linux server. Please create all necessary files and give me steps to deploy the app

---

**Cursor**

```pip-requirements
gunicorn
// ... existing code ...
```

```markdown
# Docker Deployment

## Prerequisites
- Docker and Docker Compose installed on your server
- PostgreSQL and RabbitMQ services (can be run as containers)

## Environment Variables
Set the following environment variables (replace values as needed):
- `sawaliram_secret_key`: Django secret key
- `sawaliram_debug_value`: True/False
- `sawaliram_db_password`: PostgreSQL password
- `GOOGLE_SITE_KEY`: Google Recaptcha site key
- `GOOGLE_SECRET_KEY`: Google Recaptcha secret key
- `google_secret_key_file`: Path to Google service account JSON (if used)

## Build and Run

1. Build the Docker image:
   ```sh
   docker-compose build
   ```
2. Run migrations and collect static files:
   ```sh
   docker-compose run web python manage.py migrate
   docker-compose run web python manage.py collectstatic --noinput
   ```
3. Start the app:
   ```sh
   docker-compose up
   ```

## Example Docker Compose
See `docker-compose.yml` for service definitions.

// ... existing code ...
```

```dockerfile
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

```

```dockercompose
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: sawaliram
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${sawaliram_db_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "15672:15672"
      - "5672:5672"
    restart: always

  web:
    build: .
    command: gunicorn core.wsgi --bind 0.0.0.0:8000 --log-file -
    volumes:
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
      - ./uploads:/app/uploads
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - rabbitmq
    restart: always

  celery:
    build: .
    command: celery -A core worker -l info
    volumes:
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
      - ./uploads:/app/uploads
    env_file:
      - .env
    depends_on:
      - db
      - rabbitmq
    restart: always

volumes:
  postgres_data:

```

### Dockerization Plan and Deployment Steps

#### 1. **Files Created/Modified**
- **Dockerfile**: For building the Django app image.
- **docker-compose.yml**: For orchestrating Django, Celery, PostgreSQL, and RabbitMQ.
- **requirements.txt**: Added `gunicorn` for production WSGI server.
- **README.md**: Added Docker deployment instructions.
- **.env**: (Template provided below, create this file manually)
- **Created directories**: `staticfiles`, `media`, `uploads` for persistent storage.

#### 2. **.env File Template**
Create a file named `.env` in your project root with the following content (replace values as needed):
```
sawaliram_secret_key=your-secret-key
sawaliram_debug_value=False
sawaliram_db_password=your-db-password
GOOGLE_SITE_KEY=your-google-site-key
GOOGLE_SECRET_KEY=your-google-secret-key
google_secret_key_file=/app/your-google-service-account.json
```

#### 3. **Deployment Steps on Ubuntu Linux Server**
1. **Copy your project to the server** (including the new/modified files).
2. **Create the `.env` file** as shown above.
3. **Ensure Docker and Docker Compose are installed**:
   ```sh
   sudo apt update
   sudo apt install docker.io docker-compose -y
   ```
4. **Build the Docker images**:
   ```sh
   docker-compose build
   ```
5. **Run database migrations and collect static files**:
   ```sh
   docker-compose run web python manage.py migrate
   docker-compose run web python manage.py collectstatic --noinput
   ```
6. **Start all services**:
   ```sh
   docker-compose up
   ```
7. **Access your app** at `http://your-server-ip:8000`

#### 4. **Notes**
- PostgreSQL and RabbitMQ are run as containers.
- Static, media, and uploads directories are persisted via Docker volumes.
- Celery worker is included for background tasks.
- You may want to secure your `.env` file and set up HTTPS for production.

If you need a production-ready Nginx reverse proxy or have custom domain/SSL requirements, let me know!

```plaintext
sawaliram_secret_key=your-secret-key
sawaliram_debug_value=False
sawaliram_db_password=your-db-password
GOOGLE_SITE_KEY=your-google-site-key
GOOGLE_SECRET_KEY=your-google-secret-key
google_secret_key_file=/app/your-google-service-account.json
```

```shellscript
   sudo apt update
   sudo apt install docker.io docker-compose -y
```

```shellscript
   docker-compose build
```

```shellscript
   docker-compose run web python manage.py migrate
   docker-compose run web python manage.py collectstatic --noinput
```

```shellscript
   docker-compose up
```

---

**User**

give nginx conf file for URL sawaliram.org

---

**Cursor**

Here is a production-ready Nginx configuration for your Django app running in Docker, with the domain `sawaliram.org`. This config:
- Proxies requests to your Django app running on port 8000 (as per your Docker Compose).
- Serves static and media files directly from the Docker volumes.
- Includes basic security headers.
- Is ready for SSL (see comments for certbot/Let's Encrypt).

---

**nginx.conf** (for `/etc/nginx/sites-available/sawaliram.org`):

```nginx
server {
    listen 80;
    server_name sawaliram.org www.sawaliram.org;

    # Redirect HTTP to HTTPS (uncomment after SSL setup)
    # return 301 https://$host$request_uri;

    # Path to your static and media files (adjust if needed)
    location /static/ {
        alias /path/to/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /media/ {
        alias /path/to/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /uploads/ {
        alias /path/to/uploads/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

---

### Instructions

1. **Replace paths**  
   Change `/path/to/staticfiles/`, `/path/to/media/`, and `/path/to/uploads/` to the actual absolute paths on your server where these Docker volumes are mounted (e.g., `/home/ubuntu/sawaliram/staticfiles/`).

2. **Enable the config**  
   - Save as `/etc/nginx/sites-available/sawaliram.org`
   - Link it:  
     `sudo ln -s /etc/nginx/sites-available/sawaliram.org /etc/nginx/sites-enabled/`
   - Test:  
     `sudo nginx -t`
   - Reload:  
     `sudo systemctl reload nginx`

3. **SSL (HTTPS) Setup**  
   - After DNS is set up and the site is live, use [Certbot](https://certbot.eff.org/) to get a free SSL certificate:
     ```
     sudo apt install certbot python3-certbot-nginx
     sudo certbot --nginx -d sawaliram.org -d www.sawaliram.org
     ```
   - Certbot will update your config for HTTPS.

---

Let me know if you need a version with HTTPS pre-configured, or if you want to reverse-proxy to a Docker network instead of localhost!

```plaintext
server {
    listen 80;
    server_name sawaliram.org www.sawaliram.org;

    # Redirect HTTP to HTTPS (uncomment after SSL setup)
    # return 301 https://$host$request_uri;

    # Path to your static and media files (adjust if needed)
    location /static/ {
        alias /path/to/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /media/ {
        alias /path/to/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /uploads/ {
        alias /path/to/uploads/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

```plaintext
     sudo apt install certbot python3-certbot-nginx
     sudo certbot --nginx -d sawaliram.org -d www.sawaliram.org
```

---

**User**

give me reverse proxy to docker instead

---

**Cursor**

Here is an Nginx configuration for reverse proxying to your Django app running in Docker, using the Docker Compose service name (`web`) instead of `localhost`. This is the recommended approach when Nginx is running on the same Docker network as your app (e.g., if you run Nginx as a container, or if you connect it to the same network).

---

**nginx.conf** (for `/etc/nginx/sites-available/sawaliram.org`):

```nginx
server {
    listen 80;
    server_name sawaliram.org www.sawaliram.org;

    # Redirect HTTP to HTTPS (uncomment after SSL setup)
    # return 301 https://$host$request_uri;

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /uploads/ {
        alias /app/uploads/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

---

### How to Use (Dockerized Nginx)

1. **Mount volumes**  
   - Make sure `/app/staticfiles/`, `/app/media/`, and `/app/uploads/` in the Nginx container are mounted to the same host directories as your Django container.
   - Example in `docker-compose.yml` for Nginx:
     ```yaml
     nginx:
       image: nginx:latest
       ports:
         - "80:80"
       volumes:
         - ./nginx.conf:/etc/nginx/conf.d/default.conf
         - ./staticfiles:/app/staticfiles
         - ./media:/app/media
         - ./uploads:/app/uploads
       depends_on:
         - web
       networks:
         - default
     ```

2. **Update proxy_pass**  
   - `proxy_pass http://web:8000;` uses the Docker Compose service name (`web`) and port (`8000`).

3. **Enable HTTPS**  
   - After DNS is set up, use Certbot in the Nginx container or on the host to enable SSL.

---

**If you want to run Nginx on the host (not in Docker):**
- Use the host's absolute paths for `alias` (e.g., `/home/ubuntu/sawaliram/staticfiles/`).
- Use `proxy_pass http://127.0.0.1:8000;` if you publish the Django port to the host.

Let me know if you want a full `docker-compose.yml` example including Nginx, or if you need HTTPS/SSL config!

```plaintext
server {
    listen 80;
    server_name sawaliram.org www.sawaliram.org;

    # Redirect HTTP to HTTPS (uncomment after SSL setup)
    # return 301 https://$host$request_uri;

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /uploads/ {
        alias /app/uploads/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

```yaml
     nginx:
       image: nginx:latest
       ports:
         - "80:80"
       volumes:
         - ./nginx.conf:/etc/nginx/conf.d/default.conf
         - ./staticfiles:/app/staticfiles
         - ./media:/app/media
         - ./uploads:/app/uploads
       depends_on:
         - web
       networks:
         - default
```

