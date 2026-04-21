from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import requests
import json
import os
from dotenv import load_dotenv
import re
from src.storage import get_user, save_user, update_eaten, check_and_reset, update_streak, add_workout, load_users, save_users
from state.state import UserData 
from keyboards.keyboards import (
    gender_keyboard,
    activity_keyboard,
    goal_keyboard,
    main_menu,
    confirm_keyboard,
    stop_keyboard
)

router = Router()

load_dotenv()

def format_value(value, name):
    if value >= 0:
        return f"{name}: {value}"
    else:
        return f"{name}: превышено на {abs(value)}"

API_KEY = os.getenv("OPENROUTER_API_KEY")

@router.message(Command("start"))
async def cmd_start(message: types.Message):

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Введите свои данные")]],
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
        await message.answer("Выберите пол используя кнопки", reply_markup=gender_keyboard)
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

    await message.answer("Какая у вас цель?", reply_markup=goal_keyboard)


# ввод цели + сохранение
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

    try:
        gender = data["gender"].lower()
        weight = data["weight"]
        height = data["height"]
        age = data["age"]
        activity = data["activity"]
        goal = data["goal"]

        if gender in ["мужской", "м"]:
            calories = (10 * weight + 6.25 * height - 5 * age + 5) * activity
        else:
            calories = (10 * weight + 6.25 * height - 5 * age - 161) * activity

        if goal == "lose":
            calories *= 0.8
        elif goal == "gain":
            calories *= 1.2

        calories = round(calories)

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

    except Exception as e:
        print("Ошибка:", e)
        await message.answer("⚠️ Ошибка при сохранении данных")
        return

    await message.answer(
        "✅ Профиль создан!\n\n"
        f"🔥 Калории: {calories} ккал\n\n"
        f"🥩 Белки: {protein} г\n"
        f"🧈 Жиры: {fat} г\n"
        f"🍞 Углеводы: {carbs} г",
        reply_markup=main_menu
    )

    await state.clear()


# профиль
@router.message(lambda message: message.text == "📊 Мой профиль")
async def show_profile(message: types.Message):
    check_and_reset(message.from_user.id)
    
    user = get_user(message.from_user.id)

    if not user:
        await message.answer("❌ Сначала заполните данные")
        return

    streak = user.get("streak", 0)
    
    await message.answer(
    "📊 Ваш профиль:\n\n"
    f"🔥 {format_value(user['calories'] - user.get('eaten_calories', 0), 'Калории')} ккал\n"
    f"🥩 {format_value(user['protein'] - user.get('eaten_protein', 0), 'Белки')} г\n"
    f"🧈 {format_value(user['fat'] - user.get('eaten_fat', 0), 'Жиры')} г\n"
    f"🍞 {format_value(user['carbs'] - user.get('eaten_carbs', 0), 'Углеводы')} г\n"
    f"🔥 Стрик: {streak} дней\n\n"
)
    
############################### Генерация ответа ИИшки ###############################


def generate_response(prompt):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "nvidia/nemotron-3-nano-30b-a3b:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You're a nutritionist. Calculate your calories, fats, and carbohydrates. The answer is strictly: calories, proteins, fats, and carbohydrates (4 numbers separated by spaces)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3
            })
        )

        data = response.json()

        print("API RESPONSE:", data)  

       
        if "error" in data:
            return f"Ошибка API: {data['error']['message']}"

       
        if "choices" not in data:
            return "⚠️ Неверный ответ от API"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("Ошибка:", e)
        return "⚠️ Ошибка соединения"


@router.message(lambda message: message.text == "🍽 Добавить рацион (ИИ помощник)")
async def ask_food(message: types.Message, state: FSMContext): 
    await state.set_state(UserData.food)  
    await message.answer("Напишите, что вы съели (например: рис 200, курица 150)")  
    
