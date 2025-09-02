# app/models/command.py

from app import db

class Command(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    bot_id = db.Column(db.String(16), db.ForeignKey('bot.id'), nullable=False)
    command = db.Column(db.String(255), nullable=False)
    args = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending')
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'command': self.command,
            'args': self.args,
            'status': self.status,
            'result': self.result,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }