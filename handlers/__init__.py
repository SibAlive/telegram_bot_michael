from aiogram import Router

from .user import user_router
from .other import other_router


router = Router()
router.include_routers(user_router, other_router)