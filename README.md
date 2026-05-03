# Flor y Canto Nahuatl (FCN)

The first machine-readable Nahuatl language infrastructure: a 37,000-entry lexicon, a complete CEFR A1–B1 instructional curriculum, a multi-register orthographic standard, and four production-ready reference manuals — all built from primary historical and contemporary sources and released open.

---

## Scale at a glance

| Resource | Count |
|---|---|
| Siméon 1885 parsed entries | 28,709 |
| Wiktionary/Kaikki lexical rows | 8,465 (4 varieties) |
| UD treebank sentences | 2,169 |
| UD treebank tokens | 19,549 |
| Classical example bank (text blocks) | 60,663 |
| **Master lexicon entries** | **37,146** |
| **Lexicon variants** | **44,900** |
| Lesson units | 100 |
| Core curriculum units | 32 |
| Primer vocabulary items (A1–B1) | 1,008 |
| Primer constructions | 278 |
| Unit exports (4 formats × 32 units) | 128 files |
| Assessment items | 160 |

---

## What this is

**Flor y Canto Nahuatl** treats Nahuatl as a teachable, writable, publishable living language — not a museum artifact. It builds three distinct production registers with their own orthographic standards, pedagogical materials, and governance rules:

| Register | Label | Description |
|---|---|---|
| Spoken standard | EHN | Eastern Huasteca Nahuatl — spoken-first, primer foundation |
| Written standard | MSN neutral | Modern written norm — education and publishing |
| Literary elevated | MSN-P | Elevated literary register — song, ceremony, public address |

Nahuatl is spoken by approximately 1.7 million people today — the most widely spoken indigenous language family in North America. The major historical dictionaries have been locked inside scanned page images and physical books. This project makes that foundation machine-readable, register-distinguished, and source-tracked.

---

## Project pipeline

```
source_data/          Parse raw sources → lexical rows, classical examples, UD grammar evidence
      ↓
lexicon_bootstrap/    Import and unify → first master lexicon SQLite
      ↓
orthography/          Normalize spelling → FCN conventions (k/s/w/ts/h/macrons)
      ↓
core_vocabulary/      Curate core vocab → core_ehn_250, core_ehn_500, example bank
      ↓
curriculum/           Instructional pipeline → 37K-entry database, 32 units, 1,008 primer items
      ↓
poetic_register/      Poetic inventory → 21-item MSN-P seed (diction, vocatives, formulas)
register_conversion/  Conversion rules → EHN↔MSN↔MSN-P↔Classical examples
editorial_qa/         QA framework → 6-level scale, validation status taxonomy
      ↓
reference_manuals/    Final products → 5 reference documents (D14–D18)
```

**The production database is `curriculum/fcn_master_lexicon_phase8_6_primer.sqlite`.**

---

## Directory guide

| Directory | What it contains |
|---|---|
| `source_data/` | Raw source data and parser pipeline: Kaikki JSONL, Siméon JSON, UD treebanks, COERLL HTML, processed outputs |
| `lexicon_bootstrap/` | First unified SQLite from all sources; database schema; import script |
| `orthography/` | FCN orthographic conventions; style manual; normalization script |
| `core_vocabulary/` | Curated 250/500-item EHN vocab lists; 100 essential verbs; example bank |
| `curriculum/` | **Main database and instructional pipeline** (37K entries, 100 lessons, 128 unit exports) |
| `poetic_register/` | MSN-P elevated register inventory: diction, vocatives, refrain particles, rhetorical formulas |
| `register_conversion/` | Rules and worked examples for all 4 register conversion directions |
| `editorial_qa/` | Editorial QA protocol (QA-0 through QA-5) and validation framework |
| `reference_manuals/` | All final deliverables: Master Sourcebook (D14), Spoken Primer (D15), MSN Manual (D16), Poetic Manual (D17), Dictionary Manual (D18) |
| `docs/` | Founding charter, register charter, mission statements, source hierarchy document |
| `workspace_msn/` | Scratch workspace — copy of Kaikki and Siméon data; canonical versions are in `source_data/` |

