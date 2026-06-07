from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models import ConnectedAccount, EmailRecord, Application, ApplicationStatus
from app.services.gmail_service import fetch_messages
from app.services.detection_service import score_email


def sync_account(account: ConnectedAccount, db: Session, start_date: date, end_date: date) -> dict:
    """
    Scan Gmail for job emails in [start_date, end_date].
    Creates EmailRecords for all fetched emails and Applications for classified ones.
    Returns a summary of what was processed.
    """
    new_emails = 0
    new_applications = 0
    skipped = 0

    # Track thread IDs that already have a classified application (for thread scoring bonus)
    classified_thread_ids: set[str] = set(
        row[0] for row in db.query(EmailRecord.gmail_thread_id)
        .filter(EmailRecord.is_classified == True, EmailRecord.account_id == account.id)
        .all()
    )

    for msg in fetch_messages(account, db, start_date, end_date):
        # Skip already-imported messages
        exists = db.query(EmailRecord).filter(
            EmailRecord.gmail_message_id == msg["gmail_message_id"]
        ).first()
        if exists:
            skipped += 1
            continue

        thread_classified = msg["gmail_thread_id"] in classified_thread_ids

        result = score_email(
            sender_email=msg["sender_email"],
            subject=msg["subject"],
            body_snippet=msg["body_snippet"],
            existing_thread_classified=thread_classified,
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
        db.add(record)
        db.flush()
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
            db.add(application)
            new_applications += 1

    account.last_synced_at = datetime.utcnow()
    db.commit()

    return {
        "new_emails_scanned": new_emails,
        "new_applications_found": new_applications,
        "skipped_duplicates": skipped,
    }
