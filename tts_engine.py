import asyncio
import os
import json
import re
import edge_tts
from config import DEFAULT_VOICE

def format_timestamp_ass(seconds: float) -> str:
    """Converts seconds float to ASS timestamp format H:MM:SS.cs"""
    if seconds < 0:
        seconds = 0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        secs += 1
        centis = 0
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def build_perfect_subtitles(orig_text: str, words: list) -> str:
    """
    Builds 100% synchronized, perfectly punctuated ASS subtitles.
    Never crosses sentence boundaries. Exact word timings from Microsoft Speech AI.
    Shifts start by -40ms to eliminate voice-leading lag.
    Positioned in the mobile golden reading zone (MarginV: 430, MarginL/R: 120).
    """
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,110,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,10,5,2,120,120,430,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    if not words:
        return ass_header

    orig_tokens = orig_text.split()
    chunks = []
    idx = 0
    n = len(words)

    while idx < n:
        w1 = words[idx]
        orig_w1 = orig_tokens[idx] if idx < len(orig_tokens) else w1["text"]
        s1 = w1["offset"] / 10000000.0
        e1 = (w1["offset"] + w1["duration"]) / 10000000.0

        has_terminal = bool(re.search(r'[.!?]$', orig_w1))
        has_comma = bool(re.search(r'[,;:]$', orig_w1))

        # Single word chunk if punctuation ends clause or sentence
        if has_terminal or has_comma:
            chunks.append((s1, e1, orig_w1))
            idx += 1
            continue

        if idx + 1 < n:
            w2 = words[idx + 1]
            orig_w2 = orig_tokens[idx + 1] if idx + 1 < len(orig_tokens) else w2["text"]
            e2 = (w2["offset"] + w2["duration"]) / 10000000.0
            clean1 = re.sub(r'[^a-zA-Z0-9\']', '', orig_w1)
            clean2 = re.sub(r'[^a-zA-Z0-9\']', '', orig_w2)

            if len(clean1) + len(clean2) <= 15:
                chunks.append((s1, e2, f"{orig_w1} {orig_w2}"))
                idx += 2
            else:
                chunks.append((s1, e1, orig_w1))
                idx += 1
        else:
            chunks.append((s1, e1, orig_w1))
            idx += 1

    for c_idx, (start_sec, end_sec, text) in enumerate(chunks):
        color = '&H0000FFFF&' if (c_idx % 2 == 0) else '&H00FFFFFF&'
        clean_text = text.upper().strip(" .,;:").replace('{', '').replace('}', '')

        # Give voice a crisp 40ms visual lead to kill audio lag
        display_start = max(0.0, start_sec - 0.04)
        padded_end = end_sec + 0.04
        if c_idx + 1 < len(chunks):
            next_start = chunks[c_idx + 1][0] - 0.04
            padded_end = min(padded_end, max(display_start + 0.1, next_start - 0.01))

        start_str = format_timestamp_ass(display_start)
        end_str = format_timestamp_ass(padded_end)
        events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{{\\c{color}}}{clean_text}")

    return ass_header + "\n".join(events) + "\n"

async def generate_speech_and_subtitles(text: str, output_audio: str, output_ass: str, voice: str = DEFAULT_VOICE):
    """
    Generates audio, frame-perfect synchronized subtitles, and word boundary timestamps.
    """
    os.makedirs(os.path.dirname(output_audio), exist_ok=True)
    os.makedirs(os.path.dirname(output_ass), exist_ok=True)

    communicate = edge_tts.Communicate(text=text, voice=voice, rate="+6%", boundary="WordBoundary")
    words = []

    with open(output_audio, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append(chunk)

    ass_content = build_perfect_subtitles(text, words)

    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(ass_content)

    words_json_path = output_ass.replace('.ass', '_words.json')
    with open(words_json_path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f"Audio saved to: {output_audio}")
    print(f"Subtitles saved to: {output_ass} ({len(words)} exact words tracked, perfect punctuation)")
    return output_audio, output_ass, words

def run_tts(text: str, output_audio: str, output_ass: str, voice: str = DEFAULT_VOICE):
    return asyncio.run(generate_speech_and_subtitles(text, output_audio, output_ass, voice))

if __name__ == "__main__":
    sample_text = "A billionaire was murdered on a peaceful Sunday afternoon in his locked mansion."
    run_tts(sample_text, "output/test_voice.mp3", "output/test_sub.ass")
