from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand

from lexicon import RU


def create_main_menu():
    """Создает главное меню"""
    return [
        BotCommand(
            command="/start",
            description=RU.get("/start_desc")
        ),
        BotCommand(
            command="/finance",
            description=RU.get("/finance_desc")
        ),
        BotCommand(
            command="/call",
            description=RU.get("/call_desc")
        ),
        BotCommand(
            command="/appoint",
            description=RU.get("/appoint_desc")
        ),
    ]


def create_share_phone_keyboard():
    # Создаем объекты кнопок
    share_phone_button = KeyboardButton(text=RU.get("share_phone"), request_contact=True)

    # Создаем объект клавиатуры
    share_phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[[share_phone_button]],
    resize_keyboard=True,
    )

    return share_phone_keyboard