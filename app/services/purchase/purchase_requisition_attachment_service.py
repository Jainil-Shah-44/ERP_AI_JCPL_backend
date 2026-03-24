import os
import shutil
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.models.purchase.purchase_requisition_attachment import (
    PurchaseRequisitionAttachment
)
from app.core.permissions import get_user_permissions
from uuid import uuid4

UPLOAD_BASE_PATH = "uploads"

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "xls", "xlsx"}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def save_pr_attachment(db: Session, pr_id: UUID, file: UploadFile, user):

    # ---------------- VALIDATION ---------------- #
    original_name = file.filename.lower()
    ext = original_name.split(".")[-1]

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type .{ext} not allowed")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValueError("Invalid file type")

    # ---------------- SAFE FILE NAME ---------------- #
    safe_filename = f"{uuid4()}.{ext}"

    # ---------------- EXISTING LOGIC ---------------- #
    pr = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.id == pr_id,
        PurchaseRequisition.company_id == user.company_id
    ).first()

    if not pr:
        raise ValueError("PR not found")

    if pr.status != "DRAFT":
        raise ValueError("Cannot upload documents after PR is submitted")

    permissions = get_user_permissions(db, user.id)

    if "PR_VIEW_ALL" not in permissions:
        if pr.created_by != user.id:
            raise ValueError("You cannot upload attachment to this PR")

    # ---------------- PATH ---------------- #
    pr_folder = os.path.join(
        UPLOAD_BASE_PATH,
        f"company_{user.company_id}",
        "purchase_requisition",
        str(pr_id)
    )
    os.makedirs(pr_folder, exist_ok=True)

    relative_path = os.path.join(
        f"company_{user.company_id}",
        "purchase_requisition",
        str(pr_id),
        safe_filename
    )

    file_path = os.path.join(UPLOAD_BASE_PATH, relative_path)

    # ---------------- SAVE ---------------- #
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    attachment = PurchaseRequisitionAttachment(
        pr_id=pr_id,
        file_name=file.filename,  # original name
        file_path=relative_path,
        file_type=file.content_type,
        file_size=os.path.getsize(file_path),
        uploaded_by=user.id
    )

    db.add(attachment)
    pr.has_attachment = True

    db.commit()
    db.refresh(attachment)

    return {
        "attachment_id": attachment.id,
        "file_name": attachment.file_name
    }