from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.db.session import get_db
from app.schemas.sync import SyncRequest, SyncResponse
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("", response_model=SyncResponse)
def manual_sync(
    body: SyncRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = SyncService(db)
    result = service.sync_account(user_id, body.start_date, body.end_date)
    return SyncResponse(**result)
