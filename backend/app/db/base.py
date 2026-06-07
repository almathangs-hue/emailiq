from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models here so Alembic can detect them for autogenerate
from app.models.user import User              # noqa: F401, E402
from app.models.account import ConnectedAccount  # noqa: F401, E402
from app.models.email_record import EmailRecord  # noqa: F401, E402
from app.models.application import Application   # noqa: F401, E402
from app.models.feedback import EmailFeedback    # noqa: F401, E402
