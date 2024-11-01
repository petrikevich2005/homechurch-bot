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

    def create_keyboard(self, button: dict, columns: int) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(row_width=columns)
        _buttons = [
            types.InlineKeyboardButton(
                text=child["text"], callback_data=child.get("data"), url=child.get("url")
            )
            for child in button["children"]
        ]
        keyboard.add(*_buttons)
        return keyboard

    def edit_keyboard_message(
        self,
        callback: types.CallbackQuery,
        button: dict,
        reply: str | None = None,
        columns: int = 2,
    ) -> None:
        self.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=reply if reply else button["reply"],
            reply_markup=self.create_keyboard(button, columns),
        )

    def send_keyboard_message(
        self, message: types.Message, button: dict, reply: str | None = None, columns: int = 2
    ) -> None:
        self.bot.send_message(
            message.chat.id,
            reply if reply else button["reply"],
            reply_markup=self.create_keyboard(button, columns),
        )
