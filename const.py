from NekoGram.storages.mysql import MySQLStorage
from NekoGram import Neko
from start_function import start_function
import aiogram
import os

token: str = os.getenv('bot_token')
bot_id: int = int(token.split(':')[0])
bot_name: str = os.getenv('bot_name')

bot: aiogram.Bot = aiogram.Bot(token, parse_mode='HTML')
dp: aiogram.Dispatcher = aiogram.Dispatcher(bot)


neko: Neko = Neko(dp=dp, storage=MySQLStorage(database=os.getenv('mysql_database'), user=os.getenv('mysql_user'),
                                              password=os.getenv('mysql_password')), start_function=start_function,
                  only_messages_in_functions=True)
