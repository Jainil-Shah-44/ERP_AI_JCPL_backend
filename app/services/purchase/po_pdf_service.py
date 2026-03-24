import pdfkit
from fastapi.responses import Response
from app.services.purchase.po_detail_service import get_po_detail
from app.models.factory import Factory
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

        factory = None

        if po_obj.factory_id:
            factory = db.query(Factory).filter(
                Factory.id == po_obj.factory_id
            ).first()

        items = db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.po_id == po_obj.id
        ).all()

        po = {
            "po_number": po_obj.po_number,
            "po_date": po_obj.po_date,
            "vendor_name": vendor.name if vendor else "",
            "vendor_address_line1": po_obj.vendor_address_line1,
            "vendor_address_line2": po_obj.vendor_address_line2,
            
            "vendor_contact": po_obj.vendor_contact,
            "payment_terms": po_obj.payment_terms,
            "delivery_terms": po_obj.delivery_terms,
            "transporter": po_obj.transporter,
            "plot_no": po_obj.plot_no,
            "factory_name": factory.name if factory else "",
            "factory_range": po_obj.factory_range,
            "factory_division": po_obj.factory_division,
            "factory_commissionerate": po_obj.factory_commissionerate,
            "factory_gstin": po_obj.factory_gstin,
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
                    "specification":i.specification,
                    "quantity": float(i.quantity),
                    "rate": float(i.rate),
                    "hsn_code":i.hsn_code,
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
        margin: 10mm;
    }}

    body {{
        font-family: Arial;
        font-size: 11px;
    }}

    .main-box {{
        border: 2px solid black;
        padding: 8px;
    }}

    .header {{
        text-align: center;
        border-bottom: 2px solid black;
        padding-bottom: 5px;
    }}

    .company {{
        font-size: 20px;
        font-weight: bold;
    }}

    .sub-header {{
        font-size: 10px;
    }}

    .title {{
        text-align: center;
        font-weight: bold;
        font-size: 14px;
        border: 1px solid black;
        padding: 4px;
        margin-top: 5px;
    }}

    .row {{
        display: flex;
        width: 100%;
    }}

    .box {{
        border: 1px solid black;
        padding: 6px;
    }}

    .left-box {{
        width: 60%;
    }}

    .right-box {{
        width: 40%;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 5px;
    }}

    th, td {{
        border: 1px solid black;
        padding: 5px;
        vertical-align: top;
    }}

    th {{
        text-align: center;
        font-weight: bold;
    }}

    .center {{ text-align: center; }}
    .right {{ text-align: right; }}

    .small-text {{
        font-size: 10px;
    }}

    .signature {{
        margin-top: 20px;
        text-align: right;
    }}

    </style>
    </head>

    <body>

    <div class="main-box">

    <!-- HEADER -->
    <!--
    <div class="header">
        <div class="company">JEEVAN CHEMICALS PVT. LTD.</div>
        <div class="sub-header">
            Corporate Office Add: W-2 Building, 8th Floor, Office No. 606-612, Prem Nagar, Vasai, L.T. Road, Borivali West, Mumbai - 400002<br/>
            Contact No: +91 2245187271 | Email: info@jeevanchemicals.com | Website: www.jeevanchemicals.com
        </div>
    </div>
    -->

    <div class="title">PURCHASE ORDER</div>

    <!-- TOP SECTION -->
    <table style="width:100%; margin-top:5px;">
    <tr>

    <td style="width:60%; border:1px solid black; padding:6px; vertical-align:top;">
        <b>M/S:</b> {po['vendor_name']}<br/>
        {po.get('vendor_address_line1','')}<br/>
        {po.get('vendor_address_line2','')}
    </td>

    <td style="width:40%; border:1px solid black; padding:6px; vertical-align:top;">
        <b>Plot No:</b> {po.get('factory_name','')}<br/>
        <b>P.O No:</b> {po.get('plot_no','')}<br/>
        <b>Date:</b> {po['po_date'].strftime("%d.%m.%Y") if po.get('po_date') else ""}<br/>
        <b>Transporter:</b> {po.get('transporter','')}
    </td>

    </tr>
    </table>

    <!-- ITEMS TABLE -->
    <table>
    <tr>
        <th style="width:5%">S.No</th>
        <th style="width:50%">Description & Specification</th>
        <th style="width:10%">Qty</th>
        <th style="width:15%">Rate</th>
        <th style="width:20%">Value</th>
    </tr>

    {''.join([
    f'''
    <tr>
    <td class="center">{idx+1}</td>
    <td>
    <b>{i.get('material_name','')}</b><br/>
    {i.get('description','')}<br/>
    {i.get('specification','')}<br/><br/>
    <span class="small-text">HSN: {i.get('hsn_code','')}</span>
    </td>
    <td class="center">{i['quantity']}</td>
    <td class="right">{i['rate']}</td>
    <td class="right">{i['amount']}</td>
    </tr>
    '''
    for idx, i in enumerate(po['items'])
    ])}

    </table>

    <!-- TAX + TOTAL -->
    <table>
    <tr>
    <td style="width:60%"></td>
    <td>SGST ({po['sgst_percent']}%)</td>
    <td class="right">{po['sgst_amount']}</td>
    </tr>
    <tr>
    <td></td>
    <td>CGST ({po['cgst_percent']}%)</td>
    <td class="right">{po['cgst_amount']}</td>
    </tr>
    <tr>
    <td></td>
    <td><b>TOTAL</b></td>
    <td class="right"><b>{po['total_amount']}</b></td>
    </tr>
    </table>

    <!-- BOTTOM SECTION -->
    <table style="width:100%; margin-top:10px;">
    <tr>

    <td style="width:60%; border:1px solid black; padding:6px; vertical-align:top;">
        <b>Terms of Payment:</b> {po.get('payment_terms','')}<br/><br/>

        <b>Range:</b> {po.get('factory_range','')}<br/>
        <b>Division:</b> {po.get('factory_division','')}<br/>
        <b>Commissionerate:</b> {po.get('factory_commissionerate','')}<br/>
        <b>GSTIN:</b> {po.get('factory_gstin','')}
    </td>

    <td style="width:40%; border:1px solid black; padding:6px; vertical-align:top;">
        <b>Other Instructions:</b><br/>
        {po.get('other_instructions','')}<br/><br/>

        <b>Freight:</b> PAID
    </td>

    </tr>
    </table>

    <!-- SIGNATURE -->
    <div class="signature">
        FOR JEEVAN CHEMICALS PVT LTD<br/><br/><br/>
        SANJAY SHAH<br/>
        AUTHORISED SIGNATORY
    </div>

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