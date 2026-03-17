from sqlalchemy.orm import Session

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

    return (
        value
        .lower()
        .replace("\r", "")
        .replace("\n", "")
        .replace("\t", "")
        .replace("  ", " ")
        .strip()
    )

def import_pr_from_excel(db: Session, rows, current_user, company_id, company_code):

    if not rows:
        raise ValueError("Excel sheet is empty")

    # ---------------- PRELOAD MATERIALS ----------------

    materials = {}

    for m in db.query(RawMaterial).filter(RawMaterial.company_id == company_id).all():
        materials[normalize(m.material_name)] = m

    # ---------------- PRELOAD FACTORIES ----------------

    factories = {
        f.name.strip(): f.id
        for f in db.query(Factory)
        .filter(Factory.company_id == company_id)
        .all()
    }

    # ---------------- PRELOAD DEPARTMENTS ----------------

    departments = {
        normalize(d.name): d
        for d in db.query(Department)
        .filter(Department.company_id == company_id)
        .all()
    }

    # ---------------- PRELOAD UNITS ----------------

    units = {}

    for u in db.query(Unit).filter(Unit.company_id == company_id).all():
        units[normalize(u.unit_code)] = u

    # ---------------- MAIN WAREHOUSE ----------------

    warehouse = (
        db.query(Warehouse)
        .filter(
            Warehouse.company_id == company_id,
            Warehouse.name == "Main Warehouse"
        )
        .first()
    )

    if not warehouse:
        raise ValueError("Main Warehouse not found")

    first = rows[0]

    # ---------------- FACTORY ----------------

    factory_name = (first.factory_name or "").strip()

    if factory_name not in factories:
        raise ValueError(f"Factory not found: {factory_name}")

    factory_id = factories[factory_name]

    # ---------------- CREATE PR ----------------

    pr_number = generate_pr_number(db, company_id)

    pr = PurchaseRequisition(
        company_id=company_id,
        company_code=company_code,
        pr_number=pr_number,
        pr_date=first.pr_date,
        requested_by=current_user.id,
        created_by=current_user.id,   # THIS MUST EXIST
        department=first.department,
        factory_id=factory_id,
        warehouse_id=warehouse.id,
        priority="NORMAL",
        status="DRAFT",
        remarks=first.remarks
    )

    db.add(pr)
    db.flush()

    # ---------------- PROCESS ITEMS ----------------
    # print("Materials in DB:")
    # for k in materials.keys():
    #     print(k)

    for r in rows:

        print("------ ROW ------")
        print("Excel material:", r.material_name)
        print("Normalized:", normalize(r.material_name))
        print("Excel Unit:", getattr(r, "unit", None))

        material_name = normalize(r.material_name)

        material = materials.get(material_name)
        print("Material found:", material)

        

        # ---------- CREATE MATERIAL IF NOT FOUND ----------

        if not material:           

            print("Creating new material:", r.material_name)

            material_code = r.material_name.upper().replace(" ", "_")

            excel_unit = normalize(r.unit) if getattr(r, "unit", None) else ""

            unit = None

            # ---------------- USE EXISTING UNIT ----------------
            if excel_unit:
                unit = units.get(excel_unit)

            # ---------------- CREATE UNIT IF NOT FOUND ----------------
            if excel_unit and not unit:

                print("Creating new unit:", excel_unit)

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

                # add to cache so next rows reuse it
                units[excel_unit] = unit

            # ---------------- FALLBACK TO PCS ----------------
            if not unit:
                unit = units.get("pcs")

            if not unit:
                raise ValueError("Default unit PCS not found in Unit master")            
            new_material = RawMaterial(
                company_id=company_id,
                material_code=material_code,
                material_name=r.material_name,
                category_id=DEFAULT_CATEGORY_ID,
                group_id=DEFAULT_GROUP_ID,
                unit_id=unit.id
            )

            db.add(new_material)
            db.flush()
            print("Created material ID:", new_material.id)

            material = new_material

            # add to cache
            materials[material_name] = material
            print("Material cache updated:", material_name)

        # ---------------- DEPARTMENT ----------------

        dept = departments.get(normalize(r.department))

        if not dept:
            raise ValueError(f"Department not found: {r.department}")

        # ---------------- CREATE PR ITEM ----------------

        db.add(
            PurchaseRequisitionItem(
                pr_id=pr.id,
                pr_number=pr_number,

                material_id=material.id,
                material_code=material.material_code,
                material_name=material.material_name,

                requested_qty=r.qty,
                unit_id=material.unit_id,

                department_id=dept.id,
                department_name=dept.name,

                description=getattr(r, "description", None),
                remarks=r.remarks,

                required_by_date=r.required_by_date,

                status="PENDING"
            )
        )

    db.commit()

    return pr