// Index de recherche plein texte, calculé au build (voir src/pages/search.json.ts).
// Une entrée par section de fiche (chaque titre « ## »), pour pouvoir envoyer
// directement au bon endroit de la fiche. Le navigateur ne télécharge ce fichier
// qu'à la première recherche.
import { render } from 'astro:content';
import { getModules, getFiches, getCertifications, moduleOf, ficheUrl } from './content';
import { url } from './url';

export type SearchEntry = {
  u: string; // URL de la fiche, avec l'ancre de la section
  t: string; // titre de la fiche
  m: string; // module
  h: string; // titre de la section ('' pour l'introduction)
  x: string; // texte brut de la section
};

/** Markdown → texte brut : on garde les mots (y compris dans le code), pas la mise en forme. */
export function plainText(md: string) {
  return md
    .replace(/<figure[\s\S]*?<\/figure>/g, ' ')    // schémas SVG
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/```\w*/g, ' ')
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1')       // liens : on garde le texte
    .replace(/^\s*(?:>|[-*]|\d+\.)\s+/gm, '')        // citations et listes
    .replace(/[*_`#|]+/g, ' ')
    .replace(/-{3,}/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/** Découpe le corps d'une fiche aux titres « ## », sans se tromper sur les blocs de code. */
function sections(body: string) {
  const out: { h: string; lines: string[] }[] = [{ h: '', lines: [] }];
  let inCode = false;
  for (const line of body.split('\n')) {
    if (line.startsWith('```')) inCode = !inCode;
    if (!inCode && line.startsWith('## ')) out.push({ h: line.slice(3).trim(), lines: [] });
    else out[out.length - 1].lines.push(line);
  }
  return out;
}

export async function buildSearchIndex(): Promise<SearchEntry[]> {
  const [mods, fiches] = await Promise.all([getModules(), getFiches()]);
  const modTitle = Object.fromEntries(mods.map((m) => [m.id, m.data.title]));
  const entries: SearchEntry[] = [];
  for (const f of fiches) {
    const base = ficheUrl(f);
    const m = modTitle[moduleOf(f)] ?? moduleOf(f);
    // Les ancres sont celles qu'Astro a générées pour les titres de niveau 2, dans l'ordre.
    const { headings } = await render(f);
    const slugs = headings.filter((h) => h.depth === 2).map((h) => h.slug);
    sections(f.body ?? '').forEach((s, i) => {
      const slug = i > 0 ? slugs[i - 1] : undefined;
      const x = plainText(s.lines.join('\n'));
      if (x || s.h) entries.push({ u: slug ? `${base}#${slug}` : base, t: f.data.title, m, h: plainText(s.h), x });
    });
    // Les cartes de révision font aussi partie de ce qu'on cherche.
    const cards = f.data.cards.map((c) => `${c.q} ${c.a}`).join(' ');
    if (cards) entries.push({ u: base, t: f.data.title, m, h: 'Cartes de révision', x: plainText(cards) });
  }
  // Les synthèses « jour J » des certifications.
  for (const c of await getCertifications()) {
    const base = url(`/certifications/${c.id}/`);
    const { headings } = await render(c);
    const slugs = headings.filter((h) => h.depth === 2).map((h) => h.slug);
    sections(c.body ?? '').forEach((s, i) => {
      const slug = i > 0 ? slugs[i - 1] : undefined;
      const x = plainText(s.lines.join('\n'));
      if (x) entries.push({ u: slug ? `${base}#${slug}` : base, t: c.data.name, m: 'Certification', h: plainText(s.h), x });
    });
  }
  return entries;
}