### Root-level data files

`simeon_parsed.json`, `simeon_1885_ocr_raw.txt`, `simeon_parser.py`, and `simeon_wordlist.txt` are kept at root because they are the primary public-facing data files (referenced by the S3 download links below). The canonical copies for pipeline use are in `source_data/`.

---

## Reference manuals — important note

The files in `reference_manuals/` are **editorial reference documents**. They are not the production data. They document the schema, pedagogy, and register conventions that govern the database in `curriculum/`. See `reference_manuals/README.md` for the full explanation.

---

## Sources

| Source | Date | License |
|---|---|---|
| Rémi Siméon, *Dictionnaire de la langue nahuatl ou mexicaine* | 1885 | Public domain |
| Alonso de Molina, *Vocabulario en lengua castellana y mexicana* | 1571 | Public domain |
| Bernardino de Sahagún, *Florentine Codex* | 1577 | Public domain |
| English Wiktionary (via Wiktextract/Kaikki) | 2026 | CC BY-SA 3.0 / GFDL |
| COERLL Nāhuatlahtolli course | 2026 | Open educational resource |
| UD Western Sierra Puebla Nahuatl (ITML) | 2026 | See treebank license |
| UD Highland Puebla Nahuatl (ITML) | 2026 | See treebank license |

OCR sources: [Siméon on archive.org](https://archive.org/details/dictionnairedela00sime) · [Molina on archive.org](https://archive.org/details/vocabulariodela00platgoog)

---

## Quick start — lexicon data

```python
import json

with open("simeon_parsed.json") as f:
    data = json.load(f)

# Search for a word
for entry in data["entries"]:
    if entry["headword"] == "XOCHITL":
        print(entry)
        break

# Find every word built from a root
cuica_words = [e for e in data["entries"] if "cuica" in e.get("roots", [])]
for e in cuica_words:
    print(f"  {e['headword']}: {e['definition_fr'][:80]}")
```

## Quick start — production database

```python
import sqlite3

conn = sqlite3.connect("curriculum/fcn_master_lexicon_phase8_6_primer.sqlite")
cur = conn.cursor()

# How many entries?
cur.execute("SELECT COUNT(*) FROM lexicon_entries")
print(cur.fetchone())  # (37146,)

# Browse primer vocabulary
cur.execute("SELECT surface_form, gloss_en, part_of_speech FROM primer_vocab LIMIT 20")
for row in cur.fetchall():
    print(row)

# Get the full curriculum unit plan
cur.execute("SELECT lesson_number, theme_en, target_band FROM phase82_unit_plan ORDER BY lesson_number")
for row in cur.fetchall():
    print(row)
```

---

## FCN orthographic conventions

| Feature | FCN convention | Classical variant |
|---|---|---|
| Velar stop | k | c / qu |
| Sibilant | s | z / ç |
| Labio-velar | w | hu / uh |
| Affricate | ts | tz |
| Saltillo / glottal | h | h / ʼ / unmarked |
| Vowel length | macron (ā ē ī ō) | unmarked |

---

## Data breakdown

### Siméon Dictionary

| | Count |
|---|---|
| Total entries | 28,709 |
| Unique headwords | 26,806 |
| Nouns (including derived) | 9,765 |
| Verbs | 5,888 |
| Adjectives (including derived) | 3,355 |
| Adverbs | 917 |
| Entries with root morphology | 19,150 |

### Wiktionary (Kaikki)

| Variety | Rows |
|---|---|
| Classical Nahuatl (nci) | 5,132 |
| Central Nahuatl (nhn) | 1,855 |
| Central Huasteca Nahuatl (nch) | 795 |
| Eastern Huasteca Nahuatl (nhe) | 683 |
| **Total** | **8,465** |

### Universal Dependencies

| | Count |
|---|---|
| Sentences | 2,169 |
| Tokens | 19,549 |
| Unique grammatical features | 61 |

---

## S3 hosting

Public release artifacts are hosted on Amazon S3:

```
https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/
```

> **Note:** S3 paths use the original `fcn_ingest/` directory name from before the repository reorganization. The local directory is now `source_data/`. The S3 objects have not moved.

### Siméon 1885 dictionary

| File | Size | Link |
|---|---|---|
| `simeon_parsed.json` | 6.2 MB | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/simeon_parsed.json) |
| `simeon_1885_ocr_raw.txt` | 3.2 MB | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/simeon_1885_ocr_raw.txt) |
| `simeon_wordlist.txt` | 368 KB | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/simeon_wordlist.txt) |
| `simeon_parser.py` | 13.5 KB | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/simeon_parser.py) |

