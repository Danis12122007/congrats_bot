import asyncio
from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from keyboards import inline
from aiogram.fsm.context import FSMContext
from bot_states import form_states
from services import data_base, AI_API, promotions, graphs
import datetime
from validators import validators
from services import logging


log_action = logging.log_action


TARIFFS = {
    "buy_basic": {
        "label": "💎 Базовая подписка",
        "description": "100 генераций на 30 дней.",
        "amount": 4900,  # копеек = 49₽
        "days": 30,
        "tokens": 100,
        "payload": "basic_sub",
    },
    "buy_pro": {
        "label": "🚀 Продвинутая подписка",
        "description": "250 генераций на 30 дней.",
        "amount": 9900,  # 99₽
        "days": 30,
        "tokens": 250,
        "payload": "pro_sub",
    },
    "buy_yearly": {
        "label": "👑 Годовая подписка",
        "description": "750 генераций на 365 дней.",
        "amount": 24900,  # 249₽
        "days": 365,
        "tokens": 750,
        "payload": "yearly_sub",
    }
}


sub_types = {
    "free_sub": "Бесплатная подписка",
    "basic_sub": "💎 Базовая подписка",
    "pro_sub": "🚀 Продвинутая подписка",
    "yearly_sub": "👑 Годовая подписка"
}


def check_sub(user_id: int):
    user_info = data_base.get_info(user_id)
    if user_info["available_tokens"] == 0:
        if user_info["sub_type"] == "free_sub":
            return {
                "allow_generate": False,
                "message": (
                    "Похоже, у вас не осталось доступных токенов генерации. "
                    "Вы можете купить подписку и получить неограниченое количество токенов. "
                )
            }
        else:
            return {
                "allow_generate": False,
                "message": (
                    "Количество токенов генераций на текущий период подписки исчерпан."
                )
            }
    else:
        return {
            "allow_generate": True,
            "message": ""
        }


router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    log_action(user_id, "/start")
    data_base.reg_user(user_id)

    await message.answer(
        """
👋 Привет! Я — твой личный поздравлятор.
Напишу поздравление для мамы, подруги, начальника и даже бывшей 😎
Первые 3 поздравления — бесплатно 🎁
        """,
        reply_markup=inline.generate_congrat_btn())


@router.message(Command('generate_congrat'))
async def generate_congrat(message: types.Message, state: FSMContext):
    print(f"{message.from_user.id}: generate_congrat")
    await state.clear()
    user_id = message.from_user.id
    log_action(user_id, "/generate_congrat")
    data_base.reg_user(user_id)

    sub_data = check_sub(user_id)
    if not sub_data["allow_generate"]:
        await message.answer(sub_data["message"], reply_markup=inline.see_sub_plans_btn())
    else:
        allowing_data = data_base.get_permition_by_last_request_time(message.from_user.id)
        if allowing_data["status"] == "not allowed" and allowing_data["message"] == "request frequency exceeded":
            generation_frequency_exceeded_message = await message.answer("Превышена частота генераций. Повторите позже")
            await asyncio.sleep(5)
            await generation_frequency_exceeded_message.delete()
            await message.answer()
            return
        await message.answer(
            "Выберите тип поздравления",
            reply_markup=inline.congrat_type_btn()
        )

        await state.set_state(form_states.Congrat.congrat_type)


