import base64
import re
from enum import Enum
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, AnyUrl, Field, constr, field_validator


class Status(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"


class DocumentType(str, Enum):
    PASSPORT = "PASSPORT"
    ID_CARD = "ID_CARD"
    RESIDENCE_PERMIT = "RESIDENCE_PERMIT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    VISA = "VISA"
    SELFIE = "SELFIE"


class DocumentModel(BaseModel):
    number: constr(strict=True, min_length=1) = (
        Field(...,
              description="Document number, "
                          "[a-zA-Z0-9] characters "
                          "only"))
    country: constr(strict=True, min_length=2, max_length=2) = (
        Field(...,
              description="ISO-2 string of the issuing country"))
    type: DocumentType = Field(...,
                               description="Type of document "
                                           "(SELFIE, PASSPORT, "
                                           "ID_CARD, "
                                           "RESIDENCE_PERMIT, "
                                           "DRIVERS_LICENSE, "
                                           "VISA)")

    @field_validator('number')
    def validate_number(cls, v):
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError('Document number must contain '
                             'only [a-zA-Z0-9] characters')
        return v


class VerificationModel(BaseModel):
    callback: AnyUrl = Field(
        ...,
        description="Callback URL for the verification process")
    vendorData: UUID = Field(
        ...,
        description="Vendor-specific UUID data")
    document: Optional[DocumentModel] = Field(
        None,
        description="Document of a person to be verified")


class RequestModel(BaseModel):
    verification: VerificationModel


class ImageModel(BaseModel):
    context: str = Field(
        ...,
        description="Context of the image "
                    "(e.g., document-front, document-back)")
    content: str = Field(
        ...,
        description="Base64 encoded image data")
    image_type: str = Field(
        ...,
        description="Image type (e.g., jpeg, png, gif, bmp)")

    @field_validator('image_type')
    def validate_image_type(cls, v):
        allowed_types = {'jpeg', 'png', 'gif', 'bmp'}
        if v.lower() not in allowed_types:
            raise ValueError(f'Invalid image type: {v}. Must be one of {allowed_types}')
        return v

    @field_validator('content')
    def validate_base64(cls, v):
        try:
            base64.b64decode(v, validate=True)
        except Exception:
            raise ValueError("Invalid base64 encoded image data")
        return v


class MediaUploadRequestModel(BaseModel):
    image: ImageModel = Field(
        ...,
        description="List of image (up to 5 faces) "
                    "related to the verification process")


class UploadSelfieResponseModel(BaseModel):
    sessionId: str
    status: str
    verification: List[List[float]]


class ValidationErrorDetail(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponseModel(BaseModel):
    detail: List[ValidationErrorDetail]
