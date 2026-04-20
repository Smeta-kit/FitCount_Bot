import asyncio
import logging
logging.basicConfig(level=logging.INFO)
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import os
from dotenv import load_dotenv
from handlers.user import router

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")


async def main():
    bot = Bot(token=bot_token)

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    
