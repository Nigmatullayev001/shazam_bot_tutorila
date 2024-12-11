from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from urllib.parse import urlparse, parse_qs
import requests

API_TOKEN = "7935133923:AAF-vcd1Of-tZPptfIbUVVMY3qezWTc-PKs"
RAPIDAPI_KEY_youtube = "b1173c1a80msh5a8b6302d359d65p1ff6e3jsnefbdad47bd40"
RAPIDAPI_KEY_instagram = "b53bf27ebdmshab5fa2210825e24p136077jsne9fb82b53f47"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
RAPIDAPI_HOST_YOUTUBE = "youtube-media-downloader.p.rapidapi.com"
RAPIDAPI_HOST_INSTAGRAM = "instagram-post-reels-stories-downloader-api.p.rapidapi.com"
'''https://rapidapi.com/diyorbekkanal/api/instagram-post-reels-stories-downloader-api/'''
'''https://rapidapi.com/DataFanatic/api/youtube-media-downloader/'''
user_languages = {}


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


def fetch_video_details(video_id):
    endpoint = f"https://{RAPIDAPI_HOST_YOUTUBE}/v2/video/details"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY_youtube,
        "X-RapidAPI-Host": RAPIDAPI_HOST_YOUTUBE,
    }
    params = {"videoId": video_id}
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("videos", {}).get("items", [{}])[0].get("url")
    return None


def fetch_instagram_media(url):
    endpoint = f"https://{RAPIDAPI_HOST_INSTAGRAM}/instagram/"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY_instagram,
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


language_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
language_keyboard.add(KeyboardButton("🇺🇿 Uzbek"), KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇺🇸 English"))


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_languages[message.chat.id] = "uz"
    await message.reply(""""Salom! 🚀📥

Bu bot yordamida sevimli videolaringizni YouTube va Instagram platformalaridan tez va oson yuklab oling. YouTube'dagi darsliklar, Shorts videolar yoki Instagram Reellarini saqlashni xohlaysizmi? Bu bot siz uchun eng yaxshi yordamchi bo'ladi!

✨ Xususiyatlari:

🎬 YouTube videolari va Shorts yuklab olish
📸 Instagram videolari va Reellarini yuklab olish
⚡️ Tez va ishonchli yuklab olish xizmati
🛠 Oddiy va qulay foydalanish interfeysi
📱 Telefon va kompyuter uchun moslashtirilgan
🔗 Faqatgina video havolasini yuboring va qolganini bot bajaradi! Yuklab olishni boshlashga tayyormisiz? 🚀

Yuklab olishdan rohatlaning! 😊""", reply_markup=language_keyboard)


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

                if '.mov' in media_url or '.mp4' in media_url:
                    await bot.send_video(message.chat.id, media_url, caption="Here is your video!")
                    break
                elif '.png' in media_url or '.jpg' in media_url or '.jpeg' in media_url:
                    media_group_images = []

                    for item in media_items:
                        url = item.get('url')
                        if url:
                            media_group_images.append(
                                types.InputMediaPhoto(media=url, caption="""🔗 Faqatgina video havolasini yuboring va qolganini bot bajaradi! Yuklab olishni boshlashga tayyormisiz? 🚀

Yuklab olishdan rohatlaning! 😊""")
                            )

                    if len(media_group_images) >= 2:
                        if media_group_images is not None:
                            await bot.send_media_group(chat_id=message.chat.id, media=media_group_images)
                            media_group_images = None
                            break

                    elif len(media_group_images) == 1:
                        if media_group_images is not None:
                            await bot.send_photo(chat_id=message.chat.id, photo=media_group_images[0].media,
                                                 caption=media_group_images[0].caption)
                            media_group_images = None
                            break
                    else:

                        await bot.send_message(chat_id=message.chat.id, text="No valid images found to send.")

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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
