"""
Build lesson_vocab from the full lexicon_entries table.

Strategy:
- Unit 1: hardcoded EHN alphabet letters
- Units 2-32: per-unit SQL queries against lexicon_entries
  * Prefer EHN_colloquial; fall back to Comparative_only, then Classical_citation
  * Exclude grammatical noise (alt spellings, possessive forms, etc.)
  * Global deduplication: each display_form goes to the FIRST unit that claims it
- Target 20+ items per unit
"""

import sqlite3, io, sys, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB_PATH = "curriculum/fcn_master_lexicon_phase8_6_primer.sqlite"
db = sqlite3.connect(DB_PATH)

# ── Noise filter ───────────────────────────────────────────────────────────────
NOISE = re.compile(
    r"^(alternative spelling|obsolete spelling|alternative form|alternative "
    r"spelling|variant of |diminutive of |augmentative of |"
    r"(first|second|third|impersonal)-person .*(possessive|plural|singular)|"
    r"(first|second|third) person .*(possessive|plural|singular)|"
    r"Used to form|A suffix|A prefix|form of |"
    r"plural of |singular of )",
    re.IGNORECASE,
)

def clean(g: str) -> str:
    return g.strip().rstrip(".")

def fetchq(where: str, limit=30) -> list[tuple]:
    sql = f"""
        SELECT
          COALESCE(ehn_spoken_form, msn_headword) AS form,
          gloss_en, part_of_speech, register
        FROM lexicon_entries
        WHERE is_active = 1
          AND gloss_en IS NOT NULL AND gloss_en != ''
          AND (ehn_spoken_form IS NOT NULL OR msn_headword IS NOT NULL)
          AND ({where})
        ORDER BY
          CASE register
            WHEN 'EHN_colloquial'   THEN 0
            WHEN 'Comparative_only' THEN 1
            ELSE 2
          END,
          LENGTH(COALESCE(ehn_spoken_form, msn_headword))
        LIMIT {limit * 6}
    """
    rows = db.execute(sql).fetchall()
    out, seen = [], set()
    for form, gloss, pos, reg in rows:
        form = (form or "").strip()
        if not form or not gloss:
            continue
        if NOISE.match(gloss):
            continue
        key = form.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append((form, clean(gloss), pos or "", reg or ""))
        if len(out) == limit:
            break
    return out

# ── Helper for exact-gloss words ──
def gloss_in(*words: str) -> str:
    pats = [f"gloss_en LIKE '{w}.'" for w in words]
    pats += [f"gloss_en = '{w}'" for w in words]
    return " OR ".join(pats)

# ── Helper: word boundary LIKE ───
def glike(*patterns: str) -> str:
    """Each pattern is matched as gloss_en LIKE 'pattern'."""
    return " OR ".join(f"gloss_en LIKE '{p.replace(chr(39), chr(39)*2)}'" for p in patterns)

# ── Unit definitions ───────────────────────────────────────────────────────────
ALPHABET = [
    ("a",         "vowel [a] — like 'a' in father.  Example: axtle (no)",           "letter"),
    ("e",         "vowel [e] — like 'e' in bed.  Example: etl (bean)",              "letter"),
    ("i",         "vowel [i] — like 'ee' in feet.  Example: icha (home)",           "letter"),
    ("o",         "vowel [o] — like 'o' in go.  Example: onca (there is)",          "letter"),
    ("ā ē ī ō",   "long vowels — held twice as long.  Example: piālli (hello)",     "letter"),
    ("h",         "[ʔ] glottal stop between vowels; silent at word-end.  Example: ahsi (to arrive)", "letter"),
    ("ch",        "[tʃ] — like 'ch' in church.  Example: chilli (chili)",           "letter"),
    ("tl",        "[tɬ] — no English sound; tip of tongue on upper teeth, air released sideways.  Example: tlacua (to eat)", "letter"),
    ("tz",        "[ts] — like 'ts' in cats.  Example: tzopelatl (soda)",           "letter"),
    ("x",         "[ʃ] — like 'sh' in shoe.  Example: xopan (spring)",             "letter"),
    ("hu / uh",   "[w] — hu before vowels, uh before consonants.  Example: huica (to sing)", "letter"),
    ("qu / cu",   "[k] — qu before e/i, cu before a/o.  Example: quena (yes)",     "letter"),
    ("z",         "[s] — like 's' in sun.  Example: zayoltzi (bee)",               "letter"),
    ("l m n p t y", "similar to their English counterparts.  Example: nakatl (meat)", "letter"),
]

