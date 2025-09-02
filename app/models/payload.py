# app/models/payload.py

from app import db

class Payload(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    payload_type = db.Column(db.String(50), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    architecture = db.Column(db.String(50), nullable=False)
    payload_data = db.Column(db.LargeBinary, nullable=False)
    encryption_key = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'payload_type': self.payload_type,
            'platform': self.platform,
            'architecture': self.architecture,
            'encryption_key': self.encryption_key,
            'created_at': self.created_at.isoformat()
        }