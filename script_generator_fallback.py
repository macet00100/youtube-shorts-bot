import random
import os
import json
from config import HISTORY_FILE

FALLBACK_TEMPLATES = [
    {
        "topic_name": "Submarine Abyss Lab Mystery",
        "title": "Who Is The Killer? 95% Fail This Riddle! #Shorts",
        "description": "Can you solve this deep-sea submarine mystery in 10 seconds? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "submarine underwater dark",
        "full_text": (
            "A marine scientist was murdered inside a deep-sea submarine lab two miles underwater. "
            "The detective questioned three suspects onboard. "
            "The Navigator claimed he was checking underwater coordinates on the radar. "
            "The Biologist said she was examining deep sea coral samples under the microscope. "
            "The Sonar Tech swore he heard the victim scream outside in the open water. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Sonar Tech! Human voices cannot travel through miles of deep pressurized water! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE NAVIGATOR",
            "title": "SUSPECT 1: THE NAVIGATOR",
            "alibi": "ALIBI: Checking underwater coordinates on radar.",
            "search_keyword": "radar screen tech",
            "speech_keyword": "navigator"
        },
        "suspect_2": {
            "role": "THE BIOLOGIST",
            "title": "SUSPECT 2: THE BIOLOGIST",
            "alibi": "ALIBI: Examining deep coral under microscope.",
            "search_keyword": "microscope laboratory",
            "speech_keyword": "biologist"
        },
        "suspect_3": {
            "role": "THE SONAR TECH",
            "title": "SUSPECT 3: THE SONAR TECH",
            "alibi": "ALIBI: Heard victim scream outside in water.",
            "search_keyword": "sonar headphones",
            "speech_keyword": "tech"
        },
        "culprit_role": "THE SONAR TECH",
        "culprit_speech_keyword": "tech",
        "culprit_reason": "REASON: NO VOICES HEARD OUTSIDE SUB HULL!",
        "suspect_keywords": ["navigator", "biologist", "tech"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_3.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Mars Habitat Dome Sabotage",
        "title": "Can You Spot The Liar In 10 Seconds? 🕵️‍♂️ #Shorts",
        "description": "Can you solve this Mars space colony crime riddle? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "mars planet surface space",
        "full_text": (
            "A commander was found poisoned inside the pressurized Mars habitat dome. "
            "Three crew members were immediately interrogated by the captain. "
            "The Botanist claimed he went outside to light a candle for celebration. "
            "The Engineer swore she was calibrating solar panels in the control room. "
            "The Geologist stated he was sorting rock specimens inside the airlock. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Botanist! A candle cannot burn outside on Mars because there is no oxygen! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE BOTANIST",
            "title": "SUSPECT 1: THE BOTANIST",
            "alibi": "ALIBI: Lighting a candle outside on Mars surface.",
            "search_keyword": "botanist plants space",
            "speech_keyword": "botanist"
        },
        "suspect_2": {
            "role": "THE ENGINEER",
            "title": "SUSPECT 2: THE ENGINEER",
            "alibi": "ALIBI: Calibrating solar panels in control room.",
            "search_keyword": "control room tech",
            "speech_keyword": "engineer"
        },
        "suspect_3": {
            "role": "THE GEOLOGIST",
            "title": "SUSPECT 3: THE GEOLOGIST",
            "alibi": "ALIBI: Sorting rock specimens inside airlock.",
            "search_keyword": "geologist rocks laboratory",
            "speech_keyword": "geologist"
        },
        "culprit_role": "THE BOTANIST",
        "culprit_speech_keyword": "botanist",
        "culprit_reason": "REASON: CANDLES CANNOT BURN ON AIRLESS MARS!",
        "suspect_keywords": ["botanist", "engineer", "geologist"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_1.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Venetian Glass Atelier Heist",
        "title": "Only A True Detective Catches The Flaw! #Shorts",
        "description": "Can you solve this Venice workshop murder mystery? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "glassblowing workshop fire",
        "full_text": (
            "A wealthy art collector was found dead inside a historic Venice glass workshop. "
            "The inspector questioned three people present at the atelier. "
            "The Master Artisan said he was blowing a crystal vase by the furnace. "
            "The Apprentice claimed he used a strong magnet to retrieve a dropped solid gold coin. "
            "The Art Dealer insisted he was packing delicate glassware into wooden crates. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Apprentice! Magnets do not attract pure solid gold! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE MASTER ARTISAN",
            "title": "SUSPECT 1: THE MASTER ARTISAN",
            "alibi": "ALIBI: Blowing crystal vase by the furnace.",
            "search_keyword": "glassblowing molten glass",
            "speech_keyword": "artisan"
        },
        "suspect_2": {
            "role": "THE APPRENTICE",
            "title": "SUSPECT 2: THE APPRENTICE",
            "alibi": "ALIBI: Using magnet to pick up pure gold coin.",
            "search_keyword": "workshop apprentice tools",
            "speech_keyword": "apprentice"
        },
        "suspect_3": {
            "role": "THE ART DEALER",
            "title": "SUSPECT 3: THE ART DEALER",
            "alibi": "ALIBI: Packing delicate glassware in crates.",
            "search_keyword": "antique warehouse packing",
            "speech_keyword": "dealer"
        },
        "culprit_role": "THE APPRENTICE",
        "culprit_speech_keyword": "apprentice",
        "culprit_reason": "REASON: MAGNETS DO NOT ATTRACT PURE GOLD!",
        "suspect_keywords": ["artisan", "apprentice", "dealer"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Sahara Desert Archaeological Dig",
        "title": "99% Miss The Clue! Who Murdered The Professor? #Shorts",
        "description": "Can you solve this desert excavation crime riddle? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "desert dunes sun sand",
        "full_text": (
            "A famous archaeologist was found dead at a remote Sahara desert campsite. "
            "The investigator interrogated three crew members at the tent. "
            "The Camp Cook claimed he was boiling water for tea inside the kitchen tent. "
            "The Field Guide swore he heard the victim's echo bouncing off the flat sand dunes. "
            "The Photographer said she was cleaning sand from her camera lenses. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Field Guide! Sound cannot produce an echo across wide, flat open sand dunes! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE CAMP COOK",
            "title": "SUSPECT 1: THE CAMP COOK",
            "alibi": "ALIBI: Boiling water for tea inside tent.",
            "search_keyword": "cooking camping tent",
            "speech_keyword": "cook"
        },
        "suspect_2": {
            "role": "THE FIELD GUIDE",
            "title": "SUSPECT 2: THE FIELD GUIDE",
            "alibi": "ALIBI: Hearing echo bouncing off sand dunes.",
            "search_keyword": "desert sand dunes guide",
            "speech_keyword": "guide"
        },
        "suspect_3": {
            "role": "THE PHOTOGRAPHER",
            "title": "SUSPECT 3: THE PHOTOGRAPHER",
            "alibi": "ALIBI: Cleaning sand from camera lenses.",
            "search_keyword": "photographer camera desert",
            "speech_keyword": "photographer"
        },
        "culprit_role": "THE FIELD GUIDE",
        "culprit_speech_keyword": "guide",
        "culprit_reason": "REASON: NO ECHO ON FLAT DESERT SAND!",
        "suspect_keywords": ["cook", "guide", "photographer"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Renaissance Clock Tower Mystery",
        "title": "Who Is The Killer? 95% Fail This Riddle! #Shorts",
        "description": "Can you solve this clockmaker murder mystery? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "clock tower gears vintage",
        "full_text": (
            "A master clockmaker was murdered inside an ancient town clock tower during a storm. "
            "The detective questioned three workers found in the tower. "
            "The Apprentice claimed he was oiling the giant iron brass gears. "
            "The Horologist said he was assembling a miniature gold pocket watch. "
            "The Bellringer swore he was checking the roof sundial during the thunderstorm. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Bellringer! A sundial cannot cast a shadow during a dark thunderstorm! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE APPRENTICE",
            "title": "SUSPECT 1: THE APPRENTICE",
            "alibi": "ALIBI: Oiling brass gears inside clock.",
            "search_keyword": "clockwork gears antique",
            "speech_keyword": "apprentice"
        },
        "suspect_2": {
            "role": "THE HOROLOGIST",
            "title": "SUSPECT 2: THE HOROLOGIST",
            "alibi": "ALIBI: Assembling gold pocket watch.",
            "search_keyword": "watchmaker tools vintage",
            "speech_keyword": "horologist"
        },
        "suspect_3": {
            "role": "THE BELLRINGER",
            "title": "SUSPECT 3: THE BELLRINGER",
            "alibi": "ALIBI: Checking roof sundial during storm.",
            "search_keyword": "church bell tower rain",
            "speech_keyword": "bellringer"
        },
        "culprit_role": "THE BELLRINGER",
        "culprit_speech_keyword": "bellringer",
        "culprit_reason": "REASON: SUNDIALS DO NOT WORK IN STORMS!",
        "suspect_keywords": ["apprentice", "horologist", "bellringer"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_3.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Supersonic Private Jet Murder",
        "title": "Can You Spot The Liar In 10 Seconds? 🕵️‍♂️ #Shorts",
        "description": "Can you solve this high-altitude airplane crime riddle? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "private jet airplane flying",
        "full_text": (
            "A tech CEO was murdered mid-flight on a private jet cruising at forty thousand feet. "
            "The onboard marshal questioned the three other passengers. "
            "The Flight Attendant said she was preparing champagne cocktails in the galley. "
            "The VIP Guest claimed he stepped outside onto the wing to get fresh air. "
            "The Co-Pilot stated he was monitoring navigation displays in the cockpit. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the VIP Guest! Cabin doors cannot be opened at forty thousand feet cruising altitude! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE FLIGHT ATTENDANT",
            "title": "SUSPECT 1: THE FLIGHT ATTENDANT",
            "alibi": "ALIBI: Preparing champagne in galley.",
            "search_keyword": "flight attendant cabin",
            "speech_keyword": "attendant"
        },
        "suspect_2": {
            "role": "THE VIP GUEST",
            "title": "SUSPECT 2: THE VIP GUEST",
            "alibi": "ALIBI: Stepping outside on wing for fresh air.",
            "search_keyword": "business luxury passenger",
            "speech_keyword": "guest"
        },
        "suspect_3": {
            "role": "THE CO-PILOT",
            "title": "SUSPECT 3: THE CO-PILOT",
            "alibi": "ALIBI: Monitoring navigation in cockpit.",
            "search_keyword": "airplane cockpit controls",
            "speech_keyword": "pilot"
        },
        "culprit_role": "THE VIP GUEST",
        "culprit_speech_keyword": "guest",
        "culprit_reason": "REASON: CANNOT OPEN CABIN DOORS AT 40,000FT!",
        "suspect_keywords": ["attendant", "guest", "pilot"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Formula 1 Racing Garage Mystery",
        "title": "Only 5% Of Detectives Solve This Riddle! #Shorts",
        "description": "Can you solve this high-speed racing paddock mystery in 10s? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "formula racing car garage",
        "full_text": (
            "A chief racing engineer was found dead in the garage right after the qualifying lap. "
            "The track inspector questioned three team members on duty. "
            "The Lead Mechanic claimed he was changing tires with the pneumatic air gun. "
            "The Reserve Driver swore he touched the glowing red carbon brake disc with bare hands. "
            "The Data Analyst said she was reviewing telemetry data on her laptop. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Reserve Driver! Glowing racing brake discs reach one thousand degrees and burn instantly! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE LEAD MECHANIC",
            "title": "SUSPECT 1: THE LEAD MECHANIC",
            "alibi": "ALIBI: Changing tires with pneumatic gun.",
            "search_keyword": "race car mechanic garage",
            "speech_keyword": "mechanic"
        },
        "suspect_2": {
            "role": "THE RESERVE DRIVER",
            "title": "SUSPECT 2: THE RESERVE DRIVER",
            "alibi": "ALIBI: Touching red-hot brake disc barehanded.",
            "search_keyword": "racing driver helmet suit",
            "speech_keyword": "driver"
        },
        "suspect_3": {
            "role": "THE DATA ANALYST",
            "title": "SUSPECT 3: THE DATA ANALYST",
            "alibi": "ALIBI: Reviewing telemetry data on laptop.",
            "search_keyword": "data analyst screens office",
            "speech_keyword": "analyst"
        },
        "culprit_role": "THE RESERVE DRIVER",
        "culprit_speech_keyword": "driver",
        "culprit_reason": "REASON: GLOWING BRAKE DISCS CAUSE SEVERE BURNS!",
        "suspect_keywords": ["mechanic", "driver", "analyst"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Cryogenic Supercomputer Server Vault",
        "title": "Can You Catch The Killer Before Time Out? #Shorts",
        "description": "Can you solve this high-tech server vault crime riddle? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "server room technology blue",
        "full_text": (
            "A cyber security director was found unconscious inside a sub-zero server facility. "
            "The investigator interrogated three employees on the midnight shift. "
            "The Security Guard claimed he was watching surveillance monitors at the front desk. "
            "The Network Admin said she was rerouting fiber optic cables in the hallway. "
            "The Hardware Tech swore he was dripping sweat from the intense heat inside the server room. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Hardware Tech! Server rooms are chilled to freezing temperatures, so nobody sweats from heat! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE SECURITY GUARD",
            "title": "SUSPECT 1: THE SECURITY GUARD",
            "alibi": "ALIBI: Watching security monitors at desk.",
            "search_keyword": "security monitor screens",
            "speech_keyword": "guard"
        },
        "suspect_2": {
            "role": "THE NETWORK ADMIN",
            "title": "SUSPECT 2: THE NETWORK ADMIN",
            "alibi": "ALIBI: Rerouting fiber cables in hallway.",
            "search_keyword": "cables network server rack",
            "speech_keyword": "admin"
        },
        "suspect_3": {
            "role": "THE HARDWARE TECH",
            "title": "SUSPECT 3: THE HARDWARE TECH",
            "alibi": "ALIBI: Sweating from heat inside server room.",
            "search_keyword": "computer hardware repair",
            "speech_keyword": "tech"
        },
        "culprit_role": "THE HARDWARE TECH",
        "culprit_speech_keyword": "tech",
        "culprit_reason": "REASON: SERVER ROOMS ARE ICY COLD, NOT HOT!",
        "suspect_keywords": ["guard", "admin", "tech"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_3.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Royal Rare Manuscript Archive",
        "title": "Detective IQ Test: Can You Spot The Killer? #Shorts",
        "description": "Can you solve this library archive murder mystery in 10s? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "ancient library books dark",
        "full_text": (
            "A chief historian was murdered in the high-security vault of an ancient royal library. "
            "The detective questioned three scholars present. "
            "The Archivist said she was cataloging ancient scrolls with white gloves. "
            "The Bookbinder claimed he found a hidden poisoned needle between facing pages 100 and 101. "
            "The Collector stated he was inspecting gold bindings with a magnifying glass. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Bookbinder! In any bound book, pages 100 and 101 are on opposite sides of the same page! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE ARCHIVIST",
            "title": "SUSPECT 1: THE ARCHIVIST",
            "alibi": "ALIBI: Cataloging ancient scrolls with gloves.",
            "search_keyword": "old manuscript library gloves",
            "speech_keyword": "archivist"
        },
        "suspect_2": {
            "role": "THE BOOKBINDER",
            "title": "SUSPECT 2: THE BOOKBINDER",
            "alibi": "ALIBI: Finding needle between pages 100 and 101.",
            "search_keyword": "bookbinding antique leather",
            "speech_keyword": "bookbinder"
        },
        "suspect_3": {
            "role": "THE COLLECTOR",
            "title": "SUSPECT 3: THE COLLECTOR",
            "alibi": "ALIBI: Inspecting gold bindings with glass.",
            "search_keyword": "magnifying glass old book",
            "speech_keyword": "collector"
        },
        "culprit_role": "THE BOOKBINDER",
        "culprit_speech_keyword": "bookbinder",
        "culprit_reason": "REASON: PAGES 100 AND 101 ARE BACK-TO-BACK!",
        "suspect_keywords": ["archivist", "bookbinder", "collector"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Michelin Omakase Restaurant Mystery",
        "title": "Only A True Detective Catches The Flaw! #Shorts",
        "description": "Can you solve this gourmet restaurant crime riddle? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "sushi chef restaurant kitchen",
        "full_text": (
            "A food critic was poisoned in a private dining room at a luxury sushi restaurant. "
            "The inspector questioned three members of the kitchen staff. "
            "The Head Chef said he was slicing fresh bluefin tuna with his knife. "
            "The Sommelier claimed he completely dissolved rock salt into pure sesame oil for sauce. "
            "The Dishwasher stated he was sterilizing ceramic plates in steaming hot water. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Sommelier! Salt cannot dissolve into pure oil without water! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE HEAD CHEF",
            "title": "SUSPECT 1: THE HEAD CHEF",
            "alibi": "ALIBI: Slicing bluefin tuna with knife.",
            "search_keyword": "sushi chef cutting knife",
            "speech_keyword": "chef"
        },
        "suspect_2": {
            "role": "THE SOMMELIER",
            "title": "SUSPECT 2: THE SOMMELIER",
            "alibi": "ALIBI: Dissolving rock salt in pure oil.",
            "search_keyword": "wine sommelier restaurant",
            "speech_keyword": "sommelier"
        },
        "suspect_3": {
            "role": "THE DISHWASHER",
            "title": "SUSPECT 3: THE DISHWASHER",
            "alibi": "ALIBI: Sterilizing plates in hot water.",
            "search_keyword": "kitchen dishwasher steam",
            "speech_keyword": "dishwasher"
        },
        "culprit_role": "THE SOMMELIER",
        "culprit_speech_keyword": "sommelier",
        "culprit_reason": "REASON: SALT CANNOT DISSOLVE IN PURE OIL!",
        "suspect_keywords": ["chef", "sommelier", "dishwasher"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Rooftop Honeybee Apiary Case",
        "title": "Who Is The Killer? 95% Fail This Riddle! #Shorts",
        "description": "Can you solve this rooftop honeybee mystery in 10 seconds? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "honey bees beehive rain",
        "full_text": (
            "A penthouse owner was found murdered on his luxury skyscraper rooftop garden. "
            "The detective questioned three workers found near the scene during heavy rain. "
            "The Beekeeper swore the bees were actively swarming and flying during the storm. "
            "The Building Super claimed he was checking roof water drains with a flashlight. "
            "The Landscaper said he was tying down patio furniture against the high winds. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Beekeeper! Honeybees never fly or swarm during a heavy rainstorm! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE BEEKEEPER",
            "title": "SUSPECT 1: THE BEEKEEPER",
            "alibi": "ALIBI: Bees were swarming during heavy rain.",
            "search_keyword": "beekeeper beehive honey",
            "speech_keyword": "beekeeper"
        },
        "suspect_2": {
            "role": "THE BUILDING SUPER",
            "title": "SUSPECT 2: THE BUILDING SUPER",
            "alibi": "ALIBI: Checking roof drains with flashlight.",
            "search_keyword": "maintenance worker flashlight",
            "speech_keyword": "super"
        },
        "suspect_3": {
            "role": "THE LANDSCAPER",
            "title": "SUSPECT 3: THE LANDSCAPER",
            "alibi": "ALIBI: Tying down patio furniture in wind.",
            "search_keyword": "rooftop garden furniture",
            "speech_keyword": "landscaper"
        },
        "culprit_role": "THE BEEKEEPER",
        "culprit_speech_keyword": "beekeeper",
        "culprit_reason": "REASON: BEES NEVER FLY IN HEAVY RAINSTORMS!",
        "suspect_keywords": ["beekeeper", "super", "landscaper"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_1.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Vintage Neon Bowling Alley Mystery",
        "title": "Can You Spot The Liar In 10 Seconds? 🕵️‍♂️ #Shorts",
        "description": "Can you solve this retro bowling alley murder mystery? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "bowling alley neon lights",
        "full_text": (
            "A bowling alley owner was found dead behind the pin machines late at night. "
            "The detective questioned three people inside the building. "
            "The Lane Mechanic claimed he was clearing a bowling pin jam in lane seven. "
            "The Cashier said she was counting cash bills inside the locked front office. "
            "The League Champion swore his cigarette smoke was falling straight down like water. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the League Champion! Warm smoke always rises upward because it is lighter than air! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE LANE MECHANIC",
            "title": "SUSPECT 1: THE LANE MECHANIC",
            "alibi": "ALIBI: Clearing pin jam in lane seven.",
            "search_keyword": "bowling pins machine lane",
            "speech_keyword": "mechanic"
        },
        "suspect_2": {
            "role": "THE CASHIER",
            "title": "SUSPECT 2: THE CASHIER",
            "alibi": "ALIBI: Counting bills in front office.",
            "search_keyword": "cash register money counting",
            "speech_keyword": "cashier"
        },
        "suspect_3": {
            "role": "THE LEAGUE CHAMPION",
            "title": "SUSPECT 3: THE LEAGUE CHAMPION",
            "alibi": "ALIBI: Cigarette smoke falling straight down.",
            "search_keyword": "bowling player alley ball",
            "speech_keyword": "champion"
        },
        "culprit_role": "THE LEAGUE CHAMPION",
        "culprit_speech_keyword": "champion",
        "culprit_reason": "REASON: WARM SMOKE RISES, IT NEVER FALLS!",
        "suspect_keywords": ["mechanic", "cashier", "champion"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_3.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "High-Security Diamond Cutting Guild",
        "title": "99% Miss The Clue! Who Murdered The Jeweler? #Shorts",
        "description": "Can you solve this diamond vault murder mystery in 10s? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "diamond jewelry vault sparkle",
        "full_text": (
            "A master jeweler was found dead inside the fortified vault of a diamond exchange. "
            "The investigator questioned three people locked in the room. "
            "The Gemologist said she was grading clarity under a high-power microscope. "
            "The Vault Guard claimed he accidentally sliced a raw diamond in half with steel scissors. "
            "The Diamond Cutter stated he was cutting facets with a laser cutting machine. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Vault Guard! Diamonds are the hardest natural mineral and cannot be cut by steel scissors! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE GEMOLOGIST",
            "title": "SUSPECT 1: THE GEMOLOGIST",
            "alibi": "ALIBI: Grading clarity under microscope.",
            "search_keyword": "gemologist loupe diamond",
            "speech_keyword": "gemologist"
        },
        "suspect_2": {
            "role": "THE VAULT GUARD",
            "title": "SUSPECT 2: THE VAULT GUARD",
            "alibi": "ALIBI: Cutting diamond with steel scissors.",
            "search_keyword": "vault security officer guard",
            "speech_keyword": "guard"
        },
        "suspect_3": {
            "role": "THE DIAMOND CUTTER",
            "title": "SUSPECT 3: THE DIAMOND CUTTER",
            "alibi": "ALIBI: Cutting facets with laser machine.",
            "search_keyword": "laser machine cutting metal",
            "speech_keyword": "cutter"
        },
        "culprit_role": "THE VAULT GUARD",
        "culprit_speech_keyword": "guard",
        "culprit_reason": "REASON: SCISSORS CANNOT CUT HARD DIAMONDS!",
        "suspect_keywords": ["gemologist", "guard", "cutter"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Himalayan Alpine Basecamp Case",
        "title": "Who Is The Killer? 95% Fail This Riddle! #Shorts",
        "description": "Can you solve this snowy mountain mystery in 10 seconds? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "snow mountain tent basecamp",
        "full_text": (
            "A climber was discovered poisoned at Mount Everest base camp at eighteen thousand feet. "
            "The expedition leader questioned three mountaineers in the tent. "
            "The Sherpa Guide said he was checking oxygen tanks and climbing ropes. "
            "The Doctor claimed he boiled hot water up to one hundred and twenty degrees Celsius on the camp stove. "
            "The Photographer said she was drying frozen camera batteries in her sleeping bag. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Doctor! At high altitude, water boils at much lower temperatures, never above one hundred! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE SHERPA GUIDE",
            "title": "SUSPECT 1: THE SHERPA GUIDE",
            "alibi": "ALIBI: Checking oxygen tanks and ropes.",
            "search_keyword": "mountain climbing gear rope",
            "speech_keyword": "guide"
        },
        "suspect_2": {
            "role": "THE DOCTOR",
            "title": "SUSPECT 2: THE DOCTOR",
            "alibi": "ALIBI: Boiling water to 120°C on camp stove.",
            "search_keyword": "camping stove boiling pot",
            "speech_keyword": "doctor"
        },
        "suspect_3": {
            "role": "THE PHOTOGRAPHER",
            "title": "SUSPECT 3: THE PHOTOGRAPHER",
            "alibi": "ALIBI: Drying camera batteries in sleeping bag.",
            "search_keyword": "winter expedition snow tent",
            "speech_keyword": "photographer"
        },
        "culprit_role": "THE DOCTOR",
        "culprit_speech_keyword": "doctor",
        "culprit_reason": "REASON: WATER BOILS LOWER AT HIGH ALTITUDES!",
        "suspect_keywords": ["guide", "doctor", "photographer"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Stradivarius Violin Atelier Crime",
        "title": "Only A True Detective Catches The Flaw! #Shorts",
        "description": "Can you solve this master violin craftsman murder mystery? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "violin craft wood workshop",
        "full_text": (
            "A master luthier was found dead inside his acoustic violin workshop. "
            "The detective questioned three musicians present at the studio. "
            "The Master Craftsman said he was carving maple wood for a cello bridge. "
            "The Apprentice claimed he applied traditional oil varnish five minutes ago and it dried completely solid. "
            "The Virtuoso stated she was tuning synthetic violin strings with a tuning fork. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Apprentice! Traditional oil varnish takes several days to dry, never five minutes! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE MASTER CRAFTSMAN",
            "title": "SUSPECT 1: THE MASTER CRAFTSMAN",
            "alibi": "ALIBI: Carving maple wood for cello bridge.",
            "search_keyword": "woodcarving tools artisan",
            "speech_keyword": "craftsman"
        },
        "suspect_2": {
            "role": "THE APPRENTICE",
            "title": "SUSPECT 2: THE APPRENTICE",
            "alibi": "ALIBI: Oil varnish dried in 5 minutes.",
            "search_keyword": "varnish painting brush wood",
            "speech_keyword": "apprentice"
        },
        "suspect_3": {
            "role": "THE VIRTUOSO",
            "title": "SUSPECT 3: THE VIRTUOSO",
            "alibi": "ALIBI: Tuning violin with tuning fork.",
            "search_keyword": "violin player music acoustic",
            "speech_keyword": "virtuoso"
        },
        "culprit_role": "THE APPRENTICE",
        "culprit_speech_keyword": "apprentice",
        "culprit_reason": "REASON: OIL VARNISH TAKES DAYS TO DRY!",
        "suspect_keywords": ["craftsman", "apprentice", "virtuoso"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Historic Currency Mint Heist",
        "title": "Detective IQ Test: Can You Spot The Killer? #Shorts",
        "description": "Can you solve this money mint crime riddle in 10s? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "printing press factory money",
        "full_text": (
            "A security supervisor was found locked in the vault of the national currency mint. "
            "The inspector questioned three employees on the security floor. "
            "The Press Operator said he was replacing engraving plates on the printing press. "
            "The Vault Inspector claimed he deposited new gold reserves on the afternoon of February 30th. "
            "The Security Officer stated he was testing emergency alarm sirens in the corridor. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Vault Inspector! February never has thirty days in any calendar year! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE PRESS OPERATOR",
            "title": "SUSPECT 1: THE PRESS OPERATOR",
            "alibi": "ALIBI: Replacing engraving plates on press.",
            "search_keyword": "printing press machine factory",
            "speech_keyword": "operator"
        },
        "suspect_2": {
            "role": "THE VAULT INSPECTOR",
            "title": "SUSPECT 2: THE VAULT INSPECTOR",
            "alibi": "ALIBI: Deposited gold on February 30th.",
            "search_keyword": "gold vault bullion bars",
            "speech_keyword": "inspector"
        },
        "suspect_3": {
            "role": "THE SECURITY OFFICER",
            "title": "SUSPECT 3: THE SECURITY OFFICER",
            "alibi": "ALIBI: Testing alarm sirens in corridor.",
            "search_keyword": "security alarm siren lights",
            "speech_keyword": "officer"
        },
        "culprit_role": "THE VAULT INSPECTOR",
        "culprit_speech_keyword": "inspector",
        "culprit_reason": "REASON: FEBRUARY NEVER HAS 30 DAYS!",
        "suspect_keywords": ["operator", "inspector", "officer"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Transatlantic Zeppelin Airship Mystery",
        "title": "Who Is The Killer? 95% Fail This Riddle! #Shorts",
        "description": "Can you solve this vintage airship murder mystery in 10s? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "airship zeppelin clouds storm",
        "full_text": (
            "A wealthy diplomat was found stabbed aboard an airship flying through a storm. "
            "The captain questioned three individuals in the luxury observation lounge. "
            "The Navigator said he was calculating air speed using barometric gauges. "
            "The Luxury Steward claimed he was serving iced martinis to the passengers. "
            "The Radio Operator swore he heard thunder rumble three seconds before the lightning flash. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Radio Operator! Light travels faster than sound, so lightning is always seen before thunder! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE NAVIGATOR",
            "title": "SUSPECT 1: THE NAVIGATOR",
            "alibi": "ALIBI: Calculating air speed with gauges.",
            "search_keyword": "navigation map instruments compass",
            "speech_keyword": "navigator"
        },
        "suspect_2": {
            "role": "THE LUXURY STEWARD",
            "title": "SUSPECT 2: THE LUXURY STEWARD",
            "alibi": "ALIBI: Serving iced martinis to passengers.",
            "search_keyword": "cocktail waiter luxury bar",
            "speech_keyword": "steward"
        },
        "suspect_3": {
            "role": "THE RADIO OPERATOR",
            "title": "SUSPECT 3: THE RADIO OPERATOR",
            "alibi": "ALIBI: Heard thunder before lightning flash.",
            "search_keyword": "vintage radio operator dials",
            "speech_keyword": "operator"
        },
        "culprit_role": "THE RADIO OPERATOR",
        "culprit_speech_keyword": "operator",
        "culprit_reason": "REASON: LIGHTNING ALWAYS PRECEDES THUNDER!",
        "suspect_keywords": ["navigator", "steward", "operator"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_3.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Active Volcano Caldera Station",
        "title": "Can You Spot The Liar In 10 Seconds? 🕵️‍♂️ #Shorts",
        "description": "Can you solve this volcano research station crime riddle? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "volcano lava smoke mountain",
        "full_text": (
            "A chief seismologist was found dead at an observation shelter near an active volcano rim. "
            "The investigator questioned three researchers in the cabin. "
            "The Drone Pilot said he was flying a thermal drone over the smoking crater. "
            "The Volcanologist claimed he put ice cubes in a cup of water and watched them sink to the bottom. "
            "The Park Ranger stated he was measuring sulfur gas levels outside with a detector. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Volcanologist! Ice is less dense than water and will always float to the top! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE DRONE PILOT",
            "title": "SUSPECT 1: THE DRONE PILOT",
            "alibi": "ALIBI: Flying thermal drone over crater.",
            "search_keyword": "drone pilot screen controller",
            "speech_keyword": "pilot"
        },
        "suspect_2": {
            "role": "THE VOLCANOLOGIST",
            "title": "SUSPECT 2: THE VOLCANOLOGIST",
            "alibi": "ALIBI: Ice cubes sank to bottom of water cup.",
            "search_keyword": "volcanologist research lava",
            "speech_keyword": "volcanologist"
        },
        "suspect_3": {
            "role": "THE PARK RANGER",
            "title": "SUSPECT 3: THE PARK RANGER",
            "alibi": "ALIBI: Measuring sulfur gas with detector.",
            "search_keyword": "park ranger uniform mountain",
            "speech_keyword": "ranger"
        },
        "culprit_role": "THE VOLCANOLOGIST",
        "culprit_speech_keyword": "volcanologist",
        "culprit_reason": "REASON: ICE ALWAYS FLOATS IN WATER!",
        "suspect_keywords": ["pilot", "volcanologist", "ranger"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Midnight Film Studio Soundstage",
        "title": "Only 5% Of Detectives Solve This Riddle! #Shorts",
        "description": "Can you solve this Hollywood soundstage murder mystery? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "movie studio spotlight dark",
        "full_text": (
            "A movie director was found murdered on soundstage four during a late night film shoot. "
            "The detective questioned three crew members present on the set. "
            "The Lead Actor claimed he was rehearsing his monologue inside his dressing room trailer. "
            "The Prop Master said he was cataloging stunt pistols in the locked prop room. "
            "The Lighting Tech swore his shadow was pointing directly towards the bright spotlight. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Lighting Tech! Shadows always fall directly opposite to the light source! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE LEAD ACTOR",
            "title": "SUSPECT 1: THE LEAD ACTOR",
            "alibi": "ALIBI: Rehearsing monologue in trailer.",
            "search_keyword": "actor mirror dressing room",
            "speech_keyword": "actor"
        },
        "suspect_2": {
            "role": "THE PROP MASTER",
            "title": "SUSPECT 2: THE PROP MASTER",
            "alibi": "ALIBI: Cataloging stunt pistols in prop room.",
            "search_keyword": "props room stage gear",
            "speech_keyword": "master"
        },
        "suspect_3": {
            "role": "THE LIGHTING TECH",
            "title": "SUSPECT 3: THE LIGHTING TECH",
            "alibi": "ALIBI: Shadow pointing towards spotlight.",
            "search_keyword": "lighting technician spotlight",
            "speech_keyword": "tech"
        },
        "culprit_role": "THE LIGHTING TECH",
        "culprit_speech_keyword": "tech",
        "culprit_reason": "REASON: SHADOWS FALL OPPOSITE TO LIGHT!",
        "suspect_keywords": ["actor", "master", "tech"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_3.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Underground Metro Central Signal Box",
        "title": "Who Is The Killer? 95% Fail This Riddle! #Shorts",
        "description": "Can you solve this subway control room murder mystery? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "subway tunnel train dark",
        "full_text": (
            "A subway transit director was found dead in the underground central dispatch center. "
            "The inspector questioned three railway workers on the late shift. "
            "The Dispatcher said she was monitoring track signals on the computer wall. "
            "The Track Inspector claimed he was replacing rail bolts in the maintenance tunnel. "
            "The Train Operator swore his train sped up and overtook the express train on a single one-way track. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Train Operator! Trains cannot overtake each other on a single one-way track! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE DISPATCHER",
            "title": "SUSPECT 1: THE DISPATCHER",
            "alibi": "ALIBI: Monitoring signals on computer wall.",
            "search_keyword": "subway dispatch screens monitor",
            "speech_keyword": "dispatcher"
        },
        "suspect_2": {
            "role": "THE TRACK INSPECTOR",
            "title": "SUSPECT 2: THE TRACK INSPECTOR",
            "alibi": "ALIBI: Replacing rail bolts in tunnel.",
            "search_keyword": "railroad track maintenance worker",
            "speech_keyword": "inspector"
        },
        "suspect_3": {
            "role": "THE TRAIN OPERATOR",
            "title": "SUSPECT 3: THE TRAIN OPERATOR",
            "alibi": "ALIBI: Train overtook another on single track.",
            "search_keyword": "train conductor driver subway",
            "speech_keyword": "operator"
        },
        "culprit_role": "THE TRAIN OPERATOR",
        "culprit_speech_keyword": "operator",
        "culprit_reason": "REASON: CANNOT OVERTAKE ON SINGLE TRACK!",
        "suspect_keywords": ["dispatcher", "inspector", "operator"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_3.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Botanical Poison Conservatory Case",
        "title": "Can You Catch The Killer Before Time Out? #Shorts",
        "description": "Can you solve this poisonous garden crime riddle? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "botanical garden flowers mist",
        "full_text": (
            "A chief botanist was found poisoned inside a locked rare toxic plant greenhouse. "
            "The investigator questioned three people present in the facility. "
            "The Toxicologist claimed he was analyzing lethal belladonna root samples. "
            "The Chemistry Student swore the apple slices on the laboratory bench stayed pure white for six hours. "
            "The Head Caretaker stated he was pruning dead leaves from poisonous vines. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Chemistry Student! Sliced apples oxidize and turn brown within minutes in open air! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE TOXICOLOGIST",
            "title": "SUSPECT 1: THE TOXICOLOGIST",
            "alibi": "ALIBI: Analyzing belladonna root samples.",
            "search_keyword": "chemistry lab flasks toxic",
            "speech_keyword": "toxicologist"
        },
        "suspect_2": {
            "role": "THE CHEMISTRY STUDENT",
            "title": "SUSPECT 2: THE CHEMISTRY STUDENT",
            "alibi": "ALIBI: Sliced apples stayed white for six hours.",
            "search_keyword": "apple fruit laboratory food",
            "speech_keyword": "student"
        },
        "suspect_3": {
            "role": "THE HEAD CARETAKER",
            "title": "SUSPECT 3: THE HEAD CARETAKER",
            "alibi": "ALIBI: Pruning dead leaves from toxic vines.",
            "search_keyword": "greenhouse gardener plants",
            "speech_keyword": "caretaker"
        },
        "culprit_role": "THE CHEMISTRY STUDENT",
        "culprit_speech_keyword": "student",
        "culprit_reason": "REASON: SLICED APPLES OXIDIZE AND TURN BROWN!",
        "suspect_keywords": ["toxicologist", "student", "caretaker"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "High-Rise Penthouse Infinity Pool",
        "title": "99% Miss The Clue! Who Is The Liar? #Shorts",
        "description": "Can you solve this penthouse rooftop mystery in 10s? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "rooftop infinity pool city night",
        "full_text": (
            "A billionaire heir was discovered drowned in a luxury rooftop swimming pool at night. "
            "The detective questioned three guests present at the pool deck. "
            "The Resident claimed he saw a vivid full rainbow arching across the dry midnight sky. "
            "The Bartender said he was mixing fruit mojitos at the cabana counter. "
            "The Lifeguard stated he was testing chlorine water levels with a test kit. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Resident! Rainbows cannot form in the sky without sunlight and water droplets! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE RESIDENT",
            "title": "SUSPECT 1: THE RESIDENT",
            "alibi": "ALIBI: Saw full rainbow in dry midnight sky.",
            "search_keyword": "luxury penthouse night balcony",
            "speech_keyword": "resident"
        },
        "suspect_2": {
            "role": "THE BARTENDER",
            "title": "SUSPECT 2: THE BARTENDER",
            "alibi": "ALIBI: Mixing cocktails at cabana counter.",
            "search_keyword": "bartender pouring drinks bar",
            "speech_keyword": "bartender"
        },
        "suspect_3": {
            "role": "THE LIFEGUARD",
            "title": "SUSPECT 3: THE LIFEGUARD",
            "alibi": "ALIBI: Testing chlorine with chemical kit.",
            "search_keyword": "swimming pool water clear",
            "speech_keyword": "lifeguard"
        },
        "culprit_role": "THE RESIDENT",
        "culprit_speech_keyword": "resident",
        "culprit_reason": "REASON: RAINBOWS REQUIRE SUNLIGHT!",
        "suspect_keywords": ["resident", "bartender", "lifeguard"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_1.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Arctic Glaciology Research Camp",
        "title": "Who Is The Killer? 95% Fail This Riddle! #Shorts",
        "description": "Can you solve this Arctic polar research mystery? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "arctic ice snow polar blizzard",
        "full_text": (
            "A polar expedition leader was found frozen inside a research trailer on the ice shelf. "
            "The investigator questioned three scientists inside the heated station. "
            "The Climate Scientist said she was examining ice core samples in the freezer. "
            "The Snowmobile Mechanic claimed dry ice blocks melted into a deep puddle of liquid water on the table. "
            "The Radio Operator stated he was sending weather updates to headquarters. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Snowmobile Mechanic! Dry ice sublimates directly into gas and never melts into liquid water! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE CLIMATE SCIENTIST",
            "title": "SUSPECT 1: THE CLIMATE SCIENTIST",
            "alibi": "ALIBI: Examining ice cores in freezer.",
            "search_keyword": "scientist microscope ice snow",
            "speech_keyword": "scientist"
        },
        "suspect_2": {
            "role": "THE SNOWMOBILE MECHANIC",
            "title": "SUSPECT 2: THE SNOWMOBILE MECHANIC",
            "alibi": "ALIBI: Dry ice melted into puddle of water.",
            "search_keyword": "mechanic tools winter snow",
            "speech_keyword": "mechanic"
        },
        "suspect_3": {
            "role": "THE RADIO OPERATOR",
            "title": "SUSPECT 3: THE RADIO OPERATOR",
            "alibi": "ALIBI: Sending weather updates to base.",
            "search_keyword": "radio transmission equipment",
            "speech_keyword": "operator"
        },
        "culprit_role": "THE SNOWMOBILE MECHANIC",
        "culprit_speech_keyword": "mechanic",
        "culprit_reason": "REASON: DRY ICE TURNS TO GAS, NOT LIQUID!",
        "suspect_keywords": ["scientist", "mechanic", "operator"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_2.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    },
    {
        "topic_name": "Historic Antique Mirror Atelier",
        "title": "Only A True Detective Catches The Flaw! #Shorts",
        "description": "Can you solve this antique mirror workshop crime riddle? Spot the liar! #Shorts #CrimeRiddle #Detective #Mystery #IQTest #BrainTeaser",
        "tags": ["Shorts", "CrimeRiddle", "DetectiveRiddle", "Riddle", "Mystery", "BrainTeaser", "IQTest"],
        "setting_query": "mirror reflection vintage room",
        "full_text": (
            "An antique dealer was murdered inside a historic mirror restoration workshop. "
            "The inspector questioned three people present in the building. "
            "The Silvering Tech claimed he clearly saw his sharp reflection in the clear window glass from a pitch-dark room. "
            "The Appraiser said he was dating an eighteenth century French gilded frame. "
            "The Wood Restorer stated he was polishing mahogany backing with beeswax. "
            "One of them is lying. Spot the killer before the timer runs out! "
            "Five, four, three, two, one! "
            "It was the Silvering Tech! Plain glass does not reflect images when you are standing in a pitch-dark room! "
            "Did you solve it? Comment yes or no!"
        ),
        "suspect_1": {
            "role": "THE SILVERING TECH",
            "title": "SUSPECT 1: THE SILVERING TECH",
            "alibi": "ALIBI: Saw reflection in window from dark room.",
            "search_keyword": "glass mirror reflection dark",
            "speech_keyword": "tech"
        },
        "suspect_2": {
            "role": "THE APPRAISER",
            "title": "SUSPECT 2: THE APPRAISER",
            "alibi": "ALIBI: Dating eighteenth century gilded frame.",
            "search_keyword": "antique frame gilded gold",
            "speech_keyword": "appraiser"
        },
        "suspect_3": {
            "role": "THE WOOD RESTORER",
            "title": "SUSPECT 3: THE WOOD RESTORER",
            "alibi": "ALIBI: Polishing mahogany with beeswax.",
            "search_keyword": "wood restoration polish furniture",
            "speech_keyword": "restorer"
        },
        "culprit_role": "THE SILVERING TECH",
        "culprit_speech_keyword": "tech",
        "culprit_reason": "REASON: GLASS DOES NOT REFLECT FROM DARK ROOMS!",
        "suspect_keywords": ["tech", "appraiser", "restorer"],
        "suspect_badges": [
            "assets/riddle/badge_suspect_1.png",
            "assets/riddle/badge_suspect_2.png",
            "assets/riddle/badge_suspect_3.png"
        ],
        "guilty_badge": "assets/riddle/badge_suspect_1.png",
        "guilty_stamp": "assets/riddle/guilty_stamp.png"
    }
]

def get_fallback_script(history: list) -> dict:
    """
    Selects a guaranteed non-duplicating handcrafted viral mystery from the 25+ preset pool.
    Guarantees no repetition until all fallbacks have been utilized.
    """
    history_topics = {h.get("topic_name", "").strip().lower() for h in history if h.get("topic_name")}
    
    # Filter out templates that have already appeared anywhere in history
    available = [t for t in FALLBACK_TEMPLATES if t["topic_name"].strip().lower() not in history_topics]
    
    if not available:
        # If all 25 have cycled, pick the least recent one (excluding the last 15)
        recent_15 = [h.get("topic_name", "").strip().lower() for h in history[-15:]]
        available = [t for t in FALLBACK_TEMPLATES if t["topic_name"].strip().lower() not in recent_15]
        if not available:
            available = FALLBACK_TEMPLATES

    selected = random.choice(available)
    print(f"Dự phòng kích hoạt: Chọn kịch bản mẫu số độc bản: '{selected['topic_name']}'")

    # Record in history
    history.append({
        "topic_name": selected["topic_name"],
        "title": selected["title"],
        "setting_theme": selected.get("topic_name"),
        "culprit_role": selected.get("culprit_role"),
        "culprit_reason": selected.get("culprit_reason"),
        "generated_at": str(os.getenv("GITHUB_RUN_ID", "fallback_pool"))
    })
    
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
        
    return selected
