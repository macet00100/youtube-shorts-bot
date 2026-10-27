import os
from PIL import Image, ImageDraw

def generate_suspect_nametags():
    os.makedirs('assets/riddle', exist_ok=True)

    tags = [
        ('badge_butler.png', '1. THE BUTLER', 'Claim: Polishing silverware in kitchen.', (255, 215, 0, 255)),
        ('badge_chef.png', '2. THE CHEF', 'Claim: Cooking dinner for guests.', (100, 200, 255, 255)),
        ('badge_maid.png', '3. THE MAID', 'Claim: Getting mail from mailbox.', (255, 90, 90, 255))
    ]

    for filename, title, claim, color in tags:
        tag = Image.new('RGBA', (980, 220), (0, 0, 0, 0))
        d = ImageDraw.Draw(tag)
        # Sleek dark glass card
        d.rounded_rectangle([(10, 10), (970, 210)], radius=24, fill=(15, 18, 28, 225), outline=color, width=4)
        # Top title badge
        d.rounded_rectangle([(30, 22), (360, 75)], radius=12, fill=color)
        d.text((45, 30), title, fill=(0, 0, 0), font_size=28)
        # Claim statement
        d.text((45, 100), claim, fill=(255, 255, 255), font_size=32)
        tag.save(os.path.join('assets/riddle', filename))

    print("Suspect nametags generated successfully!")

if __name__ == '__main__':
    generate_suspect_nametags()
