# Review Output Guide

`REVIEW_OUTPUT_TEMPLATE.csv` is a findings log.

It is **not** one row per source and it is **not** one row per review area.

Use one row for one concrete thing you reviewed:

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

You may repeat the same `review_id` as many times as needed.

For example, if you review ten core headwords and three need correction, return three `MSN-LEX-001` rows, one for each headword. If the other seven are acceptable, you may add one sampled approval row saying what range you checked.

## Columns

| Column | What To Put |
|---|---|
| `finding_id` | Your own ID, such as `REV-001`, `REV-002`, etc. |
| `review_id` | The review area from `START_HERE.md`, such as `MSN-LEX-001`. |
| `item_type` | `database_row`, `headword`, `spelling_rule`, `register_label`, `grammar_rule`, `sentence_pattern`, `example_sentence`, `book_plan`, `blocker`, `sample_approval`, etc. |
| `source_file_or_table` | File path or DB table/query, such as `lexicon_entries`, `primer_vocab`, `msn_system/exports/msn_sentence_patterns.csv`. |
| `locator` | Entry ID, row number, query number, section heading, line number, or sampled range. |
| `item_under_review` | The specific word/rule/example/pattern/claim being judged. |
| `current_value_or_claim` | Current form, current label, current rule, current example, or current claim. |
| `decision` | `approve`, `approve_with_note`, `rewrite`, `reject`, `needs_more_evidence`, or `outside_my_expertise`. |
| `severity` | `blocker`, `major`, `minor`, `note`, or blank. |
| `public_release_blocker` | `yes` or `no`. |
| `corrected_form_or_rule` | Better form, better rule, better label, or better example if known. |
| `evidence_or_reason` | Why you made the decision. Mention source evidence, speaker intuition, grammar reason, or conflict. |
| `required_change` | What we should change in the DB/manual/example/book plan. |
| `reviewer_notes` | Anything else useful. |
| `reviewer_name` | Your name. |
| `reviewer_role` | Your expertise or role. |
| `review_date` | Date of review. |

## Example Rows

These are examples only. Do not copy them unless they match your review.

```csv
finding_id,review_id,item_type,source_file_or_table,locator,item_under_review,current_value_or_claim,decision,severity,public_release_blocker,corrected_form_or_rule,evidence_or_reason,required_change,reviewer_notes,reviewer_name,reviewer_role,review_date
REV-001,MSN-LEX-001,headword,lexicon_entries,entry_id=abc123,example_headword,current_form,rewrite,major,yes,better_form,"Current form sounds unnatural in this register.","Update msn_headword and add note.","Check related forms too.",Reviewer Name,Nahuatl speaker,2026-05-03
REV-002,MSN-GRAM-001,sentence_pattern,msn_system/exports/msn_sentence_patterns.csv,row=7,location pattern,current pattern,needs_more_evidence,major,yes,,"Need speaker confirmation for this locative construction.","Hold pattern from public learner book until confirmed.",,Reviewer Name,teacher,2026-05-03
REV-003,MSN-ORTH-001,sample_approval,lexicon_entries,REVIEW_QUERIES.sql query 4 first 50 rows,MSN headword spellings,50 sampled headwords,approve_with_note,note,no,,"Sample looked consistent except findings REV-001 and REV-004.","No general change; fix listed rows.",,Reviewer Name,linguist,2026-05-03
```
