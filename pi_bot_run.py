"""
    1. Keep the bot running every X seconds
    2. get intenet of the request
    3. if valid response return the ask & copy me
"""
import os
import telepot
import time
from bot_utils import BotSwitch
import re
from dotenv import load_dotenv
from telegram_bot.telegram_utils import TelegramBot

load_dotenv()

global t_bot
t_bot = TelegramBot()
commands = BotSwitch()


for _ in range(0,10):
    time.sleep(30)
    update_id, chat_id, message_text=t_bot.get_text_message()
    print(update_id, chat_id, message_text)


