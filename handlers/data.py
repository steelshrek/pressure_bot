import os

from aiogram import F, Router, types
from aiogram.types import FSInputFile

from db.requsts import get_pressure_history
from keyboards.inline import report_kb
from keyboards.reply import BTN_HISTORY, main_menu_kb
from services.data_create import create_excel_report, create_pressure_chart

router = Router()


@router.message(F.text == BTN_HISTORY)
async def chart(message: types.Message):
    await message.answer("Оберіть період для формування звіту:", reply_markup=report_kb())


@router.callback_query(F.data.startswith("report_"))
async def send_report(callback: types.CallbackQuery):
    days = int(callback.data.split("_")[1])
    records = await get_pressure_history(callback.from_user.id, days if days > 0 else None)

    if not records:
        await callback.answer("Записи за обраний період відсутні.", show_alert=True)
        return

    excel_file = None
    chart_file = None

    try:
        excel_file = create_excel_report(records, f"pressure_{callback.from_user.id}.xlsx")
        chart_file = create_pressure_chart(records, f"chart_{callback.from_user.id}.png")

        period = "увесь період" if days == 0 else f"{days} дн."
        await callback.message.answer_photo(
            FSInputFile(chart_file),
            caption=f"Звіт за {period}"
        )
        await callback.message.answer_document(FSInputFile(excel_file))
        await callback.answer()
    finally:
        for file_path in (excel_file, chart_file):
            if file_path and os.path.exists(file_path):
                os.remove(file_path)


@router.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Головне меню", reply_markup=main_menu_kb())
    await callback.answer()
