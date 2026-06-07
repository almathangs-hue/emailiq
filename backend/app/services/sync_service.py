from datetime import datetime, date
from loguru import logger
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.email_record import EmailRecord
from app.repositories.account import AccountRepository
from app.repositories.email_record import EmailRecordRepository
from app.repositories.application import ApplicationRepository
from app.services.gmail_service import fetch_messages
from app.services.detection_service import score_email
from app.core.exceptions import ExternalServiceError


class SyncService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)
        self.email_repo = EmailRecordRepository(db)
        self.application_repo = ApplicationRepository(db)

    def sync_account(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ) -> dict:
        account = self.account_repo.get_by_user(user_id)
        if not account:
            raise ExternalServiceError("No connected Gmail account found.")

        logger.info("Starting sync", user_id=user_id, start=str(start_date), end=str(end_date))

        new_emails = 0
        new_applications = 0
        skipped = 0

        classified_thread_ids = self.email_repo.get_classified_thread_ids(account.id)

        try:
            for msg in fetch_messages(account, self.db, start_date, end_date):
                if self.email_repo.get_by_gmail_id(msg["gmail_message_id"]):
                    skipped += 1
                    continue

                result = score_email(
                    sender_email=msg["sender_email"],
                    subject=msg["subject"],
                    body_snippet=msg["body_snippet"],
                    existing_thread_classified=msg["gmail_thread_id"] in classified_thread_ids,
                )

                record = EmailRecord(
                    account_id=account.id,
                    gmail_message_id=msg["gmail_message_id"],
                    gmail_thread_id=msg["gmail_thread_id"],
                    sender_email=msg["sender_email"],
                    sender_name=msg["sender_name"],
                    subject=msg["subject"],
                    body_snippet=msg["body_snippet"],
                    received_at=msg["received_at"],
                    confidence_score=result.score,
                    is_classified=result.is_job,
                )
                self.email_repo.create(record)
                new_emails += 1

                if result.is_job:
                    classified_thread_ids.add(msg["gmail_thread_id"])
                    application = Application(
                        email_record_id=record.id,
                        account_id=account.id,
                        company_name=result.company_name,
                        role_title=result.role_title,
                        status=ApplicationStatus(result.inferred_status),
                        applied_at=msg["received_at"],
                        last_activity_at=msg["received_at"],
                    )
                    self.application_repo.create(application)
                    new_applications += 1

        except Exception as exc:
            logger.error("Sync failed", user_id=user_id, error=str(exc))
            raise ExternalServiceError(f"Gmail sync failed: {exc}") from exc

        account.last_synced_at = datetime.utcnow()
        self.db.commit()

        logger.info(
            "Sync complete",
            user_id=user_id,
            new_emails=new_emails,
            new_applications=new_applications,
            skipped=skipped,
        )

        return {
            "new_emails_scanned": new_emails,
            "new_applications_found": new_applications,
            "skipped_duplicates": skipped,
        }
