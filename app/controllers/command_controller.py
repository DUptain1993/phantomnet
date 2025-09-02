# app/controllers/command_controller.py

from app.models.command import Command
from app import db
import secrets

def create_command(data):
    new_command = Command(
        id=secrets.token_urlsafe(16),
        bot_id=data['bot_id'],
        command=data['command'],
        args=data.get('args')
    )
    db.session.add(new_command)
    db.session.commit()
    return {'command_id': new_command.id}, 201

def delete_command(command_id):
    command = Command.query.get(command_id)
    if not command:
        return {'error': 'Command not found'}, 404
    db.session.delete(command)
    db.session.commit()
    return {'success': True}, 200

def list_commands():
    commands = Command.query.all()
    command_list = [command.to_dict() for command in commands]
    return command_list, 200

def get_command(command_id):
    command = Command.query.get(command_id)
    if not command:
        return {'error': 'Command not found'}, 404
    return command.to_dict(), 200