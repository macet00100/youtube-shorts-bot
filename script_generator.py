import json
import os
import sys
import random
import re
import difflib
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import GEMINI_API_KEY, HISTORY_FILE

GEMINI_MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]

def call_gemini_api(payload: dict, timeout: int = 35) -> dict:
    """Calls Gemini API with automatic model fallback and retry on 503/429."""
    last_err = None
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(2):
            try:
                resp = requests.post(url, json=payload, timeout=timeout)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code in [503, 429, 500]:
                    import time
                    time.sleep(1.5)
                    continue
                else:
                    resp.raise_for_status()
            except Exception as e:
                last_err = e
                import time
                time.sleep(1.0)
    raise RuntimeError(f"All Gemini models failed: {last_err}")

# Unified Art Style applied across all scenes
BASE_ART_STYLE = (
    "moody noir detective comic illustration, dark cinematic graphic novel art style, "
    "dramatic rim lighting, high contrast shadows, detailed textures, 9:16 vertical composition"
)

# ==============================================================================
# PROCEDURAL DIMENSION MATRIX (SOPHISTICATED EVERYDAY DETECTIVE RIDDLES)
# ==============================================================================

SETTINGS_POOL = [
    # High-Tech & Science
    {"name": "Cleanroom Semiconductor Foundry", "category": "tech_science", "role_hint": "Laser Tech, Senior Chemist, Cleanroom Operator"},
    {"name": "Cryogenic Quantum Server Vault", "category": "tech_science", "role_hint": "Cryo Engineer, Systems Admin, Security Officer"},
    {"name": "Deep-Sea Submarine Laboratory", "category": "tech_science", "role_hint": "Navigator, Marine Biologist, Sonar Operator"},
    {"name": "High-Altitude Astronomical Observatory", "category": "tech_science", "role_hint": "Astronomer, Lens Polisher, Night Guard"},

    # Luxury, Arts & Antiquities
    {"name": "Stradivarius Violin Atelier", "category": "arts_luxury", "role_hint": "Master Luthier, Wood Varnisher, Museum Curator"},
    {"name": "Venetian Glassblowing Workshop", "category": "arts_luxury", "role_hint": "Master Glassblower, Furnace Keeper, Gallery Dealer"},
    {"name": "Ancient Manuscript Archives Vault", "category": "arts_luxury", "role_hint": "Head Archivist, Paper Conservator, Bookbinder"},
    {"name": "High-Security Diamond Cutting Guild", "category": "arts_luxury", "role_hint": "Gem Appraiser, Diamond Cutter, Vault Guard"},

    # Extreme Expeditions & Weather
    {"name": "Arctic Glaciology Research Camp", "category": "expedition", "role_hint": "Glaciologist, Station Mechanic, Drone Pilot"},
    {"name": "Active Volcano Caldera Lab", "category": "expedition", "role_hint": "Volcanologist, Seismologist, Thermal Tech"},
    {"name": "Himalayan Alpine Basecamp", "category": "expedition", "role_hint": "Expedition Leader, Mountain Guide, Meteorologist"},

    # Urban Mystery & Everyday Settings
    {"name": "Historic Grand Hotel Penthouse", "category": "urban", "role_hint": "Head Butler, Private Chef, Night Concierge"},
    {"name": "24-Hour Industrial Laundromat", "category": "urban", "role_hint": "Night Attendant, Shift Cleaner, Delivery Driver"},
    {"name": "Downtown Photography Darkroom Studio", "category": "urban", "role_hint": "Master Photographer, Darkroom Tech, Framing Assistant"},
    {"name": "Vintage 1980s Neon Bowling Lounge", "category": "urban", "role_hint": "Pinsetter Mechanic, Lane Manager, Bartender"},
    {"name": "Harbor Fog Horn Lighthouse", "category": "urban", "role_hint": "Lighthouse Keeper, Harbor Pilot, Radio Operator"}
]

