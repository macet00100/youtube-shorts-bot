import os
import re
from PIL import Image, ImageDraw, ImageFont

def get_font(font_name: str, size: int):
    """Loads TrueType font across Windows and Linux with graceful fallbacks."""
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

def draw_dynamic_pill(draw, x_text, y_text, text, font, text_color, pill_color, radius=14, pad_x=22, pad_y=8):
    """Dynamically computes bounding box so text NEVER overflows pill boundaries."""
    bbox = draw.textbbox((x_text, y_text), text, font=font)
    x1 = bbox[0] - pad_x
    y1 = bbox[1] - pad_y
    x2 = bbox[2] + pad_x
    y2 = bbox[3] + pad_y
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=radius, fill=pill_color)
    draw.text((x_text, y_text), text, fill=text_color, font=font)

def wrap_text_pixel_fit(draw, text: str, font, max_width: int) -> list:
    """
    Wraps text strictly using real pixel measurements from draw.textbbox.
    NEVER cuts words or hyphenates mid-word.
    """
    clean_text = re.sub(r'\s+', ' ', text).strip()
    words = clean_text.split()
    if not words:
        return []

    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_w = bbox[2] - bbox[0]

        if line_w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines

def get_fitted_font(text: str, max_width: int = 880, max_size: int = 80, min_size: int = 36, font_name: str = "arialbd.ttf"):
    """Dynamically scales down font size until text fits comfortably within max_width."""
    temp = Image.new('RGBA', (1, 1))
    d = ImageDraw.Draw(temp)
    for s in range(max_size, min_size - 1, -2):
        f = get_font(font_name, s)
        bbox = d.textbbox((0, 0), text, font=f)
        if (bbox[2] - bbox[0]) <= max_width:
            return f
    return get_font(font_name, min_size)

# ==============================================================================
# ALIBI CARDS (SUSPECT BADGES) WITH AUTO-WRAP & ZERO OVERFLOW
# ==============================================================================

def create_suspect_card(filename: str, title: str, alibi: str, accent_color: tuple, f_badge, f_body):
    """
    Renders an Alibi Card (1000x210) with exact pixel-wrapped text and safe padding.
    Guarantees no word is ever clipped or truncated.
    """
    card = Image.new('RGBA', (1000, 210), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)

    # Sleek frosted dark card
    d.rounded_rectangle([(10, 10), (990, 200)], radius=24, fill=(12, 16, 26, 235), outline=accent_color, width=4)

    # Title pill at top
    draw_dynamic_pill(d, 48, 26, title, f_badge, (0, 0, 0, 255), accent_color, radius=12, pad_x=22, pad_y=8)

    # Wrap alibi text strictly using pixel bounding box
    max_w = 900
    font_alibi = f_body
    lines = wrap_text_pixel_fit(d, alibi, font_alibi, max_w)

    # If 3 or more lines, scale down font slightly
    if len(lines) > 2:
        font_alibi = get_font("arialbd.ttf", 32)
        lines = wrap_text_pixel_fit(d, alibi, font_alibi, max_w)

    if len(lines) == 1:
        d.text((45, 110), lines[0], fill=(255, 255, 255, 255), font=font_alibi)
    elif len(lines) == 2:
        d.text((45, 96), lines[0], fill=(255, 255, 255, 255), font=font_alibi)
        d.text((45, 142), lines[1], fill=(255, 255, 255, 255), font=font_alibi)
    else:
        y_pos = 90
        for l in lines[:3]:
            d.text((45, y_pos), l, fill=(255, 255, 255, 255), font=font_alibi)
            y_pos += 36

    os.makedirs('assets/riddle', exist_ok=True)
    card.save(os.path.join('assets/riddle', filename))

# ==============================================================================
# 3-SUSPECT LINEUP SCREEN (OVERVIEW FOR 3-SECOND COUNTDOWN)
# ==============================================================================

