# app/controllers/admin_controller.py

from app.models.admin import Admin
from werkzeug.security import generate_password_hash, check_password_hash

def login_admin(username, password):
    admin = Admin.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password_hash, password):
        return True
    return False

def logout_admin():
    # Implement logout logic if needed
    pass