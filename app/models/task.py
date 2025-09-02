# app/models/task.py

from app import db

class Task(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    bot_id = db.Column(db.String(16), db.ForeignKey('bot.id'), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)
    command = db.Column(db.String(255), nullable=False)
    args = db.Column(db.Text, nullable=True)
    payload_id = db.Column(db.String(16), db.ForeignKey('payload.id'), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending')
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'task_type': self.task_type,
            'command': self.command,
            'args': self.args,
            'payload_id': self.payload_id,
            'status': self.status,
            'result': self.result,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }