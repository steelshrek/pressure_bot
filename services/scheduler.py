from sqlalchemy import select

from db.models import Settings, User, async_session
from keyboards.inline import cancel_measure_kb
from services.loader import bot, dp, scheduler
from states import MeasuresSetup


async def send_reminder(tg_id):
    state_with_data = dp.fsm.resolve_context(
        bot=bot,
        chat_id=tg_id,
        user_id=tg_id
    )
    await state_with_data.clear()
    await state_with_data.set_state(MeasuresSetup.sending_photo)

    await bot.send_message(
        tg_id,
        "Будь ласка, надішліть фото екрана тонометра для фіксації показників.",
        reply_markup=cancel_measure_kb()
    )


async def get_settings():
    async with async_session() as session:
        query = select(Settings, User.tg_id).join(User, Settings.user_id == User.id)
        result = await session.execute(query)

        for setting, tg_id in result:
            scheduler.add_job(
                send_reminder,
                trigger="cron",
                hour=setting.f_time_of_not.hour,
                minute=setting.f_time_of_not.minute,
                args=[tg_id],
                id=f"remind_1_{tg_id}",
                replace_existing=True
            )
            scheduler.add_job(
                send_reminder,
                trigger="cron",
                hour=setting.s_time_of_not.hour,
                minute=setting.s_time_of_not.minute,
                args=[tg_id],
                id=f"remind_2_{tg_id}",
                replace_existing=True
            )


async def update_settings(tg_id, new_time_morning, new_time_evening):
    for job_id in [f"remind_1_{tg_id}", f"remind_2_{tg_id}"]:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

    scheduler.add_job(
        send_reminder,
        trigger="cron",
        hour=new_time_morning.hour,
        minute=new_time_morning.minute,
        args=[tg_id],
        id=f"remind_1_{tg_id}",
        replace_existing=True
    )
    scheduler.add_job(
        send_reminder,
        trigger="cron",
        hour=new_time_evening.hour,
        minute=new_time_evening.minute,
        args=[tg_id],
        id=f"remind_2_{tg_id}",
        replace_existing=True
    )
