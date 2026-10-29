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

GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# ==============================================================================
# PROCEDURAL DIMENSION MATRIX (COMBINATORIAL EXPLOSION FOR ZERO REPETITION)
# ==============================================================================

SETTINGS_POOL = [
    # High-Tech & Space
    {"name": "Mars Habitat Bio-Dome", "category": "tech_space", "search": "mars planet surface space"},
    {"name": "Deep-Sea Submarine Research Laboratory", "category": "tech_space", "search": "submarine underwater lab"},
    {"name": "Cryogenic Quantum Server Vault", "category": "tech_space", "search": "server room technology blue"},
    {"name": "Cleanroom Semiconductor Foundry", "category": "tech_space", "search": "cleanroom science laboratory"},
    {"name": "Automated Drone Hangar", "category": "tech_space", "search": "drone technology futuristic"},
    {"name": "Subterranean Particle Accelerator", "category": "tech_space", "search": "particle accelerator science tunnel"},
    {"name": "International Space Station Cupola", "category": "tech_space", "search": "space station earth view orbit"},

    # Wild Nature & Extreme Expeditions
    {"name": "Sahara Desert Archaeological Excavation", "category": "expedition", "search": "desert archaeology excavation ruins"},
    {"name": "Himalayan High-Altitude Alpine Basecamp", "category": "expedition", "search": "snow mountain tent basecamp"},
    {"name": "Amazon River Rainforest Canopy Research Station", "category": "expedition", "search": "rainforest river research canopy"},
    {"name": "Active Volcano Caldera Monitoring Station", "category": "expedition", "search": "volcano lava smoke mountain"},
    {"name": "Subterranean Giant Crystal Cavern", "category": "expedition", "search": "crystal cave underground limestone"},
    {"name": "Arctic Glaciology Ice Core Drilling Camp", "category": "expedition", "search": "arctic ice snow polar blizzard"},
    {"name": "Deep Ocean Geothermal Vent Rig", "category": "expedition", "search": "ocean oil rig deep sea water"},

    # Historic Arts & Artisanal Craft
    {"name": "Venetian Glassblowing Furnace Atelier", "category": "art_craft", "search": "glassblowing workshop fire artisan"},
    {"name": "Stradivarius Acoustic Violin Workshop", "category": "art_craft", "search": "violin craft wood workshop"},
    {"name": "Renaissance Clock Tower Gear Room", "category": "art_craft", "search": "clock tower gears antique"},
    {"name": "Vatican Ancient Secret Manuscript Vault", "category": "art_craft", "search": "ancient library books scroll"},
    {"name": "Historic Antique Mirror Restoration Atelier", "category": "art_craft", "search": "mirror reflection vintage room"},
    {"name": "Broadway Theater Backstage Costume Wardrobe", "category": "art_craft", "search": "theater stage backstage curtains"},
    {"name": "Royal Tapestry Weaving Guild Studio", "category": "art_craft", "search": "weaving loom fabric tapestry"},

    # Luxury & High Society
    {"name": "Monaco Formula Racing Pit Garage", "category": "luxury", "search": "formula racing car garage pit"},
    {"name": "Supersonic Private Jet Cruising Cabin", "category": "luxury", "search": "private jet airplane flying luxury"},
    {"name": "High-Security Diamond Cutting Guild", "category": "luxury", "search": "diamond jewelry vault sparkle"},
    {"name": "Michelin 3-Star Sushi Omakase Counter", "category": "luxury", "search": "sushi chef restaurant counter"},
    {"name": "Royal Thoroughbred Equestrian Stables", "category": "luxury", "search": "horse stable equestrian luxury"},
    {"name": "High-Rise Penthouse Rooftop Infinity Pool", "category": "luxury", "search": "rooftop infinity pool city night"},
    {"name": "Swiss Private Vault Safety Deposit Sanctuary", "category": "luxury", "search": "bank vault gold safety deposit"},

    # Quirky Urban & Everyday Mystery
    {"name": "Vintage 1980s Neon Bowling Alley", "category": "urban", "search": "bowling alley neon lights retro"},
    {"name": "24-Hour Industrial Laundromat", "category": "urban", "search": "laundromat washing machines night"},
    {"name": "Skyscraper Rooftop Honeybee Apiary", "category": "urban", "search": "honey bees beehive rooftop"},
    {"name": "Underground Metro Central Signal Box", "category": "urban", "search": "subway tunnel train dispatch"},
    {"name": "Harbor Fog Horn Lighthouse Lantern Room", "category": "urban", "search": "lighthouse sea waves fog"},
    {"name": "Vintage Vinyl Mastering and Pressing Plant", "category": "urban", "search": "vinyl record turntable music"},
    {"name": "Neon Glass Tube Sign Workshop", "category": "urban", "search": "neon lights glass glowing gas"}
]

