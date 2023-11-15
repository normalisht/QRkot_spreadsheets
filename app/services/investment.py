from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import charity_project_crud, donation_crud
from app.models import Donation, CharityProject

InvestmentObj = TypeVar('InvestmentObj', Donation, CharityProject)


async def investment(
        invest_obj: InvestmentObj,
        session: AsyncSession
) -> InvestmentObj:
    if isinstance(invest_obj, Donation):
        list_objects: list[CharityProject] = (
            await charity_project_crud.get_unclosed_project(session)
        )
    elif isinstance(invest_obj, CharityProject):
        list_objects: list[Donation] = (
            await donation_crud.get_unused_donations(session)
        )
    else:
        raise TypeError('investment object must be Donation or CharityProject')

    for obj in list_objects:
        await transfer(invest_obj, obj, session)
        if invest_obj.fully_invested:
            break

    await session.commit()
    await session.refresh(invest_obj)

    return invest_obj


async def transfer(
        obj1: InvestmentObj,
        obj2: InvestmentObj,
        session: AsyncSession
):
    transfer_amount = min(obj1.remainder, obj2.remainder)
    obj1.invested_amount += transfer_amount
    obj2.invested_amount += transfer_amount
    await session.flush()
