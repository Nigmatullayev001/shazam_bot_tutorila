import os
import ffmpeg
from data.config import TEMP_DIR, AUDIO_FORMAT
from .find_from_audio import recognize_song


async def extract_audio(video_path):
    """Extracts audio from a given video file."""
    audio_path = os.path.join(TEMP_DIR, f"output.{AUDIO_FORMAT}")
    try:
        ffmpeg.input(video_path).output(audio_path, format=AUDIO_FORMAT, acodec="libopus").run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return audio_path
    except Exception as e:
        print(e)


async def recognize_music_from_video(video_path):
    """Extracts audio from video and recognizes it using Shazam."""
    audio_path = await extract_audio(video_path)

    with open(audio_path, "rb") as audio_file:
        result = await recognize_song(audio_file.read())

    # Clean up files after processing
    os.remove(audio_path)

    return result
