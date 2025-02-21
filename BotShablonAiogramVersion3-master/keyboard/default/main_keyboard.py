from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def menu():
    button = KeyboardButton(text="User")

    rkm = ReplyKeyboardMarkup(
        keyboard=[
            [button]
        ],
        resize_keyboard=True)
    return rkm


def back():
    button = KeyboardButton(text="Back")

    rkm = ReplyKeyboardMarkup(
        keyboard=[
            [button]
        ],
        resize_keyboard=True)
    return rkm