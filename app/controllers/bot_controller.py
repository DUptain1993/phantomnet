# app/controllers/bot_controller.py

from app.models.bot import Bot
from app import db
import secrets

def create_bot(data):
    new_bot = Bot(
        id=secrets.token_urlsafe(16),
        session_token=secrets.token_urlsafe(128),
        os_info=data['os_info'],
        ip_address=data['ip_address'],
        hostname=data['hostname']
    )
    db.session.add(new_bot)
    db.session.commit()
    return {'bot_id': new_bot.id}, 201

def delete_bot(bot_id):
    bot = Bot.query.get(bot_id)
    if not bot:
        return {'error': 'Bot not found'}, 404
    db.session.delete(bot)
    db.session.commit()
    return {'success': True}, 200

def list_bots():
    bots = Bot.query.all()
    bot_list = [bot.to_dict() for bot in bots]
    return bot_list, 200

def get_bot(bot_id):
    bot = Bot.query.get(bot_id)
    if not bot:
        return {'error': 'Bot not found'}, 404
    return bot.to_dict(), 200