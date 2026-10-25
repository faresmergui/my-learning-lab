// Fonctions utilisées au moment du build pour lire et organiser le contenu.
// Rien ici n'est envoyé au navigateur : seules les données préparées le sont.
import { getCollection, type CollectionEntry } from 'astro:content';
import { marked } from 'marked';
import { url } from './url';

export type Module = CollectionEntry<'modules'>;
export type Fiche = CollectionEntry<'fiches'>;

/** JSON à placer dans un <script type="application/json"> : « < » est échappé pour
 *  qu'un texte contenant </script> ne puisse jamais refermer la balise. */
export const jsonForScript = (data: unknown) => JSON.stringify(data).replace(/</g, '\\u003c');

/** Les questions/réponses des cartes acceptent du Markdown simple (`code`, **gras**). */
export const inline = (md: string) => marked.parseInline(md, { async: false }) as string;

/** Identifiant stable d'une carte : son `id` s'il existe, sinon un hash de la question. */
export function cardId(ficheId: string, card: { id?: string; q: string }) {
  if (card.id) return `${ficheId}#${card.id}`;
  let h = 0;
  for (const ch of card.q) h = (Math.imul(31, h) + ch.charCodeAt(0)) | 0;
  return `${ficheId}#${(h >>> 0).toString(36)}`;
}

export const moduleOf = (fiche: Fiche) => fiche.id.split('/')[0];
export const ficheSlug = (fiche: Fiche) => fiche.id.split('/').slice(1).join('/');
export const ficheUrl = (fiche: Fiche) => url(`/${moduleOf(fiche)}/${ficheSlug(fiche)}/`);

export async function getModules(universe?: 'tech' | 'perso') {
  const all = await getCollection('modules');
  const u = (m: Module) => (m.data.universe === 'tech' ? 0 : 100);
  return all
    .filter((m) => !universe || m.data.universe === universe)
    .sort((a, b) => u(a) - u(b) || a.data.order - b.data.order);
}

/** Fiches triées dans l'ordre des modules, puis des chapitres. */
export async function getFiches(moduleSlug?: string) {
  const [all, mods] = await Promise.all([getCollection('fiches'), getCollection('modules')]);
  const rank = (f: Fiche) => {
    const m = mods.find((m) => m.id === moduleOf(f));
    return m ? (m.data.universe === 'tech' ? 0 : 100) + m.data.order : 999;
  };
  return all
    .filter((f) => !moduleSlug || moduleOf(f) === moduleSlug)
    .sort((a, b) => rank(a) - rank(b) || a.data.chapter - b.data.chapter || a.data.order - b.data.order);
}

/** Chapitres d'un module, avec les fiches rangées dedans. */
export function groupByChapter(mod: Module, fiches: Fiche[]) {
  return mod.data.chapters.map((title, i) => ({
    n: i + 1,
    title,
    fiches: fiches.filter((f) => f.data.chapter === i + 1),
  }));
}

/**
 * Chapitres rangés par niveau, si le module en définit (JLPT, classement…).
 * Sans niveaux, un seul groupe sans titre.
 */
export function groupByStage(mod: Module, fiches: Fiche[]) {
  const chapters = groupByChapter(mod, fiches);
  const stages = mod.data.stages;
  if (!stages?.length) return [{ label: '', title: '', description: '', chapters }];
  let start = 0;
  const groups = stages.map((s) => {
    const g = { label: s.label, title: s.title, description: s.description ?? '', chapters: chapters.slice(start, start + s.chapters) };
    start += s.chapters;
    return g;
  });
  // Chapitres non couverts par un niveau : rangés à la fin, sans perdre de contenu.
  if (start < chapters.length) groups.push({ label: '', title: 'Autres', description: '', chapters: chapters.slice(start) });
  return groups;
}

/** Toutes les cartes, prêtes pour la page de révision. */
export async function getAllCards() {
  const [mods, fiches] = await Promise.all([getModules(), getFiches()]);
  const byId = Object.fromEntries(mods.map((m) => [m.id, m]));
  return fiches.flatMap((f) => {
    const m = byId[moduleOf(f)];
    return f.data.cards.map((c) => ({
      id: cardId(f.id, c),
      fiche: f.id,
      ficheTitle: f.data.title,
      module: m?.id ?? moduleOf(f),
      moduleTitle: m?.data.title ?? moduleOf(f),
      color: m?.data.color ?? '#888',
      q: inline(c.q),
      a: inline(c.a),
    }));
  });
}

