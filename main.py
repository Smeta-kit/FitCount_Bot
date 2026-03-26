import asyncio
import logging
logging.basicConfig(level=logging.INFO)
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import config
from handlers.user import router



async def main():
    bot = Bot(token=config.bot_token.get_secret_value())

    dp = Dispatcher(storage=MemoryStorage())

    # подключаем роутер
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())