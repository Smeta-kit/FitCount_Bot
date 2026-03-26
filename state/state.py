from aiogram.fsm.state import State, StatesGroup

users_data = {}

class UserData(StatesGroup):
    gender = State()
    height = State()
    weight = State()
    age = State()
    activity = State()
    goal = State()
