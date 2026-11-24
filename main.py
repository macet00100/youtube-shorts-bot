import os
import sys
import argparse
import time

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from script_generator import generate_script
from generate_polished_assets import generate_dynamic_assets
from image_engine import generate_scene_images
from tts_engine import run_tts
from video_engine import render_final_short, get_audio_duration
from youtube_uploader import upload_short
from config import OUTPUT_DIR, YOUTUBE_REFRESH_TOKEN

def run_pipeline(dry_run: bool = False):
    print("=" * 65)
    print("🚀 BẮT ĐẦU QUY TRÌNH TỰ ĐỘNG SẢN XUẤT YOUTUBE SHORTS (PHIÊN BẢN MỚI)")
    print("=" * 65)

    timestamp = int(time.time())
    run_output_dir = os.path.join(OUTPUT_DIR, f"run_{timestamp}")
    os.makedirs(run_output_dir, exist_ok=True)

    # 1. TẠO KỊCH BẢN ĐỘC BẢN & KIỂM DUYỆT LOGIC VỚI GEMINI AI
    print("\n[BƯỚC 1/5] Khởi tạo kịch bản vụ án 2 bước (Generator + Strict Logic Critic)...")
    script_data = generate_script()
    title = script_data.get("title", "Who Is The Killer? 🕵️ #Shorts")
    description = script_data.get("description", "")
    tags = script_data.get("tags", ["Shorts", "CrimeRiddle", "Detective"])
    full_text = script_data.get("full_text", "")

    print(f"📌 Bối cảnh vụ án: {script_data.get('setting_theme', script_data.get('topic_name'))}")
    print(f"📌 Tiêu đề YouTube độc bản ({len(title)} ký tự): {title}")
    print(f"📌 Thủ phạm: {script_data.get('culprit_role')}")
    print(f"📌 Manh mối logic: {script_data.get('culprit_reason')}")
    print(f"📌 Tổng số từ: {len(full_text.split())} từ")

    # 2. ĐỒ HỌA HÓA CÁC THẺ LỜI KHAI, MÀN HÌNH ĐẾM NGƯỢC 3 NGHI PHẠM & DẤU ÁN GUILTY
    print("\n[BƯỚC 2/5] Tạo thẻ lời khai, màn hình tổng hợp 3 nghi phạm và dấu GUILTY bằng Pillow...")
    generate_dynamic_assets(script_data)

    # 3. TẠO GIỌNG ĐỌC NHANH (+13%), CẮT KHOẢNG LẶNG & DẬP PHỤ ĐỀ CHUẨN
    print("\n[BƯỚC 3/5] Tạo giọng đọc Edge-TTS Christopher (+13%) & canh mốc thời gian...")
    audio_path = os.path.join(run_output_dir, "voice.mp3")
    subtitle_path = os.path.join(run_output_dir, "subtitles.ass")
    _, _, words = run_tts(full_text, audio_path, subtitle_path)

    audio_dur = get_audio_duration(audio_path)
    print(f"⏱️ Thời lượng audio giọng đọc: {audio_dur:.2f}s (Mục tiêu video: 22-28s)")

    # 4. TẠO BỘ 5 ẢNH 9:16 ĐỒNG BỘ PHONG CÁCH NOIR DETECTIVE COMIC
    print("\n[BƯỚC 4/5] Khởi tạo bộ 5 ảnh 9:16 đồng bộ phong cách nghệ thuật Noir Comic...")
    scene_images = generate_scene_images(script_data, run_output_dir)

    # 5. RENDER VIDEO VỚI CHUYỂN ĐỘNG KEN BURNS & MÀN HÌNH ĐẾM NGƯỢC 3S
    print("\n[BƯỚC 5/5] Render video 1080x1920 chuyển động Ken Burns và màn hình đếm ngược 3s...")
    final_video_path = os.path.join(run_output_dir, "final_short.mp4")
    try:
        render_final_short(
            scene_images=scene_images,
            voice_audio=audio_path,
            subtitle_ass=subtitle_path,
            output_video=final_video_path,
            script_data=script_data,
            words_data=words
        )
    except Exception as e:
        import traceback
        print(f"\n❌ Lỗi khi render video: {e}")
        traceback.print_exc()
        sys.exit(1)

    final_dur = get_audio_duration(final_video_path)
    print(f"🎉 RENDER HOÀN TẤT! Video dài: {final_dur:.2f}s | Lưu tại: {final_video_path}")

    # 6. UPLOAD LÊN YOUTUBE
    print("\n[XUẤT BẢN] Đăng tải lên kênh YouTube Shorts...")
    if dry_run or not YOUTUBE_REFRESH_TOKEN:
        print("ℹ️ Chế độ Dry-Run hoặc chưa thiết lập YOUTUBE_REFRESH_TOKEN: Bỏ qua bước upload.")
        print(f"👉 File video Shorts hoàn chỉnh đã sẵn sàng tại: {final_video_path}")
        return {
            "video_path": final_video_path,
            "duration": final_dur,
            "script_data": script_data,
            "title": title,
            "description": description,
            "scene_images": scene_images
        }

    try:
        video_id = upload_short(final_video_path, title, description, tags, privacy_status="public")
        print(f"\n🎉 HOÀN TẤT TOÀN BỘ QUY TRÌNH! Video ID: {video_id}")
        return video_id
    except Exception as e:
        print(f"\n❌ Lỗi khi upload YouTube: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation Bot")
    parser.add_argument("--dry-run", action="store_true", help="Render video without uploading to YouTube")
    args = parser.parse_args()

    run_pipeline(dry_run=args.dry_run)
