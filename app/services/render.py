import io
import base64
from dataclasses import dataclass
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from pdf2image import convert_from_bytes

@dataclass(frozen=True)
class Layout:
    page_w: float
    page_h: float
    margin: float
    header_h: float
    table_top: float
    row_h: float

LAYOUT = Layout(
    page_w=A4[0],
    page_h=A4[1],
    margin=18*mm,
    header_h=55*mm,
    table_top=A4[1] - (18*mm) - (55*mm) - (10*mm),
    row_h=9*mm,
)

COLS = ["NO", "DESCRIPTION", "PRICE", "QTY", "TOTAL"]
COL_WIDTHS = [14*mm, 95*mm, 25*mm, 18*mm, 28*mm]

def _hex_to_color(hex_str: str):
    h = (hex_str or "#0A66C2").lstrip("#")
    if len(h) != 6:
        h = "0A66C2"
    r = int(h[0:2], 16)/255.0
    g = int(h[2:4], 16)/255.0
    b = int(h[4:6], 16)/255.0
    return colors.Color(r, g, b)

def render_invoice_quote(payload: dict) -> tuple[bytes, bytes]:
    company = payload["company"]
    client = payload["client"]
    accent = _hex_to_color(company.get("brand_accent_color", "#0A66C2"))

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle(f"{payload['doc_type'].upper()} {payload['doc_number']}")

    w, h = LAYOUT.page_w, LAYOUT.page_h
    x0, y0 = LAYOUT.margin, LAYOUT.margin

    # HEADER LEFT
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x0, h - y0 - 10, (company.get("company_name") or "").upper())

    c.setFont("Helvetica", 9)
    tagline = company.get("tagline", "")
    if tagline:
        c.drawString(x0, h - y0 - 24, tagline)

    addr = company.get("billing_address", "")
    if addr:
        c.drawString(x0, h - y0 - 36, addr)

    reg = company.get("reg_number", "")
    if reg:
        c.drawString(x0, h - y0 - 48, f"REG: {reg}")

    # HEADER RIGHT
    right_x = w - y0 - 170
    c.setFont("Helvetica-Bold", 22)
    c.drawString(right_x, h - y0 - 18, payload["doc_type"].upper())

    c.setFont("Helvetica", 9)
    meta_y = h - y0 - 34
    c.drawString(right_x, meta_y, f"NO: {payload['doc_number']}")
    c.drawString(right_x, meta_y - 12, f"DATE: {payload['issue_date']}")
    if payload.get("due_date"):
        c.drawString(right_x, meta_y - 24, f"DUE: {payload['due_date']}")
    if payload.get("valid_until"):
        c.drawString(right_x, meta_y - 24, f"VALID UNTIL: {payload['valid_until']}")

    # BILL TO
    bill_y = h - y0 - LAYOUT.header_h
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, bill_y, "BILL TO")
    c.setFont("Helvetica", 10)
    c.drawString(x0, bill_y - 14, client.get("client_name", ""))
    ent = client.get("client_entity", "")
    if ent:
        c.drawString(x0, bill_y - 28, ent)

    c.setFont("Helvetica", 8)
    c.drawRightString(w - y0, bill_y - 14, f"PROPOSAL REF: {payload['proposal_ref']}")

    # TABLE HEADER
    table_y = LAYOUT.table_top
    c.setFillColor(accent)
    c.rect(x0, table_y, sum(COL_WIDTHS), LAYOUT.row_h, stroke=0, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    cx = x0
    for i, col in enumerate(COLS):
        c.drawString(cx + 4, table_y + 3, col)
        cx += COL_WIDTHS[i]

    # TABLE ROWS
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    y = table_y - LAYOUT.row_h
    for item in payload["line_items"]:
        cx = x0
        c.setStrokeColor(colors.lightgrey)
        c.rect(x0, y, sum(COL_WIDTHS), LAYOUT.row_h, stroke=1, fill=0)

        c.setFillColor(colors.black)
        c.drawString(cx + 4, y + 3, str(item["no"])); cx += COL_WIDTHS[0]
        c.drawString(cx + 4, y + 3, str(item["description"])[:70]); cx += COL_WIDTHS[1]
        c.drawRightString(cx + COL_WIDTHS[2] - 4, y + 3, f"{float(item['unit_price']):.2f}"); cx += COL_WIDTHS[2]
        c.drawRightString(cx + COL_WIDTHS[3] - 4, y + 3, f"{float(item['qty']):.0f}"); cx += COL_WIDTHS[3]
        c.drawRightString(cx + COL_WIDTHS[4] - 4, y + 3, f"{float(item['total']):.2f}")

        y -= LAYOUT.row_h

    # NOTES
    if payload.get("notes"):
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x0, y - 10, (payload["notes"] or "").upper())
        y -= 18

    # TOTALS BLOCK
    totals_x = w - y0 - 200
    totals_y = y - 10
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(totals_x, totals_y, "SUBTOTAL")
    c.drawRightString(w - y0, totals_y, f"{float(payload['subtotal']):.2f}")

    c.drawString(totals_x, totals_y - 14, "TAX")
    c.drawRightString(w - y0, totals_y - 14, f"{float(payload['tax']):.2f}")

    c.setFillColor(accent)
    c.rect(totals_x, totals_y - 34, (w - y0) - totals_x, 18, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(totals_x + 6, totals_y - 31, "TOTAL DUE" if payload["doc_type"] == "invoice" else "TOTAL")
    c.drawRightString(w - y0 - 6, totals_y - 31, f"{float(payload['total']):.2f}")

    # PAYMENT METHOD
    pay_y = y0 + 90
    bank = company.get("bank_details", {}) or {}
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, pay_y + 55, "PAYMENT METHOD")
    c.setFont("Helvetica", 9)
    c.drawString(x0, pay_y + 40, f"BANK: {bank.get('bank_name','')}")
    c.drawString(x0, pay_y + 28, f"ACCOUNT NAME: {bank.get('account_name','')}")
    c.drawString(x0, pay_y + 16, f"ACCOUNT NO: {bank.get('account_number','')}")
    if bank.get("branch_code"):
        c.drawString(x0, pay_y + 4, f"BRANCH CODE: {bank.get('branch_code','')}")

    # TERMS
    terms = company.get("payment_terms_default", "NET 7")
    c.setFont("Helvetica", 8)
    c.drawString(x0, pay_y - 12, f"TERMS: {terms}. Payment is due per the dates above.")

    # FOOTER
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(w/2, y0 + 30, "THANK YOU FOR YOUR BUSINESS")
    c.setFont("Helvetica", 9)
    sign = company.get("signatory_name", "")
    role = company.get("signatory_role", "Director")
    email = company.get("email", "")
    web = company.get("website", "")
    footer = " | ".join([x for x in [sign, role, email, web] if x])
    if footer:
        c.drawCentredString(w/2, y0 + 16, footer)

    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()

    images = convert_from_bytes(pdf_bytes, dpi=300)
    img = images[0].resize((3840, 2160))
    out_png = io.BytesIO()
    img.save(out_png, format="PNG")
    png_bytes = out_png.getvalue()

    return pdf_bytes, png_bytes

def b64(bytes_in: bytes) -> str:
    return base64.b64encode(bytes_in).decode("utf-8")
