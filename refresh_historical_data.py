# -*- coding: utf-8 -*-
"""
    Program to refresh market data 
    Triggered as cron every morning or on reboot. This program is to be kept running to maintain the instance of broker api. Closes after market hours.
    $ crontab -e
    11 9 * * 1-5 cd /home/pi/pi-telegram-bot && nohup python refresh_historical_data.py > refresh_historical_data_log.txt &
"""

from datetime import datetime, timedelta
from dotenv import load_dotenv
from fyers_utils import FyersUtils
import time
import telepot
import sys
import os

# getting the name of the directory where the this file is present.
parent = os.path.dirname(os.path.realpath('./'))  # noqa
# adding the parent directory to the sys.path.
sys.path.append(os.path.join(parent, 'fundamental_omniwatcher'))  # noqa
from mongodb_utils import MongoDB  # noqa
from neodb_utils import NeoDB  # noqa


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
neo_instance = NeoDB(
    username='neo4j', password='Gramener@123', host=os.environ['host'])
mongo_instance = MongoDB(username='mongo_root',
                         password='Gramenr123', host=os.environ['host'])


fu = FyersUtils(bot_send_message, mongo_instance)
try:
    get_fyers_session()
except Exception as err:
    print(err)
    bot_send_message('Failed to establish session, trying one last time')
    get_fyers_session()

fyers = fu.fyers
# normal fyers login upto this point


def download_data_chunk(ticker_name, chunk_in_days=99):
    """
    Download data from 2019

    Parameters
    ----------
    ticker_name : TYPE
        DESCRIPTION.
    chunk_in_days : TYPE, optional
        DESCRIPTION. The default is 99.

    Returns
    -------
    None.

    """
    # TODO: if the stock exists on fyers check in mongo
    _mongo_collection = mongo_instance.use_collection(ticker_name)
    # TODO: if stock exists download the data for x years & dump into mongo DB
    min_date, max_date = mongo_instance.get_minmax_dates(_mongo_collection)

    ymd_format = "%Y-%m-%d"
    today = datetime.now()

    start_date = datetime.strptime("2019-01-01", ymd_format)

    # TODO: if stock exists in mongo check the min & max - use this delta to cut down cost. Need to do same for min_date
    if max_date and start_date < max_date:
        start_date = max_date
    to_date = (start_date + timedelta(days=99))

    if to_date > today:
        to_date = today

    while to_date <= today:
        _fyers_symbol_name = f"NSE:{ticker_name}-EQ"
        print(f'Downloading data for {ticker_name} \t from',start_date.strftime(ymd_format),
              'to', to_date.strftime(ymd_format))
        if to_date == today:
            fu.dump_historical_data_equity(ticker_name, symbol_name=_fyers_symbol_name, from_date=start_date.strftime(
                ymd_format), to_date=today.strftime(ymd_format), drop_latest=True)
        else:
            fu.dump_historical_data_equity(ticker_name, symbol_name=_fyers_symbol_name, from_date=start_date.strftime(
                ymd_format), to_date=to_date.strftime(ymd_format))

        start_date = (start_date + timedelta(days=99))
        to_date = (start_date + timedelta(days=99))
        if to_date > today and start_date < today:
            print(f'Downloading data for {ticker_name} \t from',start_date.strftime(ymd_format),
                  'to', today.strftime(ymd_format))
            fu.dump_historical_data_equity(ticker_name, symbol_name=_fyers_symbol_name, from_date=start_date.strftime(
                ymd_format), to_date=today.strftime(ymd_format), drop_latest=True)


# df = fu.download_historical_data('NSE:BIOCON-EQ',granularity_in_mins=1, from_date="2022-9-1", to_date="2022-10-1")
# df.to_csv('biocon-intraday_prev2.csv')


# d_df = df[ (df.index > '2022-09-1') & (df.index < '2022-09-3') ]

# TODO: get all ticker names from neo4j
# all_stocks = neo_instance.get_all_nodes()
# # for each tickername check if the equity stock exists on fyers
# for stock_meta in all_stocks:
#     ticker_name = stock_meta.get("ticker_name")

now = datetime.now()
today900am = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
today330pm = datetime.now().replace(hour=15, minute=30, second=0, microsecond=0)

target_minute = 16  # set the target minute

# download_data_chunk('ONGC')

while datetime.now() > today900am and datetime.now() < today330pm:

    tickers = ['TATAMOTORS', 'DLINKINDIA', 'AFFLE',
               'DMART', 'WIPRO', 'TATAPOWER',  'CDSL',  'ONGC']

    for _ticker in tickers:
        download_data_chunk(_ticker)

    # calculate the next execution time based on the target minute
    now = datetime.now()
    next_hour = now.replace(
        hour=now.hour + 1, minute=target_minute, second=0, microsecond=0)
    # calculate the time to sleep until the next execution time
    sleep_time = (next_hour - now).total_seconds()

    print(
        f'program will now run at {next_hour} to download the new data...')

    time.sleep(sleep_time)
    if now.minute >= target_minute:
        next_hour += timedelta(hours=1)

print(f'Markets closed, program will now exit.')
