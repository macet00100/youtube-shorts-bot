import os
import subprocess
import math
import sys
import json
import re
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, MUSIC_DIR

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def get_audio_duration(audio_path: str) -> float:
    """Gets audio duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(result.stdout.strip())

def compute_scene_timestamps(words, suspect_keywords):
    """
    Computes exact scene split times based on Microsoft Speech WordBoundary data.
    """
    clean_words = [re.sub(r'[^a-zA-Z0-9]', '', w['text']).lower() for w in words]
    offsets = [w['offset'] / 10000000.0 for w in words]

    # 1. Find suspects
    ts_suspects = []
    for kw in suspect_keywords:
        ts = None
        for i, cw in enumerate(clean_words):
            if kw in cw:
                if i > 0 and clean_words[i-1] == 'the':
                    ts = offsets[i-1]
                else:
                    ts = offsets[i]
                break
        ts_suspects.append(ts)

    # Fallbacks if any missing
    if ts_suspects[0] is None: ts_suspects[0] = 8.0
    if ts_suspects[1] is None: ts_suspects[1] = ts_suspects[0] + 3.5
    if ts_suspects[2] is None: ts_suspects[2] = ts_suspects[1] + 3.5

    # 2. Find challenge
    ts_challenge = None
    for i, cw in enumerate(clean_words):
        if offsets[i] > ts_suspects[-1]:
            if cw in ['one', 'spot'] and i + 1 < len(clean_words) and clean_words[i+1] in ['of', 'the']:
                ts_challenge = offsets[i]
                break
    if ts_challenge is None:
        ts_challenge = ts_suspects[-1] + 3.5

    # 3. Find countdown numbers (five, four, three, two, one)
    ts_5 = None
    ts_4 = None
    ts_3 = None
    ts_2 = None
    ts_1 = None
    for i, cw in enumerate(clean_words):
        if offsets[i] > ts_challenge:
            if cw == 'five' and ts_5 is None: ts_5 = offsets[i]
            elif cw == 'four' and ts_5 and ts_4 is None: ts_4 = offsets[i]
            elif cw == 'three' and ts_4 and ts_3 is None: ts_3 = offsets[i]
            elif cw == 'two' and ts_3 and ts_2 is None: ts_2 = offsets[i]
            elif cw == 'one' and ts_2 and ts_1 is None: ts_1 = offsets[i]

    if ts_5 is None: ts_5 = ts_challenge + 5.0
    if ts_4 is None: ts_4 = ts_5 + 0.8
    if ts_3 is None: ts_3 = ts_4 + 0.6
    if ts_2 is None: ts_2 = ts_3 + 0.6
    if ts_1 is None: ts_1 = ts_2 + 0.6

    # 4. Find reveal ("it was")
    ts_reveal = None
    for i, cw in enumerate(clean_words):
        if offsets[i] > ts_1:
            if cw == 'it' and i + 1 < len(clean_words) and clean_words[i+1] == 'was':
                ts_reveal = offsets[i]
                break
    if ts_reveal is None:
        ts_reveal = ts_1 + 1.2

    return {
        "suspect_1": ts_suspects[0],
        "suspect_2": ts_suspects[1],
        "suspect_3": ts_suspects[2],
        "challenge": ts_challenge,
        "count_5": ts_5,
        "count_4": ts_4,
        "count_3": ts_3,
        "count_2": ts_2,
        "count_1": ts_1,
        "reveal": ts_reveal
    }

def validate_video_file(file_path: str) -> str:
    """Guarantees that the input file path exists and is a valid video."""
    if file_path and os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
        return file_path
    from download_stock_videos import get_stock_video_for_query
    return get_stock_video_for_query("dark storm night", "fallback_scene")

def create_cover_clip(image_path: str, duration: float, output_path: str) -> str:
    """
    Renders the opening cover / thumbnail frame (1080x1920) so that
    YouTube and short-form video players capture this exact frame as the default video thumbnail.
    """
    img = os.path.abspath(image_path).replace("\\", "/")
    filter_complex = (
        f"[0:v]loop=loop=-1:size=1:start=0,fps={FPS},"
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,settb=AVTB,setpts=PTS-STARTPTS[v]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-t", f"{duration:.3f}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-r", str(FPS),
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def create_video_clip_segment(video_path: str, badge_overlay: str, duration: float, output_path: str) -> str:
    """
    Renders a standard video segment optimized for mobile ergonomics:
    - Top Banner at y=90 (clears phone notch / top UI)
    - Suspect Card / Challenge Card at y=250
    """
    video_path = validate_video_file(video_path)
    banner = os.path.abspath("assets/riddle/riddle_banner.png").replace("\\", "/")
    vid = os.path.abspath(video_path).replace("\\", "/")

    if badge_overlay and os.path.exists(badge_overlay):
        badge = os.path.abspath(badge_overlay).replace("\\", "/")
        filter_complex = (
            f"[0:v]fps={FPS},scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base];"
            f"[base][1:v]overlay=(W-w)/2:90[v1];"
            f"[v1][2:v]overlay=(W-w)/2:250[v]"
        )
        inputs = ["-stream_loop", "-1", "-i", vid, "-loop", "1", "-i", banner, "-loop", "1", "-i", badge]
    else:
        filter_complex = (
            f"[0:v]fps={FPS},scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base];"
            f"[base][1:v]overlay=(W-w)/2:90[v]"
        )
        inputs = ["-stream_loop", "-1", "-i", vid, "-loop", "1", "-i", banner]

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-t", f"{duration:.3f}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-r", str(FPS),
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def create_live_countdown_segment(video_path: str, duration: float, output_path: str, ts_info: dict) -> str:
    """
    Renders the ACTIVE live countdown segment ticking down:
    5 -> 4 -> 3 -> 2 -> 1 in exact sync with Christopher's counting voice!
    Positioned in the prime visual focal zone at y=660.
    """
    video_path = validate_video_file(video_path)
    banner = os.path.abspath("assets/riddle/riddle_banner.png").replace("\\", "/")
    t5 = os.path.abspath("assets/riddle/timer_5.png").replace("\\", "/")
    t4 = os.path.abspath("assets/riddle/timer_4.png").replace("\\", "/")
    t3 = os.path.abspath("assets/riddle/timer_3.png").replace("\\", "/")
    t2 = os.path.abspath("assets/riddle/timer_2.png").replace("\\", "/")
    t1 = os.path.abspath("assets/riddle/timer_1.png").replace("\\", "/")
    vid = os.path.abspath(video_path).replace("\\", "/")

    t_start = ts_info["count_5"]
    d4 = max(0.2, ts_info["count_4"] - t_start)
    d3 = max(d4 + 0.2, ts_info["count_3"] - t_start)
    d2 = max(d3 + 0.2, ts_info["count_2"] - t_start)
    d1 = max(d2 + 0.2, ts_info["count_1"] - t_start)

    filter_complex = (
        f"[0:v]fps={FPS},scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base];"
        f"[base][1:v]overlay=(W-w)/2:90[v0];"
        f"[v0][2:v]overlay=(W-w)/2:660:enable='between(t,0,{d4:.2f})'[v_t5];"
        f"[v_t5][3:v]overlay=(W-w)/2:660:enable='between(t,{d4:.2f},{d3:.2f})'[v_t4];"
        f"[v_t4][4:v]overlay=(W-w)/2:660:enable='between(t,{d3:.2f},{d2:.2f})'[v_t3];"
        f"[v_t3][5:v]overlay=(W-w)/2:660:enable='between(t,{d2:.2f},{d1:.2f})'[v_t2];"
        f"[v_t2][6:v]overlay=(W-w)/2:660:enable='gte(t,{d1:.2f})'[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", vid,
        "-loop", "1", "-i", banner,
        "-loop", "1", "-i", t5,
        "-loop", "1", "-i", t4,
        "-loop", "1", "-i", t3,
        "-loop", "1", "-i", t2,
        "-loop", "1", "-i", t1,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-t", f"{duration:.3f}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-r", str(FPS),
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def create_reveal_clip(video_path: str, guilty_stamp: str, duration: float, output_path: str, guilty_badge: str = None) -> str:
    """
    Renders the dramatic revelation scene:
    Shows Top Banner at y=90 and the prominent red CASE SOLVED: GUILTY stamp centered at y=420.
    Clean, focused, cinematic, and clutter-free without overlapping duplicate cards!
    """
    video_path = validate_video_file(video_path)
    banner = os.path.abspath("assets/riddle/riddle_banner.png").replace("\\", "/")
    stamp = os.path.abspath(guilty_stamp).replace("\\", "/")
    vid = os.path.abspath(video_path).replace("\\", "/")

    filter_complex = (
        f"[0:v]fps={FPS},scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base];"
        f"[base][1:v]overlay=(W-w)/2:90[v1];"
        f"[v1][2:v]overlay=(W-w)/2:420[v]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", vid,
        "-loop", "1", "-i", banner,
        "-loop", "1", "-i", stamp,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-t", f"{duration:.3f}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-r", str(FPS),
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def render_final_short(image_paths: list, voice_audio: str, subtitle_ass: str, output_video: str, script_data: dict = None, words_data: list = None):
    """
    Renders the complete Detective Short with 100% speech-synchronized scene cuts,
    live animated countdown, and frame-perfect revelation.
    """
    os.makedirs(os.path.dirname(output_video), exist_ok=True)
    total_duration = get_audio_duration(voice_audio)
    temp_dir = os.path.dirname(output_video)

    # Load words if not provided directly
    if not words_data:
        words_json_path = subtitle_ass.replace('.ass', '_words.json')
        if os.path.exists(words_json_path):
            try:
                with open(words_json_path, 'r', encoding='utf-8') as f:
                    words_data = json.load(f)
            except Exception:
                words_data = []

    # Default fallback script metadata if None passed
    if not script_data:
        script_data = {
            "suspect_keywords": ["butler", "chef", "maid"],
            "suspect_badges": [
                "assets/riddle/badge_butler.png",
                "assets/riddle/badge_chef.png",
                "assets/riddle/badge_maid.png"
            ],
            "stock_videos": {
                "hook": "assets/stock_videos/mansion_storm.mp4",
                "suspect_1": "assets/stock_videos/butler_waiter.mp4",
                "suspect_2": "assets/stock_videos/chef_cooking.mp4",
                "suspect_3": "assets/stock_videos/rain_mail.mp4",
                "challenge": "assets/stock_videos/clock_ticking.mp4",
                "countdown": "assets/stock_videos/clock_ticking.mp4",
                "reveal": "assets/stock_videos/reveal_lightning.mp4"
            },
            "guilty_badge": "assets/riddle/badge_maid.png",
            "guilty_stamp": "assets/riddle/guilty_stamp.png"
        }

    suspect_kws = script_data.get("suspect_keywords", ["butler", "chef", "maid"])
    badges = script_data.get("suspect_badges", [
        "assets/riddle/badge_butler.png",
        "assets/riddle/badge_chef.png",
        "assets/riddle/badge_maid.png"
    ])
    stock_vids = script_data.get("stock_videos", {})
    guilty_badge = script_data.get("guilty_badge", badges[-1])
    guilty_stamp = script_data.get("guilty_stamp", "assets/riddle/guilty_stamp.png")

    # Compute exact speech-aligned transition timestamps
    if words_data:
        ts = compute_scene_timestamps(words_data, suspect_kws)
    else:
        ts = {
            "suspect_1": 8.0, "suspect_2": 11.5, "suspect_3": 15.0,
            "challenge": 19.0, "count_5": 24.0, "count_4": 24.8,
            "count_3": 25.4, "count_2": 26.0, "count_1": 26.6,
            "reveal": 28.0
        }

    t_intro = ts["suspect_1"]
    t_sus1 = ts["suspect_2"] - ts["suspect_1"]
    t_sus2 = ts["suspect_3"] - ts["suspect_2"]
    t_sus3 = ts["challenge"] - ts["suspect_3"]
    t_chal = ts["count_5"] - ts["challenge"]
    t_count = ts["reveal"] - ts["count_5"]
    t_reveal = max(total_duration - ts["reveal"], 4.0)

    print(f"Exact speech-aligned cuts: intro={t_intro:.2f}s, sus1={t_sus1:.2f}s, sus2={t_sus2:.2f}s, "
          f"sus3={t_sus3:.2f}s, chal={t_chal:.2f}s, count={t_count:.2f}s, rev={t_reveal:.2f}s (Total: {total_duration:.2f}s)")

    vid_hook = stock_vids.get("hook", "assets/stock_videos/mansion_storm.mp4")
    vid_s1 = stock_vids.get("suspect_1", "assets/stock_videos/butler_waiter.mp4")
    vid_s2 = stock_vids.get("suspect_2", "assets/stock_videos/chef_cooking.mp4")
    vid_s3 = stock_vids.get("suspect_3", "assets/stock_videos/rain_mail.mp4")
    vid_chal = stock_vids.get("challenge", "assets/stock_videos/clock_ticking.mp4")
    vid_count = stock_vids.get("countdown", "assets/stock_videos/clock_ticking.mp4")
    vid_rev = stock_vids.get("reveal", "assets/stock_videos/ocean_storm.mp4")

    seg2 = create_video_clip_segment(vid_s1, badges[0], t_sus1, os.path.join(temp_dir, "seg2.mp4"))
    seg3 = create_video_clip_segment(vid_s2, badges[1], t_sus2, os.path.join(temp_dir, "seg3.mp4"))
    seg4 = create_video_clip_segment(vid_s3, badges[2], t_sus3, os.path.join(temp_dir, "seg4.mp4"))
    seg5 = create_video_clip_segment(vid_chal, "assets/riddle/badge_challenge.png", t_chal, os.path.join(temp_dir, "seg5.mp4"))
    seg6 = create_live_countdown_segment(vid_count, t_count, os.path.join(temp_dir, "seg6.mp4"), ts)
    seg7 = create_reveal_clip(vid_rev, guilty_stamp, t_reveal, os.path.join(temp_dir, "seg7.mp4"))

    cover_thumb_file = "assets/thumbnail.png"
    if os.path.exists(cover_thumb_file) and t_intro > 2.0:
        t_cover = 0.5
        t_hook = max(0.5, t_intro - t_cover)
        seg_cover = create_cover_clip(cover_thumb_file, t_cover, os.path.join(temp_dir, "seg_cover.mp4"))
        seg1 = create_video_clip_segment(vid_hook, None, t_hook, os.path.join(temp_dir, "seg1.mp4"))
        segment_files = [seg_cover, seg1, seg2, seg3, seg4, seg5, seg6, seg7]
        print(f"🎬 Đã chèn khung hình Thumbnail bìa chính thức ({t_cover}s) làm Frame 0 cho YouTube Shorts!")
    else:
        seg1 = create_video_clip_segment(vid_hook, None, t_intro, os.path.join(temp_dir, "seg1.mp4"))
        segment_files = [seg1, seg2, seg3, seg4, seg5, seg6, seg7]

    # Background music
    bg_music_file = None
    if os.path.exists(MUSIC_DIR):
        candidates = [os.path.join(MUSIC_DIR, f) for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.wav', '.m4a'))]
        if candidates:
            bg_music_file = candidates[0]

    sub_path_escaped = os.path.abspath(subtitle_ass).replace("\\", "/").replace(":", "\\:")

    cmd = ["ffmpeg", "-y"]
    for seg in segment_files:
        cmd.extend(["-i", seg])
    
    cmd.extend(["-i", voice_audio])
    audio_input_idx = len(segment_files)

    concat_inputs = "".join([f"[{i}:v]" for i in range(len(segment_files))])
    filter_chain = f"{concat_inputs}concat=n={len(segment_files)}:v=1:a=0[v_cat]; [v_cat]ass='{sub_path_escaped}'[v]"

    if bg_music_file:
        cmd.extend(["-stream_loop", "-1", "-i", bg_music_file])
        bgm_input_idx = audio_input_idx + 1
        filter_chain += f"; [{bgm_input_idx}:a]volume=0.20[bgm]; [{audio_input_idx}:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
        cmd.extend([
            "-filter_complex", filter_chain,
            "-map", "[v]",
            "-map", "[a]"
        ])
    else:
        cmd.extend([
            "-filter_complex", filter_chain,
            "-map", "[v]",
            "-map", f"{audio_input_idx}:a"
        ])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{total_duration:.3f}",
        output_video
    ])

    print("Rendering perfectly synchronized Detective Short with FFmpeg...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"FFmpeg error: {res.stderr}")
        raise RuntimeError(f"FFmpeg render failed: {res.stderr}")

    # Clean up temp files
    for s in segment_files:
        try:
            if os.path.exists(s):
                os.remove(s)
        except Exception:
            pass

    print(f"Render completed: {output_video}")
    return output_video

if __name__ == "__main__":
    print("Video Engine ready.")
