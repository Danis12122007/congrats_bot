import logging
import os
from dotenv import load_dotenv


load_dotenv()

admins = os.getenv("ADMIN_IDS").split(",")
admins = [int(i) for i in admins]

# Убедимся, что файл логов существует
if not os.path.exists("logs"):
    os.makedirs("logs")

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()  # чтобы видеть логи и в консоли
    ]
)

logging.getLogger("aiogram").setLevel(logging.WARNING)


def log_action(user_id: int, action: str):
    if user_id not in admins:
        logging.info(f"[{user_id}] {action}")
