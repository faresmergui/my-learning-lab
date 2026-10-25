// Full-text search index, built at build time (see src/pages/search.json.ts).
// One entry per note section (each "##" heading), so a result can link straight
// to the right spot in the note. The browser only downloads this file on the
// first search.
import { render } from 'astro:content';
import { getModules, getFiches, getCertifications, moduleOf, ficheUrl } from './content';
import { url } from './url';

export type SearchEntry = {
  u: string; // note URL, with the section anchor
  t: string; // note title
  m: string; // module
  h: string; // section title ('' for the introduction)
  x: string; // section plain text
};

/** Markdown → plain text: keep the words (including in code), drop the formatting. */
export function plainText(md: string) {
  return md
    .replace(/<figure[\s\S]*?<\/figure>/g, ' ')    // SVG diagrams
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/```\w*/g, ' ')
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1')       // links: keep the text
    .replace(/^\s*(?:>|[-*]|\d+\.)\s+/gm, '')        // quotes and lists
    .replace(/[*_`#|]+/g, ' ')
    .replace(/-{3,}/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/** Splits a note body at "##" headings, without being fooled by code blocks. */
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
    // Anchors are the ones Astro generated for level-2 headings, in order.
    const { headings } = await render(f);
    const slugs = headings.filter((h) => h.depth === 2).map((h) => h.slug);
    sections(f.body ?? '').forEach((s, i) => {
      const slug = i > 0 ? slugs[i - 1] : undefined;
      const x = plainText(s.lines.join('\n'));
      if (x || s.h) entries.push({ u: slug ? `${base}#${slug}` : base, t: f.data.title, m, h: plainText(s.h), x });
    });
    // Flashcards are searchable too.
    const cards = f.data.cards.map((c) => `${c.q} ${c.a}`).join(' ');
    if (cards) entries.push({ u: base, t: f.data.title, m, h: 'Cartes de révision', x: plainText(cards) });
  }
  // The certifications' exam-day summaries.
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
