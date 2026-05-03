from __future__ import annotations

import csv
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MSN_DIR = Path(__file__).resolve().parent
DB_PATH = ROOT / "curriculum" / "fcn_master_lexicon_phase8_6_primer.sqlite"
EXPORT_DIR = MSN_DIR / "exports"
REPORT_DIR = MSN_DIR / "reports"
GRAMMAR_EXAMPLE_BANK = ROOT / "poetic_register" / "grammar_example_bank.csv"
E_TO_MSN_EXAMPLES = ROOT / "register_conversion" / "ehn_to_msn_neutral_examples.csv"


INVENTORY_FIELDS = [
    "entry_id",
    "msn_headword",
    "ehn_spoken_form",
    "classical_citation_form",
    "msn_poetic_form",
    "part_of_speech",
    "register",
    "variety",
    "gloss_en",
    "gloss_es",
    "root_family",
    "root_family_code",
    "source_id",
    "source_file",
    "source_reference",
    "source_type",
    "upstream_title",
    "authority_domain",
    "canonical_status",
    "source_confidence",
    "speaker_validation_status",
    "editorial_status",
    "msn_review_status",
    "msn_decision_basis",
    "msn_notes",
]

REVIEW_FIELDS = [
    "review_id",
    "entry_id",
    "queue_reason",
    "priority",
    "proposed_msn_headword",
    "current_register",
    "current_variety",
    "evidence_summary",
    "recommended_action",
    "source_id",
    "source_file",
    "source_reference",
    "source_confidence",
    "editorial_status",
    "speaker_validation_status",
]

EXAMPLE_FIELDS = [
    "example_id",
    "source_family",
    "source_register",
    "target_register",
    "nahuatl_text",
    "morpheme_segmentation",
    "gloss_line",
    "translation_en",
    "translation_es",
    "operation",
    "evidence_status",
    "source_reference",
    "editorial_note",
]


@dataclass(frozen=True)
class ReviewDecision:
    status: str
    reason: str
    priority: str
    action: str


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def review_decision(row: sqlite3.Row) -> ReviewDecision:
    msn = clean(row["msn_headword"])
    register = clean(row["register"])
    editorial_status = clean(row["editorial_status"])
    speaker_status = clean(row["speaker_validation_status"])
    confidence = row["source_confidence"] if row["source_confidence"] is not None else 0

    reasons: list[str] = []
    priority = "P3"
    action = "Review source evidence and keep current register label until approved."

    if not msn:
        reasons.append("missing_msn_headword")
        priority = "P1"
        action = "Propose an MSN headword only after source-backed normalization."

    if register == "Classical_citation":
        reasons.append("classical_citation_not_active_msn")
        if priority != "P1":
            priority = "P2"
        action = "Keep as citation or note-only unless explicitly approved for MSN neutral."

    if register == "Comparative_only":
        reasons.append("comparative_only")
        if priority == "P3":
            priority = "P2"
        action = "Compare against EHN and source hierarchy before promotion."

    if editorial_status.lower() == "flagged":
        reasons.append("editorial_flag")
        priority = "P1"
        action = "Resolve editorial flag before public MSN use."

    if speaker_status.lower() == "unreviewed":
        reasons.append("unreviewed")

    if confidence and float(confidence) < 0.75:
        reasons.append("low_source_confidence")
        if priority == "P3":
            priority = "P2"

    if not reasons:
        return ReviewDecision(
            status="candidate_ready_for_msn_review",
            reason="ready_candidate",
            priority="P4",
            action="Confirm and approve if register fit is clear.",
        )

    return ReviewDecision(
        status="needs_msn_review",
        reason=";".join(dict.fromkeys(reasons)),
        priority=priority,
        action=action,
    )


