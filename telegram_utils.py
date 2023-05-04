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

load_dotenv('telegram.env')


class TelegramBot:

    def __init__(self, chat_id='my_chat_id') -> None:
        # bot secret will be stored in the env var with this key
        self.botname = 'aqua4_pi_bot'
        self.bot = telepot.Bot(os.environ[self.botname])
        self.chat_id = os.environ[chat_id]
        self.bot.getMe()

    def get_text_message(self, mark_as_read=False):
        msg = self.bot.getUpdates()
        if msg:
            return self.extract_text_message(msg[-1], mark_as_read)
        return None

    def send_text_message(self, *message):
        message_str = ''
        for _msg in message:
            message_str += f'{_msg}'

        try:
            return self.bot.sendMessage(self.chat_id, message_str)
        except TelegramError as e:
            if e.error_code == 429:
                # If the error code is 429 (Too Many Requests), parse the Retry-After header value
                retry_after = int(e.response.get('Retry-After'))
                print(f"Rate limited. Waiting for {retry_after} seconds...")
                time.sleep(retry_after+1)
                return self.bot.sendMessage(self.chat_id, message_str)

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
        update_id = msg.get('update_id')
        _message = msg.get('message')
        if mark_as_read:
            self.bot.getUpdates(offset=update_id+1)
        return update_id, _message.get('chat').get('id'), _message.get('text')


if __name__ == '__main__':

    t_bot = TelegramBot()
    t_bot.send_text_message('Testing telegram utility function')
    t_bot.get_text_message()
