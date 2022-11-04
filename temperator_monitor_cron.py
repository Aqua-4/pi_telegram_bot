
import os
import telepot
import time
from utils import BotSwitch
import re
from dotenv import load_dotenv

load_dotenv()


# TOKEN = sys.argv[1]  # get token from command-line
# print(os.environ)
# aqua4_pi_bot
botname = 'aqua4_pi_bot'  # bot secret will be stored in the env var with this key
bot = telepot.Bot(os.environ[botname])
bot.getMe()

while True:
    commands = BotSwitch()
    temp = commands.intent('temperature')
    _temp = re.findall("\d+\.\d+", temp)[0]
    # if  float(_temp) > 59:
    bot.sendMessage(
        '5502113781', f'Temperature alert: System temperature is {temp}, please check')
    # please check fan
    # please check the owner of this heavy process
    time.sleep(3600)
