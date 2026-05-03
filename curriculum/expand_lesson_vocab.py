#!/usr/bin/env python3
"""
expand_lesson_vocab.py — add EHN lexicon_entries to lesson_vocab,
creating new thematic lesson units beyond the existing 32.

Run from any directory:
    python expand_lesson_vocab.py

Idempotent: checks for existing entries before inserting.
"""
from __future__ import annotations
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DB = ROOT / "database" / "fcn_master_lexicon_phase8_6_primer.sqlite"
LEGACY_DB = Path(__file__).parent / "fcn_master_lexicon_phase8_6_primer.sqlite"
DB = CANONICAL_DB if CANONICAL_DB.exists() else LEGACY_DB

# Variety preference order for deduplication (lower index = preferred)
VARIETY_RANK = {
    "Eastern Huasteca Nahuatl": 0,
    "Central Huasteca Nahuatl": 1,
    "Central Nahuatl": 2,
    "Classical Nahuatl": 3,
}

# Semantic groups → (start_lesson_number, theme, band, communicative_goal)
# Words are assigned greedily to the first matching group.
GROUPS: list[dict] = [
    # Months: exact English month names only
    {
        "id": "months",
        "lesson_num": 33,
        "theme": "The Months of the Year",
        "band": "A1",
        "goal": "Name all twelve months in Nahuatl",
        "pos": "noun",
        "exact_keywords": [
            "january","february","march","april","may","june",
            "july","august","september","october","november","december",
        ],
    },
    # Numbers: only pure number words
    {
        "id": "numbers",
        "lesson_num": 34,
        "theme": "Numbers and Counting",
        "band": "A1",
        "goal": "Count and use ordinal and cardinal numbers",
        "pos": "num",
        "exact_keywords": None,  # all num POS entries
    },
    # Colors: exact color names only — no POS filter since color words appear
    # as both adj and noun in this database.
    {
        "id": "colors",
        "lesson_num": 35,
        "theme": "Colors",
        "band": "A1",
        "goal": "Name colors to describe objects",
        "pos": None,
        "exact_keywords": [
            "red","blue","green","yellow","black","white","orange","pink",
            "purple","brown","gray","grey","color","colour",
            "coffee color, brown",
        ],
    },
    # Sizes/shapes: no POS filter for same reason
    {
        "id": "sizes_shapes",
        "lesson_num": 36,
        "theme": "Sizes and Shapes",
        "band": "A1",
        "goal": "Describe size and physical dimensions",
        "pos": None,
        "exact_keywords": [
            "big, great","big","large","great","small","little","tiny",
            "tall","short","long","wide","wide, ample","ample","narrow",
            "thin","thick","round","flat","deep",
        ],
    },
    # General descriptive adjectives
    {
        "id": "qualities",
        "lesson_num": 37,
        "theme": "Describing Things",
        "band": "A2",
        "goal": "Use adjectives to describe conditions and qualities",
        "pos": "adj",
        "keywords": [
            "good","bad","new","old","clean","dirty","hot","cold","dry",
            "hard","fast","slow","strong","weak","clear","expensive",
            "beautiful","ugly","pure","holy","cooked","fallen","silly",
            "tasty","good-smelling","happy","angry","hungry","alone","bloody",
        ],
    },
    # Animals: must be POS=noun and gloss ≤ 3 words, containing animal keywords
    {
        "id": "animals",
        "lesson_num": 38,
        "theme": "Animals",
        "band": "A2",
        "goal": "Name animals you might encounter",
        "pos": "noun",
        "keywords": [
            "cat","dog","bird","fish","horse","cow","pig","chicken","hen",
            "turkey","rabbit","deer","coyote","snake","frog","toad","lizard",
            "butterfly","bee","ant","grasshopper","eagle","owl",
            "dove","duck","parrot","jaguar","ocelot","spider","scorpion",
            "dragonfly","alligator","armadillo","squirrel","possum","skunk",
        ],
    },
    # Food items (nouns only, short glosses)
    {
        "id": "food_extra",
        "lesson_num": 39,
        "theme": "More Food and Ingredients",
        "band": "A2",
        "goal": "Talk about more foods and ingredients",
        "pos": "noun",
        "keywords": [
            "corn","maize","bean","tortilla","chile","chili","tomato",
            "fruit","meat","salt","sugar","pepper","egg","avocado",
            "squash","mushroom","herb","oil","flour","dough","alcohol",
            "milpa","cultivated field",
        ],
    },
    # Household objects and tools
    {
        "id": "household",
        "lesson_num": 40,
        "theme": "Around the House",
        "band": "A2",
        "goal": "Name household objects and tools",
        "pos": "noun",
        "keywords": [
            "sack","sandal","trap","pan","pot","rope","blanket","candle",
            "broom","mortar","grind","mill","letter","cup","plate",
        ],
    },
    # Nature vocabulary
    {
        "id": "nature",
        "lesson_num": 41,
        "theme": "Nature and the World",
        "band": "A2",
        "goal": "Talk about the natural world",
        "pos": "noun",
        "keywords": [
            "tree","flower","leaf","field","milpa","corn field","kapok","ceiba",
            "river","lake","soil","plain","land","stone","sand","seed","root",
            "mountain","forest","jungle","grass","herb","bush","vine",
        ],
    },
    # People and community roles
    {
        "id": "community",
        "lesson_num": 42,
        "theme": "People and Roles",
        "band": "A2",
        "goal": "Describe people, roles, and community",
        "pos": "noun",
        "keywords": [
            "person","man","woman","child","elder","teacher","doctor",
            "worker","farmer","merchant","friend","leader","angel",
            "mexican","nahuan","grinder","sick person","miller",
            "oldest","miss","city","town","village","altepetl",
        ],
    },
    # All remaining verbs
    {
        "id": "verbs_extra",
        "lesson_num": 43,
        "theme": "More Action Words",
        "band": "B1",
        "goal": "Expand verb vocabulary for everyday activities",
        "pos": "verb",
        "exact_keywords": None,  # all remaining verbs
    },
    # All remaining adverbs
    {
        "id": "adverbs",
        "lesson_num": 44,
        "theme": "Adverbs and Modifiers",
        "band": "B1",
        "goal": "Use adverbs to modify verbs and describe manner",
        "pos": "adv",
        "exact_keywords": None,  # all remaining adverbs
    },
]


def normalize_gloss(g: str) -> str:
    """Lowercase, strip punctuation for matching."""
    return re.sub(r"[.,!?;:\-\(\)]", "", g).lower().strip()


def gloss_matches(gloss: str, keywords: list[str]) -> bool:
    """Match whole words only, and the gloss must be short (a translation
    not a definition) — e.g. 'green' should NOT match 'green beans'."""
    norm = normalize_gloss(gloss)
    words = set(norm.split())
    # Require that a keyword is a complete word AND the gloss has ≤ 4 words
    # (so "orange" matches "orange" or "orange color" but not "orange tree juice")
    if len(norm.split()) > 4:
        return False
    for kw in keywords:
        # Allow multi-word keywords (e.g. "corn field") by checking substring
        # but single-word keywords must be whole words
        kw_words = kw.split()
        if len(kw_words) == 1:
            if kw in words:
                return True
        else:
            if kw in norm:
                return True
    return False


def gloss_is_exactly(gloss: str, keywords: list[str]) -> bool:
    """The gloss must be essentially equal to one keyword (exact match)."""
    norm = normalize_gloss(gloss)
    for kw in keywords:
        if norm == kw or norm == kw + "s":
            return True
    return False


def best_entry(candidates: list[dict]) -> dict:
    """From duplicate headwords/glosses, pick the best entry."""
    def rank(e: dict) -> tuple:
        variety_score = VARIETY_RANK.get(e["variety"], 99)
        g = e["gloss_en"]
        # Prefer: EHN > CHN > CN > Classical; shorter gloss; no leading article
        is_clean = not g.startswith(("A ", "An ", "The "))
        # Prefer entries with an ehn_spoken_form (= actual spoken EHN word)
        has_spoken = bool((e.get("ehn_spoken_form") or "").strip())
        gloss_len = len(g)
        return (variety_score, not has_spoken, not is_clean, gloss_len)
    return min(candidates, key=rank)


def deduplicate_by_gloss(entries: list[dict]) -> list[dict]:
    """Within a lesson group, keep only one entry per concept (normalized gloss).
    Handles e.g. multiple dialect forms for 'rabbit': tochij/koatochi/kuatochin."""
    by_gloss: dict[str, list[dict]] = {}
    for e in entries:
        key = normalize_gloss(e["gloss_en"])
        by_gloss.setdefault(key, []).append(e)
    return [best_entry(group) for group in by_gloss.values()]


def display_form(e: dict) -> str:
    return (e["ehn_spoken_form"] or e["msn_headword"] or "").strip()


def main() -> None:
    if not DB.exists():
        raise SystemExit(f"Database not found: {DB}")

    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    # ── Load EHN + CHN unused, clean glossed entries only ───────────────────
    # We teach Eastern Huasteca Nahuatl — exclude Classical/Central forms so
    # learners hear authentic EHN pronunciation.
    cur = conn.execute("""
        SELECT entry_id, ehn_spoken_form, msn_headword, gloss_en,
               part_of_speech, variety
        FROM lexicon_entries
        WHERE is_active = 1
          AND variety IN ('Eastern Huasteca Nahuatl', 'Central Huasteca Nahuatl')
          AND gloss_en IS NOT NULL AND gloss_en != ''
          AND gloss_en NOT LIKE 'alternative spelling%'
          AND gloss_en NOT LIKE 'obsolete spelling%'
          AND gloss_en NOT LIKE 'Chiconamel spelling%'
          AND entry_id NOT IN (
              SELECT entry_id FROM lesson_vocab WHERE entry_id IS NOT NULL
          )
        ORDER BY entry_id
    """)
    all_unused = [dict(r) for r in cur.fetchall()]

    # ── Deduplicate by display form ──────────────────────────────────────────
    by_form: dict[str, list[dict]] = {}
    for e in all_unused:
        form = display_form(e).lower()
        if not form:
            continue
        by_form.setdefault(form, []).append(e)

    deduped = [best_entry(group) for group in by_form.values()]
    print(f"Unique unused entries after deduplication: {len(deduped)}")

    # ── Assign entries to lesson groups ─────────────────────────────────────
    assigned: set[str] = set()
    groups_entries: dict[str, list[dict]] = {g["id"]: [] for g in GROUPS}

    # Pass 1: exact-keyword and keyword-based assignment
    for e in deduped:
        gloss = e["gloss_en"]
        pos = (e["part_of_speech"] or "").lower()
        for group in GROUPS:
            if e["entry_id"] in assigned:
                break
            gpos = group.get("pos")
            exact = group.get("exact_keywords")
            keywords = group.get("keywords", [])

            # POS must match if specified
            if gpos and gpos != pos:
                continue

            if exact is not None and exact:
                # Exact match group (e.g. months, colors)
                if gloss_is_exactly(gloss, exact):
                    groups_entries[group["id"]].append(e)
                    assigned.add(e["entry_id"])
                    break
            elif exact is None and not keywords:
                # POS-only catch-all — handled in pass 2
                pass
            elif keywords:
                # Keyword fuzzy match
                if gloss_matches(gloss, keywords):
                    groups_entries[group["id"]].append(e)
                    assigned.add(e["entry_id"])
                    break

    # Pass 2: POS-only catch-all groups for remaining entries
    remaining = [e for e in deduped if e["entry_id"] not in assigned]
    for e in remaining:
        pos = (e["part_of_speech"] or "").lower()
        for group in GROUPS:
            gpos = group.get("pos")
            exact = group.get("exact_keywords")
            keywords = group.get("keywords", [])
            # Only catch-all groups: have pos, no keywords, exact_keywords=None
            if gpos and gpos == pos and exact is None and not keywords:
                groups_entries[group["id"]].append(e)
                assigned.add(e["entry_id"])
                break

    unassigned = [e for e in deduped if e["entry_id"] not in assigned]
    print(f"Unassigned after grouping: {len(unassigned)}")

    # ── Check which lessons already exist ───────────────────────────────────
    existing_lessons = {
        row[0]
        for row in conn.execute("SELECT lesson_number FROM phase82_unit_plan").fetchall()
    }
    existing_display_forms = {
        row[0].lower()
        for row in conn.execute(
            "SELECT display_form FROM lesson_vocab WHERE display_form IS NOT NULL"
        ).fetchall()
    }

    # ── Insert new lessons and vocab ─────────────────────────────────────────
    total_inserted = 0
    for group in GROUPS:
        gid = group["id"]
        entries = groups_entries[gid]
        if not entries:
            continue

        lesson_num = group["lesson_num"]
        theme = group["theme"]
        band = group["band"]
        goal = group["goal"]

        # Skip already-inserted lessons
        if lesson_num in existing_lessons:
            print(f"  Lesson {lesson_num} ({theme}) already exists — skipping")
            continue

        # Filter out entries whose display_form is already in lesson_vocab
        # Deduplicate within lesson by concept (same gloss = same word)
        entries = deduplicate_by_gloss(entries)

        # Exclude words whose display form is already taught
        entries = [
            e for e in entries
            if display_form(e).lower() not in existing_display_forms
        ]
        if not entries:
            print(f"  Lesson {lesson_num} ({theme}) -- all entries already in vocab, skipping")
            continue

        # Cap at 50 words per lesson (app chunks into 10 per sub-lesson anyway)
        entries = entries[:50]

        # Insert unit
        conn.execute("""
            INSERT OR IGNORE INTO phase82_unit_plan
            (pedagogical_unit_id, unit_code, lesson_number, target_band, domain_label,
             theme_en, communicative_goal, grammar_focus, lexical_focus, output_task,
             english_vocab_count, english_dialogue_count, english_construction_count,
             bilingual_vocab_count, bilingual_dialogue_count, bilingual_construction_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0)
        """, (
            f"EXP-{lesson_num:03d}",
            f"{band}-EXP{lesson_num:02d}",
            lesson_num,
            band,
            group["pos"] or group["id"],
            theme,
            goal,
            "",
            group["pos"] or group["id"],
            "",
            len(entries),
        ))

        for rank, entry in enumerate(entries, 1):
            form = display_form(entry)
            conn.execute("""
                INSERT INTO lesson_vocab
                (lesson_number, rank, entry_id, display_form, ehn_spoken_form,
                 gloss_en, part_of_speech, semantic_domain, pedagogical_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lesson_num, rank, entry["entry_id"],
                form, entry["ehn_spoken_form"],
                entry["gloss_en"], entry["part_of_speech"],
                gid, 50,
            ))
            total_inserted += 1

        print(f"  Lesson {lesson_num} [{band}] {theme} — {len(entries)} words")

    conn.commit()
    conn.close()

    total_before = 703
    print(f"\nDone. lesson_vocab: {total_before} -> {total_before + total_inserted} words")
    print(f"Total new words added: {total_inserted}")


if __name__ == "__main__":
    main()
