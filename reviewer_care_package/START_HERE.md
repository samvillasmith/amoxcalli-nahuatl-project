# Start Here: MSN Review Packet

This packet has one job: make it possible for a reviewer to judge **Modern Standard Nahuatl (MSN)** without wading through the whole repo.

You are not being asked to approve one isolated draft. You are being asked to judge whether the MSN system is valid enough to support the two final deliverables:

1. a validated **MSN database**
2. a learner book called **Learn Modern Standard Nahuatl**

## Input For You

Use these exact inputs.

### 1. Canonical Database

Direct download:

```text
https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite
```

Expected checksum:

```text
SHA-256: 15D29FDFDDDE5FC623788B1382B6CBC4BD2537165BF9F32F66E0512CBA7C17D8
Bytes: 107200512
```

Preferred local path if reviewing from the repo:

```text
database/fcn_master_lexicon_phase8_6_primer.sqlite
```

### 2. Exact Repo Folder

Reviewer packet:

```text
reviewer_care_package/
```

GitHub:

```text
https://github.com/samvillasmith/amoxcalli-nahuatl-project/tree/main/reviewer_care_package
```

### 3. Minimum Files To Read

Read these before judging:

```text
START_HERE.md
SOURCE_OF_TRUTH.md
VALIDATION_REQUEST.md
MASTER_METHODOLOGY.md
LEARN_MODERN_STANDARD_NAHUATL_TARGET.md
REVIEW_QUERIES.sql
```

You do not need to read the whole repository unless you want to audit raw evidence.

## Material To Judge

Judge these specific materials.

| ID | What To Judge | Exact Material |
|---|---|---|
| MSN-DB-001 | Is this the correct source-of-truth database? | S3 DB URL above; `SOURCE_OF_TRUTH.md`; `DATABASE_ARTIFACTS.md` |
| MSN-ORTH-001 | Are the MSN spelling rules acceptable and teachable? | `orthography/`; `reference_manuals/fcn_deliverable16_msn_manual.md`; DB `lexicon_entries.msn_headword` |
| MSN-REG-001 | Are register boundaries clear and honest? | `docs/register_charter_v0.1.md`; `MASTER_METHODOLOGY.md`; DB `lexicon_entries.register`, `speaker_validation_status`, `editorial_status` |
| MSN-LEX-001 | Are core MSN headwords acceptable? | `msn_system/exports/msn_core_candidates.csv`; `msn_system/exports/approved_msn_core_seed.csv`; `REVIEW_QUERIES.sql` query 4 |
| MSN-LEX-002 | Which internal-drafting words can become public MSN, and which must not? | `msn_system/exports/msn_authoring_lexicon_seed.csv` |
| MSN-GRAM-001 | Are the basic sentence patterns acceptable for learners? | `msn_system/exports/msn_sentence_patterns.csv`; D16 MSN manual |
| MSN-GRAM-002 | What grammar must be approved, rewritten, or blocked before public teaching? | `reference_manuals/fcn_deliverable16_msn_manual.md`; `msn_system/exports/msn_example_bank.csv` |
| MSN-EX-001 | Are example sentences natural, teachable, and properly labeled? | `msn_system/exports/msn_example_bank.csv`; D16 examples |
| MSN-PROSE-001 | Can the system support original prose/books? | sentence patterns, authoring lexicon seed, methodology, learner-book target |
| MSN-POET-001 | Can the system support poetry/devotional/literary writing with safeguards? | `reference_manuals/fcn_deliverable17_poetic_nahuatl_manual.md`; `poetic_register/`; `LEARN_MODERN_STANDARD_NAHUATL_TARGET.md` |
| MSN-BOOK-001 | Is the final learner book target valid and realistic? | `LEARN_MODERN_STANDARD_NAHUATL_TARGET.md`; `msn_system/learn_modern_standard_nahuatl_plan.md`; DB `primer_vocab` and `primer_constructions` |

If a file or database table is too large to review fully, review a representative sample and say exactly what you sampled.

If you can open SQLite, use `REVIEW_QUERIES.sql` to pull the review tables. If you cannot open SQLite, use the CSV exports named in the table above and mark the database-specific parts as `outside_my_expertise` or `needs_more_evidence`.

## Output We Need From You

Return exactly these two files.

### 1. `REVIEW_OUTPUT_TEMPLATE.csv`

This is a findings log.

Do **not** fill one row per source. Do **not** fill one row per whole review area.

Fill one row per concrete thing you reviewed:

- one database row
- one headword
- one spelling rule
- one register label
- one grammar rule
- one sentence pattern
- one example sentence
- one prose/literary capability
- one blocker
- one sampled approval

You may repeat the same review ID as many times as needed. For example, `MSN-LEX-001` may appear 50 times if you have 50 headword decisions.

Use `REVIEW_OUTPUT_GUIDE.md` for column definitions and example rows.

Required decisions:

- `approve`
- `approve_with_note`
- `rewrite`
- `reject`
- `needs_more_evidence`
- `outside_my_expertise`

If you choose `rewrite`, include the corrected form, corrected rule, or corrected example.

If you choose `needs_more_evidence`, name the missing evidence.

### 2. `REVIEW_SUMMARY_TEMPLATE.md`

Fill this with:

- your name and expertise
- what you reviewed
- whether the database is usable as the MSN source of truth
- whether the system is ready for **Learn Modern Standard Nahuatl**
- blocking issues
- recommended next changes

## What Counts As A Useful Review

A useful review does **not** say only "looks good" or "needs work."

A useful review says:

- what exact item you reviewed
- where it appears
- your decision
- what must change, if anything
- the corrected form/rule/example if you know it

## What We Will Do With Your Review

Your return files will be used to update:

- the MSN database
- the MSN grammar/manual
- the approved core lexicon
- the example bank
- the authoring pack
- the final book plan for **Learn Modern Standard Nahuatl**
