// Static file /palette.json: the pages offered by the ⌘K palette.
// Downloaded the first time the palette opens.
import { getPaletteEntries } from '../lib/content';

export async function GET() {
  return new Response(JSON.stringify(await getPaletteEntries()), {
    headers: { 'Content-Type': 'application/json' },
  });
}
