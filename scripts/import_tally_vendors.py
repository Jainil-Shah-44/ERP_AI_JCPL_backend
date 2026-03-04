import pandas as pd
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.vendor import Vendor

FILE_PATH = "Party_Master.xls"
COMPANY_ID = "9cefd77f-0fa5-40f9-8183-3c550267aa2c"


def clean(value):
    if pd.isna(value):
        return None
    return str(value).strip()


def clean_decimal(value):
    if pd.isna(value):
        return None
    try:
        return Decimal(str(value))
    except:
        return None


def import_vendors():
    db: Session = SessionLocal()
    df = pd.read_excel(FILE_PATH)

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():

        name = clean(row.get("$Name"))
        if not name:
            skipped += 1
            continue

        existing = db.query(Vendor).filter(
            Vendor.name == name,
            Vendor.company_id == COMPANY_ID
        ).first()

        if existing:
            skipped += 1
            continue

        vendor = Vendor(
            id=uuid.uuid4(),
            company_id=COMPANY_ID,
            name=name,
            mobile_number1=clean(row.get("$LedgerMobile")),
            office_number=clean(row.get("$LedgerPhone")),
            state=clean(row.get("$StateName")),
            pincode=clean(row.get("$LEDPINCode")),
            pan_number=clean(row.get("$IncomeTaxNumber")),
            gst_number=clean(row.get("$PartyGSTIN") or row.get("$_PartyGSTIN")),
            email=clean(row.get("$email")),
            website=clean(row.get("$Website")),
            contact_person=clean(row.get("$LedgerContact")),
            address_line1=clean(row.get("$_Address1")),
            address_line2=clean(row.get("$_Address2")),
            address_line3=clean(row.get("$_Address3")),
            country=clean(row.get("$CountryofResidence")),
            credit_limit=clean_decimal(row.get("$CreditLimit")),
            gst_registration_type=clean(row.get("$GSTRegistrationType")),
        )

        db.add(vendor)
        inserted += 1

    db.commit()
    db.close()

    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    print("Vendor import completed successfully.")


if __name__ == "__main__":
    import_vendors()