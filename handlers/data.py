import os
from datetime import timedelta, datetime

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import types
from aiogram.types import FSInputFile

from db.requsts import add_pressure_record, get_pressure_history
from keyboards.inline import report_kb
from keyboards.reply import main_menu_kb, menu_back_kb
from services.data_create import create_excel_report, create_pressure_chart
from services.ocr import get_pressure_from_gemini
from services.scheduler import scheduler, send_reminder
from states import MeasuresSetup

router = Router()


@router.message(F.text=="📊 История")
async def chart(message: types.Message):
    await message.answer("За какое время отчет ?", reply_markup=report_kb())

@router.callback_query(F.data.startswith("report_"))
async def send_report(callback: types.CallbackQuery):
    days = int(callback.data.split("_")[1])
    records = await get_pressure_history(callback.from_user.id, days if days > 0 else None)

    if not records:
        await callback.answer("Нема записей")
        return

    excel_file = create_excel_report(records, f"pressure_{callback.from_user.id}.xlsx")
    chart_file = create_pressure_chart(records, f"chart_{callback.from_user.id}.png")

    # Отправляем фото графика
    await callback.message.answer_photo(
        FSInputFile(chart_file),
        caption=f"Отчет за {'все время' if days == 0 else f'{days} дн.'}"
    )
    # Отправляем файл таблицы
    await callback.message.answer_document(FSInputFile(excel_file))

    # Удаляем временные файлы
    os.remove(excel_file)
    os.remove(chart_file)
@router.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Главное меню", reply_markup=main_menu_kb())
    await callback.answer()