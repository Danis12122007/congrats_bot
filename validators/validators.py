import datetime
import re


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


def user_is_admin(user_id: int) -> bool:
    admins = ['1943303658']
    if str(user_id) in admins:
        return True
    else:
        return False
