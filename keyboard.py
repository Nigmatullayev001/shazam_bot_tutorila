import requests
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup




def keylang():
    rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    rkm.add(KeyboardButton('Русский 🇷🇺'), KeyboardButton('Oʻzbek 🇺🇿'), KeyboardButton('English 🇬🇧'))
    return rkm
# print(video_downloader(
#     link="https://www.instagram.com/p/C6EcQJLtDte/?utm_source=ig_web_button_share_sheet"))
# print(video(link="https://www.instagram.com/p/C6_mkPCtAjI/"))
