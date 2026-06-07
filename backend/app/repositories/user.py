from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def upsert(self, email: str, name: str, picture: str | None) -> User:
        user = self.get_by_email(email)
        if not user:
            user = User(email=email, name=name, picture=picture)
            self.db.add(user)
            self.db.flush()
        else:
            user.name = name
            user.picture = picture
        return user
