// Fichier statique /search.json : l'index de recherche plein texte des fiches.
import { buildSearchIndex } from '../lib/search';

export async function GET() {
  return new Response(JSON.stringify(await buildSearchIndex()), {
    headers: { 'Content-Type': 'application/json' },
  });
}
