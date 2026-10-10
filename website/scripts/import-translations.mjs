#!/usr/bin/env node
// Validate the complete translation release before updating the scoped tables.
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { createInterface } from 'node:readline';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseEnv } from 'node:util';
import pg from 'pg';

const languages = ['fr', 'en', 'es'];
const unreadableNotices = {
  en: 'The source definition is unreadable.',
  es: 'La definición de la fuente es ilegible.',
  fr: 'La définition de la source est illisible.',
};
const columns = [
  'entry_id', 'language', 'definition', 'kind', 'source_language',
  'source_content_sha256', 'source_sha256', 'provider', 'model', 'status',
  'generated_at', 'search_text',
];

export function contentHash(text) {
  return createHash('sha256').update(text || '', 'utf8').digest('hex');
}

export function fold(text) {
  return (text || '').normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
}

function options(args) {
  const result = { schema: fileURLToPath(new URL('../sql/translations.sql', import.meta.url)) };
  for (let index = 0; index < args.length; index++) {
    const flag = args[index];
    if (['--allow-partial', '--validate-only'].includes(flag)) {
      result[flag.slice(2)] = true;
    } else if (['--file', '--env', '--schema'].includes(flag) && args[index + 1]) {
      result[flag.slice(2)] = resolve(args[++index]);
    } else {
      throw new Error('Usage: import-translations.mjs --file release.jsonl [--env .env] [--schema translations.sql] [--validate-only] [--allow-partial]');
    }
  }
  if (!result.file) throw new Error('--file is required.');
  return result;
}

async function* records(file) {
  const stream = createReadStream(file, { encoding: 'utf8' });
  const lines = createInterface({ input: stream, crlfDelay: Infinity });
  let number = 0;
  try {
    for await (const line of lines) {
      number++;
      if (!line.trim()) continue;
      let record;
      try { record = JSON.parse(line); }
      catch { throw new Error(`Invalid translation JSON at line ${number}.`); }
      yield record;
    }
  } finally {
    lines.close();
    stream.destroy();
  }
}

export function validateTranslationRecord(record, source) {
  if (!source) throw new Error(`Unknown entry ID: ${record.entry_id}.`);
  if (!languages.includes(record.language)) throw new Error(`Unsupported language for ${record.entry_id}.`);
  if (record.source_language !== source.language) throw new Error(`Original language mismatch for ${record.entry_id}.`);
  if (String(record.source_content_sha256).toLowerCase() !== source.hash) throw new Error(`Original content hash mismatch for ${record.entry_id}.`);
  const missing = !source.definition || !source.definition.trim();
  if (missing) {
    if (record.kind !== 'source_missing' || record.status !== 'missing' || record.definition !== null) {
      throw new Error(`A missing source definition must stay missing for ${record.entry_id}.`);
    }
  } else if (record.language === source.language) {
    if (record.kind !== 'original' || record.status !== 'source' || record.definition !== source.definition) {
      throw new Error(`Original source text must remain exact for ${record.entry_id}.`);
    }
  } else if (!/\p{L}/u.test(source.definition)) {
    if (record.kind !== 'source_unclear' || record.status !== 'unclear' ||
      record.definition !== unreadableNotices[record.language] ||
      record.provider !== null || record.model !== null || record.generated_at !== null) {
      throw new Error(`Unreadable source must have a localized notice for ${record.entry_id}/${record.language}.`);
    }
  } else if (
    record.kind !== 'machine' || record.status !== 'unreviewed' ||
    typeof record.definition !== 'string' || !record.definition.trim() ||
    typeof record.provider !== 'string' || !record.provider.trim() ||
    typeof record.model !== 'string' || !record.model.trim() ||
    typeof record.generated_at !== 'string' || !Number.isFinite(Date.parse(record.generated_at))
  ) {
    throw new Error(`Translation text or machine provenance is missing for ${record.entry_id}/${record.language}.`);
  }
  return record;
}

async function validate(file, sources, corpus, allowPartial) {
  let metadata;
  const digest = createHash('sha256');
  const keys = new Set();
  const counts = { fr: 0, en: 0, es: 0 };
  const kinds = { original: 0, machine: 0, source_missing: 0, source_unclear: 0 };
  for await (const { type, data } of records(file)) {
    digest.update(JSON.stringify({ type, data }) + '\n');
    if (type === 'metadata') {
      if (metadata || keys.size) throw new Error('Translation metadata must appear first and only once.');
      metadata = data;
      if (metadata.export_version !== 1 || metadata.dataset_id !== 'lexicon_translations') throw new Error('Unsupported translation export.');
      if (metadata.source_sha256?.toUpperCase() !== corpus.source_sha256?.toUpperCase()) throw new Error('Translation release belongs to a different SQLite archive.');
      if (metadata.entry_count !== sources.size) throw new Error('Translation corpus entry count differs from the database.');
      if (!Array.isArray(metadata.languages) || languages.some((language) => !metadata.languages.includes(language)) || metadata.languages.length !== 3) throw new Error('Translation release must declare French, English and Spanish.');
    } else if (type === 'translation' && metadata) {
      validateTranslationRecord(data, sources.get(data.entry_id));
      const key = `${data.entry_id}/${data.language}`;
      if (keys.has(key)) throw new Error(`Duplicate translation cell: ${key}.`);
      keys.add(key);
      counts[data.language]++;
      kinds[data.kind]++;
    } else {
      throw new Error('Unknown translation record or missing first metadata record.');
    }
  }
  if (!metadata || metadata.record_count !== keys.size) throw new Error('Translation record count differs from release metadata.');
  const complete = keys.size === sources.size * 3 && languages.every((language) => counts[language] === sources.size);
  if (!complete && !allowPartial) throw new Error('Full French/English/Spanish coverage is required. Use --allow-partial only for an isolated preview branch.');
  return { metadata, counts, kinds, complete, records: keys.size, fileHash: digest.digest('hex') };
}

