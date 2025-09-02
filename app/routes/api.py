# app/routes/api.py

from flask import Blueprint, request, jsonify
from app.controllers.bot_controller import create_bot, delete_bot, list_bots, get_bot
from app.controllers.command_controller import create_command, delete_command, list_commands, get_command
from app.controllers.payload_controller import create_payload, delete_payload, list_payloads, get_payload
from app.controllers.target_controller import create_target, delete_target, list_targets, get_target
from app.controllers.task_controller import create_task, delete_task, list_tasks, get_task

bp = Blueprint('api', __name__)

@bp.route('/api/bots', methods=['GET'])
def list_bots_route():
    return list_bots()

@bp.route('/api/bot/<bot_id>', methods=['GET'])
def get_bot_route(bot_id):
    return get_bot(bot_id)

@bp.route('/api/commands', methods=['GET'])
def list_commands_route():
    return list_commands()

@bp.route('/api/command/<command_id>', methods=['GET'])
def get_command_route(command_id):
    return get_command(command_id)

@bp.route('/api/payloads', methods=['GET'])
def list_payloads_route():
    return list_payloads()

@bp.route('/api/payload/<payload_id>', methods=['GET'])
def get_payload_route(payload_id):
    return get_payload(payload_id)

@bp.route('/api/targets', methods=['GET'])
def list_targets_route():
    return list_targets()

@bp.route('/api/target/<target_id>', methods=['GET'])
def get_target_route(target_id):
    return get_target(target_id)

@bp.route('/api/tasks', methods=['GET'])
def list_tasks_route():
    return list_tasks()

@bp.route('/api/task/<task_id>', methods=['GET'])
def get_task_route(task_id):
    return get_task(task_id)

@bp.route('/api/create_bot', methods=['POST'])
def create_bot_route():
    return create_bot(request.json)

@bp.route('/api/delete_bot/<bot_id>', methods=['POST'])
def delete_bot_route(bot_id):
    return delete_bot(bot_id)

@bp.route('/api/create_command', methods=['POST'])
def create_command_route():
    return create_command(request.json)

@bp.route('/api/delete_command/<command_id>', methods=['POST'])
def delete_command_route(command_id):
    return delete_command(command_id)

@bp.route('/api/create_payload', methods=['POST'])
def create_payload_route():
    return create_payload(request.json)

@bp.route('/api/delete_payload/<payload_id>', methods=['POST'])
def delete_payload_route(payload_id):
    return delete_payload(payload_id)

@bp.route('/api/create_target', methods=['POST'])
def create_target_route():
    return create_target(request.json)

@bp.route('/api/delete_target/<target_id>', methods=['POST'])
def delete_target_route(target_id):
    return delete_target(target_id)

@bp.route('/api/create_task', methods=['POST'])
def create_task_route():
    return create_task(request.json)

@bp.route('/api/delete_task/<task_id>', methods=['POST'])
def delete_task_route(task_id):
    return delete_task(task_id)