ATMOSPHERES_POOL = [
    "Sudden midnight blackout under dim emergency amber lighting",
    "Dense morning fog at 06:00 AM with freezing frost",
    "Heavy torrential rainstorm rattling high windows",
    "Late evening twilight as sunset fades to darkness",
    "Crisp sub-zero winter midnight at -15°C with fresh snowfall",
    "Scorching midday heatwave with blinding harsh sunlight"
]

# Realistic, subtle everyday contradictions (NO childish or inverted physics)
CONTRADICTIONS_POOL = [
    # 1. Blackouts & Electrical Appliances
    {
        "core": "Claimed to read the digital oven clock or microwave display during a sudden power blackout",
        "explanation": "Digital LED appliance clocks turn completely dark during a power blackout!",
        "categories": ["urban", "arts_luxury", "tech_science"],
        "banned_words": ["digital clock", "blackout clock"]
    },
    {
        "core": "Claimed to brew coffee in the electric machine or fetch ice from the electric dispenser during the building's power outage",
        "explanation": "Electric kitchen appliances and motorized ice dispensers do not function during an outage!",
        "categories": ["urban", "arts_luxury", "tech_science"],
        "banned_words": ["electric coffee", "blackout ice"]
    },

    # 2. Window Reflections vs Pitch Darkness
    {
        "core": "Claimed they stood inside a brightly lit room looking through a window and clearly saw someone moving in the pitch-black unlit yard",
        "explanation": "Looking through glass from a brightly lit room into pitch darkness shows only interior reflections, not the dark outside!",
        "categories": ["all"],
        "banned_words": ["window dark", "reflection yard"]
    },

    # 3. Sunlight Angles & Shadows
    {
        "core": "Claimed their shadow pointed towards the West while standing on the terrace during morning sunrise at 6:00 AM",
        "explanation": "At sunrise the sun is in the East, so shadows always fall directly towards the West (away from the sun)!",
        "categories": ["all"],
        "banned_words": ["shadow sunrise"]
    },
    {
        "core": "Claimed their shadow pointed towards the East while walking outside during evening sunset at 7:00 PM",
        "explanation": "At sunset the sun is in the West, so shadows always point towards the East, away from the sun!",
        "categories": ["all"],
        "banned_words": ["shadow sunset"]
    },

    # 4. Fresh Weather, Snow, Heat & Footprints
    {
        "core": "Claimed they drove their car from 20 miles away and parked outside 5 minutes ago, but the car hood was covered in thick undisturbed frost",
        "explanation": "An engine driven 20 miles stays hot and immediately melts hood frost!",
        "categories": ["urban", "expedition"],
        "banned_words": ["car frost", "engine snow"]
    },
    {
        "core": "Claimed they ran across the open garden to check the shed during the midnight snowstorm, but the fresh snow showed zero footprints",
        "explanation": "Walking across fresh snowfall leaves obvious visible footprints!",
        "categories": ["expedition", "urban", "arts_luxury"],
        "banned_words": ["snow footprint", "tracks"]
    },
    {
        "core": "Claimed they were stranded outside in the heavy torrential downpour, but their jacket and hair were completely bone dry",
        "explanation": "Walking in a heavy downpour immediately soaks fabric and hair!",
        "categories": ["all"],
        "banned_words": ["rain dry", "bone dry"]
    },

    # 5. Acoustic & Lightning Physics
    {
        "core": "Claimed they heard the thunder rumble several seconds before seeing the flash of lightning in the sky",
        "explanation": "Light travels nearly a million times faster than sound, so lightning is ALWAYS seen before thunder!",
        "categories": ["all"],
        "banned_words": ["thunder before lightning"]
    },

    # 6. Thermal Shock & Chemistry Disguised Naturally
    {
        "core": "Claimed they washed a scorching red-hot glass beaker or baking dish directly under freezing cold tap water without cracking it",
        "explanation": "Severe thermal shock immediately shatters scorching hot glass!",
        "categories": ["arts_luxury", "tech_science", "urban"],
        "banned_words": ["hot glass water", "thermal shock"]
    },
    {
        "core": "Claimed to drink from a steaming hot mug of tea that had been sitting on the outdoor metal railing at -20°C for 30 minutes",
        "explanation": "In sub-zero temperatures and wind, hot liquids cool down and freeze within minutes!",
        "categories": ["expedition", "urban"],
        "banned_words": ["steaming tea freezing"]
    },

    # 7. Professional Protocol & Cleanroom Rules
    {
        "core": "Claimed they opened the exterior window to air out the pressurized semiconductor cleanroom",
        "explanation": "Cleanrooms are hermetically sealed positive-pressure chambers where opening windows is strictly impossible!",
        "categories": ["tech_science"],
        "banned_words": ["cleanroom window"]
    },
    {
        "core": "Claimed they took a photo with flash inside the film development darkroom while photos were processing",
        "explanation": "White flash light instantly ruins undeveloped photographic paper in a darkroom!",
        "categories": ["urban"],
        "banned_words": ["darkroom flash"]
    }
]

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

