from sqlalchemy import select, not_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectUpdate
)


class CharityProjectCRUD(
    CRUDBase[
        CharityProject,
        CharityProjectCreate,
        CharityProjectUpdate
    ]
):

    @staticmethod
    async def get_current_project(session: AsyncSession) -> CharityProject:
        project = await session.scalars(
            select(CharityProject).where(
                not_(CharityProject.fully_invested)
            ).order_by(
                CharityProject.create_date
            )
        )
        return project.first()

    @staticmethod
    async def get_projects_by_completion_rate(
            session: AsyncSession
    ) -> list[dict[str, str]]:
        projects = await session.execute(
            select(
                CharityProject.name,
                (func.julianday(CharityProject.close_date) -
                 func.julianday(CharityProject.create_date)
                 ).label('collection_time'),
                CharityProject.description
            ).where(
                CharityProject.fully_invested
            ).order_by('collection_time')
        )
        return projects.all()


charity_project_crud = CharityProjectCRUD(CharityProject)
