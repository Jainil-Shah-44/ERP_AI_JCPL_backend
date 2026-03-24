import pdfkit
from fastapi.responses import Response
from app.services.purchase.po_detail_service import get_po_detail

config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)


def generate_po_pdf(db, po_id, user):

    if user:
        po = get_po_detail(db, po_id, user)
    else:
        from app.models.purchase.purchase_order import PurchaseOrder
        from app.models.purchase.purchase_order import PurchaseOrderItem
        from app.models.vendor import Vendor

        po_obj = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == po_id
        ).first()

        if not po_obj:
            raise ValueError("PO not found")

        vendor = db.query(Vendor).filter(
            Vendor.id == po_obj.vendor_id
        ).first()

        items = db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.po_id == po_obj.id
        ).all()

        po = {
            "po_number": po_obj.po_number,
            "po_date": po_obj.po_date,
            "vendor_name": vendor.name if vendor else "",
            "vendor_address": po_obj.vendor_address,
            "vendor_contact": po_obj.vendor_contact,
            "payment_terms": po_obj.payment_terms,
            "delivery_terms": po_obj.delivery_terms,
            "transporter": po_obj.transporter,
            "sgst_percent": float(po_obj.sgst_percent or 0),
            "cgst_percent": float(po_obj.cgst_percent or 0),
            "sgst_amount": float(po_obj.sgst_amount or 0),
            "cgst_amount": float(po_obj.cgst_amount or 0),
            "total_amount": float(po_obj.total_amount or 0),
            "other_instructions": po_obj.other_instructions,
            "items": [
                {
                    "material_name": i.material_name,
                    "description": i.description,
                    "quantity": float(i.quantity),
                    "rate": float(i.rate),
                    "amount": float(i.amount),
                }
                for i in items
            ]
        }

    subtotal = po["total_amount"] - po["sgst_amount"] - po["cgst_amount"]

    html = f"""
    <html>
    <head>
    <style>

    @page {{
        size: A4;
        margin: 20mm;
    }}

    body {{
        font-family: Arial, sans-serif;
        font-size: 12px;
        color: #000;
    }}

    .header {{
        text-align: center;
        border-bottom: 2px solid black;
        padding-bottom: 6px;
    }}

    .company {{
        font-size: 18px;
        font-weight: bold;
    }}

    .title {{
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        margin: 10px 0;
        letter-spacing: 1px;
    }}

    .row {{
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }}

    .box {{
        width: 48%;
        border: 1px solid black;
        padding: 8px;
        min-height: 100px;
    }}

    .label {{
        font-weight: bold;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
    }}

    th, td {{
        border: 1px solid black;
        padding: 6px;
        font-size: 11px;
    }}

    th {{
        background-color: #f5f5f5;
        text-align: center;
    }}

    .center {{
        text-align: center;
    }}

    .right {{
        text-align: right;
    }}

    .total-table td {{
        border: none;
    }}

    .total-row td {{
        border-top: 1px solid black;
    }}

    .bold {{
        font-weight: bold;
    }}

    .terms {{
        margin-top: 15px;
        font-size: 11px;
    }}

    .signature {{
        margin-top: 40px;
        text-align: right;
    }}

    </style>
    </head>

    <body>

    <!-- HEADER -->
    <div class="header">
        <div class="company">JEEVAN CHEMICALS PVT LTD</div>
        <div>Factory Address Line Here</div>
        <div>GSTIN: XXXXXXXX</div>
    </div>

    <div class="title">PURCHASE ORDER</div>

    <!-- VENDOR + PO INFO -->
    <div class="row">
        <div class="box">
            <div class="label">Vendor:</div>
            {po['vendor_name']}<br/>
            {po['vendor_address']}<br/>
            {po['vendor_contact']}
        </div>

        <div class="box">
            <div><span class="label">PO No:</span> {po['po_number']}</div>
            <div><span class="label">Date:</span> {po['po_date']}</div>
            <div><span class="label">Transporter:</span> {po['transporter']}</div>
            <div><span class="label">Payment:</span> {po['payment_terms']}</div>
        </div>
    </div>

    <!-- ITEMS TABLE -->
    <table>
    <tr>
        <th style="width:5%">S.No</th>
        <th style="width:45%">Description</th>
        <th style="width:10%">HSN</th>
        <th style="width:10%">Qty</th>
        <th style="width:15%">Rate</th>
        <th style="width:15%">Amount</th>
    </tr>

    {''.join([
    f"""
    <tr>
        <td class="center">{idx+1}</td>
        <td>
            <b>{i['material_name']}</b><br/>
            {i['description'] or ''}
        </td>
        <td class="center">{i.get('hsn_code','')}</td>
        <td class="center">{i['quantity']}</td>
        <td class="right">{i['rate']}</td>
        <td class="right">{i['amount']}</td>
    </tr>
    """
    for idx, i in enumerate(po['items'])
    ])}

    </table>

    <!-- TOTAL -->
    <table class="total-table">
    <tr>
        <td style="width:70%"></td>
        <td class="right">Subtotal:</td>
        <td class="right">{po['total_amount'] - po['sgst_amount'] - po['cgst_amount']}</td>
    </tr>
    <tr>
        <td></td>
        <td class="right">SGST ({po['sgst_percent']}%)</td>
        <td class="right">{po['sgst_amount']}</td>
    </tr>
    <tr>
        <td></td>
        <td class="right">CGST ({po['cgst_percent']}%)</td>
        <td class="right">{po['cgst_amount']}</td>
    </tr>
    <tr class="total-row bold">
        <td></td>
        <td class="right">TOTAL</td>
        <td class="right">{po['total_amount']}</td>
    </tr>
    </table>

    <!-- TERMS -->
    <div class="terms">
        <div><b>Payment Terms:</b> {po['payment_terms']}</div>
        <div><b>Delivery Terms:</b> {po['delivery_terms']}</div>
        <div><b>Instructions:</b> {po['other_instructions']}</div>
    </div>

    <!-- SIGNATURE -->
    <div class="signature">
        For Jeevan Chemicals Pvt Ltd<br/><br/><br/>
        Authorized Signatory
    </div>

    </body>
    </html>
    """

    pdf = pdfkit.from_string(html, False, configuration=config)

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={po['po_number']}.pdf"
        }
    )