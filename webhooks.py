import asyncio
from aiohttp import web
from os import getenv

from daryabot import setup_handlers, init_scheduler
from services.loader import bot, dp
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from db.models import async_main


async def on_startup(app):
    setup_handlers()

    await async_main()      # создать таблицы
    await init_scheduler()  # поднять APScheduler

    webhook_url = f"https://{getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    await bot.set_webhook(webhook_url)
    print(f"Webhook set: {webhook_url}")


async def on_shutdown(app):
    await bot.session.close()


async def create_app():
    app = web.Application()

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Регистрируем обработчик вебхука
    # SimpleRequestHandler сам связывает бот и диспетчер для этого пути
    SimpleRequestHandler(dp, bot).register(app, path="/webhook")

    # ВАЖНО: Передаем и app, и dp
    setup_application(app, dp)

    return app


if __name__ == "__main__":
    port = int(getenv("PORT", 10000))

    # Для aiohttp лучше использовать такой способ запуска,
    # чтобы не было конфликтов с asyncio.run()
    app = asyncio.get_event_loop().run_until_complete(create_app())

    web.run_app(app, host="0.0.0.0", port=port)