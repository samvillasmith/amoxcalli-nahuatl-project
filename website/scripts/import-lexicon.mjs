#!/usr/bin/env node
// Import only the dedicated amoxcalli schema. Connection credentials stay private.
import { createReadStream } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import pg from 'pg';

const entryColumns = [
  'entry_id', 'original_headword', 'headword_folded', 'headword_search',
  'definition_fr', 'definition_en', 'definition_es', 'part_of_speech', 'register',
  'variety', 'source_id', 'source_file', 'source_reference', 'source_url',
  'source_confidence', 'editorial_status', 'speaker_validation_status',
  'classical_citation_form', 'msn_headword', 'ehn_spoken_form', 'msn_poetic_form',
  'roots', 'variants', 'etymology', 'original_payload', 'original_entry',
  'source_references', 'notes_public', 'notes_internal', 'search_text', 'source_sha256',
];
const sourceColumns = [
  'source_id', 'source_file', 'upstream_title', 'source_type', 'license',
  'source_url', 'original_metadata',
];
const jsonColumns = new Set([
  'roots', 'variants', 'original_payload', 'original_entry', 'source_references', 'original_metadata',
]);

function parseArguments(args) {
  const parsed = { schema: fileURLToPath(new URL('../sql/schema.sql', import.meta.url)) };
  for (let i = 0; i < args.length; i += 2) {
    const flag = args[i];
    if (!['--file', '--schema', '--env'].includes(flag) || !args[i + 1]) {
      throw new Error('Usage: node import-lexicon.mjs --file export.jsonl [--schema schema.sql] [--env .env]');
    }
    parsed[flag.slice(2)] = resolve(args[i + 1]);
  }
  if (!parsed.file) throw new Error('--file is required.');
  return parsed;
}

async function* records(file) {
  const stream = createReadStream(file, { encoding: 'utf8' });
  const lines = createInterface({ input: stream, crlfDelay: Infinity });
  let lineNumber = 0;
  try {
    for await (const line of lines) {
      lineNumber += 1;
      if (!line.trim()) continue;
      try {
        yield JSON.parse(line);
      } catch {
        throw new Error(`Invalid JSON at export line ${lineNumber}.`);
      }
    }
  } finally {
    lines.close();
    stream.destroy();
  }
}

async function validateExport(file) {
  let metadata;
  const sourceIds = new Set();
  const entryIds = new Set();
  const countsBySource = {};
  for await (const { type, data } of records(file)) {
    if (!data || typeof data !== 'object') throw new Error('Export record data is missing.');
    if (type === 'metadata') {
      if (metadata || sourceIds.size || entryIds.size) throw new Error('Metadata must be the first and only metadata record.');
      metadata = data;
      if (data.export_version !== 1 || !/^[A-Fa-f0-9]{64}$/.test(data.source_sha256)) throw new Error('Unsupported export or invalid source fingerprint.');
    } else if (type === 'source') {
      if (!metadata || entryIds.size || !data.source_id || sourceIds.has(data.source_id)) throw new Error('Source records must be unique and precede entries.');
      sourceIds.add(data.source_id);
    } else if (type === 'entry') {
      if (!metadata || !data.entry_id || entryIds.has(data.entry_id)) throw new Error('Missing or duplicate lexical entry identifier.');
      if (!sourceIds.has(data.source_id)) throw new Error(`Missing source for ${data.entry_id}.`);
      if (data.source_sha256 !== metadata.source_sha256) throw new Error(`Source fingerprint mismatch for ${data.entry_id}.`);
      if (!data.original_headword || !data.original_payload || !data.original_entry) throw new Error(`Missing original content for ${data.entry_id}.`);
      entryIds.add(data.entry_id);
      countsBySource[data.source_id] = (countsBySource[data.source_id] || 0) + 1;
    } else {
      throw new Error('Unknown export record type.');
    }
  }
  if (!metadata || metadata.entry_count !== entryIds.size || metadata.source_count !== sourceIds.size) throw new Error('Export record counts do not match metadata.');
  for (const [source, count] of Object.entries(metadata.entry_counts_by_source)) {
    if (countsBySource[source] !== count) throw new Error(`Source entry count mismatch for ${source}.`);
  }
  return { metadata, countsBySource };
}

