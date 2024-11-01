import os

from dotenv import load_dotenv
import telebot
from telebot import types
import yaml

from bot.src.sqlite import SQLite
from common import utils


env_file = "bot/.env"
read = load_dotenv(env_file)

buttons_file = "bot/resources/buttons.yaml"
with open(buttons_file, encoding="utf-8") as f:
    buttons = yaml.safe_load(f)

token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)

logger = utils.get_logger(__name__)

sql = SQLite()
tools = utils.TelebotTools(bot)


# echo command
@bot.message_handler(regexp="^echo ")
def echo(message: types.Message) -> None:
    bot.send_message(message.from_user.id, message.text[5:])


bot.infinity_polling()
