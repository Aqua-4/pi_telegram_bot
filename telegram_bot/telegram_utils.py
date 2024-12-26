# -*- coding: utf-8 -*-
"""
    Program to notify user about stock market changes
    Simply set this up as hourly cron
    $ crontab -e
    11 9 * * 1-5 cd /home/pi/pi-telegram-bot && nohup python3 stock_market_monitor.py > stock_market_monitor_log.txt &
"""
import os
import telepot
from telepot.exception import TelegramError
from dotenv import load_dotenv
import time
from telepot.loop import MessageLoop
import logging

log_dir_path = '../log'
if not os.path.exists(log_dir_path):
    os.makedirs(log_dir_path)

# simply use the logger from execution file
logger = logging.getLogger('telegram')
# create file handlers
log_file = logging.FileHandler(f'{log_dir_path}/telegram.log', mode='w')
json_file = logging.FileHandler(f'{log_dir_path}/telegram.json.log', mode='w')
# create formatter and add it to the handlers
detailed_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(name)s] [%(funcName)s:%(lineno)d] - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
json_formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}', datefmt='%m/%d/%Y %I:%M:%S %p')
# set formatter for log file
log_file.setFormatter(detailed_formatter)
json_file.setFormatter(json_formatter)
# add the handlers to the logger
logger.addHandler(log_file)
logger.addHandler(json_file)
# set the logging level
logger.setLevel(logging.INFO)


load_dotenv('telegram.env')


class TelegramBot:

    def __init__(self, chat_id='my_chat_id') -> None:
        # bot secret will be stored in the env var with this key
        self.botname = 'aqua4_pi_bot'
        self.bot = telepot.Bot(os.environ[self.botname])
        self.chat_id = os.environ[chat_id]
        self.bot.getMe()
        self.direct_messages = []
        logger.warning(f'created telegram instance for {chat_id}')

    def handle(msg):
        return msg
    # >>> MessageLoop(bot, handle).run_as_thread()

    def stack_direct_messages(self):
        updates = self.bot.getUpdates()
        for update in updates:
            if 'message' in update:
                update_id = update['update_id']
                msg = update['message']
                chat_id = msg['chat']['id']
                if str(chat_id) == str(self.chat_id):
                    self.direct_messages.append(msg['text'])
                    self.bot.getUpdates(offset=update_id+1)


    def pop_last_message(self):
        if self.direct_messages:
            return self.direct_messages.pop()

    def get_text_message(self, mark_as_read=False, descending = True):
        msg = self.bot.getUpdates()
        logger.debug(f'get_text_message: msg = {msg}')
        if msg:
            if descending:
                return self.extract_text_message(msg[-1], mark_as_read)
            # return first message
            return self.extract_text_message(msg[0], mark_as_read)

        return None

    def send_html_message(self, html_file_path, caption='Chart', chat_id=None):

        if chat_id == None:
            chat_id = self.chat_id

        try:
            return self.bot.sendDocument(chat_id, open(html_file_path, 'rb'), caption=caption)
        except TelegramError as e:
            if e.error_code == 429:
                # If the error code is 429 (Too Many Requests), parse the Retry-After header value
                retry_after = int(e.response.get('Retry-After'))
                logger.error(f"Rate limited. Waiting for {retry_after} seconds...")
                time.sleep(retry_after+1)
                return self.bot.sendDocument(chat_id, open(html_file_path, 'rb'), caption=caption)

    def send_image(self, image_file_path, caption=None, chat_id=None):

        if chat_id == None:
            chat_id = self.chat_id

        try:
            return self.bot.sendPhoto(chat_id, open(image_file_path, 'rb'), caption=caption)
        except TelegramError as e:
            if e.error_code == 429:
                # If the error code is 429 (Too Many Requests), parse the Retry-After header value
                retry_after = int(e.response.get('Retry-After'))
                logger.error(f"Rate limited. Waiting for {retry_after} seconds...")
                time.sleep(retry_after+1)
                return self.bot.sendPhoto(chat_id, open(image_file_path, 'rb'), caption=caption)

    def send_text_message(self, *message):
        message_str = ''
        for _msg in message:
            message_str += f'{_msg}'

        try:
            try:
                return self.bot.sendMessage(self.chat_id, message_str)
            except TelegramError as e:
                if e.error_code == 429:
                    # If the error code is 429 (Too Many Requests), parse the Retry-After header value
                    retry_after = int(e.response.get('Retry-After'))
                    logger.error(f"Rate limited. Waiting for {retry_after} seconds...")
                    time.sleep(retry_after+1)
                    return self.bot.sendMessage(self.chat_id, message_str)
        except Exception as err:
            print(err)

    def extract_text_message(self, msg, mark_as_read=False):
        """
        Parameters
        ----------
        msg : TYPE
            DESCRIPTION.
        mark_as_read : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        update_id
        chat_id
        message_text

        """
        logger.debug(f"extract_text_message: msg = {msg}")
        update_id = msg.get('update_id')
        _message = msg.get('message')
        if not _message:
            self.bot.getUpdates(offset=update_id+1)
            return None
        if mark_as_read:
            self.bot.getUpdates(offset=update_id+1)
        return update_id, _message.get('chat').get('id'), _message.get('text')


if __name__ == '__main__':

    t_bot = TelegramBot()
    t_bot.send_text_message('Testing telegram utility function')
    t_bot.get_text_message()

    t_bot.send_html_message('./candlestick_chart.html')
