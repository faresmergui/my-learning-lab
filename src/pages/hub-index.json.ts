// Static file /hub-index.json: the list of modules, notes and cards used by the
// counters (home, menu, dashboard). Downloaded once and cached by the browser,
// instead of being copied into every page.
import { getHubIndex } from '../lib/content';

export async function GET() {
  return new Response(JSON.stringify(await getHubIndex()), {
    headers: { 'Content-Type': 'application/json' },
  });
}
