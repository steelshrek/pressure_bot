from aiogram import Router, types
from aiogram.filters import Command

from db.requsts import get_or_create_settings, set_user
from keyboards.reply import main_menu_kb

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_name = message.from_user.first_name or message.from_user.username or "Користувач"
    await set_user(message.from_user.id, user_name)
    await get_or_create_settings(message.from_user.id)

    await message.answer("Вітаємо. Застосунок готовий до роботи.")
    await message.answer("Оберіть необхідну дію:", reply_markup=main_menu_kb())
