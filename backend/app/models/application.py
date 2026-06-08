import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class ApplicationStatus(str, enum.Enum):
    applied = "applied"
    screening = "screening"
    interview = "interview"
    offer = "offer"
    rejected = "rejected"
    withdrawn = "withdrawn"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email_record_id: Mapped[str] = mapped_column(String, ForeignKey("email_records.id"), unique=True, nullable=False)
    account_id: Mapped[str] = mapped_column(String, ForeignKey("connected_accounts.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    role_title: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.applied, nullable=False
    )
    status_overridden: Mapped[bool] = mapped_column(Boolean, default=False)
    applied_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    email_record: Mapped["EmailRecord"] = relationship(back_populates="application")

