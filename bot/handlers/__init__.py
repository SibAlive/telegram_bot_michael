from aiogram import Router

from .broadcast import broadcast_router
from .user import user_router
from .other import other_router


router = Router()
router.include_routers(broadcast_router, user_router, other_router)