def extract_core_keywords(text: str) -> set:
    stopwords = {
        "this", "that", "with", "from", "were", "been", "have", "what", "when", "where",
        "which", "there", "their", "about", "would", "could", "should", "murder", "mystery",
        "crime", "riddle", "shorts", "killer", "suspect", "alibi", "reason", "midnight", "grand"
    }
    words = re.findall(r'[a-zA-Z]{4,}', text.lower())
    return {w for w in words if w not in stopwords}

def clean_topic_for_comparison(text: str) -> str:
    stopwords_pattern = r'\b(murder|mystery|crime|riddle|shorts|the|and|of|in|at|on|for|case|solved)\b'
    cleaned = re.sub(stopwords_pattern, '', text.lower())
    return re.sub(r'\s+', ' ', cleaned).strip()

def check_is_duplicate(new_script: dict, history: list) -> tuple[bool, str]:
    """Strict check against history to prevent topic, setting, title, or contradiction repetition."""
    if not history:
        return False, ""

    new_topic = new_script.get("topic_name", "").strip()
    new_title = new_script.get("title", "").strip().lower()
    new_reason = new_script.get("culprit_reason", "").strip().upper()

    # Reject duplicate titles
    for h in history:
        past_title = h.get("title", "").strip().lower()
        if past_title and (new_title == past_title or difflib.SequenceMatcher(None, new_title, past_title).ratio() > 0.85):
            return True, f"Title too similar to previous upload: '{h.get('title')}'"

    clean_new_topic = clean_topic_for_comparison(new_topic)

    # Check topic names
    for h in history:
        past_topic = h.get("topic_name", "").strip()
        clean_past_topic = clean_topic_for_comparison(past_topic)
        if new_topic.lower() == past_topic.lower() or (clean_new_topic and clean_new_topic == clean_past_topic):
            return True, f"Exact topic match with history: '{past_topic}'"

    # Check recent 20 videos
    recent_history = history[-20:] if len(history) > 20 else history
    for h in recent_history:
        past_topic = h.get("topic_name", "").strip()
        past_reason = h.get("culprit_reason", "").strip().upper()
        clean_past_topic = clean_topic_for_comparison(past_topic)

        sim_topic = difflib.SequenceMatcher(None, clean_new_topic, clean_past_topic).ratio()
        if sim_topic > 0.65:
            return True, f"Topic similarity too high ({sim_topic:.2f}) with recent: '{past_topic}'"

        if past_reason and new_reason:
            sim_reason = difflib.SequenceMatcher(None, new_reason, past_reason).ratio()
            if sim_reason > 0.70:
                return True, f"Contradiction reason similarity too high ({sim_reason:.2f}) with recent: '{past_reason}'"

    return False, ""

# ==============================================================================
# STEP 1: GENERATOR (SUBTLE & BELIEVABLE EVERYDAY DETECTIVE RIDDLE)
# ==============================================================================