### Wiktionary / Kaikki lexical data

| File | Size | Variety | Link |
|---|---|---|---|
| `nahuatl_kaikki_unified.json` | 3.9 MB | All 4 varieties combined | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/nahuatl_kaikki_unified.json) |
| `nahuatl_kaikki_raw.jsonl` | 9.3 MB | All 4 varieties (raw) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/nahuatl_kaikki_raw.jsonl) |
| `kaikki_nci.jsonl` | 6.2 MB | Classical Nahuatl (5,132 rows) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/kaikki_nci.jsonl) |
| `kaikki_nhn.jsonl` | 1.6 MB | Central Nahuatl (1,855 rows) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/kaikki_nhn.jsonl) |
| `kaikki_nch.jsonl` | 616 KB | Central Huasteca (795 rows) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/kaikki_nch.jsonl) |
| `kaikki_nhe.jsonl` | 496 KB | Eastern Huasteca (683 rows) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/kaikki_nhe.jsonl) |

### FCN parsed outputs

| File | Size | Description | Link |
|---|---|---|---|
| `out_kaikki/fcn_lexical_rows.csv` | 3.1 MB | FCN lexical rows (CSV) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/out_kaikki/fcn_lexical_rows.csv) |
| `out_kaikki/fcn_lexical_rows.jsonl` | 6.9 MB | FCN lexical rows (JSONL) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/out_kaikki/fcn_lexical_rows.jsonl) |
| `out_classical/classical_blocks.jsonl` | 16.4 MB | Classical text blocks (60,663) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/out_classical/classical_blocks.jsonl) |
| `out_classical/classical_examples.jsonl` | 11.6 MB | Classical examples (55,904) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/out_classical/classical_examples.jsonl) |
| `out_classical/headword_candidates.csv` | 3 KB | Classical headword candidates | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/out_classical/headword_candidates.csv) |
| `out_ud/sentences.jsonl` | 1.0 MB | UD sentences (2,169) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/out_ud/sentences.jsonl) |
| `out_ud/tokens.csv` | 3.5 MB | UD tokens (19,549) | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/out_ud/tokens.csv) |
| `out_ud/lemma_feature_counts.csv` | 187 KB | UD lemma feature counts | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/out_ud/lemma_feature_counts.csv) |
| `out_ud/grammar_evidence_examples.jsonl` | 18.9 KB | UD grammar evidence examples | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/out_ud/grammar_evidence_examples.jsonl) |

### Universal Dependencies treebanks (CoNLL-U)

| File | Size | Link |
|---|---|---|
| `nhi_itml-ud-test.conllu` — Western Sierra Puebla Nahuatl | 1.3 MB | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/data/github/ud-western-sierra-puebla/nhi_itml-ud-test.conllu) |
| `azz_itml-ud-test.conllu` — Highland Puebla Nahuatl | 1.1 MB | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/data/github/ud-highland-puebla/azz_itml-ud-test.conllu) |

### Pipeline scripts

