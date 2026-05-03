# MSN Authoring Pack

This pack turns the MSN Phase B seed into a practical drafting layer for short controlled books.

It is intentionally conservative. It supports internal drafting, not public release, until review and QA are complete.

## Generated Files

Run:

```powershell
python .\build_msn_authoring_pack.py
```

Outputs:

- `exports/msn_core_candidates.csv` - all 683 EHN_colloquial entries with proposed MSN written forms and risk flags.
- `exports/msn_authoring_lexicon_seed.csv` - deduplicated internal drafting lexicon from low-risk EHN candidates.
- `exports/msn_sentence_patterns.csv` - seed sentence-pattern templates for controlled prose.
- `exports/msn_genre_seed_plan.csv` - comparison of the first four book paths.
- `reports/msn_authoring_pack_summary.json` - verification counts.

## What Counts As Usable Here

For internal drafting, a form may be used when it is:

- sourced from `EHN_colloquial`
- high-confidence in the current lexicon
- not flagged as obsolete, alternate-only, bound-only, proper-name-only, or otherwise special-review
- given a proposed MSN written form from the orthography candidate layer or existing DB headword

For public release, that same form still needs:

- MSN editorial approval
- register check
- source note retained
- QA pass
- speaker/community validation where appropriate

## Recommended First Book Path

Start with a children's book. It has the lowest risk because it can use:

- short captions
- repeated sentence patterns
- concrete vocabulary
- primer-safe topics
- limited EHN dialogue if clearly marked

The cookbook is second. It needs a loanword and kitchen-term policy.

The mindfulness chapbook is third. It needs abstract vocabulary controls.

The Tloque Nahuaque devotional text is fourth. It should use MSN_public and MSN_poetic, and it needs a dedicated source/theology/register pack before drafting.

## Drafting Workflow

1. Choose a genre.
2. Build a small genre vocabulary from `msn_authoring_lexicon_seed.csv`.
3. Draft the book in English or Spanish first.
4. Map each sentence to a pattern in `msn_sentence_patterns.csv`.
5. Use only the genre vocabulary plus explicitly reviewed additions.
6. Put missing words into an unresolved list.
7. Create the controlled MSN draft.
8. Produce glossary and source notes.
9. Run QA for orthography, register purity, and source traceability.
10. Only then prepare the public manuscript.
