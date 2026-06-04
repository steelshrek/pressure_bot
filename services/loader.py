from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

load_dotenv()

token = getenv("TOKEN")
if not token:
    raise RuntimeError("Не налаштовано TOKEN у файлі .env.")

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
