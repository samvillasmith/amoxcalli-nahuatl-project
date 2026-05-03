# Source Of Truth

## Canonical Database

Use this database as the source of truth:

```text
database/fcn_master_lexicon_phase8_6_primer.sqlite
```

Public S3 URL:

```text
https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite
```

GitHub reviewer packet:

```text
https://github.com/samvillasmith/amoxcalli-nahuatl-project/tree/main/reviewer_care_package
```

GitHub project repository:

```text
https://github.com/samvillasmith/amoxcalli-nahuatl-project
```

Current known checksum:

```text
SHA-256: 15D29FDFDDDE5FC623788B1382B6CBC4BD2537165BF9F32F66E0512CBA7C17D8
Bytes: 107200512
```

This is the Phase 8.6 primer database. It is the production database for validation.

## Key Human-Readable Documents

Reviewers should use `START_HERE.md` first. It names the exact input, material to judge, and output expected.

Supporting project documents:

- `docs/founding_charter_v0.1.md`
- `docs/register_charter_v0.1.md`
- `docs/Flor y Canto Nahuatl Source Hierarchy Document.md`
- `reference_manuals/fcn_deliverable15_spoken_ehn_primer.md`
- `reference_manuals/fcn_deliverable16_msn_manual.md`
- `reference_manuals/fcn_deliverable17_poetic_nahuatl_manual.md`
- `reference_manuals/fcn_deliverable18_dictionary_manual.md`
- `DATABASE_ARTIFACTS.md`
- `msn_system/project_completion_checklist.md`
- `msn_system/learn_modern_standard_nahuatl_plan.md`

## What Not To Treat As Source Of Truth

Do not treat these as final authority:

- earlier phase SQLite snapshots
- temporary top-level duplicate databases
- generated review queues without human review
- isolated classical citation forms
- comparative-only rows
- draft demonstration text

Those are useful evidence, not final validation.

## Principle

If two sources disagree, do not silently choose one. Mark the item as `needs_more_evidence` and record what evidence conflicts.
