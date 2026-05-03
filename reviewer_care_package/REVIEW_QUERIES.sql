-- MSN reviewer queries for fcn_master_lexicon_phase8_6_primer.sqlite
--
-- Open the canonical database, then run the queries below.
-- Canonical DB:
-- https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite

-- 1. Confirm database scale.
SELECT 'lexicon_entries' AS table_name, COUNT(*) AS row_count FROM lexicon_entries
UNION ALL
SELECT 'primer_vocab', COUNT(*) FROM primer_vocab
UNION ALL
SELECT 'primer_constructions', COUNT(*) FROM primer_constructions
UNION ALL
SELECT 'pedagogical_units', COUNT(*) FROM pedagogical_units;

-- 2. Check register distribution.
SELECT register, COUNT(*) AS row_count
FROM lexicon_entries
WHERE is_active = 1
GROUP BY register
ORDER BY row_count DESC;

-- 3. Check validation/editorial status distribution.
SELECT speaker_validation_status, editorial_status, COUNT(*) AS row_count
FROM lexicon_entries
WHERE is_active = 1
GROUP BY speaker_validation_status, editorial_status
ORDER BY row_count DESC;

-- 4. Review active EHN rows that currently feed MSN headword decisions.
SELECT
  entry_id,
  ehn_spoken_form,
  msn_headword,
  part_of_speech,
  gloss_en,
  register,
  variety,
  source_file,
  source_confidence,
  speaker_validation_status,
  editorial_status,
  notes_public
FROM lexicon_entries
WHERE is_active = 1
  AND register = 'EHN_colloquial'
ORDER BY part_of_speech, msn_headword, ehn_spoken_form;

-- 5. Review rows that are not ready for active MSN use by default.
SELECT
  entry_id,
  ehn_spoken_form,
  msn_headword,
  classical_citation_form,
  part_of_speech,
  gloss_en,
  register,
  variety,
  source_file,
  source_confidence,
  editorial_status
FROM lexicon_entries
WHERE is_active = 1
  AND register IN ('Classical_citation', 'Comparative_only')
LIMIT 500;

-- 6. Review primer vocabulary used by the learner-book path.
SELECT
  priority_id,
  headword,
  gloss_en,
  part_of_speech,
  first_lesson_number,
  lesson_frequency,
  occurrence_count,
  avg_confidence
FROM primer_vocab
ORDER BY first_lesson_number, lesson_frequency DESC, headword;

-- 7. Review primer grammar/construction evidence.
SELECT
  priority_id,
  construction_label,
  pattern_text,
  proficiency_band,
  first_lesson_number,
  lesson_frequency,
  occurrence_count,
  avg_confidence,
  example_original
FROM primer_constructions
ORDER BY first_lesson_number, construction_label;

-- 8. Review source records and limitations.
SELECT
  source_id,
  source_file,
  source_type,
  upstream_title,
  project_role,
  authority_domain,
  license,
  limitations,
  canonical_status
FROM sources
ORDER BY source_id;
