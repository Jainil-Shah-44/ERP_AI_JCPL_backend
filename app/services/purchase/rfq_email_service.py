from fastapi_mail import FastMail, MessageSchema
from app.core.email import conf


async def send_rfq_email(email: str, file_paths: list[str] | None, vendor_name: str):

    body = f"""
Dear {vendor_name},

Please share your quotation.

Regards,
Procurement Team
"""

    message = MessageSchema(
        subject="Request for Quotation (RFQ)",
        recipients=[email],
        body=body,
        subtype="plain",  # 🔥 REQUIRED
        attachments=file_paths or []
    )

    fm = FastMail(conf)
    await fm.send_message(message)