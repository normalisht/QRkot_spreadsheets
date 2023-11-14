from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.event import listen
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    declarative_base, declared_attr, sessionmaker, validates
)

from app.core.config import settings


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session


class InvestmentBase(Base):
    __abstract__ = True

    full_amount = Column(Integer)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    @hybrid_property
    def remainder(self):
        return self.full_amount - self.invested_amount

    @validates('full_amount')
    def validate_full_amount(self, key, value):
        if value < 1:
            raise ValueError('full_amount minimum value must be 1')
        return value

    @staticmethod
    def update_invested_amount(
            obj, value, oldvalue, initiator
    ):
        if value == obj.full_amount:
            obj.fully_invested = True
            obj.close_date = datetime.now()

    @classmethod
    def __declare_last__(cls):
        listen(cls.invested_amount, 'set', cls.update_invested_amount)
