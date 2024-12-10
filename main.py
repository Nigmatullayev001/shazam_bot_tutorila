
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram.utils import executor
import os

# RapidAPI ma'lumotlari
RAPIDAPI_HOST = "shazam.p.rapidapi.com"
RAPIDAPI_KEY = "b1173c1a80msh5a8b6302d359d65p1ff6e3jsnefbdad47bd40"

# Telegram Bot tokeni
API_TOKEN = "7425388036:AAFBeVBcOVJrRSGi33KFhidrrKZZucGxECE"

# Loglar sozlamasi
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlari
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Videoni API orqali aniqlash
def recognize_video_with_api(file_path):
    url = f"https://{RAPIDAPI_HOST}/songs/v2/detect"
    headers = {
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "Content-Type": "application/octet-stream",
    }
    try:
        with open(file_path, "rb") as file:
            response = requests.post(url, headers=headers, data=file)
        # Javobni tekshirish
        if response.status_code == 200:
            try:
                return response.json()  # JSON formatida ma'lumot
            except ValueError:
                logging.error("Javob JSON formatida emas: %s", response.text)
                return {"error": "Javob JSON formatida emas"}
        else:
            logging.error("Server xatosi. Status kod: %d, Javob: %s", response.status_code, response.text)
            return {"error": f"Status kod: {response.status_code}, Javob: {response.text}"}
    except Exception as e:
        logging.error("API so'rovida xato: %s", str(e))
        return {"error": str(e)}

# /start buyrug'iga javob
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Salom! Menga video yuboring, men undagi qo'shiqni aniqlashga harakat qilaman.")

# Video fayllarni qayta ishlash
@dp.message_handler(content_types=ContentType.VIDEO)
async def handle_video(message: types.Message):
    # Video faylni yuklab olish
    video = await message.video.get_file()
    video_path = f"{video.file_id}.mp4"
    await bot.download_file(video.file_path, video_path)

    try:
        # Video faylni to'g'ridan-to'g'ri API orqali aniqlash
        result = recognize_video_with_api(video_path)
        if "error" in result:
            await message.reply(f"Xatolik yuz berdi: {result['error']}")
        else:
            track_info = result.get("track", {})
            title = track_info.get("title", "Noma'lum")
            subtitle = track_info.get("subtitle", "Noma'lum")
            await message.reply(f"Qo'shiq: {title}\nIjrochi: {subtitle}")
    except Exception as e:
        await message.reply(f"Xatolik yuz berdi: {e}")
    finally:
        # Faylni o'chirish
        os.remove(video_path)

@dp.message_handler(content_types=ContentType.TEXT)
async def handle_text(message: types.Message):
    await message.reply("Salom! Menga video yuboring! Men uni qo'shiq nomini topib beraman")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
