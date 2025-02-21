from aiogram import Router
from .users import start, help, shazam_bot

def setup_message_routers() -> Router:

    router = Router()

    # users
    router.include_router(start.router)
    router.include_router(shazam_bot.router)
    router.include_router(help.router)

    # groups

    return router