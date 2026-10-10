#!/usr/bin/env python3
"""Validate and prepare the complete trilingual archive; publish only with --publish.

The default run creates a deterministic gzip and its public checksum manifest
locally. No AWS connection is made without --publish. Source files and the
original SQLite database are opened read-only and are never modified.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
LANGUAGES = ("fr", "en", "es")
EXPECTED_ENTRIES = 37146
EXPECTED_SOURCE_COUNTS = {"FCN-SRC-SIMEON-PARSED": 28709, "FCN-SRC-KAIKKI-UNIFIED": 8437}
RELEASE_DATE = "2026-10-10"
ARTIFACT_NAME = f"lexicon-translations-{RELEASE_DATE}.jsonl.gz"
MANIFEST_NAME = f"lexicon-translations-{RELEASE_DATE}.manifest.json"
BUCKET = "nahuatl-language"
PREFIX = "molina/translations/"
PUBLIC_BASE = f"https://{BUCKET}.s3.us-east-1.amazonaws.com/{PREFIX}"
UNCLEAR_NOTICES = {
    "en": "The source definition is unreadable.",
    "es": "La definición de la fuente es ilegible.",
    "fr": "La définition de la source est illisible.",
}


def digest_file(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def fingerprint(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise ValueError(f"Invalid {label} fingerprint.")
    return value.lower()


def timestamp(value, label):
    if not isinstance(value, str):
        raise ValueError(f"Missing {label} timestamp.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"Invalid {label} timestamp.") from None
    if parsed.tzinfo is None:
        raise ValueError(f"{label} timestamp must include a timezone.")
    return parsed


def read_source(path, database):
    with database.open("rb") as archive:
        if archive.read(16) != b"SQLite format 3\x00":
            raise ValueError("The original database is not a SQLite archive.")
    database_hash, database_bytes = digest_file(database)
    sources, source_counts = {}, Counter()
    metadata = None
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except (ValueError, UnicodeError):
                raise ValueError(f"Invalid source JSON at line {number}.") from None
            if record.get("type") == "metadata":
                if metadata is not None or sources:
                    raise ValueError("Source metadata must appear first and only once.")
                metadata = record.get("data")
            elif record.get("type") == "entry":
                if not isinstance(metadata, dict):
                    raise ValueError("Source entries require preceding metadata.")
                row = record.get("data", {})
                entry_id, source_id = row.get("entry_id"), row.get("source_id")
                if not isinstance(entry_id, str) or not entry_id or entry_id in sources:
                    raise ValueError("Source entry IDs must be nonempty and unique.")
                if source_id not in EXPECTED_SOURCE_COUNTS:
                    raise ValueError("Unexpected lexical source in the archive.")
                language = "fr" if source_id == "FCN-SRC-SIMEON-PARSED" else "en"
                definition = row.get("definition_" + language) or ""
                if not isinstance(definition, str):
                    raise ValueError("Original definitions must be text or null.")
                sources[entry_id] = {
                    "language": language, "definition": definition,
                    "hash": hashlib.sha256(definition.encode("utf-8")).hexdigest(),
                }
                source_counts[source_id] += 1
    if not isinstance(metadata, dict) or metadata.get("dataset_id") != "master_lexicon" or metadata.get("export_version") != 1:
        raise ValueError("Unsupported or missing master corpus metadata.")
    if len(sources) != EXPECTED_ENTRIES or metadata.get("entry_count") != EXPECTED_ENTRIES:
        raise ValueError(f"The master corpus must contain exactly {EXPECTED_ENTRIES} entries.")
    if dict(source_counts) != EXPECTED_SOURCE_COUNTS or metadata.get("entry_counts_by_source") != EXPECTED_SOURCE_COUNTS:
        raise ValueError("Master corpus source counts do not match the archival release.")
    if fingerprint(metadata.get("source_sha256"), "source") != database_hash or metadata.get("source_bytes") != database_bytes:
        raise ValueError("The source export fingerprint differs from the original SQLite archive.")
    return metadata, sources, database_hash


def validate_cell(row, source):
    if source is None:
        raise ValueError("Translation references an unknown source entry.")
    language = row.get("language")
    if language not in LANGUAGES or row.get("source_language") != source["language"]:
        raise ValueError("Translation language or original language does not match its source.")
    if fingerprint(row.get("source_content_sha256"), "source content") != source["hash"]:
        raise ValueError("A translation is bound to different source text.")
    definition = source["definition"]
    empty = not definition.strip()
    if empty:
        valid = row.get("kind") == "source_missing" and row.get("status") == "missing" and row.get("definition") is None
    elif language == source["language"]:
        valid = row.get("kind") == "original" and row.get("status") == "source" and row.get("definition") == definition
    elif not any(character.isalpha() for character in definition):
        valid = row.get("kind") == "source_unclear" and row.get("status") == "unclear" and row.get("definition") == UNCLEAR_NOTICES[language]
    else:
        valid = row.get("kind") == "machine" and row.get("status") == "unreviewed"
        valid = valid and all(isinstance(row.get(key), str) and row[key].strip() for key in ("definition", "provider", "model"))
        if valid:
            timestamp(row.get("generated_at"), "translation")
    if not valid:
        raise ValueError("A translation cell has invalid text, source preservation, or provenance.")
    if row.get("kind") != "machine" and any(row.get(key) is not None for key in ("provider", "model", "generated_at")):
        raise ValueError("Original, missing, and unreadable records must not claim machine provenance.")


def validate_release(path, sources, source_hash):
    metadata, keys = None, set()
    counts, kinds, providers, models, dates = Counter(), Counter(), set(), set(), []
    digest, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            digest.update(line)
            size += len(line)
            if not line.strip():
                continue
            try:
                record = json.loads(line.decode("utf-8"))
            except (ValueError, UnicodeError):
                raise ValueError(f"Invalid translation JSON at line {number}.") from None
            if not isinstance(record, dict) or not isinstance(record.get("data"), dict):
                raise ValueError("Translation records must have an object payload.")
            row = record["data"]
            if record.get("type") == "metadata":
                if metadata is not None or keys:
                    raise ValueError("Translation metadata must appear first and only once.")
                metadata = row
                if row.get("dataset_id") != "lexicon_translations" or row.get("export_version") != 1:
                    raise ValueError("Unsupported translation release.")
                if row.get("complete") is not True:
                    raise ValueError("An incomplete translation manifest cannot be published.")
                if row.get("entry_count") != EXPECTED_ENTRIES or row.get("record_count") != EXPECTED_ENTRIES * 3:
                    raise ValueError("The release must declare all 37,146 entries and 111,438 language cells.")
                if row.get("languages") is None or len(row["languages"]) != 3 or set(row["languages"]) != set(LANGUAGES):
                    raise ValueError("The release must declare exactly French, English, and Spanish.")
                if fingerprint(row.get("source_sha256"), "source") != source_hash:
                    raise ValueError("The translation release belongs to another SQLite archive.")
                fingerprint(row.get("prompt_sha256"), "translation prompt")
                timestamp(row.get("exported_at"), "export")
            elif record.get("type") == "translation" and metadata is not None:
                entry_id, language = row.get("entry_id"), row.get("language")
                if not isinstance(entry_id, str):
                    raise ValueError("Translation entry IDs must be strings.")
                validate_cell(row, sources.get(entry_id))
                key = (entry_id, language)
                if key in keys:
                    raise ValueError("Duplicate translation cell in the release.")
                keys.add(key)
                counts[language] += 1
                kinds[row["kind"]] += 1
                if row["kind"] == "machine":
                    providers.add(row["provider"])
                    models.add(row["model"])
                    dates.append(timestamp(row["generated_at"], "translation"))
            else:
                raise ValueError("Unknown translation record or missing initial metadata.")
    if metadata is None or len(keys) != EXPECTED_ENTRIES * 3 or any(counts[language] != EXPECTED_ENTRIES for language in LANGUAGES):
        raise ValueError("All entries require one validated cell in each of the three languages.")
    if metadata.get("counts_by_kind") != dict(kinds):
        raise ValueError("Manifest provenance counts differ from the actual language cells.")
    return {
        "metadata": metadata, "counts_by_language": dict(counts), "counts_by_kind": dict(kinds),
        "providers": sorted(providers), "models": sorted(models),
        "first_generated_at": min(dates).isoformat() if dates else None,
        "last_generated_at": max(dates).isoformat() if dates else None,
        "jsonl_sha256": digest.hexdigest(), "jsonl_bytes": size,
    }


def compress_release(source, output, expected_hash):
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".gz.tmp", delete=False) as target:
        temporary = Path(target.name)
        digest = hashlib.sha256()
        try:
            with gzip.GzipFile(filename="", mode="wb", fileobj=target, compresslevel=9, mtime=0) as compressed:
                with source.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(block)
                        compressed.write(block)
        except BaseException:
            target.close()
            temporary.unlink(missing_ok=True)
            raise
    if digest.hexdigest() != expected_hash:
        temporary.unlink(missing_ok=True)
        raise ValueError("The translation release changed during compression; nothing was published.")
    temporary.replace(output)
    return digest_file(output)


def publish(output, public_manifest):
    # Avoid an incompatible optional pyOpenSSL install in Windows Python setups.
    sys.modules["OpenSSL"] = None
    import boto3
    client = boto3.client("s3", region_name="us-east-1")
    with output.open("rb") as artifact:
        client.put_object(
            Bucket=BUCKET, Key=PREFIX + ARTIFACT_NAME, Body=artifact,
            ContentLength=public_manifest["gzip_bytes"], ContentType="application/gzip",
            ContentDisposition=f'attachment; filename="{ARTIFACT_NAME}"',
            CacheControl="public, max-age=3600",
            Metadata={"sha256": public_manifest["gzip_sha256"], "source-sha256": public_manifest["source_sha256"]},
            ChecksumSHA256=base64.b64encode(bytes.fromhex(public_manifest["gzip_sha256"])).decode("ascii"),
        )
    head = client.head_object(Bucket=BUCKET, Key=PREFIX + ARTIFACT_NAME)
    if head.get("ContentLength") != public_manifest["gzip_bytes"] or head.get("Metadata", {}).get("sha256") != public_manifest["gzip_sha256"]:
        raise RuntimeError("Uploaded artifact verification failed.")
    # The public manifest is written last, after a complete artifact is verified.
    client.put_object(
        Bucket=BUCKET, Key=PREFIX + MANIFEST_NAME,
        Body=(json.dumps(public_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"),
        ContentType="application/json; charset=utf-8", CacheControl="public, max-age=3600",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=ROOT / "database/lexicon-translations.jsonl")
    parser.add_argument("--source", type=Path, default=ROOT / "database/lexicon-search.jsonl")
    parser.add_argument("--database", type=Path, default=ROOT / "database/fcn_master_lexicon_phase8_6_primer.sqlite")
    parser.add_argument("--output", type=Path, default=ROOT / "database" / ARTIFACT_NAME)
    parser.add_argument("--manifest", type=Path, default=ROOT / "database" / MANIFEST_NAME)
    parser.add_argument("--publish", action="store_true", help="Upload only after full validation. Omit for a local dry run.")
    args = parser.parse_args(argv)
    try:
        inputs = {args.file.resolve(), args.source.resolve(), args.database.resolve()}
        outputs = {args.output.resolve(), args.manifest.resolve()}
        if inputs & outputs or len(outputs) != 2:
            raise ValueError("Artifact and manifest paths must be distinct from each other and all source files.")
        _, sources, source_hash = read_source(args.source, args.database)
        validated = validate_release(args.file, sources, source_hash)
        gzip_hash, gzip_bytes = compress_release(args.file, args.output, validated["jsonl_sha256"])
        public_manifest = {
            "dataset_id": "lexicon_translations", "release_date": RELEASE_DATE, "complete": True,
            "entry_count": EXPECTED_ENTRIES, "record_count": EXPECTED_ENTRIES * 3,
            "languages": list(LANGUAGES), "entry_counts_by_source": EXPECTED_SOURCE_COUNTS,
            "counts_by_language": validated["counts_by_language"], "counts_by_kind": validated["counts_by_kind"],
            "source_sha256": source_hash, "prompt_sha256": validated["metadata"]["prompt_sha256"],
            "models": validated["models"], "providers": validated["providers"],
            "first_generated_at": validated["first_generated_at"], "last_generated_at": validated["last_generated_at"],
            "exported_at": validated["metadata"]["exported_at"],
            "jsonl_sha256": validated["jsonl_sha256"], "jsonl_bytes": validated["jsonl_bytes"],
            "gzip_sha256": gzip_hash, "gzip_bytes": gzip_bytes,
            "artifact_url": PUBLIC_BASE + ARTIFACT_NAME, "manifest_url": PUBLIC_BASE + MANIFEST_NAME,
            "original_database_url": "https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite",
            "notes": "Original source cells are preserved. Machine translations are unreviewed. Missing and unreadable source definitions have explicit states, never invented meanings.",
        }
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(public_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
        if args.publish:
            publish(args.output, public_manifest)
        print(json.dumps({"prepared": True, "published": args.publish, "output": str(args.output), "manifest": str(args.manifest), **public_manifest}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, FileNotFoundError) as error:
        print(f"Release rejected: {error}", file=sys.stderr)
    except Exception as error:
        # SDK exceptions can contain private connection details; report type only.
        print(f"Release preparation or publication failed ({type(error).__name__}).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