def generate_script_draft(history: list, chosen_setting: dict, chosen_atmosphere: str, chosen_contradiction: dict, target_culprit_idx: int) -> dict:
    history_topics = [h.get("topic_name", "") for h in history if h.get("topic_name")]
    recent_topics_str = ", ".join(history_topics[-25:]) if history_topics else "None"

    system_prompt = f"""
You are an expert detective mystery creator for 24-second viral YouTube Shorts.
Target audience: Smart global viewers who love clever, subtle crime mysteries.

MANDATORY CRIME RIDDLE SPECIFICATIONS:
1. SETTING: "{chosen_setting['name']}". Characters: {chosen_setting.get('role_hint')}.
2. SITUATION & TIME: "{chosen_atmosphere}".
3. GUILTY CULPRIT: Suspect {target_culprit_idx} is the ONLY guilty person.
   - FATAL FLAW: Suspect {target_culprit_idx}'s alibi MUST hinge on this contradiction: "{chosen_contradiction['core']}".
   - NATURAL HUMAN EXCUSE: Suspect {target_culprit_idx}'s lie MUST sound completely natural and innocent on the surface (e.g. checking an appliance, looking outside, walking across the yard, parking a car, working on equipment).
   - STRICT BAN: Absolutely FORBIDDEN to use obvious textbook physics cliches (DO NOT say "smoke sank down", "stones sank in water", "ice melted", "whisper over loud machines"). The clue must feel like a real detective mystery!
   - The other two suspects MUST have airtight, realistic, and completely innocent alibis.

4. ULTRA-CRISP SCRIPT LENGTH (MANDATORY: 54 to 64 words total for 23-27s duration):
   - Hook: EXACTLY 9 to 12 words setting up the murder.
   - Suspect 1: EXACTLY 7 to 10 words stating their alibi naturally.
   - Suspect 2: EXACTLY 7 to 10 words stating their alibi naturally.
   - Suspect 3: EXACTLY 7 to 10 words stating their alibi naturally.
   - Challenge line: EXACTLY "One is lying. Spot the killer before time runs out! Three, two, one!" (13 words).
   - Reveal: EXACTLY 10 to 14 words explaining the fatal clue. Starts with "It was the [Role]! [Crisp explanation]!"
   TOTAL WORD COUNT MUST BE STRICTLY UNDER 66 WORDS!

5. CASE-SPECIFIC TITLE: Must be unique, under 50 characters, specific to this case and setting.
   Format: "The [Setting] Murder Mystery 🔍 #Shorts" or "Who Killed the [Role]? 🕵️ #Shorts".

6. VISUAL PROMPTS (5 SCENES): Cohesive art style: "{BASE_ART_STYLE}". No text in prompt.

OUTPUT STRICT JSON ONLY:
{{
  "topic_name": "Unique Case Name (e.g. Darkroom Cyanide Mystery)",
  "title": "Case-Specific Title Under 50 Chars #Shorts",
  "description": "Can you spot the fatal lie before the countdown ends? Comment your answer below!\\n\\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
  "setting_theme": "{chosen_setting['name']}",
  "contradiction_core": "{chosen_contradiction['core'][:60]}",
  "full_text": "Complete spoken text from Hook through Reveal (52 to 58 words)",
  "suspect_1": {{
    "role": "ROLE 1 (e.g. THE ARCHIVIST)",
    "title": "1. THE ARCHIVIST",
    "alibi": "Spoken alibi sentence (7 to 10 words)",
    "card_text": "Claim: Short 5-7 word summary.",
    "speech_keyword": "unique single lowercase word present in full_text for suspect 1",
    "image_prompt": "Visual prompt for suspect 1, no text"
  }},
  "suspect_2": {{
    "role": "ROLE 2 (e.g. THE BOOKBINDER)",
    "title": "2. THE BOOKBINDER",
    "alibi": "Spoken alibi sentence (7 to 10 words)",
    "card_text": "Claim: Short 5-7 word summary.",
    "speech_keyword": "unique single lowercase word present in full_text for suspect 2",
    "image_prompt": "Visual prompt for suspect 2, no text"
  }},
  "suspect_3": {{
    "role": "ROLE 3 (e.g. THE APPRENTICE)",
    "title": "3. THE APPRENTICE",
    "alibi": "Spoken alibi sentence (7 to 10 words)",
    "card_text": "Claim: Short 5-7 word summary.",
    "speech_keyword": "unique single lowercase word present in full_text for suspect 3",
    "image_prompt": "Visual prompt for suspect 3, no text"
  }},
  "culprit_role": "ROLE OF SUSPECT {target_culprit_idx}",
  "culprit_speech_keyword": "speech_keyword of suspect {target_culprit_idx}",
  "culprit_reason": "REASON: {chosen_contradiction['explanation'].upper()}",
  "scene_prompts": {{
    "hook": "Visual prompt for crime scene in setting, no text",
    "suspect_1": "Visual prompt for suspect 1 in setting, no text",
    "suspect_2": "Visual prompt for suspect 2 in setting, no text",
    "suspect_3": "Visual prompt for suspect 3 in setting, no text",
    "reveal": "Visual prompt for evidence close-up in setting, no text"
  }}
}}
"""

    payload = {
        "contents": [{"parts": [{"text": system_prompt}]}],
        "generationConfig": {
            "temperature": 0.85,
            "responseMimeType": "application/json"
        }
    }

    data = call_gemini_api(payload, timeout=35)
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return json.loads(raw_text)

