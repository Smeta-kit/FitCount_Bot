from aiogram.fsm.state import State, StatesGroup

users_data = {}

class UserData(StatesGroup):
    gender = State()
    height = State()
    weight = State()
    age = State()
    activity = State()
    goal = State()
    food = State()
    confirm_food = State()
    workout = State()
    workout_day = State()
    workout_muscle = State()
    workout_exercises = State()