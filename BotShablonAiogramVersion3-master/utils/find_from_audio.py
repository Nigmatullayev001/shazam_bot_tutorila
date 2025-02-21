import aiohttp
from data.config import API_KEY

async def recognize_song(audio_bytes):
    """Recognizes the song from an audio file using Shazam API."""
    url = "https://shazam-api6.p.rapidapi.com/shazam/recognize/"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "shazam-api6.p.rapidapi.com"
    }
    files = {"upload_file": ("audio.ogg", audio_bytes, "audio/ogg")}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=files) as response:
            if response.status == 200:
                return await response.json()
            return None
