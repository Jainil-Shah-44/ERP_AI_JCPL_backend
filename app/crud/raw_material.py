from sqlalchemy.orm import Session
from uuid import UUID

from app.crud.base import CRUDBase
from app.models.raw_material import RawMaterial
from app.models.unit import Unit


class CRUDRawMaterial(CRUDBase[RawMaterial]):

    def create(self, db: Session, *, obj_in, company_id: UUID):

        unit = db.query(Unit).filter(Unit.id == obj_in["unit_id"]).first()

        if unit:
            obj_in["unit_name"] = unit.unit_code

        return super().create(db=db, obj_in=obj_in, company_id=company_id)

    def update(self, db: Session, *, db_obj, obj_in):

        if "unit_id" in obj_in:
            unit = db.query(Unit).filter(Unit.id == obj_in["unit_id"]).first()
            if unit:
                obj_in["unit_name"] = unit.unit_code

        return super().update(db=db, db_obj=db_obj, obj_in=obj_in)

crud = CRUDRawMaterial(RawMaterial)