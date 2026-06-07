from typing import Generic, TypeVar, Type
from sqlalchemy.orm import Session
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> list[ModelType]:
        return self.db.query(self.model).all()

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, obj: ModelType) -> ModelType:
        self.db.refresh(obj)
        return obj
