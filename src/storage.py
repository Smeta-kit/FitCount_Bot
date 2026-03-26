import json
import os

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


# сохранение всех пользователей
def save_users(users_data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)


# сохранить одного пользователя
def save_user(user_id: int, data: dict):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)


# получить пользователя
def get_user(user_id: int):
    users = load_users()
    return users.get(str(user_id))