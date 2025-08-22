import json
from pathlib import Path
from typing import Dict, List, Literal

import streamlit as st

# ======================
# THEME (dark + neon + glass)
# ======================

FALLBACK_CSS = """
<style>
/* Base dark + neon red */
.stApp, .block-container { background: #0b0b0b !important; color: #ff3030 !important; }
.block-container { background: rgba(0,0,0,0.86) !important; border-radius: 12px; padding: 1.25rem; }
h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stText, .stMetric { color: #ff3030 !important; }
.stButton>button, .stDownloadButton>button { border:1px solid #444; color:#ff3030; background:#0a0a0a; }
.stButton>button:hover, .stDownloadButton>button:hover { border-color:#ff3030; }

/* Glass inputs + neon text */
:root { --glass-bg: rgba(10,10,10,0.35); --glass-bd: rgba(255,48,48,0.45); --neon:#ff3030; --neon-dim:#ff7a7a; }
.stTextInput input, .stTextArea textarea, .stNumberInput input {
  background: var(--glass-bg) !important; color: var(--neon) !important;
  border: 1px solid var(--glass-bd) !important; backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
}
div[data-baseweb="select"] { background: var(--glass-bg) !important; border: 1px solid var(--glass-bd) !important;
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); }
div[role="button"], input { color: var(--neon) !important; }
::placeholder { color: var(--neon-dim) !important; opacity: 0.85; }

.dotline { letter-spacing: 1px; }
.rowline { border-bottom:1px solid #222; padding:6px 0; margin-bottom:4px; }
.small { color:#ff7a7a; font-size:0.9rem; }
.section { border: 1px solid #222; border-radius: 10px; padding: 10px; margin-bottom: 12px; background:#0e0e0e; }
.power { border-left: 2px solid #7a0a0a; padding-left: 10px; margin: 6px 0; }
</style>
"""
st.markdown(FALLBACK_CSS, unsafe_allow_html=True)

# ======================
# DATA
# ======================

AttributeGroup = Literal["physical", "social", "mental"]
AbilityCategory = Literal["talents", "skills", "knowledges"]

NATURES: List[str] = [
    "Architect","Autocrat","Bon Vivant","Bravo","Caretaker","Celebrant","Competitor","Conformist","Conniver",
    "Curmudgeon","Defender","Director","Eye of the Storm","Fanatic","Gallant","Gambler","Jester","Judge",
    "Loner","Martyr","Masochist","Monster","Penitent","Perfectionist","Rebel","Rogue","Scientist","Survivor",
    "Thrill-Seeker","Traditionalist","Trickster","Visionary"
]

CLANS = [
    {"name":"Brujah", "disciplines":["Celerity","Potence","Presence"]},
    {"name":"Gangrel","disciplines":["Animalism","Fortitude","Protean"]},
    {"name":"Malkavian","disciplines":["Auspex","Dementation","Obfuscate"]},
    {"name":"Nosferatu","disciplines":["Animalism","Obfuscate","Potence"]},
    {"name":"Toreador","disciplines":["Auspex","Celerity","Presence"]},
    {"name":"Tremere","disciplines":["Auspex","Dominate","Thaumaturgy"]},
    {"name":"Ventrue","disciplines":["Dominate","Fortitude","Presence"]},
    {"name":"Assamite","disciplines":["Celerity","Obfuscate","Quietus"]},
    {"name":"Giovanni","disciplines":["Dominate","Fortitude","Necromancy"]},
    {"name":"Lasombra","disciplines":["Dominate","Obtenebration","Potence"]},
    {"name":"Tzimisce","disciplines":["Animalism","Auspex","Vicissitude"]},
]
CLAN_TO_DISC = {c["name"]: c["disciplines"] for c in CLANS}

ATTR_GROUPS = [
    ("physical", "Physical", ["Strength","Dexterity","Stamina"]),
    ("social",   "Social",   ["Charisma","Manipulation","Appearance"]),
    ("mental",   "Mental",   ["Perception","Intelligence","Wits"]),
]

# NOTE: “Dodge” renamed to “Awarness” exactly as requested
ABILITIES: Dict[AbilityCategory, List[str]] = {
    "talents":    ["Alertness","Athletics","Brawl","Awarness","Empathy","Expression","Intimidation","Leadership","Streetwise","Subterfuge"],
    "skills":     ["Animal Ken","Crafts","Drive","Etiquette","Firearms","Larceny","Melee","Performance","Stealth","Survival"],
    "knowledges": ["Academics","Computer","Finance","Investigation","Law","Linguistics","Medicine","Occult","Politics","Science"],
}

BACKGROUNDS = ["Allies","Contacts","Fame","Generation","Herd","Influence","Mentor","Resources","Retainers","Status"]

GENERATION_TABLE = [
    {"gen":13, "traitMax":5, "bloodPerTurn":1, "bloodPool":10},
    {"gen":12, "traitMax":5, "bloodPerTurn":1, "bloodPool":11},
    {"gen":11, "traitMax":5, "bloodPerTurn":1, "bloodPool":12},
    {"gen":10, "traitMax":5, "bloodPerTurn":1, "bloodPool":13},
    {"gen":9,  "traitMax":5, "bloodPerTurn":1, "bloodPool":14},
    {"gen":8,  "traitMax":5, "bloodPerTurn":3, "bloodPool":15},
    {"gen":7,  "traitMax":6, "bloodPerTurn":4, "bloodPool":20},
    {"gen":6,  "traitMax":7, "bloodPerTurn":6, "bloodPool":30},
    {"gen":5,  "traitMax":8, "bloodPerTurn":8, "bloodPool":40},
]

