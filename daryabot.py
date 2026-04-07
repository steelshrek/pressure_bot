from os import getenv
import asyncio
from aiohttp import web
from handlers import start, measure, settings, data
from services.loader import dp, bot
from services.scheduler import get_settings, scheduler


def setup_handlers():
    dp.include_router(start.router)
    dp.include_router(measure.router)
    dp.include_router(settings.router)
    dp.include_router(data.router)


async def init_scheduler():
    from services.scheduler import get_settings
    await get_settings()
    scheduler.start()