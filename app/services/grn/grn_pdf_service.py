import pdfkit
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.models.grn.grn import GRN
from app.models.grn.grn_item import GRNItem
from app.models.vendor import Vendor
from app.models.factory import Factory
from sqlalchemy.orm import joinedload
import os
import tempfile
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

BASE_DIR = os.getcwd()
LOGO_PATH = os.path.join(BASE_DIR, "static", "JCPL_logo_trans.png")
WATERMARK_PATH = os.path.join(BASE_DIR, "static", "watermark.png")


def create_watermark(path):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    width, height = A4
    c.drawImage(path, width/2 - 150, height/2 - 150, width=300, height=300, mask='auto')

    c.save()
    packet.seek(0)
    return PdfReader(packet)


def generate_grn_pdf(db: Session, grn_id):

    grn = db.query(GRN).filter(GRN.id == grn_id).first()
    if not grn:
        raise ValueError("GRN not found")

    vendor = db.query(Vendor).filter(Vendor.id == grn.vendor_id).first()
    factory = db.query(Factory).filter(Factory.id == grn.factory_id).first()

    

    items = db.query(GRNItem).options(
        joinedload(GRNItem.material),
        joinedload(GRNItem.unit),
        joinedload(GRNItem.po_item)
    ).filter(GRNItem.grn_id == grn.id).all()
    # ---------------- HEADER / FOOTER SAME ----------------
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

    header_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    header_file.write(header_html.encode())
    header_file.close()

    footer_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    footer_file.write(footer_html.encode())
    footer_file.close()

    # ---------------- HTML CONTENT ----------------
    html = f"""
    <html>
    <head>
    <style>
    body {{ font-family: Arial; font-size: 11px; }}
    .title {{ text-align:center; font-size:16px; font-weight:bold; margin:10px 0; }}
    table {{ width:100%; border-collapse:collapse; margin-top:10px; }}
    th, td {{ border:1px solid black; padding:5px; }}
    th {{ background:#f0f0f0; }}
    </style>
    </head>

    <body>

    <div class="title">GOODS RECEIPT NOTE</div>

    <table>
    <tr>
        <td><b>GRN No:</b> {grn.grn_number}</td>
        <td><b>Status:</b> {grn.status}</td>
    </tr>
    <tr>
        <td><b>GRN Date:</b> {grn.created_at.strftime('%d-%m-%Y')}</td>
        <td></td>
    </tr>
    <tr>
        <td><b>PO Ref:</b> {grn.po.plot_no if grn.po else ''}</td>
        <td><b>Vendor:</b> {vendor.name if vendor else ''}</td>
    </tr>
    <tr>
        <td colspan="2"><b>Factory:</b> {factory.name if factory else ''}</td>
    </tr>
    </table>

    <table>
    <tr>
        <th>#</th>
        <th>Material</th>
        <th>Specification</th>
        <th>Unit</th>
        <th>Ordered</th>
        <th>Received</th>        
        <th>Rejected</th>       
    </tr>

    {''.join([
        f'''
        <tr>
            <td>{idx+1}</td>
            <td>
            {(
                i.material.material_name
                if i.material
                else i.po_item.material_name if i.po_item else ''
            )}
            </td>
            <td>
            {(
                (i.po_item.specification or '') +
                (' | ' if i.po_item and i.po_item.specification and i.po_item.description else '') +
                (i.po_item.description or '')
            ) if i.po_item else ''}
            </td>

            <td>
            {(
                i.unit.unit_code
                if i.unit
                else i.po_item.unit_name if i.po_item else ''
            )}
            </td>
            <td>{i.ordered_qty}</td>
            <td>{i.received_qty}</td>            
            <td>{i.rejected_qty}</td>            
        </tr>
        '''
        for idx, i in enumerate(items)
    ])}

    </table>

    <br/>

    <b>Remarks:</b><br/>
    {grn.remarks or '-'}

    <br/><br/>

    <div style="text-align:right;">
    <b>{factory.incharge_name}</b><br/>
    Authorised Signatory
    </div>
    </body>
    </html>
    """

    options = {
        "enable-local-file-access": None,
        "header-html": header_file.name,
        "footer-html": footer_file.name,
        "margin-top": "40mm",
        "margin-bottom": "25mm",
        "header-spacing": "8",
        "footer-spacing": "5",
    }

    raw_pdf = pdfkit.from_string(html, False, configuration=config, options=options)

    # ---------------- WATERMARK ----------------
    reader = PdfReader(io.BytesIO(raw_pdf))
    writer = PdfWriter()

    for page in reader.pages:
        watermark_pdf = create_watermark(WATERMARK_PATH)
        watermark_page = watermark_pdf.pages[0]
        watermark_page.merge_page(page)
        writer.add_page(watermark_page)

    output = io.BytesIO()
    writer.write(output)

    return Response(
        content=output.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={grn.grn_number}.pdf"
        }
    )