# Discipline power blurbs (compact, V20-flavored; effects summarized)
DISCIPLINE_POWERS: Dict[str, Dict[int, Dict[str, str]]] = {
    "Protean": {
        1: {"name":"Eyes of the Beast", "info":"Eyes glow red; see in total darkness. Cost/roll: none. Effect: night vision, intimidating gaze."},
        2: {"name":"Feral Claws", "info":"Spend 1 Blood. Grow claws; Str +1 aggravated damage; retract at will."},
        3: {"name":"Earth Meld", "info":"Roll Stamina+Survival diff 6; 1 turn to sink. Effect: meld with natural earth/stone to hide/sleep."},
        4: {"name":"Shape of the Beast", "info":"Assume wolf/bat form (depends ST); boosts and movement per form."},
        5: {"name":"Mist Form", "info":"Become living mist; immune to physical harm; move through cracks."},
    },
    "Celerity": {
        1: {"name":"Quickness", "info":"Spend 1 Blood per extra action this turn. Effect: act faster; move blindingly."},
        2: {"name":"Alacrity", "info":"As above; improved speed and reaction."},
        3: {"name":"Rapidity", "info":"As above; multiple extra actions possible (ST adjudicates)."},
        4: {"name":"Fleetness", "info":"Supernatural speed; near-blur."},
        5: {"name":"Blinding Speed", "info":"Near-untouchable speed for a scene (with Blood)."},
    },
    "Potence": {
        1: {"name":"Prowess", "info":"Melee/Str damage boosted; spend Blood for auto successes (per dot)."},
        2: {"name":"Might", "info":"Feats of strength become trivial."},
        3: {"name":"Vigor", "info":"Devastating blows; break stone/steel with effort."},
        4: {"name":"Intensity", "info":"Crushing power; leap/throw far."},
        5: {"name":"Heroic Strength", "info":"Legendary force; shatter barriers."},
    },
    "Presence": {
        1: {"name":"Awe", "info":"Captivates those nearby; no roll vs mortals typically; social edge."},
        2: {"name":"Dread Gaze", "info":"Instill fear; many mortals flee; roll Cha+Intimidation."},
        3: {"name":"Entrancement", "info":"Target adores you; extended influence."},
        4: {"name":"Summon", "info":"Call a known target from afar; they feel compelled to come."},
        5: {"name":"Majesty", "info":"Become regal/untouchable; few dare oppose you."},
    },
    "Animalism": {
        1: {"name":"Feral Whispers", "info":"Speak with animals; simple commands."},
        2: {"name":"Beckoning", "info":"Call animals of a region; they come if able."},
        3: {"name":"Quell the Beast", "info":"Soothe or rouse Beast in mortals/vampires; resist frenzy."},
        4: {"name":"Subsume the Spirit", "info":"Possess an animal; control senses/body."},
        5: {"name":"Drawing Out the Beast", "info":"Shift frenzy to another or externalize it."},
    },
    "Fortitude": {
        1: {"name":"Endurance", "info":"Extra soak; resist harm beyond mortal limits."},
        2: {"name":"Mettle", "info":"Soak lethal; sometimes aggravated (ST)."},
        3: {"name":"Resilience", "info":"Stand against fire/sunlight longer (not immunity)."},
        4: {"name":"Resolve", "info":"Ignore crippling wounds briefly."},
        5: {"name":"Unbreakable", "info":"Near-impossible to put down."},
    },
    "Auspex": {
        1: {"name":"Heightened Senses", "info":"Sharpen all senses; risk sensory overload."},
        2: {"name":"Aura Perception", "info":"Read emotions/creature type via auras."},
        3: {"name":"Telepathy", "info":"Read/speak mind-to-mind; resisted by Willpower."},
        4: {"name":"Psychic Projection", "info":"Astral projection; travel as spirit; body inert."},
        5: {"name":"Spirit's Touch", "info":"Psychometry: read emotional impressions from objects."},
    },
    "Dementation": {
        1: {"name":"Passion", "info":"Amplify or dampen emotions."},
        2: {"name":"The Haunting", "info":"Subject experiences unsettling phenomena."},
        3: {"name":"Eyes of Chaos", "info":"Perceive patterns in madness; hidden truths."},
        4: {"name":"Voice of Madness", "info":"Brief contagious hysteria/panic."},
        5: {"name":"Total Insanity", "info":"Crush a mind under madness."},
    },
    "Obfuscate": {
        1: {"name":"Cloak of Shadows", "info":"Remain unseen if still and in cover."},
        2: {"name":"Unseen Presence", "info":"Move while unseen; avoid drawing attention."},
        3: {"name":"Mask of a Thousand Faces", "info":"Appear as someone else; casual scrutiny fails."},
        4: {"name":"Vanish from the Mind's Eye", "info":"Disappear even in plain sight briefly."},
        5: {"name":"Cloak the Gathering", "info":"Extend obfuscation to companions."},
    },
    "Dominate": {
        1: {"name":"Command", "info":"Single-word orders; eye contact; mortals easy."},
        2: {"name":"Mesmerize", "info":"Implant suggestions; longer-term commands."},
        3: {"name":"The Forgetful Mind", "info":"Alter/erase memories."},
        4: {"name":"Conditioning", "info":"Long-term mental control over a subject."},
        5: {"name":"Possession", "info":"Wear a mortal like a suit; control their body."},
    },
    "Thaumaturgy": {
        1: {"name":"Blood Magic (Paths/Rituals)", "info":"Access level 1 of chosen Path; rituals by dots (ST approval)."},
        2: {"name":"Path ••", "info":"Use level 2 effects in chosen Path(s)."},
        3: {"name":"Path •••", "info":"Use level 3 effects."},
        4: {"name":"Path ••••", "info":"Use level 4 effects."},
        5: {"name":"Path •••••", "info":"Use level 5 effects; powerful rituals."},
    },
    "Necromancy": {
        1: {"name":"Death Magic (Paths/Rituals)", "info":"Access level 1 of Necromancy Path; rituals as learned."},
        2: {"name":"Path ••", "info":"Level 2 effects."},
        3: {"name":"Path •••", "info":"Level 3 effects."},
        4: {"name":"Path ••••", "info":"Level 4 effects."},
        5: {"name":"Path •••••", "info":"Level 5 effects; potent rites."},
    },
    "Obtenebration": {
        1: {"name":"Shadow Play", "info":"Manipulate shadows; dim light."},
        2: {"name":"Shroud of Night", "info":"Summon oily darkness that hinders foes."},
        3: {"name":"Arms of the Abyss", "info":"Shadow-tentacles restrain/attack."},
        4: {"name":"Black Metamorphosis", "info":"Cloak self in living darkness; lethal to touch."},
        5: {"name":"Tenebrous Form", "info":"Become shadowstuff; pass through cracks."},
    },
    "Quietus": {
        1: {"name":"Silence of Death", "info":"Create zone of absolute silence."},
        2: {"name":"Scorpion's Touch", "info":"Envenomate blood/weapon; inflict penalties."},
        3: {"name":"Dagon's Call", "info":"Command victim’s blood to surge painfully."},
        4: {"name":"Baal's Caress", "info":"Coat weapon with deadly ichor."},
        5: {"name":"Blood of Acid", "info":"Your blood becomes corrosive."},
    },
    "Vicissitude": {
        1: {"name":"Malleable Visage", "info":"Reshape your face/flesh."},
        2: {"name":"Fleshcraft", "info":"Reshape flesh of others (willing or subdued)."},
        3: {"name":"Bonecraft", "info":"Reshape bone; change structure."},
        4: {"name":"Horrid Form", "info":"Monstrous battle-form with bonuses."},
        5: {"name":"Bloodform", "info":"Liquefy into blood; seep through cracks."},
    },
}

