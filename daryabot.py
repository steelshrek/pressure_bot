from os import getenv
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from handlers import start, measure, settings, data
from services.loader import dp, bot
from services.scheduler import get_settings, scheduler



async def main():
    dp.include_router(start.router)
    dp.include_router(measure.router)
    dp.include_router(settings.router)
    dp.include_router(data.router)
    from db.models import async_main
    await async_main()
    await get_settings()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



