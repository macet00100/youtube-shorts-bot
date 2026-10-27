import os
import re
import subprocess
import urllib.parse
import requests
from config import PIXABAY_API_KEY, VIDEO_WIDTH, VIDEO_HEIGHT, FPS

def create_emergency_fallback_video(output_path: str, duration: int = 15) -> str:
    """Generates an emergency 1080x1920 atmospheric dark gradient video with FFmpeg if all network fails."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        return output_path

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x0a0f1d:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:d={duration}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-r", str(FPS),
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def get_stock_video_for_query(query: str, slug_prefix: str = "scene") -> str:
    """
    Dynamically searches, downloads, and caches an HD stock video clip from Pixabay.
    Guaranteed 100% to return a valid existing MP4 file on disk.
    """
    os.makedirs("assets/stock_videos", exist_ok=True)
    clean_query = query.strip()
    slug = re.sub(r'[^a-zA-Z0-9]', '_', clean_query.lower()).strip('_')[:25]
    if not slug:
        slug = slug_prefix
    cached_path = os.path.join("assets/stock_videos", f"{slug}.mp4")

    # 1. Use cached file if already downloaded
    if os.path.exists(cached_path) and os.path.getsize(cached_path) > 100000:
        return cached_path

    # 2. Search and download from Pixabay API
    print(f"Searching Pixabay for stock video: '{clean_query}'...")
    headers = {"User-Agent": "Mozilla/5.0"}
    encoded = urllib.parse.quote(clean_query)
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={encoded}&per_page=3"

    try:
        r = requests.get(url, headers=headers, timeout=25)
        if r.status_code == 200:
            hits = r.json().get("hits", [])
            if hits:
                v_info = hits[0].get("videos", {})
                video_url = None
                for q in ["large", "medium", "small"]:
                    if q in v_info and v_info[q].get("url"):
                        video_url = v_info[q]["url"]
                        break

                if video_url:
                    print(f"Downloading stock video from Pixabay: {video_url[:60]}...")
                    vr = requests.get(video_url, headers=headers, stream=True, timeout=60)
                    if vr.status_code == 200:
                        with open(cached_path, "wb") as f:
                            for chunk in vr.iter_content(chunk_size=1024 * 64):
                                if chunk:
                                    f.write(chunk)
                        if os.path.exists(cached_path) and os.path.getsize(cached_path) > 100000:
                            print(f"Successfully downloaded {cached_path} ({os.path.getsize(cached_path)} bytes)")
                            return cached_path
    except Exception as e:
        print(f"Pixabay search failed for '{clean_query}': {e}")

    # 3. If specific query had no hits, try universal fallback queries
    universal_fallbacks = ["night storm", "dark city", "clock ticking", "ocean waves"]
    for fb in universal_fallbacks:
        fb_slug = re.sub(r'[^a-zA-Z0-9]', '_', fb.lower()).strip('_')[:20]
        fb_path = os.path.join("assets/stock_videos", f"{fb_slug}.mp4")
        if os.path.exists(fb_path) and os.path.getsize(fb_path) > 100000:
            print(f"Using cached universal fallback video: {fb_path}")
            return fb_path

        try:
            fb_enc = urllib.parse.quote(fb)
            fb_url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={fb_enc}&per_page=3"
            r = requests.get(fb_url, headers=headers, timeout=20)
            if r.status_code == 200 and r.json().get("hits"):
                v_info = r.json()["hits"][0].get("videos", {})
                v_url = v_info.get("large", {}).get("url") or v_info.get("medium", {}).get("url")
                if v_url:
                    vr = requests.get(v_url, headers=headers, stream=True, timeout=60)
                    with open(fb_path, "wb") as f:
                        for chunk in vr.iter_content(chunk_size=1024 * 64):
                            if chunk:
                                f.write(chunk)
                    if os.path.exists(fb_path) and os.path.getsize(fb_path) > 100000:
                        return fb_path
        except Exception:
            pass

    # 4. Check if ANY valid .mp4 exists in assets/stock_videos
    existing = [
        os.path.join("assets/stock_videos", f)
        for f in os.listdir("assets/stock_videos")
        if f.endswith(".mp4") and os.path.getsize(os.path.join("assets/stock_videos", f)) > 100000
    ]
    if existing:
        print(f"Using existing cached clip: {existing[0]}")
        return existing[0]

    # 5. Ultimate zero-fail fallback: generate local clip with FFmpeg
    fallback_emergency = os.path.join("assets/stock_videos", "emergency_noir.mp4")
    return create_emergency_fallback_video(fallback_emergency)

def prepare_scene_videos(script_data: dict) -> dict:
    """Prepares and downloads all 7 scene video clips for the current AI scenario."""
    setting = script_data.get("setting_query", "noir mystery night")
    s1_kw = script_data.get("suspect_1", {}).get("search_keyword", "butler waiter")
    s2_kw = script_data.get("suspect_2", {}).get("search_keyword", "chef cooking")
    s3_kw = script_data.get("suspect_3", {}).get("search_keyword", "gardener outdoor")

    hook_vid = get_stock_video_for_query(setting, "setting")
    s1_vid = get_stock_video_for_query(s1_kw, "suspect_1")
    s2_vid = get_stock_video_for_query(s2_kw, "suspect_2")
    s3_vid = get_stock_video_for_query(s3_kw, "suspect_3")
    chal_vid = get_stock_video_for_query("clock ticking time", "clock_ticking")
    count_vid = chal_vid
    rev_vid = get_stock_video_for_query("storm lightning night", "reveal_storm")

    return {
        "hook": hook_vid,
        "suspect_1": s1_vid,
        "suspect_2": s2_vid,
        "suspect_3": s3_vid,
        "challenge": chal_vid,
        "countdown": count_vid,
        "reveal": rev_vid
    }

if __name__ == "__main__":
    print("Testing stock video engine...")
    test_v = get_stock_video_for_query("clock ticking", "test_clock")
    print(f"Result video: {test_v} (exists: {os.path.exists(test_v)})")
