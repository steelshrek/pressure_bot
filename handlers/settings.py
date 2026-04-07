import os
from gc import callbacks

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime
from db.requsts import get_or_create_settings, update_reminder_time
from keyboards.reply import main_menu_kb, menu_notifications_kb
from services.ocr import get_pressure_from_gemini
from services.scheduler import update_settings
from states import OptionSetup

router = Router()



@router.message(F.text=="⚙️ Настройки напоминалок")
async def work_settings(message: types.Message, state: FSMContext):
    settings = await get_or_create_settings(message.from_user.id)
    await message.answer(f"Сейчас у тебя напоминалка в {settings.f_time_of_not} и в {settings.s_time_of_not}",reply_markup=menu_notifications_kb())


@router.message(F.text=="Назад")
async def back(message:types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_menu_kb())


@router.message(F.text=="Изменить")
async def start_changing_schedule(message: types.Message, state: FSMContext):
    await message.answer("Введи время в которое тебе удобно мерять давление утром (например 9:00)")
    await state.set_state(OptionSetup.changingMorning)
@router.message(OptionSetup.changingMorning, F.text)
async def process_morning(message: types.Message, state: FSMContext):
    try:
        valid_time = datetime.strptime(message.text, "%H:%M").time()
        await state.update_data(morningTime=valid_time)
        await message.answer("Отлично! Теперь введи время для ВЕЧЕРА (например, 21:00):")
        await state.set_state(OptionSetup.changingEvening)
    except ValueError:
        await message.answer("Попробуй еще")
@router.message(OptionSetup.changingEvening, F.text)
async def confirming_schedule_evening(message: types.Message, state: FSMContext):
    try:
        evening_time = datetime.strptime(message.text, "%H:%M").time()
        data = await state.get_data()
        morning_time = data['morningTime']

        await update_reminder_time(message.from_user.id, morning_time, evening_time)
        await update_settings(message.from_user.id, morning_time, evening_time)

        await message.answer(
            f"ЕСть! Утро: {morning_time.strftime('%H:%M')}, Вечер: {evening_time.strftime('%H:%M')}",
            reply_markup=main_menu_kb()
        )
        await state.clear()
    except ValueError:
        await message.answer("Попробуй еще")
