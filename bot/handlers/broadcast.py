"""Массовая рассылка"""
import logging
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
from aiogram.fsm.state import default_state
from aiogram.filters import Command, StateFilter
import asyncio

from bot import keyboards as kb, services as ser
from bot.FSM import BroadcastForm
from bot.filters import IsAdminFilter
from bot.lexicon import RU


logger = logging.getLogger(__name__)

# Инициализируем роутер модуля
broadcast_router = Router()

# Подключаем фильтр UserRoleFilter ко всем хэндлерам роутера
broadcast_router.message.filter(IsAdminFilter())


# Обрабатываем команду админа /broadcast (массовая рассылка)
@broadcast_router.message(StateFilter(default_state), Command('broadcast'))
async def broadcast_handler(message, state):
    sent = await message.answer(
        text=RU.get('broadcast'),
        reply_markup=kb.create_keyboard_broadcast()
    )

    await state.set_state(BroadcastForm.choose)  # Устанавливаем состояние ожидания выбора типа сообщения
    await state.update_data(message_ids=[sent.message_id])


# Выбрано сообщение
@broadcast_router.callback_query(BroadcastForm.choose, F.data == "message")
async def message_process(callback, state):
    await callback.message.edit_text(
        text="Введите текст сообщения:",
        reply_markup=kb.create_keyboard_back_to_broadcast()
    )
    await state.set_state(BroadcastForm.message)  # Устанавливаем состояние ожидания ввода сообщения


# Отправка тестового сообщения для рассылки
@broadcast_router.message(BroadcastForm.message)
async def test_message_send_process(message, state):
    sent_1 = await message.answer(text="Ваше сообщение выглядит так:")
    await message.answer(text=message.text)
    sent_2 = await message.answer(
        text="Хотите разослать сообщение всем пользователям?",
        reply_markup=kb.create_keyboard_affirm_broadcast()
    )

    await state.set_state(BroadcastForm.confirm)
    await state.update_data(message_id=message.message_id,
                            chat_id= message.chat.id,
                            message_ids=[sent_1.message_id, sent_2.message_id])


# Выбрано фото, видео или документ
@broadcast_router.callback_query(BroadcastForm.choose, F.data.in_(['photo', 'video', 'document']))
async def media_process(callback, state):
    await state.update_data(file_type=callback.data) # Сохраняем тип выбранного файла

    await callback.message.edit_text(
        text="Загрузите файл",
        reply_markup=kb.create_keyboard_back_to_broadcast()
    )
    await state.set_state(BroadcastForm.file)  # Устанавливаем состояние ожидания загрузки файла


# Загрузка файла для рассылки
@broadcast_router.message(BroadcastForm.file)
async def test_file_send_process(message, state):
    data = await state.get_data()
    file_type = data.get("file_type")

    if file_type != message.content_type:
        await message.answer("Загружен некорректный тип файла")
    else:
        if message.content_type == "photo":
            await state.update_data(file_id=message.photo[-1].file_id)
        elif message.content_type == "video":
            await state.update_data(file_id=message.video.file_id)
        elif message.content_type == "document":
            await state.update_data(file_id=message.document.file_id)

        sent = await message.answer(text="Введите описание (необязательно)",
                             reply_markup=kb.create_keyboard_broadcast_caption()
        )

        await state.update_data(message_ids=[sent.message_id])
        await state.set_state(BroadcastForm.caption)  # Устанавливаем состояние ожидания описания файла


# Отправка тестового сообщения с файлом для рассылки
@broadcast_router.message(BroadcastForm.caption)
async def enter_caption_process(message, bot, state):
    data = await state.get_data()
    file_type = data.get("file_type")
    file_id = data.get("file_id")
    caption = message.text
    chat_id = message.chat.id

    sent_1 = await message.answer(text="Ваше сообщение выглядит так:")
    media_msg = await ser.send_test_message_broadcast(bot=bot,
                                      chat_id=chat_id,
                                      file_type=file_type,
                                      file_id=file_id,
                                      caption=caption
    )
    sent_2 = await message.answer(
        text="Хотите разослать сообщение всем пользователям?",
        reply_markup=kb.create_keyboard_affirm_broadcast()
    )

    await state.set_state(BroadcastForm.confirm)  # Устанавливаем состояние ожидания подтверждения отправки
    await state.update_data(message_id=media_msg.message_id,
                            chat_id=message.chat.id,
                            message_ids=[sent_1.message_id, sent_2.message_id])


# Описание не требуется
@broadcast_router.callback_query(BroadcastForm.caption, F.data == "no_caption")
async def no_caption_process(callback, bot, state):
    data = await state.get_data()
    file_type = data.get("file_type")
    file_id = data.get("file_id")
    chat_id = callback.message.chat.id

    sent_1 = await callback.message.edit_text(text="Ваше сообщение выглядит так:",
                                         reply_markup=None)
    media_msg = await ser.send_test_message_broadcast(bot=bot,
                                      chat_id=chat_id,
                                      file_type=file_type,
                                      file_id=file_id,
                                      )
    sent_2 = await callback.message.answer(
        text="Хотите разослать сообщение всем пользователям?",
        reply_markup=kb.create_keyboard_affirm_broadcast()
    )

    await state.set_state(BroadcastForm.confirm)
    await state.update_data(message_id=media_msg.message_id,
                            chat_id=callback.message.chat.id,
                            message_ids=[sent_1.message_id, sent_2.message_id])


# Рассылка сообщения всем пользователям
@broadcast_router.callback_query(BroadcastForm.confirm, F.data == "broadcast_send")
async def message_send_process(callback, bot, state, session):
    data = await state.get_data()
    message_id = data.get("message_id")
    chat_id = callback.message.chat.id

    user_service = ser.UserService(session)

    telegram_ids = await user_service.get_users_list_for_broadcast()
    for telegram_id in telegram_ids:
        try:
            await bot.copy_message(chat_id=telegram_id, from_chat_id=chat_id, message_id=message_id)
            await asyncio.sleep(0.05)
        except TelegramAPIError:
            continue

    # await callback.answer() # Убираем переливание инлайн кнопки
    await callback.message.edit_text(
        text="Сообщение разослано",
        reply_markup=None
    )

    # Сбрасываем форму заполнения данных
    await state.update_data(text=None)
    await state.set_state()


# Нажатие кнопки назад (после выбора типа сообщения)
@broadcast_router.callback_query(F.data == "back_to_broadcast")
async def back_to_broadcast_process(callback, state):
    await callback.message.edit_text(
        text=RU.get('broadcast'),
        reply_markup=kb.create_keyboard_broadcast()
    )
    await state.set_state(BroadcastForm.choose)


# Отмена рассылки (после просмотра тестового сообщения)
@broadcast_router.callback_query(BroadcastForm.confirm, F.data == "broadcast_send_cancel")
async def test_message_cancel_send_process(callback, state):

    try:
        await callback.message.edit_text(
            text="Рассылка отменена!",
            reply_markup=None
        )
    except TelegramBadRequest:
        await callback.message.answer("Рассылка отменена")

    # Сбрасываем форму заполнения данных
    await state.update_data(text=None)
    await state.set_state()


# Кнопка отмена в клавиатуре broadcast
@broadcast_router.callback_query(BroadcastForm.choose, F.data == "cancel_broadcast")
async def cancel_process(callback, state):
    await callback.message.edit_text(
        text="Вы вышли из заполнения массовой рассылки",
        reply_markup=None
    )
    # Сбрасываем форму заполнения данных
    await state.update_data(text=None)