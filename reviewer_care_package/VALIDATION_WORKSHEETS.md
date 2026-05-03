# Validation Worksheets

This file is no longer the primary reviewer interface.

Use:

1. `START_HERE.md` for the assignment
2. `REVIEW_OUTPUT_TEMPLATE.csv` for item-by-item findings
3. `REVIEW_OUTPUT_GUIDE.md` for examples and column definitions
4. `REVIEW_SUMMARY_TEMPLATE.md` for the short written summary

## Required Decision Labels

- `approve`
- `approve_with_note`
- `rewrite`
- `reject`
- `needs_more_evidence`
- `outside_my_expertise`

## Required Review Logic

For every decision, reviewers should identify:

- the exact item judged
- the file, database row, query, or rule being judged
- the decision label
- the required change, if any
- the corrected form/rule/example, if known

Do not return broad notes without item-level findings. Broad notes are useful only when they are attached to a specific database row, headword, rule, example, pattern, sampled approval, or blocker in `REVIEW_OUTPUT_TEMPLATE.csv`.
