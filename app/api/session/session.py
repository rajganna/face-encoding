from fastapi import APIRouter, status, Path, HTTPException, Depends
from sqlmodel import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.session.dao import (create_db_session,
                                 get_db_session,
                                 save_session_encoding,
                                 get_session_encoding)
from app.api.session.dto import (RequestModel,
                                 MediaUploadRequestModel,
                                 UploadSelfieResponseModel)
from app.api.session.models import get_session
from app.lib.session_api_helper import verify_session_id, \
    post_face_encodings, session_exists

router = APIRouter()


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(request: RequestModel,
                         session: AsyncSession = Depends(get_session)):
    if await session_exists(request, session):
        raise HTTPException(status_code=400, detail="Session with this sessionId already exists.")
    await create_db_session(request, session)
    return {
        "status": "Session created successfully",
        "verification": request.verification.dict()
    }


@router.post("/sessions/{sessionId}/media", status_code=status.HTTP_201_CREATED)
async def upload_media(
        media: MediaUploadRequestModel,
        sessionId: str = Path(..., description="Unique identifier for the session"),
        session: AsyncSession = Depends(get_session)
):
    await verify_session_id(sessionId, session)
    response = await post_face_encodings(media)
    await save_session_encoding(sessionId, response.json(), session)
    return UploadSelfieResponseModel(sessionId=sessionId, status="Success", verification=response.json())


@router.get("/sessions/{session_id}/summary")
async def get_summary(session_id: str,
                      session: AsyncSession = Depends(get_session)):
    session_encodings = await get_session_encoding(session_id, session)
    if not session_encodings:
        raise HTTPException(status_code=404, detail="Encodings not found")
    return UploadSelfieResponseModel(sessionId=session_id, status="Verified", verification=session_encodings.encodings)
