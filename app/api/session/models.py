from typing import Annotated, Optional, Dict, Any

from fastapi import Depends
from sqlalchemy import JSON, Column
from sqlmodel import Field, Session, SQLModel, create_engine

from app.config.app_config import config

sqlite_file_name = config.database_name
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


class Sessions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(default=None, index=True)
    callback: str = Field(default=None, index=True, max_length=255)
    status: str = Field(default=None)
    doc_type: str = Field(default=None)
    doc_number: str = Field(default=None)
    country: str = Field(default=None)


class Encodings(SQLModel, table=True):
    session_id: str = Field(index=True, nullable=False, primary_key=True)
    encodings: Dict[str, Any] = Field(default_factory=dict,
                                      sa_column=Column(JSON))

    class Config:
        arbitrary_types_allowed = True


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
