# Amoxcalli searchable lexicon

The public homepage at https://amoxcalli.org centers the open lexical archive. It searches 37,146 source records: 28,709 entries parsed from Rémi Siméon's 1885 dictionary and 8,437 unique Wiktionary/Kaikki records. The original homepage, all MSN sections, bilingual copy, document viewer, and six supporting documents remain at https://amoxcalli.org/msn/.

Original spellings and French definitions are retained, alongside available English source glosses, variants, roots, source references, and review status. Search folds case and accents without changing the displayed text. Entries are not deduplicated by headword. The archive retains OCR and parsing imperfections; no machine translations are presented as originals.

The site describes this project's open, structured corpus without claiming that Siméon was first digitized here. Earlier electronic editions include Alexis Wimmer's 2004 dictionary and UNAM's Gran Diccionario Náhuatl. The original scan is credited to its existing Internet Archive source.

## Hosting

- Static website: existing S3 bucket `fcn-nahuatl-website` and CloudFront distribution `E1XNT9YCJ5QMJJ`.
- Database: supplied Neon project `wandering-darkness-49205760`, production branch `br-broad-dawn-b5l34egl`, region `aws-us-east-2`.
- Search: Neon Function `lexiconsearch`, reached through the existing site's `/api/search` CloudFront behavior.
- Data tables: `amoxcalli.lexicon_entries`, `amoxcalli.sources`, and `amoxcalli.import_metadata`. Existing tables outside this schema are untouched.
- Public database download: the existing verified SQLite release remains in S3.

Search runs parameterized, time-limited read-only transactions. CloudFront supplies the private origin credential; browsers receive no database connection string or origin credential. AWS managed policies forward query strings and disable edge caching for the API, preserving the existing Free hosting plan. Secrets and generated corpus exports are excluded from Git and website uploads.

## Neon setup changes

The setup was performed in the calling workspace, above this checkout. The exact skill at https://neon.com/.well-known/agent-skills/neon/SKILL.md was fetched and checked against the installed copy.

1. Installed the global Neon CLI, version 8.3.5, and authenticated its `DEFAULT` profile using the user's completed browser sign-in.
2. Installed eight project skills under `.agents/skills`: `neon`, `neon-ai-gateway`, `neon-auth`, `neon-functions`, `neon-object-storage`, `neon-postgres`, `neon-postgres-branches`, and `neon-postgres-egress-optimizer`.
3. Ran the requested `neon mcp -y`. The installer added the Neon MCP server to existing Claude Code, Codex, Cursor, GitHub Copilot CLI, and VS Code configurations and minted its MCP API key. Credential values are not included in this repository.
4. Created `.neon` pointing to the supplied project and production branch. The current project name reported by Neon is `amoxcalli`; no project or branch was renamed.
5. Created a private `.env.local` with `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, and `NEON_BRANCH`. Added `AMOXCALLI_ORIGIN_SECRET` for the server-to-server search route, preserving existing values.
6. Created root `package.json` and `package-lock.json` with `@neon/config`, `@neon/env`, `@neon/functions`, and `pg`. The versioned website package lists the same dependencies.
7. Replaced only the newly generated root scaffold with the user's requested `defineConfig({})`, reviewed its plan, and ran `neon deploy`. The root configuration remains empty. It caused no changes to existing Neon services.
8. Added the separate versioned `website/neon.ts` policy for the search function. Existing authentication, object storage, branch settings, and other service configuration are preserved.
9. Added ignore rules for local Neon context, environment files, dependencies, generated search exports, and deployment state.
10. Tested the migration and search on a temporary child branch before importing the same verified corpus into production, then removed that test branch. The production context remained selected throughout.
11. Added the public `/api/*` origin and behavior to the existing CloudFront distribution, preserving its static origin, aliases, certificate, other settings, and Free pricing plan. Two temporary custom policies created during setup were removed after switching to supported AWS managed policies.
12. Published the new homepage, search assets, and preserved MSN site to the existing S3 bucket without deleting existing files. Saved private distribution backups and completed a cache invalidation.

## Rebuild and deploy

Install this package's dependencies with `npm install`. Link the supplied project if the working directory is not already linked. Keep private connection strings and `AMOXCALLI_ORIGIN_SECRET` in the ignored environment file; preserve existing values.

Export the verified archive from the repository root:

```powershell
python website/scripts/export-lexicon.py --out database/lexicon-search.jsonl
node website/scripts/import-lexicon.mjs --file database/lexicon-search.jsonl --env ..\.env.local
```

The exporter opens SQLite read-only and retains every original lexical record, original payload, 44,900 variants, and 74,292 source references. The importer validates the source fingerprint and counts before applying an additive migration and transactional upserts confined to `amoxcalli`.

Deploy the search from the linked workspace:

```powershell
neon config plan --config .\amoxcalli-nahuatl-project\website\neon.ts --env .env.local
neon deploy --config .\amoxcalli-nahuatl-project\website\neon.ts --env .env.local --no-env-pull
```

Publish the website from that workspace, using the function URL returned by Neon:

```powershell
python -B .\amoxcalli-nahuatl-project\website\scripts\deploy-site.py --site .\amoxcalli-nahuatl-project\website --function-url https://br-broad-dawn-b5l34egl-lexiconsearch.compute.c-7.us-east-2.aws.neon.tech/ --env .env.local --dry-run
```

After reviewing the dry run, omit `--dry-run` to publish. The script uploads only public files, preserves unrelated CloudFront settings and existing S3 assets, backs up the previous distribution configuration in ignored `.deployment-state`, and invalidates the site cache. It never uploads scripts, SQL, function code, environment files, or credentials, and never deletes existing site assets.

## Verification

Validated archive integrity and exact source counts; all original entry records and payloads; case and accent folding; headword and French/English definition search; source filters; pagination; empty states; invalid parameters; and private origin enforcement. Browser checks cover full Siméon definitions, provenance, the separate MSN site, and mobile layout. Public deployment checks verify the corpus and both source filters through the site's own API.
