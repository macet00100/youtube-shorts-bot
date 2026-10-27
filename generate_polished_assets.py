import os
from PIL import Image, ImageDraw, ImageFont

def get_font(font_name: str, size: int):
    """Loads a TrueType font with graceful fallback across Windows and Linux."""
    paths = [
        os.path.join(r"C:\Windows\Fonts", font_name),
        os.path.join(r"C:\Windows\Fonts", "arialbd.ttf"),
        os.path.join(r"C:\Windows\Fonts", "arial.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_centered_text(draw, text, font, fill, y, total_width):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (total_width - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)

def draw_dynamic_pill(draw, x_text, y_text, text, font, text_color, pill_color, radius=14, pad_x=22, pad_y=10):
    """Dynamically computes bounding box so text NEVER overflows pill boundaries."""
    bbox = draw.textbbox((x_text, y_text), text, font=font)
    x1 = bbox[0] - pad_x
    y1 = bbox[1] - pad_y
    x2 = bbox[2] + pad_x
    y2 = bbox[3] + pad_y
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=radius, fill=pill_color)
    draw.text((x_text, y_text), text, fill=text_color, font=font)

def create_suspect_card(filename: str, title: str, alibi: str, accent_color: tuple, f_badge, f_body):
    card = Image.new('RGBA', (1000, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([(10, 10), (990, 180)], radius=22, fill=(12, 16, 26, 235), outline=accent_color, width=4)
    draw_dynamic_pill(d, 48, 28, title, f_badge, (0, 0, 0, 255), accent_color, radius=14, pad_x=22, pad_y=10)
    
    # Auto-wrap alibi if too long
    if len(alibi) > 48:
        # Wrap at 45 chars
        words = alibi.split()
        l1, l2 = [], []
        curr = l1
        for w in words:
            if len(" ".join(curr + [w])) <= 44:
                curr.append(w)
            else:
                curr = l2
                curr.append(w)
        line1 = " ".join(l1)
        line2 = " ".join(l2)
        f_sub_body = get_font("arialbd.ttf", 34)
        d.text((40, 92), line1, fill=(255, 255, 255, 255), font=f_sub_body)
        d.text((40, 132), line2, fill=(255, 255, 255, 255), font=f_sub_body)
    else:
        d.text((40, 102), alibi, fill=(255, 255, 255, 255), font=f_body)

    os.makedirs('assets/riddle', exist_ok=True)
    card.save(os.path.join('assets/riddle', filename))

def get_fitted_font(text: str, max_width: int = 880, max_size: int = 80, min_size: int = 42, font_name: str = "arialbd.ttf"):
    # Dynamically scales down font size until text fits comfortably within max_width
    temp = Image.new('RGBA', (1, 1))
    d = ImageDraw.Draw(temp)
    for s in range(max_size, min_size - 1, -2):
        f = get_font(font_name, s)
        bbox = d.textbbox((0, 0), text, font=f)
        if (bbox[2] - bbox[0]) <= max_width:
            return f
    return get_font(font_name, min_size)

def create_guilty_stamp(filename: str, culprit_role: str, culprit_reason: str, f_head):
    stamp = Image.new('RGBA', (1000, 310), (0, 0, 0, 0))
    ds = ImageDraw.Draw(stamp)
    ds.rounded_rectangle([(10, 10), (990, 300)], radius=32, fill=(190, 15, 25, 245), outline=(255, 255, 255, 255), width=7)
    ds.rounded_rectangle([(22, 22), (978, 288)], radius=24, fill=None, outline=(255, 220, 50, 255), width=3)
    
    # 1. Header
    draw_centered_text(ds, "CASE SOLVED: GUILTY!", f_head, (255, 235, 60, 255), 24, 1000)
    
    # 2. Culprit Role (Auto-scaled to never overflow or get clipped)
    clean_role = culprit_role.strip().upper()
    f_dynamic_role = get_fitted_font(clean_role, max_width=880, max_size=80, min_size=42, font_name="arialbd.ttf")
    draw_centered_text(ds, clean_role, f_dynamic_role, (255, 255, 255, 255), 78, 1000)

    # 3. Culprit Reason (Dynamic word wrap & auto-centering)
    clean_reason = culprit_reason.strip()
    words = clean_reason.split()
    f_reason = get_font("ariblk.ttf", 26)
    lines = []
    curr = []
    for w in words:
        test_line = " ".join(curr + [w])
        bbox = ds.textbbox((0, 0), test_line, font=f_reason)
        if (bbox[2] - bbox[0]) <= 880:
            curr.append(w)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))
    
    if len(lines) == 1:
        draw_centered_text(ds, lines[0], f_reason, (255, 240, 100, 255), 200, 1000)
    elif len(lines) == 2:
        draw_centered_text(ds, lines[0], f_reason, (255, 240, 100, 255), 185, 1000)
        draw_centered_text(ds, lines[1], f_reason, (255, 240, 100, 255), 225, 1000)
    else:
        f_small_reason = get_font("ariblk.ttf", 22)
        y_pos = 175
        for l in lines[:3]:
            draw_centered_text(ds, l, f_small_reason, (255, 240, 100, 255), y_pos, 1000)
            y_pos += 34

    os.makedirs('assets/riddle', exist_ok=True)
    stamp.save(os.path.join('assets/riddle', filename))

def ensure_static_assets():
    """Generates the universal static elements if they do not exist."""
    os.makedirs('assets/riddle', exist_ok=True)
    f_title = get_font("ariblk.ttf", 40)
    f_badge = get_font("ariblk.ttf", 34)
    f_body = get_font("arialbd.ttf", 40)
    f_timer_num = get_font("impact.ttf", 120)
    f_timer_sub = get_font("ariblk.ttf", 32)

    # 1. Top Banner
    if not os.path.exists('assets/riddle/riddle_banner.png'):
        banner = Image.new('RGBA', (1080, 190), (0, 0, 0, 0))
        db = ImageDraw.Draw(banner)
        db.rounded_rectangle([(60, 25), (1020, 155)], radius=26, fill=(10, 14, 24, 235), outline=(255, 185, 20, 255), width=5)
        db.ellipse([(95, 68), (135, 108)], fill=(240, 30, 30, 255), outline=(255, 255, 255, 255), width=3)
        db.text((155, 66), "CRIME RIDDLE: WHO IS THE KILLER?", fill=(255, 255, 255, 255), font=f_title)
        banner.save('assets/riddle/riddle_banner.png')

    # 2. Challenge Badge
    if not os.path.exists('assets/riddle/badge_challenge.png'):
        chal = Image.new('RGBA', (1000, 190), (0, 0, 0, 0))
        dch = ImageDraw.Draw(chal)
        dch.rounded_rectangle([(10, 10), (990, 180)], radius=24, fill=(15, 20, 32, 235), outline=(255, 215, 0, 255), width=5)
        draw_dynamic_pill(dch, 48, 28, "CHALLENGE: SPOT THE LIAR", f_badge, (255, 255, 255, 255), (255, 55, 55, 255), radius=14, pad_x=24, pad_y=10)
        dch.text((40, 102), "One suspect is lying! Can you spot who?", fill=(255, 255, 255, 255), font=f_body)
        chal.save('assets/riddle/badge_challenge.png')

    # 3. Live Timers 1-5
    for sec in range(1, 6):
        t_path = f'assets/riddle/timer_{sec}.png'
        if not os.path.exists(t_path):
            cnt = Image.new('RGBA', (520, 250), (0, 0, 0, 0))
            dc = ImageDraw.Draw(cnt)
            dc.rounded_rectangle([(10, 10), (510, 240)], radius=32, fill=(215, 20, 30, 240), outline=(255, 255, 255, 255), width=6)
            dc.rounded_rectangle([(18, 18), (502, 232)], radius=26, fill=None, outline=(255, 220, 50, 255), width=3)
            draw_centered_text(dc, "TIME REMAINING", f_timer_sub, (255, 235, 50, 255), 24, 520)
            draw_centered_text(dc, str(sec), f_timer_num, (255, 255, 255, 255), 72, 520)
            cnt.save(t_path)

def generate_dynamic_assets(script_data: dict):
    """
    Dynamically generates the 3 suspect cards and GUILTY stamp matching
    whatever AI crime mystery was just generated!
    """
    ensure_static_assets()

    f_badge = get_font("ariblk.ttf", 34)
    f_body = get_font("arialbd.ttf", 40)
    f_guilty_head = get_font("ariblk.ttf", 38)

    s1 = script_data.get("suspect_1", {"title": "SUSPECT 1: THE BUTLER", "alibi": "Alibi 1"})
    s2 = script_data.get("suspect_2", {"title": "SUSPECT 2: THE CHEF", "alibi": "Alibi 2"})
    s3 = script_data.get("suspect_3", {"title": "SUSPECT 3: THE GARDENER", "alibi": "Alibi 3"})

    # Accents: Gold, Cyan, Red/Orange
    create_suspect_card("badge_suspect_1.png", s1.get("title", "SUSPECT 1"), s1.get("alibi", ""), (255, 215, 0, 255), f_badge, f_body)
    create_suspect_card("badge_suspect_2.png", s2.get("title", "SUSPECT 2"), s2.get("alibi", ""), (40, 200, 255, 255), f_badge, f_body)
    create_suspect_card("badge_suspect_3.png", s3.get("title", "SUSPECT 3"), s3.get("alibi", ""), (255, 75, 75, 255), f_badge, f_body)

    culprit = script_data.get("culprit_role", "THE CULPRIT")
    reason = script_data.get("culprit_reason", "REASON: LOGICAL CONTRADICTION!")
    create_guilty_stamp("guilty_stamp.png", culprit, reason, f_guilty_head)

    print("Dynamic riddle badges and GUILTY stamp generated flawlessly.")

if __name__ == '__main__':
    ensure_static_assets()