| File | Size | Link |
|---|---|---|
| `download_all_nahuatl.py` | 14.5 KB | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/download_all_nahuatl.py) |
| `fcn_source_parsers.py` | 39.1 KB | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/fcn_source_parsers.py) |
| `fcn_legal_ingest.py` | 10.6 KB | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/fcn_ingest/fcn_legal_ingest.py) |

### Production databases (SQLite)

Oversized SQLite databases are hosted outside Git at the normalized S3 database prefix:

```text
https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/
```

See `DATABASE_ARTIFACTS.md` for SHA-256 checksums, local source paths, and upload instructions. The database URLs below are the canonical S3 targets for oversized DB artifacts. The canonical local database is `curriculum/fcn_master_lexicon_phase8_6_primer.sqlite`. Earlier phase databases are build snapshots.

| File | Description | Link |
|---|---|---|
| `fcn_master_lexicon.sqlite` | Initial unified master lexicon | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon.sqlite) |
| `fcn_master_lexicon_phase6_review.sqlite` | Phase 6 orthography review snapshot | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase6_review.sqlite) |
| `fcn_master_lexicon_phase7_review.sqlite` | Phase 7 pre-curriculum build snapshot | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase7_review.sqlite) |
| `fcn_master_lexicon_phase8_bootstrap.sqlite` | Phase 8 bootstrap, all sources | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_bootstrap.sqlite) |
| `fcn_master_lexicon_phase8_open_only.sqlite` | Phase 8 bootstrap, open-license entries only | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_open_only.sqlite) |
| `fcn_master_lexicon_phase8_1_clean.sqlite` | Phase 8.1 orthography-cleaned | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_1_clean.sqlite) |
| `fcn_master_lexicon_phase8_2_units.sqlite` | Phase 8.2 unit plan layer | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_2_units.sqlite) |
| `fcn_master_lexicon_phase8_3_exports.sqlite` | Phase 8.3 unit exports | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_3_exports.sqlite) |
| `fcn_master_lexicon_phase8_4_assessment.sqlite` | Phase 8.4 assessment layer | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_4_assessment.sqlite) |
| `fcn_master_lexicon_phase8_5_products.sqlite` | Phase 8.5 product bundles layer | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_5_products.sqlite) |
| `fcn_master_lexicon_phase8_6_primer.sqlite` | **Canonical: 37,146 entries, 1,008 primer items, 100 lessons** | [Download](https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite) |

---

## Limitations

**Siméon definitions are in French.** English and Spanish translations are on the roadmap.

**OCR source material.** Siméon and Molina texts were auto-OCR'd from 19th-century scans. They contain errors. Use with judgment; corrections are welcome as pull requests.

**Colonial orthography in source data.** Siméon headwords use 16th/17th-century spelling without macrons or glottal-stop marking. FCN orthographic normalization is applied in `orthography/` and forward.

---

## Roadmap

- [ ] English translations of Siméon definitions
- [ ] Spanish translations of Siméon definitions
- [ ] Parse Molina 1571 *Vocabulario* (~23,000 additional entries)
- [ ] OCR error corrections in Siméon source
- [ ] Cross-variety lemma alignment (Classical ↔ Central ↔ Huasteca)
- [ ] Searchable dictionary website
- [ ] Publish primer-ready exports from `curriculum/` instructional track
- [ ] Phase B/C expansion of MSN-P poetic inventory (`poetic_register/`)
- [ ] Community validation pipeline for proposed literary-modern items
- [ ] App and textbook bundle production from `curriculum/phase8_5_reports/`

---

## License

The parsed data in this repository is released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Source material is public domain. Wiktionary-derived data inherits CC BY-SA 3.0 / GFDL.

## Citation

```
Sam Itzli, "Flor y Canto Nahuatl," GitHub, 2026.
https://github.com/samvillasmith/nahuatl-dictionary

Parsed from: Rémi Siméon, Dictionnaire de la langue nahuatl ou mexicaine,
Paris: Imprimerie Nationale, 1885.
```
