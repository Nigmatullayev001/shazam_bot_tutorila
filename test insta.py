import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Fetch API tokens from environment variables
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN") or "7935133923:AAF-vcd1Of-tZPptfIbUVVMY3qezWTc-PKs"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") or "b1173c1a80msh5a8b6302d359d65p1ff6e3jsnefbdad47bd40"
RAPIDAPI_HOST_INSTAGRAM = "instagram-post-reels-stories-downloader-api.p.rapidapi.com"

if not API_TOKEN or not RAPIDAPI_KEY:
    raise ValueError("API_TOKEN and RAPIDAPI_KEY must be set in environment variables.")

# Bot and Dispatcher objects
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Language selection keyboard
language_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
language_keyboard.add(
    KeyboardButton("🇺🇿 Uzbek"),
    KeyboardButton("🇷🇺 Русский"),
    KeyboardButton("🇺🇸 English"),
)

# Global dictionary to store user language preferences
user_languages = {}


# /start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_languages[message.chat.id] = "en"  # Default language
    await message.reply(
        "Tilni tanlang / Выберите язык / Choose a language:",
        reply_markup=language_keyboard,
    )


# Language selection handler
@dp.message_handler(lambda message: message.text in ["🇺🇿 Uzbek", "🇷🇺 Русский", "🇺🇸 English"])
async def set_language(message: types.Message):
    if message.text == "🇺🇿 Uzbek":
        user_languages[message.chat.id] = "uz"
        await message.reply("Til muvaffaqiyatli tanlandi. Endi havolani yuboring!")
    elif message.text == "🇷🇺 Русский":
        user_languages[message.chat.id] = "ru"
        await message.reply("Язык успешно выбран. Теперь отправьте ссылку!")
    elif message.text == "🇺🇸 English":
        user_languages[message.chat.id] = "en"
        await message.reply("Language successfully set. Now send a link!")


# Fetch Instagram media (post, story, reels)
def fetch_instagram_media(url):
    endpoint = f"https://{RAPIDAPI_HOST_INSTAGRAM}/instagram/"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST_INSTAGRAM,
    }
    params = {"url": url}

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") and "result" in data:
            return data["result"]
        return None
    except requests.RequestException as e:
        print(f"Error fetching Instagram media: {e}")
        return None


# Handle Instagram media
@dp.message_handler(lambda message: "instagram.com" in message.text)
async def handle_instagram_url(message: types.Message):
    user_language = user_languages.get(message.chat.id, "en")
    url = message.text

    messages = {
        "uz": "Instagram mediatsiyasini yuklab olayapman, iltimos kuting...",
        "ru": "Загружаю медиа из Instagram, пожалуйста, подождите...",
        "en": "Downloading Instagram media, please wait...",
    }

    await message.reply(messages[user_language])

    media_items = fetch_instagram_media(url)
    print(media_items)
    if media_items:
        for media in media_items:
            media_url = media.get("url")

            # '.mp4' in media_url
            # '.mov' in media_url
            if '.mov' in media_url or '.mp4' in media_url:
                await bot.send_video(message.chat.id, media_url, caption="Here is your video!")

            #     ['.png' or 'jpg' or 'jpeg'] in media_url
            elif '.png' in media_url or '.jpg' in media_url or '.jpeg' in media_url:
                await bot.send_photo(message.chat.id, media_url, caption="Here is your image!")
            else:
                unsupported_msg = {
                    "uz": "Ushbu turdagi media qo'llab-quvvatlanmaydi.",
                    "ru": "Этот тип медиа не поддерживается.",
                    "en": "This type of media is not supported.",
                }
                await message.reply(unsupported_msg[user_language])
    else:
        error_msg = {
            "uz": "Kechirasiz, mediatsiya topilmadi.",
            "ru": "Извините, медиа не найдено.",
            "en": "Sorry, no media found.",
        }
        await message.reply(error_msg[user_language])


# Default message handler
@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(f"You said: {message.text}")


# Start polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
