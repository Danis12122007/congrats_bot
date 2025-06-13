from dotenv import load_dotenv
import os
from openai import OpenAI
import uuid


events = {
    "birthday": "День рождения",
    "anniversary": "Годовщина",
    "achievement": "Достижение",
    "holiday": "Праздник",
    "personal": "Личное достижение",
    "joke": "Розыгрыш"
}
reciever_role = {
    "mom": "Мама",
    "dad": "Папа",
    "grandma": "Бабушка",
    "grandpa": "Дедушка",
    "sister": "Сестра",
    "brother": "Брат",
    "daughter": "Дочь",
    "son": "Сын",
    "wife": "Жена",
    "husband": "Муж",
    "girlfriend": "Девушка",
    "boyfriend": "Парень",
    "friend_boy": "Друг",
    "friend_girl": "Подруга",
    "colleague": "Коллега по работе",
    "boss": "Начальник на работе",
    "teacher": "Учитель/преподаватель",
    "AI": "Искуственный интелект",
    "unknown": "Неизвестно"
}
congrat_style = {
    "spiritual": "Душевный",
    "friendly": "Дружеский",
    "official": "Официальный"
}


def generate_congrat(data: dict | None = None, prompt: str | None = None, regenerate: bool = False) -> dict:
    # Вывод: {'congrat_type': 'achievement', 'achieve': 'победа на
    # соревнованиях по плаванию', 'congrat_recipient_role': 'friend_boy',
    # 'congrat_style': 'spiritual', 'reciever_name': 'Артём'}
    # Загружаем локальные переменные
    load_dotenv()

    token = os.getenv('OPENROUTER_TOKEN')

    client = OpenAI(
            api_key=token,
            base_url="https://openrouter.ai/api/v1"
    )

    # Инструкция
    instruction = (
            "Ты — модель, предназначенная для генерации поздравлений.\n"
            "На вход ты будешь получать запрос с просьбой придумать поздравление.\n"
            "Твоя задача — придумать короткое поздравление на русском языке,"
            " соответствующее запросу, и выдать **только текст поздравления**.\n"
            "Поздравление может быть тёплым, дружелюбным, с умеренным использованием смайлов и эмодзи 😊🎉.\n"
            "Однако **запрещено использовать**:\n"
            "- бранную и нецензурную лексику;\n"
            "- упоминания сексуального характера;\n"
            "- упоминания психотропных и наркотических веществ, запрещённых в РФ.\n"
            "Перед выдачей ответа обязательно проверяй логичность, грамматическую и синтаксическую правильность текста."
            )

    # Промпт
    if regenerate:
        prompt = prompt
    else:
        try:
            if data["congrat_type"] == "achievement":
                prompt = (
                    f"Напиши короткое поздравление по заданным параметрам. "
                    f"Тип поздравления: {events[data['congrat_type']]}, "
                    f"достижение: {data['achieve']}, "
                    f"получатель: {reciever_role[data['congrat_recipient_role']]}, "
                    f"стиль поздравления: {congrat_style[data['congrat_style']]}, "
                    f"имя получателя: {data['reciever_name']}."
                    )
            elif data["congrat_type"] == "holiday":
                prompt = (
                    f"Напиши короткое поздравление по заданным параметрам. "
                    f"Тип поздравления: {events[data['congrat_type']]}, "
                    f"праздник: {data['holiday']}, "
                    f"получатель: {reciever_role[data['congrat_recipient_role']]}, "
                    f"стиль поздравления: {congrat_style[data['congrat_style']]}, "
                    f"имя получателя: {data['reciever_name']}."
                    )
            elif data["congrat_type"] == "anniversary":
                prompt = (
                    f"Напиши короткое поздравление по заданным параметрам. "
                    f"Тип поздравления: {events[data['congrat_type']]}, "
                    f"годовщина: {data['anniversary']}, "
                    f"получатель: {reciever_role[data['congrat_recipient_role']]}, "
                    f"стиль поздравления: {congrat_style[data['congrat_style']]}, "
                    f"имя получателя: {data['reciever_name']}."
                    )
            else:
                prompt = (
                    f"Напиши короткое поздравление по заданным параметрам. "
                    f"Тип поздравления: {events[data['congrat_type']]}, "
                    f"получатель: {reciever_role[data['congrat_recipient_role']]}, "
                    f"стиль поздравления: {congrat_style[data['congrat_style']]}, "
                    f"имя получателя: {data['reciever_name']}."
                    )
        except Exception:
            return {
                "status": "error",
            }

    # Сам запрос
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",  # можно заменить на другую модель
        messages=[
            {
                "role": "system",
                "content": (instruction)
            },
            {
                "role": "user",
                "content": (prompt)
            }
        ]
    )

    session_id = str(uuid.uuid4())
    return {
        "status": "ok",
        "prompt": prompt,
        "response": response.choices[0].message.content,
        "session_id": session_id
        }


if __name__ == '__main__':
    generate_congrat({
        'congrat_type': 'birthday',
        'congrat_recipient_role': 'friend_girl',
        'congrat_style': 'friendly',
        'reciever_name': 'Дарья'
        })