# Freebie costs
COSTS = {
    "attribute":5, "ability":2, "discipline":7, "background":1, "virtue":2, "humanity":1, "willpower":1
}

# ======================
# STATE
# ======================

def init_state():
    if "builder" not in st.session_state:
        st.session_state.builder = {
            "concept": {
                "name":"", "player":"", "chronicle":"", "concept":"", "clan":"", "sire":"",
                "nature":"", "demeanor":"", "generation":13
            },
            "attributes": {
                "physical":{"Strength":1,"Dexterity":1,"Stamina":1},
                "social":{"Charisma":1,"Manipulation":1,"Appearance":1},
                "mental":{"Perception":1,"Intelligence":1,"Wits":1},
                "priorities":{"primary":"physical","secondary":"social","tertiary":"mental"}
            },
            "attr_specialties": {  # Attributes specialties at 4+
                "Strength":"", "Dexterity":"", "Stamina":"",
                "Charisma":"", "Manipulation":"", "Appearance":"",
                "Perception":"", "Intelligence":"", "Wits":""
            },
            "abilities": {
                "talents":    {k:0 for k in ABILITIES["talents"]},
                "skills":     {k:0 for k in ABILITIES["skills"]},
                "knowledges": {k:0 for k in ABILITIES["knowledges"]},
                "priorities": {"primary":"talents","secondary":"skills","tertiary":"knowledges"}
            },
            "specialties": {"talents":{}, "skills":{}, "knowledges":{}},  # abilities 4+
            "disciplines": {},
            "backgrounds": {},
            "virtues": {"Conscience":1,"SelfControl":1,"Courage":1},
            "notes":"",
            "meritsFlaws":""
        }
    if "freebies" not in st.session_state:
        st.session_state.freebies = {
            "pool": 15,
            "attributes": {
                "physical":{"Strength":0,"Dexterity":0,"Stamina":0},
                "social":{"Charisma":0,"Manipulation":0,"Appearance":0},
                "mental":{"Perception":0,"Intelligence":0,"Wits":0},
            },
            "abilities": {
                "talents":    {k:0 for k in ABILITIES["talents"]},
                "skills":     {k:0 for k in ABILITIES["skills"]},
                "knowledges": {k:0 for k in ABILITIES["knowledges"]},
            },
            "disciplines": {},
            "backgrounds": {k:0 for k in BACKGROUNDS},
            "virtues": {"Conscience":0,"SelfControl":0,"Courage":0},
            "humanity": 0,
            "willpower": 0,
        }
    if "step" not in st.session_state:
        st.session_state.step = 0

init_state()
B = st.session_state.builder
F = st.session_state.freebies

def gen_info(gen: int) -> dict:
    return next((g for g in GENERATION_TABLE if g["gen"] == int(gen)), GENERATION_TABLE[0])

def dotline(value:int, max_val:int=5) -> str:
    return ("●"*value) + ("○"*max(0, max_val - value))

# ======================
# SIDEBAR NAV (left)
# ======================

STEPS = [
    "Concept",
    "Attributes",
    "Abilities",
    "Disciplines",
    "Backgrounds",
    "Virtues",
    "Merits & Flaws",
    "Freebies",
    "Finishing",
    "Sheet",
    "Export / Import",
    "Dice Roller",
]

st.sidebar.title("Navigation")
for idx, name in enumerate(STEPS):
    if st.sidebar.button(name, use_container_width=True, key=f"nav-{idx}"):
        st.session_state.step = idx

# ======================
# HELPERS: CLEAR PER PAGE
# ======================

def clear_concept():
    B["concept"] = {"name":"", "player":"", "chronicle":"", "concept":"", "clan":"", "sire":"",
                    "nature":"", "demeanor":"", "generation":13}

def clear_attributes(reset_priorities=True):
    for g,_,stats in ATTR_GROUPS:
        for s in stats: B["attributes"][g][s] = 1
    for s in list(B["attr_specialties"].keys()): B["attr_specialties"][s] = ""
    if reset_priorities:
        B["attributes"]["priorities"] = {"primary":"physical","secondary":"social","tertiary":"mental"}

def clear_abilities(reset_priorities=True):
    for cat in ["talents","skills","knowledges"]:
        for n in ABILITIES[cat]: B["abilities"][cat][n] = 0
        B["specialties"][cat] = {}
    if reset_priorities:
        B["abilities"]["priorities"] = {"primary":"talents","secondary":"skills","tertiary":"knowledges"}

def clear_disciplines():
    B["disciplines"] = {}

def clear_backgrounds():
    B["backgrounds"] = {}

def clear_virtues():
    B["virtues"] = {"Conscience":1,"SelfControl":1,"Courage":1}

