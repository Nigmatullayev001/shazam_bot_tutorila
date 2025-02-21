from aiogram import types, Router
from aiogram.filters import Command

router = Router()


@router.message(Command("help"))
async def send_welcome(message: types.Message):
    await message.answer(text="Sizga qanday yordam bera olaman?")