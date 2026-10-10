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
const columns = `e.entry_id, e.original_headword,
  COALESCE(translated.definitions->>'fr', e.definition_fr) AS definition_fr,
  COALESCE(translated.definitions->>'en', e.definition_en) AS definition_en,
  COALESCE(translated.definitions->>'es', e.definition_es) AS definition_es,
  e.part_of_speech, e.source_id, e.variety, e.variants, e.roots, e.classical_citation_form,
  e.source_reference, e.source_url, e.editorial_status, e.msn_headword, e.msn_poetic_form,
  e.ehn_spoken_form, e.etymology, translated.metadata AS translation_metadata,
  NULLIF(trim(CASE WHEN e.source_id = 'FCN-SRC-SIMEON-PARSED'
    THEN e.definition_fr ELSE e.definition_en END), '') IS NULL AS source_definition_missing`;
const translationJoin = `LEFT JOIN LATERAL (
  SELECT jsonb_object_agg(t.language, t.definition) AS definitions,
    jsonb_object_agg(t.language, jsonb_build_object(
      'kind', t.kind, 'sourceLanguage', t.source_language, 'provider', t.provider,
      'model', t.model, 'status', t.status, 'sourceContentHash', t.source_content_sha256,
      'generatedAt', t.generated_at)) AS metadata
  FROM amoxcalli.entry_translations t WHERE t.entry_id = e.entry_id
    AND t.source_sha256 = e.source_sha256
) translated ON true`;

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
  const sourceLanguage = source === 'simeon' ? 'fr' : 'en';
  const translations = row.translation_metadata || {};
  if (row.source_definition_missing) {
    for (const language of ['fr', 'en', 'es']) {
      translations[language] ||= { kind: 'source_missing', sourceLanguage, provider: null, model: null, status: 'missing' };
    }
  } else {
    translations[sourceLanguage] ||= { kind: 'original', sourceLanguage, provider: null, model: null, status: 'source' };
  }
  return {
    id: row.entry_id,
    headword: row.original_headword,
    definitionFr: row.definition_fr,
    definitionEn: row.definition_en,
    definitionEs: row.definition_es,
    translations,
    sourceDefinitionMissing: row.source_definition_missing,
    sourceDefinitionUnclear: Object.values(translations).some((translation) => translation.kind === 'source_unclear'),
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
        const { rows } = await readOnlyQuery((client) => client.query(`SELECT corpus.entry_count, corpus.source_sha256,
          COALESCE(release.details->>'complete', 'false')::boolean AND
            release.source_sha256 = corpus.source_sha256 AS translations_ready,
          release.details->'languages' AS translation_coverage
          FROM amoxcalli.import_metadata corpus
          LEFT JOIN amoxcalli.import_metadata release ON release.dataset_id = 'lexicon_translations'
          WHERE corpus.dataset_id = $1`, ['master_lexicon']));
        if (!rows.length) return json({ error: 'The corpus is not ready.' }, 503);
        return json({ ready: true, entries: rows[0].entry_count, sha256: rows[0].source_sha256,
          translationsReady: Boolean(rows[0].translations_ready), translationCoverage: rows[0].translation_coverage,
          apiVersion: '2026-10-10.4' });
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
          OR e.search_vector @@ to_tsquery('simple', $4)
          OR e.entry_id IN (SELECT entry_id FROM amoxcalli.entry_translations
            WHERE search_vector @@ to_tsquery('simple', $4)
              AND source_sha256 = (SELECT source_sha256 FROM amoxcalli.import_metadata
                WHERE dataset_id = 'master_lexicon')))`;
      const [totalResult, result] = await readOnlyQuery(async (client) => {
        const totals = await client.query(`SELECT count(*)::int AS total FROM amoxcalli.lexicon_entries e WHERE ${filter}`, values.slice(0, 4));
        const entries = await client.query(`SELECT ${columns} FROM amoxcalli.lexicon_entries e ${translationJoin} WHERE ${filter}
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
