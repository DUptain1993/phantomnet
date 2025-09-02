# app/models/bot.py

from app import db

class Bot(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    session_token = db.Column(db.String(128), unique=True, nullable=False)
    os_info = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='active')
    last_seen = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'session_token': self.session_token,
            'os_info': self.os_info,
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'status': self.status,
            'last_seen': self.last_seen.isoformat(),
            'notes': self.notes
        }