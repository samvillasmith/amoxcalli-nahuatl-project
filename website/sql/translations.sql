-- Translations are separate from the archival source records and payloads.
CREATE TABLE IF NOT EXISTS amoxcalli.entry_translations (
  entry_id text NOT NULL REFERENCES amoxcalli.lexicon_entries(entry_id),
  language text NOT NULL CHECK (language IN ('fr', 'en', 'es')),
  definition text,
  kind text NOT NULL CHECK (kind IN ('original', 'machine', 'source_missing', 'source_unclear')),
  source_language text NOT NULL CHECK (source_language IN ('fr', 'en')),
  source_content_sha256 text NOT NULL CHECK (source_content_sha256 ~ '^[A-Fa-f0-9]{64}$'),
  source_sha256 text NOT NULL,
  provider text,
  model text,
  status text NOT NULL CHECK (status IN ('source', 'unreviewed', 'missing', 'unclear')),
  generated_at timestamptz,
  search_text text NOT NULL DEFAULT '',
  search_vector tsvector GENERATED ALWAYS AS
    (to_tsvector('simple'::regconfig, search_text)) STORED,
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (entry_id, language),
  CHECK (
    (kind = 'source_missing' AND definition IS NULL AND status = 'missing') OR
    (kind = 'source_unclear' AND definition IS NOT NULL AND length(trim(definition)) > 0
      AND status = 'unclear' AND provider IS NULL AND model IS NULL AND generated_at IS NULL) OR
    (kind = 'original' AND definition IS NOT NULL AND length(trim(definition)) > 0 AND status = 'source') OR
    (kind = 'machine' AND definition IS NOT NULL AND length(trim(definition)) > 0 AND status = 'unreviewed'
      AND provider IS NOT NULL AND model IS NOT NULL AND generated_at IS NOT NULL
      AND length(trim(provider)) > 0 AND length(trim(model)) > 0)
  )
);

CREATE INDEX IF NOT EXISTS amoxcalli_translations_search_idx
  ON amoxcalli.entry_translations USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS amoxcalli_translations_language_idx
  ON amoxcalli.entry_translations (language, kind);
