# app/controllers/target_controller.py

from app.models.target import Target
from app import db
import secrets

def create_target(data):
    new_target = Target(
        id=secrets.token_urlsafe(16),
        ip_address=data['ip_address'],
        hostname=data['hostname'],
        os_info=data['os_info'],
        open_ports=data['open_ports'],
        vulnerabilities=data['vulnerabilities'],
        services=data['services']
    )
    db.session.add(new_target)
    db.session.commit()
    return {'target_id': new_target.id}, 201

def delete_target(target_id):
    target = Target.query.get(target_id)
    if not target:
        return {'error': 'Target not found'}, 404
    db.session.delete(target)
    db.session.commit()
    return {'success': True}, 200

def list_targets():
    targets = Target.query.all()
    target_list = [target.to_dict() for target in targets]
    return target_list, 200

def get_target(target_id):
    target = Target.query.get(target_id)
    if not target:
        return {'error': 'Target not found'}, 404
    return target.to_dict(), 200