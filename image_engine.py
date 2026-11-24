import os
import urllib.parse
import random
import time
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import VIDEO_WIDTH, VIDEO_HEIGHT

BASE_ART_STYLE = (
    "moody noir detective comic illustration, dark cinematic graphic novel art style, "
    "dramatic rim lighting, high contrast shadows, detailed textures, 9:16 vertical composition"
)

def generate_image_pollinations(prompt: str, output_path: str, max_retries: int = 1) -> str:
    """
    Generates a vertical image using Pollinations.ai (Flux/Turbo).
    100% Free, no API key required.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clean_prompt = prompt.strip()[:100]
    encoded_prompt = urllib.parse.quote(clean_prompt)
    seed = random.randint(10000, 999999)

    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={VIDEO_WIDTH}&height={VIDEO_HEIGHT}&nologo=true&seed={seed}&model=turbo"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=18)
        if response.status_code == 200 and len(response.content) > 10000:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Đã tải ảnh AI từ Pollinations: {output_path} ({len(response.content)} bytes)")
            return output_path
    except Exception:
        pass

    return generate_fallback_noir_image(prompt, output_path)

def generate_fallback_noir_image(prompt: str, output_path: str, scene_type: str = "hook") -> str:
    """
    Creates an atmospheric dark noir graphic illustration with Pillow if network is throttled.
    Scene-specific lighting:
    - hook: dark crime scene with subtle mystery glow and chalk lines
    - suspect_1: warm gold amber spotlight
    - suspect_2: cold electric cyan spotlight
    - suspect_3: crimson red mystery spotlight
    - reveal: dramatic central evidence magnifying glow
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=(10, 12, 18))
    draw = ImageDraw.Draw(img)

    center_x = VIDEO_WIDTH // 2
    center_y = int(VIDEO_HEIGHT * 0.45)

    palettes = {
        "hook": (35, 30, 48),
        "suspect_1": (50, 40, 15),
        "suspect_2": (15, 45, 55),
        "suspect_3": (55, 20, 25),
        "reveal": (60, 25, 20)
    }
    base_color = palettes.get(scene_type, (35, 30, 48))

    # Radial ambient spotlight
    for r in range(750, 40, -35):
        factor = (750 - r) / 750.0
        glow_c = (
            int(base_color[0] * factor + 8),
            int(base_color[1] * factor + 10),
            int(base_color[2] * factor + 16)
        )
        draw.ellipse([(center_x - r, center_y - r), (center_x + r, center_y + r)], fill=glow_c)

    # Dramatic graphic novel diagonal shadow lines
    overlay = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    d_over = ImageDraw.Draw(overlay)
    for y in range(-VIDEO_HEIGHT, VIDEO_HEIGHT * 2, 70):
        d_over.line([(0, y), (VIDEO_WIDTH, y + 420)], fill=(0, 0, 0, 80), width=30)

    # Top & bottom cinematic black letterbox shading
    d_over.rectangle([(0, 0), (VIDEO_WIDTH, 130)], fill=(5, 7, 12, 190))
    d_over.rectangle([(0, VIDEO_HEIGHT - 320), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=(5, 7, 12, 220))

    img.paste(overlay, (0, 0), overlay)
    img = img.filter(ImageFilter.GaussianBlur(radius=2))

    img.save(output_path, "JPEG", quality=92)
    return output_path

def generate_scene_images(script_data: dict, output_folder: str) -> dict:
    """
    Generates 5 cohesive 9:16 vertical images in the unified noir detective comic art style:
    1. Hook scene (Crime scene)
    2. Suspect 1 (Performing claimed action)
    3. Suspect 2 (Performing claimed action)
    4. Suspect 3 (Performing claimed action)
    5. Reveal scene (Evidence / flaw close-up)
    """
    os.makedirs(output_folder, exist_ok=True)
    scene_prompts = script_data.get("scene_prompts", {})
    setting = script_data.get("setting_theme", "Crime Scene")
    s1 = script_data.get("suspect_1", {})
    s2 = script_data.get("suspect_2", {})
    s3 = script_data.get("suspect_3", {})

    hook_prompt = scene_prompts.get("hook", f"Crime scene at {setting}, {BASE_ART_STYLE}")
    s1_prompt = scene_prompts.get("suspect_1", f"{s1.get('role', 'Suspect 1')} at {setting}, {BASE_ART_STYLE}")
    s2_prompt = scene_prompts.get("suspect_2", f"{s2.get('role', 'Suspect 2')} at {setting}, {BASE_ART_STYLE}")
    s3_prompt = scene_prompts.get("suspect_3", f"{s3.get('role', 'Suspect 3')} at {setting}, {BASE_ART_STYLE}")
    reveal_prompt = scene_prompts.get("reveal", f"Evidence close-up revealing contradiction at {setting}, {BASE_ART_STYLE}")

    targets = [
        ("hook", hook_prompt, os.path.join(output_folder, "scene_1_hook.jpg")),
        ("suspect_1", s1_prompt, os.path.join(output_folder, "scene_2_suspect_1.jpg")),
        ("suspect_2", s2_prompt, os.path.join(output_folder, "scene_3_suspect_2.jpg")),
        ("suspect_3", s3_prompt, os.path.join(output_folder, "scene_4_suspect_3.jpg")),
        ("reveal", reveal_prompt, os.path.join(output_folder, "scene_5_reveal.jpg"))
    ]

    results = {}
    print("\n[HỆ THỐNG HÌNH ẢNH] Khởi tạo bộ 5 ảnh 9:16 đồng bộ phong cách nghệ thuật Noir Comic...")
    for key, prompt, path in targets:
        if os.path.exists(path) and os.path.getsize(path) > 10000:
            results[key] = path
            continue

        clean_p = f"{prompt.split(',')[0]}, noir comic illustration, 9:16 vertical"
        img_path = generate_image_pollinations(clean_p, path)
        if not (os.path.exists(img_path) and os.path.getsize(img_path) > 10000):
            img_path = generate_fallback_noir_image(prompt, path, scene_type=key)
        results[key] = img_path

    return results

if __name__ == "__main__":
    print("Image engine ready.")
