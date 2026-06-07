from datetime import date
from pydantic import BaseModel, model_validator
from datetime import date, timedelta


class SyncRequest(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def set_defaults_and_validate(self):
        today = date.today()
        if self.start_date is None:
            self.start_date = today - timedelta(days=90)
        if self.end_date is None:
            self.end_date = today
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class SyncResponse(BaseModel):
    new_emails_scanned: int
    new_applications_found: int
    skipped_duplicates: int
