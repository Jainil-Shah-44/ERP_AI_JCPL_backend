import pandas as pd
import uuid
import re
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.raw_material import RawMaterial
from app.models.group import ItemGroup
from app.models.category import ItemCategory
from app.models.unit import Unit

FILE_PATH = "Item_Master.xls"
COMPANY_ID = "9cefd77f-0fa5-40f9-8183-3c550267aa2c"


# ---------------------------------------------------
# CLEAN VALUE (remove tally xml garbage)
# ---------------------------------------------------
def clean(value):

    if pd.isna(value):
        return None

    value = str(value)

    # remove xml escape sequences like _x0004_
    value = re.sub(r"_x[0-9A-Fa-f]{4}_", "", value)

    # remove control characters
    value = re.sub(r"[\x00-\x1F\x7F]", "", value)

    return value.strip()


# ---------------------------------------------------
# SAFE NUMBER
# ---------------------------------------------------
def safe_number(value):

    if pd.isna(value):
        return None

    try:
        return float(value)
    except:
        return None


# ---------------------------------------------------
# IMPORT FUNCTION
# ---------------------------------------------------
def import_items():

    db: Session = SessionLocal()

    df = pd.read_excel(FILE_PATH)

    print("Groups detected:", df["$Parent"].apply(clean).unique())
    print("Categories detected:", df["$Category"].apply(clean).unique())
    print("Units detected:", df["$BaseUnits"].apply(clean).unique())

    inserted = 0
    skipped = 0
    seen_codes = set()

    for _, row in df.iterrows():

        name = clean(row.get("$Name"))
        parent = clean(row.get("$Parent"))
        category = clean(row.get("$Category"))
        unit_name = clean(row.get("$BaseUnits"))

        description = clean(row.get("$Description"))
        hsn_code = clean(row.get("$_HSNCode"))

        gst_rate = safe_number(row.get("tempGSTTaxRate"))
        reorder_level = safe_number(row.get("ReorderBase"))
        min_order_qty = safe_number(row.get("MinimumOrderBase"))

        if not name:
            skipped += 1
            continue

        # normalize values
        if parent:
            parent = parent.strip()

        if category:
            category = category.strip()

        if unit_name:
            unit_name = unit_name.upper()

        # ---------------------------------------------------
        # RULE 1: Parent Primary → primary
        # ---------------------------------------------------
        if parent and parent.lower() == "primary":
            parent = "primary"

        # ---------------------------------------------------
        # RULE 2: Category Not Applicable → Parent
        # ---------------------------------------------------
        if category and category.lower() == "not applicable":
            category = parent
        if category:
            category = category.strip()

        # ---------------------------------------------------
        # FIND GROUP
        # ---------------------------------------------------
        group = db.query(ItemGroup).filter(
            ItemGroup.name.ilike(parent),
            ItemGroup.company_id == COMPANY_ID
        ).first()

        if not group:
            print(f"Group missing: {parent}")
            skipped += 1
            continue

        # ---------------------------------------------------
        # FIND CATEGORY
        # ---------------------------------------------------
        category_obj = db.query(ItemCategory).filter(
            ItemCategory.name.ilike(category),
            ItemCategory.company_id == COMPANY_ID
        ).first()

        if not category_obj:
            print(f"Category missing: {category}")
            skipped += 1
            continue

        # ---------------------------------------------------
        # FIND UNIT
        # ---------------------------------------------------
        unit = db.query(Unit).filter(
            Unit.unit_code.ilike(unit_name),
            Unit.company_id == COMPANY_ID
        ).first()

        if not unit:
            print(f"Unit missing: {unit_name}")
            skipped += 1
            continue

        # ---------------------------------------------------
        # CREATE MATERIAL CODE
        # ---------------------------------------------------
        material_code = re.sub(r'[^A-Za-z0-9]+', '_', name).upper().strip('_')

        if material_code in seen_codes:
            skipped += 1
            continue

        seen_codes.add(material_code)
        # ---------------------------------------------------
        # DUPLICATE CHECK
        # ---------------------------------------------------
        existing = db.query(RawMaterial).filter(
            RawMaterial.company_id == COMPANY_ID,
            (
                (RawMaterial.material_code == material_code) |
                (RawMaterial.material_name.ilike(name))
            )
        ).first()

        if existing:
            skipped += 1
            continue       
        # ---------------------------------------------------
        # INSERT MATERIAL
        # ---------------------------------------------------
        material = RawMaterial(
            id=uuid.uuid4(),
            company_id=COMPANY_ID,
            material_code=material_code,
            material_name=name,
            description=description,
            group_id=group.id,
            category_id=category_obj.id,
            unit_id=unit.id,
            hsn_code=hsn_code,
            gst_rate=gst_rate,
            reorder_level=reorder_level,
            minimum_order_qty=min_order_qty,
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


# ---------------------------------------------------
# RUN SCRIPT
# ---------------------------------------------------
if __name__ == "__main__":
    import_items()