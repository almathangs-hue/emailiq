import math
from datetime import date
from sqlalchemy.orm import Session, joinedload
from app.models.application import Application, ApplicationStatus
from app.models.account import ConnectedAccount
from app.models.email_record import EmailRecord
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, db: Session):
        super().__init__(Application, db)

    def _base_query(self, user_id: str):
        return (
            self.db.query(Application)
            .join(ConnectedAccount, Application.account_id == ConnectedAccount.id)
            .join(EmailRecord, Application.email_record_id == EmailRecord.id)
            .filter(ConnectedAccount.user_id == user_id)
            .options(joinedload(Application.email_record))
        )

    def get_by_id_and_user(self, application_id: str, user_id: str) -> Application | None:
        return self._base_query(user_id).filter(Application.id == application_id).first()

    def list_paginated(
        self,
        user_id: str,
        status: ApplicationStatus | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Application], int, int]:
        query = self._base_query(user_id)

        if status:
            query = query.filter(Application.status == status)
        if start_date:
            query = query.filter(Application.applied_at >= start_date)
        if end_date:
            query = query.filter(Application.applied_at <= end_date)
        if search:
            term = f"%{search}%"
            query = query.filter(
                Application.company_name.ilike(term) | Application.role_title.ilike(term)
            )

        total = query.count()
        items = (
            query.order_by(Application.applied_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        total_pages = math.ceil(total / page_size) if total else 0
        return items, total, total_pages
