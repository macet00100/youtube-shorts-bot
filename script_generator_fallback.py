import random
import os
import json
import copy
from config import HISTORY_FILE

BASE_ART_STYLE = (
    "moody noir detective comic illustration, dark cinematic graphic novel art style, "
    "dramatic rim lighting, high contrast shadows, detailed textures, 9:16 vertical composition"
)

FALLBACK_TEMPLATES = [
    {
        "topic_name": "Historic Grand Hotel Penthouse Blackout",
        "title": "The Penthouse Blackout Murder ⚡ #Shorts",
        "description": "Can you spot the fatal lie before the countdown ends? Comment your answer below!\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_theme": "Historic Grand Hotel Penthouse",
        "full_text": (
            "A billionaire was murdered in his penthouse during a midnight blackout. "
            "The Butler was lighting candles in the dark hallway. "
            "The Chef claimed he checked the digital microwave clock for the time. "
            "The Valet was unlocking the emergency stairs. "
            "One is lying. Spot the killer before time runs out! "
            "Three, two, one! "
            "It was the Chef! Digital microwave displays turn completely black during power outages!"
        ),
        "suspect_1": {
            "role": "THE BUTLER",
            "title": "1. THE BUTLER",
            "alibi": "Lighting candles in the dark hallway.",
            "card_text": "Claim: Lighting candles in dark hall.",
            "speech_keyword": "butler",
            "image_prompt": f"Butler holding brass candlestick in dark luxury hotel hallway, {BASE_ART_STYLE}"
        },
        "suspect_2": {
            "role": "THE CHEF",
            "title": "2. THE CHEF",
            "alibi": "Checked digital microwave clock for time.",
            "card_text": "Claim: Checked digital microwave clock.",
            "speech_keyword": "chef",
            "image_prompt": f"Nervous chef standing in dark kitchen near stainless microwave, {BASE_ART_STYLE}"
        },
        "suspect_3": {
            "role": "THE VALET",
            "title": "3. THE VALET",
            "alibi": "Unlocking the emergency exit stairs.",
            "card_text": "Claim: Unlocking emergency stairs.",
            "speech_keyword": "valet",
            "image_prompt": f"Hotel valet using brass keys at emergency exit stairwell, {BASE_ART_STYLE}"
        },
        "culprit_role": "THE CHEF",
        "culprit_speech_keyword": "chef",
        "culprit_reason": "REASON: DIGITAL MICROWAVE DISPLAYS ARE COMPLETELY DARK DURING A POWER OUTAGE!",
        "scene_prompts": {
            "hook": f"Crime scene in luxury penthouse suite under emergency amber lighting, {BASE_ART_STYLE}",
            "suspect_1": f"Butler holding candlestick in hotel corridor, {BASE_ART_STYLE}",
            "suspect_2": f"Chef standing beside blacked-out microwave in kitchen, {BASE_ART_STYLE}",
            "suspect_3": f"Valet turning key in emergency stairwell door, {BASE_ART_STYLE}",
            "reveal": f"Close-up of unpowered dark digital microwave LED clock screen, {BASE_ART_STYLE}"
        }
    },
    {
        "topic_name": "Active Volcano Caldera Lab Night Window",
        "title": "The Volcano Night Window Lie 🌋 #Shorts",
        "description": "Can you spot the fatal lie before the countdown ends? Comment your answer below!\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_theme": "Active Volcano Caldera Lab",
        "full_text": (
            "A scientist was murdered inside the brightly lit research bunker. "
            "The Seismologist was monitoring ground earthquake tremor sensors. "
            "The Geologist claimed he looked through the window and saw the killer running in pitch-black darkness outside. "
            "The Pilot was inspecting the drone launchpad. "
            "One is lying. Spot the killer before time runs out! "
            "Three, two, one! "
            "It was the Geologist! Looking from a lit room into pitch darkness shows only reflections, not the outside!"
        ),
        "suspect_1": {
            "role": "THE SEISMOLOGIST",
            "title": "1. THE SEISMOLOGIST",
            "alibi": "Monitoring ground tremor sensors on screens.",
            "card_text": "Claim: Monitoring ground sensors.",
            "speech_keyword": "seismologist",
            "image_prompt": f"Seismologist analyzing green graph monitors in volcanic bunker, {BASE_ART_STYLE}"
        },
        "suspect_2": {
            "role": "THE GEOLOGIST",
            "title": "2. THE GEOLOGIST",
            "alibi": "Saw killer running through dark glass window.",
            "card_text": "Claim: Saw killer through dark window.",
            "speech_keyword": "geologist",
            "image_prompt": f"Tense geologist looking at reflective dark glass window in lit room, {BASE_ART_STYLE}"
        },
        "suspect_3": {
            "role": "THE PILOT",
            "title": "3. THE PILOT",
            "alibi": "Inspecting drone propellers on launchpad.",
            "card_text": "Claim: Inspecting drone propellers.",
            "speech_keyword": "pilot",
            "image_prompt": f"Pilot checking carbon fiber drone on volcanic cliff platform, {BASE_ART_STYLE}"
        },
        "culprit_role": "THE GEOLOGIST",
        "culprit_speech_keyword": "geologist",
        "culprit_reason": "REASON: A LIT ROOM TURNS GLASS INTO A MIRROR; YOU CANNOT SEE OUTSIDE INTO PITCH BLACK!",
        "scene_prompts": {
            "hook": f"Crime scene inside brightly lit volcano research station, {BASE_ART_STYLE}",
            "suspect_1": f"Seismologist monitoring volcanic activity on screens, {BASE_ART_STYLE}",
            "suspect_2": f"Geologist staring at reflective dark glass window, {BASE_ART_STYLE}",
            "suspect_3": f"Drone pilot examining quadcopter equipment, {BASE_ART_STYLE}",
            "reveal": f"Close-up of bright interior reflection mirrored in dark night glass window, {BASE_ART_STYLE}"
        }
    },
    {
        "topic_name": "Arctic Glaciology Research Camp Cold Engine",
        "title": "The Arctic Frozen Car Lie ❄️ #Shorts",
        "description": "Can you spot the fatal lie before the countdown ends? Comment your answer below!\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_theme": "Arctic Glaciology Research Camp",
        "full_text": (
            "An expedition director was murdered inside the polar dome. "
            "The Meteorologist was logging wind speeds outside. "
            "The Mechanic claimed he just drove from the airstrip five minutes ago, but his car hood was covered in thick undisturbed ice. "
            "The Drill Tech was sharpening auger drill bits. "
            "One is lying. Spot the killer before time runs out! "
            "Three, two, one! "
            "It was the Mechanic! An engine driven miles stays hot and would have melted the hood frost!"
        ),
        "suspect_1": {
            "role": "THE METEOROLOGIST",
            "title": "1. THE METEOROLOGIST",
            "alibi": "Logging wind speeds outside in the snow.",
            "card_text": "Claim: Logging wind speeds in snow.",
            "speech_keyword": "meteorologist",
            "image_prompt": f"Female scientist in snow parka holding digital anemometer, {BASE_ART_STYLE}"
        },
        "suspect_2": {
            "role": "THE MECHANIC",
            "title": "2. THE MECHANIC",
            "alibi": "Just drove from airstrip five minutes ago.",
            "card_text": "Claim: Just drove from airstrip.",
            "speech_keyword": "mechanic",
            "image_prompt": f"Mechanic in arctic gear standing near snow-covered vehicle, {BASE_ART_STYLE}"
        },
        "suspect_3": {
            "role": "THE DRILL TECH",
            "title": "3. THE DRILL TECH",
            "alibi": "Sharpening mechanical ice drill bits.",
            "card_text": "Claim: Sharpening ice drill bits.",
            "speech_keyword": "drill",
            "image_prompt": f"Technician sharpening large steel auger drill bit in shelter, {BASE_ART_STYLE}"
        },
        "culprit_role": "THE MECHANIC",
        "culprit_speech_keyword": "mechanic",
        "culprit_reason": "REASON: A RECENTLY DRIVEN ENGINE STAYS HOT AND WOULD HAVE MELTED THE HOOD FROST!",
        "scene_prompts": {
            "hook": f"Crime scene inside arctic expedition dome tent during polar storm, {BASE_ART_STYLE}",
            "suspect_1": f"Meteorologist checking weather gear in snow, {BASE_ART_STYLE}",
            "suspect_2": f"Mechanic standing by vehicle with frozen frosted hood, {BASE_ART_STYLE}",
            "suspect_3": f"Technician working on ice core drill machinery, {BASE_ART_STYLE}",
            "reveal": f"Close-up of thick undisturbed frost and ice on car engine hood, {BASE_ART_STYLE}"
        }
    }
]

