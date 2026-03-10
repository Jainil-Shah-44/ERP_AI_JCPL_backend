import pandas as pd
import uuid
import re

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.raw_material import RawMaterial
from app.models.unit import Unit

FILE_PATH = "Material_List.xlsx"
COMPANY_ID = "9cefd77f-0fa5-40f9-8183-3c550267aa2c"


# ---------------------------------------
# CLEAN VALUE
# ---------------------------------------
def clean(value):

    if pd.isna(value):
        return None

    value = str(value)

    value = re.sub(r"_x[0-9A-Fa-f]{4}_", "", value)
    value = re.sub(r"[\x00-\x1F\x7F]", "", value)

    return value.strip()


# ---------------------------------------
# GENERATE MATERIAL CODE
# ---------------------------------------
# def generate_code(name):

    code = re.sub(r"[^A-Za-z0-9]+", "_", name)
    return code.upper().strip("_")


# ---------------------------------------
# IMPORT
# ---------------------------------------
def import_items():

    db: Session = SessionLocal()

    df = pd.read_excel(FILE_PATH)

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():

        name = clean(row.get("NAME OF MATERIAL"))
        unit_name = clean(row.get("UOM"))
        if not unit_name:
            print("Unit missing in Excel row")
            skipped += 1
            continue

        if not name:
            skipped += 1
            continue

        base_code = re.sub(r'[^A-Za-z0-9]+', '_', name).upper().strip('_')
        material_code = base_code[:45] + "_" + str(uuid.uuid4())[:4]


        # FIND UNIT
        unit = db.query(Unit).filter(
            Unit.company_id == COMPANY_ID,
            Unit.unit_code.ilike(f"{unit_name}")
        ).first()

        if not unit:
            unit = Unit(
                id=uuid.uuid4(),
                company_id=COMPANY_ID,
                unit_code=unit_name[:50],
                description=unit_name,
                conversion_factor=1,
                is_active=True
            )

            db.add(unit)
            db.flush()

            print(f"Created new unit: {unit_name}")

        # DUPLICATE CHECK
        existing = db.query(RawMaterial).filter(
            RawMaterial.company_id == COMPANY_ID,
            RawMaterial.material_code == material_code
        ).first()

        if existing:
            skipped += 1
            continue

        material = RawMaterial(
            id=uuid.uuid4(),
            company_id=COMPANY_ID,
            material_code=material_code,
            material_name=name,
            unit_id=unit.id,
            is_active=True
        )

        db.add(material)
        db.flush()

        inserted += 1

    db.commit()
    db.close()

    print("---------------")
    print("Inserted:", inserted)
    print("Skipped:", skipped)
    print("---------------")


if __name__ == "__main__":
    import_items()