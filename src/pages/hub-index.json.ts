// Fichier statique /hub-index.json : la liste des modules, fiches et cartes, utilisée
// par les compteurs (accueil, menu, tableau de bord). Téléchargé une fois, puis gardé
// en cache par le navigateur, au lieu d'être recopié dans chacune des pages.
import { getHubIndex } from '../lib/content';

export async function GET() {
  return new Response(JSON.stringify(await getHubIndex()), {
    headers: { 'Content-Type': 'application/json' },
  });
}
