from typing import Optional

from sqlalchemy import select, update

from app.api.session.dto import RequestModel, Status
from app.api.session.models import SessionDep, Sessions, Encodings


def create_db_session(request: RequestModel,
                      session_dep: SessionDep):
    session_data = Sessions(session_id=str(request.verification.vendorData),
                            callback=str(request.verification.callback),
                            status=Status.CREATED,
                            doc_type=str(request.verification.document.type),
                            doc_number=str(request.verification.document.number),
                            country=str(request.verification.document.country))
    session_dep.add(session_data)
    session_dep.commit()
    session_dep.refresh(session_data)


def get_db_session(session_id: str,
                   session_dep: SessionDep) \
        -> Optional[Sessions]:
    return session_dep.exec(select(Sessions).
                            where(Sessions.session_id == session_id)).first()


def save_session_encoding(session_id: str,
                          encodings: dict,
                          session_dep: SessionDep) -> None:
    session_dep.exec(
        update(Sessions)
        .where(Sessions.session_id == session_id)
        .values(status=Status.SUBMITTED)
    )
    encoding_data = Encodings(session_id=session_id, encodings=encodings)
    session_dep.add(encoding_data)
    session_dep.commit()
    session_dep.refresh(encoding_data)


def get_session_encoding(session_id: str,
                         session_dep: SessionDep) -> Optional[Encodings]:
    return session_dep.exec(select(Encodings).
                            where(Encodings.session_id == session_id)).first()
