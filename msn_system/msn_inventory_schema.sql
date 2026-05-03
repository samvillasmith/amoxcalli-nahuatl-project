-- Flor y Canto Nahuatl - MSN System Phase B schema
-- This schema documents the generated CSV shape and a future SQLite review layer.
-- It is not applied to the production lexicon in this phase.

CREATE TABLE IF NOT EXISTS msn_inventory (
    entry_id TEXT PRIMARY KEY,
    msn_headword TEXT,
    ehn_spoken_form TEXT,
    classical_citation_form TEXT,
    msn_poetic_form TEXT,
    part_of_speech TEXT,
    register TEXT NOT NULL,
    variety TEXT NOT NULL,
    gloss_en TEXT,
    gloss_es TEXT,
    root_family TEXT,
    root_family_code TEXT,
    source_id TEXT,
    source_file TEXT,
    source_reference TEXT,
    source_type TEXT,
    upstream_title TEXT,
    authority_domain TEXT,
    canonical_status TEXT,
    source_confidence REAL,
    speaker_validation_status TEXT,
    editorial_status TEXT,
    msn_review_status TEXT NOT NULL,
    msn_decision_basis TEXT,
    msn_notes TEXT
);

CREATE TABLE IF NOT EXISTS msn_review_queue (
    review_id TEXT PRIMARY KEY,
    entry_id TEXT NOT NULL,
    queue_reason TEXT NOT NULL,
    priority TEXT NOT NULL,
    proposed_msn_headword TEXT,
    current_register TEXT NOT NULL,
    current_variety TEXT NOT NULL,
    evidence_summary TEXT,
    recommended_action TEXT NOT NULL,
    source_id TEXT,
    source_file TEXT,
    source_reference TEXT,
    source_confidence REAL,
    editorial_status TEXT,
    speaker_validation_status TEXT,
    FOREIGN KEY (entry_id) REFERENCES msn_inventory(entry_id)
);

CREATE TABLE IF NOT EXISTS msn_example_bank (
    example_id TEXT PRIMARY KEY,
    source_family TEXT NOT NULL,
    source_register TEXT,
    target_register TEXT NOT NULL,
    nahuatl_text TEXT NOT NULL,
    morpheme_segmentation TEXT,
    gloss_line TEXT,
    translation_en TEXT,
    translation_es TEXT,
    operation TEXT,
    evidence_status TEXT NOT NULL,
    source_reference TEXT,
    editorial_note TEXT
);

CREATE TABLE IF NOT EXISTS msn_decision_log (
    decision_id TEXT PRIMARY KEY,
    entry_id TEXT NOT NULL,
    decision_date TEXT NOT NULL,
    reviewer TEXT,
    decision_status TEXT NOT NULL,
    approved_msn_headword TEXT,
    decision_basis TEXT NOT NULL,
    source_notes TEXT,
    public_notes TEXT,
    FOREIGN KEY (entry_id) REFERENCES msn_inventory(entry_id)
);
