from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def resume_button():
    button = KeyboardButton(text="Bosh ofis")
    button2 = KeyboardButton(text="Toshkent")
    button3 = KeyboardButton(text="Sirdaryo")
    button4 = KeyboardButton(text="Toshkent viloyati")
    button5 = KeyboardButton(text="◀️ Orqaga")

    rkm = ReplyKeyboardMarkup(
        keyboard=[
            [button, button2],
            [button3, button4],
            [button5],
        ],
        resize_keyboard=True)
    return rkm