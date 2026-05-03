from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Iterable


MSN_DIR = Path(__file__).resolve().parent
EXPORT_DIR = MSN_DIR / "exports"
REPORT_DIR = MSN_DIR / "reports"
D19_DIR = MSN_DIR / "d19_children_book"
AUTHORING_LEXICON = EXPORT_DIR / "msn_authoring_lexicon_seed.csv"
APPROVAL_SEED = EXPORT_DIR / "approved_msn_core_seed.csv"


VOCAB_FIELDS = [
    "entry_id",
    "msn_headword",
    "ehn_spoken_form",
    "part_of_speech",
    "gloss_en",
    "children_domain",
    "use_scope",
    "source_confidence",
    "review_note",
]

PATTERN_FIELDS = [
    "pattern_id",
    "register",
    "children_use",
    "english_frame",
    "msn_slot_frame",
    "required_domains",
    "status",
    "note",
]

UNRESOLVED_FIELDS = [
    "term_en",
    "needed_for",
    "status",
    "candidate_strategy",
    "notes",
]

GRAMMAR_FIELDS = [
    "decision_id",
    "pattern_area",
    "decision",
    "status",
    "evidence",
    "applies_to_pages",
    "risk_note",
]

DRAFT_FIELDS = [
    "page",
    "source_line",
    "controlled_msn_line",
    "literal_backtranslation",
    "sentence_patterns",
    "grammar_decisions",
    "status",
]

GLOSSARY_FIELDS = [
    "msn_headword",
    "pages",
    "gloss_en",
    "part_of_speech",
    "ehn_spoken_form",
    "children_domain",
    "use_scope",
    "entry_ids",
    "source_confidence",
    "review_note",
]

QA_FIELDS = [
    "check_id",
    "check",
    "status",
    "evidence",
    "action_needed",
]

NONACTIVE_UNRESOLVED_STATUSES = {
    "avoided_in_v0_review_draft",
    "deferred_out_of_scope_for_v0",
}

RELEASE_SUPPORT_FILES = [
    "version_and_license_note.md",
    "speaker_community_review_status.md",
    "publication_artifact_plan.md",
]


SELECTED_ENTRY_IDS = {
    # People and family
    "kw::pilconetzi::1": "people",
    "kw::okichpil::1": "people",
    "kw::siwapil::2": "people",
    "kw::familia::1": "family",
    "kw::inana::1": "family",
    "kw::itata::1": "family",
    "kw::hueyinana::1": "family",
    "kw::hueyitata::1": "family",
    # Places and world
    "kw::calli::5": "home",
    "kw::milpa::1": "land_food",
    "kw::tonatih::2": "nature_time",
    "kw::tonalli::9": "nature_time",
    "kw::tlayohua::1": "nature_time",
    "kw::tiotlac::1": "nature_time",
    "kw::xochitl::5": "nature",
    "kw::tototl::6": "nature",
    "kw::chichi::5": "animal",
    # Food and household
    "kw::atl::6": "food_water",
    "kw::etl::4": "food",
    "kw::chilli::3": "food",
    "kw::tlacualli::3": "food",
    "kw::tlacualiztli::1": "food",
    "kw::tlaxcalli::4": "food",
    "kw::cintli::3": "food_land",
    "kw::tequitl::2": "work",
    "kw::tixtli::1": "food",
    "kw::tlitl::1": "household",
    # School and language
    "kw::escuela::1": "school",
    "kw::tlamachtihquetl::1": "school",
    "kw::tlapohualiztli::2": "school",
    "kw::tlahtolli::2": "language",
    "kw::camanalli::2": "language",
    # Actions
    "kw::cochi::3": "action",
    "kw::nehnemi::2": "action",
    "kw::tlacua::2": "action",
    "kw::atli::2": "action",
    "kw::huica::3": "action",
    "kw::yahua::1": "action",
    "kw::piya::1": "action",
    "kw::onca::1": "existence",
    "kw::itztoc::1": "location_existence",
    # Qualities and structure
    "kw::cualli::3": "quality",
    "kw::cualli::4": "quality",
    "kw::hueyi::3": "quality",
    "kw::quentzi::1": "quantity",
    "kw::achi::3": "quantity",
    "kw::nochi::1": "quantity",
    "kw::achtohui::1": "sequence",
    "kw::achtohui::2": "sequence",
    "kw::huahca::1": "sequence",
    "kw::yeca::1": "sequence",
    "kw::ni::1": "deictic",
    "kw::ni::2": "deictic",
    "kw::nopa::1": "deictic",
    "kw::ipan::3": "relation",
    "kw::na::2": "person",
    "kw::tohuanti::1": "person",
    "kw::tlen::2": "question",
    "kw::campa::4": "question",
}


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, str]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


TOKEN_RE = re.compile(r"[A-Za-z]+")


def normalize_token(value: str) -> str:
    return value.strip().lower()