UNIT_QUERIES: dict[int, str] = {
    # ── 2: Questions ──────────────────────────────────────────────────────────
    2: glike(
        "who?", "what%", "where%", "how%", "why?", "when?",
        "how much%", "how many%", "which%",
        "yes%", "no, %", "not%", "not yet%", "now%", "right now%",
        "because%", "tomorrow%", "yesterday%",
    ) + """ OR ehn_spoken_form IN
        ('tlen','ahqueya','canque','queha','quezqui','para tlen','campa',
         'axtle','quena','ax','aya','ama','amantzi','yalhuaya','moztla')""",

    # ── 3: What is your name? ─────────────────────────────────────────────────
    3: """
        ehn_spoken_form = 'toca'
        OR msn_headword = 'tocaitl'
        OR msn_headword = 'notoca'
        OR msn_headword = 'motoca'
        OR gloss_en LIKE '%my name%'
        OR gloss_en LIKE '%your name%'
        OR gloss_en LIKE 'first person%'
        OR gloss_en LIKE 'second person%'
        OR gloss_en LIKE 'third person%'
        OR ehn_spoken_form IN ('na','naha','ta','taha','ya','yaha','yahaya',
           'tohuanti','yahuanti','amohuanti','imohuanti','ininhuanti',
           'mexikatl','caltlacatl','chicontepec','cualtitoc')
    """,

    # ── 4: Colors and Numbers ─────────────────────────────────────────────────
    4: """
        part_of_speech = 'num'
        OR (part_of_speech IN ('adj','adjective') AND (
            gloss_en LIKE '%red%' OR gloss_en LIKE '%blue%' OR gloss_en LIKE '%green%'
            OR gloss_en LIKE '%white%' OR gloss_en LIKE '%black%' OR gloss_en LIKE '%yellow%'
            OR gloss_en LIKE '%brown%' OR gloss_en LIKE 'big%' OR gloss_en LIKE 'great%'
            OR gloss_en LIKE 'small%' OR gloss_en LIKE 'many%' OR gloss_en LIKE 'little%'
        ))
    """,

    # ── 5: The Professions ────────────────────────────────────────────────────
    5: glike(
        "%teacher%", "%doctor%", "%healer%", "%governor%", "%official%",
        "%worker%", "%laborer%", "%merchant%", "%seller%", "%soldier%",
        "%grinder%", "%miller%", "%student%", "%scribe%", "%writer%",
        "%baker%", "%craftsman%", "%artisan%", "%midwife%", "%priest%",
        "%ruler%", "%chief%", "lesson%",
    ),

    # ── 6: Intransitive Verbs (being, moving) ─────────────────────────────────
    6: """
        part_of_speech = 'verb' AND (
            gloss_en LIKE 'to be%' OR gloss_en LIKE 'to go%' OR gloss_en LIKE 'to come%'
            OR gloss_en LIKE 'to arrive%' OR gloss_en LIKE 'to leave%' OR gloss_en LIKE 'to walk%'
            OR gloss_en LIKE 'to run%' OR gloss_en LIKE 'to sleep%' OR gloss_en LIKE 'to wake%'
            OR gloss_en LIKE 'to sit%' OR gloss_en LIKE 'to stay%' OR gloss_en LIKE 'to live%'
            OR gloss_en LIKE 'to exist%' OR gloss_en LIKE 'there is%'
            OR gloss_en LIKE 'to return%' OR gloss_en LIKE 'to pass%'
        )
    """,

    # ── 7: How to divide up the day ───────────────────────────────────────────
    7: glike(
        "%morning%", "%afternoon%", "%evening%", "%night%",
        "a day%", "%daytime%", "%noon%", "%midnight%",
        "%tomorrow%", "%yesterday%", "%today%", "%now%", "%right now%",
        "%hour%", "%week%", "%month%", "%year%",
        "%season%", "%spring%", "%summer%", "%autumn%", "%winter%",
        "%early%", "%late%", "%before%", "%after%", "%already%",
        "sun%", "moon%", "%sunrise%", "%sunset%",
    ),

    # ── 8: Possessive markers ─────────────────────────────────────────────────
    8: """
        (gloss_en LIKE 'of me%' OR gloss_en LIKE 'of you%' OR gloss_en LIKE 'of him%'
         OR gloss_en LIKE 'of her%' OR gloss_en LIKE 'with him%' OR gloss_en LIKE 'with me%'
         OR gloss_en LIKE 'with you%' OR gloss_en LIKE 'this%' OR gloss_en LIKE 'that%'
         OR gloss_en LIKE 'all%' OR gloss_en LIKE 'other%' OR gloss_en LIKE 'another%'
         OR gloss_en = 'nobody' OR gloss_en LIKE 'nobody%'
         OR ehn_spoken_form IN ('ni','ne','nopa','nochi','iaxca','moaxca','noaxca',
                                'ihuaya','cequinoc','ceyoc','neca','nepa','nica','nicani')
        )
        AND part_of_speech NOT IN ('verb')
    """,

    # ── 9: The Family ─────────────────────────────────────────────────────────
    9: """
        gloss_en LIKE '%mother%' OR gloss_en LIKE '% father%' OR gloss_en LIKE 'father%'
        OR gloss_en LIKE '%sister%' OR gloss_en LIKE '%brother%'
        OR (gloss_en LIKE '% son%' AND gloss_en NOT LIKE '%poison%')
        OR gloss_en LIKE '%daughter%'
        OR gloss_en LIKE '%uncle%' OR gloss_en LIKE '%aunt%'
        OR gloss_en LIKE '%grandmother%' OR gloss_en LIKE '%grandfather%'
        OR gloss_en LIKE '%grandchild%' OR gloss_en LIKE '%grandson%'
        OR gloss_en LIKE '%granddaughter%' OR gloss_en LIKE '%wife%'
        OR gloss_en LIKE '%husband%' OR gloss_en LIKE '% child%' OR gloss_en LIKE 'child%'
        OR gloss_en LIKE '%sibling%' OR gloss_en LIKE '%cousin%'
        OR gloss_en LIKE '%oldest son%' OR gloss_en LIKE '%oldest daughter%'
        OR gloss_en LIKE '%stepmother%' OR gloss_en LIKE '%stepfather%'
        OR gloss_en LIKE '%in-law%' OR gloss_en LIKE '%relative%'
    """,

    # ── 10: My Appearance ─────────────────────────────────────────────────────
    10: """
        part_of_speech IN ('adj','adjective') AND (
            gloss_en LIKE '%tall%' OR gloss_en LIKE '%short%' OR gloss_en LIKE '%fat%'
            OR gloss_en LIKE '%thin%' OR gloss_en LIKE '% old%' OR gloss_en LIKE 'old%'
            OR gloss_en LIKE '%young%' OR gloss_en LIKE '%strong%' OR gloss_en LIKE '%weak%'
            OR gloss_en LIKE '%beautiful%' OR gloss_en LIKE '%ugly%' OR gloss_en LIKE '%long%'
            OR gloss_en LIKE 'small%' OR gloss_en LIKE '%tiny%' OR gloss_en LIKE '%angry%'
            OR gloss_en LIKE '%happy%' OR gloss_en LIKE '%sad%' OR gloss_en LIKE '%dry%'
            OR gloss_en LIKE '%clean%' OR gloss_en LIKE '%dirty%' OR gloss_en LIKE '%clear%'
            OR gloss_en LIKE 'hot%' OR gloss_en LIKE 'cold%' OR gloss_en LIKE '%heavy%'
            OR gloss_en LIKE '%light%' OR gloss_en LIKE 'good%' OR gloss_en LIKE 'bad%'
            OR gloss_en LIKE '%fast%' OR gloss_en LIKE '%slow%' OR gloss_en LIKE '%loud%'
            OR gloss_en LIKE '%quiet%' OR gloss_en LIKE '%alone%'
        )
    """,

    # ── 11: Greetings and farewell ────────────────────────────────────────────
    11: glike(
        "hello%", "%goodbye%", "%farewell%",
        "good morning%", "good afternoon%", "good night%",
        "how are you%", "how's it going%",
        "thank%", "you're welcome%", "think nothing%",
        "yes%", "no, negative%", "fine%", "ok%", "great%",
        "%greeting%", "excuse me%", "sorry%", "please%",
        "good luck%", "take care%",
    ),

    # ── 12: Future tense and indefinite verbs ─────────────────────────────────
    12: """
        part_of_speech = 'verb' AND (
            gloss_en LIKE 'to know%' OR gloss_en LIKE 'to speak%' OR gloss_en LIKE 'to talk%'
            OR gloss_en LIKE 'to say%' OR gloss_en LIKE 'to tell%' OR gloss_en LIKE 'to write%'
            OR gloss_en LIKE 'to read%' OR gloss_en LIKE 'to have%' OR gloss_en LIKE 'to want%'
            OR gloss_en LIKE 'to need%' OR gloss_en LIKE 'to understand%'
            OR gloss_en LIKE 'to learn%' OR gloss_en LIKE 'to teach%'
            OR gloss_en LIKE 'to think%' OR gloss_en LIKE 'to see%' OR gloss_en LIKE 'to hear%'
            OR gloss_en LIKE 'to call%' OR gloss_en LIKE 'to ask%' OR gloss_en LIKE 'to answer%'
            OR gloss_en LIKE 'to remember%' OR gloss_en LIKE 'to forget%'
            OR gloss_en LIKE 'to love%' OR gloss_en LIKE 'to like%' OR gloss_en LIKE 'to converse%'
        )
    """,

    # ── 13: Verbs with specific object ────────────────────────────────────────
    13: """
        part_of_speech = 'verb' AND (
            gloss_en LIKE 'to eat%' OR gloss_en LIKE 'to drink%' OR gloss_en LIKE 'to cook%'
            OR gloss_en LIKE 'to make%' OR gloss_en LIKE 'to buy%' OR gloss_en LIKE 'to sell%'
            OR gloss_en LIKE 'to give%' OR gloss_en LIKE 'to take%' OR gloss_en LIKE 'to carry%'
            OR gloss_en LIKE 'to bring%' OR gloss_en LIKE 'to find%' OR gloss_en LIKE 'to use%'
            OR gloss_en LIKE 'to send%' OR gloss_en LIKE 'to put%' OR gloss_en LIKE 'to plant%'
            OR gloss_en LIKE 'to sign%' OR gloss_en LIKE 'to grind%' OR gloss_en LIKE 'to build%'
            OR gloss_en LIKE 'to wash%' OR gloss_en LIKE 'to prepare%' OR gloss_en LIKE 'to cut%'
            OR gloss_en LIKE 'to receive%' OR gloss_en LIKE 'to leave%'
        )
    """,

    # ── 14: Past Tense Part 1 ─────────────────────────────────────────────────
    14: """
        part_of_speech = 'verb' AND (
            gloss_en LIKE 'to enter%' OR gloss_en LIKE 'to exit%'
            OR gloss_en LIKE 'to die%' OR gloss_en LIKE 'to fall%'
            OR gloss_en LIKE 'to flee%' OR gloss_en LIKE 'to swim%'
            OR gloss_en LIKE 'to jump%' OR gloss_en LIKE 'to climb%'
            OR gloss_en LIKE 'to descend%' OR gloss_en LIKE 'to cross%'
            OR gloss_en LIKE 'to travel%' OR gloss_en LIKE 'to ride%'
            OR gloss_en LIKE 'to be afraid%' OR gloss_en LIKE 'to hide%'
            OR gloss_en LIKE 'to be born%' OR gloss_en LIKE 'to grow%'
            OR gloss_en LIKE 'to chase%' OR gloss_en LIKE 'to follow%'
            OR gloss_en LIKE 'to fight%' OR gloss_en LIKE 'to win%'
            OR gloss_en LIKE 'to lose%' OR gloss_en LIKE 'to open%'
            OR gloss_en LIKE 'to close%' OR gloss_en LIKE 'to turn%'
        )
    """,

    # ── 15: Past Tense Part 2 ─────────────────────────────────────────────────
    15: """
        part_of_speech = 'verb' AND (
            gloss_en LIKE 'to be sick%' OR gloss_en LIKE 'to cure%' OR gloss_en LIKE 'to heal%'
            OR gloss_en LIKE 'to sweat%' OR gloss_en LIKE 'to cry%' OR gloss_en LIKE 'to laugh%'
            OR gloss_en LIKE 'to sing%' OR gloss_en LIKE 'to dance%' OR gloss_en LIKE 'to play%'
            OR gloss_en LIKE 'to work%' OR gloss_en LIKE 'to rest%' OR gloss_en LIKE 'to help%'
            OR gloss_en LIKE 'to lie%' OR gloss_en LIKE 'to dig%' OR gloss_en LIKE 'to sweep%'
            OR gloss_en LIKE 'to clean%' OR gloss_en LIKE 'to hurt%' OR gloss_en LIKE 'to ache%'
            OR gloss_en LIKE 'to have a cold%' OR gloss_en LIKE 'to have a fever%'
            OR gloss_en LIKE 'to cough%' OR gloss_en LIKE 'to sneeze%'
        )
    """,

    # ── 16: Past Tense Part 3 ─────────────────────────────────────────────────
    16: """
        part_of_speech = 'verb' AND (
            gloss_en LIKE 'to finish%' OR gloss_en LIKE 'to begin%' OR gloss_en LIKE 'to start%'
            OR gloss_en LIKE 'to stop%' OR gloss_en LIKE 'to break%' OR gloss_en LIKE 'to fix%'
            OR gloss_en LIKE 'to drop%' OR gloss_en LIKE 'to fill%' OR gloss_en LIKE 'to count%'
            OR gloss_en LIKE 'to pay%' OR gloss_en LIKE 'to steal%' OR gloss_en LIKE 'to touch%'
            OR gloss_en LIKE 'to push%' OR gloss_en LIKE 'to pull%' OR gloss_en LIKE 'to lift%'
            OR gloss_en LIKE 'to throw%' OR gloss_en LIKE 'to drop%' OR gloss_en LIKE 'to spill%'
            OR gloss_en LIKE 'to remember%' OR gloss_en LIKE 'to tie%' OR gloss_en LIKE 'to untie%'
            OR gloss_en LIKE 'to measure%' OR gloss_en LIKE 'to weigh%' OR gloss_en LIKE 'to split%'
        )
    """,

    # ── 17: I Sit in the Chair ────────────────────────────────────────────────
    17: glike(
        "%chair%", "%table%", "%bed%", "%door%", "%window%", "%wall%",
        "%floor%", "%roof%", "%kitchen%", "pot%", "%cooking pot%", "%pan%",
        "%plate%", "%cup%", "%bowl%", "%gourd bowl%", "%cloth%", "%clothing%",
        "%shirt%", "%blanket%", "%candle%", "fire%", "%lamp%", "%broom%",
        "%smoke%", "%rope%", "%mat%", "%straw%",
    ),

    # ── 18: What I Like and Do Not Like ──────────────────────────────────────
    18: glike(
        "good%", "bad%", "tasty%", "delicious%", "hungry%", "thirsty%",
        "sweet%", "bitter%", "sour%", "spicy%", "%smell%", "%odor%",
        "%like%", "%enjoy%", "%hate%", "%beautiful%", "%ugly%",
        "happy%", "sad%", "angry%",
    ),

    # ── 19: Stand Up! ─────────────────────────────────────────────────────────
    19: """
        part_of_speech = 'verb' AND (
            gloss_en LIKE 'to stand%' OR gloss_en LIKE 'to sit down%'
            OR gloss_en LIKE 'to get up%' OR gloss_en LIKE 'to lie down%'
            OR gloss_en LIKE 'to rise%' OR gloss_en LIKE 'to bend%'
            OR gloss_en LIKE 'to look%' OR gloss_en LIKE 'to listen%'
            OR gloss_en LIKE 'to reach%' OR gloss_en LIKE 'to grab%'
            OR gloss_en LIKE 'to hold%' OR gloss_en LIKE 'to approach%'
            OR gloss_en LIKE 'to leave%' OR gloss_en LIKE 'to drive%'
            OR gloss_en LIKE 'to get dressed%' OR gloss_en LIKE 'to undress%'
            OR gloss_en LIKE 'to get on%' OR gloss_en LIKE 'to order%'
            OR gloss_en LIKE 'to command%' OR gloss_en LIKE 'to obey%'
        )
    """,

    # ── 20: Grammar of -pil and -tzin ────────────────────────────────────────
    20: """
        (gloss_en LIKE '%man%' OR gloss_en LIKE '%woman%'
         OR gloss_en LIKE '% boy%' OR gloss_en LIKE '% girl%'
         OR gloss_en LIKE '%young man%' OR gloss_en LIKE '%young woman%'
         OR gloss_en LIKE '%friend%' OR gloss_en LIKE '%neighbor%'
         OR gloss_en LIKE '%community%' OR gloss_en LIKE '%people%'
         OR gloss_en LIKE '%elder%' OR gloss_en LIKE '% old man%'
         OR gloss_en LIKE '%widow%' OR gloss_en LIKE '%orphan%'
         OR gloss_en LIKE '%newcomer%' OR gloss_en LIKE '%foreigner%'
         OR gloss_en LIKE '%Mexican%' OR gloss_en LIKE '%Nahua%'
        )
        AND gloss_en NOT LIKE '%woman%s%'
        AND part_of_speech IN ('noun','name')
    """,

    # ── 21: What We Have in the Field ────────────────────────────────────────
    21: glike(
        "%field%", "%milpa%", "%cornfield%", "%land%", "%earth%",
        "corn%", "% corn%", "%cob%", "%maize%",
        "%goat%", "cow%", "%cattle%", "%bull%", "%horse%",
        "dog%", "cat%", "bird%", "%chicken%", "%turkey%", "%rabbit%",
        "%bee%", "%insect%", "%snake%", "%deer%",
        "%flower%", "%tree%", "%plant%", "%grass%", "%weed%",
        "%rain%", "%river%", "%spring%", "%mountain%",
    ),

    # ── 22: Our Cornfield and Our Food ────────────────────────────────────────
    22: glike(
        "bean%", "% bean%", "%tortilla%", "corn%", "tamale%",
        "%dough%", "water%", "%masa%", "%atole%",
        "squash%", "%gourd%", "%pumpkin%", "%sweet potato%",
        "avocado%", "%tomato%", "%onion%", "%herb%", "salt%",
        "%chili%", "%chile%", "%pepper%", "food%", "%cooked food%",
        "to eat%", "to cook%", "cornfield%",
    ),

    # ── 23: What is Inside the House ─────────────────────────────────────────
    23: glike(
        "house%", "% house%", "home%", "book%", "paper%",
        "letter%", "map%", "rope%", "%cord%", "basket%",
        "%bag%", "needle%", "thread%", "%clay%", "medicine%",
        "blanket%", "%storage%", "barn%", "hay%",
        "candle%", "%broom%", "%grinding stone%", "torch%",
    ),

    # ── 24: I Had Gone to the City Part 1 ────────────────────────────────────
    24: glike(
        "city%", "%town%", "%village%", "%mountain%", "%hill%",
        "%river%", "%forest%", "%road%", "%path%", "%bridge%",
        "%market%", "%church%", "%school%", "%plaza%", "%street%",
        "here%", "there%", "%over there%",
        "%government%", "country%", "%state%",
    ),

    # ── 25: I Had Gone to the City Part 2 ────────────────────────────────────
    25: glike(
        "then%", "next%", "%after%", "%before%", "above%", "below%",
        "under%", "inside%", "outside%", "%in front%", "behind%",
        "near%", "far%", "until%", "%because%", "also%",
        "%still%", "%even%", "only%", "already%",
    ),

    # ── 26: I Came to Buy a Tortilla Napkin ──────────────────────────────────
    26: glike(
        "bread%", "tamale%", "tortilla%", "dough%", "%orange%",
        "shrimp%", "comal%", "%griddle%", "to buy%", "to sell%",
        "money%", "%peso%", "%price%", "%cloth%", "%napkin%",
        "basket%", "%bag%", "to trade%", "to exchange%", "market%",
    ),

    # ── 27: It's Market Day Today! ────────────────────────────────────────────
    27: glike(
        "chocolate%", "coffee%", "soda%", "fish%", "meat%",
        "fruit%", "avocado%", "mango%", "%chili%", "%chile%",
        "sugar%", "honey%", "lime%", "lemon%", "banana%",
        "pineapple%", "papaya%", "food%", "drink%", "%vendor%",
        "watermelon%", "%juice%",
    ),

    # ── 28: I Was Passing By Your House ──────────────────────────────────────
    28: glike(
        "% home%", "home%", "to visit%", "companion%", "to pass%",
        "to knock%", "to wait%", "to invite%", "%together%", "%neighbor%",
        "to stay%", "to greet%", "door%", "to enter%", "to arrive%",
    ),

    # ── 29: What Illnesses Do You Know? ──────────────────────────────────────
    29: glike(
        "%sick%", "%illness%", "%disease%", "%sickness%",
        "% cold%", "a cold%", "fever%", "%cough%",
        "pain%", "%ache%", "to cure%", "to heal%",
        "medicine%", "death%", "dead%",
        "%head%", "%stomach%", "%throat%", "%tooth%", "%bone%",
        "%body%", "to suffer%", "wound%",
    ),

    # ── 30: The Conditional Part 1 ────────────────────────────────────────────
    30: """
        gloss_en LIKE 'if%'
        OR gloss_en LIKE 'but%'
        OR gloss_en LIKE 'never%'
        OR gloss_en LIKE 'not yet%'
        OR gloss_en LIKE 'not%'
        OR gloss_en LIKE 'because%'
        OR gloss_en LIKE 'although%'
        OR gloss_en LIKE 'perhaps%'
        OR gloss_en LIKE 'maybe%'
        OR gloss_en LIKE 'when%'
        OR gloss_en LIKE 'while%'
        OR gloss_en LIKE 'once%'
        OR gloss_en LIKE 'just%'
        OR gloss_en LIKE 'only%'
        OR gloss_en LIKE 'except%'
        OR gloss_en LIKE 'indeed%'
        OR gloss_en LIKE 'truly%'
        OR gloss_en LIKE 'really%'
    """,

    # ── 31: Cleansing Ceremonies ──────────────────────────────────────────────
    31: glike(
        "song%", "prayer%", "ritual%", "ceremony%",
        "god%", "spirit%", "sacred%",
        "smoke%", "incense%", "fire%",
        "sky%", "sun%", "moon%", "star%", "wind%", "rain%",
        "earth%", "flower%", "honey%", "snow%", "%butterfly%",
        "%thunder%", "%lightning%", "%cloud%", "sea%",
    ),

    # ── 32: Tē- and tla- non-specific object markers ──────────────────────────
    32: glike(
        "other%", "another%", "all%", "none%", "some%",
        "just%", "only%", "very%", "like%", "as %",
        "in%", "on%", "with%", "from%", "by%",
        "plural%", "that%", "which%", "still%",
        "%suffix%", "%prefix%", "%marker%",
    ),
}

