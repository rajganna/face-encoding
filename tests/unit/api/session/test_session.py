import pytest

from unittest.mock import AsyncMock, patch, MagicMock

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.session.models import Sessions
from app_loader import app
from tests.unit.test_utils import (request_data,
                                   invalid_request_data,
                                   media_request_data,
                                   mock_session,
                                   mock_dependencies,
                                   session_dep,
                                   mock_session_id,
                                   mock_get_session_encoding,
                                   mock_session_exists,
                                   mock_create_session_encoding)


client = TestClient(app)


@patch("app.api.session.dao.SessionDep", autospec=True)
def test_create_session_success(mock_session, mock_create_session_encoding):
    mock_session.return_value = MagicMock(return_value=request_data)
    mock_create_session_encoding.return_value = None

    response = client.post("/api/sessions", json=request_data)

    assert response.status_code == 201
    assert response.json() == {
        "status": "Session created successfully",
        "verification": request_data["verification"]
    }
    assert mock_session_id == request_data["verification"]["vendorData"]


@patch("app.api.session.dao.SessionDep", autospec=True)
def test_create_session_already_exists(mock_session, mock_session_exists):
    mock_session.return_value = MagicMock(return_value=request_data)
    mock_session_exists.return_value.execute.side_effect = HTTPException(
        status_code=400,
        detail="Session with this sessionId already exists."
    )
    response = client.post("/api/sessions", json=request_data)

    assert response.status_code == 400
    assert response.json() == {
        "detail":
            "Session with this sessionId already exists."
    }


@patch("app.api.session.dao.SessionDep", autospec=True)
def test_create_session_invalid_request(mock_session):
    mock_existing_session = Sessions(session_id="123456", callback="http://example.com/callback", status="CREATED")
    mock_session.return_value = AsyncMock(return_value=mock_existing_session)

    response = client.post("/api/sessions", json=invalid_request_data)

    assert response.status_code == 422


@patch("app.api.session.dao.SessionDep", autospec=True)
def test_get_summary_success(mock_session, mock_get_session_encoding):
    session_id = "1e1d09a8-4674-41df-b2f3-25c3bd5efd58"
    mock_encodings = AsyncMock()
    mock_encodings.Encodings.encodings = []
    mock_session.return_value = AsyncMock()
    mock_get_session_encoding.return_value = mock_encodings

    response = client.get(f"/api/sessions/{session_id}/summary")

    assert response.status_code == 200
    assert response.json() == {
        "sessionId": session_id,
        "status": "Verified",
        "verification": mock_encodings.Encodings.encodings
    }


@patch("app.api.session.dao.SessionDep", autospec=True)
def test_get_summary_not_found(mock_session, mock_get_session_encoding):
    mock_session.return_value = AsyncMock()
    mock_get_session_encoding.return_value = None

    response = client.get(f"/api/sessions/{mock_session_id}/summary")

    assert response.status_code == 404
    assert response.json() == {"detail": "Encodings not found"}


def test_upload_media_success(mock_dependencies):
    mock_verify, mock_post_encodings, mock_save_encoding = mock_dependencies
    mock_verify.return_value = MagicMock()
    mock_face_encodings_response = MagicMock()
    mock_face_encodings_response.json.return_value = [[0.1, 0.2, 0.3]]
    mock_post_encodings.return_value = mock_face_encodings_response

    response = client.post("/api/sessions/test-session/media", json=media_request_data)

    assert response.status_code == 201
    assert response.json() == {
        "sessionId": "test-session",
        "status": "Success",
        "verification": [[0.1, 0.2, 0.3]]
    }


def test_upload_media_session_not_found(mock_dependencies):
    mock_verify, mock_post_encodings, mock_save_encoding = mock_dependencies
    mock_verify.side_effect = HTTPException(status_code=404, detail="Session not found")

    response = client.post("/api/sessions/test-session/media", json=media_request_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


def test_upload_media_encoding_error(mock_dependencies):
    mock_verify, mock_post_encodings, mock_save_encoding = mock_dependencies
    mock_verify.return_value = None
    mock_post_encodings.side_effect = HTTPException(status_code=500, detail="Encoding service error")

    response = client.post("/api/sessions/test-session/media", json=media_request_data)

    assert response.status_code == 500
    assert response.json() == {"detail": "Encoding service error"}
