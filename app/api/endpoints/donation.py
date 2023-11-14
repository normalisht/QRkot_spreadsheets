from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import donation_crud
from app.models import User
from app.schemas.donation import (
    DonationShortDB, DonationDB, DonationCreate
)
from app.services.investment import donation_investment

router = APIRouter()


@router.get(
    '/my',
    response_model=list[DonationShortDB],
    response_model_exclude_none=True,
)
async def get_user_donations(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    return await donation_crud.get_multi(session, user)


@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session)
):
    return await donation_crud.get_multi(session)


@router.post(
    '/',
    response_model=DonationShortDB,
    response_model_exclude_none=True,
)
async def create_donation(
        donation: DonationCreate,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    donation = await donation_crud.create(donation, session, user)
    return await donation_investment(donation, session)
