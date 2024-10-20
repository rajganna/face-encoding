from typing import Annotated, Optional, Dict, Any
from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy import JSON, Column
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import Field, SQLModel, create_engine

from app.config.app_config import config

sqlite_url = config.database_name
connect_args = {"check_same_thread": False}
async_engine = create_async_engine(sqlite_url, connect_args=connect_args)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
sync_engine = create_engine(sqlite_url.replace("sqlite+aiosqlite", "sqlite"),
                            connect_args=connect_args)


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


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
