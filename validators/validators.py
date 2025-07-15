import datetime
import re
from dotenv import load_dotenv
import os


load_dotenv()

ADMIN_IDS = os.getenv("ADMIN_IDS").split(",")


def contains_bad_symbols(text: str) -> bool:
    # Ищем HTML-теги
    if re.search(r"<[^>]+>", text):
        return True
    # SQL-инъекции: апострофы + ключевые слова
    if re.search(r"(?:--|\b(SELECT|DROP|INSERT|DELETE|UPDATE)\b)", text, re.IGNORECASE):
        return True
    # Emoji — простая проверка (не идеальная, но работает)
    if re.search(r"[\U0001F600-\U0001F64F]", text):  # смайлики
        return True
    if re.search(r"[\U0001F300-\U0001F5FF]", text):  # символы
        return True
    return False


def is_valid_date(date_str: str) -> bool:
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_name(name: str) -> bool:
    if name == "-":
        return True
    PATTERN_NAME = re.compile(r"^[A-Za-zА-Яа-я]+(?:-[A-Za-zА-Яа-я]+)*$")
    name = name.strip()
    return bool(PATTERN_NAME.fullmatch(name))


def user_is_admin(user_id: int) -> bool:
    if str(user_id) in ADMIN_IDS:
        return True
    else:
        return False


def get_admins_ids():
    return ADMIN_IDS
