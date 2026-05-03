# Master Methodology

## Purpose

This document explains how the MSN system was assembled and what reviewers are being asked to validate.

MSN means **Modern Standard Nahuatl**. It is intended to be a teachable, writable, publishable modern written standard. It is not meant to erase living spoken varieties, and it is not meant to pretend that classical Nahuatl is the same thing as modern Nahuatl.

The final project goal is a learner-facing book:

```text
Learn Modern Standard Nahuatl
```

That book should give a learner enough reliable MSN to read, write, compose, and eventually create new books or poetry.

## Source Layers

The project uses several source layers:

1. **Modern spoken and pedagogical material**
   - Especially Eastern Huasteca Nahuatl (EHN) and lesson/curriculum material.
   - Used as the safest foundation for modern learner-facing language.

2. **Lexical databases**
   - Wiktionary/Kaikki derived data across Nahuatl varieties.
   - Used for comparative lexical evidence and variant tracking.

3. **Classical sources**
   - Siméon, Molina, Sahagún, and other historical materials.
   - Used as citation and comparison sources, not automatically as modern MSN.

4. **Grammar and example banks**
   - Existing sentence examples, register conversion examples, and curriculum constructions.
   - Used to build controlled examples and learner patterns.

## Source Of Truth

The canonical production database is:

```text
database/fcn_master_lexicon_phase8_6_primer.sqlite
```

Public S3 URL:

```text
https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite
```

If that local `database/` copy is not present yet, older scripts may temporarily read:

```text
curriculum/fcn_master_lexicon_phase8_6_primer.sqlite
```

For reviewer purposes, the database source of truth is the Phase 8.6 primer database, not earlier build snapshots.

## Register System

Reviewers should validate whether the register system is clear and useful.

Current labels:

- `EHN_colloquial`: spoken Eastern Huasteca evidence
- `EHN_formal`: formal modern spoken/educational style
- `MSN_neutral`: standard written learner/prose register
- `MSN_public`: public-facing polished prose
- `MSN_poetic`: literary, devotional, elevated, or poetic register
- `Classical_citation`: historical/classical form used as citation evidence
- `Comparative_only`: useful comparison form, not approved for MSN use
- `Proposed`: not yet validated
- `Needs_review`: should not be taught as settled
- `Deprecated`: should not be used except historically

The central validation question is not merely "does this word exist?" The question is:

```text
What register does this belong to, and can a learner safely use it in MSN?
```

## Orthography Method

The writing system normalizes toward a modern, teachable orthography while keeping source forms visible.

Common normalizations include:

- `c/qu` to `k` where appropriate
- `z/ç` to `s`
- `hu/uh` to `w` where appropriate
- `tz` to `ts`
- visible `h` for saltillo/glottal evidence where the system supports it

Reviewers should check whether these choices are acceptable, teachable, and not misleading.

## Lexicon Method

Each candidate MSN form should preserve:

- source form
- proposed MSN headword
- part of speech
- English/Spanish gloss
- source reference
- confidence/status
- register label
- review decision

No form should be promoted into public MSN solely because it appears in a historical dictionary or comparative source.

## Grammar Method

Grammar is being validated as teachable learner grammar.

That means reviewers should check:

- whether a pattern is correct
- whether it is too colloquial, too classical, or too artificial
- whether it is appropriate for MSN neutral
- whether it needs a register note
- whether a learner could use it productively

## Poetry And Literary Method

The system should eventually support poetry. But poetry must be marked as poetic/literary register, not smuggled into neutral prose.

Reviewers should check:

- which formulas belong in `MSN_poetic`
- which classical expressions should remain citations
- which devotional or elevated expressions require special notes
- whether learners can understand the boundary between neutral prose and poetic composition

## Validation Method

Validation happens in layers:

1. Source and database integrity
2. Orthography
3. Register labels
4. Core lexicon
5. Core grammar
6. Example sentences
7. Prose-writing readiness
8. Poetic/literary readiness
9. Learner-book readiness

The system is not fully validated until these layers have reviewer decisions.
