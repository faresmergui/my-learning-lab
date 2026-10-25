// Static file /search.json: the full-text search index of the notes.
import { buildSearchIndex } from '../lib/search';

export async function GET() {
  return new Response(JSON.stringify(await buildSearchIndex()), {
    headers: { 'Content-Type': 'application/json' },
  });
}
