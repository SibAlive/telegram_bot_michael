import logging
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

from lexicon import RU


logger = logging.getLogger(__name__)

other_router = Router()


# Этот хэндлер будет срабатывать на все текстовые сообщения
@other_router.message(StateFilter(default_state))
async def process_any_message(message: Message, state: FSMContext):
    logger.debug(f"Входим в хэндлер любое сообщение")
    sent = await message.answer(text=RU.get("Unknown command"))
    await state.update_data(message_ids=[sent.message_id])
    logger.debug(f"Выходим из хэндлера любое сообщение")