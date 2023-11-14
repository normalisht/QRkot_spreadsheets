from sqlalchemy import Column, String, Text

from app.core.db import InvestmentBase


class CharityProject(InvestmentBase):
    name = Column(String(100), unique=True)
    description = Column(Text, nullable=False)
