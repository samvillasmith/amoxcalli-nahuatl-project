# Definition translation standards

Amoxcalli preserves 37,146 archival records: 28,709 entries parsed from Rémi Siméon's 1885 French dictionary and 8,437 Wiktionary/Kaikki records. English, Spanish, and French reading versions make the archive more accessible while keeping the original definition available for comparison.

## Originals and translations

Siméon's French transcription and Kaikki's English source glosses remain unchanged. A French definition translated from Kaikki is a machine translation, just as an English or Spanish definition translated from Siméon is. A translation does not replace the original or establish a new authoritative Nahuatl meaning.

Generated definitions carry the label **Machine translation · Unreviewed**. Their records retain the source language, the fingerprint of the exact source definition, actual provider, actual model, generation time, and review status. The release includes translations from OpenAI's `gpt-5.4-mini-2026-03-17` and OpenAI GPT OSS 120B through AWS Bedrock, using the identifier `openai.gpt-oss-120b-1:0`.

Both providers use the same versioned translation policy and preservation checks. The release checkpoint identifies that policy; it does not imply that every cell came from one model. Compatible completed work may be retained after comparing the source, requested languages, masked inputs, and instructions. Reused cells keep their original provider, model, and generation time. A provider change does not confer human review or alter the source transcription.

## Preservation criteria

- Preserve Nahuatl headwords, historical spellings, quoted forms, roots, conjugated forms, and person or object prefixes, including visible OCR damage.
- Retain author citations, page references, dates, numbered senses, and the distinction between a definition, an alternative spelling, and a cross-reference.
- Translate the full explanatory text and every sense. Expand grammatical abbreviations when their meaning is clear. Translate French `Voy.` as English **See** or Spanish **Véase**, keeping its reference target.
- Repair ordinary French OCR only when the intended reading is clear. Identify an unreadable segment in the selected language rather than inventing its meaning.
- Preserve scientific names and the source's level of specificity. A general plant, animal, or historical medical term must not become a newly asserted species or modern medical claim.
- Interpret compound expressions and grammatical terminology in context. For example, **reed bed** names an area of growing reeds; **premièrement** describes sequence; **temps primitifs** in historical prose refers to ancient times.

The pipeline masks detected root expressions, preterite forms, cross-reference targets, author citations, and recognized Nahuatl prefixes before requesting translations. It restores those exact source spans afterward. This protects detected forms; it does not establish the accuracy of every translation.

## Source gaps

Automated source checks identify **219 records without a usable definition**: 61 have no definition text, and 158 contain only punctuation or numbers. These records remain in the archive with explicit source-gap or unreadable-fragment status. They are not counted as successful translations. Other records may still contain OCR or parsing defects that require review against their sources.

Some incomplete records are continuations created by OCR or parsing, such as the second half of a cross-reference. Others have explanatory text displaced into a neighboring record. Recovering a meaning requires checking the original scan or another identified source and recording that evidence. A similar headword, grammatical root, neighboring diminutive, or broad category such as “birds” does not justify supplying a missing meaning.

## Release checks and review

A complete release requires an entry for each of the three languages for every archival record, including explicit gap records. The importer checks all 111,438 entry and language cells, their source fingerprints, unchanged originals, provenance, and coverage before accepting the release. Failed requests remain pending; partial exports are used only for isolated previews.

Automated checks verify response structure, exact entry IDs, nonempty translated text, protected spans, unresolved placeholders, and possible truncation. Pilot and ongoing samples check meaning, terminology, alternative forms, morphology, and readable explanations. Machine translations remain unreviewed until a qualified reviewer assesses the entry; passing structural checks alone does not confer scholarly approval.

Corrections should identify the entry, quote the affected source segment, provide the proposed reading, and cite supporting evidence. Preserve the archival transcription while recording corrections and reviewed translations separately.

## Source references

The Siméon corpus derives from the [1885 dictionary scan hosted by Internet Archive](https://archive.org/details/dictionnairedela00sime), which credits Boston Public Library. Kaikki records retain their existing Wiktionary source references, attribution, variety labels, and licensing metadata. The original SQLite release remains the archival download; generated definitions are stored separately.
