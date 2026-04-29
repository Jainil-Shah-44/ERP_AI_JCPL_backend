import pdfkit
from fastapi.responses import Response
from app.services.purchase.po_detail_service import get_po_detail
from app.models.factory import Factory
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)
import os
import tempfile
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import re
from app.models.purchase.purchase_order_charges import PurchaseOrderCharge

def create_watermark(watermark_path):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    width, height = A4

    # Center image
    img_width = 300
    img_height = 300

    x = (width - img_width) / 2
    y = (height - img_height) / 2

    c.saveState()
    # c.setFillAlpha(0.08)  # transparency
    c.drawImage(watermark_path, x, y, width=img_width, height=img_height, mask='auto')
    c.restoreState()

    c.save()
    packet.seek(0)

    return PdfReader(packet)

BASE_DIR = os.getcwd()
LOGO_PATH = os.path.join(BASE_DIR, "static", "JCPL_logo_trans.png")
WATERMARK_PATH = os.path.join(BASE_DIR, "static", "watermark.png")

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

        subtotal = getattr(po_obj, "subtotal", None)

        if subtotal is None or float(subtotal) == 0:
            subtotal = sum([
                (i.quantity or 0) * (i.rate or 0)
                for i in items
            ])
        
        charges = db.query(PurchaseOrderCharge).filter(
                PurchaseOrderCharge.po_id == po_obj.id
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
            "subtotal": float(subtotal),
            "sgst_amount": float(po_obj.sgst_amount or 0),
            "cgst_amount": float(po_obj.cgst_amount or 0),
            "additional_charges_total": float(getattr(po_obj, "additional_charges_total", 0) or 0),
            "tax_type": po_obj.tax_type,
            "igst_percent": float(po_obj.igst_percent or 0),
            "igst_amount": float(po_obj.igst_amount or 0),
            "charges": [
                {
                    "title": c.title,
                    "amount": float(c.amount or 0)
                }
                for c in charges
            ],
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


    

    instructions = po.get("other_instructions", "") or ""

    def format_delivery_date(match):
        date = match.group(1)

        if "-" in date:  # YYYY-MM-DD
            y, m, d = date.split("-")
            return f"Delivery Date: {d}/{m}/{y}"

        return f"Delivery Date: {date}"  # already formatted

    # Replace delivery date format
    instructions = re.sub(
        r"Delivery Date:\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})",
        format_delivery_date,
        instructions
    )

    # Convert line breaks for HTML
    other_instructions_html = instructions.replace("\n", "<br/>")
    

    tax_rows = ""

    if po.get("tax_type") == "IGST":
        tax_rows = f"""
        <tr>
            <td></td>
            <td>IGST ({po.get('igst_percent', 0)}%)</td>
            <td class="right">{po.get('igst_amount', 0):.2f}</td>
        </tr>
        """
    else:
        tax_rows = f"""
        <tr>
            <td></td>
            <td>SGST ({po.get('sgst_percent', 0)}%)</td>
            <td class="right">{po.get('sgst_amount', 0):.2f}</td>
        </tr>
        <tr>
            <td></td>
            <td>CGST ({po.get('cgst_percent', 0)}%)</td>
            <td class="right">{po.get('cgst_amount', 0):.2f}</td>
        </tr>
        """

    charges_rows = ""

    for c in po.get("charges", []):
        charges_rows += f"""
        <tr>
            <td></td>
            <td>{c['title']}</td>
            <td class="right">{c['amount']:.2f}</td>
        </tr>
        """

    # ---------------- HEADER HTML ----------------
    header_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    body {{
        margin: 0;
        font-family: Arial;
        font-size: 10px;
    }}

    .header {{
        width: 100%;
        text-align: center;
        border-bottom: 2px solid black;
        padding-bottom: 5px;
    }}

    img {{
        width: 70px;
    }}
    </style>
    </head>
    <body>
    <div class="header">
        <img src="file:///{LOGO_PATH}" />
        <div style="font-size:16px; font-weight:bold;">
            JEEVAN CHEMICALS PVT. LTD.
        </div>
        <div style="font-size:9px;">
            Corporate Office Add: W-2 Building, 8th Floor, Office No. 606-612,
            Prem Nagar, Vasai, L.T. Road, Borivali West, Mumbai - 400002<br/>
            Contact No: +91 2245187271 | Email: info@jeevanchemicals.com
        </div>
    </div>
    </body>
    </html>
    """

    # ---------------- FOOTER HTML ----------------
    footer_html = """
    <html>
    <head>
    <style>
    body {
        font-family: Arial;
        font-size: 9px;
        margin: 0;
    }
    .footer {
        width: 100%;
        text-align: center;
        border-top: 1px solid black;
        padding-top: 5px;
    }
    </style>
    </head>
    <body>
    <div class="footer">
        FACTORY OFFICE: PLOT NO. C1B-1907/1, 1911/1 + 1913, 1911/2, 1905/2, A2/2403,
        G.I.D.C., SARIGAM, VIA BHILAD, DIST. VALSAD, GUJARAT - 396155.<br/>
        PLOT NO: D-3-2-1, GIDC DAHEJ III, DAHEJ, BHARUCH, GUJARAT - 392130.<br/>
        CIN: U24100MH2005PTC151145
    </div>
    </body>
    </html>
    """

    # -------- CREATE TEMP FILES --------
    header_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    header_file.write(header_html.encode("utf-8"))
    header_file.close()

    footer_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    footer_file.write(footer_html.encode("utf-8"))
    footer_file.close()

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
        position: relative;
        background: transparent;
    }}

    .main-box {{
        border: 2px solid black;
        padding: 8px;
    }}

    .header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 2px solid black;
        padding-bottom: 8px;
    }}

    .logo-container {{
        width: 30%;
    }}

    .logo {{
        width: 130px;
    }}

    .summary-row td {{
        font-weight: bold;
    }}

    .company-container {{
        width: 70%;
        text-align: right;
    }}

    .company {{
        font-size: 18px;
        font-weight: bold;
    }}

    .sub-header {{
        font-size: 10px;
    }}

   

    .content {{
        position: relative;
        z-index: 1;
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
        page-break-inside: auto;
    }}

    tr {{
    page-break-inside: avoid;
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

    table, th, td {{
    position: relative;
    z-index: 1;
    }}

    thead {{
    display: table-header-group;
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

    html, body {{
        height: 100%;
    }}

    </style>
    </head>

    

    
    
    <body>

    
    <div class="content">

    <div class="main-box">

    <!-- HEADER -->
    
    

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
        <b>Date:</b> {po['po_date'].strftime("%d/%m/%Y") if po.get('po_date') else ""}<br/>
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
    <td class="right">{i['rate']:.2f}</td>
    <td class="right">{i['amount']:.2f}</td>
    </tr>
    '''
    for idx, i in enumerate(po['items'])
    ])}

    </table>

    <!-- TAX + TOTAL -->
    <table>

    <tr class="summary-row">
        <td></td>
        <td><b>SUBTOTAL</b></td>
        <td class="right">{po.get('subtotal', 0):.2f}</td>
    </tr>

    {charges_rows}

    <tr>
        <td></td>
        <td><b>ADDITIONAL CHARGES</b></td>
        <td class="right">{po.get('additional_charges_total', 0):.2f}</td>
    </tr>

    <tr class="summary-row">
        <td></td>
        <td><b>TAXABLE AMOUNT</b></td>
        <td class="right">
            {(po.get('subtotal', 0) + po.get('additional_charges_total', 0)):.2f}
        </td>
    </tr>

    {tax_rows}

    <tr class="summary-row">
        <td></td>
        <td><b>TOTAL</b></td>
        <td class="right"><b>{round(po['total_amount'])}</b></td>
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
        <b>GSTIN:</b> 24AABCJ5069J1ZG, DT : 08.02.17
    </td>

    <td style="width:40%; border:1px solid black; padding:6px; vertical-align:top;">
        <b>Other Instructions:</b><br/>
        {other_instructions_html}<br/><br/>

        
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
    </div>

    </body>
    </html>
    """
    options = {
        "enable-local-file-access": None,
        "print-media-type": None,
        "zoom":"1.0",
        "no-stop-slow-scripts":None,
        "header-html": header_file.name,
        "footer-html": footer_file.name,
        "margin-top": "45mm",
        "margin-bottom": "30mm",
        "header-spacing": "8",
        "footer-spacing": "5",
    }

    raw_pdf = pdfkit.from_string(html, False, configuration=config, options=options)

    reader = PdfReader(io.BytesIO(raw_pdf))
    writer = PdfWriter()

    for page in reader.pages:
        watermark_pdf = create_watermark(WATERMARK_PATH)
        watermark_page = watermark_pdf.pages[0]

        watermark_page.merge_page(page)
        writer.add_page(watermark_page)

    output = io.BytesIO()
    writer.write(output)

    pdf = output.getvalue()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={po['po_number']}.pdf"
        }
    )