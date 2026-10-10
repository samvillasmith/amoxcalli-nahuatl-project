# MSN Convergence Target

Everything in Flor y Canto Nahuatl now converges on two final deliverables:

1. A validated **Modern Standard Nahuatl database**
2. A learner book called **Learn Modern Standard Nahuatl**

The database is the source of truth. It must hold the forms, registers, source notes, grammar decisions, example sentences, review status, and publication status needed for responsible MSN use.

The book is the learner-facing synthesis. It should teach someone how to read MSN, write MSN, understand register labels, write short prose or a short book, and begin composing poetry or literary work without confusing MSN neutral, MSN public, MSN poetic, spoken EHN, and classical citation material.

## Canonical Database

The canonical oversized SQLite database is:

```text
fcn_master_lexicon_phase8_6_primer.sqlite
```

The preferred public S3 location is:

```text
https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite
```

The preferred local repo path is:

```text
database/fcn_master_lexicon_phase8_6_primer.sqlite
```

Earlier SQLite files are build snapshots. They are useful evidence, but they are not the final source of truth for MSN validation.

## Validation Target

Reviewers are being asked to validate the whole MSN system, not one isolated draft. A useful review checks:

- orthography
- register boundaries
- core grammar
- core lexicon and headwords
- example sentences
- prose and book-writing readiness
- poetic and literary readiness
- learner-book readiness

The system is not complete until reviewers can separate approved material from material that must be rewritten, rejected, or held for more evidence.

## Reviewer Packet

The reviewer packet is here:

```text
https://github.com/samvillasmith/amoxcalli-nahuatl-project/tree/main/reviewer_care_package
```

Reviewers should start with:

```text
START_HERE.md
```

That file gives:

- input for the reviewer
- exact material to judge
- SQL queries for the database
- the output expected from the reviewer

Expected return files:

```text
REVIEW_OUTPUT_TEMPLATE.csv
REVIEW_SUMMARY_TEMPLATE.md
```

## Final Book

**Learn Modern Standard Nahuatl** comes at the end of the process. It should be written only after the database and reviewer decisions are stable enough to support a learner who wants to write MSN, not merely read about it.
