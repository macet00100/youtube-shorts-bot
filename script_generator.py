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

# Unified Art Style applied across all scenes for visual consistency
BASE_ART_STYLE = (
    "moody noir detective comic illustration, dark cinematic graphic novel art style, "
    "dramatic rim lighting, high contrast shadows, detailed textures, 9:16 vertical composition"
)

# ==============================================================================
# PROCEDURAL DIMENSION MATRIX
# ==============================================================================

SETTINGS_POOL = [
    # High-Tech & Space
    {"name": "Mars Habitat Bio-Dome", "category": "tech_space", "role_hint": "Commander, Astrobiologist, System Engineer"},
    {"name": "Deep-Sea Submarine Laboratory", "category": "tech_space", "role_hint": "Captain, Sonar Tech, Marine Biologist"},
    {"name": "Cryogenic Quantum Server Vault", "category": "tech_space", "role_hint": "Data Architect, Cryo Engineer, Security Lead"},
    {"name": "Cleanroom Semiconductor Foundry", "category": "tech_space", "role_hint": "Laser Tech, Chemist, Quality Inspector"},
    {"name": "Subterranean Particle Accelerator", "category": "tech_space", "role_hint": "Physicist, Magnet Engineer, Radiation Officer"},
    {"name": "Orbital Space Station Cupola", "category": "tech_space", "role_hint": "Flight Engineer, Payload Specialist, Pilot"},

    # Wild Nature & Extreme Expeditions
    {"name": "Sahara Desert Archaeological Dig", "category": "expedition", "role_hint": "Archaeologist, Cartographer, Drone Operator"},
    {"name": "Himalayan High-Altitude Basecamp", "category": "expedition", "role_hint": "Expedition Leader, Sherpa Guide, Meteorologist"},
    {"name": "Amazon Canopy Research Station", "category": "expedition", "role_hint": "Botanist, Entomologist, Field Medic"},
    {"name": "Active Volcano Caldera Lab", "category": "expedition", "role_hint": "Volcanologist, Seismologist, Thermal Tech"},
    {"name": "Arctic Ice Core Drilling Camp", "category": "expedition", "role_hint": "Glaciologist, Drill Mechanic, Camp Cook"},
    {"name": "Deep Ocean Geothermal Vent Rig", "category": "expedition", "role_hint": "Geochemist, Submersible Pilot, Rig Engineer"},

    # Historic Arts & Artisanal Craft
    {"name": "Venetian Glassblowing Furnace", "category": "art_craft", "role_hint": "Master Glassblower, Furnace Keeper, Apprentice"},
    {"name": "Stradivarius Violin Workshop", "category": "art_craft", "role_hint": "Master Luthier, Wood Varnisher, Curator"},
    {"name": "Renaissance Clock Tower Gear Room", "category": "art_craft", "role_hint": "Horologist, Tower Keeper, Bellringer"},
    {"name": "Ancient Manuscript Archives Vault", "category": "art_craft", "role_hint": "Head Archivist, Paper Conservator, Translator"},
    {"name": "Historic Antique Mirror Atelier", "category": "art_craft", "role_hint": "Silvering Artisan, Frame Restorer, Valuer"},
    {"name": "Broadway Theater Prop Wardrobe", "category": "art_craft", "role_hint": "Costume Designer, Stage Carpenter, Lighting Tech"},

    # Luxury & High Society
    {"name": "Monaco Formula Pit Garage", "category": "luxury", "role_hint": "Chief Mechanic, Tire Strategist, Telemetry Engineer"},
    {"name": "Supersonic Private Jet Cabin", "category": "luxury", "role_hint": "Private Pilot, Flight Attendant, Co-Pilot"},
    {"name": "High-Security Diamond Cutting Guild", "category": "luxury", "role_hint": "Master Gemologist, Laser Cutter, Vault Guard"},
    {"name": "Michelin 3-Star Omakase Counter", "category": "luxury", "role_hint": "Head Chef, Sous Chef, Sake Sommelier"},
    {"name": "Royal Thoroughbred Equestrian Stables", "category": "luxury", "role_hint": "Head Trainer, Equine Vet, Stable Hand"},
    {"name": "Swiss Private Vault Sanctuary", "category": "luxury", "role_hint": "Bank Manager, Locksmith, Security Officer"},

    # Quirky Urban & Everyday Mystery
    {"name": "Vintage 1980s Neon Bowling Alley", "category": "urban", "role_hint": "Pinsetter Mechanic, Lane Attendant, Bartender"},
    {"name": "24-Hour Industrial Laundromat", "category": "urban", "role_hint": "Night Attendant, Dry Cleaner, Delivery Driver"},
    {"name": "Skyscraper Rooftop Honeybee Apiary", "category": "urban", "role_hint": "Urban Beekeeper, Building Engineer, Rooftop Gardener"},
    {"name": "Underground Metro Central Signal Box", "category": "urban", "role_hint": "Train Dispatcher, Signal Tech, Track Inspector"},
    {"name": "Harbor Lighthouse Lantern Room", "category": "urban", "role_hint": "Lighthouse Keeper, Harbor Pilot, Coast Guard"},
    {"name": "Vintage Vinyl Record Pressing Plant", "category": "urban", "role_hint": "Mastering Engineer, Press Operator, QA Tester"}
]