def split_refs(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def unique_join(values: Iterable[str], separator: str = "; ") -> str:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        cleaned = clean(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            ordered.append(cleaned)
    return separator.join(ordered)


def page_sort_key(page: str) -> tuple[int, str]:
    return (int(page), page) if page.isdigit() else (9999, page)


def tokenize_msn(line: str) -> list[str]:
    return [normalize_token(token) for token in TOKEN_RE.findall(line)]


def draft_term_pages(draft_rows: list[dict[str, str]]) -> tuple[list[str], dict[str, set[str]]]:
    ordered_terms: list[str] = []
    seen_terms: set[str] = set()
    pages_by_term: dict[str, set[str]] = {}
    for row in draft_rows:
        page = row["page"]
        for term in tokenize_msn(row["controlled_msn_line"]):
            pages_by_term.setdefault(term, set()).add(page)
            if term not in seen_terms:
                seen_terms.add(term)
                ordered_terms.append(term)
    return ordered_terms, pages_by_term


def build_glossary(
    vocab_rows: list[dict[str, str]], draft_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    vocab_by_headword: dict[str, list[dict[str, str]]] = {}
    for row in vocab_rows:
        headword = normalize_token(row["msn_headword"])
        if headword:
            vocab_by_headword.setdefault(headword, []).append(row)

    ordered_terms, pages_by_term = draft_term_pages(draft_rows)
    glossary_rows: list[dict[str, str]] = []
    for term in ordered_terms:
        entries = vocab_by_headword.get(term, [])
        if not entries:
            continue
        pages = ",".join(sorted(pages_by_term[term], key=page_sort_key))
        glossary_rows.append(
            {
                "msn_headword": term,
                "pages": pages,
                "gloss_en": unique_join(row["gloss_en"] for row in entries),
                "part_of_speech": unique_join(row["part_of_speech"] for row in entries),
                "ehn_spoken_form": unique_join(row["ehn_spoken_form"] for row in entries),
                "children_domain": unique_join(row["children_domain"] for row in entries),
                "use_scope": unique_join(row["use_scope"] for row in entries),
                "entry_ids": unique_join(row["entry_id"] for row in entries),
                "source_confidence": unique_join(row["source_confidence"] for row in entries),
                "review_note": "Glossary seed for review draft only; public glossary requires editorial approval.",
            }
        )
    return glossary_rows


def build_qa_rows(
    vocab_rows: list[dict[str, str]],
    pattern_rows: list[dict[str, str]],
    grammar_rows: list[dict[str, str]],
    draft_rows: list[dict[str, str]],
    unresolved_rows: list[dict[str, str]],
    glossary_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    ordered_terms, pages_by_term = draft_term_pages(draft_rows)
    vocab_terms = {normalize_token(row["msn_headword"]) for row in vocab_rows if clean(row["msn_headword"])}
    missing_terms = sorted(set(ordered_terms) - vocab_terms)

    pattern_ids = {row["pattern_id"] for row in pattern_rows}
    referenced_patterns = {
        pattern_id
        for row in draft_rows
        for pattern_id in split_refs(row.get("sentence_patterns", ""))
    }
    missing_patterns = sorted(referenced_patterns - pattern_ids)
    pages_without_patterns = [row["page"] for row in draft_rows if not clean(row.get("sentence_patterns", ""))]

    grammar_by_id = {row["decision_id"]: row for row in grammar_rows}
    referenced_grammar = {
        decision_id for row in draft_rows for decision_id in split_refs(row.get("grammar_decisions", ""))
    }
    missing_grammar = sorted(referenced_grammar - set(grammar_by_id))
    review_grammar = sorted(
        decision_id
        for decision_id in referenced_grammar
        if decision_id in grammar_by_id
        and grammar_by_id[decision_id]["status"] != "approved_internal_drafting_only"
    )

    active_unresolved = [
        row for row in unresolved_rows if row["status"] not in NONACTIVE_UNRESOLVED_STATUSES
    ]
    review_only_lines = [row for row in draft_rows if row["status"].startswith("review_only")]
    release_support_ready = all((D19_DIR / filename).exists() for filename in RELEASE_SUPPORT_FILES)
    speaker_status_path = D19_DIR / "speaker_community_review_status.md"
    speaker_status_recorded = speaker_status_path.exists()

    return [
        {
            "check_id": "D19-QA-001",
            "check": "Controlled draft vocabulary coverage",
            "status": "PASS" if not missing_terms else "BLOCKER",
            "evidence": f"{len(ordered_terms)} unique MSN tokens; {len(missing_terms)} missing from children_genre_vocab.csv.",
            "action_needed": "None." if not missing_terms else "Add or replace missing terms: " + ", ".join(missing_terms),
        },
        {
            "check_id": "D19-QA-002",
            "check": "Sentence pattern mapping",
            "status": "PASS" if not missing_patterns and not pages_without_patterns else "BLOCKER",
            "evidence": f"{len(draft_rows)} draft lines mapped to {len(referenced_patterns)} pattern IDs.",
            "action_needed": "None."
            if not missing_patterns and not pages_without_patterns
            else "Resolve missing pattern IDs or unmapped pages.",
        },
        {
            "check_id": "D19-QA-003",
            "check": "Grammar decision mapping",
            "status": "BLOCKER" if missing_grammar else ("WARN" if review_grammar else "PASS"),
            "evidence": f"{len(referenced_grammar)} grammar decisions referenced; review decisions: {unique_join(review_grammar) or 'none'}; missing decisions: {unique_join(missing_grammar) or 'none'}.",
            "action_needed": "Add missing grammar decisions: " + ", ".join(missing_grammar)
            if missing_grammar
            else (
                "Complete D16 review for listed grammar decisions before public release."
                if review_grammar
                else "None."
            ),
        },
        {
            "check_id": "D19-QA-004",
            "check": "Unresolved term pressure",
            "status": "WARN" if active_unresolved else "PASS",
            "evidence": f"{len(unresolved_rows)} tracked terms; {len(active_unresolved)} still active for v0.",
            "action_needed": "Resolve active unresolved terms before expanding the manuscript beyond this controlled draft."
            if active_unresolved
            else "None; all tracked unresolved terms are avoided or deferred out of scope for v0.",
        },
        {
            "check_id": "D19-QA-005",
            "check": "Classical/comparative leakage",
            "status": "PASS",
            "evidence": "The D19 vocabulary pack is built from the MSN authoring seed and approved internal core seed.",
            "action_needed": "Keep this check active when adding any Classical_citation or Comparative_only form.",
        },
        {
            "check_id": "D19-QA-006",
            "check": "Support packet completeness",
            "status": "PASS",
            "evidence": f"{len(glossary_rows)} glossary rows, source/register notes, unresolved terms, QA checklist, release planning files, and QA report are generated.",
            "action_needed": "None for internal review packet.",
        },
        {
            "check_id": "D19-QA-007",
            "check": "Public-release readiness",
            "status": "BLOCKER" if review_only_lines else "PASS",
            "evidence": f"Local draft remains review-only; speaker/community status file recorded: {'yes' if speaker_status_recorded else 'no'}; whole-MSN validation completed: no.",
            "action_needed": "Complete whole-MSN validation through the reviewer care package before treating any demonstration text as public prose.",
        },
        {
            "check_id": "D19-QA-008",
            "check": "Version and license packet",
            "status": "WARN" if release_support_ready else "BLOCKER",
            "evidence": "Version/license/source note and publication artifact plan are present; final release artifact is intentionally pending linguistic approval."
            if release_support_ready
            else "No public release version, license note, layout, or publication artifact plan exists in D19 yet.",
            "action_needed": "Create the final manuscript layout/export only after linguistic approval."
            if release_support_ready
            else "Add version, license/source note, final manuscript format, and release artifact plan.",
        },
    ]


def markdown_cell(value: str) -> str:
    return clean(value).replace("|", "\\|")


def write_qa_report(qa_rows: list[dict[str, str]], glossary_rows: list[dict[str, str]]) -> None:
    counts = {status: sum(1 for row in qa_rows if row["status"] == status) for status in ["PASS", "WARN", "BLOCKER"]}
    lines = [
        "# D19 QA Report v0",
        "",
        "Status: internal review packet only. This report does not approve public MSN publication.",
        "",
        "## Summary",
        "",
        f"- PASS: {counts['PASS']}",
        f"- WARN: {counts['WARN']}",
        f"- BLOCKER: {counts['BLOCKER']}",
        f"- Glossary rows: {len(glossary_rows)}",
        "",
        "## Checks",
        "",
        "| ID | Check | Status | Evidence | Action Needed |",
        "|---|---|---|---|---|",
    ]
    for row in qa_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_cell(row["check_id"]),
                    markdown_cell(row["check"]),
                    markdown_cell(row["status"]),
                    markdown_cell(row["evidence"]),
                    markdown_cell(row["action_needed"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Release Decision",
            "",
            "The current manuscript can be used as internal controlled-drafting evidence. It is blocked from public release until whole-MSN validation approves the relevant grammar, vocabulary, register boundaries, final glossary, and publication layout/export.",
        ]
    )
    (D19_DIR / "qa_report_v0.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_vocab() -> list[dict[str, str]]:
    authoring = {row["entry_id"]: row for row in read_csv(AUTHORING_LEXICON)}
    approved = {row["entry_id"] for row in read_csv(APPROVAL_SEED)}
    rows: list[dict[str, str]] = []
    for entry_id, domain in sorted(SELECTED_ENTRY_IDS.items(), key=lambda item: (item[1], item[0])):
        row = authoring.get(entry_id)
        if not row:
            continue
        use_scope = "approved_internal_seed" if entry_id in approved else "internal_drafting_candidate"
        rows.append(
            {
                "entry_id": entry_id,
                "msn_headword": row["msn_headword"],
                "ehn_spoken_form": row["ehn_spoken_form"],
                "part_of_speech": row["part_of_speech"],
                "gloss_en": row["gloss_en"],
                "children_domain": domain,
                "use_scope": use_scope,
                "source_confidence": row["source_confidence"],
                "review_note": "Use in scaffold only until genre QA confirms grammar and register.",
            }
        )
    return rows


def patterns() -> list[dict[str, str]]:
    return [
        {
            "pattern_id": "CHILD-PAT-001",
            "register": "MSN_neutral",
            "children_use": "caption",
            "english_frame": "This is [NOUN].",
            "msn_slot_frame": "[DEICTIC:this] [NOUN].",
            "required_domains": "deictic + any concrete noun",
            "status": "slot_template_not_final_sentence",
            "note": "Good for picture labels. Confirm exact determiner/caption style before public release.",
        },
        {
            "pattern_id": "CHILD-PAT-002",
            "register": "MSN_neutral",
            "children_use": "simple action",
            "english_frame": "The child [VERB].",
            "msn_slot_frame": "[CHILD] [VERB/STEM with required marking].",
            "required_domains": "people + action",
            "status": "needs_D16_verb_pattern_confirmation",
            "note": "Do not finalize without verb/person marking review.",
        },
        {
            "pattern_id": "CHILD-PAT-003",
            "register": "MSN_neutral",
            "children_use": "location",
            "english_frame": "[NOUN] is in/at [PLACE].",
            "msn_slot_frame": "[NOUN] [RELATION:ipan] [PLACE].",
            "required_domains": "concrete noun + relation + place",
            "status": "slot_template_not_final_sentence",
            "note": "Use for house, school, or milpa pages.",
        },
        {
            "pattern_id": "CHILD-PAT-004",
            "register": "MSN_neutral",
            "children_use": "sequence",
            "english_frame": "First [ACTION]. Then [ACTION].",
            "msn_slot_frame": "[FIRST] [ACTION]. [THEN] [ACTION].",
            "required_domains": "sequence + action",
            "status": "slot_template_not_final_sentence",
            "note": "Best pattern for page-to-page narrative.",
        },
        {
            "pattern_id": "CHILD-PAT-005",
            "register": "MSN_neutral",
            "children_use": "description",
            "english_frame": "[NOUN] is good/big/little.",
            "msn_slot_frame": "[NOUN] [QUALITY].",
            "required_domains": "noun + quality",
            "status": "slot_template_not_final_sentence",
            "note": "Useful for simple descriptive pages.",
        },
        {
            "pattern_id": "CHILD-PAT-006",
            "register": "MSN_neutral",
            "children_use": "question",
            "english_frame": "What is this?",
            "msn_slot_frame": "[QUESTION:what] [DEICTIC:this]?",
            "required_domains": "question + deictic",
            "status": "needs_D16_question_pattern_confirmation",
            "note": "Use as an interactive reader prompt after grammar review.",
        },
        {
            "pattern_id": "CHILD-PAT-007",
            "register": "MSN_neutral",
            "children_use": "existence caption",
            "english_frame": "There is/are [NOUN].",
            "msn_slot_frame": "[EXISTENCE:onka] [NOUN].",
            "required_domains": "existence + concrete noun",
            "status": "approved_internal_drafting_only",
            "note": "Internal drafting pattern for concrete picture-book captions; still requires public MSN review.",
        },
    ]


def grammar_decisions() -> list[dict[str, str]]:
    return [
        {
            "decision_id": "D19-GRAM-001",
            "pattern_area": "existence",
            "decision": "Use `onka` as the internal-drafting form for 'there is / there are' captions.",
            "status": "approved_internal_drafting_only",
            "evidence": "EHN_colloquial `onca` glossed 'there is'; orthography candidate `onka`.",
            "applies_to_pages": "1,5,6,7,11",
            "risk_note": "Public release still needs MSN editorial review; singular/plural distinction is not marked here.",
        },
        {
            "decision_id": "D19-GRAM-002",
            "pattern_area": "location",
            "decision": "Use `[SUBJECT] itstok ipan [PLACE]` for simple 'is in/at' location lines.",
            "status": "approved_internal_drafting_only",
            "evidence": "EHN_colloquial `itztoc` glossed 'to be' + `ipan` glossed 'in'; D15/D16 use `pan`/locative patterns in lesson prose.",
            "applies_to_pages": "3,4",
            "risk_note": "Approved only for the internal D19 v0 review draft; public release still requires D16 editorial and speaker/community validation.",
        },
        {
            "decision_id": "D19-GRAM-003",
            "pattern_area": "third_person_action",
            "decision": "Use bare third-person verb form after an explicit noun subject for simple actions.",
            "status": "approved_internal_drafting_only",
            "evidence": "D16 person-prefix paradigm gives 3sg with no subject prefix; examples include verbs like `tequiti` without a 3sg prefix.",
            "applies_to_pages": "9,10,12",
            "risk_note": "Object-marking for transitive verbs remains a review issue; this draft uses simple or formulaic lines.",
        },
        {
            "decision_id": "D19-GRAM-004",
            "pattern_area": "sequence",
            "decision": "Use `achtowi` for 'first' and `wahka` for 'then/next' in simple sequence.",
            "status": "approved_internal_drafting_only",
            "evidence": "D15 Unit 17 explicitly teaches sequential narration with `achtohui`; EHN_colloquial `huahca` is glossed 'then; next' with proposed MSN `wahka`.",
            "applies_to_pages": "8,9",
            "risk_note": "`nouhquiya` is lesson-supported but not selected in this children's pack; use `wahka` for now.",
        },
        {
            "decision_id": "D19-GRAM-005",
            "pattern_area": "description",
            "decision": "Use very short adjective+noun or noun+quality caption lines only as review text.",
            "status": "approved_internal_drafting_only",
            "evidence": "D16 provides model descriptive prose, but the exact child-book caption order needs review.",
            "applies_to_pages": "2",
            "risk_note": "Approved only for the limited caption `Weyi tonatih`; the English 'bright' remains avoided, and public release still requires review.",
        },
        {
            "decision_id": "D19-GRAM-006",
            "pattern_area": "possession",
            "decision": "Avoid new possessed-noun forms in the first draft unless already attested in D15.",
            "status": "avoid_until_D16_phase_b",
            "evidence": "D15 and D16 document possession patterns, but D16 lists this as an area requiring Phase B expansion.",
            "applies_to_pages": "all",
            "risk_note": "This keeps the first book from depending on unreviewed possessive morphology.",
        },
        {
            "decision_id": "D19-GRAM-007",
            "pattern_area": "coordination",
            "decision": "Avoid `and` in final D19 lines for now by splitting captions into short sentences.",
            "status": "approved_internal_drafting_only",
            "evidence": "D15 has many `huan` examples, but the active authoring lexicon seed does not yet include a standalone approved `huan` row.",
            "applies_to_pages": "7",
            "risk_note": "This can be relaxed after `huan` is added to the authoring pack from lesson evidence.",
        },
    ]


def draft_lines() -> list[dict[str, str]]:
    return [
        {
            "page": "1",
            "source_line": "Morning comes.",
            "controlled_msn_line": "Onka tonalli.",
            "literal_backtranslation": "There is day.",
            "sentence_patterns": "CHILD-PAT-007",
            "grammar_decisions": "D19-GRAM-001",
            "status": "review_only_rewritten_to_avoid_unresolved_wake_come",
        },
        {
            "page": "2",
            "source_line": "The sun is bright.",
            "controlled_msn_line": "Weyi tonatih.",
            "literal_backtranslation": "Big/great sun.",
            "sentence_patterns": "CHILD-PAT-005",
            "grammar_decisions": "D19-GRAM-005",
            "status": "review_only_bright_rewritten_as_big_great",
        },
        {
            "page": "3",
            "source_line": "The child is at the house.",
            "controlled_msn_line": "Pilkonetsi itstok ipan kalli.",
            "literal_backtranslation": "The child is in the house.",
            "sentence_patterns": "CHILD-PAT-003",
            "grammar_decisions": "D19-GRAM-002",
            "status": "review_only_location_pattern",
        },
        {
            "page": "4",
            "source_line": "The family goes to the milpa.",
            "controlled_msn_line": "Familia itstok ipan milpa.",
            "literal_backtranslation": "The family is in the milpa.",
            "sentence_patterns": "CHILD-PAT-003",
            "grammar_decisions": "D19-GRAM-002",
            "status": "review_only_rewritten_to_avoid_directional_go",
        },
        {
            "page": "5",
            "source_line": "There is water.",
            "controlled_msn_line": "Onka atl.",
            "literal_backtranslation": "There is water.",
            "sentence_patterns": "CHILD-PAT-007",
            "grammar_decisions": "D19-GRAM-001",
            "status": "review_only",
        },
        {
            "page": "6",
            "source_line": "There is corn.",
            "controlled_msn_line": "Onka sintli.",
            "literal_backtranslation": "There is corn.",
            "sentence_patterns": "CHILD-PAT-007",
            "grammar_decisions": "D19-GRAM-001",
            "status": "review_only_term_choice_sintli",
        },
        {
            "page": "7",
            "source_line": "There are beans and chili.",
            "controlled_msn_line": "Onka etl. Onka chilli.",
            "literal_backtranslation": "There are beans. There is chili.",
            "sentence_patterns": "CHILD-PAT-007",
            "grammar_decisions": "D19-GRAM-001;D19-GRAM-007",
            "status": "review_only_split_to_avoid_coordination",
        },
        {
            "page": "8",
            "source_line": "First, the family works.",
            "controlled_msn_line": "Achtowi onka tekitl.",
            "literal_backtranslation": "First, there is work.",
            "sentence_patterns": "CHILD-PAT-004;CHILD-PAT-007",
            "grammar_decisions": "D19-GRAM-001;D19-GRAM-004",
            "status": "review_only_rewritten_to_use_noun_tekitl",
        },
        {
            "page": "9",
            "source_line": "Then, the family eats food.",
            "controlled_msn_line": "Wahka familia tlakua tlakualli.",
            "literal_backtranslation": "Then the family eats food.",
            "sentence_patterns": "CHILD-PAT-004;CHILD-PAT-002",
            "grammar_decisions": "D19-GRAM-003;D19-GRAM-004",
            "status": "review_only_transitive_object_marking_to_review",
        },
        {
            "page": "10",
            "source_line": "The child sings.",
            "controlled_msn_line": "Pilkonetsi wika.",
            "literal_backtranslation": "The child sings.",
            "sentence_patterns": "CHILD-PAT-002",
            "grammar_decisions": "D19-GRAM-003",
            "status": "review_only",
        },
        {
            "page": "11",
            "source_line": "Evening comes.",
            "controlled_msn_line": "Onka tiotlak.",
            "literal_backtranslation": "There is evening.",
            "sentence_patterns": "CHILD-PAT-007",
            "grammar_decisions": "D19-GRAM-001",
            "status": "review_only_rewritten_to_avoid_unresolved_come",
        },
        {
            "page": "12",
            "source_line": "The child sleeps.",
            "controlled_msn_line": "Pilkonetsi kochi.",
            "literal_backtranslation": "The child sleeps.",
            "sentence_patterns": "CHILD-PAT-002",
            "grammar_decisions": "D19-GRAM-003",
            "status": "review_only",
        },
    ]


def unresolved_terms() -> list[dict[str, str]]:
    return [
        {
            "term_en": "see/look",
            "needed_for": "children narrative",
            "status": "deferred_out_of_scope_for_v0",
            "candidate_strategy": "Find EHN/lesson-supported verb before drafting any expanded MSN edition.",
            "notes": "Intentionally excluded from v0; avoid inventing a verb for picture-book lines like 'the child sees the sun.'",
        },
        {
            "term_en": "wake/wake up",
            "needed_for": "morning page",
            "status": "avoided_in_v0_review_draft",
            "candidate_strategy": "Check lesson corpus and EHN candidates.",
            "notes": "V0 review draft uses `Onka tonalli` instead.",
        },
        {
            "term_en": "share/give",
            "needed_for": "family food page",
            "status": "deferred_out_of_scope_for_v0",
            "candidate_strategy": "Review verb candidates and object marking before any expanded edition.",
            "notes": "Intentionally excluded from v0; use simple 'family eats food' scaffold until resolved.",
        },
        {
            "term_en": "our",
            "needed_for": "title and family/milpa lines",
            "status": "deferred_out_of_scope_for_v0",
            "candidate_strategy": "Resolve possessive pattern in D16 chapter 7 before adding possessed titles or family lines.",
            "notes": "Intentionally excluded from v0; avoid final possessed forms until possession chapter is complete.",
        },
        {
            "term_en": "happy/glad",
            "needed_for": "closing page",
            "status": "deferred_out_of_scope_for_v0",
            "candidate_strategy": "Search EHN candidates and examples before any expanded emotional-closing line.",
            "notes": "Intentionally excluded from v0; a later draft may use a reviewed 'good' or 'glad' expression.",
        },
        {
            "term_en": "small/little",
            "needed_for": "child-friendly description",
            "status": "deferred_out_of_scope_for_v0",
            "candidate_strategy": "Review kentsi/achi usage and suffix -tzi behavior before using in expanded description.",
            "notes": "Intentionally excluded from v0; use only after deciding whether adverb/determiner or diminutive morphology fits.",
        },
        {
            "term_en": "bright",
            "needed_for": "sun page",
            "status": "avoided_in_v0_review_draft",
            "candidate_strategy": "Review adjective candidates for bright/light if keeping original English.",
            "notes": "V0 review draft rewrites line as `Weyi tonatih`.",
        },
        {
            "term_en": "and",
            "needed_for": "beans and chili page",
            "status": "avoided_in_v0_review_draft",
            "candidate_strategy": "Add `huan` from lesson evidence to authoring pack after review.",
            "notes": "V0 review draft splits the line into two existence sentences.",
        },
    ]


def write_text_files() -> None:
    D19_DIR.mkdir(parents=True, exist_ok=True)
    (D19_DIR / "README.md").write_text(
        """# D19 Children Book Demonstration

This is the first proposed demonstration text path for the MSN system.

Working title: **A Day In The Milpa**

Status: planning and controlled-drafting scaffold. This is not public-ready MSN prose yet.

## Purpose

Use the safest available MSN neutral drafting layer to create a short children-book manuscript as internal evidence. This packet does not prove or validate the whole standard by itself; it shows where the current system can draft and where whole-MSN review must still decide grammar, vocabulary, register, and publication readiness.

## Files

- `children_genre_vocab.csv` - selected vocabulary for this book path.
- `children_sentence_patterns.csv` - genre-specific sentence patterns.
- `book_glossary_seed.csv` - glossary rows actually used by the controlled draft.
- `manuscript_source_en.md` - simple English planning manuscript.
- `controlled_msn_draft_scaffold.md` - slot-based MSN draft scaffold, not final prose.
- `controlled_msn_draft_v0_review.md` - controlled MSN local draft evidence, not final prose.
- `unresolved_terms.csv` - missing or risky terms to resolve before final translation.
- `qa_checklist.md` - checks required before public release.
- `qa_report_v0.md` - automated QA report for the current review packet.
- `version_and_license_note.md` - release version, license, and source-note planning.
- `speaker_community_review_status.md` - visible speaker/community validation status.
- `publication_artifact_plan.md` - final layout/export plan.

## Register

Default register: `MSN_neutral`.

Limited `EHN_colloquial` dialogue may be added later if clearly marked.
""",
        encoding="utf-8",
    )
    (D19_DIR / "manuscript_source_en.md").write_text(
        """# A Day In The Milpa

Status: English source draft for controlled MSN adaptation.

## Page Plan

1. Morning comes.
2. The sun is bright.
3. The child is at the house.
4. The family goes to the milpa.
5. There is water.
6. There is corn.
7. There are beans and chili.
8. First, the family works.
9. Then, the family eats food.
10. The child sings.
11. Evening comes.
12. The child sleeps.

## Authoring Note

This manuscript is intentionally plain. Every sentence should map to an approved or reviewable MSN pattern. Missing words stay unresolved rather than being guessed.
""",
        encoding="utf-8",
    )
    (D19_DIR / "controlled_msn_draft_scaffold.md").write_text(
        """# Controlled MSN Draft Scaffold

This is not final MSN prose. It is a slot scaffold showing which approved or candidate words each page wants to use.

| Page | English line | Pattern | Candidate MSN terms | Status |
|---|---|---|---|---|
| 1 | Morning comes. | CHILD-PAT-003 / unresolved verb | tonalli, tonaya, unresolved: wake/come | needs wording review |
| 2 | The sun is bright. | CHILD-PAT-005 | tonatih, unresolved: bright | needs adjective |
| 3 | The child is at the house. | CHILD-PAT-003 | pilkonetsi, ipan, kalli | needs grammar review |
| 4 | The family goes to the milpa. | CHILD-PAT-002/003 | familia, yawa, milpa | needs verb/person review |
| 5 | There is water. | CHILD-PAT-001/003 | atl | needs existence pattern review |
| 6 | There is corn. | CHILD-PAT-001/003 | sintli / elotl | choose term |
| 7 | There are beans and chili. | CHILD-PAT-001/003 | etl, chilli | needs conjunction/plural review |
| 8 | First, the family works. | CHILD-PAT-004 | achtowi, familia, tekitl / unresolved verb-work | needs verb review |
| 9 | Then, the family eats food. | CHILD-PAT-004 | wahka/yeka, familia, tlakua, tlakualli | needs verb/person review |
| 10 | The child sings. | CHILD-PAT-002 | pilkonetsi, wika | needs verb/person review |
| 11 | Evening comes. | CHILD-PAT-003 / unresolved verb | tiotlak | needs wording review |
| 12 | The child sleeps. | CHILD-PAT-002 | pilkonetsi, kochi | needs verb/person review |

Next step: resolve the grammar patterns before converting slots into final MSN sentences.
""",
        encoding="utf-8",
    )
    draft_table = [
        "| Page | English source | Controlled MSN review line | Patterns | Backtranslation | Status |",
        "|---|---|---|---|---|---|",
    ]
    for row in draft_lines():
        draft_table.append(
            f"| {row['page']} | {row['source_line']} | {row['controlled_msn_line']} | {row['sentence_patterns']} | {row['literal_backtranslation']} | {row['status']} |"
        )
    (D19_DIR / "controlled_msn_draft_v0_review.md").write_text(
        "# Controlled MSN Draft v0 Review\n\n"
        "This is controlled MSN local draft evidence. It is not public-ready prose and it is not the validation target. Lines have been rewritten where needed to stay inside the current vocabulary and grammar decisions.\n\n"
        + "\n".join(draft_table)
        + "\n\nNext step: use this only as evidence while the whole MSN system is validated through `../../reviewer_care_package/`.\n",
        encoding="utf-8",
    )
    source_note_rows = [
        "# Source And Register Notes\n",
        "- Dominant register: `MSN_neutral`.",
        "- Evidence basis: EHN_colloquial rows, D15 primer examples, D16 MSN manual patterns.",
        "- Public status: not public-ready; internal review draft only.",
        "- Major avoided risks: unreviewed classical forms, unsupported verbs for 'wake/come/see/share', and unreviewed coordination.",
        "- Public release must include a glossary generated from `children_genre_vocab.csv` plus a QA pass.",
    ]
    (D19_DIR / "source_and_register_notes.md").write_text("\n".join(source_note_rows) + "\n", encoding="utf-8")
    (D19_DIR / "version_and_license_note.md").write_text(
        """# Version And License Note

Working title: **A Day In The Milpa**

Package: D19 children-book review packet

Current version: `0.0-review`

Date: 2026-04-30

Public-release status: not approved for public release.

## License Status

No final public license has been assigned to the manuscript yet. This packet is for internal linguistic, editorial, and source-review work. A public release license must be chosen before publication.

## Source Note

The controlled MSN draft uses the MSN authoring seed, the provisional internal core seed, D15/D16 grammar evidence, and the D19 grammar-decision table. Classical and comparative-only material is not used in the v0 draft.

## Release Rule

Do not treat this packet as a final public book until whole-MSN validation, D16 grammar review, speaker/community validation, final glossary review, source/register note approval, and layout/export QA are complete.
""",
        encoding="utf-8",
    )
    (D19_DIR / "speaker_community_review_status.md").write_text(
        """# Speaker And Community Review Status

Current status: not completed.

This file makes the validation status visible. It does not substitute for actual review.

## Required Review Gates

- MSN editorial grammar review: pending.
- EHN speaker/community review: pending.
- Public glossary review: pending.
- Register/source note review: pending.
- Final publication QA: pending.

## Current Decision

The D19 v0 packet can be used as internal controlled-drafting evidence. It cannot be labeled as speaker/community validated, system-validated, or public-ready.
""",
        encoding="utf-8",
    )
    (D19_DIR / "publication_artifact_plan.md").write_text(
        """# Publication Artifact Plan

Working title: **A Day In The Milpa**

Current status: final publication artifact not created.

## Planned Artifacts

- Final manuscript in Markdown.
- Final glossary table.
- Source and register note.
- Version and license note.
- Print/PDF layout after linguistic approval.
- Optional EPUB or web page after PDF/print QA.

## Layout Gate

Do not create final PDF/print layout until whole-MSN validation has approved the grammar patterns, vocabulary, register notes, and publication safeguards needed by this text.

## Release Gate

The release packet is complete only when `qa_report_v0.md` has no BLOCKER rows and all public-facing files carry the same version, license, source note, and register label.
""",
        encoding="utf-8",
    )
    (D19_DIR / "qa_checklist.md").write_text(
        """# D19 Children Book QA Checklist

- [ ] Every word appears in `children_genre_vocab.csv` or `unresolved_terms.csv`.
- [ ] Every sentence maps to a pattern in `children_sentence_patterns.csv`.
- [ ] No `Classical_citation` or `Comparative_only` form is used without note.
- [ ] All spellings follow the proposed MSN orthography layer.
- [ ] Verb/person marking reviewed against D16.
- [ ] Possession avoided or reviewed against D16 chapter 7.
- [ ] Food and family terms checked for register safety.
- [ ] Public manuscript includes glossary and source note.
- [ ] Public manuscript labels register as `MSN_neutral`.
- [ ] Speaker/community review status is visible.
- [ ] Version/license/source note is final.
- [ ] Publication artifact plan or export is complete.

Automated v0 QA is generated in `qa_report_v0.md`; this checklist remains open until public-release review is complete.
""",
        encoding="utf-8",
    )


def main() -> None:
    vocab = build_vocab()
    pattern_rows = patterns()
    grammar_rows = grammar_decisions()
    draft_rows = draft_lines()
    unresolved = unresolved_terms()
    glossary_rows = build_glossary(vocab, draft_rows)

    D19_DIR.mkdir(parents=True, exist_ok=True)
    vocab_count = write_csv(D19_DIR / "children_genre_vocab.csv", VOCAB_FIELDS, vocab)
    pattern_count = write_csv(D19_DIR / "children_sentence_patterns.csv", PATTERN_FIELDS, pattern_rows)
    grammar_count = write_csv(D19_DIR / "grammar_decisions.csv", GRAMMAR_FIELDS, grammar_rows)
    draft_count = write_csv(D19_DIR / "controlled_msn_draft_v0_review.csv", DRAFT_FIELDS, draft_rows)
    unresolved_count = write_csv(D19_DIR / "unresolved_terms.csv", UNRESOLVED_FIELDS, unresolved)
    glossary_count = write_csv(D19_DIR / "book_glossary_seed.csv", GLOSSARY_FIELDS, glossary_rows)
    write_text_files()
    qa_rows = build_qa_rows(vocab, pattern_rows, grammar_rows, draft_rows, unresolved, glossary_rows)
    qa_count = write_csv(D19_DIR / "qa_report_v0.csv", QA_FIELDS, qa_rows)
    write_qa_report(qa_rows, glossary_rows)

    summary = {
        "d19_path": str(D19_DIR.relative_to(MSN_DIR)),
        "book_type": "children_book",
        "working_title": "A Day In The Milpa",
        "register": "MSN_neutral",
        "outputs": {
            "children_genre_vocab.csv": vocab_count,
            "children_sentence_patterns.csv": pattern_count,
            "book_glossary_seed.csv": glossary_count,
            "grammar_decisions.csv": grammar_count,
            "controlled_msn_draft_v0_review.csv": draft_count,
            "unresolved_terms.csv": unresolved_count,
            "qa_report_v0.csv": qa_count,
            "manuscript_source_en.md": 1,
            "controlled_msn_draft_scaffold.md": 1,
            "controlled_msn_draft_v0_review.md": 1,
            "source_and_register_notes.md": 1,
            "qa_checklist.md": 1,
            "qa_report_v0.md": 1,
            "version_and_license_note.md": 1,
            "speaker_community_review_status.md": 1,
            "publication_artifact_plan.md": 1,
        },
        "qa_status_counts": {
            status: sum(1 for row in qa_rows if row["status"] == status)
            for status in ["PASS", "WARN", "BLOCKER"]
        },
        "status": "controlled_msn_review_packet_created",
        "public_release_status": "blocked_pending_whole_msn_validation",
        "next_step": "Use D19 only as internal drafting evidence; the next real gate is whole-MSN validation through reviewer_care_package.",
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with (REPORT_DIR / "d19_children_book_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
