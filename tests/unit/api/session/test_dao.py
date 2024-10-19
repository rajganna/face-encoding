from unittest.mock import MagicMock

from app.api.session.dao import (create_db_session,
                                 get_db_session,
                                 get_session_encoding,
                                 save_session_encoding)
from app.api.session.dto import Status
from app.api.session.models import Sessions, Encodings
from tests.unit.test_utils import (MockRequestModel,
                                   mock_session_id,
                                   mock_callback,
                                   session_dep)


def test_create_db_session(session_dep):
    request = MockRequestModel()

    create_db_session(request, session_dep)
    session_dep.add.assert_called_once()
    session_data = session_dep.add.call_args[0][0]
    assert session_data.session_id == mock_session_id
    assert session_data.callback == mock_callback
    assert session_data.status == Status.CREATED  #


def test_get_db_session(session_dep):
    expected_session = Sessions(session_id=mock_session_id,
                                callback="some_callback",
                                status="CREATED")
    mock_query_result = MagicMock()
    mock_query_result.first.return_value = expected_session
    session_dep.exec.return_value = mock_query_result

    result = get_db_session(mock_session_id, session_dep)

    assert result is expected_session


def test_get_db_session_found(session_dep):
    mock_query_result = MagicMock()
    mock_query_result.first.return_value = None
    session_dep.exec.return_value = mock_query_result

    result = get_db_session(mock_session_id, session_dep)

    session_dep.exec.assert_called_once()

    assert result is None


def test_get_session_encoding_found(session_dep):
    expected_encoding = Encodings(
        session_id=mock_session_id,
        encodings={"example_encoding": [1.0, 2.0]})

    mock_query_result = MagicMock()
    mock_query_result.first.return_value = expected_encoding
    session_dep.exec.return_value = mock_query_result

    result = get_session_encoding(mock_session_id, session_dep)

    session_dep.exec.assert_called_once()
    assert result is expected_encoding


def test_get_session_encoding_not_found(session_dep):
    mock_query_result = MagicMock()
    mock_query_result.first.return_value = None
    session_dep.exec.return_value = mock_query_result

    result = get_session_encoding(mock_session_id, session_dep)

    assert result is None


def test_save_session_encoding(session_dep):
    mock_encodings = {"example_encoding": [1.0, 2.0]}

    save_session_encoding(mock_session_id, mock_encodings, session_dep)

    session_dep.exec.assert_called_once()
    session_dep.add.assert_called_once()
    added_encoding_data = session_dep.add.call_args[0][0]
    assert added_encoding_data.session_id == mock_session_id
    assert added_encoding_data.encodings == mock_encodings
