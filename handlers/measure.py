import os
from datetime import timedelta, datetime

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.inline import confirm_measure_kb
from db.requsts import add_pressure_record
from keyboards.reply import main_menu_kb, menu_back_kb
from services.ocr import get_pressure_from_gemini
from services.scheduler import scheduler, send_reminder
from states import MeasuresSetup

router = Router()


@router.message(F.text == "📝 Сфоткать тонометр")
async def measure(message: types.Message, state: FSMContext):
    await message.answer("Жду фота", reply_markup=menu_back_kb())
    await state.set_state(MeasuresSetup.sending_photo)


@router.callback_query(F.data == "cancel_send")
async def cancel_photo(callback: types.CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    run_time = datetime.now() + timedelta(minutes=10)

    scheduler.add_job(
        send_reminder,
        trigger="date",
        run_date=run_time,
        args=[tg_id],
        id=f"delay_{tg_id}_{run_time.strftime('%M%S')}"
    )

    await callback.answer("Через 10 мин тада")
    await callback.message.delete()
    await state.clear()


@router.message(F.text == "Назад")
async def back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_menu_kb())


@router.message(MeasuresSetup.sending_photo, F.photo)
@router.message(MeasuresSetup.sending_photo, F.photo)
async def send_photo(message: types.Message, state: FSMContext):
    await message.answer("Читаю фота")
    file_id = message.photo[-1].file_id
    file = await message.bot.get_file(file_id)
    file_path = f"temp_{file_id}.jpg"
    await message.bot.download_file(file.file_path, file_path)

    try:
        result = await get_pressure_from_gemini(file_path)

        # ПРОВЕРКА НА ОШИБКУ ИЗ ГЕМИНИ
        if "error" in result:
            print(f"OCR Error: {result['error']}")  # Увидишь в консоли
            await message.answer(f"Ошибка сервиса: {result['error']}")
            return

        sys = result.get('sys')
        dia = result.get('dia')
        pul = result.get('pul')

        if sys is None or dia is None or pul is None:
            raise KeyError("Missing data")

        await state.update_data(recognized_data=result)

        if (sys < 90) or (sys > 200) or (dia < 40) or (dia > 150) or (pul < 20) or (pul > 200):
            await message.answer("Чота хуня, давай заново")
        else:
            await message.answer(
                f"Распознало: {sys}/{dia}, Пульс: {pul}\nВсе верно?",
                reply_markup=confirm_measure_kb()
            )
            await state.set_state(MeasuresSetup.confirming_data)

    except Exception as e:
        print(f"Хендлер упал: {e}")
        await message.answer("Хуня, попробуй снова")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.callback_query(MeasuresSetup.confirming_data, F.data == "confirm_save")
async def confirm_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Фиксирую показания")
    user_data = await state.get_data()
    result = user_data.get('recognized_data')

    if result:
        await add_pressure_record(callback.from_user.id, result['sys'], result['dia'], result['pul'])
        await callback.message.edit_text("ЕСть")
        await state.clear()


@router.callback_query(MeasuresSetup.confirming_data, F.data == "edit_measure")
async def edit_measure(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введи руками, типа: 120/80/60")
    await state.set_state(MeasuresSetup.sending_manual)


@router.message(MeasuresSetup.sending_manual, F.text)
async def measure_manual(message: types.Message, state: FSMContext):
    try:
        messaglist = message.text.replace(' ', '').split('/')
        if len(messaglist) != 3:
            raise ValueError
        sys, dia, pul = map(int, messaglist)
        await add_pressure_record(message.from_user.id, sys, dia, pul)
        await message.answer("ЕСть", reply_markup=main_menu_kb())
        await state.clear()
    except ValueError:
        await message.answer("Ошибка! Введи в формате: 120/80/60")