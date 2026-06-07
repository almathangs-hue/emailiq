from datetime import datetime
from pydantic import BaseModel
from app.models.feedback import FeedbackType


class FeedbackCreate(BaseModel):
    feedback: FeedbackType


class FeedbackResponse(BaseModel):
    id: str
    email_record_id: str
    feedback: FeedbackType
    original_score: int
    created_at: datetime

    model_config = {"from_attributes": True}
