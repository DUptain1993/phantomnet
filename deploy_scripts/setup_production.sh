#!/bin/bash

# PhantomNet Production Deployment Script
# This script automates the production deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="phantomnet"
APP_DIR="/opt/$APP_NAME"
APP_USER="www-data"
APP_GROUP="www-data"
DOMAIN_NAME="your-domain.com"  # Change this to your domain

echo -e "${GREEN}🚀 Starting PhantomNet Production Deployment...${NC}"

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    print_error "sudo is not installed. Please install it first."
    exit 1
fi

print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

print_status "Installing required system packages..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor ufw curl

print_status "Creating application directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

print_status "Copying application files..."
cp -r * $APP_DIR/
cd $APP_DIR

print_status "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

print_status "Creating production configuration..."
cat > config.py << EOF
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '$(openssl rand -hex 32)'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///$APP_DIR/phantomnet.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
EOF

print_status "Creating Gunicorn configuration..."
cat > gunicorn.conf.py << EOF
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
EOF

print_status "Creating Supervisor configuration..."
sudo tee /etc/supervisor/conf.d/$APP_NAME.conf > /dev/null << EOF
[program:$APP_NAME]
directory=$APP_DIR
command=$APP_DIR/venv/bin/gunicorn -c gunicorn.conf.py server:app
user=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/$APP_NAME/app.log
stderr_logfile=/var/log/$APP_NAME/error.log
environment=PYTHONPATH="$APP_DIR"
EOF

print_status "Creating log directories..."
sudo mkdir -p /var/log/$APP_NAME
sudo chown $APP_USER:$APP_GROUP /var/log/$APP_NAME

print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # Redirect HTTP to HTTPS (will be configured after SSL setup)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
    
    location /static/ {
        alias $APP_DIR/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

print_status "Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

print_status "Testing Nginx configuration..."
sudo nginx -t

print_status "Setting up firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

print_status "Setting proper permissions..."
sudo chown -R $APP_USER:$APP_GROUP $APP_DIR
sudo chmod -R 755 $APP_DIR

print_status "Initializing database..."
python init_db.py

print_status "Starting services..."
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start $APP_NAME

print_status "Checking service status..."
sudo supervisorctl status $APP_NAME
sudo systemctl status nginx

print_status "Creating backup script..."
cat > backup.sh << 'EOF'
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

chmod +x backup.sh

print_status "Setting up automatic backups..."
echo "0 2 * * * $APP_DIR/backup.sh" | sudo crontab -

print_status "Creating health check endpoint..."
cat > health_check.py << EOF
from flask import Flask
app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'phantomnet'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
EOF

print_status "Creating systemd service for health check..."
sudo tee /etc/systemd/system/phantomnet-health.service > /dev/null << EOF
[Unit]
Description=PhantomNet Health Check Service
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python health_check.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable phantomnet-health
sudo systemctl start phantomnet-health

print_status "Creating deployment info file..."
cat > DEPLOYMENT_INFO.txt << EOF
PhantomNet Production Deployment
================================

Deployment Date: $(date)
Domain: $DOMAIN_NAME
Application Directory: $APP_DIR
Application User: $APP_USER

Services:
- Nginx: $(sudo systemctl is-active nginx)
- Supervisor: $(sudo systemctl is-active supervisor)
- PhantomNet: $(sudo supervisorctl status $APP_NAME | awk '{print $2}')
- Health Check: $(sudo systemctl is-active phantomnet-health)

Access URLs:
- HTTP: http://$DOMAIN_NAME
- Admin Panel: http://$DOMAIN_NAME/admin/login
- Default Admin: admin / admin123

Next Steps:
1. Configure SSL certificate with Let's Encrypt
2. Update domain name in Nginx configuration
3. Change default admin password
4. Configure monitoring and alerting

Backup Schedule: Daily at 2:00 AM
Backup Location: /opt/backups/phantomnet

Log Locations:
- Application: /var/log/$APP_NAME/
- Nginx: /var/log/nginx/
- Supervisor: /var/log/supervisor/
EOF

print_status "Deployment completed successfully! 🎉"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Update the domain name in Nginx configuration"
echo "2. Set up SSL certificate with: sudo certbot --nginx -d $DOMAIN_NAME"
echo "3. Change the default admin password"
echo "4. Review the DEPLOYMENT_INFO.txt file for more details"
echo ""
echo -e "${GREEN}Your PhantomNet application is now running at:${NC}"
echo "http://$DOMAIN_NAME"
echo ""
echo -e "${YELLOW}Default admin credentials: admin / admin123${NC}"
echo -e "${RED}⚠️  IMPORTANT: Change this password immediately!${NC}"
