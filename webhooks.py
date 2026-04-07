# webhook.py
import asyncio
from aiohttp import web
from os import getenv

from daryabot import setup_handlers, init_scheduler
from services.loader import bot, dp
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from db.models import async_main


async def on_startup(app):
    setup_handlers()
    await async_main()              # создать таблицы
    await init_scheduler()          # поднять APScheduler

    WEBHOOK_URL = f"https://{getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook set: {WEBHOOK_URL}")


async def on_shutdown(app):
    await bot.session.close()


async def main():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(dp, bot).register(app, path="/webhook")
    setup_application(app)

    port = int(getenv("PORT", 10000))
    return app, port


if __name__ == "__main__":
    web.run_app(*asyncio.run(main()))