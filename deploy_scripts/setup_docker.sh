#!/bin/bash

# PhantomNet Docker Deployment Script
# This script automates the Docker deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="phantomnet"
COMPOSE_FILE="docker-compose.yml"
DOMAIN_NAME="your-domain.com"  # Change this to your domain

echo -e "${GREEN}🐳 Starting PhantomNet Docker Deployment...${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    print_status "Install Docker with: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    print_status "Install Docker Compose with: sudo curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

print_status "Creating Dockerfile..."
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
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
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "sync", "server:app"]
EOF

print_status "Creating docker-compose.yml..."
cat > docker-compose.yml << EOF
version: '3.8'

services:
  phantomnet:
    build: .
    container_name: ${APP_NAME}-app
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./phantom.db:/app/phantomnet.db
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=$(openssl rand -hex 32)
      - DATABASE_URL=sqlite:///phantomnet.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - phantomnet-network

  nginx:
    image: nginx:alpine
    container_name: ${APP_NAME}-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      phantomnet:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - phantomnet-network

  redis:
    image: redis:alpine
    container_name: ${APP_NAME}-redis
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
    restart: unless-stopped
    networks:
      - phantomnet-network

networks:
  phantomnet-network:
    driver: bridge

volumes:
  phantomnet-data:
EOF

print_status "Creating Nginx configuration..."
mkdir -p nginx
cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};
        
        # Redirect all HTTP traffic to HTTPS
        return 301 https://\$server_name\$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};

        # SSL Configuration (will be updated by Certbot)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin";

        # Rate limiting for login
        location /admin/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://phantomnet:8000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Rate limiting for API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://phantomnet:8000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Main application
        location / {
            proxy_pass http://phantomnet:8000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_redirect off;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Static files
        location /static/ {
            proxy_pass http://phantomnet:8000;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Health check endpoint
        location /health {
            proxy_pass http://phantomnet:8000;
            access_log off;
        }
    }
}
EOF

print_status "Creating directories..."
mkdir -p data logs/nginx ssl

print_status "Creating .dockerignore file..."
cat > .dockerignore << 'EOF'
.git
.gitignore
README.md
DEPLOYMENT_TUTORIAL.md
deploy_scripts/
*.pyc
__pycache__/
.env
.venv/
venv/
*.log
data/
logs/
ssl/
nginx/
docker-compose.yml
Dockerfile
.dockerignore
EOF

print_status "Creating environment file..."
cat > .env << EOF
# PhantomNet Environment Variables
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///phantomnet.db
REDIS_URL=redis://redis:6379/0

# Domain configuration
DOMAIN_NAME=${DOMAIN_NAME}

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
EOF

print_status "Creating health check endpoint..."
cat > health_check.py << 'EOF'
from flask import Flask, jsonify
import sqlite3
import os
import redis
import json

app = Flask(__name__)

def check_database():
    try:
        conn = sqlite3.connect('phantomnet.db')
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        return True
    except Exception as e:
        return False

def check_redis():
    try:
        r = redis.Redis(host='redis', port=6379, db=0)
        r.ping()
        return True
    except Exception as e:
        return False