ATMOSPHERES_POOL = [
    "Scorching Midday Sun at 42°C under an open sky",
    "Dense Morning Fog at 06:00 AM with near-zero visibility",
    "Heavy Torrential Rainstorm with lightning flashes",
    "Quiet Mid-Afternoon with pale sunlight streaming through high windows",
    "Crisp Winter Dawn with fresh morning frost at -15°C",
    "Late Evening Twilight as darkness settles in",
    "Sudden Midnight Blackout under dim emergency amber lighting",
    "Roaring Windstorm rattling exterior windows",
    "Sultry Humid Tropical Dusk before a sudden storm",
    "Deep Chilly Night under an overcast moonless sky"
]

CONTRADICTIONS_POOL = [
    # Thermodynamics & States of Matter
    {"core": "Claiming dry ice blocks melted into a puddle of liquid water (dry ice sublimates directly into CO2 gas)", "categories": ["all"], "banned_words": ["dry ice"]},
    {"core": "Claiming water boiled at 120°C on an open stove at high mountain altitude (water boils at lower temperature under lower atmospheric pressure)", "categories": ["expedition"], "banned_words": ["boil", "altitude"]},
    {"core": "Claiming liquid candle wax froze solid instantaneously while touching an active blazing iron stove", "categories": ["art_craft", "urban", "expedition"], "banned_words": ["wax", "candle"]},
    {"core": "Claiming warm smoke flowed downward toward the floor like liquid in still room air (warm smoke is buoyant and rises)", "categories": ["all"], "banned_words": ["smoke sink", "smoke flow"]},

    # Optics, Light & Shadows
    {"core": "Claiming their shadow pointed directly toward the primary spotlight instead of falling away", "categories": ["all"], "banned_words": ["shadow"]},
    {"core": "Claiming to see a vivid colorful rainbow inside a windowless room or at night without direct sunlight and mist", "categories": ["all"], "banned_words": ["rainbow"]},
    {"core": "Claiming to see clear reflections on a glass window while standing in pitch-black darkness outside", "categories": ["all"], "banned_words": ["reflection", "mirror"]},
    {"core": "Claiming a sundial cast a sharp readable shadow during a dark torrential overcast rainstorm", "categories": ["expedition", "art_craft", "urban"], "banned_words": ["sundial"]},

    # Chemistry, Materials & Physics
    {"core": "Claiming to retrieve pure 24-karat solid gold using an ordinary magnetic retriever tool (pure gold is non-magnetic)", "categories": ["luxury", "art_craft", "urban", "expedition"], "banned_words": ["magnet", "gold"]},
    {"core": "Claiming traditional oil varnish or oil paint dried rock-hard in 5 minutes (oil finishes require hours or days to cure)", "categories": ["art_craft", "luxury", "urban"], "banned_words": ["oil paint", "varnish"]},
    {"core": "Claiming coarse table salt dissolved into a jar of pure vegetable oil (salt dissolves in polar water, not non-polar oil)", "categories": ["luxury", "expedition", "urban"], "banned_words": ["salt dissolve", "oil"]},
    {"core": "Claiming freshly sliced apples remained pure snow-white after sitting 6 hours in open air (raw apple enzymes oxidize and turn brown)", "categories": ["all"], "banned_words": ["apple white", "oxidize"]},
    {"core": "Claiming ordinary steel scissors cleanly cut a genuine raw diamond in half (diamonds are hardness 10 and cannot be cut by steel)", "categories": ["luxury", "art_craft", "urban"], "banned_words": ["cut diamond"]},

    # Sound & Pressure
    {"core": "Claiming to hear a faint whisper clearly over the deafening 100-decibel roar of operating heavy engines", "categories": ["luxury", "urban", "tech_space"], "banned_words": ["whisper", "engine"]},
    {"core": "Claiming to hear vocal human cries traveling from open water through the sealed pressurized hull of a submerged submarine", "categories": ["tech_space"], "banned_words": ["hull scream", "submarine voice"]},
    {"core": "Claiming to hear thunder rumble several seconds before seeing the lightning flash (light travels nearly a million times faster than sound)", "categories": ["all"], "banned_words": ["thunder before"]},

    # Biology & Environment
    {"core": "Claiming honeybees were actively swarming and foraging outside during a torrential freezing downpour (bees stay inside hives during rain and cold)", "categories": ["urban", "expedition"], "banned_words": ["bees rain", "swarm"]},
    {"core": "Claiming an ordinary open match burned bright inside a sealed airtight vacuum decompression chamber without oxygen", "categories": ["tech_space"], "banned_words": ["match vacuum", "candle vacuum"]}
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
    new_topic_words = extract_core_keywords(clean_new_topic)

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
# STEP 1: GENERATE RIDDLE SCRIPT WITH STRICT DURATION CONSTRAINTS
# ==============================================================================

def generate_script_draft(history: list, chosen_setting: dict, chosen_atmosphere: str, chosen_contradiction: dict, target_culprit_idx: int) -> dict:
    history_topics = [h.get("topic_name", "") for h in history if h.get("topic_name")]
    recent_topics_str = ", ".join(history_topics[-25:]) if history_topics else "None"

    system_prompt = f"""
You are an award-winning YouTube Shorts detective mystery creator.
Produce an ultra-crisp, 24-SECOND interactive detective riddle targeting global English audiences.

MANDATORY SPECIFICATIONS:
1. SETTING: "{chosen_setting['name']}". Roles present: {chosen_setting.get('role_hint', 'Diverse staff')}.
2. TIME & ATMOSPHERE: "{chosen_atmosphere}".
3. GUILTY CULPRIT: Suspect {target_culprit_idx} is the ONLY guilty person.
   - Suspect {target_culprit_idx}'s alibi MUST contain a fatal flaw based on: "{chosen_contradiction['core']}".
   - Suspect {target_culprit_idx}'s lie must feel natural to their role and setting.
   - The other two suspects MUST have airtight, realistic, and completely innocent alibis.
4. STRICT LENGTH LIMITS (TARGET TOTAL WORDS: 52-60 words for 22-26s duration):
   - Hook: EXACTLY 8 to 12 words setting up the crime scene.
   - Suspect 1 alibi: EXACTLY 8 to 11 words.
   - Suspect 2 alibi: EXACTLY 8 to 11 words.
   - Suspect 3 alibi: EXACTLY 8 to 11 words.
   - Challenge line: EXACTLY "One is lying. Spot the killer before time runs out! Three, two, one!" (13 words).
   - Reveal explanation: EXACTLY 10 to 14 words. Starts with "It was the [Role]! [Crisp scientific reason]!"
   TOTAL FULL_TEXT MUST BE STRICTLY UNDER 62 WORDS! FAST, PUNCHY, VIRAL!
5. CASE-SPECIFIC TITLE: Must be unique, under 50 characters, specific to this case and setting.
   Format examples: "Who Killed the Glacier Scientist? ❄️ #Shorts", "The Submarine Oxygen Sabotage 🌊 #Shorts", "The Antique Clockmaker's Fatal Lie 🕰️ #Shorts".
   NEVER use generic titles like "Can You Solve This" or "Are You Smarter".
6. VISUAL PROMPTS (5 SCENES): Must use cohesive art style: "{BASE_ART_STYLE}".
   - scene_hook: Crime scene visual in {chosen_setting['name']}.
   - scene_suspect_1: Suspect 1 performing their claimed action in setting.
   - scene_suspect_2: Suspect 2 performing their claimed action in setting.
   - scene_suspect_3: Suspect 3 performing their claimed action in setting.
   - scene_reveal: Dramatic close-up of the contradiction evidence / moment of exposure.

FORBIDDEN:
- Do NOT use topics from past history: [{recent_topics_str}].
- Do NOT use cliché tropes (e.g. ice cubes sinking, page 100-101 in book, stone sinks, whispering in loud machine).

OUTPUT STRICT JSON ONLY:
{{
  "topic_name": "Unique Case Name (e.g. Glacier Core Sabotage)",
  "title": "Case-Specific Title Under 50 Chars #Shorts",
  "description": "Can you spot the fatal lie in 10 seconds? Test your detective IQ!\\n\\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
  "setting_theme": "{chosen_setting['name']}",
  "contradiction_core": "{chosen_contradiction['core'][:60]}",
  "full_text": "Complete spoken text from Hook through Reveal (55 to 65 words)",
  "suspect_1": {{
    "role": "ROLE 1 (e.g. THE MECHANIC)",
    "title": "1. THE MECHANIC",
    "alibi": "Exact spoken alibi sentence (max 14 words)",
    "card_text": "Claim: Short 5-7 word summary matching spoken alibi.",
    "speech_keyword": "unique single lowercase word present in full_text for suspect 1",
    "image_prompt": "Visual prompt for suspect 1 with base art style"
  }},
  "suspect_2": {{
    "role": "ROLE 2 (e.g. THE PILOT)",
    "title": "2. THE PILOT",
    "alibi": "Exact spoken alibi sentence (max 14 words)",
    "card_text": "Claim: Short 5-7 word summary matching spoken alibi.",
    "speech_keyword": "unique single lowercase word present in full_text for suspect 2",
    "image_prompt": "Visual prompt for suspect 2 with base art style"
  }},
  "suspect_3": {{
    "role": "ROLE 3 (e.g. THE COOK)",
    "title": "3. THE COOK",
    "alibi": "Exact spoken alibi sentence (max 14 words)",
    "card_text": "Claim: Short 5-7 word summary matching spoken alibi.",
    "speech_keyword": "unique single lowercase word present in full_text for suspect 3",
    "image_prompt": "Visual prompt for suspect 3 with base art style"
  }},
  "culprit_role": "ROLE OF SUSPECT {target_culprit_idx}",
  "culprit_speech_keyword": "speech_keyword of suspect {target_culprit_idx}",
  "culprit_reason": "REASON: [CRISP UPPERCASE SCIENTIFIC CONTRADICTION]!",
  "scene_prompts": {{
    "hook": "Visual prompt for hook crime scene with base art style",
    "suspect_1": "Visual prompt for suspect 1",
    "suspect_2": "Visual prompt for suspect 2",
    "suspect_3": "Visual prompt for suspect 3",
    "reveal": "Visual prompt for reveal evidence close-up"
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
# STEP 2: STRICT LOGIC CRITIC (INDEPENDENT GEMINI EVALUATION)
# ==============================================================================

def evaluate_logic_with_gemini(script_data: dict) -> dict:
    """
    Independent Gemini evaluation step acting as a skeptical Senior Detective.
    Rejects scientifically flawed, ambiguous, or multi-answer riddles.
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
You are a skeptical Senior Detective and Physics/Logic Critic evaluating a 30-second crime riddle.

CASE UNDER REVIEW:
- Topic: {topic}
- Setting: {setting}
- Suspect 1 ({s1.get('role')}): "{s1.get('alibi')}"
- Suspect 2 ({s2.get('role')}): "{s2.get('alibi')}"
- Suspect 3 ({s3.get('role')}): "{s3.get('alibi')}"
- Accused Culprit: {culprit_role}
- Contradiction Reason: {reason}
- Full Script: "{full_text}" (Total words: {word_count})

STRICT CRITERIA:
1. SCIENTIFIC & LOGICAL SOUNDNESS: Is the contradiction against natural laws/physics 100% indisputable?
   - Reject ambiguous claims or factual errors (e.g. pages 100-101 facing error, water boiling rules, vacuum physics).
2. UNIQUENESS OF GUILT: Is there EXACTLY ONE guilty suspect? Are the other 2 suspects completely plausible and innocent?
3. SCRIPT TIGHTNESS: Is total word count between 52 and 70 words?
4. QUALITY: Is it clever yet solvable in 10 seconds? (Reject trivial clichés like 'stones sink' or 'whispering over 10 engines').

Return strict JSON:
{{
  "valid": true/false,
  "score": 1-10,
  "critique": "Brief 1-sentence assessment of logic quality",
  "refined_reason": "Refined 1-sentence uppercase contradiction reason (or keep existing if good)"
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
        # Fallback rule-based validation
        is_valid = (50 <= word_count <= 72) and bool(culprit_role) and bool(reason)
        return {
            "valid": is_valid,
            "score": 8 if is_valid else 5,
            "critique": "Rule-based validation passed.",
            "refined_reason": reason
        }

# ==============================================================================
# MAIN ORCHESTRATION PIPELINE
# ==============================================================================

def generate_script_with_ai(history: list, max_attempts: int = 4) -> dict:
    """
    2-Step Gemini generation:
    1. Generator creates riddle with strict duration & visual specs.
    2. Strict Logic Critic verifies logic and uniqueness.
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

        print(f"\n[BƯỚC 1/2: GENERATOR #{attempt}] Bối cảnh: '{chosen_setting['name']}' | Cơ chế: '{chosen_contradiction['core'][:45]}...'")

        try:
            draft = generate_script_draft(history, chosen_setting, chosen_atmosphere, chosen_contradiction, target_culprit_idx)

            # Check history duplication
            is_dup, dup_reason = check_is_duplicate(draft, history)
            if is_dup:
                print(f"⚠️ Trùng lặp lịch sử ({dup_reason}). Đổi bối cảnh...")
                continue

            # Check word count strictly for 22-28s total video duration
            word_count = len(draft.get("full_text", "").split())
            if word_count < 48 or word_count > 64:
                print(f"⚠️ Số từ không tối ưu ({word_count} từ, cần 50-62 từ để đạt thời lượng chuẩn 22-26s). Thử lại...")
                continue

            # Ensure title length < 55 chars
            title = draft.get("title", "")
            if len(title) > 55:
                # Trim cleanly before #Shorts
                short_title = re.sub(r'\s*#Shorts.*$', '', title)[:40].strip()
                draft["title"] = f"{short_title} #Shorts"

            # Step 2: Strict Logic Critic
            print(f"[BƯỚC 2/2: LOGIC CRITIC] Kiểm tra tính xác thực khoa học và tính độc nhất của lời giải...")
            critique = evaluate_logic_with_gemini(draft)
            print(f"   -> Điểm Logic: {critique.get('score')}/10 | Đạt chuẩn: {critique.get('valid')} | Nhận xét: {critique.get('critique')}")

            if not critique.get("valid") or critique.get("score", 0) < 7:
                print(f"⚠️ Kịch bản bị Logic Critic từ chối ({critique.get('critique')}). Tạo lại kịch bản mới...")
                continue

            if critique.get("refined_reason"):
                draft["culprit_reason"] = critique["refined_reason"]

            draft["logic_score"] = critique.get("score", 8)
            draft["logic_critique"] = critique.get("critique", "Approved")

            # Validate scene prompts exist
            if "scene_prompts" not in draft or not all(k in draft["scene_prompts"] for k in ["hook", "suspect_1", "suspect_2", "suspect_3", "reveal"]):
                draft["scene_prompts"] = {
                    "hook": f"Crime scene at {chosen_setting['name']}, victim found, {BASE_ART_STYLE}",
                    "suspect_1": f"{draft['suspect_1'].get('role')} at {chosen_setting['name']}, {BASE_ART_STYLE}",
                    "suspect_2": f"{draft['suspect_2'].get('role')} at {chosen_setting['name']}, {BASE_ART_STYLE}",
                    "suspect_3": f"{draft['suspect_3'].get('role')} at {chosen_setting['name']}, {BASE_ART_STYLE}",
                    "reveal": f"Close-up evidence showing contradiction at {chosen_setting['name']}, {BASE_ART_STYLE}"
                }

            print(f"✅ Kịch bản xuất sắc được phê duyệt: '{draft.get('topic_name')}' | Tiêu đề: '{draft.get('title')}'")
            return draft

        except Exception as e:
            print(f"Lỗi ở lượt tạo {attempt}: {e}")

    raise RuntimeError("Gemini AI failed to produce a verified script within the maximum attempts.")

def generate_script():
    """Generates a dynamic non-duplicating Short script with 2-step AI pipeline and fallback safety."""
    history = load_history()

    if GEMINI_API_KEY:
        try:
            print("Đang khởi động Quy trình 2 bước (Generator + Strict Logic Critic)...")
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
