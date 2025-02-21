from aiogram import types, Router, F
from aiogram.filters import Command


router = Router()

admins = ["1707418028",]


@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(text=f"Salom sizni botga /start berdingiz")


