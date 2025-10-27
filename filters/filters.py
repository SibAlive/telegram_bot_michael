from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config import Config, load_config


config: Config = load_config()


class IsCorrectFullNameMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, str]:
        full_name = message.text.strip().split()
        if len(full_name) == 3:
            if all(s.isalpha() and len(s) >= 2 for s in full_name):
                return {'full_name': ' '.join(full_name)}
        return False


class IsCorrectAgeMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, str]:
        age = message.text.strip()
        if age.isdigit() and 0 < int(age) < 100:
            return {'age': age}
        return False


class ChooseTime(BaseFilter):
    async def __call__(self, callback_query):
        # print(message)
        if ':' in callback_query.data and callback_query.data.replace(':', '').isdigit():
            return True
        return False


class IsAdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery):
        user_id = event.from_user.id
        admin_ids = config.bot.admin_ids
        return user_id in admin_ids