def clear_merits_flaws():
    B["meritsFlaws"] = ""

def clear_finishing():
    B["notes"] = ""

def clear_freebies():
    F["pool"] = 15
    for g,_,stats in ATTR_GROUPS:
        for s in stats: F["attributes"][g][s] = 0
    for cat in ["talents","skills","knowledges"]:
        for n in ABILITIES[cat]: F["abilities"][cat][n] = 0
    F["disciplines"] = {}
    for bg in BACKGROUNDS: F["backgrounds"][bg] = 0
    F["virtues"] = {"Conscience":0,"SelfControl":0,"Courage":0}
    F["humanity"] = 0
    F["willpower"] = 0

def total_value_attribute(group:str, stat:str, trait_max:int) -> int:
    return min(trait_max, B["attributes"][group][stat] + F["attributes"][group][stat])

def total_value_ability(cat:str, name:str) -> int:
    return min(5, B["abilities"][cat][name] + F["abilities"][cat][name])

def total_value_background(name:str) -> int:
    base = B["backgrounds"].get(name, 0)
    add  = F["backgrounds"].get(name, 0)
    return min(5, base + add)

def total_value_discipline(name:str) -> int:
    base = B["disciplines"].get(name, 0)
    add  = F["disciplines"].get(name, 0)
    return min(5, base + add)

def total_value_virtue(name:str) -> int:
    return min(5, B["virtues"][name] + F["virtues"][name])

def total_humanity() -> int:
    val = B["virtues"]["Conscience"] + F["virtues"]["Conscience"] + B["virtues"]["SelfControl"] + F["virtues"]["SelfControl"] + F["humanity"]
    return min(10, val)

def total_willpower() -> int:
    val = B["virtues"]["Courage"] + F["virtues"]["Courage"] + F["willpower"]
    return min(10, val)

# ======================
# CONTENT
# ======================

st.markdown("## World of Darkness : V20 Character creation by Andy Dark")

step = st.session_state.step
GI = gen_info(B["concept"]["generation"])
TRAIT_MAX = GI["traitMax"]

# ---- Concept ----
if step == 0:
    c1, c2 = st.columns(2)
    with c1:
        B["concept"]["name"] = st.text_input("Name", B["concept"]["name"])
        B["concept"]["player"] = st.text_input("Player", B["concept"]["player"])
        B["concept"]["chronicle"] = st.text_input("Chronicle", B["concept"]["chronicle"])
        B["concept"]["concept"] = st.text_input("Concept", B["concept"]["concept"])
    with c2:
        B["concept"]["nature"] = st.selectbox("Nature", [""]+NATURES, index=([""]+NATURES).index(B["concept"]["nature"]) if B["concept"]["nature"] in NATURES else 0)
        B["concept"]["demeanor"] = st.selectbox("Demeanor", [""]+NATURES, index=([""]+NATURES).index(B["concept"]["demeanor"]) if B["concept"]["demeanor"] in NATURES else 0)
        clans = [""]+[c["name"] for c in CLANS]
        B["concept"]["clan"] = st.selectbox("Clan", clans, index=clans.index(B["concept"]["clan"]) if B["concept"]["clan"] in clans else 0)
        B["concept"]["sire"] = st.text_input("Sire", B["concept"]["sire"])
        gens = [g["gen"] for g in GENERATION_TABLE]
        B["concept"]["generation"] = st.selectbox("Generation", gens, index=gens.index(B["concept"]["generation"]))
    GI = gen_info(B["concept"]["generation"]); TRAIT_MAX = GI["traitMax"]
    st.caption(f"Trait Max: {TRAIT_MAX} · Blood Pool: {GI['bloodPool']} · Blood/Turn: {GI['bloodPerTurn']}")
    if st.button("CLEAR ALL (Concept)"):
        clear_concept()
        st.rerun()

# ---- Attributes (buttons; 7/5/3 above base 1; specialties at 4+) ----
elif step == 1:
    st.markdown("**Assign 7/5/3 dots above base 1**. Attributes may remain at **1**. Specialties unlock at **4+**.")
    colA, colB, colC = st.columns(3)
    options = ["physical","social","mental"]
    with colA:
        primary = st.selectbox("Primary", options, index=options.index(B["attributes"]["priorities"]["primary"]), key="attr_primary")
    with colB:
        secondary = st.selectbox("Secondary", options, index=options.index(B["attributes"]["priorities"]["secondary"]), key="attr_secondary")
    with colC:
        tertiary = st.selectbox("Tertiary", options, index=options.index(B["attributes"]["priorities"]["tertiary"]), key="attr_tertiary")
    chosen = [primary, secondary, tertiary]
    if len(set(chosen)) < 3:
        for o in options:
            if chosen.count(o) == 0:
                if primary == secondary: secondary = o
                elif primary == tertiary: tertiary = o
                elif secondary == tertiary: tertiary = o
    B["attributes"]["priorities"] = {"primary":primary,"secondary":secondary,"tertiary":tertiary}

    budget_map = {"primary":7,"secondary":5,"tertiary":3}
    def slot_of(group:str)->str:
        for slot, grp in B["attributes"]["priorities"].items():
            if grp == group: return slot
        return "tertiary"

    for key,label,stats in ATTR_GROUPS:
        s = slot_of(key); budget = budget_map[s]
        spent_now = sum(B["attributes"][key][n]-1 for n in stats)
        st.markdown(f"### {label} — {s.capitalize()} ({budget}) — Remaining: {budget - spent_now}")
        for stat_name in stats:
            current = B["attributes"][key][stat_name]
            cols = st.columns([1.6, 2.2, 0.8, 0.8])
            with cols[0]:
                st.write(stat_name)
            with cols[1]:
                st.markdown(f"<span class='dotline'>{dotline(current, TRAIT_MAX)}</span>", unsafe_allow_html=True)
            with cols[2]:
                if st.button("−1", key=f"attr-dec-{key}-{stat_name}", disabled=(current<=1)):
                    B["attributes"][key][stat_name] = max(1, current-1)
                    st.rerun()
            with cols[3]:
                # check live budget + max
                spent_live = sum(B["attributes"][key][n]-1 for n in stats)
                can_inc = (spent_live < budget) and (current < TRAIT_MAX)
                if st.button("+1", key=f"attr-inc-{key}-{stat_name}", disabled=not can_inc):
                    B["attributes"][key][stat_name] = current+1
                    st.rerun()
            # Attribute specialty at 4+
            if B["attributes"][key][stat_name] >= 4:
                B["attr_specialties"][stat_name] = st.text_input(
                    f"{stat_name} — Specialty (4+):",
                    B["attr_specialties"].get(stat_name,""),
                    key=f"attrspec-{stat_name}",
                    placeholder="e.g., Brutal Strikes, Fast Hands, Keen Senses…"
                )
        st.markdown("---")
    if st.button("CLEAR ALL (Attributes)"):
        clear_attributes(reset_priorities=True); st.rerun()

