from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    # Добавляем кнопки
    builder.add(KeyboardButton(text="📊 История"))
    builder.add(KeyboardButton(text="⚙️ Настройки напоминалок"))
    builder.add(KeyboardButton(text="📝 Сфоткать тонометр"))
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)

def menu_notifications_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Изменить"))
    builder.add(KeyboardButton(text="Назад"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def menu_back_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Назад"))
    return builder.as_markup(resize_keyboard=True)
# Использование в хендлере:
# await message.answer("Выберите действие:", reply_markup=main_menu_kb())