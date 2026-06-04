from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from db.requsts import get_or_create_settings, update_reminder_time
from keyboards.reply import (
    BTN_BACK,
    BTN_CHANGE,
    BTN_REMINDER_SETTINGS,
    main_menu_kb,
    menu_notifications_kb,
)
from services.scheduler import update_settings
from states import OptionSetup

router = Router()


@router.message(F.text == BTN_REMINDER_SETTINGS)
async def work_settings(message: types.Message, state: FSMContext):
    settings = await get_or_create_settings(message.from_user.id)
    morning = settings.f_time_of_not.strftime("%H:%M")
    evening = settings.s_time_of_not.strftime("%H:%M")

    await message.answer(
        f"Поточні нагадування встановлено на {morning} та {evening}.",
        reply_markup=menu_notifications_kb()
    )


@router.message(F.text == BTN_BACK)
async def back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Головне меню", reply_markup=main_menu_kb())


@router.message(F.text == BTN_CHANGE)
async def start_changing_schedule(message: types.Message, state: FSMContext):
    await message.answer(
        "Введіть час ранкового нагадування у форматі HH:MM, наприклад 09:00."
    )
    await state.set_state(OptionSetup.changingMorning)


@router.message(OptionSetup.changingMorning, F.text)
async def process_morning(message: types.Message, state: FSMContext):
    try:
        valid_time = datetime.strptime(message.text.strip(), "%H:%M").time()
        await state.update_data(morningTime=valid_time)
        await message.answer(
            "Введіть час вечірнього нагадування у форматі HH:MM, наприклад 21:00."
        )
        await state.set_state(OptionSetup.changingEvening)
    except ValueError:
        await message.answer(
            "Некоректний формат часу. Введіть час у форматі HH:MM, наприклад 09:00."
        )


@router.message(OptionSetup.changingEvening, F.text)
async def confirming_schedule_evening(message: types.Message, state: FSMContext):
    try:
        evening_time = datetime.strptime(message.text.strip(), "%H:%M").time()
        data = await state.get_data()
        morning_time = data["morningTime"]

        await update_reminder_time(message.from_user.id, morning_time, evening_time)
        await update_settings(message.from_user.id, morning_time, evening_time)

        await message.answer(
            (
                "Нагадування оновлено. "
                f"Ранок: {morning_time.strftime('%H:%M')}, "
                f"вечір: {evening_time.strftime('%H:%M')}."
            ),
            reply_markup=main_menu_kb()
        )
        await state.clear()
    except ValueError:
        await message.answer(
            "Некоректний формат часу. Введіть час у форматі HH:MM, наприклад 21:00."
        )