async function upsert(client, table, columns, key, batch) {
  if (!batch.length) return;
  const values = [];
  const placeholders = batch.map((record) => '(' + columns.map((column) => {
    const value = record[column] ?? null;
    values.push(jsonColumns.has(column) && value !== null ? JSON.stringify(value) : value);
    return `$${values.length}`;
  }).join(', ') + ')');
  const assignments = columns.filter((column) => column !== key).map((column) => `${column} = EXCLUDED.${column}`);
  if (table === 'lexicon_entries') assignments.push('imported_at = now()');
  await client.query(
    `INSERT INTO amoxcalli.${table} (${columns.join(', ')}) VALUES ${placeholders.join(', ')}
     ON CONFLICT (${key}) DO UPDATE SET ${assignments.join(', ')}`,
    values,
  );
}

async function main() {
  const args = parseArguments(process.argv.slice(2));
  if (args.env) process.loadEnvFile(args.env);
  const connectionString = process.env.DATABASE_URL_UNPOOLED || process.env.DATABASE_URL;
  if (!connectionString) throw new Error('Set DATABASE_URL_UNPOOLED or DATABASE_URL in the environment or --env file.');
  const { metadata } = await validateExport(args.file);
  const schema = await readFile(args.schema, 'utf8');
  const pool = new pg.Pool({ connectionString, max: 1, connectionTimeoutMillis: 30000 });
  let client;
  try {
    client = await pool.connect();
    await client.query('BEGIN');
    await client.query(schema);
    let batch = [];
    for await (const { type, data } of records(args.file)) {
      if (type === 'source') {
        await upsert(client, 'sources', sourceColumns, 'source_id', [data]);
      } else if (type === 'entry') {
        batch.push(data);
        if (batch.length === 200) {
          await upsert(client, 'lexicon_entries', entryColumns, 'entry_id', batch);
          batch = [];
        }
      }
    }
    await upsert(client, 'lexicon_entries', entryColumns, 'entry_id', batch);
    const result = await client.query(
      'SELECT count(*)::int AS total, count(*) FILTER (WHERE source_sha256 = $1)::int AS matching FROM amoxcalli.lexicon_entries',
      [metadata.source_sha256],
    );
    if (result.rows[0].total !== metadata.entry_count || result.rows[0].matching !== metadata.entry_count) {
      throw new Error('Imported entry count does not match this source archive. The transaction was rolled back.');
    }
    await client.query(
      `INSERT INTO amoxcalli.import_metadata (dataset_id, source_sha256, source_bytes, entry_count, source_count, details)
       VALUES ($1, $2, $3, $4, $5, $6::jsonb)
       ON CONFLICT (dataset_id) DO UPDATE SET source_sha256 = EXCLUDED.source_sha256,
       source_bytes = EXCLUDED.source_bytes, entry_count = EXCLUDED.entry_count,
       source_count = EXCLUDED.source_count, details = EXCLUDED.details, imported_at = now()`,
      [metadata.dataset_id, metadata.source_sha256, metadata.source_bytes, metadata.entry_count, metadata.source_count, JSON.stringify(metadata)],
    );
    await client.query('COMMIT');
    console.log(JSON.stringify({
      imported_entries: metadata.entry_count,
      imported_sources: metadata.source_count,
      counts_by_source: metadata.entry_counts_by_source,
      source_sha256: metadata.source_sha256,
      schema: 'amoxcalli',
    }, null, 2));
  } catch (error) {
    if (client) await client.query('ROLLBACK').catch(() => {});
    throw error;
  } finally {
    client?.release();
    await pool.end();
  }
}

main().catch((error) => {
  // Avoid printing connection strings or database detail that can contain secrets.
  const safeMessage = error.message.replace(/postgres(?:ql)?:\/\/\S+/gi, '[database connection]');
  console.error(`Lexicon import failed: ${safeMessage}`);
  process.exitCode = 1;
});
