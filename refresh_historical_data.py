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


import os
import telepot
import time
from fyers_utils import FyersUtils
from dotenv import load_dotenv
from datetime import datetime,timedelta

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


fu = FyersUtils(bot_send_message)
try:
    get_fyers_session()
except Exception as err:
    print(err)
    bot_send_message('Failed to establish session, trying one last time')
    get_fyers_session()

fyers = fu.fyers

now = datetime.now()
today910am = datetime.now().replace(hour=9, minute=10, second=0, microsecond=0)
today330pm = datetime.now().replace(hour=15, minute=30, second=0, microsecond=0)

while datetime.now() > today910am and datetime.now() < today330pm:
    is_notify_user = False
    quote_data = fu.get_quote_data()
    # if not fu.is_quote_sideways():
    #    is_notify_user = True
    if fu.is_high_broken(quote_data):
        is_notify_user = True
        bot_send_message('Broke market high')
    if fu.is_low_broken(quote_data):
        is_notify_user = True
        bot_send_message('Broke market low')
    if is_notify_user:
        bot_send_message(quote_data)

    fu.save_df(quote_data)
    time.sleep(60)

bot_send_message('Markets has been closed, shutting down bot')


tmp_df=fu.download_historical_data(symbol_name = "NSE:NIFTYBANK-INDEX", from_date = "2022-11-1" , to_date = "2022-11-30")


mongo_instance = MongoDB()

bnf = mongo_instance.use_collection('CRUDEOIL22DECFUT', 'seconds')

bnf.find({
    'high': {"$gt":100}
    })


x= bnf.aggregate([
    { "$project" : { "dt":{ "$dateToString": 
                           { "format": "%Y-%m-%d", "date": "$datetime"}     }}}
    #{"$group":{"$month":'$dateteime'}}
    ])
    
today = datetime.strptime(datetime.strftime(datetime.now(), "%Y-%m-%d"), "%Y-%m-%d")

date_delta = timedelta(days = 7)
date_before_week = datetime.now() - date_delta 

datetime(date_before_week)

today_high = 0
max_query= bnf.find( { "datetime": { "$gte": today } }).sort("high",-1).limit(1)
for i in max_query:
    today_high = i.get('high')
today_high


bnf.find_one( { "datetime": { "$gte": today } ,"high" :{"$gt":today_high} } )

x= bnf.aggregate([
    { "$match": { "datetime": { "$gte": today } } },
    { "$group": { "_id": { "$dateToString": { "format": "%Y-%m-%d", "date": "$datetime"} },
       "low": { "$max": '$high' } } },
  ])

for i in x:
    print(i)


weekly_demand_collection.find({
    "center_id" : 55,
    "checkout_price" : { "$lt" : 200, "$gt" : 100}
})
