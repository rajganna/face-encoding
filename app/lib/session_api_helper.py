import base64

import httpx
from fastapi import status, HTTPException
from httpx import Response

from app.api.session.dao import get_db_session
from app.api.session.dto import (ValidationErrorResponseModel,
                                 Status,
                                 MediaUploadRequestModel)
from app.api.session.models import SessionDep
from app.config.app_config import config
from app.lib.logging_config import logger


def validate_api_response(response: Response):
    logger.error(response.status_code)
    if response.status_code == 400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="More than 5 faces found in the image."
        )
    elif response.status_code == 422:
        try:
            errors = ValidationErrorResponseModel(**response.json())
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=errors.detail,
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Validation error occurred with "
                       "the external API response."
            )


def get_filename_and_content_type(image_type: str):
    context = "image"
    filename = f"{context}.jpg"
    content_type = "image/jpeg"

    if "png" in image_type.lower():
        filename = f"{context}.png"
        content_type = "image/png"
    elif "gif" in image_type.lower():
        filename = f"{context}.gif"
        content_type = "image/gif"
    elif "bmp" in image_type.lower():
        filename = f"{context}.bmp"
        content_type = "image/bmp"

    return filename, content_type


def verify_session_id(sessionId: str, session: SessionDep):
    session_data = get_db_session(sessionId, session)
    if not session_data:
        raise HTTPException(
            status_code=404,
            detail="Session not found")
    if session_data.Sessions.status != Status.CREATED:
        raise HTTPException(status_code=400,
                            detail="Session already processed")


async def post_face_encodings(media: MediaUploadRequestModel):
    filename, content_type = (get_filename_and_content_type
                              (media.image.image_type))
    files_payload = [('file', (filename,
                               base64.b64decode(media.image.content),
                               content_type))]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(config.face_encoding_service_url,
                                         files=files_payload)
            validate_api_response(response)
            return response
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading images to external API")