/** Toutes les questions de quiz. */
export async function getAllQuestions() {
  const [mods, fiches] = await Promise.all([getModules(), getFiches()]);
  const byId = Object.fromEntries(mods.map((m) => [m.id, m]));
  return fiches.flatMap((f) =>
    f.data.quiz.map((q) => ({
      fiche: f.id,
      module: moduleOf(f),
      moduleTitle: byId[moduleOf(f)]?.data.title ?? moduleOf(f),
      q: inline(q.q),
      options: q.options.map(inline),
      answer: q.answer,
      explain: q.explain ? inline(q.explain) : '',
    })),
  );
}

/**
 * Index léger embarqué dans chaque page : quelles cartes et fiches
 * appartiennent à quel module. Le navigateur le croise avec ta progression
 * pour afficher les compteurs (à réviser, pourcentages...).
 */
export async function getHubIndex() {
  const [mods, fiches] = await Promise.all([getModules(), getFiches()]);
  return {
    modules: Object.fromEntries(
      mods.map((m) => {
        const fs = fiches.filter((f) => moduleOf(f) === m.id);
        return [m.id, {
          title: m.data.title,
          universe: m.data.universe,
          fiches: fs.map((f) => ({ id: f.id, title: f.data.title, url: ficheUrl(f), chapter: f.data.chapter })),
          cards: fs.flatMap((f) => f.data.cards.map((c) => cardId(f.id, c))),
        }];
      }),
    ),
  };
}

/** Synthèses (aide-mémoire), une par module au plus. */
export async function getSyntheses() {
  return getCollection('syntheses');
}

/** Entrées de la palette ⌘K. */
export async function getPaletteEntries() {
  const [mods, fiches, syns, certs] = await Promise.all([getModules(), getFiches(), getSyntheses(), getCertifications()]);
  const byId = Object.fromEntries(mods.map((m) => [m.id, m]));
  return [
    { label: 'Certifications', url: url('/certifications/'), kind: 'page' },
    ...certs.map((c) => ({ label: `${c.data.title} · ${c.data.name}`, url: url(`/certifications/${c.id}/`), kind: 'certification' })),
    { label: 'Synthèses', url: url('/syntheses/'), kind: 'page' },
    ...syns.map((s) => ({ label: `Synthèse ${byId[s.id]?.data.title ?? s.id}`, url: url(`/${s.id}/synthese/`), kind: 'synthèse' })),
    { label: 'Accueil', url: url('/'), kind: 'page' },
    { label: 'Univers Tech', url: url('/tech/'), kind: 'page' },
    { label: 'Univers Perso', url: url('/perso/'), kind: 'page' },
    { label: 'Tableau de bord', url: url('/progression/'), kind: 'page' },
    { label: 'Réviser mes cartes', url: url('/reviser/'), kind: 'action' },
    { label: 'Lancer un quiz', url: url('/quiz/'), kind: 'action' },
    ...mods.map((m) => ({ label: m.data.title, url: url(`/${m.id}/`), kind: 'module' })),
    ...fiches.map((f) => ({ label: f.data.title, url: ficheUrl(f), kind: byId[moduleOf(f)]?.data.title ?? 'fiche' })),
  ];
}

/** Certifications, dans l'ordre de priorité. */
export async function getCertifications() {
  return (await getCollection('certifications')).sort((a, b) => a.data.order - b.data.order);
}

export type Certification = Awaited<ReturnType<typeof getCertifications>>[number];

/** Fiches d'une certification (sans doublon) ; une fiche introuvable fait échouer le build. */
export async function certFiches(cert: Certification) {
  const fiches = await getFiches();
  const ids = [...new Set(cert.data.domains.flatMap((d) => d.fiches))];
  return ids.map((id) => {
    const f = fiches.find((x) => x.id === id);
    if (!f) throw new Error(`Certification ${cert.id} : la fiche « ${id} » n'existe pas.`);
    return f;
  });
}

/** Pour le navigateur : les fiches et cartes de chaque certification (progression, filtres). */
export async function getCertIndex() {
  const certs = await getCertifications();
  return Object.fromEntries(await Promise.all(certs.map(async (c) => {
    const fs = await certFiches(c);
    return [c.id, {
      title: c.data.title,
      fiches: fs.map((f) => f.id),
      cards: fs.flatMap((f) => f.data.cards.map((card) => cardId(f.id, card))),
    }] as const;
  })));
}
