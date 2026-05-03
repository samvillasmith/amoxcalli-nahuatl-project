# Database Artifacts

Oversized SQLite databases are external release artifacts. They should live in S3, not in Git.

Public base URL:

```text
https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/
```

S3 prefix:

```text
s3://nahuatl-language/molina/databases/
```

Upload helper:

```powershell
.\scripts\upload_database_artifacts.ps1
```

The helper requires AWS credentials with write access to `s3://nahuatl-language/molina/databases/`.

## Canonical Artifacts

| Artifact | Local source | Bytes | SHA-256 | Public URL |
|---|---:|---:|---|---|
| `fcn_master_lexicon.sqlite` | `lexicon_bootstrap/fcn_master_lexicon.sqlite` | 104222720 | `A154749AE34D9FF21B65C2AFB12133755563CC89FC8DCB2EBA293457E37C7BE2` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon.sqlite> |
| `fcn_master_lexicon_phase6_review.sqlite` | `orthography/fcn_master_lexicon_phase6_review.sqlite` | 104378368 | `E07EEE83383C7BDF05B645FBDE33CEFB3A19E574FDD3CC4B9BDDBB66C4D6F6D2` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase6_review.sqlite> |
| `fcn_master_lexicon_phase7_review.sqlite` | `core_vocabulary/fcn_master_lexicon_phase7_review (1).sqlite` | 105082880 | `322B7621C6CC506C485F99F4EF96FE2564DA3CCA332AB6ABF93C3061E20FC655` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase7_review.sqlite> |
| `fcn_master_lexicon_phase8_bootstrap.sqlite` | `curriculum/fcn_master_lexicon_phase8_bootstrap.sqlite` | 104312832 | `D6DD4E380D1EDA3758D04471FE99C8A539BF7CCE454EF078EAEDD17318C69787` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_bootstrap.sqlite> |
| `fcn_master_lexicon_phase8_open_only.sqlite` | `curriculum/fcn_master_lexicon_phase8_open_only.sqlite` | 106717184 | `FD5BE61B8BEDD3E55772ECACC000BFF29EFEB5BD9E9FA78F8B8112BB67310DEB` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_open_only.sqlite> |
| `fcn_master_lexicon_phase8_1_clean.sqlite` | `curriculum/fcn_master_lexicon_phase8_1_clean.sqlite` | 106766336 | `B79EB92A97A76D91D612E37A5036502F85DD55FA0F6BCE8A76D8BA818E506D35` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_1_clean.sqlite> |
| `fcn_master_lexicon_phase8_2_units.sqlite` | `curriculum/fcn_master_lexicon_phase8_2_units.sqlite` | 107016192 | `B266E12A74E0D3386934967053A0E3660352BF0DE3B32559E48ECF5FFF5863A4` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_2_units.sqlite> |
| `fcn_master_lexicon_phase8_3_exports.sqlite` | `curriculum/fcn_master_lexicon_phase8_3_exports.sqlite` | 107036672 | `F3F41FB0E2B1E7C8BDF99BE8319E416910FC75F3265573BFB3F75A93B5FFA4BF` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_3_exports.sqlite> |
| `fcn_master_lexicon_phase8_4_assessment.sqlite` | `curriculum/fcn_master_lexicon_phase8_4_assessment.sqlite` | 107061248 | `C1C7B6B23D8E4E4E66140A679CE2108E6A4F96E333836569C5AC670BD0D8D7B9` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_4_assessment.sqlite> |
| `fcn_master_lexicon_phase8_5_products.sqlite` | `curriculum/fcn_master_lexicon_phase8_5_products.sqlite` | 107061248 | `C1C7B6B23D8E4E4E66140A679CE2108E6A4F96E333836569C5AC670BD0D8D7B9` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_5_products.sqlite> |
| `fcn_master_lexicon_phase8_6_primer.sqlite` | `curriculum/fcn_master_lexicon_phase8_6_primer.sqlite` | 107200512 | `15D29FDFDDDE5FC623788B1382B6CBC4BD2537165BF9F32F66E0512CBA7C17D8` | <https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite> |

## Notes

- `curriculum/fcn_master_lexicon_phase8_6_primer.sqlite` is the canonical production database.
- The top-level `fcn_master_lexicon_phase8_6_primer.sqlite` is excluded from this manifest because it has a different hash than the canonical curriculum copy and appears to be a stale duplicate.
- New `.sqlite`, `.sqlite3`, `.db`, `*.sqlite-wal`, and `*.sqlite-shm` files are ignored by Git. Keep database binaries in S3 and commit source code, manifests, reports, and generated CSV/JSON exports to Git.
- Legacy tracked SQLite files should be removed from Git after their S3 uploads are confirmed.
