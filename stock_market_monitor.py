# -*- coding: utf-8 -*-
"""
    Program to notify user about stock market changes
    Simply set this up as hourly cron
    $ crontab -e
    11 9 * * 1-5 cd /home/pi/pi-telegram-bot && nohup python3 stock_market_monitor.py > stock_market_monitor_log.txt &
"""
import os
import telepot
import time
from fyers_utils import FyersUtils
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

botname = 'aqua4_pi_bot'  # bot secret will be stored in the env var with this key
bot = telepot.Bot(os.environ[botname])
chat_id = os.environ['chat_id']
bot.getMe()


def bot_send_message(*message):
    message_str = ''
    for _msg in message:
        message_str += f'{_msg}'
    return bot.sendMessage(chat_id, message_str)


def bot_get_message_text(msg):
    update_id = msg.get('update_id')
    _message = msg.get('message')
    return update_id, _message.get('chat').get('id'), _message.get('text')


def get_fyers_session():
    """
        fyers login flow
        1. user asks to subscribe for 24 hours
        2. bot checks the session
        3. if session does not exist
        4. bot returns an url
        5. user logins to url & return the auth code
    """
    if not fu.is_bot_session_active():
        #auth_code_gen_url = fu._get_auth_url()
        fu._get_auth_url()
        counter = 10
        msg = bot.getUpdates()
        while not msg and counter < 15:
            msg = bot.getUpdates()
            time.sleep(counter)
            counter += 1
        update_id, chat_id, auth_code_str = bot_get_message_text(msg[-1])
        # add offest to remove last message
        bot.getUpdates(offset=update_id+1)
        fu._set_auth_code(auth_code_str)
        get_fyers_session()
    else:
        pass


fu = FyersUtils(bot_send_message)
get_fyers_session()
fyers = fu.fyers

now = datetime.now()
today910am = datetime.now().replace(hour=9, minute=10, second=0, microsecond=0)
today330pm = datetime.now().replace(hour=15, minute=30, second=0, microsecond=0)

while datetime.now() > today910am and datetime.now() < today330pm:
    quote_data = fu.get_quote_data()
    if not fu.is_quote_sideways():
        bot_send_message(quote_data)
    fu.save_df(quote_data)
    time.sleep(60)

bot_send_message('Markets has been closed, shutting down bot')
