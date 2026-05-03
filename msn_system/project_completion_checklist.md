# FCN Project Completion Checklist

This checklist organizes the remaining work around the Founding Charter, Register Charter, existing deliverables D14-D18, and the new MSN authoring/book-production path.

Last updated: 2026-05-03

Status key:

- `[x]` done enough to build on
- `[~]` started, needs completion
- `[ ]` not done yet

## Current Snapshot

- [x] MSN Phase B seed package exists.
  - Full inventory export: 37,146 rows.
  - Full review queue: 37,146 rows.
  - Seed MSN example bank: 7 examples.

- [x] MSN authoring seed package exists.
  - EHN core candidate packet: 683 rows.
  - Internal drafting candidates: 602 rows.
  - Held for cleanup/special review: 81 rows.
  - Provisional internal core seed: 41 rows.
  - Deduplicated authoring lexicon seed: 563 rows.
  - Sentence pattern templates: 10.
  - Genre plans: 4.

- [~] Demonstration drafting path exists, but it is not the validation target.
  - Selected path: children's book.
  - Working title: `A Day In The Milpa`.
  - Current D19 packet: 59 vocabulary rows, 7 sentence patterns, 22 glossary rows, 7 grammar decisions, 8 intentionally avoided/deferred terms, 12-page English source draft, and controlled MSN draft evidence.
  - Role: demonstration evidence only. It does not replace full MSN-system validation.
  - Other possible paths: cookbook, mindfulness chapbook, Tloque Nahuaque devotional/literary work.

- [ ] Final capstone learner book planned.
  - Title: `Learn Modern Standard Nahuatl`.
  - Role: final synthesis book after the MSN system is validated for grammar, lexicon, examples, prose-writing, and poetic/literary use.
  - Plan file: `msn_system/learn_modern_standard_nahuatl_plan.md`.

- [x] Whole-MSN reviewer care package created.
  - Directory: `reviewer_care_package/`.
  - Purpose: give reviewers a small packet that explains what MSN is, how it was built, what source of truth to use, and what decisions are needed.
  - Scope: entire MSN standard: orthography, register, grammar, lexicon, examples, prose, poetry, and learner-book readiness.

- [ ] Whole-MSN validation not yet complete.
  - Needed decisions: orthography, register boundaries, core grammar, core lexicon/headwords, examples, prose/book-writing readiness, poetic/literary readiness, learner-book readiness.
  - Output target: reviewer decisions that can promote, rewrite, reject, or mark evidence gaps before `Learn Modern Standard Nahuatl` is drafted as a public book.

## 1. Constitutional And Governance Layer

- [x] Founding Charter complete
  - File: `docs/founding_charter_v0.1.md`
  - Charter role: defines mission, scope, and publication goals.

- [x] Register Charter complete
  - File: `docs/register_charter_v0.1.md`
  - Charter role: defines EHN, MSN_neutral, MSN_public, MSN_poetic, Classical_citation, Comparative_only, Proposed, Deprecated, Needs_review.

- [x] Source Hierarchy complete
  - File: `docs/Flor y Canto Nahuatl Source Hierarchy Document.md`
  - Charter role: defines which sources can support spoken, written, poetic, grammar, and unresolved claims.

- [x] Editorial QA and validation framework started
  - Files: `editorial_qa/fcn_deliverable12_editorial_qa_protocol.md`, `editorial_qa/fcn_deliverable13_validation_framework.md`
  - Next: apply these checks to actual public book/manuscript outputs.

## 2. Data And Lexicon Layer

- [x] Raw source corpus assembled
  - Directory: `source_data/`
  - Includes Kaikki/Wiktionary, Simeon, UD, COERLL-derived material, and parser outputs.

- [x] Master lexicon built
  - File: `curriculum/fcn_master_lexicon_phase8_6_primer.sqlite`
  - Current scale: 37,146 entries and 44,900 variants.

- [x] Orthography and style layer built
  - Directory: `orthography/`
  - Includes normalization scripts, orthography manual, style manual, and EHN-to-MSN candidates.

- [~] Lexicon publication layer started
  - File: `reference_manuals/fcn_deliverable18_dictionary_manual.md`
  - Next: create public dictionary prototype or searchable site.

- [ ] Cross-variety lemma alignment complete
  - Goal: align Classical, Central, Huasteca, EHN, and MSN forms by source and register.

- [ ] Simeon/Molina cleanup and expansion complete
  - Goals: OCR corrections, English/Spanish translation of Simeon definitions, Molina parse/import.

## 3. Spoken EHN Curriculum Layer

- [x] Core EHN vocabulary and primer foundation built
  - Directories: `core_vocabulary/`, `curriculum/`
  - Current scale: 1,008 primer vocab items, 278 primer constructions, 23 primer units.

