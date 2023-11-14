from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_project_crud
from app.models import CharityProject
from app.schemas.charity_project import (
    CharityProjectDB, CharityProjectCreate, CharityProjectUpdate
)
from app.services.investment import project_investment

router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude={'close_date'},
)
async def get_project_list(session: AsyncSession = Depends(get_async_session)):
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_project(
        project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
):
    await check_project_name_duplicates(project, session)
    new_project = await charity_project_crud.create(project, session)
    return await project_investment(new_project, session)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    project = await charity_project_crud.get(project_id, session)
    await check_project_delete_allowed(project)
    return await charity_project_crud.remove(project, session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def update_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session)
):
    project = await charity_project_crud.get(project_id, session)
    await check_project_update_allowed(project, obj_in, session)
    return await charity_project_crud.update(project, obj_in, session)


async def check_project_name_duplicates(
        project: Union[CharityProjectCreate, CharityProjectUpdate],
        session: AsyncSession
):
    try:
        await charity_project_crud.check_unique_fields(project, session)
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


async def check_project_update_allowed(
        project: CharityProject,
        obj_in: CharityProjectUpdate,
        session: AsyncSession
):
    await check_project_name_duplicates(obj_in, session)
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )
    if (obj_in.full_amount is not None and
            obj_in.full_amount < project.invested_amount):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Запрещено устанавливать требуемую сумму меньше внесённой'
        )


async def check_project_delete_allowed(
        project: CharityProject,
):
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Такого проекта не существует'
        )
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя удалять завершённый проект'
        )
