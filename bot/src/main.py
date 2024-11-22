import os

from dotenv import load_dotenv
import telebot
from telebot import types
import yaml

from bot.src.sqlite import SQLite
from common import utils


GAME_STATUS = True


env_file = "bot/.env"
read = load_dotenv(env_file)

buttons_file = "bot/resources/buttons.yaml"
with open(buttons_file, encoding="utf-8") as f:
    buttons = yaml.safe_load(f)

token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)

logger = utils.get_logger(__name__)

sql_file = "bot/data.db"
sql = SQLite(sql_file)
tools = utils.TelebotTools(bot)


# echo command
@bot.message_handler(regexp="^echo ")
def echo(message: types.Message) -> None:
    bot.send_message(message.from_user.id, message.text[5:])


# welcome command
@bot.message_handler(commands=["start", "menu"])
def welcome(message: types.Message) -> None:
    if not sql.check_available_user_in_database(message.from_user.id):
        sql.add_to_database(
            message.from_user.id, message.from_user.username, message.from_user.first_name
        )
    tools.send_keyboard_message(
        message,
        buttons["welcome"],
        reply=buttons["welcome"]["reply"].format(first_name=message.from_user.first_name),
    )


# render global menu
@bot.callback_query_handler(func=lambda callback: callback.data == "menu")
def menu(callback: types.CallbackQuery) -> None:
    tools.edit_keyboard_message(callback, buttons["menu"])


# menu of secret angel
@bot.callback_query_handler(func=lambda callback: callback.data == "secret_angel")
def secret_angel(callback: types.CallbackQuery) -> None:
    available = sql.get_angel_status(callback.from_user.id)
    children = (
        buttons["secret_angel"]["available"]
        if available
        else buttons["secret_angel"]["not_available"]
    )
    tools.edit_keyboard_message(
        callback,
        children,
        reply=buttons["secret_angel"]["available"]["reply"].format(
            first_name="ИМЯ",
            username="username",
            wish="пожелания",
        )
        if available
        else None,
    )


# add user to secret angel
@bot.callback_query_handler(func=lambda callback: callback.data == "add_to_secret_angel")
def add_to_secret_angel(callback: types.CallbackQuery) -> None:
    if GAME_STATUS:
        sql.set_angel_status(callback.from_user.id, True)
        tools.edit_keyboard_message(callback, buttons["add_to_secret_angel"])
    else:
        tools.edit_keyboard_message(callback, buttons["registration_timeout"])


# remove user from secret angel
@bot.callback_query_handler(func=lambda callback: callback.data == "remove_from_secret_angel")
def remove_from_secret_angel(callback: types.CallbackQuery) -> None:
    if GAME_STATUS:
        sql.set_angel_status(callback.from_user.id, False)
        tools.edit_keyboard_message(callback, buttons["remove_from_secret_angel"])
    else:
        tools.edit_keyboard_message(callback, buttons["registration_timeout"])


# START BOT
logger.info("START BOT...")
bot.infinity_polling()
