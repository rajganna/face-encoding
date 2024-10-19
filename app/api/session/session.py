from fastapi import APIRouter, status, Path, HTTPException, Depends
from sqlmodel import Session

from app.api.session.dao import (create_db_session,
                                 get_db_session,
                                 save_session_encoding,
                                 get_session_encoding)
from app.api.session.dto import (RequestModel,
                                 MediaUploadRequestModel,
                                 UploadSelfieResponseModel)
from app.api.session.models import get_session
from app.lib.session_api_helper import verify_session_id, \
    post_face_encodings

router = APIRouter()


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(request: RequestModel,
                         session: Session = Depends(get_session)):
    session_data = get_db_session(
        str(request.verification.vendorData),
        session)
    if session_data:
        raise HTTPException(
            status_code=400,
            detail="Session with this sessionId already exists.")
    create_db_session(request, session)
    return {
        "status": "Session created successfully",
        "verification": request.verification.dict()
    }


@router.post("/sessions/{sessionId}/media",
             status_code=status.HTTP_201_CREATED)
async def upload_media(
        media: MediaUploadRequestModel,
        sessionId: str = Path(
            ...,
            description="Unique identifier for the session"),
        session: Session = Depends(get_session)
):
    verify_session_id(sessionId, session)
    response = await post_face_encodings(media)
    save_session_encoding(sessionId, response.json(), session)
    upload_response = UploadSelfieResponseModel(
        sessionId=sessionId,
        status="Success",
        verification=response.json()
    )
    return upload_response


@router.get("/sessions/{session_id}/decision")
async def get_decision(session_id: str,
                       session: Session = Depends(get_session)):
    session_encodings = get_session_encoding(session_id, session)
    if not session_encodings:
        raise HTTPException(status_code=404, detail="Encodings not found")
    response = UploadSelfieResponseModel(
        sessionId=session_id,
        status="Verified",
        verification=session_encodings.Encodings.encodings
    )
    return response
