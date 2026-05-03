# Database Source Of Truth

This folder is the preferred local home for the canonical production database:

```text
database/fcn_master_lexicon_phase8_6_primer.sqlite
```

The database file itself is intentionally not tracked by Git because it is larger than GitHub's normal file limit. The public S3 source of truth is:

```text
https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite
```

## Why This Folder Exists

Earlier build phases created SQLite snapshots in several folders. Those are useful build artifacts, but they are not the validation source of truth.

For reviewer packets, MSN generation, and public-facing references, use the Phase 8.6 primer database above. It contains:

- 37,146 lexicon entries
- 44,900 variants
- 1,008 primer vocabulary items
- 100 lessons

## Get The Database

With AWS CLI:

```powershell
aws s3 cp s3://nahuatl-language/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite .\database\fcn_master_lexicon_phase8_6_primer.sqlite --region us-east-1
```

Or use the helper:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\database\fetch_source_of_truth.ps1
```

## Fallback

Some legacy scripts still have a fallback to:

```text
curriculum/fcn_master_lexicon_phase8_6_primer.sqlite
```

That fallback exists only to keep old local checkouts working. New work should point to `database/`.
