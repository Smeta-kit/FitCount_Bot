<p align="center"> <img src="https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python" alt="Python"> <img src="https://img.shields.io/badge/Aiogram-3.x-green?style=for-the-badge&logo=telegram" alt="Aiogram"> <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"> </p><p align="center"> <b>FitCount</b> — это твой персональный диетолог в кармане. Просто отправь боту, что ты съел, и он посчитает калории, белки, жиры и углеводы, поможет следить за нормой и достигать фитнес-целей. 🚀 </p>

# 💪 FitCount Bot

Telegram-бот для подсчёта калорий, БЖУ, ведения рациона и отслеживания тренировок.

## 🚀 Возможности

### 📊 Профиль
- Расчёт суточной нормы калорий (формула Миффлина-Сан Жеора)
- Подсчёт:
  - Белков 🥩
  - Жиров 🧈
  - Углеводов 🍞
- Учёт уровня активности и цели (похудение / поддержание / набор)

---

### 🍽 Рацион (с ИИ)
- Ввод еды обычным текстом  
  _пример: `рис 200 г, курица 150 г`_
- Автоматический расчёт КБЖУ через нейросеть
- Подтверждение перед добавлением
- Учёт съеденного за день
- Отображение остатка

---

### 🏋️ Тренировки
- Добавление тренировок:
  - День недели
  - Группа мышц
  - Упражнения (построчно)
- Запись нескольких упражнений
- Запрет дубликатов дней
- Просмотр всех тренировок
- Редактирование тренировок ✏️
- Отмена ввода ❌

---

### 🔥 Дополнительно
- Дневной сброс КБЖУ (каждый день)
- Стрики (дни без превышения калорий)
- Хранение данных в JSON

---

## 🧠 Технологии

- Python 3.11+
- aiogram 3.x
- FSM (Finite State Machine)
- OpenRouter API (LLM для расчёта КБЖУ)
- JSON как база данных

---

## 📁 Структура проекта
workoutbot/
│
├── handlers/
│ └── user.py # Основная логика бота
│
├── keyboards/
│ └── keyboards.py # Клавиатуры
│
├── src/
│ └── storage.py # Работа с JSON БД
│
└── state/
   └── state.py # FSM состояния

  
---

## ⚙️ Установка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/fitcount-bot.git
cd fitcount-bot

### 2. Создать виртуальное окружение

python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

### 3. Установить зависимости

pip install -r requirements.txt

### 4. Создать .env

BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_api_key

### 5. Запуск

python main.py