ATMOSPHERES_POOL = [
    "Scorching Midday Sun at 42°C under an open sky",
    "Dense Morning Fog at 06:00 AM with near-zero visibility",
    "Heavy Torrential Rainstorm with thunderous lightning flashes",
    "Quiet Mid-Afternoon with pale sunlight streaming through high windows",
    "Crisp Winter Dawn with a fresh dusting of morning frost",
    "Late Evening Twilight as darkness settles in",
    "Sudden Midnight Blackout under dim emergency amber lighting",
    "Roaring Windstorm rattling the building's exterior windows",
    "Sultry Humid Tropical Dusk before a sudden monsoonal storm",
    "Eerie Pre-Dawn Stillness right before the sunrise",
    "Blinding Noon Sunlight reflecting intensely off polished surfaces",
    "Deep Chilly Night under an overcast moonless sky"
]

CONTRADICTIONS_POOL = [
    # Universal Optics & Shadows
    {"core": "Shadow pointing towards the primary light source instead of falling directly away", "categories": ["all"], "banned_words": ["shadow", "spotlight"]},
    {"core": "Claiming to see a vivid colorful rainbow inside a dry indoor room or at night without direct sunlight and water mist", "categories": ["all"], "banned_words": ["rainbow"]},
    {"core": "Claiming to see clear reflections in plain transparent window glass while standing inside a pitch-black room", "categories": ["all"], "banned_words": ["reflection", "mirror"]},
    
    # Universal Thermodynamics & Physics
    {"core": "Claiming ice cubes sank to the bottom of a glass of pure water (ice is less dense and always floats)", "categories": ["all"], "banned_words": ["ice float", "sink"]},
    {"core": "Claiming dry ice blocks melted into a deep puddle of liquid water (dry ice sublimates directly into carbon dioxide gas)", "categories": ["all"], "banned_words": ["dry ice", "sublimate"]},
    {"core": "Claiming glowing cherry-red metal was touched barehanded without causing severe third-degree burns", "categories": ["art_craft", "luxury", "tech_space", "urban"], "banned_words": ["glowing metal", "brake disc", "furnace"]},
    {"core": "Claiming warm smoke fell straight downwards to the floor like liquid in still room air (warm smoke is buoyant and rises)", "categories": ["all"], "banned_words": ["smoke sink", "smoke fall"]},

    # Universal Chemistry & Materials
    {"core": "Claiming to retrieve pure 24-karat solid gold using an ordinary magnetic tool (pure gold is non-magnetic)", "categories": ["luxury", "art_craft", "urban", "expedition"], "banned_words": ["magnet", "gold"]},
    {"core": "Claiming traditional oil varnish or oil paint dried completely hard in 5 minutes (oil finishes take days to cure)", "categories": ["art_craft", "luxury", "urban"], "banned_words": ["oil paint", "varnish"]},
    {"core": "Claiming coarse table salt dissolved into a container of pure vegetable cooking oil (salt dissolves in polar water, not non-polar oil)", "categories": ["luxury", "expedition", "urban"], "banned_words": ["salt dissolve", "oil"]},
    {"core": "Claiming sliced fresh apples remained crisp and pure snow-white after sitting for 8 hours in open air (apples oxidize and turn brown)", "categories": ["all"], "banned_words": ["apple brown", "oxidize"]},
    {"core": "Claiming steel scissors easily cut a real natural raw diamond in half (diamonds are the hardest natural mineral and cannot be cut by steel)", "categories": ["luxury", "art_craft", "urban"], "banned_words": ["cut diamond", "scissors"]},

    # Universal Clocks, Calendars & Logic
    {"core": "Claiming an official business transaction occurred on the fictitious calendar date of February 30th", "categories": ["all"], "banned_words": ["february 30", "calendar"]},
    {"core": "Claiming to read a secret note placed between facing book pages 100 and 101 (in bound books, consecutive even and odd pages are opposite sides of one sheet)", "categories": ["art_craft", "luxury", "tech_space", "urban"], "banned_words": ["page 100", "pages 100 and 101"]},
    {"core": "Claiming a sundial cast a sharp readable shadow on a roof during an overcast thunderstorm", "categories": ["expedition", "art_craft", "urban"], "banned_words": ["sundial"]},

    # Universal Sound & Acoustics
    {"core": "Claiming to hear a loud vocal echo across flat open sand dunes or open water without vertical reflective surfaces", "categories": ["expedition", "luxury", "tech_space"], "banned_words": ["echo", "sand"]},
    {"core": "Claiming to hear thunder rumble several seconds before seeing the lightning flash strike (light travels 1 million times faster than sound)", "categories": ["all"], "banned_words": ["thunder", "lightning"]},
    {"core": "Claiming to hear a quiet whisper clearly over the roaring deafening decibels of an active engine or machinery", "categories": ["luxury", "urban", "tech_space"], "banned_words": ["whisper", "engine"]},

    # Setting-Specific Principles
    {"core": "Claiming a candle was burning inside a sealed airless vacuum chamber without oxygen", "categories": ["tech_space"], "banned_words": ["candle", "vacuum", "oxygen"]},
    {"core": "Claiming to sweat from excessive heat inside a cryogenic sub-zero server vault or refrigerated room", "categories": ["tech_space", "luxury", "urban"], "banned_words": ["sweat", "server room", "refrigerator"]},
    {"core": "Claiming water boiled at over 120°C on an open camp stove at high mountain altitude (water boils at lower temperature at high altitude)", "categories": ["expedition"], "banned_words": ["boil", "altitude"]},
    {"core": "Claiming to hear human voices or cries traveling through an exterior pressurized submarine hull underwater", "categories": ["tech_space"], "banned_words": ["hull", "submarine voice"]},
    {"core": "Claiming an express train overtook another train while traveling on a single one-way track", "categories": ["urban"], "banned_words": ["overtake", "single track"]},
    {"core": "Claiming honeybees were actively flying and swarming outside during a heavy torrential rainstorm (bees stay inside hives during rain)", "categories": ["urban", "expedition"], "banned_words": ["bees rain", "swarm"]}
]

