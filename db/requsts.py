from datetime import time, datetime, timedelta

from db.models import async_session, User, PressureRecord, Settings
from sqlalchemy import select


async def set_user(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()


async def add_pressure_record(tg_id, sys, dia, pul):
    async with async_session() as session:
        # Находим внутреннего ID пользователя
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            new_record = PressureRecord(user_id=user.id, sys=sys, dia=dia, pul=pul)
            session.add(new_record)
            await session.commit()


async def get_pressure_history(tg_id: int, days = None):
    async with async_session() as session:
        query = select(PressureRecord).join(User).where(User.tg_id == tg_id)

        if days:
            start_date = datetime.now() - timedelta(days=days)
            query = query.where(PressureRecord.timestamp >= start_date)

        query = query.order_by(PressureRecord.timestamp.asc())
        result = await session.execute(query)
        return result.scalars().all()




async def get_or_create_settings(tg_id: int):
    async with async_session() as session:
        # Ищем настройки, соединяя таблицы по user_id
        query = select(Settings).join(User).where(User.tg_id == tg_id)
        settings = await session.scalar(query)
        if not settings:
            # Сначала находим юзера, чтобы получить его внутренний id
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                settings = Settings(user_id=user.id, f_time_of_not=time(9,0), s_time_of_not=time(21,0))
                session.add(settings)
                await session.commit()
                await session.refresh(settings)
        return settings


async def update_reminder_time(tg_id, morning, evening):
    async with async_session() as session:
        # 1. Находим настройки через JOIN с пользователем по его tg_id
        query = select(Settings).join(User).where(User.tg_id == tg_id)
        settings = await session.scalar(query)

        if settings:
            settings.f_time_of_not = morning
            settings.s_time_of_not = evening
            await session.commit()
        else:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                new_settings = Settings(
                    user_id=user.id,
                    f_time_of_not=morning,
                    s_time_of_not=evening
                )
                session.add(new_settings)
                await session.commit()