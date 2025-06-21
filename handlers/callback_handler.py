from datetime import datetime, timedelta, timezone
import json
from aiogram import Router, types, F
from keyboards import inline
from aiogram.fsm.context import FSMContext
from bot_states import form_states
from services import data_base, AI_API
from dotenv import load_dotenv
import os
import asyncio
from services import logging


log_action = logging.log_action

# data dicts
events_dict = {
    "birthday": "День рождения",
    "anniversary": "Годовщина",
    "achievement": "Достижение",
    "holiday": "Праздник",
    "personal": "Личное достижение",
    "joke": "Розыгрыш"
}
reciever_role_dict = {
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
style_dict = {
    "spiritual": "Душевный",
    "friendly": "Дружеский",
    "official": "Официальный"
}

TARIFFS = {
    "buy_basic": {
        "label": "💎 Базовая подписка",
        "description": "100 генераций на 30 дней.",
        "amount": 9900,  # копеек = 49₽
        "days": 30,
        "tokens": 100,
        "payload": "basic_sub",
    },
    "buy_pro": {
        "label": "🚀 Продвинутая подписка",
        "description": "250 генераций на 30 дней.",
        "amount": 14900,  # 99₽
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

load_dotenv()
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")

router = Router()


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


@router.callback_query(F.data == "generate_congrat")
async def generate_congrat(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    log_action(user_id, "callback:generate_congrat")
    sub_data = check_sub(user_id)
    if not sub_data["allow_generate"]:
        await callback.message.answer(sub_data["message"], reply_markup=inline.see_sub_plans_btn())
    else:
        allowing_data = data_base.get_permition_by_last_request_time(callback.from_user.id)
        if allowing_data["status"] == "not allowed" and allowing_data["message"] == "request frequency exceeded":
            generation_frequency_exceeded_message = await callback.message.answer((
                "Превышена частота генераций. "
                "Повторите позже"
            ))
            await asyncio.sleep(5)
            await generation_frequency_exceeded_message.delete()
            await callback.answer()
            return
        print(f"{user_id}: generate_congrat")
        await callback.message.edit_text(
            "Выберите тип поздравления",
            reply_markup=inline.congrat_type_btn()
        )

        data_base.set_last_request_time(callback.from_user.id)

        await state.set_state(form_states.Congrat.congrat_type)

    await callback.answer()


@router.callback_query(F.data == "generate_another")
async def generate_another(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    log_action(user_id, "callback:generate_another")
    print(f"{user_id}: generate_another")

    sub_data = check_sub(user_id)
    if not sub_data["allow_generate"]:
        await callback.message.answer(sub_data["message"], reply_markup=inline.see_sub_plans_btn())
    else:
        allowing_data = data_base.get_permition_by_last_request_time(callback.from_user.id)
        if allowing_data["status"] == "not allowed" and allowing_data["message"] == "request frequency exceeded":
            generation_frequency_exceeded_message = await callback.message.answer((
                "Превышена частота генераций. "
                "Повторите позже"
                ))
            await asyncio.sleep(5)
            await generation_frequency_exceeded_message.delete()
            await callback.answer()
            return
        await callback.message.answer(
            "Выберите тип поздравления",
            reply_markup=inline.congrat_type_btn()
        )

        await state.set_state(form_states.Congrat.congrat_type)

    await callback.answer()


@router.callback_query(F.data.contains("regenerate_current:"))
async def regenerate_current(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_info = data_base.get_info(user_id)
    log_action(user_id, "callback:regenerate_current")
    print(f"{user_id}: regenerate_current")

    sub_data = check_sub(user_id)
    if not sub_data["allow_generate"]:
        await callback.message.answer(sub_data["message"], reply_markup=inline.see_sub_plans_btn())
        await state.clear()
    else:
        allowing_data = data_base.get_permition_by_last_request_time(callback.from_user.id)
        if allowing_data["status"] == "not allowed" and allowing_data["message"] == "request frequency exceeded":
            generation_frequency_exceeded_message = await callback.message.answer((
                "Превышена частота генераций. "
                "Повторите позже"
                ))
            await asyncio.sleep(5)
            await generation_frequency_exceeded_message.delete()
            await callback.answer()
            return

        session_id = callback.data.split(":", 1)[1]
        answer_generation = await callback.message.edit_text("Генерация...")
        prompt = data_base.get_prompt_by_session_id(session_id)
        if user_info["sub_type"] == "free_sub":
            result = AI_API.generate_congrat_gpt_3_5(prompt=prompt, regenerate=True)
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
            data_base.log_generation(callback.from_user.id, prompt, response, session_id, "gpt-3.5")
        else:
            result = AI_API.generate_congrat_gpt_4_1(prompt=prompt, regenerate=True)
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
            data_base.log_generation(callback.from_user.id, prompt, response, session_id, "gpt-4.1")

        data_base.write_off_a_token(callback.from_user.id)
        await answer_generation.edit_text(response, reply_markup=inline.regenerate_btn(session_id))
        log_action(user_id, f"Получил поздравление {session_id}")
        data_base.set_last_request_time(callback.from_user.id)
        gen_count = data_base.send_mess_after_first_second_gen(user_id)
        print(f"gen_count:{gen_count}")
        if gen_count == '1':
            await callback.message.answer(
                """
                🎉 Готово! Надеюсь, понравилось.\n
                Осталось: 2 бесплатных генерации.
                """)
        elif gen_count == '2':
            await callback.message.answer(
                """
                🎉 Готово! Надеюсь, понравилось.
                Осталось: 1 бесплатная генерация.
                """)
        elif gen_count == '3':
            await callback.message.answer(
                """
                ⛔ Больше бесплатных генераций нет.
                Хочешь продолжить? Вот доступные варианты 👇
                """, reply_markup=inline.sub_plans_btn())

    await callback.answer()


# Обработчик типа поздравления
@router.callback_query(F.data.in_({
    "birthday",
    "anniversary",
    "achievement",
    "holiday",
    "personal"
}))
async def congrat_type(callback: types.CallbackQuery, state: FSMContext):
    c_type = callback.data
    log_action(callback.from_user.id, f"Тип поздравления: {events_dict[c_type]}")
    await state.update_data(congrat_type=c_type)

    await callback.message.edit_text(
                            f'Выберите тип поздравления\n✅{events_dict[c_type]}'
                            )

    if c_type == "achievement":
        await callback.message.answer(
                            "С каким достижением вы хотели бы поздравить?"
                            )
        await state.set_state(form_states.Congrat.achieve)

    elif c_type == "holiday":
        await callback.message.answer(
                            "С каким праздником вы хотели бы поздравить?"
                            )
        await state.set_state(form_states.Congrat.holiday)
    elif c_type == "anniversary":
        await callback.message.answer(
                            "С какой годовщиной вы хотели бы поздравить?"
                            )
        await state.set_state(form_states.Congrat.anniversary)
    else:
        await callback.message.answer(
                                "Выберите кому будет поздравление",
                                reply_markup=inline.congrat_recipient_role_btn()
                                )
        await state.set_state(form_states.Congrat.congrat_recipient_role)


# Обработчики получателя поздравления
@router.callback_query(F.data.in_({
    "mom",
    "dad",
    "grandma",
    "grandpa",
    "sister",
    "brother",
    "daughter",
    "son",
    "wife",
    "husband",
    "girlfriend",
    "boyfriend",
    "friend_boy",
    "friend_girl",
    "colleague",
    "boss",
    "teacher",
    "AI",
    "unknown"
}))
async def congrat_reciever_role(callback: types.CallbackQuery, state: FSMContext):
    role = callback.data
    log_action(callback.from_user.id, f"Роль получателя: {reciever_role_dict[role]}")

    await state.update_data(congrat_recipient_role=role)
    await state.set_state(form_states.Congrat.congrat_style)

    await callback.message.edit_text(
                            f'Выберите кому будет поздравление\n✅{reciever_role_dict[role]}'
                            )

    await callback.message.answer(
                            "Выберите стиль поздравления",
                            reply_markup=inline.congrat_style_btn()
    )


# Обработчики стиля поздравления
@router.callback_query(F.data.in_({
    "spiritual",
    "friendly",
    "official"
}))
async def congrat_style(callback: types.CallbackQuery, state: FSMContext):
    style = callback.data
    log_action(callback.from_user.id, f"Стиль поздравления: {style_dict[style]}")
    await state.update_data(congrat_style=style)
    await state.set_state(form_states.Congrat.reciever_name)

    await callback.message.edit_text(
                            f"Выберите стиль поздравления\n✅{style_dict[style]}"
                            )

    await callback.message.answer(
                            "Выберите имя получателя('-' - не указывать)"
    )


@router.callback_query(F.data == 'see_sub_plans')
async def see_sub_plans(callback: types.CallbackQuery, state: FSMContext):
    log_action(callback.from_user.id, "callback:see_sub_plans")
    await callback.message.answer("""
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

    await callback.answer()


@router.callback_query(F.data.in_(TARIFFS.keys()))
async def handle_buy_subscription(callback: types.CallbackQuery):
    tariff = TARIFFS[callback.data]
    user_id = callback.from_user.id
    log_action(user_id, "handle_buy_sub")

    provider_data = {
        "receipt": {
            "items": [
                {
                    "description": tariff["label"],
                    "quantity": 1,
                    "amount": {
                        "value": tariff["amount"] / 100,  # в рублях
                        "currency": "RUB"
                    },
                    "vat_code": 1,
                    "payment_mode": "full_payment",
                    "payment_subject": "commodity"
                }
            ],
            "tax_system_code": 1
        }
    }

    if data_base.get_info(user_id)["sub_type"] != "free_sub":
        additional_description = (
            "\nВнимание! У вас уже есть подписка!\n"
            "При оплате новой оставшиеся дни и токены будут сброшены\n")
    else:
        additional_description = ""

    prices = [types.LabeledPrice(label=tariff["label"], amount=tariff["amount"])]
    print((
        f"title:{tariff['label']}\n"
        f"description:{tariff['description'] + additional_description}"
        f"payload:{tariff['payload']}\n"
        f"provider_token:{PROVIDER_TOKEN}\n"
        "currency=RUB\n"
        f"prices:{prices}\n"
        f"start_parameter:{callback.data}\n"
    ))

    await callback.message.answer_invoice(
        title=tariff["label"],
        description=(tariff["description"] + additional_description)[:255],
        payload=tariff["payload"],
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter=callback.data,
        need_email=True,
        send_email_to_provider=True,
        provider_data=json.dumps(provider_data)
    )
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
    await pre_checkout_q.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: types.Message):
    payload = message.successful_payment.invoice_payload
    user_id = message.from_user.id
    log_action(user_id, f"success_payment:{payload}")

    # По payload узнаём, какой тариф был куплен
    for tariff in TARIFFS.values():
        if payload == tariff["payload"]:
            sub_expires = datetime.now(timezone.utc) + timedelta(days=tariff["days"])
            tokens = tariff["tokens"]

            # 🔧 Обнови БД: выстави подписку, токены, срок
            data_base.set_subscription(user_id, payload, tokens, sub_expires)
            # Тут вставь свою функцию:
            # update_subscription(user_id, tokens, sub_expires)

            await message.answer(
                f"✅ Подписка *{tariff['label']}* активирована!\n"
                f"💬 Доступно: {tokens} генераций\n"
                f"⏳ Срок действия: {sub_expires.strftime('%d.%m.%Y')}",
                parse_mode="Markdown"
            )
            break

# Выберите тип поздравления
# Введите праздник/достижение (при выбраных опциях праздник/достижение
# соответственно)
# Выберите кому будет поздравление
# Выберите стиль поздравления
# Выберите имя получателя("-" - не указывать)
