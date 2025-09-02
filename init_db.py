#!/usr/bin/env python3
"""
Database initialization script for PhantomNet C2
Creates the database tables and initial admin user
"""

from app import create_app, db
from app.models.admin import Admin

def init_database():
    """Initialize the database with tables and initial data"""
    app = create_app()
    
    with app.app_context():
        # Create all database tables
        print("Creating database tables...")
        db.create_all()
        
        # Check if admin user already exists
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            # Create default admin user
            print("Creating default admin user...")
            admin = Admin(username='admin')
            admin.set_password('admin123')  # Change this password in production!
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created:")
            print("Username: admin")
            print("Password: admin123")
            print("⚠️  IMPORTANT: Change this password after first login!")
        else:
            print("Admin user already exists")
        
        print("Database initialization complete!")

if __name__ == '__main__':
    init_database()
