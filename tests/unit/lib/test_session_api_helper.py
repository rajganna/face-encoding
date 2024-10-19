import base64
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from fastapi import HTTPException
from httpx import Response
from starlette import status

from app.api.session.dto import ValidationErrorResponseModel, Status
from app.lib.session_api_helper import validate_api_response, get_filename_and_content_type, verify_session_id, \
    post_face_encodings
from tests.unit.test_utils import MockSessionData, MockMediaUploadRequestModel


def test_verify_api_response_invalid_request():
    response = Response(status_code=400)
    with pytest.raises(HTTPException) as exc:
        validate_api_response(response)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "More than 5 faces found in the image."


def test_verify_api_response_validation_error():
    response = Response(status_code=422, json="Invalid JSON")

    with pytest.raises(HTTPException) as exc_info:
        validate_api_response(response)

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc_info.value.detail == "Validation error occurred with the external API response."


def test_verify_api_response_invalid_json(mocker):
    response_data = {
        "detail": [{"loc": ["body", "field"], "msg": "Invalid input", "type": "value_error"}]
    }
    response = Response(status_code=422, json=response_data)

    validation_error_response = ValidationErrorResponseModel(**response_data)

    mocker.patch('app.api.session.dto.ValidationErrorResponseModel', return_value=validation_error_response)

    with pytest.raises(HTTPException) as exc_info:
        validate_api_response(response)

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc_info.value.detail == "Validation error occurred with the external API response."


def test_get_filename_and_content_type():
    filename, content_type = get_filename_and_content_type("jpg")
    assert filename == "image.jpg"
    assert content_type == "image/jpeg"

    filename, content_type = get_filename_and_content_type("png")
    assert filename == "image.png"
    assert content_type == "image/png"

    filename, content_type = get_filename_and_content_type("gif")
    assert filename == "image.gif"
    assert content_type == "image/gif"

    filename, content_type = get_filename_and_content_type("bmp")
    assert filename == "image.bmp"
    assert content_type == "image/bmp"


def test_verify_session_id_not_found():
    mock_session_dep = MagicMock()
    session_id = "non_existent_session_id"

    mock_session_dep.exec.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        verify_session_id(session_id, mock_session_dep)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


def test_verify_session_id_already_processed():
    mock_session_dep = MagicMock()
    session_id = "processed_session_id"

    mock_session_dep.exec.return_value.first.return_value = MockSessionData(session_id, Status.SUBMITTED)

    with pytest.raises(HTTPException) as exc_info:
        verify_session_id(session_id, mock_session_dep)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Session already processed"


def test_verify_session_id_success():
    mock_session_dep = MagicMock()
    session_id = "test_session_id"

    mock_session_dep.exec.return_value.first.return_value = MockSessionData(session_id, Status.CREATED)

    try:
        verify_session_id(session_id, mock_session_dep)
    except HTTPException:
        pytest.fail("HTTPException was raised unexpectedly")


@pytest.mark.asyncio
async def test_post_face_encodings_success():
    image_type = 'image/jpeg'
    content = base64.b64encode(b'some_binary_data').decode('utf-8')
    media = MockMediaUploadRequestModel(image_type, content)

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}

    with patch('httpx.AsyncClient.post', return_value=mock_response) as mock_post:
        response = await post_face_encodings(media)

    assert response == mock_response
    mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_post_face_encodings_http_exception():
    image_type = 'image/jpeg'
    content = base64.b64encode(b'some_binary_data').decode('utf-8')  # Create a proper base64 string
    media = MockMediaUploadRequestModel(image_type, content)

    with patch('httpx.AsyncClient.post', side_effect=HTTPException(status_code=400, detail="Bad Request")):
        with pytest.raises(HTTPException) as exc_info:
            await post_face_encodings(media)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Bad Request"


@pytest.mark.asyncio
async def test_post_face_encodings_general_exception():
    image_type = 'image/jpeg'
    content = base64.b64encode(b'some_binary_data').decode('utf-8')
    media = MockMediaUploadRequestModel(image_type, content)

    with patch('httpx.AsyncClient.post', side_effect=Exception("Some error occurred")):
        with pytest.raises(HTTPException) as exc_info:
            await post_face_encodings(media)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Error uploading images to external API"
