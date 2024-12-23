import os

from dotenv import load_dotenv
import telebot
from telebot import types
import yaml

from bot.src.data_processing import DataProcessing
from bot.src.sqlite import SQLite
from common import utils


REGISTRATION_STATUS = True
timeout = []


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
@bot.message_handler(commands=["start"])
def welcome(message: types.Message) -> None:
    if not sql.check_available_user_in_database(message.from_user.id, message.from_user.username):
        sql.add_to_database(
            message.from_user.id, message.from_user.username, message.from_user.first_name
        )
    tools.send_keyboard_message(
        message.chat.id,
        buttons["welcome"],
        reply=buttons["welcome"]["reply"].format(first_name=message.from_user.first_name),
    )


# open menu
@bot.message_handler(commands=["menu"])
def open_menu(message: types.Message) -> None:
    if not sql.check_available_user_in_database(message.from_user.id, message.from_user.username):
        sql.add_to_database(
            message.from_user.id, message.from_user.username, message.from_user.first_name
        )
    tools.send_keyboard_message(message.chat.id, buttons["menu"])


# update command
@bot.message_handler(commands=["update"])
def update(message: types.Message) -> None:
    if not sql.check_available_user_in_database(message.from_user.id, message.from_user.username):
        sql.add_to_database(
            message.from_user.id, message.from_user.username, message.from_user.first_name
        )
    tools.send_keyboard_message(message.chat.id, buttons["update"])


# render global menu
@bot.callback_query_handler(func=lambda callback: callback.data == "menu")
def menu(callback: types.CallbackQuery) -> None:
    tools.edit_keyboard_message(callback, buttons["menu"])


# menu of secret angel before
@bot.callback_query_handler(
    func=lambda callback: callback.data == "secret_angel" and REGISTRATION_STATUS
)
def secret_angel_before(callback: types.CallbackQuery) -> None:
    available = sql.get_angel_status(callback.from_user.id)
    wish_available = sql.get_wish(callback.from_user.id) is not None
    if not available:
        children = buttons["secret_angel_before"]["not_available"]
    else:
        children = buttons["secret_angel_before"]["available"][
            "wish_available" if wish_available else "wish_not_available"
        ]
    tools.edit_keyboard_message(
        callback,
        children,
        reply=None
        if not available or not wish_available
        else buttons["secret_angel_before"]["available"]["wish_available"]["reply"].format(
            wish=sql.get_wish(callback.from_user.id)
        ),
    )


# menu of secret angel after
@bot.callback_query_handler(
    func=lambda callback: callback.data == "secret_angel" and not REGISTRATION_STATUS
)
def secret_angel_after(callback: types.CallbackQuery) -> None:
    available = sql.get_angel_status(callback.from_user.id)

    if available:
        children = buttons["secret_angel_after"]["available"]
        data = sql.get_data(sql.get_angel(callback.from_user.id))
        tools.edit_keyboard_message(
            callback,
            children,
            reply=children["reply_with_wish"].format(
                first_name=data["first_name"] if data["first_name"] is not None else "",
                username=data["username"] if data["username"] is not None else "unnamed",
                wish=data["wish"],
            )
            if data["wish"] is not None
            else children["reply_without_wish"].format(
                first_name=data["first_name"] if data["first_name"] is not None else "",
                username=data["username"] if data["username"] is not None else "",
            ),
        )
    else:
        tools.edit_keyboard_message(callback, buttons["secret_angel_after"]["not_available"])


# add user to secret angel
@bot.callback_query_handler(func=lambda callback: callback.data == "add_to_secret_angel")
def add_to_secret_angel(callback: types.CallbackQuery) -> None:
    if callback.from_user.username is not None:
        sql.check_available_user_in_database(callback.from_user.id, callback.from_user.username)
        if REGISTRATION_STATUS:
            sql.set_angel_status(callback.from_user.id, True)
            tools.edit_keyboard_message(callback, buttons["add_to_secret_angel"])
        else:
            tools.edit_keyboard_message(callback, buttons["registration_timeout"])
    else:
        if callback.from_user.id not in timeout:
            tools.send_keyboard_message(callback.from_user.id, buttons["username_not_found"])
            timeout.append(callback.from_user.id)


# remove user from secret angel
@bot.callback_query_handler(func=lambda callback: callback.data == "remove_from_secret_angel")
def remove_from_secret_angel(callback: types.CallbackQuery) -> None:
    if REGISTRATION_STATUS:
        sql.set_angel_status(callback.from_user.id, False)
        tools.edit_keyboard_message(callback, buttons["remove_from_secret_angel"])
    else:
        tools.edit_keyboard_message(callback, buttons["registration_timeout"])


# set wish of user
@bot.callback_query_handler(func=lambda callback: callback.data == "set_wish")
def set_wish_for_user(callback: types.CallbackQuery) -> None:
    if REGISTRATION_STATUS:
        tools.edit_keyboard_message(callback, buttons["set_wish"])
        bot.register_next_step_handler(callback.message, write_wish_to_database)
    else:
        tools.edit_keyboard_message(callback, buttons["registration_timeout"])


def write_wish_to_database(message: types.Message) -> None:
    if REGISTRATION_STATUS:
        sql.set_wish(message.from_user.id, message.text)
        tools.send_keyboard_message(message.chat.id, buttons["set_wish_success"])
    else:
        tools.send_keyboard_message(message.from_user.id, buttons["registration_timeout"])


# randomize secret angels
@bot.message_handler(commands=["randomize"])
def randomize_secret_angels(message: types.Message) -> None:
    global REGISTRATION_STATUS  # noqa: PLW0603
    if sql.get_admin_status(message.from_user.id) and REGISTRATION_STATUS:
        REGISTRATION_STATUS = False
        logger.info("randomize...")
        users = sql.get_users_list()
        parallel = DataProcessing.random_users(users=users)
        sql.set_angels(users, parallel)

        for user_id in users:
            tools.send_keyboard_message(user_id, buttons["randomized"])


# what's next
@bot.callback_query_handler(func=lambda callback: callback.data == "what_next")
def what_next(callback: types.CallbackQuery) -> None:
    tools.edit_keyboard_message(
        callback,
        buttons["what_next"],
        reply=buttons["what_next"]["reply"].format(first_name=callback.from_user.first_name),
    )


# how it work
@bot.callback_query_handler(func=lambda callback: callback.data == "how_it_work")
def how_it_work(callback: types.CallbackQuery) -> None:
    tools.edit_keyboard_message(callback, buttons["how_it_work"])


# START BOT
logger.info("START BOT...")
bot.infinity_polling()
