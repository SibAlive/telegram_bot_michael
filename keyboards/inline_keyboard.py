from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon import RU


def create_keyboard_confirm():
    # инлайн кнопки подтверждения данных
    buttons = [
        [InlineKeyboardButton(text=RU.get('correct'), callback_data='correct'),
         InlineKeyboardButton(text=RU.get('confirm'), callback_data='confirm')
         ]
    ]
    inline_keyboard_confirm = InlineKeyboardMarkup(
        inline_keyboard=buttons,
        one_time_keyboard=True
    )
    return inline_keyboard_confirm


def create_keyboard_employee():
    # инлайн кнопки выбора врача
    buttons = [
        [InlineKeyboardButton(text="Хирург", callback_data='Хирург'),
         InlineKeyboardButton(text="Лор", callback_data='Лор')
         ],
        [InlineKeyboardButton(text="Окулист", callback_data='Окулист'),
         InlineKeyboardButton(text="Невролог", callback_data='Невролог')
         ],
        [InlineKeyboardButton(text="Отмена", callback_data='Отмена')]
    ]
    inline_keyboard_confirm = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return inline_keyboard_confirm


def create_keyboard_day():
    # инлайн кнопки выбора дня посещения
    buttons = [
        [InlineKeyboardButton(text="Сегодня", callback_data='Сегодня'),
         InlineKeyboardButton(text="Завтра", callback_data='Завтра')
         ],
        [InlineKeyboardButton(text="Назад", callback_data='Назад')]
    ]
    inline_keyboard_confirm = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return inline_keyboard_confirm


def create_keyboard_time(times):
    builder = InlineKeyboardBuilder()

    for time in times:
        builder.row(
            InlineKeyboardButton(text=time, callback_data=time)
        )
    builder.button(text="Назад", callback_data="Назад к дате")

    builder.adjust(2)

    return builder.as_markup()


def create_keyboard_broadcast():
    buttons = [
        [InlineKeyboardButton(text='Сообщение', callback_data='message'),
         InlineKeyboardButton(text='Фото', callback_data='photo')
         ],
        [InlineKeyboardButton(text='Видео', callback_data='video'),
         InlineKeyboardButton(text='Документ', callback_data='document')
         ],
        [InlineKeyboardButton(text='Отмена', callback_data='cancel_broadcast')]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return inline_keyboard


def create_keyboard_affirm_broadcast():
    buttons = [
        [InlineKeyboardButton(text='Разослать', callback_data='broadcast_send')],
        [InlineKeyboardButton(text='Отмена', callback_data='broadcast_send_cancel')]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return inline_keyboard


def create_keyboard_broadcast_caption():
    buttons = [
        [InlineKeyboardButton(text='Без описания', callback_data='no_caption'),
         ]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return inline_keyboard


def create_keyboard_back_to_broadcast():
    buttons = [
        [InlineKeyboardButton(text='Назад', callback_data='back_to_broadcast'),
         ]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return inline_keyboard