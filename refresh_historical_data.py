# -*- coding: utf-8 -*-
"""
    Program to notify user about stock market changes
    Simply set this up as hourly cron
    $ crontab -e
    11 9 * * 1-5 cd /home/pi/pi-telegram-bot && nohup python3 stock_market_monitor.py > stock_market_monitor_log.txt &
"""

import sys
import os
 
# getting the name of the directory
# where the this file is present.
parent = os.path.dirname(os.path.realpath('./'))
 
# adding the parent directory to
# the sys.path.
sys.path.append(os.path.join(parent,'fundamental-omniwatcher'))

from mongodb_utils import MongoDB
from neodb_utils import NeoDB


import os
import telepot
import time
from fyers_utils import FyersUtils
from dotenv import load_dotenv
from datetime import datetime,timedelta

load_dotenv()
load_dotenv("db.env")


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
        msg = bot.getUpdates()
        while not msg:
            msg = bot.getUpdates()
            time.sleep(30)
        try:
            update_id, chat_id, message_text = bot_get_message_text(msg[-1])
            # add offest to remove last message
            bot.getUpdates(offset=update_id+1)
            if message_text == 'exit':
                bot_send_message('Closing the bot on users request')
                exit()
            fu._set_auth_code(message_text)
            time.sleep(5)
        except:
            bot_send_message('Error message text')
        get_fyers_session()
    else:
        pass

# neo4j & mongo init intance here
neo_instance = NeoDB(username='neo4j', password='Gramener@123', host=os.environ['host'])
mongo_instance = MongoDB(username='mongo_root', password='Gramenr123', host=os.environ['host'])


fu = FyersUtils(bot_send_message,mongo_instance)
try:
    get_fyers_session()
except Exception as err:
    print(err)
    bot_send_message('Failed to establish session, trying one last time')
    get_fyers_session()

fyers = fu.fyers
# normal fyers login upto this point



def download_data_chunk(ticker_name, chunk_in_days = 99):
    # TODO: if the stock exists on fyers check in mongo
    # TODO: if stock exists in mongo check the min & max - use this delta to cut down cost
    # TODO: if stock exists download the data for x years & dump into mongo DB

    ymd_format = "%Y-%m-%d"
    today = datetime.now()
    
    start_date = datetime.strptime( "2019-01-01", ymd_format)
    to_date = (start_date + timedelta(days=99))
    
    while to_date < today:
        print( start_date.strftime(ymd_format) , 'to' , to_date.strftime(ymd_format) )
        fu.dump_historical_data_equity(ticker_name, symbol_name = f"NSE:{ticker_name}-EQ", from_date = start_date.strftime(ymd_format) , to_date = to_date.strftime(ymd_format))

        start_date = (start_date + timedelta(days=99))
        to_date = (start_date + timedelta(days=99))
        if to_date > today:
            print( start_date.strftime(ymd_format) , 'to' , today.strftime(ymd_format) )
            fu.dump_historical_data_equity(ticker_name, symbol_name = f"NSE:{ticker_name}-EQ", from_date = start_date.strftime(ymd_format) , to_date = today.strftime(ymd_format))
    
        
    
    

# get all ticker names from neo4j 
all_stocks = neo_instance.get_all_nodes()
# for each tickername check if the equity stock exists on fyers
for stock_meta in all_stocks:
    ticker_name = stock_meta.get("ticker_name")    
download_data_chunk('DLINKINDIA')