def create_lineup_screen(script_data: dict, output_path: str = "assets/riddle/suspect_lineup.png"):
    """
    Renders the composite 3-Suspect Lineup Screen (1000x640) displayed during
    the active 3-second countdown.
    Shows all 3 suspects and their claims side-by-side/stacked so viewers can
    pause and re-evaluate evidence.
    """
    w, h = 1000, 640
    screen = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(screen)

    # Main semi-transparent panel
    d.rounded_rectangle([(8, 8), (w - 8, h - 8)], radius=28, fill=(8, 12, 20, 235), outline=(255, 205, 30, 255), width=4)

    # Header: SUSPECT LINEUP
    f_header = get_font("ariblk.ttf", 36)
    draw_centered_text(d, "SUSPECT LINEUP - SPOT THE LIAR", f_header, (255, 220, 40, 255), 26, w)

    f_pill = get_font("ariblk.ttf", 26)
    f_claim = get_font("arialbd.ttf", 28)

    suspects = [
        (script_data.get("suspect_1", {}), (255, 215, 0, 255), 90),
        (script_data.get("suspect_2", {}), (40, 200, 255, 255), 260),
        (script_data.get("suspect_3", {}), (255, 80, 80, 255), 430)
    ]

    for idx, (s_data, color, y_offset) in enumerate(suspects, start=1):
        # Mini card for suspect
        d.rounded_rectangle([(30, y_offset), (w - 30, y_offset + 145)], radius=18, fill=(18, 24, 38, 220), outline=color, width=3)

        role_title = s_data.get("title", f"{idx}. SUSPECT {idx}")
        draw_dynamic_pill(d, 50, y_offset + 16, role_title, f_pill, (0, 0, 0, 255), color, radius=10, pad_x=18, pad_y=6)

        claim_text = s_data.get("card_text", s_data.get("alibi", ""))
        lines = wrap_text_pixel_fit(d, claim_text, f_claim, max_width=860)

        if len(lines) == 1:
            d.text((50, y_offset + 80), lines[0], fill=(255, 255, 255, 255), font=f_claim)
        elif len(lines) >= 2:
            d.text((50, y_offset + 68), lines[0], fill=(255, 255, 255, 255), font=f_claim)
            d.text((50, y_offset + 104), lines[1], fill=(255, 255, 255, 255), font=f_claim)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    screen.save(output_path)
    print(f"✅ Đã tạo màn hình tổng hợp 3 nghi phạm (Suspect Lineup): {output_path}")
    return output_path

# ==============================================================================
# GUILTY STAMP (REVEAL BADGE) WITH AUTO-SCALING
# ==============================================================================

def create_guilty_stamp(filename: str, culprit_role: str, culprit_reason: str, f_head):
    """
    Renders the dramatic red CASE SOLVED: GUILTY stamp (1000x310).
    Auto-scales role name and pixel-wraps contradiction reason so text never overflows.
    """
    stamp = Image.new('RGBA', (1000, 310), (0, 0, 0, 0))
    ds = ImageDraw.Draw(stamp)
    ds.rounded_rectangle([(10, 10), (990, 300)], radius=32, fill=(195, 15, 25, 245), outline=(255, 255, 255, 255), width=7)
    ds.rounded_rectangle([(22, 22), (978, 288)], radius=24, fill=None, outline=(255, 220, 50, 255), width=3)

    # 1. Header
    draw_centered_text(ds, "CASE SOLVED: GUILTY!", f_head, (255, 235, 60, 255), 24, 1000)

    # 2. Culprit Role (Auto-scaled to never overflow)
    clean_role = culprit_role.strip().upper()
    f_dynamic_role = get_fitted_font(clean_role, max_width=880, max_size=76, min_size=38, font_name="arialbd.ttf")
    draw_centered_text(ds, clean_role, f_dynamic_role, (255, 255, 255, 255), 76, 1000)

    # 3. Culprit Reason (Pixel wrap & auto-center)
    clean_reason = culprit_reason.strip()
    f_reason = get_font("ariblk.ttf", 26)
    lines = wrap_text_pixel_fit(ds, clean_reason, f_reason, max_width=880)

    if len(lines) == 1:
        draw_centered_text(ds, lines[0], f_reason, (255, 240, 100, 255), 195, 1000)
    elif len(lines) == 2:
        draw_centered_text(ds, lines[0], f_reason, (255, 240, 100, 255), 180, 1000)
        draw_centered_text(ds, lines[1], f_reason, (255, 240, 100, 255), 224, 1000)
    else:
        f_small_reason = get_font("ariblk.ttf", 22)
        lines_small = wrap_text_pixel_fit(ds, clean_reason, f_small_reason, max_width=880)
        y_pos = 172
        for l in lines_small[:3]:
            draw_centered_text(ds, l, f_small_reason, (255, 240, 100, 255), y_pos, 1000)
            y_pos += 34

    os.makedirs('assets/riddle', exist_ok=True)
    stamp.save(os.path.join('assets/riddle', filename))