# ── Build all unit vocab, global dedup ────────────────────────────────────────
ALL_UNITS: dict[int, list[tuple]] = {}
used_forms: set[str] = set()

# Unit 1 first (no dedup needed)
ALL_UNITS[1] = [(form, gloss, pos, "EHN_colloquial") for form, gloss, pos in ALPHABET]
for form, *_ in ALPHABET:
    used_forms.add(form.lower())

for unit_num in sorted(UNIT_QUERIES.keys()):
    rows = fetchq(UNIT_QUERIES[unit_num], limit=30)
    kept = []
    for form, gloss, pos, reg in rows:
        key = form.lower()
        if key in used_forms:
            continue
        used_forms.add(key)
        kept.append((form, gloss, pos, reg))
    ALL_UNITS[unit_num] = kept

# ── Write to SQLite ────────────────────────────────────────────────────────────
db.execute("DROP TABLE IF EXISTS lesson_vocab")
db.execute("""
    CREATE TABLE lesson_vocab (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_number   INTEGER NOT NULL,
        rank            INTEGER,
        entry_id        TEXT,
        display_form    TEXT NOT NULL,
        ehn_spoken_form TEXT,
        gloss_en        TEXT NOT NULL,
        part_of_speech  TEXT,
        semantic_domain TEXT,
        pedagogical_score INTEGER
    )
""")

rows_to_insert = []
for unit_num, items in sorted(ALL_UNITS.items()):
    for rank, (form, gloss, pos, reg) in enumerate(items, 1):
        rows_to_insert.append((
            unit_num, rank, None,
            form,
            form if reg == "EHN_colloquial" else None,
            gloss, pos, reg, 0,
        ))

db.executemany("""
    INSERT INTO lesson_vocab
      (lesson_number, rank, entry_id, display_form, ehn_spoken_form,
       gloss_en, part_of_speech, semantic_domain, pedagogical_score)
    VALUES (?,?,?,?,?,?,?,?,?)
""", rows_to_insert)
db.commit()

# ── Report ─────────────────────────────────────────────────────────────────────
total = len(rows_to_insert)
print(f"Inserted {total} vocab items across {len(ALL_UNITS)} units.\n")
for unit_num, items in sorted(ALL_UNITS.items()):
    preview = " · ".join(f"{form} ({gloss[:18]})" for form, gloss, *_ in items[:6])
    print(f"Unit {unit_num:2d} ({len(items):2d} items): {preview}{'...' if len(items)>6 else ''}")
