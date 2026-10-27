import os
import sys
import argparse
import time

# Ensure UTF-8 output across Windows and Linux
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from script_generator import generate_script
from generate_polished_assets import generate_dynamic_assets
from download_stock_videos import prepare_scene_videos
from tts_engine import run_tts
from video_engine import render_final_short
from youtube_uploader import upload_short
from config import OUTPUT_DIR, YOUTUBE_REFRESH_TOKEN

def run_pipeline(dry_run: bool = False):
    print("=" * 60)
    print("🚀 BẮT ĐẦU QUY TRÌNH TỰ ĐỘNG SẢN XUẤT YOUTUBE SHORT 24/24")
    print("=" * 60)

    timestamp = int(time.time())
    run_output_dir = os.path.join(OUTPUT_DIR, f"run_{timestamp}")
    os.makedirs(run_output_dir, exist_ok=True)

    # 1. TẠO KỊCH BẢN VỤ ÁN MỚI TOANH BẰNG GEMINI AI
    print("\n[BƯỚC 1/5] Khởi tạo kịch bản vụ án hoàn toàn mới với Gemini AI...")
    script_data = generate_script()
    title = script_data["title"]
    description = script_data.get("description", "")
    tags = script_data.get("tags", ["Shorts", "CrimeRiddle", "Detective"])
    full_text = script_data["full_text"]

    print(f"Chủ đề vụ án: {script_data.get('topic_name')}")
    print(f"Tiêu đề YouTube: {title}")

    # 2. KHỞI TẠO BADGE NGHI PHẠM & DẤU ĐỎ GUILTY KHỚP KỊCH BẢN
    print("\n[BƯỚC 2/5] Đồ họa hóa các thẻ nghi phạm và dấu án GUILTY bằng Pillow...")
    generate_dynamic_assets(script_data)

    # 3. TẠO GIỌNG ĐỌC & DẬP PHỤ ĐỀ THEO TỪNG TỪ
    print("\n[BƯỚC 3/5] Tạo giọng đọc Edge-TTS Christopher & canh mốc thời gian...")
    audio_path = os.path.join(run_output_dir, "voice.mp3")
    subtitle_path = os.path.join(run_output_dir, "subtitles.ass")
    _, _, words = run_tts(full_text, audio_path, subtitle_path)

    # 4. CHUẨN BỊ KHO FOOTAGE 4K TỪ PIXABAY
    print("\n[BƯỚC 4/5] Đồng bộ kho video HD/4K từ Pixabay phù hợp bối cảnh...")
    script_data["stock_videos"] = prepare_scene_videos(script_data)

    # 5. RENDER VIDEO DỌC CHUẨN SHORTS BẰNG FFMPEG
    print("\n[BƯỚC 5/5] Render video 1080x1920 với chuyển cảnh, đếm ngược và dấu án...")
    final_video_path = os.path.join(run_output_dir, "final_short.mp4")
    try:
        render_final_short([], audio_path, subtitle_path, final_video_path, script_data=script_data, words_data=words)
    except Exception as e:
        import traceback
        print(f"\n❌ Lỗi khi render video: {e}")
        traceback.print_exc()
        sys.exit(1)

    # 6. UPLOAD LÊN YOUTUBE
    print("\n[XUẤT BẢN] Đăng tải lên kênh YouTube...")
    if dry_run or not YOUTUBE_REFRESH_TOKEN:
        print("Chế độ Dry-Run hoặc chưa thiết lập YOUTUBE_REFRESH_TOKEN: Bỏ qua bước upload.")
        print(f"Video đã tạo thành công và lưu tại: {final_video_path}")
        return final_video_path

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
