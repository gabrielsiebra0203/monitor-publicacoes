import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
QD_BASE_URL = os.getenv("QD_BASE_URL", "https://api.queridodiario.org.br")
QD_TERRITORY_IDS = [
    t.strip() for t in os.getenv("QD_TERRITORY_IDS", "2304400").split(",") if t.strip()
]
DIAS_RETROATIVOS = int(os.getenv("DIAS_RETROATIVOS", "7"))