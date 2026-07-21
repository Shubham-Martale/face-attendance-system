import io, os
KNOWN_FACES_DIR = os.path.join(os.path.dirname(__file__), "known_faces")
BUILDING_IMG    = os.path.join(os.path.dirname(__file__), "mgm_building.jpg")

def ensure_dirs():
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

def _font(size, bold=False):
    try:
        from PIL import ImageFont
        paths = (
            ["C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/calibrib.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
            if bold else
            ["C:/Windows/Fonts/arial.ttf","C:/Windows/Fonts/calibri.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        )
        for p in paths:
            try: return ImageFont.truetype(p, size)
            except: pass
        return ImageFont.load_default()
    except: return None

def _load_img(path, w, h):
    try:
        from PIL import Image
        if not path or not os.path.exists(path): return None
        with open(path,"rb") as f: raw = f.read()
        if len(raw) < 100: return None
        img = Image.open(io.BytesIO(raw))
        img.load()
        return img.convert("RGB").resize((w, h))
    except: return None

def _make_qr(data, size=160):
    try:
        import qrcode as _qr
        qr = _qr.QRCode(version=1, box_size=4, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image(fill_color="black",
                             back_color="white").convert("RGB").resize((size,size))
    except: return None


def generate_id_card(student_id, name, department, email,
                     registered_on, photo_path=None,
                     college_name="Mahatma Gandhi Mission's College of Computer Science & IT",
                     extra_info=None):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise RuntimeError("Pillow not installed.")

    if extra_info is None:
        extra_info = {}

    PURPLE = "#6a0dad"
    GOLD   = "#ffcc00"
    W      = 1020

    # ── Sizes ─────────────────────────────────────────────────────
    HEADER_H = 150
    PW, PH   = 185, 220     # photo width, height
    GAP      = 33           # row gap
    PAD_TOP  = 16
    PAD_L    = 18
    SIG_GAP  = 8

    # Count address lines
    addr = extra_info.get("address","—")
    addr_lines = 2 if len(addr) > 32 else 1

    # Detail rows: Name, Class, DOB+Blood, Contact, Address, Year
    DETAIL_ROWS = 5 + addr_lines
    DETAILS_H   = DETAIL_ROWS * GAP

    # Badge
    BADGE_H   = 44
    BADGE_GAP = 10

    # Card body height = max(photo block, details block) + badge + padding
    PHOTO_BLOCK    = PAD_TOP + PH + SIG_GAP + 24   # photo + sig line + "Principal" text
    DETAILS_BLOCK  = PAD_TOP + DETAILS_H
    BODY_CONTENT_H = max(PHOTO_BLOCK, DETAILS_BLOCK)
    BODY_H         = BODY_CONTENT_H + BADGE_GAP + BADGE_H + 14

    H = HEADER_H + 9 + BODY_H  # 9 = gold+lavender accent

    card = Image.new("RGB", (W, H), "#ffffff")
    draw = ImageDraw.Draw(card)

    # ── HEADER ────────────────────────────────────────────────────
    draw.rectangle([0,0,W,HEADER_H], fill=PURPLE)
    for i in range(8):
        draw.rectangle([0,HEADER_H-8+i,W,HEADER_H-7+i], fill=(75,0,115))

    # Logo circle
    CX,CY,CR = 76,75,56
    draw.ellipse([CX-CR,CY-CR,CX+CR,CY+CR], fill="#ff8c00",outline="#ffaa00",width=3)
    draw.ellipse([CX-42,CY-42,CX+42,CY+42], fill="#ff6600",outline="#ffcc00",width=2)
    draw.ellipse([CX-11,CY-33,CX+11,CY-13], fill="#8B0000")
    draw.line([(CX,CY-13),(CX-6,CY+12)],    fill="#8B0000",width=5)
    draw.line([(CX,CY-13),(CX+6,CY+12)],    fill="#8B0000",width=5)
    draw.line([(CX-6,CY+12),(CX-17,CY+34)], fill="#8B0000",width=4)
    draw.line([(CX+6,CY+12),(CX+17,CY+34)], fill="#8B0000",width=4)
    draw.line([(CX,CY-4),(CX-21,CY+3)],     fill="#8B0000",width=4)

    # College text
    TX = CX+CR+16
    draw.text((TX,10),  "Mahatma Gandhi Mission's",
              font=_font(15),           fill="white")
    draw.text((TX,29),  "COLLEGE OF COMPUTER SCIENCE & IT",
              font=_font(28,bold=True), fill="white")
    draw.text((TX,68),  "Near Airport, Nanded - 431605",
              font=_font(13),           fill=(220,200,255))
    draw.text((TX,86),  "Tel: (02462)-222592   Web: www.mgmccsit.ac.in",
              font=_font(13),           fill=(220,200,255))

    # Accent lines
    draw.rectangle([0,HEADER_H,  W,HEADER_H+5], fill=GOLD)
    draw.rectangle([0,HEADER_H+5,W,HEADER_H+9], fill="#f0e0ff")

    # ── BODY ──────────────────────────────────────────────────────
    BY = HEADER_H+9
    draw.rectangle([0,BY,W,H],  fill="#fdfbff")
    draw.rectangle([0,BY,9,H],  fill=PURPLE)   # left stripe

    # ── PHOTO — right side, zero gap from header ──────────────────
    PX = W - PW - 38
    PY = BY + PAD_TOP

    photo = _load_img(photo_path, PW, PH)
    if photo:
        draw.rectangle([PX-4,PY-4,PX+PW+4,PY+PH+4], fill="black")
        card.paste(photo,(PX,PY))
    else:
        draw.rectangle([PX-4,PY-4,PX+PW+4,PY+PH+4], fill="black")
        draw.rectangle([PX,PY,PX+PW,PY+PH],          fill="#e8e0f0")
        draw.text((PX+46,PY+90),"PHOTO",font=_font(20,bold=True),fill="#9b6dcc")

    # Signature — no gap
    SY = PY+PH+SIG_GAP
    draw.line([PX,SY,PX+PW,SY], fill="#333",width=1)
    draw.text((PX+40,SY+5),"Principal",font=_font(15),fill="#333")

    # ── DETAILS — left side ───────────────────────────────────────
    LBL = _font(17,bold=True)
    VAL = _font(17)
    V2  = _font(15)
    COL = "#111"
    xl,xc,xv = PAD_L+6, PAD_L+130, PAD_L+147
    y = BY + PAD_TOP

    def row(lbl,val,yy,f=None):
        draw.text((xl,yy),lbl,font=LBL,fill=COL)
        draw.text((xc,yy),":", font=LBL,fill=COL)
        draw.text((xv,yy),str(val),font=f or VAL,fill=COL)
        return yy+GAP

    y = row("Name",   name,                              y)
    y = row("Class",  department or "SY BCA",            y)

    # DOB + Blood grp
    draw.text((xl, y),"DOB",        font=LBL,fill=COL)
    draw.text((xc, y),":",          font=LBL,fill=COL)
    draw.text((xv, y),extra_info.get("dob",str(registered_on)[:10]),
              font=VAL,fill=COL)
    draw.text((390,y),"Blood grp:", font=LBL,fill=COL)
    draw.text((528,y),extra_info.get("blood_group","—"),font=VAL,fill=COL)
    y += GAP

    y = row("Contact",extra_info.get("contact",email or "—"),y)

    # Address
    draw.text((xl,y),"Address",font=LBL,fill=COL)
    draw.text((xc,y),":",      font=LBL,fill=COL)
    if len(addr)>32:
        mid = addr[:32].rfind(",")+1 if "," in addr[:32] else 32
        draw.text((xv,y),   addr[:mid].strip(),font=V2,fill=COL)
        draw.text((xv,y+22),addr[mid:].strip(),font=V2,fill=COL)
        y += GAP+22
    else:
        draw.text((xv,y),addr,font=V2,fill=COL)
        y += GAP

    y = row("Year",extra_info.get("year","2025-26"),y)

    # ── STUDENT ID BADGE — right after last row ────────────────────
    BY2 = y+BADGE_GAP
    draw.rounded_rectangle([PAD_L, BY2, 400, BY2+BADGE_H],
                           radius=10, fill=PURPLE)
    draw.text((PAD_L+12, BY2+12),f"Student ID : {student_id}",
              font=_font(18,bold=True),fill="white")

    # ── BOTTOM STRIPS ─────────────────────────────────────────────
    draw.rectangle([0,H-8,W,H],    fill=PURPLE)
    draw.rectangle([0,H-13,W,H-8], fill=GOLD)

    buf = io.BytesIO()
    card.save(buf,format="PNG",dpi=(300,300))
    buf.seek(0)
    return buf


def generate_id_card_back(student_id, name,
                           college_name="MGM's College of Comp. Sci. & IT, Nanded"):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise RuntimeError("Pillow not installed.")

    W, H   = 1020, 600
    PURPLE = "#6a0dad"
    GOLD   = "#ffcc00"

    card = Image.new("RGB", (W, H), "#f8f8f8")
    draw = ImageDraw.Draw(card)

    # Borders
    draw.rectangle([0,0,W,9],     fill=PURPLE)
    draw.rectangle([0,9,W,14],    fill=GOLD)
    draw.rectangle([0,H-9,W,H],   fill=PURPLE)
    draw.rectangle([0,H-14,W,H-9],fill=GOLD)
    draw.rectangle([0,0,9,H],     fill=PURPLE)
    draw.rectangle([W-9,0,W,H],   fill=PURPLE)

    # ── PLEASE NOTE + barcode ─────────────────────────────────────
    draw.text((24,20),"PLEASE NOTE",font=_font(22,bold=True),fill="#000")

    bx = W-275
    for i in range(72):
        bw = 3 if i%3!=0 else 5
        draw.rectangle([bx+i*3,18,bx+i*3+bw,72],fill="black")
    draw.text((bx+10,76),student_id,font=_font(13),fill="black")

    # Rules
    rules = [
        "1.  The student should possess Identity Card and must produce whenever demanded.",
        "2.  If it is lost, the card holder must intimate to the Principal",
        "     and apply for a new card within a week.",
        "3.  If this card does not belong to you, please return it to :",
        f"     The Principal, {college_name}",
    ]
    ry = 56
    for r in rules:
        draw.text((20,ry),r,font=_font(15),fill="#222")
        ry += 27

    # ── BUILDING PHOTO (bottom half) ──────────────────────────────
    BLDG_Y  = 210
    BLDG_H  = H - BLDG_Y - 22
    QR_W    = 200

    # Right section: actual college building photo
    bldg_img = _load_img(BUILDING_IMG, W - QR_W - 60, BLDG_H)
    if bldg_img:
        # Paste building on right side of bottom
        card.paste(bldg_img, (QR_W + 40, BLDG_Y))
    else:
        # Fallback: coloured box
        draw.rectangle([QR_W+40, BLDG_Y, W-18, BLDG_Y+BLDG_H], fill="#d4edda")
        draw.text((QR_W+60, BLDG_Y+BLDG_H//2-10),
                  "MGM Campus, Nanded", font=_font(16), fill="#3a6b50")

    # ── QR CODE (bottom left) ─────────────────────────────────────
    qr_img = _make_qr(
        f"Student:{name}|ID:{student_id}|College:{college_name}", QR_W)
    if qr_img:
        card.paste(qr_img,(22, BLDG_Y + (BLDG_H - QR_W)//2))
        draw.text((38, BLDG_Y + (BLDG_H - QR_W)//2 + QR_W + 5),
                  "Scan to verify",font=_font(12),fill="#555")

    # Footer
    draw.rectangle([0,H-36,W,H-14],fill=PURPLE)
    draw.text((W//2-210,H-32),
              "This card is the property of the institution.",
              font=_font(13),fill="white")

    buf = io.BytesIO()
    card.save(buf,format="PNG",dpi=(300,300))
    buf.seek(0)
    return buf