@router.message(UserData.food)
async def process_food(message: types.Message, state: FSMContext):
    check_and_reset(message.from_user.id)
    msg = await message.answer("Считаю КБЖУ ⌛")

    response = generate_response(message.text)

    numbers = list(map(int, re.findall(r"\d+", response)))

    if len(numbers) != 4:
        await message.answer("❌ Ошибка обработки еды, попробуйте ещё раз")
        return

    calories, protein, fat, carbs = numbers

    await msg.delete()

    sent_msg = await message.answer(
    "🍽 Найдено:\n\n"
    f"🔥 {calories} ккал\n"
    f"🥩 {protein} г\n"
    f"🧈 {fat} г\n"
    f"🍞 {carbs} г\n\n"
    "Добавить в рацион?",
    reply_markup=confirm_keyboard
)
    
    await state.update_data(
        food_calories=calories,
        food_protein=protein,
        food_fat=fat,
        food_carbs=carbs,
        food_message_id=sent_msg.message_id
    )

    await state.set_state(UserData.confirm_food)

@router.message(UserData.confirm_food)
async def confirm_food(message: types.Message, state: FSMContext):
    check_and_reset(message.from_user.id)
    data = await state.get_data()

    msg_id = data.get("food_message_id")

    if msg_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=msg_id
            )
        except:
            pass

    if message.text == "❌ Нет":
        await message.answer("Ок, не добавляю 👌", reply_markup=main_menu)
        await state.clear()
        return

    if message.text != "✅ Да":
        await message.answer("Выберите вариант с кнопок")
        return

    data = await state.get_data()

    calories = data["food_calories"]
    protein = data["food_protein"]
    fat = data["food_fat"]
    carbs = data["food_carbs"]


    update_eaten(message.from_user.id, calories, protein, fat, carbs)

    user = get_user(message.from_user.id)

    remaining_calories = user["calories"] - user.get("eaten_calories", 0)
    remaining_protein = user["protein"] - user.get("eaten_protein", 0)
    remaining_fat = user["fat"] - user.get("eaten_fat", 0)
    remaining_carbs = user["carbs"] - user.get("eaten_carbs", 0)
    
    
    await message.answer(
    "✅ Добавлено!\n\n"
    "📊 Баланс:\n"
    f"🔥 {format_value(remaining_calories, 'Калории')} ккал\n"
    f"🥩 {format_value(remaining_protein, 'Белки')} г\n"
    f"🧈 {format_value(remaining_fat, 'Жиры')} г\n"
    f"🍞 {format_value(remaining_carbs, 'Углеводы')} г",
    reply_markup=main_menu
    )
    update_streak(message.from_user.id)
    await state.clear()
    
    
    
###################### ТРЕНИРОВКИ ####################
@router.message(lambda m: m.text == "➕ Добавить тренировку")
async def start_workout(message: types.Message, state: FSMContext):

    await state.set_state(UserData.workout_day)

    await message.answer(
        "Введите день тренировки (например: Понедельник)",
        reply_markup=stop_keyboard
    )


@router.message(UserData.workout_day)
async def workout_day(message: types.Message, state: FSMContext):

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=main_menu)
        return

    valid_days = {
        "понедельник": "Понедельник",
        "вторник": "Вторник",
        "среда": "Среда",
        "четверг": "Четверг",
        "пятница": "Пятница",
        "суббота": "Суббота",
        "воскресенье": "Воскресенье",
        "пн": "Понедельник",
        "вт": "Вторник",
        "ср": "Среда",
        "чт": "Четверг",
        "пт": "Пятница",
        "сб": "Суббота",
        "вс": "Воскресенье",
    }

    user_input = message.text.strip().lower()

    if user_input not in valid_days:
        await message.answer(
            "❌ Введите корректный день недели\n\nПример: Понедельник или Пн",
            reply_markup=stop_keyboard
        )
        return

    day = valid_days[user_input]

    user = get_user(message.from_user.id)
    if user and "workouts" in user:
        for workout in user["workouts"]:
            if workout.startswith(day):
                await message.answer(
                    f"❌ Тренировка на {day} уже есть!",
                    reply_markup=main_menu
                )
                await state.clear()
                return

    await state.update_data(day=day)
    await state.set_state(UserData.workout_muscle)

    await message.answer(
        "Какая группа мышц?",
        reply_markup=stop_keyboard
    )


