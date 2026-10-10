import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { readFileSync } from 'node:fs';
import { parseEnv } from 'node:util';
import { resolve, relative, extname } from 'node:path';

const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) options[args[i].replace(/^--/, '')] = args[i + 1];
const site = resolve(options.site || '.');
const env = parseEnv(readFileSync(options.env, 'utf8'));
const origin = new URL(options['function-url']);
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.md': 'text/markdown', '.svg': 'image/svg+xml' };
createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://127.0.0.1:5173');
    if (url.pathname.startsWith('/api/')) {
      if (!['/api/search', '/api/health'].includes(url.pathname)) { response.writeHead(404).end(); return; }
      const upstream = new URL(url.pathname + url.search, origin);
      const result = await fetch(upstream, { headers: { 'x-secret': env.AMOXCALLI_ORIGIN_SECRET }, redirect: 'manual' });
      response.writeHead(result.status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
      response.end(Buffer.from(await result.arrayBuffer()));
      return;
    }
    const path = decodeURIComponent(url.pathname).replace(/^\/+/, '') || 'index.html';
    const file = resolve(site, path.endsWith('/') ? path + 'index.html' : path);
    if (relative(site, file).startsWith('..')) { response.writeHead(403).end(); return; }
    const body = await readFile(file);
    response.writeHead(200, { 'Content-Type': (types[extname(file)] || 'application/octet-stream') + '; charset=utf-8', 'Cache-Control': 'no-store' });
    response.end(body);
  } catch {
    response.writeHead(502, { 'Content-Type': 'text/plain' });
    response.end('Preview resource is unavailable.');
  }
}).listen(5173, '127.0.0.1', () => console.log('Local: http://127.0.0.1:5173'));
