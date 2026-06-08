import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class FeedbackType(str, enum.Enum):
    confirm = "confirm"
    reject = "reject"


class EmailFeedback(Base):
    __tablename__ = "email_feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email_record_id: Mapped[str] = mapped_column(String, ForeignKey("email_records.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    feedback: Mapped[FeedbackType] = mapped_column(Enum(FeedbackType), nullable=False)
    original_score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    email_record: Mapped["EmailRecord"] = relationship(back_populates="feedback")
    user: Mapped["User"] = relationship(back_populates="feedback")