# ---- Abilities (buttons; 13/9/5; specialties at 4+) ----
elif step == 2:
    st.markdown("Assign **13/9/5** across Talents / Skills / Knowledges. Specialties unlock at **4+**.")
    pcol1,pcol2,pcol3 = st.columns(3)
    with pcol1:
        a_primary = st.selectbox("Primary", ["talents","skills","knowledges"], index=["talents","skills","knowledges"].index(B["abilities"]["priorities"]["primary"]))
    with pcol2:
        a_secondary = st.selectbox("Secondary", ["talents","skills","knowledges"], index=["talents","skills","knowledges"].index(B["abilities"]["priorities"]["secondary"]))
    with pcol3:
        a_tertiary = st.selectbox("Tertiary", ["talents","skills","knowledges"], index=["talents","skills","knowledges"].index(B["abilities"]["priorities"]["tertiary"]))
    if len({a_primary,a_secondary,a_tertiary}) < 3:
        st.warning("Primary/Secondary/Tertiary must be different.")
    else:
        B["abilities"]["priorities"] = {"primary":a_primary,"secondary":a_secondary,"tertiary":a_tertiary}

    budget_map = {"primary":13,"secondary":9,"tertiary":5}
    def cat_slot(cat:str)->str:
        for slot, val in B["abilities"]["priorities"].items():
            if val == cat: return slot
        return "tertiary"

    for cat in ["talents","skills","knowledges"]:
        spent_now = sum(B["abilities"][cat].values())
        st.markdown(f"### {cat.capitalize()} — {cat_slot(cat).capitalize()} ({budget_map[cat_slot(cat)]}) — Remaining: {budget_map[cat_slot(cat)] - spent_now}")
        for name in ABILITIES[cat]:
            current = B["abilities"][cat][name]
            cols = st.columns([1.8, 2.0, 0.8, 0.8])
            with cols[0]:
                st.write(name)
            with cols[1]:
                st.markdown(f"<span class='dotline'>{dotline(current,5)}</span>", unsafe_allow_html=True)
            with cols[2]:
                if st.button("−1", key=f"abil-dec-{cat}-{name}", disabled=(current<=0)):
                    B["abilities"][cat][name] = max(0, current-1)
                    st.rerun()
            with cols[3]:
                spent_live = sum(B["abilities"][cat].values())
                can_inc = (spent_live < budget_map[cat_slot(cat)]) and (current < 5)
                if st.button("+1", key=f"abil-inc-{cat}-{name}", disabled=not can_inc):
                    B["abilities"][cat][name] = current+1
                    st.rerun()
            if B["abilities"][cat][name] >= 4:
                if name not in B["specialties"][cat]: B["specialties"][cat][name] = ""
                B["specialties"][cat][name] = st.text_input(
                    f"{name} — Specialty (4+):",
                    B["specialties"][cat][name],
                    key=f"spec-{cat}-{name}",
                    placeholder="e.g., Parkour, Grappling, Forensics…"
                )
        st.markdown("---")
    if st.button("CLEAR ALL (Abilities)"):
        clear_abilities(reset_priorities=True); st.rerun()

# ---- Disciplines (buttons; clan-limited; base budget 3) + power blurbs ----
elif step == 3:
    st.markdown("### Disciplines (3 dots total) — clan-limited")
    clan = B["concept"]["clan"]
    allowed = CLAN_TO_DISC.get(clan, [])
    if not clan:
        st.warning("Pick a **Clan** on the Concept page first.")
    elif not allowed:
        st.warning(f"No disciplines defined for clan: {clan}")
    else:
        for k in list(B["disciplines"].keys()):
            if k not in allowed: del B["disciplines"][k]
        spent_now = sum(B["disciplines"].values())
        st.caption(f"Remaining: {3 - spent_now}")
        for d in allowed:
            current = B["disciplines"].get(d, 0)
            cols = st.columns([1.8, 2.0, 0.8, 0.8])
            with cols[0]:
                st.write(d)
            with cols[1]:
                st.markdown(f"<span class='dotline'>{dotline(current,5)}</span>", unsafe_allow_html=True)
            with cols[2]:
                if st.button("−1", key=f"disc-dec-{d}", disabled=(current<=0)):
                    B["disciplines"][d] = max(0, current-1)
                    st.rerun()
            with cols[3]:
                spent_live = sum(B["disciplines"].values())
                can_inc = (spent_live < 3) and (current < 5)
                if st.button("+1", key=f"disc-inc-{d}", disabled=not can_inc):
                    B["disciplines"][d] = current+1
                    st.rerun()

            # powers up to TOTAL (base + freebies)
            total = total_value_discipline(d)
            if total > 0:
                st.markdown("<div class='small'>Unlocked powers:</div>", unsafe_allow_html=True)
                for lvl in range(1, total+1):
                    info = DISCIPLINE_POWERS.get(d, {}).get(lvl)
                    if info:
                        st.markdown(f"<div class='power'>• <b>{info['name']}</b><br/><span class='small'>{info['info']}</span></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='power'>• Level {lvl} power</div>", unsafe_allow_html=True)
            st.markdown("---")
    if st.button("CLEAR ALL (Disciplines)"):
        clear_disciplines(); st.rerun()

