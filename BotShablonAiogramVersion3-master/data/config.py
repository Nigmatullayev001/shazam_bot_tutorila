from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot token
API_KEY = env.str("API_KEY")  # rapidapi.com dan api olish
CHANNEL_USERNAME = env.str("TEMP_DIR")  # kanal/guruh linki
AUDIO_FORMAT = env.str("AUDIO_FORMAT")  # adminlar ro'yxati
TEMP_DIR = env.str("ADMINS")  # adminlar ro'yxati
ADMINS = env.list("ADMINS")  # adminlar ro'yxati
IP = env.str("ip")  # Xosting ip manzili