# ==============================================================================
# STEP 2: STRICT LOGIC & SUBTLETY CRITIC
# ==============================================================================

def evaluate_logic_with_gemini(script_data: dict) -> dict:
    """
    Independent Gemini evaluation step acting as a skeptical Senior Detective.
    Evaluates both Scientific Accuracy (1-10) and Subtlety/Naturalness (1-10).
    Rejects childishly obvious clues or unnatural statements.
    """
    topic = script_data.get("topic_name", "")
    setting = script_data.get("setting_theme", "")
    s1 = script_data.get("suspect_1", {})
    s2 = script_data.get("suspect_2", {})
    s3 = script_data.get("suspect_3", {})
    culprit_role = script_data.get("culprit_role", "")
    reason = script_data.get("culprit_reason", "")
    full_text = script_data.get("full_text", "")
    word_count = len(full_text.split())

    critic_prompt = f"""
You are a skeptical Senior Detective and Riddle Quality Critic.
Review this 24-second detective crime riddle.

CASE UNDER REVIEW:
- Topic: {topic}
- Setting: {setting}
- Suspect 1 ({s1.get('role')}): "{s1.get('alibi')}"
- Suspect 2 ({s2.get('role')}): "{s2.get('alibi')}"
- Suspect 3 ({s3.get('role')}): "{s3.get('alibi')}"
- Accused Culprit: {culprit_role}
- Contradiction Reason: {reason}
- Full Script: "{full_text}" (Words: {word_count})

EVALUATION CRITERIA:
1. SCIENTIFIC & LOGICAL ACCURACY (1-10): Is the contradiction 100% indisputable based on physics, weather, optics, or real facts?
2. SUBTLETY & NATURALNESS (1-10): Does the culprit's statement sound like a natural, believable human excuse?
   - REJECT (score < 7) if the clue is childishly obvious (e.g. stones sink, smoke sinks, whisper over 10 machines).
   - REJECT (score < 7) if the suspect sounds like they deliberately recited an inverted textbook physics formula.
   - The alibi MUST be disguised as a normal everyday action that subtly betrays the lie.
3. UNIQUENESS OF GUILT: Is there EXACTLY ONE guilty suspect with 2 completely innocent suspects?
4. SCRIPT DURATION TIGHTNESS: Is word count between 50 and 66 words (mandatory for 22-27s audio)?

Return strict JSON:
{{
  "valid": true/false,
  "accuracy_score": 1-10,
  "subtlety_score": 1-10,
  "overall_score": 1-10,
  "critique": "Brief 1-sentence assessment of logic and subtlety",
  "refined_reason": "Refined 1-sentence uppercase contradiction reason"
}}
"""

    payload = {
        "contents": [{"parts": [{"text": critic_prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    try:
        data = call_gemini_api(payload, timeout=25)
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        critic_result = json.loads(raw_text)
        return critic_result
    except Exception as e:
        print(f"⚠️ Logic Critic call warning: {e}. Falling back to rule-based validation.")
        is_valid = (48 <= word_count <= 62) and bool(culprit_role) and bool(reason)
        return {
            "valid": is_valid,
            "accuracy_score": 8 if is_valid else 5,
            "subtlety_score": 8 if is_valid else 5,
            "overall_score": 8 if is_valid else 5,
            "critique": "Rule-based validation passed.",
            "refined_reason": reason
        }

# ==============================================================================
# MAIN ORCHESTRATION PIPELINE
# ==============================================================================

def generate_script_with_ai(history: list, max_attempts: int = 4) -> dict:
    """
    2-Step Gemini generation:
    1. Generator creates riddle with strict duration & subtle everyday alibis.
    2. Strict Logic Critic verifies accuracy (>=7) AND subtlety (>=7).
    """
    recent_history = history[-20:] if len(history) > 20 else history
    used_keywords = set()
    for h in recent_history:
        used_keywords.update(extract_core_keywords(h.get("topic_name", "")))
        if h.get("culprit_reason"):
            used_keywords.update(extract_core_keywords(h.get("culprit_reason", "")))

    available_settings = [
        s for s in SETTINGS_POOL
        if not extract_core_keywords(s["name"]).intersection(used_keywords)
    ]
    if not available_settings:
        available_settings = SETTINGS_POOL

    for attempt in range(1, max_attempts + 1):
        chosen_setting = random.choice(available_settings)
        chosen_atmosphere = random.choice(ATMOSPHERES_POOL)

        compatible_contradictions = [
            c for c in CONTRADICTIONS_POOL
            if ("all" in c["categories"] or chosen_setting["category"] in c["categories"])
            and not any(bw in " ".join(used_keywords) for bw in c["banned_words"])
        ]
        if not compatible_contradictions:
            compatible_contradictions = [
                c for c in CONTRADICTIONS_POOL
                if "all" in c["categories"] or chosen_setting["category"] in c["categories"]
            ]

        chosen_contradiction = random.choice(compatible_contradictions)
        target_culprit_idx = random.choice([1, 2, 3])

        print(f"\n[BƯỚC 1/2: GENERATOR #{attempt}] Bối cảnh: '{chosen_setting['name']}' | Manh mối: '{chosen_contradiction['core'][:45]}...'")

        try:
            draft = generate_script_draft(history, chosen_setting, chosen_atmosphere, chosen_contradiction, target_culprit_idx)

            # Check history duplication
            is_dup, dup_reason = check_is_duplicate(draft, history)
            if is_dup:
                print(f"⚠️ Trùng lặp lịch sử ({dup_reason}). Đổi bối cảnh...")
                continue

            # Check word count strictly for 22-28s total video duration (50-68 words at +16% speed)
            word_count = len(draft.get("full_text", "").split())
            if word_count < 50 or word_count > 68:
                print(f"⚠️ Số từ không tối ưu ({word_count} từ, cần 52-66 từ để đạt chuẩn 22-27s). Thử lại...")
                continue

            # Ensure title length < 50 chars
            title = draft.get("title", "")
            if len(title) > 50:
                short_title = re.sub(r'\s*#Shorts.*$', '', title)[:38].strip()
                draft["title"] = f"{short_title} #Shorts"

            # Step 2: Strict Logic & Subtlety Critic
            print(f"[BƯỚC 2/2: LOGIC & SUBTLETY CRITIC] Thẩm định độ chính xác và tính tự nhiên của lời khai...")
            critique = evaluate_logic_with_gemini(draft)
            acc_score = critique.get("accuracy_score", critique.get("overall_score", 0))
            sub_score = critique.get("subtlety_score", critique.get("overall_score", 0))
            print(f"   -> Điểm Chính xác: {acc_score}/10 | Điểm Tinh tế: {sub_score}/10 | Duyệt: {critique.get('valid')}")
            print(f"   -> Đánh giá: {critique.get('critique')}")

            # Reject if inaccurate, obvious, or invalid
            if not critique.get("valid") or acc_score < 7 or sub_score < 7:
                print(f"⚠️ Kịch bản bị từ chối do quá lộ liễu hoặc thiếu chặt chẽ ({critique.get('critique')}). Tạo lại kịch bản mới...")
                continue

            if critique.get("refined_reason"):
                draft["culprit_reason"] = critique["refined_reason"]

            draft["logic_score"] = critique.get("overall_score", 8)
            draft["logic_critique"] = critique.get("critique", "Approved")

            # Validate scene prompts exist without text
            if "scene_prompts" not in draft or not all(k in draft["scene_prompts"] for k in ["hook", "suspect_1", "suspect_2", "suspect_3", "reveal"]):
                draft["scene_prompts"] = {
                    "hook": f"Crime scene at {chosen_setting['name']}, mysterious atmosphere, {BASE_ART_STYLE}",
                    "suspect_1": f"{draft['suspect_1'].get('role')} at {chosen_setting['name']}, {BASE_ART_STYLE}",
                    "suspect_2": f"{draft['suspect_2'].get('role')} at {chosen_setting['name']}, {BASE_ART_STYLE}",
                    "suspect_3": f"{draft['suspect_3'].get('role')} at {chosen_setting['name']}, {BASE_ART_STYLE}",
                    "reveal": f"Close-up of evidence flaw at {chosen_setting['name']}, {BASE_ART_STYLE}"
                }

            print(f"✅ Kịch bản sắc sảo đã được duyệt: '{draft.get('topic_name')}' | Tiêu đề: '{draft.get('title')}'")
            return draft

        except Exception as e:
            print(f"Lỗi ở lượt tạo {attempt}: {e}")

    raise RuntimeError("Gemini AI failed to produce a verified script within the maximum attempts.")

def generate_script():
    """Generates a dynamic non-duplicating Short script with 2-step AI pipeline and fallback safety."""
    history = load_history()

    if GEMINI_API_KEY:
        try:
            print("Đang khởi động Quy trình 2 bước (Generator + Strict Logic & Subtlety Critic)...")
            script_data = generate_script_with_ai(history)

            # Map into standard pipeline structure
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
            script_data["guilty_stamp"] = "assets/riddle/guilty_stamp.png"

            # Record in history
            history.append({
                "topic_name": script_data.get("topic_name", "AI Crime Riddle"),
                "title": script_data.get("title", ""),
                "setting_theme": script_data.get("setting_theme", ""),
                "culprit_role": script_data.get("culprit_role", ""),
                "culprit_reason": script_data.get("culprit_reason", ""),
                "logic_score": script_data.get("logic_score", 8),
                "generated_at": str(os.getenv("GITHUB_RUN_ID", "local_ai"))
            })
            save_history(history)
            return script_data
        except Exception as e:
            print(f"Lỗi khi gọi Gemini AI: {e}. Kích hoạt Kho kịch bản độc bản dự phòng...")

    from script_generator_fallback import get_fallback_script
    return get_fallback_script(history)

if __name__ == "__main__":
    s = generate_script()
    print("\n--- KỊCH BẢN ĐÃ TẠO THÀNH CÔNG ---")
    print(f"Topic: {s.get('topic_name')}")
    print(f"Title: {s.get('title')} (Length: {len(s.get('title', ''))} chars)")
    print(f"Culprit: {s.get('culprit_role')}")
    print(f"Reason: {s.get('culprit_reason')}")
    print(f"Words ({len(s.get('full_text', '').split())}): {s.get('full_text')}")
