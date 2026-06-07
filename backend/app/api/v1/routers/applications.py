from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.application import ApplicationStatus
from app.models.feedback import FeedbackType, EmailFeedback
from app.repositories.application import ApplicationRepository
from app.schemas.application import ApplicationResponse, ApplicationUpdate, PaginatedApplications
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/applications", tags=["applications"])


def _to_response(app) -> ApplicationResponse:
    return ApplicationResponse(
        id=app.id,
        company_name=app.company_name,
        role_title=app.role_title,
        status=app.status,
        status_overridden=app.status_overridden,
        applied_at=app.applied_at,
        last_activity_at=app.last_activity_at,
        notes=app.notes,
        confidence_score=app.email_record.confidence_score,
        sender_email=app.email_record.sender_email,
        subject=app.email_record.subject,
        created_at=app.created_at,
        updated_at=app.updated_at,
    )


@router.get("", response_model=PaginatedApplications)
def list_applications(
    status: ApplicationStatus | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    search: str | None = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    repo = ApplicationRepository(db)
    items, total, total_pages = repo.list_paginated(
        user_id=user_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedApplications(
        items=[_to_response(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    repo = ApplicationRepository(db)
    app = repo.get_by_id_and_user(application_id, user_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return _to_response(app)


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: str,
    body: ApplicationUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    repo = ApplicationRepository(db)
    app = repo.get_by_id_and_user(application_id, user_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if body.status is not None:
        app.status = body.status
        app.status_overridden = True
    if body.notes is not None:
        app.notes = body.notes
    if body.company_name is not None:
        app.company_name = body.company_name
    if body.role_title is not None:
        app.role_title = body.role_title

    db.commit()
    db.refresh(app)
    return _to_response(app)


@router.delete("/{application_id}", status_code=204)
def delete_application(
    application_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    repo = ApplicationRepository(db)
    app = repo.get_by_id_and_user(application_id, user_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    repo.delete(app)
    db.commit()


@router.post("/{application_id}/feedback", response_model=FeedbackResponse, status_code=201)
def submit_feedback(
    application_id: str,
    body: FeedbackCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    repo = ApplicationRepository(db)
    app = repo.get_by_id_and_user(application_id, user_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    feedback = EmailFeedback(
        email_record_id=app.email_record_id,
        user_id=user_id,
        feedback=body.feedback,
        original_score=app.email_record.confidence_score,
    )
    db.add(feedback)

    if body.feedback == FeedbackType.reject:
        repo.delete(app)

    db.commit()
    return feedback