def inventory_rows(conn: sqlite3.Connection) -> list[dict[str, object]]:
    sql = """
        SELECT
            e.entry_id,
            e.msn_headword,
            e.ehn_spoken_form,
            e.classical_citation_form,
            e.msn_poetic_form,
            e.part_of_speech,
            e.register,
            e.variety,
            e.gloss_en,
            e.gloss_es,
            e.root_family,
            e.root_family_code,
            e.source_id,
            e.source_file,
            e.source_reference,
            s.source_type,
            s.upstream_title,
            s.authority_domain,
            s.canonical_status,
            e.source_confidence,
            e.speaker_validation_status,
            e.editorial_status,
            e.notes_internal,
            e.notes_public
        FROM lexicon_entries e
        LEFT JOIN sources s ON e.source_id = s.source_id
        WHERE e.is_active = 1
        ORDER BY
            CASE e.register
                WHEN 'EHN_colloquial' THEN 1
                WHEN 'Comparative_only' THEN 2
                WHEN 'Classical_citation' THEN 3
                ELSE 4
            END,
            lower(coalesce(e.msn_headword, e.ehn_spoken_form, e.classical_citation_form, e.entry_id)),
            e.entry_id
    """
    rows: list[dict[str, object]] = []
    for row in conn.execute(sql):
        decision = review_decision(row)
        notes = []
        if clean(row["notes_public"]):
            notes.append(clean(row["notes_public"]))
        if clean(row["notes_internal"]):
            notes.append(clean(row["notes_internal"]))
        rows.append(
            {
                "entry_id": row["entry_id"],
                "msn_headword": row["msn_headword"],
                "ehn_spoken_form": row["ehn_spoken_form"],
                "classical_citation_form": row["classical_citation_form"],
                "msn_poetic_form": row["msn_poetic_form"],
                "part_of_speech": row["part_of_speech"],
                "register": row["register"],
                "variety": row["variety"],
                "gloss_en": row["gloss_en"],
                "gloss_es": row["gloss_es"],
                "root_family": row["root_family"],
                "root_family_code": row["root_family_code"],
                "source_id": row["source_id"],
                "source_file": row["source_file"],
                "source_reference": row["source_reference"],
                "source_type": row["source_type"],
                "upstream_title": row["upstream_title"],
                "authority_domain": row["authority_domain"],
                "canonical_status": row["canonical_status"],
                "source_confidence": row["source_confidence"],
                "speaker_validation_status": row["speaker_validation_status"],
                "editorial_status": row["editorial_status"],
                "msn_review_status": decision.status,
                "msn_decision_basis": decision.reason,
                "msn_notes": " | ".join(notes),
            }
        )
    return rows


