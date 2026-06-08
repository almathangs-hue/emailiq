import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="accounts")
    email_records: Mapped[list["EmailRecord"]] = relationship(back_populates="account", cascade="all, delete-orphan")

