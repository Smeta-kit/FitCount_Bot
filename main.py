import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_reader import config
from keyboards.keyboards import main_menu, goal_keyboard, gender_keyboard, activity_keyboard



bot = Bot(token=config.bot_token.get_secret_value())

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
    
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())