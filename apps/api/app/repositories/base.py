from typing import TypeVar, Generic, Type, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model_cls: Type[T]):
        self.model_cls = model_cls

    def get_by_id(self, db: Session, id: Any) -> Optional[T]:
        return db.query(self.model_cls).filter(self.model_cls.id == id).first()

    def create(self, db: Session, obj_in: dict) -> T:
        obj = self.model_cls(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, db_obj: T, obj_in: dict) -> T:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> bool:
        obj = self.get_by_id(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
