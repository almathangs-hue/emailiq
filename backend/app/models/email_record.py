import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class EmailRecord(Base):
    __tablename__ = "email_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id: Mapped[str] = mapped_column(String, ForeignKey("connected_accounts.id"), nullable=False)
    gmail_message_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    gmail_thread_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    sender_email: Mapped[str] = mapped_column(String, nullable=False)
    sender_name: Mapped[str | None] = mapped_column(String, nullable=True)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    body_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    confidence_score: Mapped[int] = mapped_column(Integer, default=0)
    is_classified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    account: Mapped["ConnectedAccount"] = relationship(back_populates="email_records")
    application: Mapped["Application | None"] = relationship(back_populates="email_record", uselist=False)
    feedback: Mapped[list["EmailFeedback"]] = relationship(back_populates="email_record", cascade="all, delete-orphan")

