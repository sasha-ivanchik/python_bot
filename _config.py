from dotenv import load_dotenv
import os


load_dotenv()

# токен от телеграм
TG_TOKEN = os.getenv('TG_TOKEN')

# ключ от апи Hotels.com
RAPID_KEY = os.getenv('RAPID_KEY')

# хост апи Hotels.com
RAPID_HOST = os.getenv('RAPID_HOST')