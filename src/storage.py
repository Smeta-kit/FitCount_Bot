import json
import os
from datetime import datetime, timedelta

FILE_PATH = "src/users.json"


# 📥 загрузка всех пользователей
def load_users():
    if not os.path.exists(FILE_PATH):
        return {}

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


# 💾 сохранение всех пользователей
def save_users(users):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


# 👤 сохранить пользователя (создание/обновление)
def save_user(user_id, data):
    users = load_users()
    user_id = str(user_id)

    if user_id not in users:
        users[user_id] = {}

    # ✅ только нужные поля
    allowed_fields = {
        "gender",
        "height",
        "weight",
        "age",
        "activity",
        "goal",
        "calories",
        "protein",
        "fat",
        "carbs",
    }

    clean_data = {k: v for k, v in data.items() if k in allowed_fields}

    users[user_id].update(clean_data)

    # значения по умолчанию
    users[user_id].setdefault("eaten_calories", 0)
    users[user_id].setdefault("eaten_protein", 0)
    users[user_id].setdefault("eaten_fat", 0)
    users[user_id].setdefault("eaten_carbs", 0)
    users[user_id].setdefault("workouts", [])
    users[user_id].setdefault("streak", 0)
    users[user_id].setdefault("last_streak_date", None)
    users[user_id].setdefault("last_update", datetime.now().strftime("%Y-%m-%d"))

    save_users(users)

# 📊 получить пользователя
def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))


# 🍽 обновление съеденного
def update_eaten(user_id, cals, prot, fat, carbs):
    users = load_users()
    user_id = str(user_id)

    if user_id not in users:
        return

    user = users[user_id]

    user["eaten_calories"] = user.get("eaten_calories", 0) + cals
    user["eaten_protein"] = user.get("eaten_protein", 0) + prot
    user["eaten_fat"] = user.get("eaten_fat", 0) + fat
    user["eaten_carbs"] = user.get("eaten_carbs", 0) + carbs

    users[user_id] = user
    save_users(users)


# 🔄 сброс каждый день
def check_and_reset(user_id):
    users = load_users()
    user = users.get(str(user_id))

    if not user:
        return

    today = datetime.now().strftime("%Y-%m-%d")

    if user.get("last_update") != today:
        user["eaten_calories"] = 0
        user["eaten_protein"] = 0
        user["eaten_fat"] = 0
        user["eaten_carbs"] = 0
        user["last_update"] = today

        save_users(users)


# 🔥 обновление стрика
def update_streak(user_id):
    users = load_users()
    user = users.get(str(user_id))

    if not user:
        return

    today = datetime.now().date()
    last_date_str = user.get("last_streak_date")

    remaining_calories = user["calories"] - user.get("eaten_calories", 0)

    # если превысил норму — сброс
    if remaining_calories < 0:
        user["streak"] = 0
        user["last_streak_date"] = str(today)
        save_users(users)
        return

    if not last_date_str:
        user["streak"] = 1
        user["last_streak_date"] = str(today)
        save_users(users)
        return

    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()

    if last_date == today:
        return

    if last_date == today - timedelta(days=1):
        user["streak"] += 1
    else:
        user["streak"] = 1

    user["last_streak_date"] = str(today)
    save_users(users)


# 🏋️ добавить тренировку
def add_workout(user_id, workout_text):
    users = load_users()
    user_id = str(user_id)

    if user_id not in users:
        users[user_id] = {}

    users[user_id].setdefault("workouts", [])
    users[user_id]["workouts"].append(workout_text)

    save_users(users)