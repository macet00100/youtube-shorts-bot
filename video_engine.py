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

def compute_scene_timestamps(words: list, suspect_keywords: list) -> dict:
    """
    Computes exact scene transition timestamps from Edge-TTS WordBoundary offsets.
    Guarantees strict forward sequence:
    hook (0.0s) -> suspect 1 -> suspect 2 -> suspect 3 -> challenge -> count 3 -> count 2 -> count 1 -> reveal.
    """
    clean_words = [re.sub(r'[^a-zA-Z0-9]', '', w['text']).lower() for w in words]
    offsets = [w['offset'] / 10000000.0 for w in words]

    # 1. Sequential search for 3 suspects
    ts_suspects = []
    last_idx = 0
    prev_ts = 3.2

    for kw in suspect_keywords:
        kw_clean = kw.lower().strip()
        ts = None
        match_idx = None
        for i in range(last_idx, len(clean_words)):
            cw = clean_words[i]
            if kw_clean in cw or (len(kw_clean) > 4 and cw.startswith(kw_clean[:4])):
                cand_ts = offsets[i-1] if (i > 0 and clean_words[i-1] in ['the', 'suspect']) else offsets[i]
                if cand_ts >= prev_ts + 1.8:
                    ts = cand_ts
                    match_idx = i
                    break

        if ts is not None and match_idx is not None:
            ts_suspects.append(ts)
            prev_ts = ts
            last_idx = match_idx + 1
        else:
            fallback_ts = prev_ts + 2.8
            ts_suspects.append(fallback_ts)
            prev_ts = fallback_ts

    # 2. Challenge sentence ("one is", "spot", "killer", "lying")
    ts_challenge = None
    chal_idx = None
    for i in range(last_idx, len(clean_words)):
        cw = clean_words[i]
        if cw in ['one', 'spot', 'liar', 'killer', 'lying'] and offsets[i] >= prev_ts + 1.8:
            ts_challenge = offsets[i]
            chal_idx = i
            break

    if ts_challenge is None:
        ts_challenge = prev_ts + 2.8
        last_idx = len(clean_words)
    else:
        last_idx = chal_idx + 1
    prev_ts = ts_challenge

    # 3. 3-Second Countdown ("three", "two", "one")
    ts_3 = None
    ts_2 = None
    ts_1 = None
    for i in range(last_idx, len(clean_words)):
        cw = clean_words[i]
        off = offsets[i]
        if off > prev_ts:
            if cw == 'three' and ts_3 is None:
                ts_3 = off
            elif cw == 'two' and ts_3 and ts_2 is None:
                ts_2 = off
            elif cw == 'one' and ts_2 and ts_1 is None:
                ts_1 = off
                last_idx = i + 1

    if ts_3 is None: ts_3 = prev_ts + 2.2
    if ts_2 is None: ts_2 = ts_3 + 0.65
    if ts_1 is None: ts_1 = ts_2 + 0.65
    prev_ts = ts_1

    # 4. Reveal ("it was")
    ts_reveal = None
    for i in range(last_idx, len(clean_words)):
        cw = clean_words[i]
        if cw == 'it' and (i + 1 < len(clean_words) and clean_words[i+1] == 'was'):
            if offsets[i] >= prev_ts:
                ts_reveal = offsets[i]
                break

    if ts_reveal is None:
        ts_reveal = prev_ts + 0.85

    return {
        "suspect_1": max(3.2, ts_suspects[0]),
        "suspect_2": max(ts_suspects[0] + 2.0, ts_suspects[1]),
        "suspect_3": max(ts_suspects[1] + 2.0, ts_suspects[2]),
        "challenge": max(ts_suspects[2] + 2.0, ts_challenge),
        "count_3": max(ts_challenge + 1.8, ts_3),
        "count_2": ts_2,
        "count_1": ts_1,
        "reveal": max(ts_1 + 0.65, ts_reveal)
    }

