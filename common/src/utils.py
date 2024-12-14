# utils_module
import logging

import telebot
from telebot import types


# logger settings
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler("bot.log")
    handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | (%(levelname)s): %(message)s (Line:" + "%(lineno)d) [%(filename)s]",
        datefmt="%d-%m-%Y %I:%M:%S",
    )

    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger


class TelebotTools:
    def __init__(self, bot: telebot.TeleBot) -> None:
        self.bot = bot

    def create_keyboard(
        self, row_width: int, children: list[dict[str, str]]
    ) -> types.InlineKeyboardMarkup:
        if row_width > 0:
            keyboard = types.InlineKeyboardMarkup(row_width=row_width)
            _buttons = [
                types.InlineKeyboardButton(
                    text=child["text"], callback_data=child.get("data"), url=child.get("url")
                )
                for child in children["children"]
            ]
            keyboard.add(*_buttons)
            return keyboard
        else:
            return None

    def edit_keyboard_message(
        self,
        callback: types.CallbackQuery,
        children: list[dict[str, str]],
        reply: str | None = None,
    ) -> None:
        row_width = children["row_width"]
        self.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=reply if reply else children["reply"],
            reply_markup=self.create_keyboard(row_width, children),
            parse_mode="Markdown",
        )

    def send_keyboard_message(
        self,
        chat_id: int,
        children: dict,
        reply: str | None = None,
    ) -> None:
        row_width = children["row_width"]
        self.bot.send_message(
            chat_id,
            reply if reply else children["reply"],
            reply_markup=self.create_keyboard(row_width, children),
        )
