import os
import ffmpeg
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from data.config import TEMP_DIR, AUDIO_FORMAT
from utils.find_from_audio import recognize_song
from utils.shazam_text_finder import search_track
from utils.shazam_video_finder import recognize_music_from_video

# Create a router for user commands
router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("🎵 Send me an audio, voice, or video file, and I'll recognize the song!")


@router.message(F.audio | F.voice)
async def handle_audio(message: Message):
    """Handles audio and voice messages and recognizes the song."""
    file = await message.audio or message.voice
    file_path = await file.get_file()

    # Download the file
    audio_file = await message.bot.download_file(file_path.file_path)

    await message.reply("🔍 Recognizing song... Please wait.")

    # Send to Shazam API
    result = await recognize_song(audio_file.read())

    if result and "track" in result:
        track = result["track"]
        title = track.get("title", "Unknown Title")
        artist = track.get("subtitle", "Unknown Artist")
        url = track.get("url", "No link available")

        response_text = f"🎵 <b>Song:</b> {title}\n🎤 <b>Artist:</b> {artist}\n🔗 <a href='{url}'>Listen on Shazam</a>"
        await message.answer(response_text)
    else:
        await message.answer("❌ Could not recognize the song. Try again!")


@router.message(F.video)
async def handle_video(message: Message):
    """Handles video messages, extracts audio, and recognizes the song."""
    file = await message.video.get_file()
    video_path = os.path.join(TEMP_DIR, "input_video.mp4")

    # Download the video file
    await message.bot.download_file(file.file_path, video_path)

    await message.reply("🔍 Extracting audio and recognizing song... Please wait.")

    # Process the video
    try:
        result = await recognize_music_from_video(video_path)

    except Exception as e:
        print(e)
        await message.answer('AUDIO TOPILMADI')
        return None
    # Remove the video file after processing
    os.remove(video_path)

    if result and "track" in result:
        track = result["track"]
        title = track.get("title", "Unknown Title")
        artist = track.get("subtitle", "Unknown Artist")
        url = track.get("url")

        response_text = f"🎵 <b>Song:</b> {title}\n🎤 <b>Artist:</b> {artist}\n🔗 <a href='{url}'>Listen on Shazam</a>"
        await message.answer(response_text)
    else:
        await message.answer("❌ Could not recognize the song. Try again!")


@router.message(F.text)
async def handle_text(message: Message):
    """Handles text messages, searches for the song, and returns results with a 'Download' button."""
    await message.reply("🔍 Searching for the song... Please wait.")
    query = message.text.strip()

    try:
        result = search_track(query=query, limit=5)
        print("API Response:", result)

        if not result or "tracks" not in result or "hits" not in result["tracks"]:
            await message.answer("❌ No songs found!")
            return

        searched = []
        buttons = []

        for track in result["tracks"]["hits"]:
            title = track["heading"].get("title", "Unknown Title")[:20]  # Max 20 belgi
            artist = track["heading"].get("subtitle", "Unknown Artist")[:20]  # Max 20 belgi
            url = track.get("url", "")

            searched.append(f"🎵 {title} - {artist}")

            buttons.append([InlineKeyboardButton(text=f'{title} - {artist}', url=url)])

            # **Tuzatilgan callback_data**
            callback_data = f"download|{title}|{artist}"
            buttons.append([InlineKeyboardButton(text="⬇️ Download", callback_data=callback_data)])

        next_page_url = result.get("tracks", {}).get("next")
        if next_page_url:
            buttons.append([InlineKeyboardButton(text="➡️ Next", callback_data="next_page")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        song_list = "\n".join(searched)
        await message.reply(f"🎶 Found songs:\n\n{song_list} \n\n🔽 Choose an option below:", reply_markup=keyboard)

    except Exception as e:
        print(f"❌ Error: {e}")
        await message.answer("🚨 An error occurred. Please try again later!")


@router.callback_query(F.data.startswith("download|"))
async def handle_download(callback_query: CallbackQuery):
    """Handles the 'Download' button click and sends an audio file."""
    _, title, artist = callback_query.data.split("|")

    audio_file_path = os.path.join(TEMP_DIR, f"{title} - {artist}.{AUDIO_FORMAT}")

    if os.path.exists(audio_file_path):
        with open(audio_file_path, "rb"):
            await callback_query.message.answer_audio(
                audio=audio_file_path,
                caption=f"🎵 {title} - {artist}"
            )
    else:
        await callback_query.answer("🚫 File not found!", show_alert=True)

