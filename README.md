# PhantomNet Project

A Flask-based web application with a modular architecture for managing bots, commands, payloads, targets, and tasks.

## Project Structure

```
phantomnet/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Application configuration
│   ├── controllers/              # Business logic controllers
│   │   ├── __init__.py
│   │   ├── admin_controller.py
│   │   ├── bot_controller.py
│   │   ├── command_controller.py
│   │   ├── payload_controller.py
│   │   ├── target_controller.py
│   │   └── task_controller.py
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── bot.py
│   │   ├── command.py
│   │   ├── payload.py
│   │   ├── target.py
│   │   └── task.py
│   ├── routes/                   # Route definitions
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── api.py
│   │   └── web.py
│   ├── static/                   # Static files
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── scripts.js
│   ├── templates/                # HTML templates
│   │   ├── 404.html
│   │   ├── 500.html
│   │   ├── admin_login.html
│   │   └── base.html
│   └── utils/                    # Utility functions
│       └── __init__.py
├── migrations/                    # Database migrations
│   ├── __init__.py
│   └── alembic.ini
├── server.py                     # Application entry point
├── requirements.txt              # Python dependencies
├── phantom.db                    # SQLite database
├── phantom_client.py             # Phantom client implementation
├── deploy.py                     # Deployment script
├── deploy_to_ubuntu_vps.py      # Ubuntu VPS deployment script
├── dynu_config.json             # Dynu DNS configuration
└── Features.txt                  # Feature documentation
```

## Setup Instructions

### Local Development Setup

1. **Clone and Setup Project:**
   ```bash
   # Navigate to project directory
   cd phantomnet
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Database:**
   ```bash
   python init_db.py
   ```

4. **Run the Application:**
   ```bash
   python server.py
   ```

5. **Access the Application:**
   - Web Interface: http://localhost:8443
   - Admin Panel: http://localhost:8443/admin/login
   - Default Admin Credentials: admin / admin123

### Production Deployment

For production deployment, see the [DEPLOYMENT_TUTORIAL.md](DEPLOYMENT_TUTORIAL.md) for detailed instructions or use the automated deployment scripts:

```bash
# Production deployment
chmod +x deploy_scripts/setup_production.sh
./deploy_scripts/setup_production.sh

# Docker deployment
chmod +x deploy_scripts/setup_docker.sh
./deploy_scripts/setup_docker.sh
```

## Features

- **Bot Management:** Create, configure, and manage bot instances
- **Command System:** Define and execute commands on targets
- **Payload Management:** Handle different types of payloads
- **Target Tracking:** Monitor and manage target systems
- **Task Automation:** Schedule and execute automated tasks
- **Admin Interface:** Secure administrative controls
- **API Endpoints:** RESTful API for programmatic access

## Configuration

The application uses a configuration file (`app/config.py`) for:
- Database connection settings
- Secret key generation
- Application-specific configurations

## Database

The application uses SQLite as the default database (`phantom.db`) with the following models:
- Admin users
- Bot instances
- Commands
- Payloads
- Targets
- Tasks

## Security

- Admin authentication required for administrative functions
- Secure session management
- Input validation and sanitization

## Deployment

### Quick Start
1. **Local Development**: Follow the [Local Development Setup](#local-development-setup) section below
2. **Production**: Use the automated [Production Deployment Script](deploy_scripts/setup_production.sh)
3. **Docker**: Use the automated [Docker Deployment Script](deploy_scripts/setup_docker.sh)

### Deployment Resources
- **[DEPLOYMENT_TUTORIAL.md](DEPLOYMENT_TUTORIAL.md)** - Comprehensive deployment guide
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Step-by-step deployment checklist
- **`deploy_scripts/setup_production.sh`** - Automated production deployment script
- **`deploy_scripts/setup_docker.sh`** - Automated Docker deployment script
- **`deploy.py`** - General deployment utility
- **`deploy_to_ubuntu_vps.py`** - Ubuntu VPS specific deployment

## License

This project is proprietary software. All rights reserved.
