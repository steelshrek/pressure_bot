import asyncio
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



@router.message(F.text=="📝 Сфоткать тонометр")
async def measure(message: types.Message, state: FSMContext):
    await message.answer("Жду фота",reply_markup=menu_back_kb())
    await state.set_state(MeasuresSetup.sending_photo)

@router.callback_query(F.data=="cancel_send")
async def cancel_photo(callback: types.CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id

    # Визначаємо час: зараз + 10 хвилин
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


@router.message(F.text=="Назад")
async def back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_menu_kb())


import os
import asyncio
from aiogram import types, F


# ... ваш роутер ...

@router.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("Читаю фото...")
    # Запускаем фоновую задачу
    asyncio.create_task(process_ocr_logic(message))


async def process_ocr_logic(message: types.Message):
    try:
        # 1. Получаем информацию о файле
        file_id = message.photo[-1].file_id
        file = await message.bot.get_file(file_id)

        # 2. Формируем путь (используем os.path для совместимости с Linux)
        folder = "photos"
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_name = f"{file.file_id}.jpg"
        destination = os.path.join(folder, file_name)

        # 3. СКАЧИВАЕМ файл на диск (Критический момент!)
        await message.bot.download_file(file.file_path, destination)

        # 4. Передаем путь в Gemini
        # Убедитесь, что функция принимает путь к локальному файлу
        result = await get_pressure_from_gemini(destination)

        await message.answer(f"Результат: {result}")

        os.remove(destination)

    except Exception as e:
        print(f"Ошибка в фоне: {e}")
        # Стоит уведомить пользователя, если что-то пошло не так



@router.callback_query(MeasuresSetup.confirming_data, F.data=="confirm_save")
async def confirm_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Фиксирую показания")
    user_data=await state.get_data()
    result=user_data['recognized_data']
    await add_pressure_record(callback.from_user.id,result['sys'],result['dia'],result['pul'])
    await callback.message.edit_text("ЕСть")


@router.callback_query(MeasuresSetup.confirming_data, F.data=="edit_measure")
async def edit_measure(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введи руками, типа: 120/80/60")
    await state.set_state(MeasuresSetup.sending_manual)



@router.message(MeasuresSetup.sending_manual, F.text)
async def measure_manual(message: types.Message, state: FSMContext):
    try:
        messaglist = message.text.split('/')
        if len(messaglist) != 3:
            raise ValueError
        sys, dia, pul = map(int, messaglist)  # Конвертируем всё в числа
        await add_pressure_record(message.from_user.id, sys, dia, pul)
        await message.answer("ЕСть", reply_markup=main_menu_kb())
        await state.clear()
    except ValueError:
        await message.answer("Ошибка! Введи в формате: 120/80/60")




