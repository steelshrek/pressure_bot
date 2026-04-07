from os import getenv
import asyncio
from aiohttp import web
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from handlers import start, measure, settings, data
from services.loader import dp, bot
from services.scheduler import get_settings, scheduler

async def handle(request):
    return web.Response(text="Bot is alive")

async def main():
    dp.include_router(start.router)
    dp.include_router(measure.router)
    dp.include_router(settings.router)
    dp.include_router(data.router)
    from db.models import async_main
    await async_main()
    await get_settings()
    scheduler.start()
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render сам подставит нужный порт в переменную окружения PORT
    port = int(getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    from db.models import async_main
    await async_main()
    await get_settings()
    scheduler.start()

    print(f"Server started on port {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



