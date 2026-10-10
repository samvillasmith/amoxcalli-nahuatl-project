-- Additive search projection. The original SQLite release remains the archive.
CREATE SCHEMA IF NOT EXISTS amoxcalli;

CREATE TABLE IF NOT EXISTS amoxcalli.sources (
  source_id text PRIMARY KEY,
  source_file text NOT NULL,
  upstream_title text,
  source_type text,
  license text,
  source_url text,
  original_metadata jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS amoxcalli.lexicon_entries (
  entry_id text PRIMARY KEY,
  original_headword text NOT NULL,
  headword_folded text NOT NULL,
  headword_search text NOT NULL,
  definition_fr text,
  definition_en text,
  definition_es text,
  part_of_speech text NOT NULL,
  register text NOT NULL,
  variety text NOT NULL,
  source_id text NOT NULL REFERENCES amoxcalli.sources(source_id),
  source_file text NOT NULL,
  source_reference text NOT NULL,
  source_url text,
  source_confidence double precision,
  editorial_status text NOT NULL,
  speaker_validation_status text NOT NULL,
  classical_citation_form text,
  msn_headword text,
  ehn_spoken_form text,
  msn_poetic_form text,
  roots jsonb NOT NULL DEFAULT '[]'::jsonb,
  variants jsonb NOT NULL DEFAULT '[]'::jsonb,
  etymology text,
  original_payload jsonb NOT NULL,
  original_entry jsonb NOT NULL,
  source_references jsonb NOT NULL DEFAULT '[]'::jsonb,
  notes_public text,
  notes_internal text,
  search_text text NOT NULL,
  source_sha256 text NOT NULL,
  search_vector tsvector GENERATED ALWAYS AS
    (to_tsvector('simple'::regconfig, search_text)) STORED,
  imported_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS amoxcalli_lexicon_headword_idx
  ON amoxcalli.lexicon_entries (headword_folded);
CREATE INDEX IF NOT EXISTS amoxcalli_lexicon_headword_prefix_idx
  ON amoxcalli.lexicon_entries (headword_folded text_pattern_ops);
CREATE INDEX IF NOT EXISTS amoxcalli_lexicon_search_idx
  ON amoxcalli.lexicon_entries USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS amoxcalli_lexicon_source_idx
  ON amoxcalli.lexicon_entries (source_id);
CREATE INDEX IF NOT EXISTS amoxcalli_lexicon_register_idx
  ON amoxcalli.lexicon_entries (register);

CREATE TABLE IF NOT EXISTS amoxcalli.import_metadata (
  dataset_id text PRIMARY KEY,
  source_sha256 text NOT NULL,
  source_bytes bigint NOT NULL,
  entry_count integer NOT NULL,
  source_count integer NOT NULL,
  details jsonb NOT NULL,
  imported_at timestamptz NOT NULL DEFAULT now()
);
