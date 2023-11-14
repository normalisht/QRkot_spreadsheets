from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Donation, CharityProject
from app.crud import charity_project_crud, donation_crud


async def donation_investment(
        donation: Donation,
        session: AsyncSession
) -> Donation:
    project = await charity_project_crud.get_current_project(session)
    if project is None:
        return donation
    _, donation = await add_donation(project, donation, session)
    return donation


async def project_investment(
        project: CharityProject,
        session: AsyncSession
) -> CharityProject:
    donations = await donation_crud.get_unused_donations(session)

    for donation in donations:
        project, _ = await add_donation(project, donation, session)
        if project.fully_invested:
            return project

    return project


async def add_donation(
        project: CharityProject,
        donation: Donation,
        session: AsyncSession
) -> tuple[CharityProject, Donation]:
    donation_amount = min(project.remainder, donation.remainder)
    project.invested_amount += donation_amount
    donation.invested_amount += donation_amount

    session.add(donation)
    session.add(project)
    await session.commit()
    await session.refresh(donation)
    await session.refresh(project)
    return project, donation
