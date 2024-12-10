import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from urllib.parse import urlparse, parse_qs
import requests

# Telegram and RapidAPI credentials
API_TOKEN = "7935133923:AAF-vcd1Of-tZPptfIbUVVMY3qezWTc-PKs"
RAPIDAPI_KEY = "b1173c1a80msh5a8b6302d359d65p1ff6e3jsnefbdad47bd40"

# Bot and Dispatcher objects
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# YouTube and Instagram API settings
RAPIDAPI_HOST_YOUTUBE = "youtube-media-downloader.p.rapidapi.com"
RAPIDAPI_HOST_INSTAGRAM = "instagram-post-reels-stories-downloader-api.p.rapidapi.com"

# Global variable to store user language preference
user_languages = {}


# Extract video ID from URL (supports YouTube Shorts)
def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query = parse_qs(parsed_url.query)
        if "v" in query:
            return query["v"][0]
        if parsed_url.path.startswith("/shorts/"):
            return parsed_url.path.split("/")[2]
    elif parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    return None


# Fetch YouTube video details
def fetch_video_details(video_id):
    endpoint = f"https://{RAPIDAPI_HOST_YOUTUBE}/v2/video/details"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST_YOUTUBE,
    }
    params = {"videoId": video_id}
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("videos", {}).get("items", [{}])[0].get("url")
    return None


# Fetch Instagram media
def fetch_instagram_media(url):
    endpoint = f"https://{RAPIDAPI_HOST_INSTAGRAM}/instagram/"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST_INSTAGRAM,
    }
    params = {"url": url}
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if data.get("status") and "result" in data:
            # Extract the first media item in the result array
            media = data["result"][0]['url']
            # media = data["result"][0]
            return media
        else:
            print('Ishlamadi')
            return None

    else:
        print(f"Error fetching Instagram media. Status: {response.status_code}, Response: {response.text}")
        return None
    # except requests.RequestException as e:
    #     print(f"Request error: {e}")
    #     return None


# Language selection keyboard
language_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
language_keyboard.add(KeyboardButton("🇺🇿 Uzbek"), KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇺🇸 English"))


# /start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_languages[message.chat.id] = "uz"  # Default language
    await message.reply("Tilni tanlang / Выберите язык / Choose a language:", reply_markup=language_keyboard)


# Handle language selection
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


# Process video request
@dp.message_handler()
async def process_video_request(message: types.Message):
    user_language = user_languages.get(message.chat.id, "uz")
    url = message.text

    if "youtube.com" in url or "youtu.be" in url:
        video_id = extract_video_id(url)
        if not video_id:
            response = {
                "uz": "Iltimos, to'g'ri YouTube yoki Shorts havolasini yuboring.",
                "ru": "Пожалуйста, отправьте правильную ссылку на YouTube или Shorts.",
                "en": "Please provide a valid YouTube or Shorts URL."
            }
            await message.reply(response[user_language])
            return

        await message.reply({
                                "uz": "YouTube videoni yuklab olayapman, iltimos kuting...",
                                "ru": "Загружаю видео с YouTube, пожалуйста, подождите...",
                                "en": "Downloading YouTube video, please wait..."
                            }[user_language])
        download_url = fetch_video_details(video_id)

        if download_url:
            await bot.send_video(message.chat.id, download_url)
        else:
            await message.reply({
                                    "uz": "Kechirasiz, videoni yuklab olishda xatolik yuz berdi.",
                                    "ru": "Извините, произошла ошибка при загрузке видео.",
                                    "en": "Sorry, there was an error downloading the video."
                                }[user_language])
    elif "instagram.com" in url:
        await message.reply({
                                "uz": "Instagram mediatsiyasini yuklab olayapman, iltimos kuting...",
                                "ru": "Загружаю медиа из Instagram, пожалуйста, подождите...",
                                "en": "Downloading Instagram media, please wait..."
                            }[user_language])
        media_url = fetch_instagram_media(url)
        print(media_url)
        # await asyncio.sleep(5)
        try:
            split_url = message.text.strip()  # Foydalanuvchi yuborgan URL
            parts = split_url.split('/')

            # Video va rasm uchun kengaytmalar
            extensions_to_find_vid = ['.mp4' or '.mov']
            extensions_to_find_img = ['.jpg' or '.png']

            # Kengaytmalarning mavjudligini tekshirish
            found_extensions_vid = [ext for ext in extensions_to_find_vid if ext in ''.join(parts)]
            found_extensions_img = [ext for ext in extensions_to_find_img if ext in ''.join(parts)]

            if found_extensions_vid is not []:
                await bot.send_video(message.chat.id, media_url, caption="Here is your video!")
            elif found_extensions_img is not []:
                await bot.send_photo(message.chat.id, media_url, caption="Here is your post image!")
            else:
                # Foydalanuvchi tili asosida xabar
                # user_language = 'en'  # Foydalanuvchi tilini aniqlash uchun kerakli mexanizmni qo'shing
                messages = {
                    "uz": "Kechirasiz, ushbu URL orqali media topilmadi yoki qo'llab-quvvatlanmaydi.",
                    "ru": "Извините, по этому URL не найдено подходящее медиа или оно не поддерживается.",
                    "en": "Sorry, no supported media found in the URL or it's not supported."
                }
                await message.reply(messages.get(user_language, messages["en"]))
        except Exception as e:
            logging.error(f"Error: {e}")
            await message.reply(
                "Xatolik: Iltimos, URL manzilni to'g'ri kiriting! "
                "⚠️Ogohlantirish: Faqat video va rasm fayllarni qo'llab-quvvatlaymiz!⚠️"
            )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
