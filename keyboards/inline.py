from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_congrat_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Придумать поздравление",
                callback_data="generate_congrat")]
        ]
    )


def sub_plans_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="💎 49₽ / мес (100)",
                callback_data="buy_basic")],
            [InlineKeyboardButton(
                text="🚀 99₽ / мес (250)",
                callback_data="buy_pro")],
            [InlineKeyboardButton(
                text="👑 249₽ / год (750)",
                callback_data="buy_yearly")]
        ]
    )


def see_sub_plans_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Ознакомиться с планами подписки",
                callback_data="see_sub_plans"
            )]
        ]
    )


def congrat_type_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="С днем рождения",
                callback_data="birthday")],
            [InlineKeyboardButton(
                text="С годовщиной",
                callback_data="anniversary")],
            [InlineKeyboardButton(
                text="С достижением/событием",
                callback_data="achievement")],
            [InlineKeyboardButton(
                text="С праздником",
                callback_data="holiday")],
            [InlineKeyboardButton(
                text="Личное и душевное",
                callback_data="personal")]
        ]
    )


def congrat_recipient_role_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Мама",
                callback_data="mom")],
            [InlineKeyboardButton(
                text="Папа",
                callback_data="dad")],
            [InlineKeyboardButton(
                text="Бабушка",
                callback_data="grandma")],
            [InlineKeyboardButton(
                text="Дедушка",
                callback_data="grandpa")],
            [InlineKeyboardButton(
                text="Сестра",
                callback_data="sister")],
            [InlineKeyboardButton(
                text="Брат",
                callback_data="brother")],
            [InlineKeyboardButton(
                text="Дочь",
                callback_data="daughter")],
            [InlineKeyboardButton(
                text="Сын",
                callback_data="son")],
            [InlineKeyboardButton(
                text="Жена",
                callback_data="wife")],
            [InlineKeyboardButton(
                text="Муж",
                callback_data="husband")],
            [InlineKeyboardButton(
                text="Девушка",
                callback_data="girlfriend")],
            [InlineKeyboardButton(
                text="Парень",
                callback_data="boyfriend")],
            [InlineKeyboardButton(
                text="Друг",
                callback_data="friend_boy")],
            [InlineKeyboardButton(
                text="Подруга",
                callback_data="friend_girl")],
            [InlineKeyboardButton(
                text="Коллега",
                callback_data="colleague")],
            [InlineKeyboardButton(
                text="Начальник",
                callback_data="boss")],
            [InlineKeyboardButton(
                text="Учитель",
                callback_data="teacher")],
            [InlineKeyboardButton(
                text="ИИ",
                callback_data="AI")],
            [InlineKeyboardButton(
                text="Не указывать",
                callback_data="unknown")]
        ]
    )


def congrat_style_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Тёплое / душевное',
                callback_data='spiritual')],
            [InlineKeyboardButton(
                text='Лёгкое / дружеское',
                callback_data='friendly')],
            [InlineKeyboardButton(
                text='Официальное / деловое',
                callback_data='official')]
        ]
    )


def regenerate_btn(session_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Сгенерировать еще раз",
                callback_data=f"regenerate_current:{session_id}")],
            [InlineKeyboardButton(
                text="Сгенерировать другое",
                callback_data="generate_another")]
        ]
    )
