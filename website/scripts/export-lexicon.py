#!/usr/bin/env python3
"""Export a lossless lexical archive plus search fields from read-only SQLite."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import unicodedata


ROOT = Path(__file__).resolve().parents[2]
SIMEON_SOURCE = "FCN-SRC-SIMEON-PARSED"
SOURCE_URLS = {
    "FCN-SRC-SIMEON-PARSED": "https://archive.org/details/dictionnairedela00sime",
    "FCN-SRC-SIMEON-OCR-RAW": "https://archive.org/details/dictionnairedela00sime",
    "FCN-SRC-KAIKKI-UNIFIED": "https://kaikki.org/",
    "FCN-SRC-OUT-KAIKKI-JSONL": "https://kaikki.org/",
    "FCN-SRC-OUT-KAIKKI-CSV": "https://kaikki.org/",
}


def fold(value: object) -> str:
    """Fold only for lookup; archived and displayed strings stay unchanged."""
    text = "" if value is None else str(value)
    return "".join(
        char for char in unicodedata.normalize("NFD", text.casefold())
        if not unicodedata.combining(char)
    )


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def write_record(stream, kind: str, data: dict) -> None:
    stream.write(json.dumps({"type": kind, "data": data}, ensure_ascii=False) + "\n")


def export(sqlite_path: Path, out_path: Path) -> dict:
    sqlite_path = sqlite_path.resolve(strict=True)
    out_path = out_path.resolve()
    if sqlite_path == out_path:
        raise ValueError("Output must be separate from the SQLite archive.")
    source_sha256 = fingerprint(sqlite_path)
    source_bytes = sqlite_path.stat().st_size
    connection = sqlite3.connect(sqlite_path.as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    temporary_path = out_path.with_suffix(out_path.suffix + ".tmp")
    try:
        checks = [row[0] for row in connection.execute("PRAGMA quick_check")]
        if checks != ["ok"]:
            raise ValueError("SQLite integrity check failed.")
        sources = [dict(row) for row in connection.execute("SELECT * FROM sources ORDER BY source_id")]
        payloads = defaultdict(list)
        for row in connection.execute("SELECT * FROM entry_payloads ORDER BY payload_id"):
            payloads[row["entry_id"]].append(dict(row))
        variants = defaultdict(list)
        for row in connection.execute("SELECT * FROM variants ORDER BY entry_id, sort_order, variant_id"):
            variants[row["entry_id"]].append(dict(row))
        references = defaultdict(list)
        for row in connection.execute("SELECT * FROM entry_sources ORDER BY entry_id, is_primary DESC, entry_source_id"):
            references[row["entry_id"]].append(dict(row))
        entries = [dict(row) for row in connection.execute("SELECT * FROM lexicon_entries ORDER BY entry_id")]
        counts = Counter(row["source_id"] for row in entries)
        metadata = {
            "dataset_id": "master_lexicon",
            "export_version": 1,
            "source_filename": sqlite_path.name,
            "source_sha256": source_sha256,
            "source_bytes": source_bytes,
            "entry_count": len(entries),
            "source_count": len(sources),
            "variant_count": sum(map(len, variants.values())),
            "payload_count": sum(map(len, payloads.values())),
            "entry_counts_by_source": dict(counts),
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "search_normalization": "Unicode NFD, casefold, remove combining marks; originals preserved",
            "translations": "Original French and existing source English/Spanish glosses only; no generated translations",
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8", newline="\n") as output:
            write_record(output, "metadata", metadata)
            for source in sources:
                write_record(output, "source", {
                    "source_id": source["source_id"],
                    "source_file": source["source_file"],
                    "upstream_title": source["upstream_title"],
                    "source_type": source["source_type"],
                    "license": source["license"],
                    "source_url": SOURCE_URLS.get(source["source_id"]),
                    "original_metadata": source,
                })
            for entry in entries:
                entry_id = entry["entry_id"]
                archived = payloads.get(entry_id, [])
                desired_kind = "simeon_parsed_entry" if entry["source_id"] == SIMEON_SOURCE else "out_kaikki_row"
                selected = next((row for row in archived if row["payload_kind"] == desired_kind), None)
                if selected is None:
                    raise ValueError(f"Missing original source payload for {entry_id}.")
                original = json.loads(selected["payload_json"])
                headword = (
                    original.get("headword") if entry["source_id"] == SIMEON_SOURCE
                    else original.get("lemma_display")
                ) or entry["classical_citation_form"] or entry["ehn_spoken_form"] or entry["msn_headword"] or entry_id
                definition_fr = original.get("definition_fr") if entry["source_id"] == SIMEON_SOURCE else None
                entry_variants = variants.get(entry_id, [])
                roots = original.get("roots") or ([entry["root_family"]] if entry["root_family"] else [])
                if not isinstance(roots, list):
                    roots = [roots]
                etymology = original.get("etymology") or None
                forms = [headword, entry["classical_citation_form"], entry["ehn_spoken_form"], entry["msn_headword"], entry["msn_poetic_form"]]
                for variant in entry_variants:
                    forms.extend([variant["form_text"], variant["raw_form"], variant["normalized_form"]])
                # De-duplicate lookup forms only, never source entries or variants.
                folded_forms = list(dict.fromkeys(fold(form) for form in forms if form))
                search_parts = [*forms, definition_fr, entry["gloss_en"], entry["gloss_es"], etymology, *roots]
                record = {
                    "entry_id": entry_id,
                    "original_headword": headword,
                    "headword_folded": fold(headword),
                    "headword_search": "\n".join(folded_forms),
                    "definition_fr": definition_fr,
                    "definition_en": entry["gloss_en"],
                    "definition_es": entry["gloss_es"],
                    "part_of_speech": entry["part_of_speech"],
                    "register": entry["register"],
                    "variety": entry["variety"],
                    "source_id": entry["source_id"],
                    "source_file": entry["source_file"],
                    "source_reference": entry["source_reference"],
                    "source_url": SOURCE_URLS.get(entry["source_id"]),
                    "source_confidence": entry["source_confidence"],
                    "editorial_status": entry["editorial_status"],
                    "speaker_validation_status": entry["speaker_validation_status"],
                    "classical_citation_form": entry["classical_citation_form"],
                    "msn_headword": entry["msn_headword"],
                    "ehn_spoken_form": entry["ehn_spoken_form"],
                    "msn_poetic_form": entry["msn_poetic_form"],
                    "roots": roots,
                    "variants": entry_variants,
                    "etymology": etymology,
                    "original_payload": original,
                    "original_entry": entry,
                    "source_references": references.get(entry_id, []),
                    "notes_public": entry["notes_public"],
                    "notes_internal": entry["notes_internal"],
                    "search_text": "\n".join(fold(part) for part in search_parts if part),
                    "source_sha256": source_sha256,
                }
                write_record(output, "entry", record)
        if fingerprint(sqlite_path) != source_sha256:
            raise ValueError("Source archive changed during export; retry from a stable copy.")
        temporary_path.replace(out_path)
        return {**metadata, "output": str(out_path)}
    finally:
        connection.close()
        if temporary_path.exists():
            temporary_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", type=Path, default=ROOT / "database" / "fcn_master_lexicon_phase8_6_primer.sqlite")
    parser.add_argument("--out", type=Path, required=True, help="Destination JSONL file, separate from the SQLite source.")
    args = parser.parse_args()
    print(json.dumps(export(args.sqlite, args.out), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
