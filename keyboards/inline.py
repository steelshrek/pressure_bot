from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def confirm_measure_kb():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="Підтвердити",
        callback_data="confirm_save")
    )
    builder.add(InlineKeyboardButton(
        text="Виправити",
        callback_data="edit_measure")
    )

    return builder.as_markup()


def cancel_measure_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Відкласти на 10 хвилин",
        callback_data="cancel_send"
    ))
    return builder.as_markup()


def report_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="7 днів", callback_data="report_7"))
    builder.add(InlineKeyboardButton(text="2 тижні", callback_data="report_14"))
    builder.add(InlineKeyboardButton(text="3 тижні", callback_data="report_21"))
    builder.add(InlineKeyboardButton(text="1 місяць", callback_data="report_30"))
    builder.add(InlineKeyboardButton(text="Увесь період", callback_data="report_0"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="back"))
    builder.adjust(2)
    return builder.as_markup()
