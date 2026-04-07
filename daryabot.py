from os import getenv
import asyncio
from aiohttp import web
from handlers import start, measure, settings, data
from services.loader import dp, bot
from services.scheduler import get_settings, scheduler

async def handle(request):
    return web.Response(text="Bot is alive")

async def main():
    # 1. Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(measure.router)
    dp.include_router(settings.router)
    dp.include_router(data.router)

    # 2. Инициализация БД
    from db.models import async_main
    await async_main()

    # 3. Настройка планировщика
    await get_settings()
    scheduler.start() # ВЫЗЫВАЕМ ТОЛЬКО ОДИН РАЗ

    # 4. Запуск веб-сервера для Render
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    print(f"Server started on port {port}")

    # 5. Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())