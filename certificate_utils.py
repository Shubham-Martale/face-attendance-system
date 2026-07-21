"""
certificate_utils.py
---------------------
Generates a beautiful A4 attendance certificate PDF using ReportLab.
"""

import io
from datetime import datetime

def generate_certificate(student_id, name, department, college_name,
                         total_days, start_date, end_date,
                         issued_by="Principal"):
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
    except ImportError:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")

    buf = io.BytesIO()
    page_w, page_h = A4
    c = canvas.Canvas(buf, pagesize=A4)

    # ── Background ───────────────────────────────────────────────
    c.setFillColor(colors.HexColor("#fdfaf4"))
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # ── Watermark ────────────────────────────────────────────────
    c.saveState()
    c.setFillColor(colors.HexColor("#0d1b2a"))
    c.setFillAlpha(0.04)
    c.setFont("Helvetica-Bold", 72)
    c.translate(page_w/2, page_h/2)
    c.rotate(35)
    c.drawCentredString(0, 0, "CERTIFIED")
    c.restoreState()

    # ── Outer border ─────────────────────────────────────────────
    GOLD  = colors.HexColor("#c9a84c")
    GOLD2 = colors.HexColor("#f0d080")
    NAVY  = colors.HexColor("#0d1b2a")
    MID   = colors.HexColor("#1a3a5c")
    GREY  = colors.HexColor("#666666")

    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.rect(18, 18, page_w-36, page_h-36)
    c.setLineWidth(1)
    c.setStrokeColor(GOLD2)
    c.rect(24, 24, page_w-48, page_h-48)

    # Corner diamonds
    c.setFillColor(GOLD)
    for cx, cy in [(18,18),(page_w-18,18),(18,page_h-18),(page_w-18,page_h-18)]:
        c.saveState()
        c.translate(cx, cy)
        c.rotate(45)
        c.rect(-5,-5,10,10, fill=1, stroke=0)
        c.restoreState()

    # Top center ornament
    mid = page_w/2
    c.circle(mid, page_h-18, 5, fill=1, stroke=0)
    c.circle(mid-22, page_h-18, 3, fill=1, stroke=0)
    c.circle(mid+22, page_h-18, 3, fill=1, stroke=0)

    # ── Header band ──────────────────────────────────────────────
    c.setFillColor(NAVY)
    c.rect(25, page_h-90, page_w-50, 60, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(25, page_h-92, page_w-50, 4, fill=1, stroke=0)
    c.rect(25, page_h-30, page_w-50, 4, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(page_w/2, page_h-58, f"🎓  {college_name}")
    c.setFont("Helvetica", 10)
    c.setFillColor(GOLD2)
    c.drawCentredString(page_w/2, page_h-74, "Department of Academic Affairs")

    # ── Title ────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 34)
    c.setFillColor(NAVY)
    c.drawCentredString(page_w/2, page_h-132, "CERTIFICATE")
    c.setFont("Helvetica", 15)
    c.setFillColor(MID)
    c.drawCentredString(page_w/2, page_h-153, "O F   A T T E N D A N C E")

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(page_w/2-80, page_h-163, page_w/2+80, page_h-163)

    # Decorative side lines near title
    c.setLineWidth(1.5)
    c.line(30, page_h-97, page_w/2-65, page_h-97)
    c.line(page_w/2+65, page_h-97, page_w-30, page_h-97)
    c.setLineWidth(0.5)
    c.line(30, page_h-100, page_w/2-65, page_h-100)
    c.line(page_w/2+65, page_h-100, page_w-30, page_h-100)

    # ── Body text ────────────────────────────────────────────────
    y = page_h - 198
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(GREY)
    c.drawCentredString(page_w/2, y, "This is to certify that")

    # Student name
    y -= 38
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(NAVY)
    c.drawCentredString(page_w/2, y, name.upper())
    # Underline
    nw = c.stringWidth(name.upper(), "Helvetica-Bold", 30)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(page_w/2 - nw/2, y-6, page_w/2 + nw/2, y-6)

    # ID & dept
    y -= 30
    c.setFont("Helvetica", 11)
    c.setFillColor(MID)
    c.drawCentredString(page_w/2, y,
        f"Student ID: {student_id}   |   Department: {department or 'N/A'}")

    # Body sentence
    y -= 42
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawCentredString(page_w/2, y,
        "has successfully maintained attendance during the academic period")
    y -= 22
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(NAVY)
    c.drawCentredString(page_w/2, y, f"from  {start_date}  to  {end_date}")

    # ── Stats box ────────────────────────────────────────────────
    y -= 58
    bw, bh = 420, 78
    bx = (page_w - bw) / 2
    c.setFillColor(NAVY)
    c.roundRect(bx, y-bh+20, bw, bh, 10, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.roundRect(bx, y-bh+16, bw, 4, 0, fill=1, stroke=0)

    stats = [
        (str(total_days),                        "Days Present"),
        (datetime.now().strftime("%d %b %Y"),    "Date Issued"),
        (issued_by,                              "Issued By"),
    ]
    col_w = bw / 3
    for i, (val, lbl) in enumerate(stats):
        cx = bx + col_w*i + col_w/2
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(GOLD2)
        c.drawCentredString(cx, y-14, val)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#aabbcc"))
        c.drawCentredString(cx, y-28, lbl.upper())
        if i < 2:
            c.setStrokeColor(colors.HexColor("#2a4a6a"))
            c.setLineWidth(0.5)
            c.line(bx+col_w*(i+1), y-bh+28, bx+col_w*(i+1), y+10)

    # Remark
    y -= bh + 8
    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(colors.HexColor("#444"))
    c.drawCentredString(page_w/2, y,
        "This certificate is issued in recognition of regular and dedicated attendance.")

    # ── Signatures ───────────────────────────────────────────────
    y -= 56
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.8)
    for sx, role in [(page_w*0.22,"Class Teacher"),
                     (page_w*0.50, issued_by),
                     (page_w*0.78,"HOD / Dean")]:
        c.line(sx-55, y, sx+55, y)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(NAVY)
        c.drawCentredString(sx, y-14, role)
        c.setFont("Helvetica", 8)
        c.setFillColor(GREY)
        c.drawCentredString(sx, y-25, "Signature & Seal")

    # ── QR code ──────────────────────────────────────────────────
    try:
        import qrcode as _qr
        from reportlab.lib.utils import ImageReader
        qr = _qr.QRCode(version=1, box_size=3, border=2)
        qr.add_data(f"Student:{name}|ID:{student_id}|Dept:{department}|Days:{total_days}")
        qr.make(fit=True)
        qi_pil = qr.make_image(fill_color="#0d1b2a",
                                back_color="white").convert("RGB")
        tmp = io.BytesIO()
        qi_pil.save(tmp, format="PNG")
        tmp.seek(0)
        c.drawImage(ImageReader(tmp), page_w-102, 30, 65, 65)
        c.setFont("Helvetica", 6.5)
        c.setFillColor(GREY)
        c.drawCentredString(page_w-70, 26, "Scan to Verify")
    except Exception:
        pass  # QR optional

    # ── Footer ───────────────────────────────────────────────────
    import hashlib
    serial = hashlib.md5(
        f"{student_id}{name}".encode()
    ).hexdigest()[:12].upper()
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#aaaaaa"))
    c.drawString(30, 30, f"Certificate No: CERT-{serial}")
    c.drawCentredString(page_w/2, 30,
        f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")

    c.save()
    buf.seek(0)
    return buf.read()