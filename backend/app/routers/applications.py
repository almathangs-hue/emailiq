import math
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.auth import get_current_user_id
from app.database import get_db
from app.models import Application, EmailRecord, ConnectedAccount, EmailFeedback
from app.models.application import ApplicationStatus
from app.models.feedback import FeedbackType
from app.schemas import (
    ApplicationResponse,
    ApplicationUpdate,
    PaginatedApplications,
    FeedbackCreate,
    FeedbackResponse,
)

router = APIRouter(prefix="/applications", tags=["applications"])


def _get_application_or_404(
    application_id: str, user_id: str, db: Session
) -> Application:
    """Fetch application belonging to the current user or raise 404."""
    app = (
        db.query(Application)
        .join(ConnectedAccount, Application.account_id == ConnectedAccount.id)
        .join(EmailRecord, Application.email_record_id == EmailRecord.id)
        .filter(
            Application.id == application_id,
            ConnectedAccount.user_id == user_id,
        )
        .options(joinedload(Application.email_record))
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


def _to_response(app: Application) -> ApplicationResponse:
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
    query = (
        db.query(Application)
        .join(ConnectedAccount, Application.account_id == ConnectedAccount.id)
        .join(EmailRecord, Application.email_record_id == EmailRecord.id)
        .filter(ConnectedAccount.user_id == user_id)
        .options(joinedload(Application.email_record))
    )

    if status:
        query = query.filter(Application.status == status)
    if start_date:
        query = query.filter(Application.applied_at >= start_date)
    if end_date:
        query = query.filter(Application.applied_at <= end_date)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Application.company_name.ilike(search_term)
            | Application.role_title.ilike(search_term)
        )

    total = query.count()
    items = (
        query.order_by(Application.applied_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedApplications(
        items=[_to_response(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return _to_response(_get_application_or_404(application_id, user_id, db))


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: str,
    body: ApplicationUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    app = _get_application_or_404(application_id, user_id, db)

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
    app = _get_application_or_404(application_id, user_id, db)
    db.delete(app)
    db.commit()


@router.post("/{application_id}/feedback", response_model=FeedbackResponse, status_code=201)
def submit_feedback(
    application_id: str,
    body: FeedbackCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    app = _get_application_or_404(application_id, user_id, db)

    feedback = EmailFeedback(
        email_record_id=app.email_record_id,
        user_id=user_id,
        feedback=body.feedback,
        original_score=app.email_record.confidence_score,
    )
    db.add(feedback)

    # Reject feedback removes the application from the tracker
    if body.feedback == FeedbackType.reject:
        db.delete(app)

    db.commit()
    return feedback
