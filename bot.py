from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from handlers import user_handlers, callback_handler
from services.data_base import connect_db, close_db
import signal
import datetime


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def shutdown(bot: Bot):
    await bot.session.close()
    close_db()
    print("🔻 Бот завершил работу корректно")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="/start",
            description="Запустить бота"),
        BotCommand(
            command="/generate_congrat",
            description="Сгенерировать поздравление"),
        BotCommand(
            command="/information",
            description="Личный кабинет"),
        BotCommand(
            command="/favourite",
            description="Избранные поздравления"),
        BotCommand(
            command="/subscription",
            description="Купить подписку"),
        BotCommand(
            command="/promocode",
            description="Ввести промокод")
    ]
    await bot.set_my_commands(commands)


async def main():
    global bot
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    before_conn = datetime.datetime.now()
    connect_db()
    after_conn = datetime.datetime.now()
    print(f"Подключение производилось {after_conn - before_conn}")

    # Регистрация хэндлеров
    dp.include_router(user_handlers.router)
    dp.include_router(callback_handler.router)

    await set_commands(bot)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка во время запуска: {e}")
    finally:
        await shutdown(bot)


def run():
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig,
                                lambda: asyncio.ensure_future(shutdown(bot)))

    try:
        loop.run_until_complete(main())
    finally:
        loop.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
