import os
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import yt_dlp

BOT_TOKEN = '7425388036:AAFBeVBcOVJrRSGi33KFhidrrKZZucGxECE'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


def search_songs(song_name):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_url = f"ytsearch10:{song_name}"
            info = ydl.extract_info(search_url, download=False)
            return [(entry['title'], entry['id']) for entry in info['entries']]
    except Exception as e:
        print(f"Error searching songs: {e}")
        return []

def download_audio(song_id, output_dir="downloads"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'quiet': False,  # Loglarni ko'rish uchun False qiling
    }
    os.makedirs(output_dir, exist_ok=True)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = f"https://www.youtube.com/watch?v={song_id}"
            info = ydl.extract_info(url, download=True)
            file_path = f"{output_dir}/{info['title']}.mp3"
            if os.path.exists(file_path):
                return file_path
            else:
                print(f"File not found after download: {file_path}")
    except Exception as e:
        print(f"Error downloading: {e}")
    return None


def convert_webm_to_mp3(webm_file):
    if not os.path.exists(webm_file):
        print(f"File does not exist: {webm_file}")
        return None

    mp3_file = os.path.splitext(webm_file)[0] + '.mp3'

    try:
        subprocess.run(['ffmpeg', '-i', webm_file, '-vn', '-ab', '192k', mp3_file], check=True)
        print(f"Converted: {webm_file} -> {mp3_file}")
        os.remove(webm_file)  # Remove the original .webm file
        return mp3_file
    except Exception as e:
        print(f"Error converting {webm_file}: {e}")
        return None


def create_inline_keyboard(suggestions):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for title, song_id in suggestions:
        button = InlineKeyboardButton(text=title, callback_data=song_id)
        keyboard.add(button)
    return keyboard


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Salom! Qo'shiq nomini yuboring, men topib beraman va uni MP3 formatda jo'nataman.")


@dp.message_handler()
async def find_and_send_music(message: types.Message):
    song_name = message.text
    await message.reply(f"'{song_name}' uchun izlanmoqda...")

    suggestions = search_songs(song_name)

    if suggestions:
        keyboard = create_inline_keyboard(suggestions)
        await message.reply("Mana natijalar:", reply_markup=keyboard)
    else:
        await message.reply("Kechirasiz, hech qanday natija topilmadi.")


@dp.callback_query_handler()
async def handle_callback(callback_query: types.CallbackQuery):
    song_id = callback_query.data
    await bot.answer_callback_query(callback_query.id, "Qo'shiq yuklanmoqda...")

    # Download the song
    audio_file = download_audio(song_id)

    # Validate the audio_file before proceeding
    if not audio_file:
        await bot.send_message(callback_query.message.chat.id, "Kechirasiz, qo'shiqni yuklab bo'lmadi.")
        return

    # Convert .webm to .mp3 if necessary
    if audio_file.endswith('.webm'):
        audio_file = convert_webm_to_mp3(audio_file)
        if not audio_file:
            await bot.send_message(callback_query.message.chat.id, "Kechirasiz, faylni konvertatsiya qilishda xatolik yuz berdi.")
            return

    # Attempt to send the file
    try:
        print(f"Downloaded and processed file: {audio_file}")
        await bot.send_document(callback_query.message.chat.id, InputFile(audio_file))
        await bot.send_message(callback_query.message.chat.id, "Qo'shiq muvaffaqiyatli jo'natildi!")
    except Exception as e:
        print(f"Error sending file: {e}")
        await bot.send_message(callback_query.message.chat.id, f"Faylni jo'natishda xatolik: {e}")
    finally:
        # Cleanup: Remove the file if it exists
        if os.path.exists(audio_file):
            os.remove(audio_file)

    # Delete the inline message
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
