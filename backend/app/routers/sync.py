from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.database import get_db
from app.models import ConnectedAccount
from app.schemas import SyncRequest, SyncResponse
from app.services.sync_service import sync_account

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("", response_model=SyncResponse, status_code=200)
def manual_sync(
    body: SyncRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    account = db.query(ConnectedAccount).filter(
        ConnectedAccount.user_id == user_id
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="No connected Gmail account found. Please sign in with Google first.",
        )

    result = sync_account(account, db, body.start_date, body.end_date)
    return SyncResponse(**result)