@router.message(Command('information'))
async def info(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    log_action(user_id, "/information")
    data_base.reg_user(user_id)

    info = data_base.get_info(user_id)

    info_user_id = f"Пользователь №{info['user_id']}\n"
    info_reg_date = f"Дата регистрации: {info['reg_date'].date()}\n"
    info_subscription = f"Тип подписки: {sub_types[info['sub_type']]}\n"
    info_sub_expired = f"Истекает: {info['sub_expired'].date()}\n"
    info_available_tokens = f"Доступно токенов: {info['available_tokens']}"

    await message.answer(
        text="{}{}{}{}{}".format(
                                info_user_id,
                                info_reg_date,
                                info_subscription,
                                info_sub_expired,
                                info_available_tokens
                                )
    )


@router.message(Command("subscription"))
async def subscription(message: types.Message, state: FSMContext):
    log_action(message.from_user.id, "/subscription")
    await message.answer("""
🎉 Хочешь больше поздравлений и лучшее качество?
Подпишись и получи доступ к расширенным генерациям на базе GPT-4.1 — более креативной и душевной модели!

💡 Бесплатно
— 3 поздравления
— На базе GPT-3.5
— Отлично, чтобы попробовать

💎 Базовая — 99₽ / мес
— 100 поздравлений
— Используется GPT-4.1
— Для редких, но качественных поздравлений

🚀 Продвинутая — 149₽ / мес
— 250 поздравлений
— Используется GPT-4.1
— Для активных пользователей и креативных идей

👑 Годовая — 249₽ / год
— 750 поздравлений на весь год
— Используется GPT-4.1
— Максимальная выгода!

📌 Подписка активируется сразу. Генерации не сгорают до конца срока.
""", reply_markup=inline.sub_plans_btn())


@router.message(Command('promocode'))
async def promocode(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    log_action(user_id, "/promocode")
    data_base.reg_user(user_id)
    await state.set_state(form_states.Congrat.promocode)
    await message.answer("Введите промокод")


@router.message(Command("awake"))
async def awake_inactive_users(message: types.Message):
    if not validators.user_is_admin(message.from_user.id):
        return
    log_action(message.from_user.id, "/awake")
    users = data_base.get_inactive_users()
    text = "🎉 Привет! Ты давно не заходил. Пора бы сгенерировать поздравление 😉"
    await promotions.broadcast_message(message.bot, users, text, inline.generate_congrat_btn)


@router.message(F.text)
async def recipient_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_info = data_base.get_info(user_id)
    message_text = message.text
    if "<script>" in message_text or any(x in message_text for x in ["<", ">", "{", "}"]):
        await message.answer("Пожалуйста, не используйте подозрительные символы.")
        return
    if len(message_text) > 50:
        await message.answer("Сообщение слишком длинное(более 50 символов)")
        return
    if len(message_text.strip()) == 0:
        message.answer("Сообщение не может быть пустым")
        return
    if validators.contains_bad_symbols(message.text):
        await message.answer("Пожалуйста, не используйте emoji, HTML-теги или подозрительные символы.")
        return

    current_state = await state.get_state()

    if current_state == 'Congrat:reciever_name':
        if not message_text.replace(" ", "").isalpha():
            await message.answer("Имя может содержать только буквы.")
            return
        allowing_data = data_base.get_permition_by_last_request_time(message.from_user.id)
        if allowing_data["status"] == "not allowed" and allowing_data["message"] == "request frequency exceeded":
            await message.answer("Превышена частота генераций. Повторите позже")
            return
        answer_generation = await message.answer("Генерация...")
        log_action(user_id, f"Выбрал получателя: {message.text}")
        await state.update_data(reciever_name=message.text)
        congrat_data = await state.get_data()
        print(f"{message.from_user.id}: {congrat_data}")

        if user_info["sub_type"] == "free_sub":
            result = AI_API.generate_congrat_gpt_3_5(congrat_data)
            if result["status"] == "error":
                log_action(user_id, f"Ошибка при генерации: {result['error']}")
                await answer_generation.edit_text(
                    "Какая-то ошибка\nПопробуйте еще раз\nТокены не списаны",
                    reply_markup=inline.generate_congrat_btn()
                    )
                return
            prompt = result["prompt"]
            response = result["response"]
            session_id = result["session_id"]
            data_base.log_generation(user_id, prompt, response, session_id, "gpt-3.5")
        else:
            result = AI_API.generate_congrat_gpt_4_1(congrat_data)
            if result["status"] == "error":
                log_action(user_id, f"Ошибка при генерации: {result['error']}")
                await answer_generation.edit_text(
                    "Какая-то ошибка\nПопробуйте еще раз\nТокены не списаны",
                    reply_markup=inline.generate_congrat_btn()
                    )
                return
            prompt = result["prompt"]
            response = result["response"]
            session_id = result["session_id"]
            data_base.log_generation(user_id, prompt, response, session_id, "gpt-4.1")

        data_base.write_off_a_token(user_id)
        await answer_generation.edit_text(response, reply_markup=inline.regenerate_btn(session_id))
        log_action(user_id, f"Получил поздравление {session_id}")
        data_base.set_last_request_time(user_id)
        gen_count = data_base.send_mess_after_first_second_gen(user_id)
        if gen_count == '1':
            await message.answer(
                """
                🎉 Готово! Надеюсь, понравилось.\n
                Осталось: 2 бесплатных генерации.
                """)
        elif gen_count == '2':
            await message.answer(
                """
                🎉 Готово! Надеюсь, понравилось.
                Осталось: 1 бесплатная генерация.
                """)
        elif gen_count == '3':
            await message.answer(
                """
                ⛔ Больше бесплатных генераций нет.
                Хочешь продолжить? Вот доступные варианты 👇
                """, reply_markup=inline.sub_plans_btn())

    elif current_state == 'Congrat:promocode':
        promo = message.text
        log_action(user_id, f"Ввел промокод: {promo}")
        if promo in []:
            user_id = message.from_user.id
            data_base.set_subscription(user_id, "monthly")
            await message.answer("Промокод применён")
            await state.clear()
        else:
            await message.answer("Промокод не подходит")
            await state.clear()
    elif current_state == 'Congrat:achieve':
        log_action(user_id, f"Ввел достижение: {message.text}")
        await state.update_data(achieve=message.text)
        await state.set_state(form_states.Congrat.congrat_recipient_role)
        await message.answer(
                            "Выберите кому будет поздравление",
                            reply_markup=inline.congrat_recipient_role_btn()
        )
    elif current_state == 'Congrat:holiday':
        log_action(user_id, f"Ввел праздник: {message.text}")
        await state.update_data(holiday=message.text)
        await state.set_state(form_states.Congrat.congrat_recipient_role)
        await message.answer(
                            "Выберите кому будет поздравление",
                            reply_markup=inline.congrat_recipient_role_btn()
        )
    elif current_state == 'Congrat:anniversary':
        log_action(user_id, f"Ввел годовщину: {message.text}")
        await state.update_data(anniversary=message.text)
        await state.set_state(form_states.Congrat.congrat_recipient_role)
        await message.answer(
                            "Выберите кому будет поздравление",
                            reply_markup=inline.congrat_recipient_role_btn()
        )
    elif message.text.startswith("/daily_stat") and validators.user_is_admin(message.from_user.id):
        user_id = message.from_user.id
        print(f"{user_id}:{str(message.text)[1:]}")
        await state.clear()
        try:
            date = message.text.split()[1]
        except IndexError:
            await message.answer("Запрос не соответствует формату /daily_stat ГГГГ-ММ-ДД")
            return
        if len(message.text.split()) != 2:
            await message.answer("Запрос не соответствует формату /daily_stat ГГГГ-ММ-ДД")
            return
        date = message.text.split()[1]
        if not validators.is_valid_date(date):
            await message.answer("Несуществующая дата или запрос не соответствует формату /daily_stat ГГГГ-ММ-ДД")
            return
        date = date.split("-")
        date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
        daily_info = data_base.get_daily_stat(date)
        await message.answer((
            f"Количество генераций: {daily_info['gen_count']}\n"
            f"Количество пользователей произведших генерацию: {daily_info['users_gen_count']}\n"
            f"Количество новых пользователей: {daily_info['newcomers_count']}\n"
        ))
    elif message.text.startswith("/monthly_stat") and validators.user_is_admin(message.from_user.id):
        user_id = message.from_user.id
        print(f"{user_id}:{str(message.text)[1:]}")
        await state.clear()
        try:
            date = message.text.split()[1]
        except IndexError:
            await message.answer("Запрос не соответствует формату /monthly_stat ГГГГ-ММ")
            return
        if len(message.text.split()) != 2:
            await message.answer("Запрос не соответствует формату /monthly_stat ГГГГ-ММ")
            return
        date = message.text.split()[1]
        date = date + "-01"
        if not validators.is_valid_date(date):
            await message.answer("Несуществующая дата или запрос не соответствует формату /monthly_stat ГГГГ-ММ")
            return
        date = date.split("-")
        date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
        monthly_info = data_base.get_monthly_stat(date)
        await message.answer((
            f"Количество генераций: {monthly_info['gen_count']}\n"
            f"Количество пользователей произведших генерацию: {monthly_info['users_gen_count']}\n"
            f"Количество новых пользователей: {monthly_info['newcomers_count']}\n"
        ))
    elif message.text.startswith("/graph_gens") and validators.user_is_admin(message.from_user.id):
        user_id = message.from_user.id
        print(f"{user_id}:{str(message.text)[1:]}")
        await state.clear()

        date_range = str(message.text).split()[1].split("=")

        start = datetime.date(
            int(date_range[0].split("-")[0]),
            int(date_range[0].split("-")[1]),
            int(date_range[0].split("-")[2])
            )
        end = datetime.date(
            int(date_range[1].split("-")[0]),
            int(date_range[1].split("-")[1]),
            int(date_range[1].split("-")[2])
            )

        graph = graphs.get_gens_graph(start, end)

        await message.answer(f"```\n{graph}\n```", parse_mode="Markdown")
        print(graph)

    elif message.text.startswith("/graph_users") and validators.user_is_admin(message.from_user.id):
        user_id = message.from_user.id
        print(f"{user_id}:{str(message.text)[1:]}")
        await state.clear()

        date_range = str(message.text).split()[1].split("=")

        start = datetime.date(
            int(date_range[0].split("-")[0]),
            int(date_range[0].split("-")[1]),
            int(date_range[0].split("-")[2])
            )
        end = datetime.date(
            int(date_range[1].split("-")[0]),
            int(date_range[1].split("-")[1]),
            int(date_range[1].split("-")[2])
            )

        graph = graphs.get_users_graph(start, end)

        await message.answer(f"```\n{graph}\n```", parse_mode="Markdown")
        print(graph)
    else:
        log_action(user_id, f"Сообщение вне контекста: {message.text}")
        await state.clear()
        await message.answer("Сообщение вне контекста")
        user_id = message.from_user.id
        data_base.reg_user(user_id)