def create_kenburns_segment(image_path: str, badge_overlay: str, duration: float, output_path: str, motion_type: str = "zoom_in") -> str:
    """
    Renders an individual scene video clip with smooth Ken Burns camera motion and
    YouTube Shorts Safe Zone compliant overlays:
    - Top Banner at y=120 (clearing 100px status bar)
    - Alibi Card at y=290 (centered, 70px side margins)
    """
    banner = os.path.abspath("assets/riddle/riddle_banner.png").replace("\\", "/")
    img = os.path.abspath(image_path).replace("\\", "/")
    d = max(0.5, duration)

    if motion_type == "zoom_in":
        kb_filter = f"fps={FPS},scale=w='{VIDEO_WIDTH}*(1+0.07*t/{d:.3f})':h='{VIDEO_HEIGHT}*(1+0.07*t/{d:.3f})':eval=frame,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(in_w-{VIDEO_WIDTH})/2:(in_h-{VIDEO_HEIGHT})/2,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base]"
    elif motion_type == "pan_right":
        scale_w = int(VIDEO_WIDTH * 1.08)
        scale_h = int(VIDEO_HEIGHT * 1.08)
        kb_filter = f"fps={FPS},scale={scale_w}:{scale_h},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:'({scale_w}-{VIDEO_WIDTH})*(t/{d:.3f})':'({scale_h}-{VIDEO_HEIGHT})/2',setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base]"
    elif motion_type == "pan_left":
        scale_w = int(VIDEO_WIDTH * 1.08)
        scale_h = int(VIDEO_HEIGHT * 1.08)
        kb_filter = f"fps={FPS},scale={scale_w}:{scale_h},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:'({scale_w}-{VIDEO_WIDTH})*(1-t/{d:.3f})':'({scale_h}-{VIDEO_HEIGHT})/2',setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base]"
    else:
        kb_filter = f"fps={FPS},scale=w='{VIDEO_WIDTH}*(1+0.06*t/{d:.3f})':h='{VIDEO_HEIGHT}*(1+0.06*t/{d:.3f})':eval=frame,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(in_w-{VIDEO_WIDTH})/2:(in_h-{VIDEO_HEIGHT})/2,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base]"

    if badge_overlay and os.path.exists(badge_overlay):
        badge = os.path.abspath(badge_overlay).replace("\\", "/")
        filter_complex = (
            f"[0:v]{kb_filter};"
            f"[base][1:v]overlay=(W-w)/2:120[v1];"
            f"[v1][2:v]overlay=(W-w)/2:290[v]"
        )
        inputs = ["-loop", "1", "-i", img, "-loop", "1", "-i", banner, "-loop", "1", "-i", badge]
    else:
        filter_complex = (
            f"[0:v]{kb_filter};"
            f"[base][1:v]overlay=(W-w)/2:120[v]"
        )
        inputs = ["-loop", "1", "-i", img, "-loop", "1", "-i", banner]

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-t", f"{d:.3f}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-r", str(FPS),
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def create_lineup_countdown_segment(bg_image: str, lineup_screen: str, duration: float, output_path: str, ts_info: dict) -> str:
    """
    Renders the SUSPECT LINEUP screen with active 3-second live countdown (3 -> 2 -> 1).
    Safe Zone compliant:
    - Banner at y=120
    - Lineup Screen (940x600) at y=290
    - Timer (460x170) at y=920 (centered, 310px margin clearing 150px right buttons!)
    """
    banner = os.path.abspath("assets/riddle/riddle_banner.png").replace("\\", "/")
    lineup = os.path.abspath(lineup_screen).replace("\\", "/")
    t3 = os.path.abspath("assets/riddle/timer_3.png").replace("\\", "/")
    t2 = os.path.abspath("assets/riddle/timer_2.png").replace("\\", "/")
    t1 = os.path.abspath("assets/riddle/timer_1.png").replace("\\", "/")
    bg = os.path.abspath(bg_image).replace("\\", "/")

    d = max(2.5, duration)
    t_start = ts_info.get("count_3", 0.0)
    d2 = max(0.35, ts_info.get("count_2", t_start + 0.65) - t_start)
    d1 = max(d2 + 0.35, ts_info.get("count_1", t_start + 1.30) - t_start)

    kb_filter = f"fps={FPS},scale=w='{VIDEO_WIDTH}*(1+0.04*t/{d:.3f})':h='{VIDEO_HEIGHT}*(1+0.04*t/{d:.3f})':eval=frame,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(in_w-{VIDEO_WIDTH})/2:(in_h-{VIDEO_HEIGHT})/2,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base]"

    filter_complex = (
        f"[0:v]{kb_filter};"
        f"[base][1:v]overlay=(W-w)/2:120[v0];"
        f"[v0][2:v]overlay=(W-w)/2:290[v_lineup];"
        f"[v_lineup][3:v]overlay=(W-w)/2:920:enable='between(t,0,{d2:.2f})'[v_t3];"
        f"[v_t3][4:v]overlay=(W-w)/2:920:enable='between(t,{d2:.2f},{d1:.2f})'[v_t2];"
        f"[v_t2][5:v]overlay=(W-w)/2:920:enable='gte(t,{d1:.2f})'[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", bg,
        "-loop", "1", "-i", banner,
        "-loop", "1", "-i", lineup,
        "-loop", "1", "-i", t3,
        "-loop", "1", "-i", t2,
        "-loop", "1", "-i", t1,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-t", f"{d:.3f}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-r", str(FPS),
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def create_reveal_segment(reveal_image: str, guilty_stamp: str, duration: float, output_path: str) -> str:
    """
    Renders the dramatic revelation scene:
    Slow zoom-in on the evidence with CASE SOLVED: GUILTY stamp at y=340.
    Ends sharply without lingering delay.
    """
    banner = os.path.abspath("assets/riddle/riddle_banner.png").replace("\\", "/")
    stamp = os.path.abspath(guilty_stamp).replace("\\", "/")
    img = os.path.abspath(reveal_image).replace("\\", "/")
    d = max(1.5, duration)

    kb_filter = f"fps={FPS},scale=w='{VIDEO_WIDTH}*(1+0.10*t/{d:.3f})':h='{VIDEO_HEIGHT}*(1+0.10*t/{d:.3f})':eval=frame,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(in_w-{VIDEO_WIDTH})/2:(in_h-{VIDEO_HEIGHT})/2,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[base]"

    filter_complex = (
        f"[0:v]{kb_filter};"
        f"[base][1:v]overlay=(W-w)/2:120[v1];"
        f"[v1][2:v]overlay=(W-w)/2:340[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img,
        "-loop", "1", "-i", banner,
        "-loop", "1", "-i", stamp,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-t", f"{d:.3f}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-r", str(FPS),
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def render_final_short(scene_images: dict, voice_audio: str, subtitle_ass: str, output_video: str, script_data: dict = None, words_data: list = None):
    """
    Renders the complete 22-28 second Detective Short with:
    1. Zero intro delay (starts immediately at 0.0s on the Hook scene).
    2. 5 AI scene illustrations with smooth Ken Burns pan/zoom.
    3. 3-second live countdown on the Suspect Lineup screen.
    4. Crisp, decisive reveal with CASE SOLVED: GUILTY stamp.
    5. Safe Zone compliant layout avoiding bottom 320px and right 150px.
    """
    os.makedirs(os.path.dirname(output_video), exist_ok=True)
    total_duration = get_audio_duration(voice_audio)
    temp_dir = os.path.dirname(output_video)

    if not words_data:
        words_json_path = subtitle_ass.replace('.ass', '_words.json')
        if os.path.exists(words_json_path):
            try:
                with open(words_json_path, 'r', encoding='utf-8') as f:
                    words_data = json.load(f)
            except Exception:
                words_data = []

    suspect_kws = script_data.get("suspect_keywords", ["first", "second", "third"])
    badges = script_data.get("suspect_badges", [
        "assets/riddle/badge_suspect_1.png",
        "assets/riddle/badge_suspect_2.png",
        "assets/riddle/badge_suspect_3.png"
    ])
    guilty_stamp = script_data.get("guilty_stamp", "assets/riddle/guilty_stamp.png")

    if words_data:
        ts = compute_scene_timestamps(words_data, suspect_kws)
    else:
        ts = {
            "suspect_1": 3.8, "suspect_2": 6.8, "suspect_3": 9.8,
            "challenge": 12.8, "count_3": 15.8, "count_2": 16.5,
            "count_1": 17.2, "reveal": 18.2
        }

    t_hook = max(ts["suspect_1"], 3.2)
    t_sus1 = max(ts["suspect_2"] - ts["suspect_1"], 2.0)
    t_sus2 = max(ts["suspect_3"] - ts["suspect_2"], 2.0)
    t_sus3 = max(ts["challenge"] - ts["suspect_3"], 2.0)
    t_count = max(ts["reveal"] - ts["challenge"], 2.8)
    t_reveal = max(total_duration - ts["reveal"], 3.0)

    print(f"🎬 Scene cuts (Total audio: {total_duration:.2f}s): "
          f"Hook={t_hook:.2f}s, Sus1={t_sus1:.2f}s, Sus2={t_sus2:.2f}s, "
          f"Sus3={t_sus3:.2f}s, Countdown={t_count:.2f}s, Reveal={t_reveal:.2f}s")

    img_hook = scene_images.get("hook")
    img_s1 = scene_images.get("suspect_1")
    img_s2 = scene_images.get("suspect_2")
    img_s3 = scene_images.get("suspect_3")
    img_rev = scene_images.get("reveal", img_hook)

    # 1. Hook Scene (0.0s immediately, slow zoom-in)
    seg1 = create_kenburns_segment(img_hook, None, t_hook, os.path.join(temp_dir, "seg1.mp4"), motion_type="zoom_in")

    # 2. Suspect 1 (Pan right)
    seg2 = create_kenburns_segment(img_s1, badges[0], t_sus1, os.path.join(temp_dir, "seg2.mp4"), motion_type="pan_right")

    # 3. Suspect 2 (Pan left)
    seg3 = create_kenburns_segment(img_s2, badges[1], t_sus2, os.path.join(temp_dir, "seg3.mp4"), motion_type="pan_left")

    # 4. Suspect 3 (Zoom in)
    seg4 = create_kenburns_segment(img_s3, badges[2], t_sus3, os.path.join(temp_dir, "seg4.mp4"), motion_type="zoom_in")

    # 5. Suspect Lineup + 3-Second Countdown
    lineup_path = "assets/riddle/suspect_lineup.png"
    seg5 = create_lineup_countdown_segment(img_hook, lineup_path, t_count, os.path.join(temp_dir, "seg5.mp4"), ts)

    # 6. Reveal + CASE SOLVED: GUILTY stamp
    seg6 = create_reveal_segment(img_rev, guilty_stamp, t_reveal, os.path.join(temp_dir, "seg6.mp4"))

    segment_files = [seg1, seg2, seg3, seg4, seg5, seg6]

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
        filter_chain += f"; [{bgm_input_idx}:a]volume=0.18[bgm]; [{audio_input_idx}:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
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

    print("Rendering final Detective Short with FFmpeg...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"FFmpeg error: {res.stderr}")
        raise RuntimeError(f"FFmpeg render failed: {res.stderr}")

    for s in segment_files:
        try:
            if os.path.exists(s):
                os.remove(s)
        except Exception:
            pass

    print(f"✅ Render thành công video Shorts hoàn chỉnh: {output_video}")
    return output_video

if __name__ == "__main__":
    print("Video Engine ready.")