def get_fallback_script(history: list) -> dict:
    """Selects an unused fallback template from the verified pool."""
    past_topics = [h.get("topic_name", "").strip().lower() for h in history]
    available = [t for t in FALLBACK_TEMPLATES if t["topic_name"].strip().lower() not in past_topics]

    if not available:
        recent_3 = [h.get("topic_name", "").strip().lower() for h in history[-3:]]
        available = [t for t in FALLBACK_TEMPLATES if t["topic_name"].strip().lower() not in recent_3]
        if not available:
            available = FALLBACK_TEMPLATES

    selected = copy.deepcopy(random.choice(available))
    print(f"Dự phòng kích hoạt: Chọn kịch bản độc bản '{selected['topic_name']}' với tiêu đề '{selected['title']}'")

    selected["suspect_keywords"] = [
        selected["suspect_1"].get("speech_keyword", "first"),
        selected["suspect_2"].get("speech_keyword", "second"),
        selected["suspect_3"].get("speech_keyword", "third")
    ]
    selected["suspect_badges"] = [
        "assets/riddle/badge_suspect_1.png",
        "assets/riddle/badge_suspect_2.png",
        "assets/riddle/badge_suspect_3.png"
    ]
    selected["guilty_stamp"] = "assets/riddle/guilty_stamp.png"

    # Record in history
    history.append({
        "topic_name": selected["topic_name"],
        "title": selected["title"],
        "setting_theme": selected.get("setting_theme", selected["topic_name"]),
        "culprit_role": selected.get("culprit_role"),
        "culprit_reason": selected.get("culprit_reason"),
        "logic_score": 9,
        "generated_at": str(os.getenv("GITHUB_RUN_ID", "fallback_pool"))
    })

    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return selected
