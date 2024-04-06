"""
    Program to check rpi temperature & send notification to telegram
    Simply set this up as hourly cron
    $ crontab -e
    @hourly cd /home/pi/pi-telegram-bot && nohup python3 temperature_monitor_cron.py >> log.txt &
"""
import os
import telepot
import time
from bot_utils import BotSwitch
import re
from dotenv import load_dotenv

load_dotenv('telegram.env')

botname = 'aqua4_pi_bot'  # bot secret will be stored in the env var with this key
bot = telepot.Bot(os.environ[botname])
chat_id = os.environ['chat_id']
bot.getMe()

commands = BotSwitch()
temp = commands.intent('temperature')
_temp = re.findall("\d+\.\d+", temp)[0]
print(_temp, temp)
if  float(_temp) > 55:
    bot.sendMessage(
        chat_id, f'Temperature alert: System temperature is {temp}, please check fan')
    # please check fan
    # please check the owner of this heavy process
