from config import *
from main import bot

async def check_follow(id):
    for kanal in CHANNELS:
        member = await bot.get_chat_member(kanal, id)
        if member.status not in ('member', 'administrator', 'creator'):
            return False
    return True