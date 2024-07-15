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


# simply use the logger from execution file
logger = logging.getLogger('backtrader')

load_dotenv('telegram.env')


class TelegramBot:
    _instances = {}

    def __new__(cls, chat_id='my_chat_id'):
        if chat_id not in cls._instances:
            instance = super(TelegramBot, cls).__new__(cls)
            cls._instances[chat_id] = instance
            logger.warning(f'created new bot instance for {chat_id}')
        return cls._instances[chat_id]

    def __init__(self, chat_id='my_chat_id') -> None:
        if not hasattr(self, 'initialized'):
            self.botname = 'aqua4_pi_bot'
            self.bot = telepot.Bot(os.environ[self.botname])
            self.chat_id = os.environ[chat_id]
            self.bot.getMe()
            self.initialized = True

    def handle(msg):
        return msg
    # >>> MessageLoop(bot, handle).run_as_thread()

    def get_text_message(self, mark_as_read=False):
        msg = self.bot.getUpdates()
        logger.debug(f'get_text_message: msg = {msg}')
        if msg:
            return self.extract_text_message(msg[-1], mark_as_read)
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
