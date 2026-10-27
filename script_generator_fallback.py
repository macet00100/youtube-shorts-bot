import random
import os
import json
from config import HISTORY_FILE

FALLBACK_TEMPLATES = [
    {
        "topic_name": "Midnight Cruise Murder Riddle",
        "title": "Who Is The Killer? 99% Fail This Riddle! #Shorts",
        "description": "Can you solve this luxury cruise murder mystery in 10 seconds? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "cruise ship night",
        "full_text": (
            "A billionaire was murdered near the pool of a luxury cruise ship at midnight. "
            "Three suspects were questioned by the detective. "
            "The Waiter claimed he was serving drinks at the casino lounge. "
            "The Lifeguard swore he was lying on a deck chair getting a sun tan. "
            "The Captain said he was steering the ship through the storm. "
            "One of them is lying! Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Lifeguard! You cannot get a sun tan in the middle of the night! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE WAITER",
            "title": "SUSPECT 1: THE WAITER",
            "alibi": "ALIBI: Serving drinks at casino lounge.",
            "search_keyword": "cocktail bar",
            "speech_keyword": "waiter"
        },
        "suspect_2": {
            "role": "THE LIFEGUARD",
            "title": "SUSPECT 2: THE LIFEGUARD",
            "alibi": "ALIBI: Getting a sun tan on pool deck.",
            "search_keyword": "swimming pool luxury",
            "speech_keyword": "lifeguard"
        },
        "suspect_3": {
            "role": "THE CAPTAIN",
            "title": "SUSPECT 3: THE CAPTAIN",
            "alibi": "ALIBI: Steering ship through the storm.",
            "search_keyword": "ship helm",
            "speech_keyword": "captain"
        },
        "culprit_role": "THE LIFEGUARD",
        "culprit_speech_keyword": "lifeguard",
        "culprit_reason": "REASON: NO SUNLIGHT AT MIDNIGHT!",
        "suspect_keywords": ["waiter", "lifeguard", "captain"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Sunday Mansion Murder Riddle",
        "title": "Who Is The Killer? 95% Fail This Riddle! #Shorts",
        "description": "Can you solve this mansion murder mystery in 10 seconds? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "castle storm",
        "full_text": (
            "A billionaire was murdered on a peaceful Sunday afternoon in his locked mansion. "
            "Three suspects were in the house, each with an alibi. "
            "The Butler claimed he was polishing silverware in the kitchen. "
            "The Chef said he was cooking dinner for the guests. "
            "The Maid swore she was getting mail from the mailbox outside. "
            "One of them is lying. Can you spot the killer before the timer runs out? "
            "Five, four, three, two, one! "
            "It was the Maid! The murder took place on Sunday, and there is no mail delivery on Sundays! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE BUTLER",
            "title": "SUSPECT 1: THE BUTLER",
            "alibi": "ALIBI: Polishing silverware in the kitchen.",
            "search_keyword": "waiter",
            "speech_keyword": "butler"
        },
        "suspect_2": {
            "role": "THE CHEF",
            "title": "SUSPECT 2: THE CHEF",
            "alibi": "ALIBI: Cooking dinner for the guests.",
            "search_keyword": "chef cooking",
            "speech_keyword": "chef"
        },
        "suspect_3": {
            "role": "THE MAID",
            "title": "SUSPECT 3: THE MAID",
            "alibi": "ALIBI: Getting mail from mailbox outside.",
            "search_keyword": "rain letter",
            "speech_keyword": "maid"
        },
        "culprit_role": "THE MAID",
        "culprit_speech_keyword": "maid",
        "culprit_reason": "REASON: NO MAIL DELIVERY ON SUNDAY!",
        "suspect_keywords": ["butler", "chef", "maid"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_3.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    }
]

def get_fallback_script(history: list) -> dict:
    recent = [h.get("topic_name", "") for h in history[-5:]] if history else []
    avail = [t for t in FALLBACK_TEMPLATES if t["topic_name"] not in recent]
    if not avail:
        avail = FALLBACK_TEMPLATES
    selected = random.choice(avail)
    history.append({
        "topic_name": selected["topic_name"],
        "title": selected["title"],
        "generated_at": str(os.getenv("GITHUB_RUN_ID", "fallback"))
    })
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return selected
