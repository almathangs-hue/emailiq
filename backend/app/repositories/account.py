from sqlalchemy.orm import Session
from app.models.account import ConnectedAccount
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[ConnectedAccount]):
    def __init__(self, db: Session):
        super().__init__(ConnectedAccount, db)

    def get_by_user(self, user_id: str) -> ConnectedAccount | None:
        return self.db.query(ConnectedAccount).filter(
            ConnectedAccount.user_id == user_id
        ).first()

    def get_by_user_and_email(self, user_id: str, email: str) -> ConnectedAccount | None:
        return self.db.query(ConnectedAccount).filter(
            ConnectedAccount.user_id == user_id,
            ConnectedAccount.email == email,
        ).first()

    def upsert(
        self,
        user_id: str,
        email: str,
        access_token: str,
        refresh_token: str,
    ) -> ConnectedAccount:
        account = self.get_by_user_and_email(user_id, email)
        if not account:
            account = ConnectedAccount(
                user_id=user_id,
                email=email,
                access_token=access_token,
                refresh_token=refresh_token,
            )
            self.db.add(account)
            self.db.flush()
        else:
            account.access_token = access_token
            if refresh_token:
                account.refresh_token = refresh_token
        return account
