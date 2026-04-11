from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Мой профиль")],
        [KeyboardButton(text="🍽 Добавить рацион (ИИ помощник)")],
        [KeyboardButton(text="✏️ Изменить данные")]
    ],
    resize_keyboard=True
)

gender_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

activity_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сидячий образ жизни (1.2)")],
        [KeyboardButton(text="Легкая активность (1.375)")],
        [KeyboardButton(text="Средняя активность (1.55)")],
        [KeyboardButton(text="Высокая активность (1.725)")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

goal_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Похудение")],
        [KeyboardButton(text="⚖️ Поддержание формы")],
        [KeyboardButton(text="💪 Набор массы")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
