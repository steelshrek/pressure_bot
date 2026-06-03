from datetime import time, datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload  # Понадобится, если будут сложные связи

from db.models import async_session, User, PressureRecord, Settings


async def set_user(tg_id: int, name: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()
        return user


async def add_pressure_record(tg_id: int, sys: int, dia: int, pul: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            user = User(tg_id=tg_id, name="User")
            session.add(user)
            await session.flush()

        new_record = PressureRecord(user_id=user.id, sys=sys, dia=dia, pul=pul)
        session.add(new_record)
        await session.commit()
        return True


async def get_pressure_history(tg_id: int, days: int = None):
    async with async_session() as session:
        user_id_subquery = select(User.id).where(User.tg_id == tg_id).scalar_subquery()

        query = select(PressureRecord).where(PressureRecord.user_id == user_id_subquery)

        if days:
            start_date = datetime.now() - timedelta(days=days)
            query = query.where(PressureRecord.timestamp >= start_date)

        query = query.order_by(PressureRecord.timestamp.desc())

        result = await session.execute(query)
        return result.scalars().all()


async def get_or_create_settings(tg_id: int):
    async with async_session() as session:
        query = select(Settings).join(User).where(User.tg_id == tg_id)
        settings = await session.scalar(query)

        if not settings:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                user = User(tg_id=tg_id, name="User")
                session.add(user)
                await session.flush()

            settings = Settings(
                user_id=user.id,
                f_time_of_not=time(9, 0),
                s_time_of_not=time(21, 0)
            )
            session.add(settings)
            await session.commit()
            await session.refresh(settings)

        return settings


async def update_reminder_time(tg_id: int, morning: time, evening: time):
    async with async_session() as session:
        query = select(Settings).join(User).where(User.tg_id == tg_id)
        settings = await session.scalar(query)

        if settings:
            settings.f_time_of_not = morning
            settings.s_time_of_not = evening
        else:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                user = User(tg_id=tg_id, name="User")
                session.add(user)
                await session.flush()

            settings = Settings(
                user_id=user.id,
                f_time_of_not=morning,
                s_time_of_not=evening
            )
            session.add(settings)

        await session.commit()
        return settings