VIRAL_TITLES_POOL = [
    "Who Is The Killer? 95% Fail This Riddle! #Shorts",
    "Can You Spot The Liar In 10 Seconds? 🕵️‍♂️ #Shorts",
    "Only A True Detective Catches The Flaw! #Shorts",
    "99% Miss The Clue! Who Murdered The Victim? #Shorts",
    "Detective IQ Test: Can You Catch The Killer? #Shorts",
    "Only 5% Of Detectives Solve This Riddle! #Shorts",
    "Can You Catch The Killer Before Time Runs Out? #Shorts",
    "Spot The Single Lie Before The Timer Ends! #Shorts"
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
    """Extracts lowercase words of length >= 4, filtering common stopwords."""
    stopwords = {
        "this", "that", "with", "from", "were", "been", "have", "what", "when", "where",
        "which", "there", "their", "about", "would", "could", "should", "murder", "mystery",
        "crime", "riddle", "shorts", "killer", "suspect", "alibi", "reason", "midnight", "grand"
    }
    words = re.findall(r'[a-zA-Z]{4,}', text.lower())
    return {w for w in words if w not in stopwords}

def clean_topic_for_comparison(text: str) -> str:
    """Removes generic boilerplate stopwords to ensure high-accuracy semantic comparison."""
    stopwords_pattern = r'\b(murder|mystery|crime|riddle|shorts|the|and|of|in|at|on|for|case|solved)\b'
    cleaned = re.sub(stopwords_pattern, '', text.lower())
    return re.sub(r'\s+', ' ', cleaned).strip()

def check_is_duplicate(new_script: dict, history: list) -> tuple[bool, str]:
    """
    Strict fuzzy and semantic check against all past history entries.
    Rejects any script that duplicates setting, contradiction, or wording.
    """
    if not history:
        return False, ""

    new_topic = new_script.get("topic_name", "").strip()
    new_reason = new_script.get("culprit_reason", "").strip().upper()
    new_full = new_script.get("full_text", "").strip()
    
    # 1. Reject cliché naming pattern "Midnight Grand ..."
    if new_topic.lower().startswith("midnight grand"):
        return True, "Banned cliché naming pattern 'Midnight Grand...'"

    clean_new_topic = clean_topic_for_comparison(new_topic)
    new_topic_words = extract_core_keywords(clean_new_topic)

    # 2. Check each historical entry
    for h in history:
        past_topic = h.get("topic_name", "").strip()
        past_reason = h.get("culprit_reason", "").strip().upper()
        clean_past_topic = clean_topic_for_comparison(past_topic)

        # Check A: Exact topic match
        if new_topic.lower() == past_topic.lower() or clean_new_topic == clean_past_topic:
            return True, f"Exact topic name match with history: '{past_topic}'"

        # Check B: High SequenceMatcher topic similarity on cleaned text
        sim_topic = difflib.SequenceMatcher(None, clean_new_topic, clean_past_topic).ratio()
        if sim_topic > 0.60:
            return True, f"Topic similarity too high ({sim_topic:.2f}) with past topic: '{past_topic}'"

        # Check C: Core setting keyword collision (e.g. greenhouse, bakery, lighthouse, ski, hotel)
        past_topic_words = extract_core_keywords(clean_past_topic)
        overlap = new_topic_words.intersection(past_topic_words)
        if overlap:
            # If any distinctive setting noun matches (e.g. greenhouse, bakery, lighthouse)
            distinctive_setting_words = {
                "greenhouse", "bakery", "lighthouse", "hotel", "chalet", "observatory",
                "planetarium", "museum", "casino", "aquarium", "winery", "library",
                "subway", "train", "submarine", "lounge", "suite", "manor"
            }
            colliding = overlap.intersection(distinctive_setting_words)
            if colliding:
                return True, f"Topic shares distinctive setting keyword {colliding} with past topic: '{past_topic}'"

        # Check D: Reason keyword collision (e.g. sunbathing, watering plants, sub-zero coffee)
        if past_reason and new_reason:
            sim_reason = difflib.SequenceMatcher(None, new_reason, past_reason).ratio()
            if sim_reason > 0.60:
                return True, f"Culprit contradiction reason similarity too high ({sim_reason:.2f}) with: '{past_reason}'"

    # 3. Explicitly ban ancient repetitive tropes
    banned_tropes = [
        "sunbathe", "sunbathing",
        "watering orchid", "watering roses", "watering flower",
        "coffee freeze", "coffee freezing",
        "checking ticket in pitch black", "darkness without any light",
        "mail delivery on sunday", "no mail delivery on sunday"
    ]
    combined_content = f"{new_topic} {new_reason} {new_full}".lower()
    for trope in banned_tropes:
        if trope in combined_content:
            return True, f"Contains banned cliché trope: '{trope}'"

    return False, ""

def generate_script_with_ai(history: list, max_attempts: int = 4) -> dict:
    """
    Procedurally prompts Gemini with random dimensional constraints,
    verifying every output against history to ensure 100% uniqueness.
    """
    history_topics = [h.get("topic_name", "") for h in history if h.get("topic_name")]
    recent_topics_str = ", ".join(history_topics[-35:]) if history_topics else "None"

    # Identify settings and contradictions already used in history
    used_keywords = set()
    for h in history:
        used_keywords.update(extract_core_keywords(h.get("topic_name", "")))
        if h.get("culprit_reason"):
            used_keywords.update(extract_core_keywords(h.get("culprit_reason", "")))

    # Filter available settings to ones that don't overlap with recent history
    available_settings = [
        s for s in SETTINGS_POOL
        if not extract_core_keywords(s["name"]).intersection(used_keywords)
    ]
    if not available_settings:
        available_settings = SETTINGS_POOL

    for attempt in range(1, max_attempts + 1):
        chosen_setting = random.choice(available_settings)
        chosen_atmosphere = random.choice(ATMOSPHERES_POOL)
        
        # Pick a contradiction compatible with this setting category
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
        chosen_title_hook = random.choice(VIRAL_TITLES_POOL)
        target_culprit_idx = random.choice([1, 2, 3])

        print(f"\n[Thử thách {attempt}/{max_attempts}] Bối cảnh: '{chosen_setting['name']}' | Cơ chế: '{chosen_contradiction['core'][:40]}...' | Thủ phạm: Nghi phạm {target_culprit_idx}")

        system_prompt = f"""
You are a viral YouTube Shorts creator specializing in interactive "30-SECOND CRIME RIDDLES & DETECTIVE MYSTERIES" (Targeting Global US/UK English Audience).
Format Concept: "CAN YOU SPOT THE KILLER IN 10 SECONDS?"

MANDATORY PROCEDURAL CONSTRAINTS (ZERO REPETITION):
1. MANDATORY SETTING: You MUST base this crime mystery entirely inside: "{chosen_setting['name']}".
2. TIME & ATMOSPHERE: The crime occurred during: "{chosen_atmosphere}".
3. MANDATORY CULPRIT: The GUILTY CULPRIT MUST BE SUSPECT {target_culprit_idx}!
   - Suspect {target_culprit_idx} MUST be the only one with a physical, scientific, or logical lie.
   - The exact contradiction in Suspect {target_culprit_idx}'s alibi MUST be based on this physical principle: "{chosen_contradiction['core']}".
   - NARRATIVE COHESION: Suspect {target_culprit_idx}'s alibi must naturally fit the setting of "{chosen_setting['name']}" (e.g. if the contradiction is about oil paint/varnish, they were coating equipment/props; if about a magnet, they were retrieving fallen tools; if about ice/water, they were preparing a drink or cooling samples).
   - The other two suspects MUST have airtight, completely innocent, and realistic alibis.
   - "culprit_role" MUST be identical to Suspect {target_culprit_idx}'s role!
4. YOUTUBE TITLE FORMAT: Use or adapt this viral hook: "{chosen_title_hook}".
5. ABSOLUTELY FORBIDDEN (INSTANT REJECTION):
   - Do NOT use the words "Midnight Grand" in the topic name.
   - Do NOT use these previously published topics: [{recent_topics_str}].
   - BANNED TROPES: Sunbathing at night, watering plants/flowers in freezing blizzard, hot coffee freezing in sub-zero wind, checking tickets in pitch darkness, mail on Sunday.

Strict Formula for 150%+ Retention (Watch-Time + Replay):
1. LENGTH: Exactly 75 to 85 spoken English words (30 to 33 seconds spoken).
2. STRUCTURE:
   - Seconds 0-8 (CRIME HOOK): A murder mystery setup in {chosen_setting['name']}.
   - Seconds 8-19 (THE 3 SUSPECTS): 3 suspects with concise, tailored roles for {chosen_setting['name']}. Suspect {target_culprit_idx} tells the physical lie.
   - Seconds 19-24 (CHALLENGE): "One of them is lying. Spot the killer before the timer runs out! Five, four, three, two, one..."
   - Seconds 24-34 (REVELATION & LOOP): "It was the [Role]! [Explain exact scientific contradiction in 1 crisp sentence]! Did you solve it? Comment YES or NO!"

OUTPUT FORMAT: Strict valid JSON only:
{{
  "topic_name": "Unique Topic Name (DO NOT start with Midnight Grand)",
  "title": "{chosen_title_hook}",
  "description": "Can you solve this crime mystery in 10 seconds? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
  "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
  "setting_query": "{chosen_setting['search']}",
  "full_text": "Complete spoken voiceover text from start to end (75-85 words)",
  "suspect_1": {{
    "role": "ROLE 1",
    "title": "SUSPECT 1: ROLE 1",
    "alibi": "ALIBI: Concise alibi statement.",
    "search_keyword": "pixabay footage keyword",
    "speech_keyword": "unique single word present in full_text for suspect 1"
  }},
  "suspect_2": {{
    "role": "ROLE 2",
    "title": "SUSPECT 2: ROLE 2",
    "alibi": "ALIBI: Concise alibi statement.",
    "search_keyword": "pixabay footage keyword",
    "speech_keyword": "unique single word present in full_text for suspect 2"
  }},
  "suspect_3": {{
    "role": "ROLE 3",
    "title": "SUSPECT 3: ROLE 3",
    "alibi": "ALIBI: Concise alibi statement.",
    "search_keyword": "pixabay footage keyword",
    "speech_keyword": "unique single word present in full_text for suspect 3"
  }},
  "culprit_role": "ROLE OF SUSPECT {target_culprit_idx}",
  "culprit_speech_keyword": "speech_keyword of suspect {target_culprit_idx}",
  "culprit_reason": "REASON: [SHORT UPPERCASE EXPLANATION OF CONTRADICTION]!"
}}
"""

        payload = {
            "contents": [{"parts": [{"text": system_prompt}]}],
            "generationConfig": {
                "temperature": 0.90,
                "responseMimeType": "application/json"
            }
        }

        try:
            response = requests.post(GEMINI_URL, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            script_data = json.loads(raw_text)

            # Validate against history
            is_dup, dup_reason = check_is_duplicate(script_data, history)
            if is_dup:
                print(f"⚠️ Kịch bản bị từ chối do trùng lặp ({dup_reason}). Đang thử lại với góc sáng tạo mới...")
                continue

            # Ensure all required keys exist
            required_keys = ["topic_name", "title", "full_text", "suspect_1", "suspect_2", "suspect_3", "culprit_role", "culprit_reason"]
            if not all(k in script_data for k in required_keys):
                print("⚠️ Kịch bản thiếu trường dữ liệu bắt buộc. Đang thử lại...")
                continue

            script_data["setting_theme"] = chosen_setting["name"]
            print(f"✅ Kịch bản độc bản xuất sắc: '{script_data.get('topic_name')}' (Thủ phạm: {script_data.get('culprit_role')})")
            return script_data

        except Exception as e:
            print(f"Lỗi ở lượt gọi {attempt}: {e}")

    raise RuntimeError("Gemini AI failed to produce a non-duplicating script within the maximum attempts.")

def generate_script():
    """Generates a dynamic non-duplicating Short script using Gemini AI with fallback safety."""
    history = load_history()

    if GEMINI_API_KEY:
        try:
            print("Đang kết nối Gemini AI với Bộ ma trận đa chiều chống lặp kịch bản...")
            script_data = generate_script_with_ai(history)

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
                "setting_theme": script_data.get("setting_theme", ""),
                "culprit_role": script_data.get("culprit_role", ""),
                "culprit_reason": script_data.get("culprit_reason", ""),
                "generated_at": str(os.getenv("GITHUB_RUN_ID", "local_ai"))
            })
            save_history(history)
            return script_data
        except Exception as e:
            print(f"Lỗi khi gọi Gemini AI: {e}. Kích hoạt Kho 25 kịch bản độc bản dự phòng...")

    # Fallback rotation if AI fails or no key
    from script_generator_fallback import get_fallback_script
    return get_fallback_script(history)

if __name__ == "__main__":
    s = generate_script()
    print("\n--- KỊCH BẢN ĐÃ TẠO THÀNH CÔNG ---")
    print(f"Topic: {s.get('topic_name')}")
    print(f"Title: {s.get('title')}")
    print(f"Culprit: {s.get('culprit_role')}")
    print(f"Reason: {s.get('culprit_reason')}")
    print(f"Full text ({len(s.get('full_text', '').split())} words):\n{s.get('full_text')}")
