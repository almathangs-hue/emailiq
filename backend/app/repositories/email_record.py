from sqlalchemy.orm import Session
from app.models.email_record import EmailRecord
from app.repositories.base import BaseRepository


class EmailRecordRepository(BaseRepository[EmailRecord]):
    def __init__(self, db: Session):
        super().__init__(EmailRecord, db)

    def get_by_gmail_id(self, gmail_message_id: str) -> EmailRecord | None:
        return self.db.query(EmailRecord).filter(
            EmailRecord.gmail_message_id == gmail_message_id
        ).first()

    def get_classified_thread_ids(self, account_id: str) -> set[str]:
        rows = (
            self.db.query(EmailRecord.gmail_thread_id)
            .filter(
                EmailRecord.account_id == account_id,
                EmailRecord.is_classified == True,
            )
            .all()
        )
        return {row[0] for row in rows}
