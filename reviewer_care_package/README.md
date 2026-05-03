# MSN Reviewer Care Package

This folder is the reviewer-facing packet for validating **Modern Standard Nahuatl (MSN)**.

Reviewers should not need to infer the assignment or wander through the repo. The packet is organized as:

```text
input for reviewer -> material to judge -> output for us
```

Start with `START_HERE.md`.

## What We Are Asking You To Validate

The goal is to validate the **whole MSN system**:

- the canonical MSN database
- the writing standard
- the register boundary between spoken EHN, MSN neutral, MSN public, MSN poetic, and classical citation
- the core grammar choices
- the core lexicon and headword choices
- the example sentences
- learner-book readiness
- prose/book-writing readiness
- poetic/literary/devotional readiness

## Required Reviewer Output

Return exactly these two completed files:

1. `REVIEW_OUTPUT_TEMPLATE.csv`
   - item-by-item decisions
   - corrected forms/rules/examples where needed
   - required changes

2. `REVIEW_SUMMARY_TEMPLATE.md`
   - short overall judgment
   - blocking issues
   - whether the database can serve as source of truth
   - whether **Learn Modern Standard Nahuatl** is ready to be drafted from this system

## Files In This Packet

| File | Purpose |
|---|---|
| `START_HERE.md` | The actual assignment: input, material to judge, expected output. |
| `REVIEW_OUTPUT_TEMPLATE.csv` | Required findings-log template. Return this completed with one row per concrete finding, not one row per source. |
| `REVIEW_OUTPUT_GUIDE.md` | Column definitions and example rows for the findings log. |
| `REVIEW_SUMMARY_TEMPLATE.md` | Required summary template. Return this completed. |
| `REVIEW_QUERIES.sql` | SQL queries that pull the concrete database material reviewers should inspect. |
| `SOURCE_OF_TRUTH.md` | Canonical database, checksum, S3 link, and supporting sources. |
| `VALIDATION_REQUEST.md` | The review question in prose form. |
| `MASTER_METHODOLOGY.md` | How the system was assembled. |
| `LEARN_MODERN_STANDARD_NAHUATL_TARGET.md` | The final learner-book target. |
| `PACKET_SCOPE.md` | What is and is not in scope. |
| `VALIDATION_WORKSHEETS.md` | Compatibility note; no longer the main interface. |
| `REVIEWER_INDEX.md` | Routing notes for different reviewer types. |

## Decision Labels

Use only these labels:

- `approve`
- `approve_with_note`
- `rewrite`
- `reject`
- `needs_more_evidence`
- `outside_my_expertise`

If something sounds wrong or unnatural, give the better form when possible and put it in the `corrected_form_or_rule` column of `REVIEW_OUTPUT_TEMPLATE.csv`.