@app.route('/health')
def health():
    db_status = check_database()
    redis_status = check_redis()
    
    status = 'healthy' if db_status and redis_status else 'unhealthy'
    
    return jsonify({
        'status': status,
        'service': 'phantomnet',
        'database': 'healthy' if db_status else 'unhealthy',
        'redis': 'healthy' if redis_status else 'unhealthy',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF

print_status "Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Creating backup: $DATE"

# Backup database
if [ -f "data/phantomnet.db" ]; then
    cp data/phantomnet.db $BACKUP_DIR/phantomnet_$DATE.db
    echo "Database backed up"
fi

# Backup application data
tar -czf $BACKUP_DIR/phantomnet_data_$DATE.tar.gz data/ logs/ ssl/ 2>/dev/null || true
echo "Application data backed up"

# Backup Docker images
docker save phantomnet_phantomnet:latest -o $BACKUP_DIR/phantomnet_image_$DATE.tar
echo "Docker image backed up"

# Keep only last 7 backups
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar" -mtime +7 -delete

echo "Backup completed: $DATE"
echo "Backup location: $BACKUP_DIR"
EOF

chmod +x backup.sh

print_status "Creating monitoring script..."
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "=== PhantomNet Docker Monitoring ==="
echo ""

echo "Container Status:"
docker-compose ps
echo ""

echo "Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
echo ""

echo "Recent Logs (last 10 lines):"
docker-compose logs --tail=10 phantomnet
echo ""

echo "Health Check:"
curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Health check failed"
echo ""

echo "Disk Usage:"
df -h | grep -E "(Filesystem|/dev/)"
echo ""

echo "Memory Usage:"
free -h
EOF

chmod +x monitor.sh

print_status "Building and starting services..."
docker-compose build --no-cache

print_status "Starting services..."
docker-compose up -d

print_status "Waiting for services to be ready..."
sleep 10

print_status "Checking service status..."
docker-compose ps

print_status "Testing health endpoint..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Health check passed!"
else
    print_warning "Health check failed. Check logs with: docker-compose logs phantomnet"
fi

print_status "Creating deployment info file..."
cat > DEPLOYMENT_INFO.txt << EOF
PhantomNet Docker Deployment
============================

Deployment Date: $(date)
Domain: ${DOMAIN_NAME}
Docker Compose File: ${COMPOSE_FILE}

Services:
- PhantomNet App: $(docker-compose ps phantomnet | grep -o "Up\|Down")
- Nginx: $(docker-compose ps nginx | grep -o "Up\|Down")
- Redis: $(docker-compose ps redis | grep -o "Up\|Down")

Access URLs:
- HTTP: http://${DOMAIN_NAME}
- Admin Panel: http://${DOMAIN_NAME}/admin/login
- Default Admin: admin / admin123

Docker Commands:
- View logs: docker-compose logs -f
- Stop services: docker-compose down
- Restart services: docker-compose restart
- Update services: docker-compose pull && docker-compose up -d

Backup:
- Run backup: ./backup.sh
- Backup location: ./backups/

Monitoring:
- Check status: ./monitor.sh
- Health check: curl http://localhost:8000/health

Next Steps:
1. Update domain name in nginx/nginx.conf
2. Set up SSL certificates
3. Change default admin password
4. Configure monitoring and alerting
5. Set up automatic backups

SSL Setup:
1. Place SSL certificates in ssl/ directory
2. Update nginx configuration
3. Restart nginx: docker-compose restart nginx
EOF

print_status "Creating systemd service for auto-start..."
sudo tee /etc/systemd/system/phantomnet-docker.service > /dev/null << EOF
[Unit]
Description=PhantomNet Docker Services
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable phantomnet-docker

print_status "Setting up automatic backups..."
echo "0 2 * * * cd $(pwd) && ./backup.sh" | crontab -

print_status "Docker deployment completed successfully! 🎉"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Update the domain name in nginx/nginx.conf"
echo "2. Place SSL certificates in ssl/ directory"
echo "3. Change the default admin password"
echo "4. Review the DEPLOYMENT_INFO.txt file for more details"
echo ""
echo -e "${GREEN}Your PhantomNet application is now running at:${NC}"
echo "http://localhost:8000"
echo "http://${DOMAIN_NAME} (after DNS configuration)"
echo ""
echo -e "${YELLOW}Default admin credentials: admin / admin123${NC}"
echo -e "${RED}⚠️  IMPORTANT: Change this password immediately!${NC}"
echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo "- Monitor: ./monitor.sh"
echo "- Backup: ./backup.sh"
echo "- Logs: docker-compose logs -f"
echo "- Stop: docker-compose down"
echo "- Start: docker-compose up -d"