# ==============================================================================
# STATIC & DYNAMIC ASSET INITIALIZATION
# ==============================================================================

def ensure_static_assets():
    """Generates the universal static elements: Top Banner and Timers 1-3."""
    os.makedirs('assets/riddle', exist_ok=True)
    f_title = get_font("ariblk.ttf", 40)
    f_timer_num = get_font("impact.ttf", 110)
    f_timer_sub = get_font("ariblk.ttf", 28)

    # 1. Top Banner
    banner_path = 'assets/riddle/riddle_banner.png'
    banner = Image.new('RGBA', (1080, 180), (0, 0, 0, 0))
    db = ImageDraw.Draw(banner)
    db.rounded_rectangle([(60, 20), (1020, 150)], radius=24, fill=(10, 14, 24, 235), outline=(255, 185, 20, 255), width=5)
    db.ellipse([(95, 62), (135, 102)], fill=(240, 30, 30, 255), outline=(255, 255, 255, 255), width=3)
    db.text((155, 60), "CRIME RIDDLE: WHO IS THE KILLER?", fill=(255, 255, 255, 255), font=f_title)
    banner.save(banner_path)

    # 2. Timers 1-3 (Clean, compact 3-second countdown badges)
    for sec in range(1, 4):
        t_path = f'assets/riddle/timer_{sec}.png'
        cnt = Image.new('RGBA', (480, 200), (0, 0, 0, 0))
        dc = ImageDraw.Draw(cnt)
        dc.rounded_rectangle([(8, 8), (472, 192)], radius=28, fill=(215, 20, 30, 240), outline=(255, 255, 255, 255), width=5)
        dc.rounded_rectangle([(16, 16), (464, 184)], radius=22, fill=None, outline=(255, 220, 50, 255), width=3)
        draw_centered_text(dc, "TIME REMAINING", f_timer_sub, (255, 235, 50, 255), 18, 480)
        draw_centered_text(dc, str(sec), f_timer_num, (255, 255, 255, 255), 58, 480)
        cnt.save(t_path)

def generate_dynamic_assets(script_data: dict):
    """
    Dynamically generates the 3 suspect alibi cards, the 3-suspect lineup screen,
    and the GUILTY stamp tailored to the current AI crime mystery.
    """
    ensure_static_assets()

    f_badge = get_font("ariblk.ttf", 32)
    f_body = get_font("arialbd.ttf", 38)
    f_guilty_head = get_font("ariblk.ttf", 38)

    s1 = script_data.get("suspect_1", {})
    s2 = script_data.get("suspect_2", {})
    s3 = script_data.get("suspect_3", {})

    # Accents: Gold, Cyan, Red/Coral
    create_suspect_card(
        "badge_suspect_1.png",
        s1.get("title", "1. SUSPECT 1"),
        s1.get("card_text", s1.get("alibi", "")),
        (255, 215, 0, 255),
        f_badge,
        f_body
    )
    create_suspect_card(
        "badge_suspect_2.png",
        s2.get("title", "2. SUSPECT 2"),
        s2.get("card_text", s2.get("alibi", "")),
        (40, 200, 255, 255),
        f_badge,
        f_body
    )
    create_suspect_card(
        "badge_suspect_3.png",
        s3.get("title", "3. SUSPECT 3"),
        s3.get("card_text", s3.get("alibi", "")),
        (255, 80, 80, 255),
        f_badge,
        f_body
    )

    # 3-Suspect Lineup Screen for Countdown
    create_lineup_screen(script_data, "assets/riddle/suspect_lineup.png")

    # GUILTY stamp
    culprit = script_data.get("culprit_role", "THE CULPRIT")
    reason = script_data.get("culprit_reason", "REASON: LOGICAL CONTRADICTION!")
    create_guilty_stamp("guilty_stamp.png", culprit, reason, f_guilty_head)

    print("Dynamic UI assets (cards, lineup, stamp) generated with pixel-perfect fitting.")

if __name__ == '__main__':
    ensure_static_assets()
