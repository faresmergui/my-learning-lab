// Numbers shown on the pages (counters, percentages), computed in the browser.
// They combine the content index (/hub-index.json) with the user's progress.
import { isDue, isMastered, load, type Progress } from './progress';
import { url } from './url';

export type HubIndex = {
  modules: Record<string, {
    title: string;
    universe: 'tech' | 'perso';
    fiches: { id: string; title: string; url: string; chapter: number }[];
    cards: string[];
  }>;
};

// Downloaded once per page (and cached by the browser across pages).
let pending: Promise<HubIndex> | null = null;
export const loadIndex = (): Promise<HubIndex> =>
  (pending ??= fetch(url('/hub-index.json'))
    .then((r) => (r.ok ? r.json() : { modules: {} }))
    .catch(() => ({ modules: {} })));

export function moduleStats(slug: string, idx: HubIndex, p: Progress = load()) {
  const m = idx.modules[slug];
  if (!m) return { due: 0, mastered: 0, cards: 0, read: 0, fiches: 0, pct: 0 };
  const due = m.cards.filter((id) => p.cards[id] && isDue(p.cards[id])).length;
  const mastered = m.cards.filter((id) => isMastered(p.cards[id])).length;
  const read = m.fiches.filter((f) => p.read[f.id]).length;
  const total = m.cards.length + m.fiches.length;
  // Progress = notes read + cards mastered, over the total of both.
  const pct = total ? Math.round(((read + mastered) / total) * 100) : 0;
  return { due, mastered, cards: m.cards.length, read, fiches: m.fiches.length, pct };
}

export function globalStats(idx: HubIndex, p: Progress = load()) {
  const all = Object.values(idx.modules).flatMap((m) => m.cards);
  const dueOld = all.filter((id) => p.cards[id] && isDue(p.cards[id])).length;
  const fresh = all.filter((id) => !p.cards[id]).length;
  const answers = Object.values(p.quiz).reduce((a, q) => ({ r: a.r + q.right, t: a.t + q.total }), { r: 0, t: 0 });
  return {
    due: dueOld,
    fresh,
    mastered: all.filter((id) => isMastered(p.cards[id])).length,
    quizPct: answers.t ? Math.round((answers.r / answers.t) * 100) : null,
    read: Object.keys(p.read).length,
  };
}