- [x] Curriculum export system built
  - Directory: `curriculum/phase8_3_reports/unit_exports/`
  - Current scale: 32 units in 4 formats.

- [x] Assessment layer built
  - Current scale: 160 assessment items.

- [~] D15 Spoken EHN Primer drafted
  - File: `reference_manuals/fcn_deliverable15_spoken_ehn_primer.md`
  - Next: convert from reference-manual draft into a polished public primer.

- [ ] Public primer release packet complete
  - Needs: final manuscript, glossary, exercises, source note, QA report, version number.

## 4. MSN Neutral Written System

- [~] D16 MSN Manual drafted
  - File: `reference_manuals/fcn_deliverable16_msn_manual.md`
  - Done: definition, orthography, model sentences, initial paradigms, register cautions.
  - Next: complete Phase B gaps.

- [x] MSN System Phase B seed created
  - Directory: `msn_system/`
  - Outputs: inventory, review queue, example bank, summary report.
  - Counts: 37,146 inventory rows, 37,146 review rows, 7 seed examples.

- [~] Approve first active MSN core inventory
  - Starting target: review the 683 EHN_colloquial candidates first.
  - Output: `approved_msn_core.csv` or decision table.
  - Current progress: `exports/msn_core_candidates.csv` created with proposed MSN forms, review priorities, and risk flags. This is not public approval yet.
  - Review queue split: 41 primer-core candidates, 561 general EHN candidates, 81 cleanup/special-review rows.
  - Drafting status: 602 candidate rows are acceptable for internal drafting only; none are public-approved yet.
  - Current output: `exports/approved_msn_core_seed.csv` with 41 rows approved for internal controlled drafting only.

- [ ] Complete D16 Phase B
  - Finish grammar chapters 7-9.
  - Expand to 20+ MSN neutral examples.
  - Add 4-5 sample MSN neutral prose paragraphs.
  - Create loanword policy.
  - Define validation workflow for MSN approvals.

- [~] Build MSN Authoring Pack
  - Needs: approved vocabulary, sentence templates, prose patterns, unresolved terms list, QA checklist.
  - Purpose: turn the system into a book-writing engine.
  - Current progress: seed pack created in `msn_authoring_pack.md` with `exports/msn_authoring_lexicon_seed.csv`, `exports/msn_sentence_patterns.csv`, and `exports/msn_genre_seed_plan.csv`.
  - Counts: 563 deduplicated authoring lexicon rows, 10 sentence patterns, 4 genre plans.

## 5. MSN-P And Literary/Devotional Layer

- [~] D17 Poetic Nahuatl Manual drafted
  - File: `reference_manuals/fcn_deliverable17_poetic_nahuatl_manual.md`
  - Current status: seed-stage poetic/manual framework.

- [~] Poetic register inventory started
  - Directory: `poetic_register/`
  - Current scale: small seed inventory for elevated diction, vocatives, refrain particles, rhetorical formulas.

- [ ] Phase B/C MSN-P expansion complete
  - Expand elevated diction inventory.
  - Add approved poetic devices and examples.
  - Add devotional/ceremonial safeguards.

- [ ] Tloque Nahuaque devotional register pack complete
  - Needs: divine-name policy, source notes, prayer/praise formulas, classical citation handling, MSN_public/MSN_poetic boundary rules.

## 6. Annotated Corpus And Demonstration Texts

- [ ] Starter annotated corpus complete
  - Charter role: demonstrate the standard in use and preserve register/source annotations.
  - Needs: EHN examples, MSN neutral prose, MSN_public prose, MSN_poetic/literary examples.

- [~] D19 MSN Authoring System and First Demonstration Text complete
  - Proposed new deliverable.
  - Includes authoring pack, controlled vocabulary, model prose, QA report, and first short public text.
  - Current progress: authoring system seed exists; first demonstration text selected and packaged for internal review as `d19_children_book/`.
  - Current D19 status: controlled MSN review packet created; not public-ready.

- [x] First book project selected
  - Recommended order:
    1. Children's book: selected as `A Day In The Milpa`
    2. Cookbook
    3. Mindfulness chapbook
    4. Tloque Nahuaque devotional/literary work

- [~] First book manuscript complete
  - Needs: English/Spanish planning draft, controlled MSN draft, glossary, annotations, QA report.
  - Current progress: English source draft, controlled MSN slot scaffold, controlled MSN review draft, grammar decisions, glossary seed, and QA report created.
  - Current files: `d19_children_book/manuscript_source_en.md`, `d19_children_book/controlled_msn_draft_scaffold.md`, `d19_children_book/controlled_msn_draft_v0_review.md`, `d19_children_book/book_glossary_seed.csv`, `d19_children_book/qa_report_v0.md`.

