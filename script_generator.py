import json
import os
import sys
import random
import re
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import GEMINI_API_KEY, HISTORY_FILE

GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def generate_script_with_ai(recent_topics: list) -> dict:
    """Calls Gemini to generate a brand new, non-repeating crime mystery riddle."""
    topics_str = ", ".join(recent_topics[-30:]) if recent_topics else "None"

    # Randomly assign the culprit to Suspect 1, Suspect 2, or Suspect 3 with equal probability
    target_culprit_idx = random.choice([1, 2, 3])

    system_prompt = f"""
You are a viral YouTube Shorts creator specializing in interactive "30-SECOND CRIME RIDDLES & DETECTIVE MYSTERIES" (Targeting Global US/UK English Audience).
Format Concept: "CAN YOU SPOT THE KILLER IN 10 SECONDS?"

CRITICAL INSTRUCTION - ZERO DUPLICATION:
You MUST create a completely brand-new, unique crime mystery scenario that has NEVER been done before.
Do NOT use or repeat any of these previously used topics: [{topics_str}].

MANDATORY CULPRIT ASSIGNMENT (ANTI-REPETITION):
In this episode, the GUILTY CULPRIT MUST BE SUSPECT {target_culprit_idx}!
- Suspect {target_culprit_idx} MUST be the one who has the physical or logical lie in their alibi.
- The other two suspects MUST have completely innocent, airtight alibis.
- "culprit_role" MUST be identical to Suspect {target_culprit_idx}'s role!
- (Do NOT always choose Suspect 3! Respect Suspect {target_culprit_idx} as the culprit!).

Strict Formula for 150%+ Retention (Watch-Time + Replay):
1. LENGTH: Exactly 75 to 90 spoken English words (30 to 35 seconds spoken).
2. STRUCTURE:
   - Seconds 0-8 (CRIME HOOK): A murder mystery setup in a specific setting (e.g. ancient art museum, snowy ski chalet, locked penthouse, high-speed train, space observatory, underwater research lab, luxury casino, grand opera theater).
   - Seconds 8-19 (THE 3 SUSPECTS): 3 suspects with concise alibis. Exactly ONE suspect has an obvious logical or physical contradiction (e.g. shadow pointing wrong direction, ice melting before freezing, steam on cold drink, window wiping during blizzard, sunbathing at night, watering flowers in freezing sub-zero blizzard, fresh paint dried instantly, reading book pages 100 and 101 facing each other).
   - Seconds 19-24 (CHALLENGE): "One of them is lying. Spot the killer before the timer runs out! Five, four, three, two, one..."
   - Seconds 24-34 (REVELATION & LOOP): "It was the [Role]! [Explain exact contradiction in 1 crisp sentence]! Did you solve it? Comment YES or NO!"

OUTPUT FORMAT: Strict valid JSON only:
{{
  "topic_name": "Unique Topic Name",
  "title": "Who Is The Killer? 95% Fail This Riddle! #Shorts",
  "description": "Can you solve this crime mystery in 10 seconds? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
  "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
  "setting_query": "pixabay video search keyword for scene 1 (e.g. museum night, snow chalet, dark train)",
  "full_text": "Complete spoken voiceover text from start to end (75-90 words)",
  "suspect_1": {{
    "role": "THE BUTLER",
    "title": "SUSPECT 1: THE BUTLER",
    "alibi": "ALIBI: Polishing silverware in the kitchen.",
    "search_keyword": "waiter silverware",
    "speech_keyword": "butler"
  }},
  "suspect_2": {{
    "role": "THE CHEF",
    "title": "SUSPECT 2: THE CHEF",
    "alibi": "ALIBI: Baking pastries in the oven.",
    "search_keyword": "chef cooking",
    "speech_keyword": "chef"
  }},
  "suspect_3": {{
    "role": "THE GARDENER",
    "title": "SUSPECT 3: THE GARDENER",
    "alibi": "ALIBI: Watering roses outside in freezing blizzard.",
    "search_keyword": "gardener outdoor",
    "speech_keyword": "gardener"
  }},
  "culprit_role": "THE GARDENER",
  "culprit_speech_keyword": "gardener",
  "culprit_reason": "REASON: WATER FREEZES INSTANTLY IN SUB-ZERO BLIZZARD!"
}}
"""

    payload = {
        "contents": [{"parts": [{"text": system_prompt}]}],
        "generationConfig": {
            "temperature": 0.95,
            "responseMimeType": "application/json"
        }
    }

    response = requests.post(GEMINI_URL, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return json.loads(raw_text)

def generate_script():
    """Generates a dynamic non-duplicating Short script using Gemini AI."""
    history = load_history()
    recent_topics = [h.get("topic_name", "") for h in history if h.get("topic_name")]

    if GEMINI_API_KEY:
        try:
            print("Đang kết nối Gemini AI để tự động sinh kịch bản vụ án hoàn toàn mới...")
            script_data = generate_script_with_ai(recent_topics)
            
            # Map into standard pipeline format
            script_data["suspect_keywords"] = [
                script_data["suspect_1"].get("speech_keyword", "first"),
                script_data["suspect_2"].get("speech_keyword", "second"),
                script_data["suspect_3"].get("speech_keyword", "third")
            ]
            script_data["suspect_badges"] = [
                "assets/riddle/badge_suspect_1.png",
                "assets/riddle/badge_suspect_2.png",
                "assets/riddle/badge_suspect_3.png"
            ]
            culprit_role_u = script_data.get("culprit_role", "").upper()
            s1_role_u = script_data.get("suspect_1", {}).get("role", "").upper()
            s2_role_u = script_data.get("suspect_2", {}).get("role", "").upper()
            if culprit_role_u in s1_role_u or s1_role_u in culprit_role_u:
                script_data["guilty_badge"] = "assets/riddle/badge_suspect_1.png"
            elif culprit_role_u in s2_role_u or s2_role_u in culprit_role_u:
                script_data["guilty_badge"] = "assets/riddle/badge_suspect_2.png"
            else:
                script_data["guilty_badge"] = "assets/riddle/badge_suspect_3.png"
            script_data["guilty_stamp"] = "assets/riddle/guilty_stamp.png"

            # Record in history
            history.append({
                "topic_name": script_data.get("topic_name", "AI Crime Riddle"),
                "title": script_data.get("title", ""),
                "generated_at": str(os.getenv("GITHUB_RUN_ID", "local_ai"))
            })
            save_history(history)
            print(f"Kịch bản mới đã tạo: '{script_data.get('topic_name')}' (Thủ phạm: {script_data.get('culprit_role')})")
            return script_data
        except Exception as e:
            print(f"Lỗi khi gọi Gemini AI: {e}. Đang dùng chế độ xoay tua kịch bản dự phòng...")

    # Fallback rotation if AI fails or no key
    from script_generator_fallback import get_fallback_script
    return get_fallback_script(history)

if __name__ == "__main__":
    s = generate_script()
    print("Script Generated:")
    print(json.dumps(s, ensure_ascii=False, indent=2))
