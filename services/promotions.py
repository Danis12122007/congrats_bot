from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramNotFound, TelegramAPIError
import asyncio


async def broadcast_message(bot: Bot, user_ids: list[int], text: str, reply_markup=None) -> dict:
    success = 0
    failed = 0
    if reply_markup:
        for user_id in user_ids:
            user_id = user_id[0]
            try:
                await bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup())
                success += 1
            except (TelegramForbiddenError, TelegramNotFound):
                print(f"❌ Пользователь {user_id} недоступен (удалил бота или заблокировал)")
                failed += 1
            except TelegramAPIError as e:
                print(f"⚠️ Ошибка при отправке {user_id}: {e}")
                failed += 1
            await asyncio.sleep(0.05)  # Пауза во избежание flood
    else:
        for user_id in user_ids:
            user_id = user_id[0]
            try:
                await bot.send_message(chat_id=user_id, text=text)
                success += 1
            except (TelegramForbiddenError, TelegramNotFound):
                print(f"❌ Пользователь {user_id} недоступен (удалил бота или заблокировал)")
                failed += 1
            except TelegramAPIError as e:
                print(f"⚠️ Ошибка при отправке {user_id}: {e}")
                failed += 1
            await asyncio.sleep(0.05)  # Пауза во избежание flood
    return {
        "success": success,
        "failed": failed
    }
