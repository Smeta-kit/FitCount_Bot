from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from state.state import UserData
from keyboards.keyboards import (
    gender_keyboard,
    activity_keyboard,
    goal_keyboard,
    main_menu
)
from src.storage import save_user

router = Router()


# старт
@router.message(Command("start"))
async def cmd_start(message: types.Message):

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Введите свои данные")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "💪 Добро пожаловать в FitCount!\n\n"
        "Я помогу считать калории и следить за прогрессом.\n\n"
        "Давай настроим профиль 👇",
        reply_markup=kb
    )


# начать ввод данных
@router.message(lambda message: message.text in ["Введите свои данные", "✏️ Изменить данные"])
async def start_data_input(message: types.Message, state: FSMContext):

    await state.set_state(UserData.gender)

    await message.answer(
        "Выбери свой пол",
        reply_markup=gender_keyboard
    )


# ввод пола
@router.message(UserData.gender)
async def process_gender(message: types.Message, state: FSMContext):

    if message.text.lower() not in ['мужской', 'женский', 'м', 'ж']:
        await message.answer(
            "Выберите пол используя кнопки",
            reply_markup=gender_keyboard
        )
        return

    await state.update_data(gender=message.text)

    await state.set_state(UserData.height)

    await message.answer(
        "Пол сохранен!\n\nТеперь укажи рост (см):",
        reply_markup=ReplyKeyboardRemove()
    )


# ввод роста
@router.message(UserData.height)
async def process_height(message: types.Message, state: FSMContext):

    try:
        height = int(message.text)

        if height < 110 or height > 250:
            raise ValueError

    except ValueError:
        await message.answer("Введите корректный рост (110-250 см)")
        return

    await state.update_data(height=height)

    await state.set_state(UserData.weight)

    await message.answer("Рост сохранён!\n\nТеперь укажи вес (кг):")


# ввод веса
@router.message(UserData.weight)
async def process_weight(message: types.Message, state: FSMContext):

    try:
        weight = int(message.text)

        if weight < 30 or weight > 300:
            raise ValueError

    except ValueError:
        await message.answer("Введите корректный вес")
        return

    await state.update_data(weight=weight)

    await state.set_state(UserData.age)

    await message.answer("Вес сохранён!\n\nТеперь укажи возраст:")


# ввод возраста
@router.message(UserData.age)
async def process_age(message: types.Message, state: FSMContext):

    try:
        age = int(message.text)

        if age < 5 or age > 120:
            raise ValueError

    except ValueError:
        await message.answer("Введите корректный возраст")
        return

    await state.update_data(age=age)

    await state.set_state(UserData.activity)

    await message.answer(
        "Выберите уровень активности:",
        reply_markup=activity_keyboard
    )


# ввод активности
@router.message(UserData.activity)
async def process_activity(message: types.Message, state: FSMContext):

    activity_levels = {
        "Сидячий образ жизни (1.2)": 1.2,
        "Легкая активность (1.375)": 1.375,
        "Средняя активность (1.55)": 1.55,
        "Высокая активность (1.725)": 1.725
    }

    if message.text not in activity_levels:
        await message.answer("Выберите вариант из кнопок")
        return

    await state.update_data(activity=activity_levels[message.text])

    await state.set_state(UserData.goal)

    await message.answer(
        "Какая у вас цель?",
        reply_markup=goal_keyboard
    )


# ввод цели + расчёт
@router.message(UserData.goal)
async def process_goal(message: types.Message, state: FSMContext):

    goals = {
        "🔥 Похудение": "lose",
        "⚖️ Поддержание формы": "maintain",
        "💪 Набор массы": "gain"
    }

    if message.text not in goals:
        await message.answer("Выберите цель используя кнопки")
        return

    await state.update_data(goal=goals[message.text])

    data = await state.get_data()

    gender = data["gender"].lower()
    weight = data["weight"]
    height = data["height"]
    age = data["age"]
    activity = data["activity"]
    goal = data["goal"]

    # формула Миффлина-Сан Жеора
    if gender in ["мужской", "м"]:
        calories = (10 * weight + 6.25 * height - 5 * age + 5) * activity
    else:
        calories = (10 * weight + 6.25 * height - 5 * age - 161) * activity

    # корректировка под цель
    if goal == "lose":
        calories *= 0.8
    elif goal == "gain":
        calories *= 1.2

    calories = round(calories)

    # БЖУ
    protein = round(1.8 * weight)
    fat = round(weight)
    carbs = round((calories * 0.40) / 4)

    save_user(
    message.from_user.id,
    {
        **data,
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs
    }
)

    await message.answer(
        "✅ Профиль создан!\n\n"
        f"🔥 Калории: {calories} ккал\n\n"
        f"🥩 Белки: {protein} г\n"
        f"🧈 Жиры: {fat} г\n"
        f"🍞 Углеводы: {carbs} г",
        reply_markup=main_menu
    )

    await state.clear()
