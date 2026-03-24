from sqlalchemy.orm import Session
import re
from datetime import date, datetime

from app.models.raw_material import RawMaterial
from app.models.factory import Factory
from app.models.warehouse import Warehouse
from app.models.department import Department
from app.models.unit import Unit

from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.models.purchase.purchase_requisition import PurchaseRequisitionItem

from app.services.purchase.pr_number_service import generate_pr_number

# DEFAULT MASTER IDS
DEFAULT_CATEGORY_ID = "b82a8f13-4cb9-46fa-b0c4-b6a31a149d03"
DEFAULT_GROUP_ID = "775b552d-e55a-4990-9fc3-66d711bcddd8"


def normalize(value: str):
    if not value:
        return ""
    value = value.lower()
    value = re.sub(r"[^\w\s]", "", value)
    value = value.replace(" ", "")
    return value.strip()


def parse_date_safe(val):
    if not val:
        return date.today()

    if isinstance(val, date):
        return val

    if isinstance(val, str):
        val = val.strip()
        if not val:
            return date.today()

        try:
            return datetime.strptime(val, "%Y-%m-%d").date()
        except:
            return date.today()

    return date.today()


def import_pr_from_excel(db: Session, rows, current_user, company_id, company_code):

    errors = []
    valid_rows = []

    if not rows:
        return {"success": False, "errors": [{"row": 0, "message": "Excel sheet is empty"}]}

    # ---------------- PRELOAD ----------------

    materials = {
        normalize(m.material_name): m
        for m in db.query(RawMaterial).filter(RawMaterial.company_id == company_id).all()
    }

    factories = {
        f.name.strip(): f.id
        for f in db.query(Factory).filter(Factory.company_id == company_id).all()
    }

    departments_by_name = {}
    departments_list = []

    for d in db.query(Department).filter(Department.company_id == company_id).all():
        departments_by_name[normalize(d.name)] = d
        departments_list.append(d)

    units = {
        normalize(u.unit_code): u
        for u in db.query(Unit).filter(Unit.company_id == company_id).all()
    }

    warehouse = (
        db.query(Warehouse)
        .filter(Warehouse.company_id == company_id, Warehouse.name == "Main Warehouse")
        .first()
    )

    if not warehouse:
        return {"success": False, "errors": [{"row": 0, "message": "Main Warehouse not found"}]}

    # ---------------- DEPARTMENT RESOLVER ----------------

    def resolve_department(val):
        key = normalize(val)
        if not key:
            return None

        if key in departments_by_name:
            return departments_by_name[key]

        short = key[:3]

        for d in departments_list:
            if normalize(d.name).startswith(short):
                return d

        return None

    # ---------------- MAIN LOOP ----------------

    for index, r in enumerate(rows, start=1):
        try:
            # -------- FACTORY --------
            factory_name = (r.get("factory_name") or "").strip()

            if not factory_name:
                raise ValueError("Factory is empty")

            if factory_name not in factories:
                raise ValueError(f"Factory not found: {factory_name}")

            factory_id = factories[factory_name]

            # # -------- DATE VALIDATION --------
            # if r.get("pr_date"):
            #     try:
            #         datetime.strptime(r["pr_date"], "%Y-%m-%d")
            #     except:
            #         raise ValueError(f"Invalid pr_date: {r['pr_date']}")

            # if r.get("required_by_date"):
            #     try:
            #         datetime.strptime(r["required_by_date"], "%Y-%m-%d")
            #     except:
            #         raise ValueError(f"Invalid required_by_date: {r['required_by_date']}")

            # -------- MATERIAL --------
            material_name = normalize(r.get("material_name"))

            material = materials.get(material_name)

            if not material:
                material_code = r.get("material_name", "").upper().replace(" ", "_")

                excel_unit = normalize(r.get("unit"))

                unit = units.get(excel_unit)

                if excel_unit and not unit:
                    new_unit = Unit(
                        company_id=company_id,
                        unit_code=excel_unit.upper(),
                        description=excel_unit.upper(),
                        base_unit_id=None,
                        conversion_factor=1
                    )
                    db.add(new_unit)
                    db.flush()
                    unit = new_unit
                    units[excel_unit] = unit

                if not unit:
                    unit = units.get("pcs")

                if not unit:
                    raise ValueError("Default unit PCS not found")

                new_material = RawMaterial(
                    company_id=company_id,
                    material_code=material_code,
                    material_name=r.get("material_name"),
                    category_id=DEFAULT_CATEGORY_ID,
                    group_id=DEFAULT_GROUP_ID,
                    unit_id=unit.id
                )

                db.add(new_material)
                db.flush()

                material = new_material
                materials[material_name] = material

            # -------- DEPARTMENT --------
            dept = resolve_department(r.get("department"))

            if not dept:
                raise ValueError(f"Department not found: {r.get('department')}")

            valid_rows.append({
                "row": index,
                "data": r,
                "material": material,
                "dept": dept,
                "factory_id": factory_id
            })

        except Exception as e:
            errors.append({
                "row": index,
                "message": str(e)
            })

    # ---------------- STRICT VALIDATION ----------------

    if errors:
        return {
            "success": False,
            "errors": errors
        }

    # ---------------- CREATE PR ----------------

    first = valid_rows[0]["data"]

    pr_number = generate_pr_number(db, company_id)

    pr = PurchaseRequisition(
        company_id=company_id,
        company_code=company_code,
        pr_number=pr_number,
        pr_date=parse_date_safe(first.get("pr_date")),
        requested_by=current_user.id,
        created_by=current_user.id,
        department=first.get("department"),
        factory_id=valid_rows[0]["factory_id"],
        warehouse_id=warehouse.id,
        priority="NORMAL",
        status="DRAFT",
        remarks=first.get("remarks")
    )

    db.add(pr)
    db.flush()

    # ---------------- CREATE ITEMS ----------------

    for item in valid_rows:
        r = item["data"]

        db.add(
            PurchaseRequisitionItem(
                pr_id=pr.id,
                pr_number=pr_number,
                line_number=item["row"],

                material_id=item["material"].id,
                material_code=item["material"].material_code,
                material_name=item["material"].material_name,

                requested_qty=r.get("qty"),
                unit_id=item["material"].unit_id,

                department_id=item["dept"].id,
                department_name=item["dept"].name,

                description=r.get("description"),
                remarks=r.get("remarks"),

                required_by_date=parse_date_safe(r.get("required_by_date")),
                status="PENDING"
            )
        )

    db.commit()

    return {
        "success": True,
        "pr_id": pr.id,
        "pr_number": pr_number,
        "errors": errors
    }