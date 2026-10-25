// Fichier statique /palette.json : les pages proposées par la palette ⌘K.
// Téléchargé à la première ouverture de la palette.
import { getPaletteEntries } from '../lib/content';

export async function GET() {
  return new Response(JSON.stringify(await getPaletteEntries()), {
    headers: { 'Content-Type': 'application/json' },
  });
}
