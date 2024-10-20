import pytest
import asyncio

from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import (
    AsyncSession)
from app.api.session.dao import (create_db_session,
                                 get_db_session,
                                 get_session_encoding,
                                 save_session_encoding)
from app.api.session.dto import Status
from app.api.session.models import Sessions, Encodings
from tests.unit.test_utils import (MockRequestModel,
                                   mock_session_id,
                                   mock_callback,
                                   session_dep,
                                   MockSessionData
                                   )


@pytest.mark.asyncio
async def test_create_db_session(session_dep):
    session_dep = AsyncMock()
    request = MockRequestModel()

    await create_db_session(request, session_dep)

    session_data = session_dep.add.call_args[0][0]

    assert session_data.session_id == mock_session_id
    assert session_data.callback == mock_callback
    assert session_data.status == Status.CREATED

    session_dep.commit.assert_awaited_once()
    session_dep.refresh.assert_awaited_once_with(session_data)


@pytest.mark.asyncio
async def test_get_db_session(session_dep):
    mock_session = MockSessionData(
        session_id=mock_session_id,
        callback='some_callback',
        status=Status.SUBMITTED
    )
    mock_query_result = MagicMock()
    mock_query_result.scalars.return_value.first.return_value = mock_session
    mock_db = AsyncMock(return_value=asyncio.Future())
    mock_db.execute.return_value = mock_query_result

    result = await get_db_session(mock_session_id, mock_db)

    assert result == mock_session


@pytest.mark.asyncio
async def test_get_db_session_found(session_dep):
    mock_session = MockSessionData(
        session_id=mock_session_id,
        callback='some_callback',
        status=Status.CREATED
    )

    mock_query_result = MagicMock()
    mock_query_result.scalars.return_value.first.return_value = mock_session
    mock_db = AsyncMock(return_value=asyncio.Future())
    mock_db.execute.return_value = mock_query_result

    result = await get_db_session(mock_session_id, mock_db)

    assert result == mock_session


@pytest.mark.asyncio
async def test_get_session_encoding_found(session_dep):
    expected_encodings = Encodings(session_id=mock_session_id, encodings={"example": [1.0, 2.0]})
    mock_query_result = MagicMock()
    mock_query_result.scalars.return_value.first.return_value = expected_encodings
    mock_db = AsyncMock(return_value=asyncio.Future())
    mock_db.execute.return_value = mock_query_result

    result = await get_session_encoding(mock_session_id, mock_db)
    assert result == expected_encodings


@pytest.mark.asyncio
async def test_get_session_encoding_not_found(session_dep):
    mock_query_result = MagicMock()
    mock_query_result.scalars.return_value.first.return_value = None
    mock_db = AsyncMock(return_value=asyncio.Future())
    mock_db.execute.return_value = mock_query_result

    result = await get_session_encoding(mock_session_id, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_save_session_encoding(session_dep):
    session_dep = AsyncMock()
    mock_encodings = {"example_encoding": [1.0, 2.0]}
    session_dep.execute = AsyncMock()
    session_dep.add = AsyncMock()
    session_dep.commit = AsyncMock()
    session_dep.refresh = AsyncMock()

    await save_session_encoding(mock_session_id, mock_encodings, session_dep)

    session_dep.execute.assert_called_once()
    session_dep.add.assert_called_once()
    added_encoding_data = session_dep.add.call_args[0][0]
    assert added_encoding_data.session_id == mock_session_id
    assert added_encoding_data.encodings == mock_encodings
    session_dep.commit.assert_called_once()
