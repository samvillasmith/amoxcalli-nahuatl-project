# MSN System Phase B Seed

This directory is the first formal package for **MSN neutral**: the Flor y Canto Nahuatl modern written norm used for education, reference writing, public prose, dictionary headwords, and cross-register conversion.

MSN neutral is not spoken EHN written down without review, and it is not classical Nahuatl respelled. It is an editorially governed written layer that stays connected to EHN, preserves source provenance, and keeps classical or poetic material visibly labeled.

## Inputs

- `../curriculum/fcn_master_lexicon_phase8_6_primer.sqlite` - canonical production database.
- `../docs/register_charter_v0.1.md` - register definitions and governance.
- `../docs/Flor y Canto Nahuatl Source Hierarchy Document.md` - source authority and unresolved-case policy.
- `../reference_manuals/fcn_deliverable16_msn_manual.md` - current MSN manual draft.
- `../register_conversion/fcn_deliverable11_register_conversion_guide.md` - EHN to MSN and MSN to MSN-P rules.
- `../orthography/ehn_to_msn_candidates.csv` - EHN to MSN orthographic candidates.
- `../poetic_register/grammar_example_bank.csv` - register-labeled example sentences.

## Outputs

Run:

```powershell
python .\build_msn_system.py
python .\build_msn_authoring_pack.py
python .\build_d19_children_book.py
```

The generators create:

- `exports/msn_inventory.csv` - all active lexicon entries with MSN-facing fields and source metadata.
- `exports/msn_review_queue.csv` - entries requiring MSN editorial decision.
- `exports/msn_example_bank.csv` - initial MSN neutral examples and conversion pairs.
- `exports/msn_authoring_lexicon_seed.csv` - internal drafting lexicon seed.
- `exports/approved_msn_core_seed.csv` - provisional internal core seed.
- `exports/msn_sentence_patterns.csv` - seed sentence templates.
- `d19_children_book/` - first children-book controlled review packet.
- `reports/msn_phase_b_summary.json` - row counts and distribution checks.
- `reports/msn_authoring_pack_summary.json` - authoring-pack counts and checks.
- `reports/d19_children_book_summary.json` - D19 children-book counts and QA status.
- `learn_modern_standard_nahuatl_plan.md` - plan for the final capstone learner book.

## Decision Rules

The review queue is intentionally conservative. It does not promote a form into MSN neutral simply because a usable-looking form exists. It flags:

- missing `msn_headword`
- `Classical_citation` rows
- `Comparative_only` rows
- flagged editorial rows
- low-confidence rows
- unreviewed speaker/editorial statuses

The intended Phase B workflow is: preserve evidence first, propose an MSN decision second, approve only after the source basis and register fit are explicit.

## Current Limits

This is a seed system, not a finished MSN authority layer. It organizes the existing evidence and exposes review work. The D19 children-book packet proves that controlled MSN drafting is achievable, but public release is blocked until editorial and speaker/community validation promote or rewrite the 12 review-only lines.

The final capstone deliverable is **Learn Modern Standard Nahuatl**. That book should come last, after the MSN grammar, lexicon, QA process, demonstration texts, glossary conventions, and release packaging are stable enough to support a standalone learner book.
