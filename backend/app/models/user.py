import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    picture: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    accounts: Mapped[list["ConnectedAccount"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    feedback: Mapped[list["EmailFeedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")

