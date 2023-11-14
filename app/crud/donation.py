from sqlalchemy import select, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation
from app.schemas.donation import DonationCreate


class DonationCrud(
    CRUDBase[
        Donation,
        DonationCreate,
        None
    ]
):

    @staticmethod
    async def get_unused_donations(session: AsyncSession) -> list[Donation]:
        donations = await session.scalars(
            select(Donation).where(
                not_(Donation.fully_invested)
            ).order_by(
                Donation.create_date
            )
        )
        return donations.all()


donation_crud = DonationCrud(Donation)
