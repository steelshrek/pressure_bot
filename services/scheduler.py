from os import getenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from aiogram import Bot, Dispatcher
from db.models import async_session, Settings, User
from db.requsts import update_reminder_time
from keyboards.inline import cancel_measure_kb
from services.loader import bot, dp, scheduler
from states import MeasuresSetup

token = getenv("TOKEN")


async def send_reminder(tg_id):
    await bot.send_message(tg_id, "СКИНЬ ФОТА ТОНОМЕТРА, ПРЯМ ЩАС", reply_markup=cancel_measure_kb())
    state_with_data = dp.fsm.resolve_context(
        bot=bot,
        chat_id=tg_id,
        user_id=tg_id
    )
    await state_with_data.set_state(MeasuresSetup.sending_photo)

async def get_settings():
    async with async_session() as session:
        # Получаем настройки вместе с tg_id пользователя
        query = select(Settings, User.tg_id).join(User, Settings.user_id == User.id)
        result = await session.execute(query)

        for setting, tg_id in result:
            # Добавляем первое напоминание
            scheduler.add_job(
                send_reminder,
                trigger="cron",
                hour=setting.f_time_of_not.hour,
                minute=setting.f_time_of_not.minute,
                args=[tg_id],
                id=f"remind_1_{tg_id}"  # Уникальный ID, чтобы не дублировать
            )
            # Добавляем второе напоминание
            scheduler.add_job(
                send_reminder,
                trigger="cron",
                hour=setting.s_time_of_not.hour,
                minute=setting.s_time_of_not.minute,
                args=[tg_id],
                id=f"remind_2_{tg_id}"
            )
async def update_settings(tg_id, new_time_morning, new_time_evening ):
    async with async_session() as session:
        await update_reminder_time(tg_id, new_time_morning, new_time_evening)
        if scheduler.get_job(f"remind_1_{tg_id}") or scheduler.get_job(f"remind_2_{tg_id}"):
            scheduler.remove_job(f"remind_1_{tg_id}")
            scheduler.remove_job(f"remind_2_{tg_id}")
        scheduler.add_job(
            send_reminder,
            trigger="cron",
            hour=new_time_morning.hour,
            minute=new_time_morning.minute,
            args=[tg_id],
            id=f"remind_1_{tg_id}"
        )
        scheduler.add_job(
            send_reminder,
            trigger="cron",
            hour=new_time_evening.hour,
            minute=new_time_evening.minute,
            args=[tg_id],
            id=f"remind_2_{tg_id}"
        )