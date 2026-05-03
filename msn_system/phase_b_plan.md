# MSN Phase B Plan

## Purpose

Phase B turns the existing MSN draft material into a usable written-system layer: searchable inventory, explicit review queues, controlled examples, and completion work for Deliverable 16.

## Workstreams

1. **Inventory governance**
   - Review `msn_review_queue.csv` by priority.
   - Resolve missing `msn_headword` rows only when the evidence basis is clear.
   - Keep classical-only material as `Classical_citation` or `note_only` unless explicitly approved.
   - Add decision records using the schema in `msn_inventory_schema.sql`.

2. **D16 grammar expansion**
   - Fully author chapters 7-9: possession, tense/aspect, negation, and question formation.
   - Expand mini-paradigms with direct source notes and provisional labels.
   - Distinguish forms shared with EHN from forms normalized for written prose.

3. **Example bank expansion**
   - Grow `msn_example_bank.csv` to at least 20 MSN neutral examples.
   - Cover explanation, narration, instruction, public prose, dictionary prose, captions, and neutral contrast examples.
   - Preserve `constructed_pedagogical`, `editorially_normalized`, `lesson_derived_modern`, and `adapted_classical` labels.

4. **Loanword policy**
   - Decide how Spanish loans are handled in MSN neutral.
   - Mark accepted modern loans separately from classical or comparative replacements.
   - Provide examples where a loan, native term, and classical term coexist by register.

5. **Sample prose**
   - Draft 4-5 short MSN neutral paragraphs.
   - Topics: language learning, school/community, milpa/food, public notice, dictionary explanation.
   - Each paragraph should include source notes or construction notes.

6. **Validation workflow**
   - Define reviewer statuses: `proposed`, `approved_msn_neutral`, `needs_review`, `comparative_only`, `classical_citation`, `deprecated`.
   - Require exact source references and a short decision basis for every approval.
   - Produce a public-safe subset only after review.

7. **Capstone learner book**
   - Treat **Learn Modern Standard Nahuatl** as the final synthesis of the project, not an early draft artifact.
   - Build it only after D16 grammar, approved core vocabulary, reviewed examples, glossary conventions, and validation statuses are stable.
   - Use D19 and later demonstration texts as reading material and model prose for the learner book.

## Immediate Next Step

Start with high-value entries already connected to EHN or primer usage. Review those before attempting mass promotion of comparative or classical material.
