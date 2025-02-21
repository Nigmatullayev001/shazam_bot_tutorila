from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def opinions_keyboard(title: str, callback_data: str):
    """Creates an inline keyboard button with a song title."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🎵 {title}", callback_data=callback_data)]
    ])
    return keyboard
