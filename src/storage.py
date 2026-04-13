import json
import os
from datetime import datetime

FILE_PATH = "src/users.json"


import json
import os

FILE_PATH = "src/users.json"


def load_users():
    if not os.path.exists(FILE_PATH):
        return {}

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users_data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

def save_user(user_id: int, data: dict):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

def get_user(user_id: int):
    users = load_users()
    return users.get(str(user_id))

def save_all_users(users):
    with open("src/users.json", "w") as f:
        json.dump(users, f, indent=4)
        
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

    save_all_users(users)


def save_user(user_id, data):
    users = load_users()

    users[str(user_id)] = {
        **data,
        "eaten_calories": 0,
        "eaten_protein": 0,
        "eaten_fat": 0,
        "eaten_carbs": 0,
        "last_update": datetime.now().strftime("%Y-%m-%d")  
    }

    save_users(users)    
    
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