async function upsert(client, rows) {
  if (!rows.length) return;
  const values = [];
  const placeholders = rows.map((row) => '(' + columns.map((column) => {
    values.push(row[column] ?? null);
    return `$${values.length}`;
  }).join(', ') + ')');
  const assignments = columns.filter((column) => !['entry_id', 'language'].includes(column)).map((column) => `${column} = EXCLUDED.${column}`);
  await client.query(
    `INSERT INTO amoxcalli.entry_translations (${columns.join(', ')}) VALUES ${placeholders.join(', ')}
     ON CONFLICT (entry_id, language) DO UPDATE SET ${assignments.join(', ')}, updated_at = now()`,
    values,
  );
}

async function main() {
  const args = options(process.argv.slice(2));
  // An explicitly chosen preview env must never fall back to another branch.
  const environment = args.env ? parseEnv(await readFile(args.env, 'utf8')) : process.env;
  const connectionString = environment.DATABASE_URL_UNPOOLED || environment.DATABASE_URL;
  if (!connectionString) throw new Error('Set DATABASE_URL_UNPOOLED or DATABASE_URL privately.');
  const databaseUrl = new URL(connectionString);
  databaseUrl.searchParams.set('sslmode', 'verify-full');
  databaseUrl.searchParams.delete('options');
  const pool = new pg.Pool({ connectionString: databaseUrl.href, max: 1, connectionTimeoutMillis: 30000, options: '' });
  let client;
  try {
    client = await pool.connect();
    const { rows: metadataRows } = await client.query("SELECT entry_count, source_sha256 FROM amoxcalli.import_metadata WHERE dataset_id = 'master_lexicon'");
    if (metadataRows.length !== 1) throw new Error('Import the archival master corpus first.');
    const corpus = metadataRows[0];
    const { rows: entries } = await client.query('SELECT entry_id, source_id, definition_fr, definition_en FROM amoxcalli.lexicon_entries');
    if (entries.length !== corpus.entry_count) throw new Error('Master corpus count does not match its fingerprint metadata.');
    const sources = new Map(entries.map((entry) => {
      const language = entry.source_id === 'FCN-SRC-SIMEON-PARSED' ? 'fr' : 'en';
      const definition = entry[`definition_${language}`] || '';
      return [entry.entry_id, { language, definition, hash: contentHash(definition) }];
    }));
    const release = await validate(args.file, sources, corpus, args['allow-partial']);
    const summary = {
      records: release.records,
      entries: sources.size,
      languages: release.counts,
      kinds: release.kinds,
      complete: release.complete,
      source_sha256: corpus.source_sha256,
    };
    if (args['validate-only']) {
      console.log(JSON.stringify({ validated: true, ...summary }, null, 2));
      return;
    }
    await client.query('BEGIN');
    await client.query(await readFile(args.schema, 'utf8'));
    let batch = [];
    const importedDigest = createHash('sha256');
    for await (const { type, data } of records(args.file)) {
      importedDigest.update(JSON.stringify({ type, data }) + '\n');
      if (type !== 'translation') continue;
      batch.push({ ...data, source_sha256: corpus.source_sha256, source_content_sha256: data.source_content_sha256.toLowerCase(),
        search_text: ['original', 'machine'].includes(data.kind) ? fold(data.definition) : '' });
      if (batch.length === 200) {
        await upsert(client, batch);
        batch = [];
      }
    }
    await upsert(client, batch);
    if (importedDigest.digest('hex') !== release.fileHash) {
      throw new Error('Translation release changed after validation; the transaction was rolled back.');
    }
    const { rows: coverage } = await client.query(
      `SELECT language, count(*)::int AS records FROM amoxcalli.entry_translations
       WHERE source_sha256 = $1 GROUP BY language`, [corpus.source_sha256],
    );
    const actual = Object.fromEntries(coverage.map((row) => [row.language, row.records]));
    if (!args['allow-partial'] && languages.some((language) => actual[language] !== sources.size)) {
      throw new Error('Persisted translations do not cover the complete corpus.');
    }
    await client.query(
      `INSERT INTO amoxcalli.import_metadata (dataset_id, source_sha256, source_bytes, entry_count, source_count, details)
       SELECT 'lexicon_translations', source_sha256, source_bytes, entry_count, source_count, $1::jsonb
       FROM amoxcalli.import_metadata WHERE dataset_id = 'master_lexicon'
       ON CONFLICT (dataset_id) DO UPDATE SET source_sha256 = EXCLUDED.source_sha256,
       source_bytes = EXCLUDED.source_bytes, entry_count = EXCLUDED.entry_count,
       source_count = EXCLUDED.source_count, details = EXCLUDED.details, imported_at = now()`,
      [JSON.stringify({ ...release.metadata, ...summary })],
    );
    await client.query('COMMIT');
    console.log(JSON.stringify({ imported: true, ...summary }, null, 2));
  } catch (error) {
    if (client) await client.query('ROLLBACK').catch(() => {});
    throw error;
  } finally {
    client?.release();
    await pool.end();
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    const safeMessage = String(error.message).replace(/postgres(?:ql)?:\/\/\S+/gi, '[database connection]');
    console.error(`Translation import failed: ${safeMessage}`);
    process.exitCode = 1;
  });
}
