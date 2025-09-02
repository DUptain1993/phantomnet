# PhantomNet Deployment Checklist

Use this checklist to ensure a successful deployment of your PhantomNet application.

## Pre-Deployment Checklist

### ✅ System Requirements
- [ ] **Operating System**: Linux (Ubuntu 20.04+), Windows 10+, or macOS
- [ ] **Python**: 3.8+ (3.11+ recommended)
- [ ] **RAM**: Minimum 2GB, 4GB+ recommended
- [ ] **Storage**: 10GB+ available space
- [ ] **Network**: Stable internet connection

### ✅ Software Dependencies
- [ ] **Python 3.8+** installed and accessible
- [ ] **pip** package manager available
- [ ] **Git** (for version control, optional)
- [ ] **Docker & Docker Compose** (for containerized deployment)

### ✅ Project Files
- [ ] **Project directory** contains all required files
- [ ] **requirements.txt** present and up-to-date
- [ ] **Database initialization script** (init_db.py) present
- [ ] **Configuration files** properly set up

## Local Development Deployment

### ✅ Environment Setup
- [ ] **Virtual environment** created and activated
- [ ] **Dependencies installed** from requirements.txt
- [ ] **Environment variables** configured (.env file)
- [ ] **Database initialized** (python init_db.py)

### ✅ Application Testing
- [ ] **Application imports** without errors
- [ ] **Database connection** working
- [ ] **Admin user created** with default credentials
- [ ] **Development server starts** successfully
- [ ] **Web interface accessible** at http://localhost:8443
- [ ] **Admin login working** at /admin/login

## Production Deployment

### ✅ Server Preparation
- [ ] **System packages updated** (apt update && apt upgrade)
- [ ] **Required packages installed** (nginx, supervisor, ufw)
- [ ] **Firewall configured** (SSH, HTTP, HTTPS ports open)
- [ ] **Non-root user created** for application

### ✅ Application Deployment
- [ ] **Application directory created** (/opt/phantomnet)
- [ ] **Files copied** to production location
- [ ] **Virtual environment** created and activated
- [ ] **Production dependencies** installed (including gunicorn)
- [ ] **Production configuration** created (config.py)

### ✅ Service Configuration
- [ ] **Gunicorn configuration** created (gunicorn.conf.py)
- [ ] **Supervisor configuration** created and enabled
- [ ] **Nginx configuration** created and enabled
- [ ] **Log directories** created with proper permissions
- [ ] **Services started** and running

### ✅ Database & Security
- [ ] **Database initialized** in production
- [ ] **File permissions** set correctly
- [ ] **Default admin password** changed
- [ ] **Secret key** generated and configured
- [ ] **Environment variables** set securely

## VPS Deployment

### ✅ VPS Setup
- [ ] **VPS provider account** created
- [ ] **SSH access** configured
- [ ] **Domain name** pointing to VPS IP
- [ ] **Non-root user** created with sudo access
- [ ] **SSH key authentication** configured

### ✅ Security Configuration
- [ ] **Firewall (UFW)** enabled and configured
- [ ] **SSH port** secured (change from default if desired)
- [ ] **Fail2ban** installed and configured (optional but recommended)
- [ ] **Regular security updates** scheduled

## Docker Deployment

### ✅ Docker Environment
- [ ] **Docker** installed and running
- [ ] **Docker Compose** installed
- [ ] **Dockerfile** created and optimized
- [ ] **docker-compose.yml** configured
- [ ] **Docker networks** properly configured

### ✅ Container Configuration
- [ ] **Application container** building successfully
- [ ] **Nginx container** configured
- [ ] **Redis container** running (if using)
- [ ] **Volume mounts** configured correctly
- [ ] **Environment variables** set in containers

## SSL/HTTPS Setup

### ✅ SSL Certificate
- [ ] **Domain name** properly configured
- [ ] **DNS records** pointing to server
- [ ] **Certbot** installed
- [ ] **SSL certificate** obtained from Let's Encrypt
- [ ] **Auto-renewal** configured

### ✅ HTTPS Configuration
- [ ] **Nginx SSL configuration** updated
- [ ] **HTTP to HTTPS redirect** working
- [ ] **SSL protocols** configured (TLS 1.2+)
- [ ] **Security headers** implemented
- [ ] **Mixed content** issues resolved

## Post-Deployment Verification

### ✅ Application Health
- [ ] **Application accessible** via domain name
- [ ] **Admin panel** working correctly
- [ ] **Database operations** functioning
- [ ] **Static files** serving properly
- [ ] **Error pages** displaying correctly

### ✅ Performance & Monitoring
- [ ] **Log monitoring** configured
- [ ] **Performance metrics** collected
- [ ] **Health checks** implemented
- [ ] **Backup strategy** in place
- [ ] **Monitoring alerts** configured

### ✅ Security Verification
- [ ] **Default passwords** changed
- [ ] **Unnecessary ports** closed
- [ ] **Security headers** implemented
- [ ] **Rate limiting** configured
- [ ] **Input validation** working

## Maintenance & Updates

### ✅ Regular Maintenance
- [ ] **System updates** scheduled
- [ ] **Security patches** applied
- [ ] **Log rotation** configured
- [ ] **Backup verification** tested
- [ ] **Performance monitoring** active

### ✅ Update Procedures
- [ ] **Application update** process documented
- [ ] **Database migration** procedures tested
- [ ] **Rollback procedures** in place
- [ ] **Change management** process established

## Troubleshooting Preparation

### ✅ Documentation
- [ ] **Deployment documentation** complete
- [ ] **Troubleshooting guide** available
- [ ] **Contact information** documented
- [ ] **Emergency procedures** established

### ✅ Tools & Access
- [ ] **SSH access** to server
- [ ] **Log access** configured
- [ ] **Database access** available
- [ ] **Monitoring tools** accessible
- [ ] **Backup access** verified

## Final Verification

### ✅ Complete System Test
- [ ] **All features** working correctly
- [ ] **Performance** meets requirements
- [ ] **Security** measures effective
- [ ] **Backup/restore** tested
- [ ] **Monitoring** alerts working

### ✅ Documentation & Handover
- [ ] **Deployment guide** updated
- [ ] **Configuration files** documented
- [ ] **Credentials** securely stored
- [ ] **Team access** configured
- [ ] **Knowledge transfer** completed

---

## Quick Commands Reference

### Health Checks
```bash
# Application health
curl http://your-domain.com/health

# Service status
sudo systemctl status nginx
sudo supervisorctl status phantomnet

# Database connection
python -c "from app import db; print('DB OK')"
```

### Common Issues
```bash
# Check logs
sudo tail -f /var/log/phantomnet/app.log
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart nginx
sudo supervisorctl restart phantomnet

# Check permissions
ls -la /opt/phantomnet/
sudo chown -R www-data:www-data /opt/phantomnet/
```

### Backup & Recovery
```bash
# Manual backup
./backup.sh

# Check backup status
ls -la /opt/backups/phantomnet/

# Restore database
cp /opt/backups/phantomnet/phantomnet_YYYYMMDD_HHMMSS.db /opt/phantomnet/phantomnet.db
```

---

**Remember**: This checklist is a guide. Adapt it to your specific deployment requirements and environment. Always test in a development environment before deploying to production.
