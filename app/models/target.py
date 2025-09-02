# app/models/target.py

from app import db

class Target(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    os_info = db.Column(db.Text, nullable=False)
    open_ports = db.Column(db.Text, nullable=False)
    vulnerabilities = db.Column(db.Text, nullable=False)
    services = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='new')
    exploitation_method = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'os_info': self.os_info,
            'open_ports': self.open_ports,
            'vulnerabilities': self.vulnerabilities,
            'services': self.services,
            'status': self.status,
            'exploitation_method': self.exploitation_method,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }