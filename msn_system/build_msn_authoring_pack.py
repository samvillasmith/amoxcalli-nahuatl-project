from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MSN_DIR = Path(__file__).resolve().parent
DB_PATH = ROOT / "curriculum" / "fcn_master_lexicon_phase8_6_primer.sqlite"
ORTHO_CANDIDATES = ROOT / "orthography" / "ehn_to_msn_candidates.csv"
EXPORT_DIR = MSN_DIR / "exports"
REPORT_DIR = MSN_DIR / "reports"


CORE_FIELDS = [
    "entry_id",
    "source_form",
    "current_db_msn_headword",
    "proposed_msn_headword",
    "part_of_speech",
    "gloss_en",
    "gloss_es",
    "primer_overlap",
    "review_priority",
    "msn_use_status",
    "risk_flags",
    "orthography_basis",
    "search_fallbacks_json",
    "source_id",
    "source_file",
    "source_reference",
    "source_confidence",
    "speaker_validation_status",
    "editorial_status",
    "recommended_action",
]

AUTHORING_FIELDS = [
    "entry_id",
    "msn_headword",
    "ehn_spoken_form",
    "part_of_speech",
    "gloss_en",
    "gloss_es",
    "authoring_domain",
    "use_status",
    "source_confidence",
    "review_note",
]

APPROVAL_SEED_FIELDS = [
    "entry_id",
    "source_form",
    "proposed_msn_headword",
    "part_of_speech",
    "gloss_en",
    "approval_status",
    "approval_scope",
    "approval_note",
    "source_id",
    "source_file",
    "source_reference",
    "source_confidence",
]

PATTERN_FIELDS = [
    "pattern_id",
    "register",
    "domain",
    "english_frame",
    "msn_pattern",
    "slots",
    "evidence_status",
    "review_note",
]

GENRE_FIELDS = [
    "genre_id",
    "book_type",
    "recommended_register",
    "difficulty",
    "best_first",
    "required_next_pack",
    "notes",
]


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def load_orthography_candidates() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    if not ORTHO_CANDIDATES.exists():
        return rows
    with ORTHO_CANDIDATES.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rows[row["entry_id"]] = row
    return rows


def load_primer_headwords(conn: sqlite3.Connection) -> set[str]:
    values: set[str] = set()
    for row in conn.execute("SELECT headword FROM primer_vocab WHERE headword IS NOT NULL"):
        values.add(clean(row["headword"]).lower())
    return values


def risk_flags(row: sqlite3.Row, proposed: str) -> list[str]:
    flags: list[str] = []
    gloss = clean(row["gloss_en"]).lower()
    pos = clean(row["part_of_speech"]).lower()
    headword = proposed.lower()
    source_form = clean(row["ehn_spoken_form"]).lower()

    if "obsolete spelling" in gloss:
        flags.append("obsolete_spelling_gloss")
    if "alternative spelling" in gloss:
        flags.append("alternative_spelling_gloss")
    if "misspelling" in gloss:
        flags.append("misspelling_gloss")
    if "plural of" in gloss or "form of" in gloss:
        flags.append("inflected_or_reference_form")
    if pos == "suffix" or headword.startswith("-") or source_form.startswith("-"):
        flags.append("bound_morpheme")
    if pos == "name":
        flags.append("proper_name")
    if gloss in {"april", "august", "december", "february", "january", "july", "june", "march", "may", "november", "october", "september"}:
        flags.append("calendar_loan_or_name")
    if any(word in gloss for word in ["obsolete", "archaic"]):
        flags.append("historical_or_archaic_note")
    return flags


def domain_for(row: dict[str, str]) -> str:
    gloss = row["gloss_en"].lower()
    pos = row["part_of_speech"].lower()
    if row["primer_overlap"] == "yes":
        return "primer_core"
    if pos in {"pron", "det", "prep", "conj", "particle", "adv", "num"}:
        return "function_and_structure"
    if any(word in gloss for word in ["corn", "bean", "chili", "food", "water", "house", "work", "school", "family", "mother", "father"]):
        return "daily_life"
    if pos == "verb":
        return "actions"
    if pos in {"adj", "noun"}:
        return "general_vocabulary"
    return "special_review"


def build_core_candidates(conn: sqlite3.Connection) -> list[dict[str, str]]:
    ortho = load_orthography_candidates()
    primer = load_primer_headwords(conn)
    rows: list[dict[str, str]] = []
    sql = """
        SELECT
            entry_id,
            ehn_spoken_form,
            msn_headword,
            part_of_speech,
            gloss_en,
            gloss_es,
            source_id,
            source_file,
            source_reference,
            source_confidence,
            speaker_validation_status,
            editorial_status
        FROM lexicon_entries
        WHERE register = 'EHN_colloquial' AND is_active = 1
        ORDER BY lower(coalesce(msn_headword, ehn_spoken_form, entry_id)), entry_id
    """
    for row in conn.execute(sql):
        entry_id = row["entry_id"]
        ortho_row = ortho.get(entry_id, {})
        proposed = clean(ortho_row.get("candidate_msn_headword")) or clean(row["msn_headword"]) or clean(row["ehn_spoken_form"])
        candidates = {clean(row["msn_headword"]).lower(), clean(row["ehn_spoken_form"]).lower(), proposed.lower()}
        has_primer_overlap = bool(candidates & primer)
        flags = risk_flags(row, proposed)

        if flags:
            priority = "P4_cleanup_not_for_authoring"
            status = "needs_cleanup_or_special_review"
            action = "Do not use in public MSN prose until the risk flag is resolved."
        elif has_primer_overlap:
            priority = "P1_primer_core_candidate"
            status = "candidate_internal_use"
            action = "Review first; likely useful for initial MSN authoring."
        else:
            priority = "P2_general_ehn_candidate"
            status = "candidate_internal_use"
            action = "Review after primer-core candidates; usable for controlled drafting once checked."

        rows.append(
            {
                "entry_id": entry_id,
                "source_form": clean(row["ehn_spoken_form"]),
                "current_db_msn_headword": clean(row["msn_headword"]),
                "proposed_msn_headword": proposed,
                "part_of_speech": clean(row["part_of_speech"]),
                "gloss_en": clean(row["gloss_en"]),
                "gloss_es": clean(row["gloss_es"]),
                "primer_overlap": "yes" if has_primer_overlap else "no",
                "review_priority": priority,
                "msn_use_status": status,
                "risk_flags": ";".join(flags),
                "orthography_basis": clean(ortho_row.get("rule_trace")) or "current_db_headword",
                "search_fallbacks_json": clean(ortho_row.get("search_fallbacks_json")),
                "source_id": clean(row["source_id"]),
                "source_file": clean(row["source_file"]),
                "source_reference": clean(row["source_reference"]),
                "source_confidence": clean(row["source_confidence"]),
                "speaker_validation_status": clean(row["speaker_validation_status"]),
                "editorial_status": clean(row["editorial_status"]),
                "recommended_action": action,
            }
        )
    return rows


def build_authoring_seed(core_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in core_rows:
        if row["msn_use_status"] != "candidate_internal_use":
            continue
        key = (row["proposed_msn_headword"].lower(), row["part_of_speech"].lower())
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "entry_id": row["entry_id"],
                "msn_headword": row["proposed_msn_headword"],
                "ehn_spoken_form": row["source_form"],
                "part_of_speech": row["part_of_speech"],
                "gloss_en": row["gloss_en"],
                "gloss_es": row["gloss_es"],
                "authoring_domain": domain_for(row),
                "use_status": "internal_drafting_candidate_not_speaker_validated",
                "source_confidence": row["source_confidence"],
                "review_note": "EHN_colloquial source-backed candidate; requires MSN approval before public release.",
            }
        )
    rows.sort(key=lambda r: (r["authoring_domain"], r["msn_headword"].lower(), r["part_of_speech"]))
    return rows


def build_approval_seed(core_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in core_rows:
        if row["review_priority"] != "P1_primer_core_candidate":
            continue
        rows.append(
            {
                "entry_id": row["entry_id"],
                "source_form": row["source_form"],
                "proposed_msn_headword": row["proposed_msn_headword"],
                "part_of_speech": row["part_of_speech"],
                "gloss_en": row["gloss_en"],
                "approval_status": "approved_internal_drafting_only",
                "approval_scope": "controlled_msn_drafting_seed_not_public_release",
                "approval_note": "Primer-overlap EHN_colloquial candidate; suitable for controlled drafting experiments pending MSN editorial and speaker/community review.",
                "source_id": row["source_id"],
                "source_file": row["source_file"],
                "source_reference": row["source_reference"],
                "source_confidence": row["source_confidence"],
            }
        )
    return rows


def sentence_patterns() -> list[dict[str, str]]:
    return [
        {
            "pattern_id": "MSN-PAT-001",
            "register": "MSN_neutral",
            "domain": "identity",
            "english_frame": "This is [NOUN].",
            "msn_pattern": "[DEICTIC] [NOUN].",
            "slots": "DEICTIC,NOUN",
            "evidence_status": "template_for_editorial_drafting",
            "review_note": "Use for children book captions and glossary-style prose.",
        },
        {
            "pattern_id": "MSN-PAT-002",
            "register": "MSN_neutral",
            "domain": "identity",
            "english_frame": "[NOUN] is called [NAME/TERM].",
            "msn_pattern": "[NOUN] [called] [TERM].",
            "slots": "NOUN,called,TERM",
            "evidence_status": "template_for_editorial_drafting",
            "review_note": "Exact verb choice must be checked against approved core.",
        },
        {
            "pattern_id": "MSN-PAT-003",
            "register": "MSN_neutral",
            "domain": "description",
            "english_frame": "[NOUN] is [ADJECTIVE].",
            "msn_pattern": "[NOUN] [ADJECTIVE].",
            "slots": "NOUN,ADJECTIVE",
            "evidence_status": "template_for_editorial_drafting",
            "review_note": "Useful for children book and cookbook descriptions.",
        },
        {
            "pattern_id": "MSN-PAT-004",
            "register": "MSN_neutral",
            "domain": "action",
            "english_frame": "I/we [VERB].",
            "msn_pattern": "[PERSON_PREFIX]-[VERB].",
            "slots": "PERSON_PREFIX,VERB",
            "evidence_status": "template_for_editorial_drafting",
            "review_note": "Verb stem and person marking require D16 grammar confirmation.",
        },
        {
            "pattern_id": "MSN-PAT-005",
            "register": "MSN_neutral",
            "domain": "sequence",
            "english_frame": "First [ACTION], then [ACTION].",
            "msn_pattern": "[FIRST] [ACTION], [THEN/ALSO] [ACTION].",
            "slots": "FIRST,ACTION,THEN",
            "evidence_status": "template_for_editorial_drafting",
            "review_note": "Based on D16 sequence examples; good for cookbook and mindfulness steps.",
        },
        {
            "pattern_id": "MSN-PAT-006",
            "register": "MSN_neutral",
            "domain": "instruction",
            "english_frame": "Do [ACTION].",
            "msn_pattern": "[IMPERATIVE] [ACTION].",
            "slots": "IMPERATIVE,ACTION",
            "evidence_status": "template_for_editorial_drafting",
            "review_note": "Use carefully; imperatives may feel more EHN/spoken depending context.",
        },
        {
            "pattern_id": "MSN-PAT-007",
            "register": "MSN_neutral",
            "domain": "location",
            "english_frame": "[PERSON/THING] is in/at [PLACE].",
            "msn_pattern": "[SUBJECT] [LOCATIVE] [PLACE].",
            "slots": "SUBJECT,LOCATIVE,PLACE",
            "evidence_status": "template_for_editorial_drafting",
            "review_note": "Good for captions, cookbook context, and public prose.",
        },
        {
            "pattern_id": "MSN-PAT-008",
            "register": "MSN_neutral",
            "domain": "possession",
            "english_frame": "My/our [NOUN].",
            "msn_pattern": "[POSSESSIVE_PREFIX]-[NOUN_STEM].",
            "slots": "POSSESSIVE_PREFIX,NOUN_STEM",
            "evidence_status": "template_for_editorial_drafting",
            "review_note": "Requires D16 possession chapter completion before public use.",
        },
        {
            "pattern_id": "MSN-PAT-009",
            "register": "MSN_neutral",
            "domain": "definition",
            "english_frame": "[TERM] means [GLOSS].",
            "msn_pattern": "[TERM] [MEAN/CALL] [GLOSS].",
            "slots": "TERM,MEAN_OR_CALL,GLOSS",
            "evidence_status": "template_for_editorial_drafting",
            "review_note": "Useful for dictionary and glossary prose.",
        },
        {
            "pattern_id": "MSN-PAT-010",
            "register": "MSN_public",
            "domain": "devotional_public",
            "english_frame": "Let us honor [DIVINE/VALUED NOUN].",
            "msn_pattern": "[HORTATIVE] [HONOR_VERB] [OBJECT].",
            "slots": "HORTATIVE,HONOR_VERB,OBJECT",
            "evidence_status": "requires_register_review",
            "review_note": "Reserved for MSN_public/MSN_poetic devotional pack; do not use as neutral prose without review.",
        },
    ]


def genre_plan() -> list[dict[str, str]]:
    return [
        {
            "genre_id": "GENRE-001",
            "book_type": "children_book",
            "recommended_register": "MSN_neutral with limited EHN dialogue",
            "difficulty": "lowest",
            "best_first": "yes",
            "required_next_pack": "children_core_vocab_and_caption_patterns",
            "notes": "Best proof of system: short sentences, repetition, primer-safe vocabulary.",
        },
        {
            "genre_id": "GENRE-002",
            "book_type": "cookbook",
            "recommended_register": "MSN_neutral",
            "difficulty": "medium",
            "best_first": "possible",
            "required_next_pack": "food_tools_measurements_sequence_policy",
            "notes": "Needs loanword and measurement policy for modern kitchen terms.",
        },
        {
            "genre_id": "GENRE-003",
            "book_type": "mindfulness_chapbook",
            "recommended_register": "MSN_neutral or MSN_public",
            "difficulty": "medium_high",
            "best_first": "after_children_or_food",
            "required_next_pack": "body_breath_heart_attention_vocabulary",
            "notes": "Needs abstract vocabulary controls and careful tone decisions.",
        },
        {
            "genre_id": "GENRE-004",
            "book_type": "tloque_nahuaque_devotional",
            "recommended_register": "MSN_public and MSN_poetic",
            "difficulty": "highest",
            "best_first": "no",
            "required_next_pack": "devotional_msn_p_source_and_theology_pack",
            "notes": "Requires classical citation policy, divine-name policy, and explicit register annotation.",
        },
    ]


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, str]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    count = 0
    try:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in materialized:
                writer.writerow(row)
                count += 1
    except PermissionError:
        if not path.exists():
            raise
        # On Windows, CSVs may be locked by spreadsheet previews. Keep the
        # existing export so the rest of the package can still be generated.
        return len(materialized)
    return count


