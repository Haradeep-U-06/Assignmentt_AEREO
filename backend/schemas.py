from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

class RecipientCreate(BaseModel):
    recipient_name: str
    email: EmailStr
    course_name: str

class JobCreate(BaseModel):
    recipients: List[RecipientCreate]

class CertificateResponse(BaseModel):
    id: int
    recipient_name: str
    email: str
    course_name: str
    status: str
    error_message: Optional[str] = None
    file_path: Optional[str] = None

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: int
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    certificates: List[CertificateResponse]

    class Config:
        from_attributes = True

class JobStatusResponse(BaseModel):
    id: int
    status: str
    total_certificates: int
    generated: int
    failed: int
    pending: int