# ---- Backgrounds (buttons; base budget 5) ----
elif step == 4:
    st.markdown("### Backgrounds (5 dots total)")
    spent_now = sum(B["backgrounds"].values()) if B["backgrounds"] else 0
    st.caption(f"Remaining: {5 - spent_now}")
    for bg in BACKGROUNDS:
        current = B["backgrounds"].get(bg, 0)
        cols = st.columns([1.8, 2.0, 0.8, 0.8])
        with cols[0]:
            st.write(bg)
        with cols[1]:
            st.markdown(f"<span class='dotline'>{dotline(current,5)}</span>", unsafe_allow_html=True)
        with cols[2]:
            if st.button("−1", key=f"bg-dec-{bg}", disabled=(current<=0)):
                B["backgrounds"][bg] = max(0, current-1)
                st.rerun()
        with cols[3]:
            spent_live = sum(B["backgrounds"].values())
            can_inc = (spent_live < 5) and (current < 5)
            if st.button("+1", key=f"bg-inc-{bg}", disabled=not can_inc):
                B["backgrounds"][bg] = current+1
                st.rerun()
    if st.button("CLEAR ALL (Backgrounds)"):
        clear_backgrounds(); st.rerun()

# ---- Virtues (buttons; start 1 each; +7 above base) ----
elif step == 5:
    st.markdown("### Virtues (start 1 each; add 7 dots)")
    v_added_now = sum(v-1 for v in B["virtues"].values())
    st.caption(f"Remaining above base: {7 - v_added_now}")
    for vt in ["Conscience","SelfControl","Courage"]:
        current = B["virtues"][vt]
        cols = st.columns([1.6, 2.0, 0.8, 0.8])
        with cols[0]:
            st.write(vt)
        with cols[1]:
            st.markdown(f"<span class='dotline'>{dotline(current,5)}</span>", unsafe_allow_html=True)
        with cols[2]:
            if st.button("−1", key=f"virt-dec-{vt}", disabled=(current<=1)):
                B["virtues"][vt] = max(1, current-1)
                st.rerun()
        with cols[3]:
            v_added_live = sum(v-1 for v in B["virtues"].values())
            can_inc = (v_added_live < 7) and (current < 5)
            if st.button("+1", key=f"virt-inc-{vt}", disabled=not can_inc):
                B["virtues"][vt] = current+1
                st.rerun()
    st.caption("Humanity = Conscience + Self-Control (plus any Freebies). Willpower = Courage (plus any Freebies).")
    if st.button("CLEAR ALL (Virtues)"):
        clear_virtues(); st.rerun()

# ---- Merits & Flaws ----
elif step == 6:
    st.markdown("### Merits & Flaws (notes)")
    B["meritsFlaws"] = st.text_area("Merits/Flaws", B["meritsFlaws"], height=220, placeholder="Write merits & flaws here…")
    if st.button("CLEAR ALL (Merits & Flaws)"):
        clear_merits_flaws(); st.rerun()

