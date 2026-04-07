from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def confirm_measure_kb():
    builder = InlineKeyboardBuilder()

    # Кнопка с данными для обработки ботом
    builder.add(InlineKeyboardButton(
        text="✅ Все верно",
        callback_data="confirm_save")
    )
    builder.add(InlineKeyboardButton(
        text="❌ Ошибка",
        callback_data="edit_measure")
    )

    return builder.as_markup()

def cancel_measure_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Щас не могу", callback_data="cancel_send"))
    return builder.as_markup()


def report_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="7 дней", callback_data="report_7"))
    builder.add(InlineKeyboardButton(text="2 недели", callback_data="report_14"))
    builder.add(InlineKeyboardButton(text="3 недели", callback_data="report_21"))
    builder.add(InlineKeyboardButton(text="1 месяц", callback_data="report_30"))
    builder.add(InlineKeyboardButton(text="Все время", callback_data="report_0"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="back"))
    return builder.as_markup()