- [ ] First book public release packet complete
  - Needs: approved final book, final glossary, source note, register note, license, version number, layout/export, and speaker/community review status.
  - Current blockers: `qa_report_v0.md` has 1 WARN and 1 BLOCKER row.
  - Planning files now exist: `version_and_license_note.md`, `speaker_community_review_status.md`, `publication_artifact_plan.md`.

## 7. Public Release And Product Layer

- [x] Whole-MSN validation package complete
  - Files: reviewer-facing methodology, source-of-truth note, validation request, worksheets, packet scope, target-book description, and reviewer index.
  - Directory: `reviewer_care_package/`.

- [ ] Whole-MSN external validation complete
  - Needs: reviewer decisions across orthography, register boundaries, grammar, lexicon, example policy, prose/book-writing readiness, poetic/literary readiness, and learner-book readiness.
  - Output: a signed-off decision log that separates approved material from rewrite/reject/needs-more-evidence material.

- [ ] Searchable dictionary website complete

- [ ] Public primer/product bundles complete

- [ ] Public MSN manual release complete

- [ ] Public poetic/literary manual release complete

- [ ] Public corpus/release packet complete

- [ ] `Learn Modern Standard Nahuatl` capstone book complete
  - Final project book.
  - Needs: completed D16 grammar, approved core MSN lexicon, exercises, answer key, public-safe glossary, source/register notes, validation statuses, version number, license/source note, and publication layout/export.
  - Current progress: capstone plan created at `msn_system/learn_modern_standard_nahuatl_plan.md`.

- [ ] Versioning and editorial process stable
  - Required for FCN v1.0.

## Immediate Work Order

1. Send the whole-MSN reviewer care package.
   - Directory: `reviewer_care_package/`.
   - What reviewers are validating: the standard itself, not a small draft.
   - Required response files: completed `VALIDATION_WORKSHEETS.md` or equivalent spreadsheet responses, plus any corrected forms/examples.
   - Status: care package created; external review pending.

2. Review the 41 `P1_primer_core_candidate` rows as part of whole-system validation.
   - Source file: `msn_system/exports/msn_core_candidates.csv`.
   - Output target: `approved_msn_core_seed.csv` or a decision table.
   - Rule: approval means "usable for controlled MSN drafting," not final community validation.
   - Status: provisional internal seed complete at `msn_system/exports/approved_msn_core_seed.csv`.

3. Validate the core MSN grammar and example policy.
   - Use D16 plus `reviewer_care_package/VALIDATION_WORKSHEETS.md`.
   - Decide which sentence patterns, question forms, negation forms, possession forms, verb/person/aspect patterns, location patterns, and narrative connectors are public-teachable.
   - Output target: approved/rewrite/reject decision log.

4. Validate prose and book-writing readiness.
   - Required genres to assess: short learner paragraphs, short book, cookbook/procedural writing, mindfulness/reflective prose, children's book/simple concrete prose, and devotional/literary writing.
   - Output target: list of approved genres and blocked genres, with required safeguards.

5. Validate poetic/literary readiness.
   - Decide what belongs in MSN_neutral, MSN_public, and MSN_poetic.
   - Add safeguards for Tloque Nahuaque devotional/literary material, classical citation, elevated diction, vocatives, and parallelism.

6. Revise D16 and the authoring pack from reviewer decisions.
   - Update grammar chapters, examples, lexicon status, unresolved terms, source/register notes, and QA gates.
   - Keep rejected or uncertain items visibly marked.

7. Build validated model texts.
   - Possible paths: children's book, cookbook, mindfulness chapbook, or Tloque Nahuaque devotional/literary work.
   - Rule: model texts come after system-level decisions, and every form must carry source/register/validation status.

8. Complete the relevant D16 Phase B pieces.
   - Grammar chapters 7-9.
   - 20+ MSN examples.
   - Loanword policy.
   - 4-5 sample prose paragraphs.

9. Revise into publication format.
   - Markdown first, then PDF/print format.

10. Release validated demonstration texts as D19 or later deliverables.

11. Build the final capstone learner book.
   - Title: `Learn Modern Standard Nahuatl`.
   - Use D15 for learner sequencing, D16 for MSN grammar authority, D18 for glossary conventions, validated model texts for reading passages, and the reviewer decision log for public-safe forms.
   - Status: planned as the end-of-process book.

## FCN v1.0 Completion Definition

FCN v1.0 is complete when the project has:

- stable charters and source hierarchy
- stable orthography and style manual
- production master lexicon
- complete spoken EHN primer
- complete MSN manual
- complete MSN-P manual
- publication-ready dictionary prototype
- starter annotated corpus
- at least one public demonstration text/book in the standard
- the final capstone book `Learn Modern Standard Nahuatl`
- visible validation status across core materials
- stable versioning and editorial process