# ---- Freebies (with refund buttons) ----
elif step == 7:
    GI = gen_info(B["concept"]["generation"]); TRAIT_MAX = GI["traitMax"]
    st.markdown("### Freebies — spend after core build")
    topA, topB, topC = st.columns([1,1,3])
    with topA:
        if st.button("-1 Freebie", key="pool_minus") and F["pool"] > 0:
            F["pool"] -= 1
    with topB:
        if st.button("+1 Freebie", key="pool_plus"):
            F["pool"] += 1
    with topC:
        st.markdown(f"**Current Freebie Pool:** {F['pool']}")
        st.caption("Costs — Attribute:5 · Ability:2 · Discipline:7 · Background:1 · Virtue:2 · Humanity/Path:1 · Willpower:1")

    st.markdown("#### Attributes")
    for key,label,stats in ATTR_GROUPS:
        st.markdown(f"**{label}**")
        for s in stats:
            base = B["attributes"][key][s]
            add  = F["attributes"][key][s]
            total = min(TRAIT_MAX, base + add)
            cols = st.columns([2.2, 1.2, 1.0, 1.0])
            with cols[0]:
                st.markdown(f"{s}: <span class='dotline'>{dotline(total, TRAIT_MAX)}</span>", unsafe_allow_html=True)
            with cols[1]:
                st.caption(f"base {base} +{add}")
            with cols[2]:
                can_refund = add > 0
                if st.button("Refund −1 (+5)", key=f"fb-attr-refund-{key}-{s}", disabled=not can_refund):
                    F["attributes"][key][s] -= 1
                    F["pool"] += COSTS["attribute"]
                    st.rerun()
            with cols[3]:
                can_buy = (F["pool"] >= COSTS["attribute"]) and (total < TRAIT_MAX)
                if st.button("Buy +1 (5)", key=f"fb-attr-{key}-{s}", disabled=not can_buy):
                    F["attributes"][key][s] += 1
                    F["pool"] -= COSTS["attribute"]
                    st.rerun()
        st.markdown("---")

    st.markdown("#### Abilities")
    for cat in ["talents","skills","knowledges"]:
        st.markdown(f"**{cat.capitalize()}**")
        for n in ABILITIES[cat]:
            base = B["abilities"][cat][n]
            add  = F["abilities"][cat][n]
            total = min(5, base + add)
            cols = st.columns([2.4, 1.0, 1.0, 1.0])
            with cols[0]:
                st.markdown(f"{n}: <span class='dotline'>{dotline(total,5)}</span>", unsafe_allow_html=True)
            with cols[1]:
                st.caption(f"base {base} +{add}")
            with cols[2]:
                can_refund = add > 0
                if st.button("Refund −1 (+2)", key=f"fb-abil-refund-{cat}-{n}", disabled=not can_refund):
                    F["abilities"][cat][n] -= 1
                    F["pool"] += COSTS["ability"]
                    st.rerun()
            with cols[3]:
                can_buy = (F["pool"] >= COSTS["ability"]) and (total < 5)
                if st.button("Buy +1 (2)", key=f"fb-abil-{cat}-{n}", disabled=not can_buy):
                    F["abilities"][cat][n] += 1
                    F["pool"] -= COSTS["ability"]
                    st.rerun()
        st.markdown("---")

    st.markdown("#### Disciplines (Clan-limited)")
    clan = B["concept"]["clan"]; allowed = CLAN_TO_DISC.get(clan, [])
    if not clan:
        st.warning("Pick a **Clan** on the Concept page first.")
    elif not allowed:
        st.warning(f"No disciplines defined for clan: {clan}")
    else:
        for d in allowed:
            if d not in F["disciplines"]: F["disciplines"][d] = 0
        for d in allowed:
            base = B["disciplines"].get(d, 0)
            add  = F["disciplines"].get(d, 0)
            total = min(5, base + add)
            cols = st.columns([2.4, 1.0, 1.0, 1.0])
            with cols[0]:
                st.markdown(f"{d}: <span class='dotline'>{dotline(total,5)}</span>", unsafe_allow_html=True)
            with cols[1]:
                st.caption(f"base {base} +{add}")
            with cols[2]:
                can_refund = add > 0
                if st.button("Refund −1 (+7)", key=f"fb-disc-refund-{d}", disabled=not can_refund):
                    F["disciplines"][d] -= 1
                    F["pool"] += COSTS["discipline"]
                    st.rerun()
            with cols[3]:
                can_buy = (F["pool"] >= COSTS["discipline"]) and (total < 5)
                if st.button("Buy +1 (7)", key=f"fb-disc-{d}", disabled=not can_buy):
                    F["disciplines"][d] = F["disciplines"].get(d, 0) + 1
                    F["pool"] -= COSTS["discipline"]
                    st.rerun()

            # show powers up to TOTAL
            if total > 0:
                st.caption("Unlocked powers:")
                for lvl in range(1, total+1):
                    info = DISCIPLINE_POWERS.get(d, {}).get(lvl)
                    if info:
                        st.markdown(f"<div class='power'>• <b>{info['name']}</b><br/><span class='small'>{info['info']}</span></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='power'>• Level {lvl} power</div>", unsafe_allow_html=True)
        st.markdown("---")

    st.markdown("#### Backgrounds")
    for bg in BACKGROUNDS:
        base = B["backgrounds"].get(bg, 0)
        add  = F["backgrounds"].get(bg, 0)
        total = min(5, base + add)
        cols = st.columns([2.4, 1.0, 1.0, 1.0])
        with cols[0]:
            st.markdown(f"{bg}: <span class='dotline'>{dotline(total,5)}</span>", unsafe_allow_html=True)
        with cols[1]:
            st.caption(f"base {base} +{add}")
        with cols[2]:
            can_refund = add > 0
            if st.button("Refund −1 (+1)", key=f"fb-bg-refund-{bg}", disabled=not can_refund):
                F["backgrounds"][bg] -= 1
                F["pool"] += COSTS["background"]
                st.rerun()
        with cols[3]:
            can_buy = (F["pool"] >= COSTS["background"]) and (total < 5)
            if st.button("Buy +1 (1)", key=f"fb-bg-{bg}", disabled=not can_buy):
                F["backgrounds"][bg] += 1
                F["pool"] -= COSTS["background"]
                st.rerun()
    st.markdown("---")

    st.markdown("#### Virtues")
    for vt in ["Conscience","SelfControl","Courage"]:
        base = B["virtues"][vt]
        add  = F["virtues"][vt]
        total = min(5, base + add)
        cols = st.columns([2.0, 1.0, 1.0, 1.0])
        with cols[0]:
            st.markdown(f"{vt}: <span class='dotline'>{dotline(total,5)}</span>", unsafe_allow_html=True)
        with cols[1]:
            st.caption(f"base {base} +{add}")
        with cols[2]:
            can_refund = add > 0
            if st.button("Refund −1 (+2)", key=f"fb-virt-refund-{vt}", disabled=not can_refund):
                F["virtues"][vt] -= 1
                F["pool"] += COSTS["virtue"]
                st.rerun()
        with cols[3]:
            can_buy = (F["pool"] >= COSTS["virtue"]) and (total < 5)
            if st.button("Buy +1 (2)", key=f"fb-virt-{vt}", disabled=not can_buy):
                F["virtues"][vt] += 1
                F["pool"] -= COSTS["virtue"]
                st.rerun()
    st.markdown("---")

    st.markdown("#### Humanity / Path & Willpower")
    cols = st.columns(2)
    with cols[0]:
        hum_total = total_humanity()
        st.markdown(f"Humanity/Path: <span class='dotline'>{dotline(hum_total,10)}</span>", unsafe_allow_html=True)
        ccols = st.columns(2)
        with ccols[0]:
            can_refund = F["humanity"] > 0
            if st.button("Refund −1 (+1)", key="fb-hum-refund", disabled=not can_refund):
                F["humanity"] -= 1
                F["pool"] += COSTS["humanity"]
                st.rerun()
        with ccols[1]:
            can_buy = (F["pool"] >= COSTS["humanity"]) and (hum_total < 10)
            if st.button("Buy +1 (1)", key="fb-hum", disabled=not can_buy):
                F["humanity"] += 1
                F["pool"] -= COSTS["humanity"]
                st.rerun()
    with cols[1]:
        wp_total = total_willpower()
        st.markdown(f"Willpower: <span class='dotline'>{dotline(wp_total,10)}</span>", unsafe_allow_html=True)
        ccols = st.columns(2)
        with ccols[0]:
            can_refund = F["willpower"] > 0
            if st.button("Refund −1 (+1)", key="fb-wp-refund", disabled=not can_refund):
                F["willpower"] -= 1
                F["pool"] += COSTS["willpower"]
                st.rerun()
        with ccols[1]:
            can_buy = (F["pool"] >= COSTS["willpower"]) and (wp_total < 10)
            if st.button("Buy +1 (1)", key="fb-wp", disabled=not can_buy):
                F["willpower"] += 1
                F["pool"] -= COSTS["willpower"]
                st.rerun()

    if st.button("CLEAR ALL (Freebies)"):
        clear_freebies(); st.rerun()