# мышцы
@router.message(UserData.workout_muscle)
async def workout_muscle(message: types.Message, state: FSMContext):

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=main_menu)
        return

    await state.update_data(muscle=message.text, exercises=[])
    await state.set_state(UserData.workout_exercises)

    await message.answer(
        "Вводите упражнения по одному сообщению.\nКогда закончите — нажмите ⛔ Завершить",
        reply_markup=stop_keyboard
    )


@router.message(UserData.workout_exercises)
async def workout_exercises(message: types.Message, state: FSMContext):

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=main_menu)
        return

    if message.text == "⛔ Завершить":
        data = await state.get_data()

        day = data.get("day")

        if not day:
            await message.answer("❌ Ошибка: день не найден. Начните заново")
            await state.clear()
            return
        muscle = data["muscle"]
        exercises = data["exercises"]

        if not exercises:
            await message.answer("❌ Вы не добавили упражнения")
            return

        workout_text = f"{day}\n{muscle}\n" + "\n".join(exercises)

        data = await state.get_data()

        if "edit_index" in data:
            users = load_users()
            user_id = str(message.from_user.id)

            users[user_id]["workouts"][data["edit_index"]] = workout_text
            save_users(users)
        else:
            add_workout(message.from_user.id, workout_text)

        await message.answer(
            "✅ Тренировка сохранена!",
            reply_markup=main_menu
        )

        await state.clear()
        return

    data = await state.get_data()
    exercises = data.get("exercises", [])

    exercises.append(message.text)

    await state.update_data(exercises=exercises)

    await message.answer("➕ Добавлено")


# просмотр тренировок
@router.message(lambda m: m.text == "🏋️ Тренировки")
async def show_workouts(message: types.Message):

    user = get_user(message.from_user.id)

    if not user or not user.get("workouts"):
        await message.answer("❌ У вас пока нет тренировок")
        return

    day_short = {
        "Понедельник": "Пн",
        "Вторник": "Вт",
        "Среда": "Ср",
        "Четверг": "Чт",
        "Пятница": "Пт",
        "Суббота": "Сб",
        "Воскресенье": "Вс"
    }

    text = "🏋️ Ваши тренировки:\n\n"

    for workout in user["workouts"]:
        lines = workout.split("\n")
        day = lines[0]

        text += f"📅 {day_short.get(day, day)}\n"
        text += "\n".join(lines[1:])
        text += "\n\n"

    await message.answer(text)
    
@router.message(lambda m: m.text == "✏️ Изменить тренировку")
async def edit_workout_start(message: types.Message, state: FSMContext):

    user = get_user(message.from_user.id)

    if not user or not user.get("workouts"):
        await message.answer("❌ У вас нет тренировок")
        return

    text = "Выберите день тренировки для изменения:\n\n"

    for workout in user["workouts"]:
        day = workout.split("\n")[0]
        text += f"• {day}\n"

    await state.set_state(UserData.edit_workout_day)

    await message.answer(text, reply_markup=stop_keyboard)
    
@router.message(UserData.edit_workout_day)
async def edit_workout_day(message: types.Message, state: FSMContext):

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=main_menu)
        return

    user = get_user(message.from_user.id)

    selected_day = message.text.strip()

    workouts = user.get("workouts", [])

    for i, workout in enumerate(workouts):
        if workout.startswith(selected_day):
            await state.update_data(edit_index=i, day=selected_day)
            await state.set_state(UserData.workout_muscle)

            await message.answer(
                f"Редактируем {selected_day}\n\nВведите новую группу мышц:",
                reply_markup=stop_keyboard
            )
            return

    await message.answer("❌ День не найден, попробуйте снова")