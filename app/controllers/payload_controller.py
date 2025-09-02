# app/controllers/payload_controller.py

from app.models.payload import Payload
from app import db
import secrets

def create_payload(data):
    new_payload = Payload(
        id=secrets.token_urlsafe(16),
        name=data['name'],
        payload_type=data['payload_type'],
        platform=data['platform'],
        architecture=data['architecture'],
        payload_data=data['payload_data'],
        encryption_key=data['encryption_key']
    )
    db.session.add(new_payload)
    db.session.commit()
    return {'payload_id': new_payload.id}, 201

def delete_payload(payload_id):
    payload = Payload.query.get(payload_id)
    if not payload:
        return {'error': 'Payload not found'}, 404
    db.session.delete(payload)
    db.session.commit()
    return {'success': True}, 200

def list_payloads():
    payloads = Payload.query.all()
    payload_list = [payload.to_dict() for payload in payloads]
    return payload_list, 200

def get_payload(payload_id):
    payload = Payload.query.get(payload_id)
    if not payload:
        return {'error': 'Payload not found'}, 404
    return payload.to_dict(), 200