from os import getenv


from sqlalchemy import BigInteger, String, ForeignKey, DateTime
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime, time

engine = create_async_engine(getenv("DATABASE_URL"))
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass


# 2. Таблица пользователей
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)  # ID из Телеграма
    name: Mapped[str] = mapped_column(String(100), nullable=True)


# 3. Таблица замеров давления
class PressureRecord(Base):
    __tablename__ = 'pressure_records'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    sys: Mapped[int] = mapped_column()
    dia: Mapped[int] = mapped_column()
    pul: Mapped[int] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)

class Settings(Base):
    __tablename__ = 'settings'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    f_time_of_not:Mapped[time]= mapped_column()
    s_time_of_not:Mapped[time]= mapped_column()

# Функция для создания таблиц при запуске
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)