from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.api.session.dto import RequestModel, Status
from app.api.session.models import SessionDep, Sessions, Encodings


async def create_db_session(request: RequestModel,
                            session_dep: AsyncSession):
    session_data = Sessions(
        session_id=str(request.verification.vendorData),
        callback=str(request.verification.callback),
        status=Status.CREATED,
        doc_type=str(request.verification.document.type),
        doc_number=str(request.verification.document.number),
        country=str(request.verification.document.country)
    )
    session_dep.add(session_data)
    await session_dep.flush()
    await session_dep.commit()
    await session_dep.refresh(session_data)


async def get_db_session(session_id: str,
                         session_dep: AsyncSession) -> Optional[Sessions]:
    result = await session_dep.execute(
        select(Sessions).where(Sessions.session_id == session_id)
    )
    return result.scalars().first()


async def save_session_encoding(session_id: str,
                                encodings: dict,
                                session_dep: AsyncSession) -> None:
    await session_dep.execute(
        update(Sessions)
        .where(Sessions.session_id == session_id)
        .values(status=Status.SUBMITTED)
    )

    encoding_data = Encodings(session_id=session_id, encodings=encodings)
    session_dep.add(encoding_data)

    await session_dep.commit()
    await session_dep.refresh(encoding_data)


async def get_session_encoding(session_id: str,
                               session_dep: AsyncSession) -> Optional[Encodings]:
    result = await session_dep.execute(
        select(Encodings).where(Encodings.session_id == session_id)
    )
    return result.scalars().first()
