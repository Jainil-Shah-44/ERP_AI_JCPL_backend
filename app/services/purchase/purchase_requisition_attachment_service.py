import os
import shutil
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.models.purchase.purchase_requisition_attachment import (
    PurchaseRequisitionAttachment
)

UPLOAD_BASE_PATH = "uploads"


def save_pr_attachment(
    db: Session,
    pr_id: UUID,
    file: UploadFile,
    user
):
    pr = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.id == pr_id,
        PurchaseRequisition.company_id == user.company_id
    ).first()

    if not pr:
        raise ValueError("PR not found")

    if pr.status != "DRAFT":
        raise ValueError("Cannot upload documents after PR is submitted")

    # 📁 Build path
    pr_folder = os.path.join(
        UPLOAD_BASE_PATH,
        f"company_{user.company_id}",
        "purchase_requisition",
        str(pr_id)
    )
    os.makedirs(pr_folder, exist_ok=True)

    file_path = os.path.join(pr_folder, file.filename)

    # 💾 Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    attachment = PurchaseRequisitionAttachment(
        pr_id=pr_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=os.path.getsize(file_path),
        uploaded_by=user.id
    )

    db.add(attachment)

    # Optional optimization
    pr.has_attachment = True

    db.commit()
    db.refresh(attachment)

    return {
        "attachment_id": attachment.id,
        "file_name": attachment.file_name
    }
