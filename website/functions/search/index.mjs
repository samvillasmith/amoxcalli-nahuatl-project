import pg from 'pg';
import { timingSafeEqual } from 'node:crypto';
import { attachDatabasePool } from '@neon/functions';

const secret = process.env.AMOXCALLI_ORIGIN_SECRET;
if (!secret || !process.env.DATABASE_URL) throw new Error('Search service configuration is missing.');
const expectedSecret = Buffer.from(secret);
const databaseUrl = new URL(process.env.DATABASE_URL);
databaseUrl.searchParams.set('sslmode', 'verify-full');
databaseUrl.searchParams.delete('options');
const pool = new pg.Pool({
  connectionString: databaseUrl.href,
  max: 5,
  connectionTimeoutMillis: 10000,
  idleTimeoutMillis: 30000,
  query_timeout: 10000,
  options: '',
});
attachDatabasePool(pool);

async function readOnlyQuery(work) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN READ ONLY');
    await client.query("SET LOCAL statement_timeout = '8s'");
    const result = await work(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK').catch(() => {});
    throw error;
  } finally {
    client.release();
  }
}

const sourceIds = {
  simeon: 'FCN-SRC-SIMEON-PARSED',
  kaikki: 'FCN-SRC-KAIKKI-UNIFIED',
};
const columns = `entry_id, original_headword, definition_fr, definition_en, definition_es,
  part_of_speech, source_id, variety, variants, roots, classical_citation_form,
  source_reference, source_url, editorial_status, msn_headword, msn_poetic_form,
  ehn_spoken_form, etymology`;

export function fold(text) {
  return text.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
}

function authorized(request) {
  const header = request.headers.get('x-secret');
  if (!header) return false;
  const provided = Buffer.from(header);
  return provided.length === expectedSecret.length && timingSafeEqual(provided, expectedSecret);
}

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: {
      'Cache-Control': status === 200 ? 'public, max-age=60' : 'no-store',
      'X-Content-Type-Options': 'nosniff',
    },
  });
}

function entry(row) {
  const source = row.source_id === sourceIds.simeon ? 'simeon' : 'kaikki';
  return {
    id: row.entry_id,
    headword: row.original_headword,
    definitionFr: row.definition_fr,
    definitionEn: row.definition_en,
    definitionEs: row.definition_es,
    pos: row.part_of_speech,
    source,
    sourceLabel: source === 'simeon' ? 'Siméon · 1885' : 'Wiktionary / Kaikki',
    variety: row.variety,
    variants: [...new Set(row.variants.flatMap((v) => [v.form_text, v.raw_form, v.normalized_form]).filter(Boolean))],
    roots: row.roots,
    citation: row.classical_citation_form,
    sourceReference: row.source_reference,
    sourceUrl: row.source_url,
    status: row.editorial_status,
    etymology: row.etymology,
    msn: { headword: row.msn_headword, poeticForm: row.msn_poetic_form, spokenForm: row.ehn_spoken_form },
  };
}

function integer(value, fallback, maximum) {
  if (value === null) return fallback;
  if (!/^\d+$/.test(value)) throw new Error('Pagination must use whole positive numbers.');
  const n = Number(value);
  if (!Number.isSafeInteger(n) || n > maximum) throw new Error('Pagination is outside the supported range.');
  return n;
}

export default {
  async fetch(request) {
    if (!authorized(request)) return json({ error: 'Unauthorized origin.' }, 401);
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return new Response(null, { status: 405, headers: { Allow: 'GET, HEAD' } });
    }
    const url = new URL(request.url);
    if (!['/', '/search', '/api/search', '/health', '/api/health'].includes(url.pathname)) {
      return json({ error: 'Endpoint not found.' }, 404);
    }
    try {
      if (url.pathname.endsWith('/health')) {
        const { rows } = await readOnlyQuery((client) => client.query('SELECT entry_count, source_sha256 FROM amoxcalli.import_metadata WHERE dataset_id = $1', ['master_lexicon']));
        if (!rows.length) return json({ error: 'The corpus is not ready.' }, 503);
        return json({ ready: true, entries: rows[0].entry_count, sha256: rows[0].source_sha256, apiVersion: '2026-10-10.3' });
      }
      const q = (url.searchParams.get('q') || '').trim();
      if (q.length > 200) return json({ error: 'Please search with 200 characters or fewer.' }, 400);
      const source = url.searchParams.get('source') || 'all';
      if (!['all', 'simeon', 'kaikki'].includes(source)) return json({ error: 'Unknown dictionary source.' }, 400);
      let offset, limit;
      try {
        offset = integer(url.searchParams.get('offset'), 0, 100000);
        limit = integer(url.searchParams.get('limit'), 20, 50);
        if (!limit) throw new Error('Page size must be at least one.');
      } catch (error) {
        return json({ error: error.message }, 400);
      }
      const term = fold(q);
      const escaped = term.replace(/[\\%_]/g, '\\$&');
      const words = term.match(/[\p{L}\p{N}]+/gu) || [];
      const fullTextQuery = words.map((word) => `'${word}':*`).join(' & ');
      const values = [source === 'all' ? null : sourceIds[source], term, `%${escaped}%`, fullTextQuery, `${escaped}%`];
      const filter = `($1::text IS NULL OR source_id = $1)
        AND ($2 = '' OR headword_search LIKE $3
          OR search_vector @@ to_tsquery('simple', $4))`;
      const [totalResult, result] = await readOnlyQuery(async (client) => {
        const totals = await client.query(`SELECT count(*)::int AS total FROM amoxcalli.lexicon_entries WHERE ${filter}`, values.slice(0, 4));
        const entries = await client.query(`SELECT ${columns} FROM amoxcalli.lexicon_entries WHERE ${filter}
          ORDER BY CASE WHEN $2 = '' THEN 0 WHEN headword_folded = $2 THEN 0
            WHEN headword_folded LIKE $5 THEN 1 WHEN headword_search LIKE $3 THEN 2 ELSE 3 END,
            CASE WHEN $2 = '' AND source_id <> 'FCN-SRC-SIMEON-PARSED' THEN 1 ELSE 0 END,
            headword_folded, CASE WHEN source_id = 'FCN-SRC-SIMEON-PARSED' THEN 0 ELSE 1 END, entry_id
          LIMIT $6 OFFSET $7`, [...values, limit, offset]);
        return [totals, entries];
      });
      const body = { total: totalResult.rows[0].total, limit, offset, entries: result.rows.map(entry) };
      if (request.method === 'HEAD') return new Response(null, { headers: { 'Cache-Control': 'public, max-age=60' } });
      return json(body);
    } catch (error) {
      const safeMessage = String(error.message).replace(/postgres(?:ql)?:\/\/\S+/gi, '[database connection]').replaceAll(secret, '[private credential]');
      console.error('Lexicon query failed', { code: error.code || 'query_error', message: safeMessage.slice(0, 300) });
      return json({ error: 'Search is temporarily unavailable. Please try again.' }, 503);
    }
  },
};