def review_rows(inventory: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in inventory:
        status = clean(row["msn_review_status"])
        if status != "needs_msn_review":
            continue
        reason = clean(row["msn_decision_basis"])
        priority = "P3"
        action = "Review source evidence and keep current register label until approved."
        if "missing_msn_headword" in reason or "editorial_flag" in reason:
            priority = "P1"
        elif "classical_citation" in reason or "comparative_only" in reason or "low_source_confidence" in reason:
            priority = "P2"
        if "missing_msn_headword" in reason:
            action = "Propose an MSN headword only after source-backed normalization."
        elif "classical_citation" in reason:
            action = "Keep as citation or note-only unless explicitly approved for MSN neutral."
        elif "comparative_only" in reason:
            action = "Compare against EHN and source hierarchy before promotion."
        elif "editorial_flag" in reason:
            action = "Resolve editorial flag before public MSN use."

        evidence = "; ".join(
            part
            for part in [
                f"register={clean(row['register'])}",
                f"variety={clean(row['variety'])}",
                f"source={clean(row['source_file'])}",
                f"confidence={clean(row['source_confidence'])}",
            ]
            if part
        )
        rows.append(
            {
                "review_id": f"MSN-REV-{len(rows) + 1:06d}",
                "entry_id": row["entry_id"],
                "queue_reason": reason,
                "priority": priority,
                "proposed_msn_headword": row["msn_headword"],
                "current_register": row["register"],
                "current_variety": row["variety"],
                "evidence_summary": evidence,
                "recommended_action": action,
                "source_id": row["source_id"],
                "source_file": row["source_file"],
                "source_reference": row["source_reference"],
                "source_confidence": row["source_confidence"],
                "editorial_status": row["editorial_status"],
                "speaker_validation_status": row["speaker_validation_status"],
            }
        )
    return rows


def example_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if GRAMMAR_EXAMPLE_BANK.exists():
        with GRAMMAR_EXAMPLE_BANK.open("r", encoding="utf-8-sig", newline="") as f:
            for source_row in csv.DictReader(f):
                if source_row.get("register") != "MSN_neutral":
                    continue
                rows.append(
                    {
                        "example_id": source_row["example_id"],
                        "source_family": "grammar_example_bank",
                        "source_register": source_row.get("register", ""),
                        "target_register": "MSN_neutral",
                        "nahuatl_text": source_row.get("nahuatl_text", ""),
                        "morpheme_segmentation": source_row.get("morpheme_segmentation", ""),
                        "gloss_line": source_row.get("gloss_line", ""),
                        "translation_en": source_row.get("translation_en", ""),
                        "translation_es": source_row.get("translation_es", ""),
                        "operation": source_row.get("source_type", ""),
                        "evidence_status": source_row.get("evidence_status", ""),
                        "source_reference": source_row.get("source_reference", ""),
                        "editorial_note": source_row.get("editorial_note", ""),
                    }
                )
    if E_TO_MSN_EXAMPLES.exists():
        with E_TO_MSN_EXAMPLES.open("r", encoding="utf-8-sig", newline="") as f:
            for source_row in csv.DictReader(f):
                rows.append(
                    {
                        "example_id": f"MSN-CONV-{len(rows) + 1:04d}",
                        "source_family": "register_conversion",
                        "source_register": source_row.get("source_register", ""),
                        "target_register": source_row.get("target_register", ""),
                        "nahuatl_text": source_row.get("target_text", ""),
                        "morpheme_segmentation": "",
                        "gloss_line": "",
                        "translation_en": "",
                        "translation_es": "",
                        "operation": source_row.get("operation", ""),
                        "evidence_status": "editorially_normalized",
                        "source_reference": "register_conversion/ehn_to_msn_neutral_examples.csv",
                        "editorial_note": source_row.get("note", ""),
                    }
                )
    return rows


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, object]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def distribution(rows: Iterable[dict[str, object]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = clean(row.get(field)) or "(blank)"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    conn = connect()
    quick_check = conn.execute("PRAGMA quick_check").fetchone()[0]
    inventory = inventory_rows(conn)
    conn.close()

    reviews = review_rows(inventory)
    examples = example_rows()

    inventory_count = write_csv(EXPORT_DIR / "msn_inventory.csv", INVENTORY_FIELDS, inventory)
    review_count = write_csv(EXPORT_DIR / "msn_review_queue.csv", REVIEW_FIELDS, reviews)
    example_count = write_csv(EXPORT_DIR / "msn_example_bank.csv", EXAMPLE_FIELDS, examples)

    summary = {
        "database": str(DB_PATH.relative_to(ROOT)),
        "quick_check": quick_check,
        "outputs": {
            "msn_inventory.csv": inventory_count,
            "msn_review_queue.csv": review_count,
            "msn_example_bank.csv": example_count,
        },
        "inventory_by_register": distribution(inventory, "register"),
        "inventory_by_review_status": distribution(inventory, "msn_review_status"),
        "review_queue_by_priority": distribution(reviews, "priority"),
        "review_queue_by_reason": distribution(reviews, "queue_reason"),
        "examples_by_source_family": distribution(examples, "source_family"),
        "notes": [
            "Classical citation and comparative-only rows are flagged for review by design.",
            "This phase does not mutate the production SQLite database.",
        ],
    }
    with (REPORT_DIR / "msn_phase_b_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