# ---- Finishing (derived + notes; freebies reflected automatically) ----
elif step == 8:
    GI = gen_info(B["concept"]["generation"]); TRAIT_MAX = GI["traitMax"]
    humanity = total_humanity()
    willpower = total_willpower()

    st.markdown("### Derived (including Freebies)")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"- Humanity/Path: **{humanity}**")
        st.markdown(f"- Willpower: **{willpower}**")
        st.markdown(f"- Trait Max: **{GI['traitMax']}**")
    with c2:
        st.markdown(f"- Blood Pool: **{GI['bloodPool']}**")
        st.markdown(f"- Blood per Turn: **{GI['bloodPerTurn']}**")

    st.markdown("### Notes")
    B["notes"] = st.text_area("Notes (Equipment, Haven, Goals...)", B["notes"], height=160)
    if st.button("CLEAR ALL (Finishing)"):
        clear_finishing(); st.rerun()

# ---- Sheet (totals = base + freebies) ----
elif step == 9:
    GI = gen_info(B["concept"]["generation"]); TRAIT_MAX = GI["traitMax"]
    st.header(B["concept"]["name"] or "Unnamed")
    st.caption(B["concept"]["concept"])

    c1,c2,c3 = st.columns(3)
    with c1:
        st.write(f"**Player:** {B['concept']['player'] or '—'}")
        st.write(f"**Chronicle:** {B['concept']['chronicle'] or '—'}")
        st.write(f"**Sire:** {B['concept']['sire'] or '—'}")
    with c2:
        st.write(f"**Clan:** {B['concept']['clan'] or '—'}")
        st.write(f"**Nature:** {B['concept']['nature'] or '—'}")
        st.write(f"**Demeanor:** {B['concept']['demeanor'] or '—'}")
    with c3:
        st.write(f"**Generation:** {B['concept']['generation']}th")
        st.write(f"**Blood Pool:** {GI['bloodPool']} (per turn {GI['bloodPerTurn']})")

    st.markdown("---")
    st.subheader("Attributes")
    a1,a2,a3 = st.columns(3)
    for i,(key,label,stats) in enumerate(ATTR_GROUPS):
        col = [a1,a2,a3][i]
        with col:
            st.markdown(f"**{label}**")
            for s in stats:
                total = total_value_attribute(key,s,TRAIT_MAX)
                spec = B["attr_specialties"].get(s, "")
                spec_txt = f" — *({spec})*" if spec and total>=4 else ""
                st.markdown(f"{s}: <span class='dotline'>{dotline(total, TRAIT_MAX)}</span>{spec_txt}", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Abilities")
    ab1,ab2,ab3 = st.columns(3)
    for i,cat in enumerate(["talents","skills","knowledges"]):
        col = [ab1,ab2,ab3][i]
        with col:
            st.markdown(f"**{cat.capitalize()}**")
            empty = True
            for name in ABILITIES[cat]:
                total = total_value_ability(cat,name)
                if total>0:
                    empty = False
                    spec = B["specialties"][cat].get(name, "")
                    spec_txt = f" — *({spec})*" if spec and total>=4 else ""
                    st.markdown(f"{name}: <span class='dotline'>{dotline(total,5)}</span>{spec_txt}", unsafe_allow_html=True)
            if empty: st.caption("—")

    st.markdown("---")
    st.subheader("Disciplines")
    clan = B["concept"]["clan"]; allowed = CLAN_TO_DISC.get(clan, [])
    if not allowed:
        st.caption("—")
    else:
        for d in allowed:
            total = total_value_discipline(d)
            if total>0:
                st.markdown(f"{d}: <span class='dotline'>{dotline(total,5)}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Backgrounds")
    any_bg = False
    for bg in BACKGROUNDS:
        total = total_value_background(bg)
        if total>0:
            any_bg = True
            st.markdown(f"{bg}: <span class='dotline'>{dotline(total,5)}</span>", unsafe_allow_html=True)
    if not any_bg: st.caption("—")

    st.markdown("---")
    st.subheader("Virtues / Humanity / Willpower")
    for vt in ["Conscience","SelfControl","Courage"]:
        total = total_value_virtue(vt)
        st.markdown(f"{vt}: <span class='dotline'>{dotline(total,5)}</span>", unsafe_allow_html=True)
    st.markdown(f"Humanity/Path: <span class='dotline'>{dotline(total_humanity(),10)}</span>", unsafe_allow_html=True)
    st.markdown(f"Willpower: <span class='dotline'>{dotline(total_willpower(),10)}</span>", unsafe_allow_html=True)

# ---- Export / Import (includes freebies) ----
elif step == 10:
    payload = json.dumps({"builder": B, "freebies": F}, indent=2)
    st.download_button("⬇️ Export JSON", data=payload, file_name=f"{B['concept']['name'] or 'V20_Character'}.json", mime="application/json")
    uploaded = st.file_uploader("⬆️ Import JSON", type=["json"])
    if uploaded:
        try:
            data = json.loads(uploaded.read().decode("utf-8"))
            if "builder" in data:
                st.session_state.builder = data["builder"]
            if "freebies" in data:
                st.session_state.freebies = data["freebies"]
            st.success("Imported! Use the sidebar to navigate.")
        except Exception as e:
            st.error(f"Import failed: {e}")

# ---- Dice Roller ----
elif step == 11:
    st.subheader("Quick Dice Roller (d10)")
    pool = st.number_input("Pool", 1, 30, 5)
    diff = st.number_input("Difficulty", 2, 10, 6)
    if st.button("Roll d10s"):
        import random
        rolls = [random.randint(1,10) for _ in range(int(pool))]
        successes = sum(1 for r in rolls if r >= diff and r != 1)
        ones = rolls.count(1)
        net = successes - ones
        st.write(f"Rolls: {rolls}")
        st.write(f"Successes: **{successes}** · 1s: {ones} · Net: **{net}**")
