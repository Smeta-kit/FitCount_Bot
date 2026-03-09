import logging 
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config

bot = Bot(token=config.bot_token.get_secret_value())

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('💪 Добро пожаловать в FitCount! \n Привет! Я — твой персональный счетовод в мире питания. \n Моя задача — сделать подсчет калорий таким же простым, как и шагомер считает твои шаги.\n FitCount умеет: \n 🧮 Точный счет. Быстрый поиск калорий и БЖУ по названию продукта. \n 📊 Контроль прогресса. Веди дневник питания и следи, укладываешься ли ты в норму. \n 💪 Контроль тренеровок. Записывай свои тренервоки и следи за прогрессом. \n Давай настроим профиль, введи свои данные 👇 ')
    
async def main():
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())
    