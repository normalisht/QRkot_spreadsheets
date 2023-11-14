from sqlalchemy import Column, Integer, ForeignKey, Text

from app.core.db import InvestmentBase


class Donation(InvestmentBase):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
