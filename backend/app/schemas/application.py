from datetime import datetime
from pydantic import BaseModel, Field
from app.models.application import ApplicationStatus


class ApplicationResponse(BaseModel):
    id: str
    company_name: str
    role_title: str | None
    status: ApplicationStatus
    status_overridden: bool
    applied_at: datetime
    last_activity_at: datetime
    notes: str | None
    confidence_score: int
    sender_email: str
    subject: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    notes: str | None = None
    company_name: str | None = None
    role_title: str | None = None


class PaginatedApplications(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
