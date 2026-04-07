from aiogram import types, Router, F
from aiogram.filters import Command

from db.requsts import set_user, get_or_create_settings
from keyboards.reply import main_menu_kb

router=Router()

@router.message(Command('start'))
async def start_handler(message: types.Message):
    await set_user(message.from_user.id, message.from_user.first_name)
    await get_or_create_settings(message.from_user.id)
    await message.answer(f"Даров, Даря")
    await message.answer("Выбери действие:", reply_markup=main_menu_kb())