def distribution(rows: Iterable[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = clean(row.get(field)) or "(blank)"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def main() -> None:
    conn = connect()
    quick_check = conn.execute("PRAGMA quick_check").fetchone()[0]
    core = build_core_candidates(conn)
    conn.close()

    authoring = build_authoring_seed(core)
    approval_seed = build_approval_seed(core)
    patterns = sentence_patterns()
    genres = genre_plan()

    core_count = write_csv(EXPORT_DIR / "msn_core_candidates.csv", CORE_FIELDS, core)
    authoring_count = write_csv(EXPORT_DIR / "msn_authoring_lexicon_seed.csv", AUTHORING_FIELDS, authoring)
    approval_seed_count = write_csv(EXPORT_DIR / "approved_msn_core_seed.csv", APPROVAL_SEED_FIELDS, approval_seed)
    pattern_count = write_csv(EXPORT_DIR / "msn_sentence_patterns.csv", PATTERN_FIELDS, patterns)
    genre_count = write_csv(EXPORT_DIR / "msn_genre_seed_plan.csv", GENRE_FIELDS, genres)

    summary = {
        "database": str(DB_PATH.relative_to(ROOT)),
        "quick_check": quick_check,
        "outputs": {
            "msn_core_candidates.csv": core_count,
            "msn_authoring_lexicon_seed.csv": authoring_count,
            "approved_msn_core_seed.csv": approval_seed_count,
            "msn_sentence_patterns.csv": pattern_count,
            "msn_genre_seed_plan.csv": genre_count,
        },
        "core_by_priority": distribution(core, "review_priority"),
        "core_by_status": distribution(core, "msn_use_status"),
        "core_by_pos": distribution(core, "part_of_speech"),
        "authoring_by_domain": distribution(authoring, "authoring_domain"),
        "genre_recommendation": "Start with GENRE-001 children_book unless user chooses otherwise.",
        "notes": [
            "This does not speaker-validate or publicly approve entries.",
            "Proposed MSN headwords prefer orthography/ehn_to_msn_candidates.csv when available.",
        ],
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with (REPORT_DIR / "msn_authoring_pack_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
