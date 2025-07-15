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
                text="💎 99₽ / мес (100)",
                callback_data="buy_basic")],
            [InlineKeyboardButton(
                text="🚀 149₽ / мес (250)",
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
                text="🎂 С днем рождения",
                callback_data="birthday")],
            [InlineKeyboardButton(
                text="🎁 С годовщиной",
                callback_data="anniversary")],
            [InlineKeyboardButton(
                text="⭐️ С достижением/событием",
                callback_data="achievement")],
            [InlineKeyboardButton(
                text="🗓️ С праздником",
                callback_data="holiday")],
            [InlineKeyboardButton(
                text="❤️ Личное и душевное",
                callback_data="personal")]
        ]
    )


def congrat_recipient_role_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="👩 Мама",
                callback_data="mom"),
            InlineKeyboardButton(
                text="👨 Папа",
                callback_data="dad")],
            [InlineKeyboardButton(
                text="👵 Бабушка",
                callback_data="grandma"),
            InlineKeyboardButton(
                text="👴 Дедушка",
                callback_data="grandpa")],
            [InlineKeyboardButton(
                text="🧑 Сестра",
                callback_data="sister"),
            InlineKeyboardButton(
                text="👦 Брат",
                callback_data="brother")],
            [InlineKeyboardButton(
                text="🧒 Дочь",
                callback_data="daughter"),
            InlineKeyboardButton(
                text="👦 Сын",
                callback_data="son")],
            [InlineKeyboardButton(
                text="👰‍♀️ Жена",
                callback_data="wife"),
            InlineKeyboardButton(
                text="🤵‍♂️ Муж",
                callback_data="husband")],
            [InlineKeyboardButton(
                text="🙋‍♀️ Девушка",
                callback_data="girlfriend"),
            InlineKeyboardButton(
                text="🙋‍♂️ Парень",
                callback_data="boyfriend")],
            [InlineKeyboardButton(
                text="🤝 Друг",
                callback_data="friend_boy"),
            InlineKeyboardButton(
                text="🤝 Подруга",
                callback_data="friend_girl")],
            [InlineKeyboardButton(
                text="💼 Коллега",
                callback_data="colleague"),
            InlineKeyboardButton(
                text="🧑‍💼Начальник",
                callback_data="boss")],
            [InlineKeyboardButton(
                text="🧑‍🏫Учитель",
                callback_data="teacher"),
            InlineKeyboardButton(
                text="🤖 ИИ",
                callback_data="AI")],
            [InlineKeyboardButton(
                text="🛑 Не указывать",
                callback_data="unknown")]
        ]
    )


def congrat_style_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='🌞 Тёплое / душевное',
                callback_data='spiritual')],
            [InlineKeyboardButton(
                text='😄 Лёгкое / дружеское',
                callback_data='friendly')],
            [InlineKeyboardButton(
                text='📎 Официальное / деловое',
                callback_data='official')]
        ]
    )


def regenerate_btn_not_fav(session_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Сгенерировать еще раз",
                callback_data=f"regenerate_current:{session_id}")],
            [InlineKeyboardButton(
                text="Сгенерировать другое",
                callback_data="generate_another")],
            [InlineKeyboardButton(
                text="⭐ Сохранить поздравление в избранные",
                callback_data=f"add_favourite:{session_id}")]
        ]
    )


def regenerate_btn_fav(session_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Сгенерировать еще раз",
                callback_data=f"regenerate_current:{session_id}")],
            [InlineKeyboardButton(
                text="Сгенерировать другое",
                callback_data="generate_another")],
            [InlineKeyboardButton(
                text="❌ Удалить поздравление из избранных",
                callback_data=f"delete_favourite:{session_id}")]
        ]
    )


def fav_mess_nav_btns(
        total_amount: int,
        cur_mess: int,
        session_id: str,
        last: bool = False,
        first: bool = False):
    if first and last:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"{cur_mess + 1}/{total_amount}",
                    callback_data="none")],
                [InlineKeyboardButton(
                    text="❌ Удалить поздравление из избранных",
                    callback_data=f"del_fav:{session_id},{cur_mess}")]
            ]
        )
    elif first:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{cur_mess + 1}/{total_amount}",
                        callback_data="none"),
                    InlineKeyboardButton(
                        text=">>",
                        callback_data=f"next_mess:{cur_mess}")
                ],
                [InlineKeyboardButton(
                    text="❌ Удалить поздравление из избранных",
                    callback_data=f"del_fav:{session_id},{cur_mess}")]
            ]
        )
    if last:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="<<",
                        callback_data=f"prev_mess:{cur_mess}"),
                    InlineKeyboardButton(
                        text=f"{cur_mess + 1}/{total_amount}",
                        callback_data="none")
                ],
                [InlineKeyboardButton(
                    text="❌ Удалить поздравление из избранных",
                    callback_data=f"del_fav:{session_id},{cur_mess}")]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="<<",
                        callback_data=f"prev_mess:{cur_mess}"),
                    InlineKeyboardButton(
                        text=f"{cur_mess + 1}/{total_amount}",
                        callback_data="none"),
                    InlineKeyboardButton(
                        text=">>",
                        callback_data=f"next_mess:{cur_mess}")
                ],
                [InlineKeyboardButton(
                    text="❌ Удалить поздравление из избранных",
                    callback_data=f"del_fav:{session_id},{cur_mess}")]
            ]
        )
