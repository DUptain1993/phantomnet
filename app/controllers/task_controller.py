# app/controllers/task_controller.py

from app.models.task import Task
from app import db
import secrets

def create_task(data):
    new_task = Task(
        id=secrets.token_urlsafe(16),
        bot_id=data['bot_id'],
        task_type=data['task_type'],
        command=data['command'],
        args=data.get('args'),
        payload_id=data.get('payload_id')
    )
    db.session.add(new_task)
    db.session.commit()
    return {'task_id': new_task.id}, 201

def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task not found'}, 404
    db.session.delete(task)
    db.session.commit()
    return {'success': True}, 200

def list_tasks():
    tasks = Task.query.all()
    task_list = [task.to_dict() for task in tasks]
    return task_list, 200

def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task not found'}, 404
    return task.to_dict(), 200