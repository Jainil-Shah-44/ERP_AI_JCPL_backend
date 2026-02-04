from typing import Generic, Type, TypeVar, List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.base import MasterBase

ModelType = TypeVar("ModelType", bound=MasterBase)

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        model: SQLAlchemy model class
        """
        self.model = model

    # -------------------------------
    # CREATE
    # -------------------------------
    def create(
        self,
        db: Session,
        *,
        obj_in: Dict[str, Any],
        company_id: UUID,
    ) -> ModelType:
        try:
            db_obj = self.model(**obj_in, company_id=company_id)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise e

    # -------------------------------
    # GET BY ID
    # -------------------------------
    def get(
        self,
        db: Session,
        *,
        id: UUID,
        company_id: UUID,
    ) -> Optional[ModelType]:
        return (
            db.query(self.model)
            .filter(
                self.model.id == id,
                self.model.company_id == company_id,
                self.model.is_active == True,
            )
            .first()
        )

    # -------------------------------
    # LIST (with filters)
    # -------------------------------
    def list(
        self,
        db: Session,
        *,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        query = (
            db.query(self.model)
            .filter(
                self.model.company_id == company_id,
                self.model.is_active == True,
            )
        )

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)

        return query.offset(skip).limit(limit).all()

    # -------------------------------
    # UPDATE
    # -------------------------------
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Dict[str, Any],
    ) -> ModelType:
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # -------------------------------
    # SOFT DELETE
    # -------------------------------
    def remove(
        self,
        db: Session,
        *,
        id: UUID,
        company_id: UUID,
    ) -> Optional[ModelType]:
        obj = (
            db.query(self.model)
            .filter(
                self.model.id == id,
                self.model.company_id == company_id,
                self.model.is_active == True,
            )
            .first()
        )

        if not obj:
            return None

        obj.is_active = False
        db.add(obj)
        db.commit()
        return obj
