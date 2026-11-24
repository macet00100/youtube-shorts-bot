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
        "topic_name": "Deep-Sea Submarine Sabotage",
        "title": "Who Murdered the Submarine Scientist? 🌊 #Shorts",
        "description": "Can you spot the fatal lie in 10 seconds? Test your detective IQ!\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_theme": "Deep-Sea Submarine Laboratory",
        "full_text": (
            "A marine scientist was murdered inside a deep submarine lab two miles underwater. "
            "The Navigator claimed he was checking underwater coordinates on the radar. "
            "The Biologist said she was examining deep coral under the microscope. "
            "The Sonar Tech swore he heard the victim scream outside in open water. "
            "One of them is lying. Spot the killer before time runs out! "
            "Three, two, one! "
            "It was the Sonar Tech! Human voices cannot travel through miles of deep pressurized water!"
        ),
        "suspect_1": {
            "role": "THE NAVIGATOR",
            "title": "1. THE NAVIGATOR",
            "alibi": "Checking underwater coordinates on the radar screen.",
            "card_text": "Claim: Checking coordinates on radar.",
            "speech_keyword": "navigator",
            "image_prompt": f"Submarine navigator studying green sonar radar screen, control room, {BASE_ART_STYLE}"
        },
        "suspect_2": {
            "role": "THE BIOLOGIST",
            "title": "2. THE BIOLOGIST",
            "alibi": "Examining deep coral samples under the laboratory microscope.",
            "card_text": "Claim: Examining coral under microscope.",
            "speech_keyword": "biologist",
            "image_prompt": f"Female marine biologist examining glowing coral under laboratory microscope, {BASE_ART_STYLE}"
        },
        "suspect_3": {
            "role": "THE SONAR TECH",
            "title": "3. THE SONAR TECH",
            "alibi": "Swore he heard the victim scream outside in open water.",
            "card_text": "Claim: Heard victim scream in ocean.",
            "speech_keyword": "sonar",
            "image_prompt": f"Tense sonar technician wearing bulky headphones inside dark metal submarine, {BASE_ART_STYLE}"
        },
        "culprit_role": "THE SONAR TECH",
        "culprit_speech_keyword": "sonar",
        "culprit_reason": "REASON: VOICES CANNOT TRAVEL THROUGH MILES OF OCEAN WATER!",
        "scene_prompts": {
            "hook": f"Murder crime scene inside deep-sea submarine laboratory, flashing amber emergency lights, {BASE_ART_STYLE}",
            "suspect_1": f"Submarine navigator studying green radar screen, {BASE_ART_STYLE}",
            "suspect_2": f"Female biologist with microscope in submarine lab, {BASE_ART_STYLE}",
            "suspect_3": f"Nervous sonar technician touching headphones, {BASE_ART_STYLE}",
            "reveal": f"Close-up of thick reinforced submarine titanium hull against deep dark ocean, {BASE_ART_STYLE}"
        }
    },
    {
        "topic_name": "Active Volcano Caldera Lab Murder",
        "title": "Who Killed the Volcano Scientist? 🌋 #Shorts",
        "description": "Can you spot the fatal lie in 10 seconds? Test your detective IQ!\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_theme": "Active Volcano Caldera Lab",
        "full_text": (
            "A chief volcanologist was found dead near the bubbling volcanic crater laboratory. "
            "The Seismologist stated he was calibrating ground earthquake tremor sensors. "
            "The Geologist claimed he poured a bucket of cold water directly into molten lava. "
            "The Pilot swore he was refueling the observation drone outside. "
            "One of them is lying. Spot the killer before time runs out! "
            "Three, two, one! "
            "It was the Geologist! Pouring water into molten lava causes an immediate explosive steam blast!"
        ),
        "suspect_1": {
            "role": "THE SEISMOLOGIST",
            "title": "1. THE SEISMOLOGIST",
            "alibi": "Calibrating ground earthquake tremor sensors in the station.",
            "card_text": "Claim: Calibrating ground tremor sensors.",
            "speech_keyword": "seismologist",
            "image_prompt": f"Seismologist analyzing digital earthquake waves on monitors, {BASE_ART_STYLE}"
        },
        "suspect_2": {
            "role": "THE GEOLOGIST",
            "title": "2. THE GEOLOGIST",
            "alibi": "Claimed he poured cold water into molten lava.",
            "card_text": "Claim: Poured cold water into molten lava.",
            "speech_keyword": "geologist",
            "image_prompt": f"Geologist in heat-resistant suit holding metal bucket near smoking crater, {BASE_ART_STYLE}"
        },
        "suspect_3": {
            "role": "THE PILOT",
            "title": "3. THE PILOT",
            "alibi": "Refueling the heavy observation drone on the launchpad.",
            "card_text": "Claim: Refueling drone on launchpad.",
            "speech_keyword": "pilot",
            "image_prompt": f"Drone pilot adjusting carbon fiber drone on volcanic cliff pad, {BASE_ART_STYLE}"
        },
        "culprit_role": "THE GEOLOGIST",
        "culprit_speech_keyword": "geologist",
        "culprit_reason": "REASON: WATER IN MOLTEN LAVA CAUSES EXPLOSIVE STEAM BURSTS!",
        "scene_prompts": {
            "hook": f"Crime scene at active volcano research station with glowing red magma crater, {BASE_ART_STYLE}",
            "suspect_1": f"Seismologist monitoring volcanic tremor graphs, {BASE_ART_STYLE}",
            "suspect_2": f"Geologist holding metal container near smoking red lava, {BASE_ART_STYLE}",
            "suspect_3": f"Drone pilot inspecting rotor blades, {BASE_ART_STYLE}",
            "reveal": f"Violent explosive steam eruption burst over molten orange lava, {BASE_ART_STYLE}"
        }
    },
    {
        "topic_name": "Venetian Glass Atelier Heist",
        "title": "The Venetian Gold Magnet Lie 🎭 #Shorts",
        "description": "Can you spot the fatal lie in 10 seconds? Test your detective IQ!\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_theme": "Venetian Glassblowing Furnace",
        "full_text": (
            "A wealthy art collector was murdered inside a historic Venetian glass atelier. "
            "The Master Artisan said he was blowing red-hot crystal by the roaring furnace. "
            "The Apprentice claimed he used a strong magnet to retrieve a pure gold medallion. "
            "The Dealer insisted he was packing delicate glassware in soft paper crates. "
            "One of them is lying. Spot the killer before time runs out! "
            "Three, two, one! "
            "It was the Apprentice! Magnets have zero attraction to pure twenty-four karat gold!"
        ),
        "suspect_1": {
            "role": "THE MASTER ARTISAN",
            "title": "1. THE MASTER ARTISAN",
            "alibi": "Blowing red-hot crystal vase by the roaring furnace.",
            "card_text": "Claim: Blowing glass by the furnace.",
            "speech_keyword": "artisan",
            "image_prompt": f"Elderly master glassblower shaping glowing molten glass on blowpipe, {BASE_ART_STYLE}"
        },
        "suspect_2": {
            "role": "THE APPRENTICE",
            "title": "2. THE APPRENTICE",
            "alibi": "Claimed he used magnet to retrieve pure gold medallion.",
            "card_text": "Claim: Retrieved pure gold with magnet.",
            "speech_keyword": "apprentice",
            "image_prompt": f"Young workshop apprentice holding strong horseshoe magnet, {BASE_ART_STYLE}"
        },
        "suspect_3": {
            "role": "THE DEALER",
            "title": "3. THE DEALER",
            "alibi": "Packing delicate crystal glassware into soft paper crates.",
            "card_text": "Claim: Packing crystal in crates.",
            "speech_keyword": "dealer",
            "image_prompt": f"Art dealer carefully wrapping Venetian vases in wooden crates, {BASE_ART_STYLE}"
        },
        "culprit_role": "THE APPRENTICE",
        "culprit_speech_keyword": "apprentice",
        "culprit_reason": "REASON: PURE GOLD IS NON-MAGNETIC!",
        "scene_prompts": {
            "hook": f"Crime scene in ancient Venice glass workshop, glowing orange furnace, shattered glass, {BASE_ART_STYLE}",
            "suspect_1": f"Glassblower at glowing furnace shaping molten glass, {BASE_ART_STYLE}",
            "suspect_2": f"Apprentice holding magnet near stone floor, {BASE_ART_STYLE}",
            "suspect_3": f"Dealer packing ornate vases into crates, {BASE_ART_STYLE}",
            "reveal": f"Close-up of pure 24k gold coin completely failing to stick to magnet, {BASE_ART_STYLE}"
        }
    },
    {
        "topic_name": "Arctic Glaciology Camp Sabotage",
        "title": "The Arctic Ice Core Mystery ❄️ #Shorts",
        "description": "Can you spot the fatal lie in 10 seconds? Test your detective IQ!\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_theme": "Arctic Ice Core Drilling Camp",
        "full_text": (
            "A polar expedition leader was found poisoned in the sub-zero ice research tent. "
            "The Meteorologist said she was recording wind speeds in the forty-knot blizzard. "
            "The Mechanic claimed dry ice blocks melted into a deep puddle on his desk. "
            "The Drill Tech stated he was greasing the mechanical core auger. "
            "One of them is lying. Spot the killer before time runs out! "
            "Three, two, one! "
            "It was the Mechanic! Dry ice sublimates straight into carbon dioxide gas, never melting into liquid!"
        ),
        "suspect_1": {
            "role": "THE METEOROLOGIST",
            "title": "1. THE METEOROLOGIST",
            "alibi": "Recording wind speeds outside in the freezing forty-knot blizzard.",
            "card_text": "Claim: Recording wind in blizzard.",
            "speech_keyword": "meteorologist",
            "image_prompt": f"Female meteorologist in heavy snow parka holding digital anemometer, {BASE_ART_STYLE}"
        },
        "suspect_2": {
            "role": "THE MECHANIC",
            "title": "2. THE MECHANIC",
            "alibi": "Claimed dry ice blocks melted into a liquid water puddle.",
            "card_text": "Claim: Dry ice melted into puddle.",
            "speech_keyword": "mechanic",
            "image_prompt": f"Camp mechanic in heavy thermal suit pointing to stainless steel desk, {BASE_ART_STYLE}"
        },
        "suspect_3": {
            "role": "THE DRILL TECH",
            "title": "3. THE DRILL TECH",
            "alibi": "Greasing mechanical drill bits inside the equipment shelter.",
            "card_text": "Claim: Greasing mechanical drill bits.",
            "speech_keyword": "drill",
            "image_prompt": f"Drill technician applying grease to massive spiral ice core drill, {BASE_ART_STYLE}"
        },
        "culprit_role": "THE MECHANIC",
        "culprit_speech_keyword": "mechanic",
        "culprit_reason": "REASON: DRY ICE SUBLIMATES TO GAS, IT NEVER LIQUEFIES!",
        "scene_prompts": {
            "hook": f"Crime scene inside arctic expedition dome tent surrounded by polar blizzard, {BASE_ART_STYLE}",
            "suspect_1": f"Meteorologist battling blizzard wind with weather gear, {BASE_ART_STYLE}",
            "suspect_2": f"Mechanic in arctic gear standing beside steel table, {BASE_ART_STYLE}",
            "suspect_3": f"Technician servicing industrial ice core drill, {BASE_ART_STYLE}",
            "reveal": f"Close-up of dry ice sublimating directly into thick white smoky gas, {BASE_ART_STYLE}"
        }
    },
    {
        "topic_name": "High-Security Diamond Guild Heist",
        "title": "The High-Security Diamond Lie 💎 #Shorts",
        "description": "Can you spot the fatal lie in 10 seconds? Test your detective IQ!\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_theme": "High-Security Diamond Cutting Guild",
        "full_text": (
            "A master diamond cutter was murdered inside the armored cutting laboratory vault. "
            "The Laser Tech said she was programming optical cleavage lines on computer. "
            "The Appraiser claimed he cut an uncut rough diamond in half with steel shears. "
            "The Security Guard insisted he was monitoring hallway cameras during the shift. "
            "One of them is lying. Spot the killer before time runs out! "
            "Three, two, one! "
            "It was the Appraiser! Diamonds are the hardest natural mineral and cannot be cut by steel scissors!"
        ),
        "suspect_1": {
            "role": "THE LASER TECH",
            "title": "1. THE LASER TECH",
            "alibi": "Programming optical cleavage lines on the cutting computer.",
            "card_text": "Claim: Programming laser cut lines.",
            "speech_keyword": "laser",
            "image_prompt": f"Laser technician analyzing gemstone 3D scan on computer, {BASE_ART_STYLE}"
        },
        "suspect_2": {
            "role": "THE APPRAISER",
            "title": "2. THE APPRAISER",
            "alibi": "Claimed he cleanly cut raw diamond with steel shears.",
            "card_text": "Claim: Cut diamond with steel shears.",
            "speech_keyword": "appraiser",
            "image_prompt": f"Gem appraiser holding steel shears over jewelry workbench, {BASE_ART_STYLE}"
        },
        "suspect_3": {
            "role": "THE SECURITY GUARD",
            "title": "3. THE SECURITY GUARD",
            "alibi": "Monitoring hallway surveillance cameras during the entire shift.",
            "card_text": "Claim: Monitoring security cameras.",
            "speech_keyword": "guard",
            "image_prompt": f"Security officer at multi-monitor CCTV surveillance wall, {BASE_ART_STYLE}"
        },
        "culprit_role": "THE APPRAISER",
        "culprit_speech_keyword": "appraiser",
        "culprit_reason": "REASON: STEEL SHEARS CANNOT CUT DIAMONDS!",
        "scene_prompts": {
            "hook": f"Crime scene inside high-security diamond cutting vault, scattered magnifying loupes, {BASE_ART_STYLE}",
            "suspect_1": f"Female technician programming industrial gem laser, {BASE_ART_STYLE}",
            "suspect_2": f"Appraiser holding steel cutting shears, {BASE_ART_STYLE}",
            "suspect_3": f"Security guard watching bank vault monitors, {BASE_ART_STYLE}",
            "reveal": f"Close-up of steel scissor blades bending or blunting against uncut raw diamond, {BASE_ART_STYLE}"
        }
    },
    {
        "topic_name": "24-Hour Industrial Laundromat Murder",
        "title": "The 24-Hour Laundromat Lie 🕵️ #Shorts",
        "description": "Can you spot the fatal lie in 10 seconds? Test your detective IQ!\n\n#Shorts #CrimeRiddle #Detective #Mystery #Puzzle",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_theme": "24-Hour Industrial Laundromat",
        "full_text": (
            "A midnight customer was found strangled behind the rows of industrial washing machines. "
            "The Night Attendant stated he was refilling detergent soap into high dispensers. "
            "The Cleaner swore he heard a quiet whisper over ten roaring spin-cycle machines. "
            "The Delivery Driver claimed he was unloading heavy laundry baskets from his van. "
            "One of them is lying. Spot the killer before time runs out! "
            "Three, two, one! "
            "It was the Cleaner! A faint human whisper is completely inaudible over deafening industrial washing machines!"
        ),
        "suspect_1": {
            "role": "THE NIGHT ATTENDANT",
            "title": "1. THE NIGHT ATTENDANT",
            "alibi": "Refilling liquid detergent soap into high wall dispensers.",
            "card_text": "Claim: Refilling detergent dispensers.",
            "speech_keyword": "attendant",
            "image_prompt": f"Laundromat attendant pouring blue detergent into industrial dispenser, {BASE_ART_STYLE}"
        },
        "suspect_2": {
            "role": "THE CLEANER",
            "title": "2. THE CLEANER",
            "alibi": "Swore he heard whisper over ten roaring spin-cycle machines.",
            "card_text": "Claim: Heard whisper over 10 loud machines.",
            "speech_keyword": "cleaner",
            "image_prompt": f"Night cleaner with mop listening intently beside spinning washing machines, {BASE_ART_STYLE}"
        },
        "suspect_3": {
            "role": "THE DELIVERY DRIVER",
            "title": "3. THE DELIVERY DRIVER",
            "alibi": "Unloading heavy canvas laundry baskets from his delivery van.",
            "card_text": "Claim: Unloading baskets from van.",
            "speech_keyword": "driver",
            "image_prompt": f"Delivery driver rolling heavy laundry carts into neon-lit laundromat, {BASE_ART_STYLE}"
        },
        "culprit_role": "THE CLEANER",
        "culprit_speech_keyword": "cleaner",
        "culprit_reason": "REASON: WHISPERS CANNOT BE HEARD OVER ROARING MACHINES!",
        "scene_prompts": {
            "hook": f"Crime scene inside neon-lit 24-hour industrial laundromat, flashing neon reflections, {BASE_ART_STYLE}",
            "suspect_1": f"Attendant pouring blue soap into machine hopper, {BASE_ART_STYLE}",
            "suspect_2": f"Cleaner standing near vibrating loud commercial washers, {BASE_ART_STYLE}",
            "suspect_3": f"Driver carrying canvas laundry bags near open doors, {BASE_ART_STYLE}",
            "reveal": f"Close-up of vibrating industrial drum spinning at 100 decibels, {BASE_ART_STYLE}"
        }
    }
]

def get_fallback_script(history: list) -> dict:
    """Selects an unused fallback template from the verified pool."""
    past_topics = [h.get("topic_name", "").strip().lower() for h in history]
    available = [t for t in FALLBACK_TEMPLATES if t["topic_name"].strip().lower() not in past_topics]

    if not available:
        # Exclude recent 5
        recent_5 = [h.get("topic_name", "").strip().lower() for h in history[-5:]]
        available = [t for t in FALLBACK_TEMPLATES if t["topic_name"].strip().lower() not in recent_5]
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
