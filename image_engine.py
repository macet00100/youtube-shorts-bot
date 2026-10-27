import os
import urllib.parse
import random
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from config import VIDEO_WIDTH, VIDEO_HEIGHT

def generate_image_pollinations(prompt: str, output_path: str, max_retries: int = 3) -> str:
    """
    Generates a 1080x1920 vertical image using Pollinations.ai (Flux/SDXL).
    100% Free, no API key required.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clean_prompt = prompt.strip()
    encoded_prompt = urllib.parse.quote(clean_prompt)
    seed = random.randint(10000, 999999)

    # Pollinations turbo endpoint (ultra-fast 3-5s response, high quality 9:16 vertical)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={VIDEO_WIDTH}&height={VIDEO_HEIGHT}&nologo=true&seed={seed}&model=turbo"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Downloading AI image (Attempt {attempt}/{max_retries})...")
            response = requests.get(url, headers=headers, timeout=25)
            if response.status_code == 200 and len(response.content) > 10000:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"Image successfully created at: {output_path}")
                return output_path
        except Exception as e:
            print(f"Pollinations request warning: {e}. Retrying in 2s...")
            time.sleep(2)

    print("Pollinations failed after retries. Generating emergency aesthetic gradient fallback...")
    return generate_fallback_image(prompt, output_path)

def generate_fallback_image(prompt: str, output_path: str) -> str:
    """Creates a high-resolution dark aesthetic gradient image if network drops."""
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)

    # Draw dark moody gradients & geometric glowing circles
    for r in range(400, 50, -30):
        color = (random.randint(40, 80), random.randint(20, 60), random.randint(80, 150))
        draw.ellipse([(VIDEO_WIDTH//2 - r, VIDEO_HEIGHT//2 - r), (VIDEO_WIDTH//2 + r, VIDEO_HEIGHT//2 + r)], outline=color, width=3)

    img.save(output_path, "JPEG", quality=90)
    return output_path

def generate_all_scene_images(scenes: list, output_folder: str) -> list:
    """Generates an image for each scene in the script with high-impact visual aesthetics."""
    image_paths = []
    for idx, scene in enumerate(scenes):
        out_file = os.path.join(output_folder, f"scene_{idx+1}.jpg")
        prompt = scene.get("image_prompt", "surreal mystery psychology dark cinematic 8k vertical")
        # Enhance prompt for maximum visual impact & high retention
        enhanced_prompt = f"{prompt}, dark surrealism, hyperrealistic, cinematic rim lighting, 8k octane render, volumetric fog, Unreal Engine 5 aesthetic, photorealistic"
        img_path = generate_image_pollinations(enhanced_prompt, out_file)
        image_paths.append(img_path)
        # 2-second cooldown prevents free API rate-limiting on consecutive scene generation
        time.sleep(2)
    return image_paths

if __name__ == "__main__":
    test_prompt = "A glowing optical illusion portal in dark space, neon cyan and purple, 8k vertical"
    generate_image_pollinations(test_prompt, "output/test_image.jpg")
