from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


BTN_HISTORY = "Історія"
BTN_REMINDER_SETTINGS = "Налаштування нагадувань"
BTN_MEASURE_PHOTO = "Надіслати фото тонометра"
BTN_CHANGE = "Змінити"
BTN_BACK = "Назад"


def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=BTN_HISTORY))
    builder.add(KeyboardButton(text=BTN_REMINDER_SETTINGS))
    builder.add(KeyboardButton(text=BTN_MEASURE_PHOTO))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def menu_notifications_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=BTN_CHANGE))
    builder.add(KeyboardButton(text=BTN_BACK))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def menu_back_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=BTN_BACK))
    return builder.as_markup(resize_keyboard=True)
