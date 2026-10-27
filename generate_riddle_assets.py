import os
from PIL import Image, ImageDraw

def generate_riddle_assets():
    os.makedirs('assets/riddle', exist_ok=True)

    # 1. Top Detective Banner
    banner = Image.new('RGBA', (1080, 240), (0, 0, 0, 0))
    draw = ImageDraw.Draw(banner)
    draw.rounded_rectangle([(100, 50), (980, 170)], radius=25, fill=(15, 18, 28, 235), outline=(255, 190, 0, 255), width=4)
    draw.ellipse([(140, 85), (180, 125)], fill=(255, 190, 0, 255))
    draw.text((205, 84), "CRIME RIDDLE: WHO IS THE KILLER?", fill=(255, 255, 255), font_size=38)
    banner.save('assets/riddle/riddle_banner.png')

    # 2. Suspect Cards (Butler, Chef, Maid)
    def create_card(name, statement, color, filename):
        card = Image.new('RGBA', (960, 240), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([(10, 10), (950, 230)], radius=20, fill=(20, 22, 34, 230), outline=color, width=4)
        # Badge
        d.rounded_rectangle([(30, 25), (320, 78)], radius=12, fill=color)
        d.text((45, 32), name, fill=(0, 0, 0), font_size=30)
        # Statement
        d.text((45, 105), statement, fill=(240, 240, 240), font_size=32)
        card.save(f'assets/riddle/{filename}')

    create_card('1. THE BUTLER', 'Claim: Polishing silverware in kitchen.', (255, 215, 0, 255), 'suspect_1.png')
    create_card('2. THE CHEF', 'Claim: Cooking dinner for the guests.', (100, 200, 255, 255), 'suspect_2.png')
    create_card('3. THE MAID', 'Claim: Getting mail from the mailbox.', (255, 100, 100, 255), 'suspect_3.png')

    # 3. GUILTY Stamp
    stamp = Image.new('RGBA', (500, 180), (0, 0, 0, 0))
    ds = ImageDraw.Draw(stamp)
    ds.rounded_rectangle([(15, 15), (485, 165)], radius=18, fill=(190, 20, 20, 235), outline=(255, 255, 255, 255), width=5)
    ds.text((70, 48), "GUILTY! (THE MAID)", fill=(255, 255, 255), font_size=40)
    stamp.save('assets/riddle/guilty_stamp.png')

    # 4. Countdown Timer Badges (5, 4, 3, 2, 1)
    for sec in range(1, 6):
        cnt = Image.new('RGBA', (320, 160), (0, 0, 0, 0))
        dc = ImageDraw.Draw(cnt)
        dc.rounded_rectangle([(10, 10), (310, 150)], radius=25, fill=(230, 30, 30, 230), outline=(255, 255, 255, 255), width=4)
        dc.text((80, 40), f"TIMER: {sec}s", fill=(255, 255, 255), font_size=38)
        cnt.save(f'assets/riddle/timer_{sec}.png')

    print("All riddle graphic assets generated successfully!")

if __name__ == '__main__':
    generate_riddle_assets()
