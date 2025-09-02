# PhantomNet Deployment Tutorial

This comprehensive guide covers deploying the PhantomNet C2 application across different environments, from local development to production deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [VPS Deployment](#vps-deployment)
5. [Docker Deployment](#docker-deployment)
6. [SSL/HTTPS Setup](#sslhttps-setup)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended), Windows 10+, or macOS
- **Python**: 3.8+ (3.11+ recommended)
- **RAM**: Minimum 2GB, 4GB+ recommended
- **Storage**: 10GB+ available space
- **Network**: Stable internet connection for external deployments

### Required Software
- Python 3.8+
- pip (Python package manager)
- Git (for version control)
- Nginx (for production reverse proxy)
- Supervisor or systemd (for process management)

## Local Development Setup

### Step 1: Clone and Setup Project
```bash
# Clone the project (if using git)
git clone <your-repository-url>
cd phantomnet

# Or navigate to your project directory
cd /path/to/phantomnet
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Install additional development packages
pip install flask-debugtoolbar python-dotenv
```

### Step 4: Environment Configuration
Create a `.env` file in the project root:
```bash
# .env file
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///phantomnet.db
```

### Step 5: Initialize Database
```bash
# Run database initialization
python init_db.py
```

### Step 6: Start Development Server
```bash
# Start the Flask development server
python server.py
```

**Access URLs:**
- Main Application: http://localhost:8443
- Admin Panel: http://localhost:8443/admin/login
- Default Credentials: admin / admin123

## Production Deployment

### Step 1: Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3 python3-pip python3-venv nginx supervisor
```

### Step 2: Project Deployment
```bash
# Create application directory
sudo mkdir -p /opt/phantomnet
sudo chown $USER:$USER /opt/phantomnet

# Copy project files
cp -r * /opt/phantomnet/
cd /opt/phantomnet

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Step 3: Production Configuration
Create `/opt/phantomnet/config.py`:
```python
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-production-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////opt/phantomnet/phantomnet.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
```

### Step 4: Gunicorn Configuration
Create `/opt/phantomnet/gunicorn.conf.py`:
```python
# Gunicorn configuration
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

### Step 5: Supervisor Configuration
Create `/etc/supervisor/conf.d/phantomnet.conf`:
```ini
[program:phantomnet]
directory=/opt/phantomnet
command=/opt/phantomnet/venv/bin/gunicorn -c gunicorn.conf.py server:app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/phantomnet/app.log
stderr_logfile=/var/log/phantomnet/error.log
environment=PYTHONPATH="/opt/phantomnet"
```

### Step 6: Nginx Configuration
Create `/etc/nginx/sites-available/phantomnet`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Static files
    location /static/ {
        alias /opt/phantomnet/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Step 7: Enable and Start Services
```bash
# Create log directory
sudo mkdir -p /var/log/phantomnet
sudo chown www-data:www-data /var/log/phantomnet

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/phantomnet /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart services
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start phantomnet
```

## VPS Deployment

### Step 1: VPS Setup
```bash
# Connect to your VPS
ssh root@your-vps-ip

# Create non-root user
adduser phantomnet
usermod -aG sudo phantomnet

# Switch to new user
su - phantomnet
```

### Step 2: Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx supervisor ufw
```

### Step 3: Firewall Configuration
```bash
# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Step 4: Deploy Application
```bash
# Clone or upload project
cd /home/phantomnet
# Upload your project files here

# Create application directory
sudo mkdir -p /opt/phantomnet
sudo chown phantomnet:phantomnet /opt/phantomnet

# Copy files
cp -r * /opt/phantomnet/
cd /opt/phantomnet

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### Step 5: Database Setup
```bash
# Initialize database
python init_db.py

# Set proper permissions
sudo chown -R www-data:www-data /opt/phantomnet
sudo chmod -R 755 /opt/phantomnet
```

### Step 6: Service Configuration
Follow the same Supervisor and Nginx configuration steps from the Production Deployment section.

## Docker Deployment

### Step 1: Create Dockerfile
Create `Dockerfile` in the project root:
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 phantomnet && chown -R phantomnet:phantomnet /app
USER phantomnet

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "server:app"]
```

### Step 2: Create Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  phantomnet:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-production-secret-key
      - DATABASE_URL=sqlite:///data/phantomnet.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - phantomnet
    restart: unless-stopped
```

### Step 3: Build and Run
```bash
# Build and start services
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## SSL/HTTPS Setup

### Step 1: Install Certbot
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx
```

### Step 2: Obtain SSL Certificate
```bash
# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 3: Auto-renewal Setup
```bash
# Add to crontab
sudo crontab -e

# Add this line
0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring & Maintenance

### Step 1: Log Management
```bash
# View application logs
sudo tail -f /var/log/phantomnet/app.log

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View supervisor logs
sudo supervisorctl tail phantomnet
```

### Step 2: Performance Monitoring
```bash
# Check system resources
htop
df -h
free -h

# Check application status
sudo supervisorctl status phantomnet
sudo systemctl status nginx
```

### Step 3: Backup Strategy
```bash
# Create backup script
cat > /opt/phantomnet/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/phantomnet"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /opt/phantomnet/phantomnet.db $BACKUP_DIR/phantomnet_$DATE.db

# Backup application files
tar -czf $BACKUP_DIR/phantomnet_app_$DATE.tar.gz /opt/phantomnet

# Keep only last 7 backups
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

# Make executable and add to crontab
chmod +x /opt/phantomnet/backup.sh
echo "0 2 * * * /opt/phantomnet/backup.sh" | crontab -
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start
```bash
# Check logs
sudo supervisorctl tail phantomnet

# Check Python path
python3 -c "import sys; print(sys.path)"

# Verify virtual environment
source /opt/phantomnet/venv/bin/activate
python -c "from app import create_app; print('OK')"
```

#### 2. Database Connection Issues
```bash
# Check database file permissions
ls -la /opt/phantomnet/phantomnet.db

# Fix permissions if needed
sudo chown www-data:www-data /opt/phantomnet/phantomnet.db
sudo chmod 644 /opt/phantomnet/phantomnet.db
```

#### 3. Nginx Configuration Errors
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

#### 4. Port Already in Use
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Kill process if needed
sudo kill -9 <PID>
```

#### 5. Permission Denied Errors
```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/phantomnet

# Fix permissions
sudo chmod -R 755 /opt/phantomnet
sudo chmod 644 /opt/phantomnet/phantomnet.db
```

### Performance Optimization

#### 1. Gunicorn Tuning
```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = (2 * cpu_count()) + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

#### 2. Nginx Optimization
```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

## Security Considerations

### 1. Firewall Configuration
```bash
# Only allow necessary ports
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8000  # Don't expose Gunicorn directly
```

### 2. User Permissions
```bash
# Run application as non-root user
sudo useradd -r -s /bin/false phantomnet
sudo chown -R phantomnet:phantomnet /opt/phantomnet
```

### 3. Environment Variables
```bash
# Use environment variables for sensitive data
export SECRET_KEY="your-super-secret-key"
export DATABASE_URL="sqlite:////opt/phantomnet/phantomnet.db"
```

### 4. Regular Updates
```bash
# Update system packages regularly
sudo apt update && sudo apt upgrade -y

# Update Python packages
source /opt/phantomnet/venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Conclusion

This deployment tutorial covers the essential steps to deploy PhantomNet in various environments. Remember to:

1. **Always test in development first**
2. **Use strong, unique passwords**
3. **Keep systems updated**
4. **Monitor logs regularly**
5. **Implement proper backup strategies**
6. **Use HTTPS in production**
7. **Follow security best practices**

For additional support or questions, refer to the project documentation or create an issue in the project repository.

---

**Note**: This tutorial assumes a Linux environment. For Windows deployment, some commands and paths may need to be adjusted accordingly.
