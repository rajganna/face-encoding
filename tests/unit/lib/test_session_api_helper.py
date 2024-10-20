import base64
from unittest.mock import MagicMock, AsyncMock, patch

import asyncio
import pytest
from fastapi import HTTPException
from httpx import Response
from starlette import status

from app.api.session.dto import ValidationErrorResponseModel, Status
from app.lib.session_api_helper import validate_api_response, get_filename_and_content_type, verify_session_id, \
    post_face_encodings
from tests.unit.test_utils import MockSessionData, MockMediaUploadRequestModel, mock_session_id
from app.api.session.models import Sessions


@pytest.mark.asyncio
async def test_verify_api_response_invalid_request():
    response = Response(status_code=400)
    with pytest.raises(HTTPException) as exc:
        validate_api_response(response)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "More than 5 faces found in the image."


@pytest.mark.asyncio
async def test_verify_api_response_validation_error():
    response = Response(status_code=422, json="Invalid JSON")
    with pytest.raises(HTTPException) as exc_info:
        validate_api_response(response)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc_info.value.detail == "Validation error occurred with the external API response."


@pytest.mark.asyncio
async def test_verify_api_response_invalid_json(mocker):
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


@pytest.mark.asyncio
async def test_verify_session_id_not_found():
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db = AsyncMock(return_value=asyncio.Future())
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await verify_session_id(mock_session_id, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


@pytest.mark.asyncio
async def test_verify_session_id_already_processed():
    mock_session_data = Sessions(
        session_id=mock_session_id,
        callback='some_callback',
        status=Status.SUBMITTED
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_session_data
    mock_db = AsyncMock(return_value=asyncio.Future())
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await verify_session_id(mock_session_id, mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Session already processed"


@pytest.mark.asyncio
async def test_verify_session_id_success():
    mock_session_data = Sessions(
        session_id=mock_session_id,
        callback='some_callback',
        status=Status.CREATED
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_session_data
    mock_db = AsyncMock(return_value=asyncio.Future())
    mock_db.execute.return_value = mock_result

    await verify_session_id(mock_session_id, mock_db)

    mock_db.execute.assert_called_once()
    mock_result.scalars.assert_called_once()
    mock_result.scalars.return_value.first.assert_called_once()


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
