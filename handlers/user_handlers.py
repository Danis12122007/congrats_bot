import asyncio
from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from keyboards import inline
from aiogram.fsm.context import FSMContext
from bot_states import form_states
from services import data_base, AI_API
import datetime
from validators import validators


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
    print(message.from_user.full_name)
    user_id = message.from_user.id
    data_base.reg_user(user_id)

    await message.answer(
        "Привет! Я бот, который генерирует поздравления! Просто жми на кнопку ниже!",
        reply_markup=inline.generate_congrat_btn())


@router.message(Command('generate_congrat'))
async def generate_congrat(message: types.Message, state: FSMContext):
    print(f"{message.from_user.id}: generate_congrat")
    await state.clear()
    user_id = message.from_user.id
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
    await message.answer("""
🎉 Хочешь больше поздравлений? Подпишись и получи доступ к генерациям без лишних ограничений:

💡 Бесплатно:
— 5 поздравлений в месяц
— Хорошо, чтобы попробовать

💎 Базовая — 49₽ / мес:
— 100 генераций
— Для редких поздравлений

🚀 Продвинутая — 99₽ / мес:
— 250 генераций
— Для активных пользователей

👑 Годовая — 249₽ / год:
— 750 генераций на весь год
— Максимальная выгода: одно поздравление меньше 35 копеек!

Подписка активируется сразу. Генерации не сгорают до конца срока.
""", reply_markup=inline.sub_plans_btn())


@router.message(Command('promocode'))
async def promocode(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    data_base.reg_user(user_id)
    await state.set_state(form_states.Congrat.promocode)
    await message.answer("Введите промокод")


@router.message(F.text)
async def recipient_name(message: types.Message, state: FSMContext):
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
        await state.update_data(reciever_name=message.text)
        congrat_data = await state.get_data()
        print(f"{message.from_user.id}: {congrat_data}")
        result = AI_API.generate_congrat(congrat_data)
        if result["status"] == "error":
            await answer_generation.edit_text(
                "Какая-то ошибка\nПопробуйте еще раз\nТокены не списаны",
                reply_markup=inline.generate_congrat_btn()
                )
            return
        prompt = result["prompt"]
        response = result["response"]
        session_id = result["session_id"]
        data_base.log_generation(message.from_user.id, prompt, response, session_id)
        data_base.write_off_a_token(message.from_user.id)
        await answer_generation.edit_text(response, reply_markup=inline.regenerate_btn(session_id))
        data_base.set_last_request_time(message.from_user.id)
    elif current_state == 'Congrat:promocode':
        promo = message.text
        if promo in []:
            user_id = message.from_user.id
            data_base.set_subscription(user_id, "monthly")
            await message.answer("Промокод применён")
            await state.clear()
        else:
            await message.answer("Промокод не подходит")
            await state.clear()
    elif current_state == 'Congrat:achieve':
        await state.update_data(achieve=message.text)
        await state.set_state(form_states.Congrat.congrat_recipient_role)
        await message.answer(
                            "Выберите кому будет поздравление",
                            reply_markup=inline.congrat_recipient_role_btn()
        )
    elif current_state == 'Congrat:holiday':
        await state.update_data(holiday=message.text)
        await state.set_state(form_states.Congrat.congrat_recipient_role)
        await message.answer(
                            "Выберите кому будет поздравление",
                            reply_markup=inline.congrat_recipient_role_btn()
        )
    elif current_state == 'Congrat:anniversary':
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
    else:
        await state.clear()
        await message.answer("Сообщение вне контекста")
        user_id = message.from_user.id
        data_base.reg_user(user_id)
