import asyncio
import os
from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from db.requsts import add_pressure_record
from keyboards.inline import confirm_measure_kb
from keyboards.reply import BTN_BACK, BTN_MEASURE_PHOTO, main_menu_kb, menu_back_kb
from services.ocr import get_pressure_from_gemini
from services.scheduler import scheduler, send_reminder
from states import MeasuresSetup

router = Router()

MIN_SYS = 50
MAX_SYS = 300
MIN_DIA = 30
MAX_DIA = 200
MIN_PUL = 30
MAX_PUL = 220


def normalize_pressure_values(sys_value, dia_value, pul_value):
    sys = int(sys_value)
    dia = int(dia_value)
    pul = int(pul_value)
    return sys, dia, pul


def has_absurd_pressure_values(sys: int, dia: int, pul: int):
    return (
        sys < MIN_SYS
        or sys > MAX_SYS
        or dia < MIN_DIA
        or dia > MAX_DIA
        or pul < MIN_PUL
        or pul > MAX_PUL
        or dia >= sys
    )


async def switch_to_manual_input(message: types.Message, state: FSMContext):
    await message.answer(
        "Розпізнані показники виглядають некоректними. "
        "Введіть дані вручну у форматі 120/80/60."
    )
    await state.set_state(MeasuresSetup.sending_manual)


@router.message(F.text == BTN_MEASURE_PHOTO)
async def measure(message: types.Message, state: FSMContext):
    await message.answer(
        "Надішліть фото екрана тонометра.",
        reply_markup=menu_back_kb()
    )
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
        id=f"delay_{tg_id}_{run_time.strftime('%Y%m%d%H%M%S')}",
        replace_existing=True
    )

    await callback.answer("Нагадування відкладено на 10 хвилин.")
    if callback.message:
        await callback.message.delete()
    await state.clear()


@router.message(F.text == BTN_BACK)
async def back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Головне меню", reply_markup=main_menu_kb())


@router.message(MeasuresSetup.sending_photo, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    await message.answer("Фото отримано. Виконується розпізнавання...")
    asyncio.create_task(process_ocr_logic(message, state))


async def process_ocr_logic(message: types.Message, state: FSMContext):
    destination = None
    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)

        folder = "photos"
        os.makedirs(folder, exist_ok=True)
        destination = os.path.join(folder, f"{photo.file_unique_id}.jpg")

        await message.bot.download_file(file.file_path, destination)
        result = await get_pressure_from_gemini(destination)

        if not {"sys", "dia", "pul"}.issubset(result):
            raise ValueError(result.get("msg", "Не вдалося розпізнати показники."))

        sys, dia, pul = normalize_pressure_values(result["sys"], result["dia"], result["pul"])
        if has_absurd_pressure_values(sys, dia, pul):
            await switch_to_manual_input(message, state)
            return

        await state.update_data(sys=sys, dia=dia, pul=pul)
        await state.set_state(MeasuresSetup.confirming_data)

        await message.answer(
            (
                "Розпізнано:\n"
                f"{sys}\n"
                f"{dia}\n"
                f"{pul}\n\n"
                "Підтвердити збереження?"
            ),
            reply_markup=confirm_measure_kb()
        )
    except Exception as exc:
        print(f"OCR processing error: {exc}")
        await message.answer(
            "Не вдалося розпізнати показники з фото. Введіть дані вручну у форматі 120/80/60."
        )
        await state.set_state(MeasuresSetup.sending_manual)
    finally:
        if destination and os.path.exists(destination):
            os.remove(destination)


@router.callback_query(MeasuresSetup.confirming_data, F.data == "confirm_save")
async def confirm_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Показники зберігаються.")
    user_data = await state.get_data()

    try:
        sys, dia, pul = normalize_pressure_values(
            user_data.get("sys"),
            user_data.get("dia"),
            user_data.get("pul")
        )
    except (TypeError, ValueError):
        await callback.message.answer(
            "Дані відсутні. Введіть показники вручну у форматі 120/80/60."
        )
        await state.set_state(MeasuresSetup.sending_manual)
        return

    if has_absurd_pressure_values(sys, dia, pul):
        await callback.message.answer(
            "Показники некоректні. Введіть дані вручну у форматі 120/80/60."
        )
        await state.set_state(MeasuresSetup.sending_manual)
        return

    await add_pressure_record(callback.from_user.id, sys, dia, pul)
    await callback.message.edit_text("Показники збережено.")
    await callback.message.answer("Оберіть наступну дію:", reply_markup=main_menu_kb())
    await state.clear()


@router.callback_query(MeasuresSetup.confirming_data, F.data == "edit_measure")
async def edit_measure(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Введіть показники вручну у форматі 120/80/60 "
    )
    await state.set_state(MeasuresSetup.sending_manual)


@router.message(MeasuresSetup.sending_manual, F.text)
async def measure_manual(message: types.Message, state: FSMContext):
    try:
        values = [part.strip() for part in message.text.split("/")]
        if len(values) != 3:
            raise ValueError

        sys, dia, pul = normalize_pressure_values(*values)
        if has_absurd_pressure_values(sys, dia, pul):
            raise ValueError

        await add_pressure_record(message.from_user.id, sys, dia, pul)
        await message.answer("Показники збережено.", reply_markup=main_menu_kb())
        await state.clear()
    except ValueError:
        await message.answer(
            "Некоректні показники. Введіть дані у форматі 120/80/60."
        )
