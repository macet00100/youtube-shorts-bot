import os
import urllib.parse
import random
import time
import re
import requests
from config import VIDEO_WIDTH, VIDEO_HEIGHT

# Unified Art Style applied across all scenes
BASE_ART_STYLE = (
    "moody noir detective comic illustration, dark cinematic graphic novel art style, "
    "dramatic rim lighting, high contrast shadows, detailed textures, 9:16 vertical composition"
)

NEGATIVE_PROMPT = (
    "text, watermark, speech bubbles, letters, words, typography, signature, subtitles, font, logo, UI, frames, borders"
)

# Supported Pollinations image models with automatic fallback
IMAGE_MODELS = ["turbo", "sana"]

def generate_image_pollinations(prompt: str, output_path: str, max_retries: int = 3) -> str:
    """
    Generates a 1080x1920 vertical scene image using Pollinations.ai with multi-model fallback.
    - Tier 1: Pollinations 'turbo' (Fast Flux/SDXL)
    - Tier 2: Pollinations 'sana' (NVIDIA Efficient Diffusion)
    Includes negative prompt to eliminate text, watermarks, and speech bubbles.
    Handles rate-limits with adaptive backoff.
    DOES NOT silently fallback to empty gradients or unrelated stock footage.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clean_prompt = prompt.strip()[:180]
    encoded_negative = urllib.parse.quote(NEGATIVE_PROMPT)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    last_error = None

    for model in IMAGE_MODELS:
        seed = random.randint(10000, 999999)
        full_text_prompt = f"{clean_prompt}, {BASE_ART_STYLE}, strictly no text, no watermark"
        encoded_prompt = urllib.parse.quote(full_text_prompt)

        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?negative={encoded_negative}&width={VIDEO_WIDTH}&height={VIDEO_HEIGHT}"
            f"&nologo=true&seed={seed}&model={model}"
        )

        for attempt in range(1, max_retries + 1):
            try:
                print(f"🎨 [Image Engine] Đang tạo ảnh AI qua model '{model}': '{clean_prompt[:45]}...' (Lượt {attempt}/{max_retries})")
                response = requests.get(url, headers=headers, timeout=28)

                if response.status_code == 200 and len(response.content) > 10000:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Đã tạo ảnh AI thành công bằng '{model}': {output_path} ({len(response.content)} bytes)")
                    return output_path

                elif response.status_code == 402:
                    match = re.search(r'Retry after (\d+)s', response.text)
                    wait_sec = int(match.group(1)) + 2 if match else 25
                    print(f"⏳ [Rate Limit] Server yêu cầu đợi {wait_sec}s trước khi gọi lại...")
                    time.sleep(wait_sec)
                    continue

                else:
                    print(f"⚠️ [Image Engine] HTTP {response.status_code} trên model '{model}'. Chuyển sang thử lại/model tiếp theo...")
                    last_error = f"HTTP {response.status_code}"
                    time.sleep(2.0)
                    break

            except Exception as e:
                print(f"⚠️ [Image Engine] Lỗi mạng khi gọi model '{model}': {e}")
                last_error = str(e)
                time.sleep(2.0)

    # If all models and retries failed, raise explicit exception
    # NEVER silently fallback to blank gradients or irrelevant stock videos!
    raise RuntimeError(
        f"❌ [IMAGE ENGINE ERROR] Không thể tạo ảnh AI chất lượng cao cho: '{output_path}'. "
        f"Lỗi cuối cùng: {last_error}. "
        f"Hệ thống dừng pipeline để bảo vệ kênh khỏi việc đăng video lỗi hoặc mất bối cảnh."
    )

def generate_scene_images(script_data: dict, output_folder: str) -> dict:
    """
    Generates all 5 cohesive 9:16 vertical images:
    1. Hook scene (Crime scene)
    2. Suspect 1 (Performing claimed action)
    3. Suspect 2 (Performing claimed action)
    4. Suspect 3 (Performing claimed action)
    5. Reveal scene (Evidence / flaw close-up)

    Guarantees no watermark, no text in artwork, and strictly fails if image generation fails.
    """
    os.makedirs(output_folder, exist_ok=True)
    scene_prompts = script_data.get("scene_prompts", {})
    setting = script_data.get("setting_theme", "Crime Scene")
    s1 = script_data.get("suspect_1", {})
    s2 = script_data.get("suspect_2", {})
    s3 = script_data.get("suspect_3", {})

    hook_prompt = scene_prompts.get(
        "hook",
        f"Crime scene at {setting}, intense mystery atmosphere, dramatic shadows, clean cinematic comic art"
    )
    s1_prompt = scene_prompts.get(
        "suspect_1",
        f"{s1.get('role', 'Suspect 1')} at {setting}, {s1.get('card_text', '')}, comic character illustration"
    )
    s2_prompt = scene_prompts.get(
        "suspect_2",
        f"{s2.get('role', 'Suspect 2')} at {setting}, {s2.get('card_text', '')}, comic character illustration"
    )
    s3_prompt = scene_prompts.get(
        "suspect_3",
        f"{s3.get('role', 'Suspect 3')} at {setting}, {s3.get('card_text', '')}, comic character illustration"
    )
    reveal_prompt = scene_prompts.get(
        "reveal",
        f"Dramatic close-up evidence revealing the contradiction at {setting}, focal illumination"
    )

    targets = [
        ("hook", hook_prompt, os.path.join(output_folder, "scene_1_hook.jpg")),
        ("suspect_1", s1_prompt, os.path.join(output_folder, "scene_2_suspect_1.jpg")),
        ("suspect_2", s2_prompt, os.path.join(output_folder, "scene_3_suspect_2.jpg")),
        ("suspect_3", s3_prompt, os.path.join(output_folder, "scene_4_suspect_3.jpg")),
        ("reveal", reveal_prompt, os.path.join(output_folder, "scene_5_reveal.jpg"))
    ]

    results = {}
    print("\n[HỆ THỐNG HÌNH ẢNH] Bắt đầu khởi tạo bộ 5 ảnh AI 9:16 đồng bộ phong cách Noir Comic...")

    for key, prompt, path in targets:
        if os.path.exists(path) and os.path.getsize(path) > 10000:
            print(f"Ảnh '{key}' đã tồn tại sẵn tại: {path}")
            results[key] = path
            continue

        img_path = generate_image_pollinations(prompt, path)
        results[key] = img_path
        time.sleep(1.0)

    return results

if __name__ == "__main__":
    print("Image engine module ready.")
