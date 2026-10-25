// Learning progress, stored in the browser (localStorage).
// This file runs in the browser only. Everything goes through load()/save()
// so localStorage could one day be swapped for a file or an API
// without touching the rest of the site.
import { url } from './url';

const KEY = 'hub:v1';
const DAY = 86_400_000;

export type CardState = {
  due: number;      // timestamp (ms) of the next review
  interval: number; // current interval in days (0 = learning)
  ease: number;     // ease factor, starts at 2.5
  reps: number;     // consecutive successful reviews
  lapses: number;   // number of lapses
};

export type Progress = {
  cards: Record<string, CardState>;
  read: Record<string, number>;                         // note -> date read
  quiz: Record<string, { right: number; total: number }>; // note -> cumulative answers
  activity: Record<string, number>;                     // 'YYYY-MM-DD' -> number of actions
  last?: { url: string; title: string; module: string };
};

const empty = (): Progress => ({ cards: {}, read: {}, quiz: {}, activity: {} });

/* ---------------- Validation ----------------
   Data comes from the browser or from an imported file: only well-formed values
   are kept (numbers where numbers are expected, an internal URL for "resume").
   A hand-edited backup therefore cannot inject HTML or a javascript: link
   into the pages. */

const num = (v: unknown, def = 0) => (typeof v === 'number' && Number.isFinite(v) ? v : def);
const obj = (v: unknown): Record<string, unknown> =>
  v && typeof v === 'object' && !Array.isArray(v) ? (v as Record<string, unknown>) : {};
const str = (v: unknown, max = 300) => (typeof v === 'string' ? v.slice(0, max) : '');
// Browsers read "/\\site.com" as "//site.com" (another site): rejected too.
const isInternalUrl = (u: string) => /^\/(?![/\\])/.test(u) && !/[\s\\]/.test(u);
// Keys that would modify an object's prototype instead of adding an entry.
const safeEntries = (v: unknown) => Object.entries(obj(v)).filter(([k]) => k !== '__proto__' && k !== 'constructor' && k !== 'prototype');

function sanitize(raw: unknown): Progress {
  const d = obj(raw);
  const p = empty();
  for (const [id, v] of safeEntries(d.cards)) {
    const c = obj(v);
    p.cards[id] = { due: num(c.due), interval: num(c.interval), ease: num(c.ease, 2.5), reps: num(c.reps), lapses: num(c.lapses) };
  }
  for (const [id, v] of safeEntries(d.read)) p.read[id] = num(v);
  for (const [id, v] of safeEntries(d.quiz)) { const q = obj(v); p.quiz[id] = { right: num(q.right), total: num(q.total) }; }
  for (const [k, v] of Object.entries(obj(d.activity))) if (/^\d{4}-\d{2}-\d{2}$/.test(k)) p.activity[k] = num(v);
  const last = obj(d.last);
  const link = str(last.url);
  if (isInternalUrl(link)) p.last = { url: link, title: str(last.title), module: str(last.module, 60) };
  return p;
}

// Renamed notes: the old ID maps to the new one, so that progress
// (notes read, cards, quiz) follows the renamed file.
const RENAMED: Record<string, string> = {
  'badminton/01-amorti': 'badminton/04-amorti',
  'badminton/03-degagement-et-smash': 'badminton/04-degagement-et-smash',
  'badminton/04-jeu-au-filet': 'badminton/05-jeu-au-filet',
  'badminton/05-deplacements': 'badminton/06-deplacements',
  'badminton/06-tactique-simple': 'badminton/09-tactique-simple',
  'badminton/07-tactique-double': 'badminton/10-tactique-double',
  'badminton/08-preparation-physique': 'badminton/14-preparation-physique',
  // Security: 3 methodology notes inserted (2026-10-25), tools overview and certifications shifted.
  'securite/10-panorama-des-outils': 'securite/13-panorama-des-outils',
  'securite/11-certifications-securite': 'securite/14-certifications-securite',
  // Piano reorganized on 2026-10-25 (play-by-ear path first, sheet music later).
  'piano/02-lire-une-partition': 'piano/20-lire-une-partition',
  'piano/03-le-rythme': 'piano/21-le-rythme',
  'piano/05-intervalles-et-gamme-majeure': 'piano/07-intervalles-et-gamme-majeure',
  'piano/06-gammes-mineures-et-tonalites': 'piano/08-gammes-mineures-et-tonalites',
  'piano/07-les-accords-et-les-renversements': 'piano/09-les-accords-et-les-renversements',
  'piano/08-progressions-et-accompagnement': 'piano/10-progressions-et-accompagnement',
  'piano/09-accords-enrichis': 'piano/11-accords-enrichis',
  'piano/10-travailler-un-morceau': 'piano/12-travailler-un-morceau',
  'piano/11-nuances-articulation-et-pedale': 'piano/13-nuances-articulation-et-pedale',
  'piano/12-improviser-et-jouer-d-oreille': 'piano/14-improviser-et-jouer-d-oreille',
  'piano/13-les-modes-et-l-harmonie-modale': 'piano/15-les-modes-et-l-harmonie-modale',
  'piano/14-voicings-et-ii-v-i': 'piano/16-voicings-et-ii-v-i',
  'piano/15-reharmoniser': 'piano/17-reharmoniser',
  'piano/16-technique-avancee': 'piano/18-technique-avancee',
  'piano/17-analyser-un-morceau': 'piano/19-analyser-un-morceau',
  'piano/18-dechiffrer-et-jouer-en-public': 'piano/22-dechiffrer-et-jouer-en-public',
};

function migrate(p: Progress): boolean {
  let changed = false;
  for (const [from, to] of Object.entries(RENAMED)) {
    for (const bag of [p.read, p.quiz] as Record<string, unknown>[]) {
      if (from in bag) { bag[to] ??= bag[from]; delete bag[from]; changed = true; }
    }
    for (const id of Object.keys(p.cards)) {
      if (id.startsWith(from + '#')) {
        const nid = to + id.slice(from.length);
        p.cards[nid] ??= p.cards[id];
        delete p.cards[id];
        changed = true;
      }
    }
    if (p.last?.url === url(`/${from}/`)) { p.last.url = url(`/${to}/`); changed = true; }
  }
  return changed;
}

export function load(): Progress {
  try {
    const raw = localStorage.getItem(KEY);
    const p: Progress = raw ? sanitize(JSON.parse(raw)) : empty();
    if (raw && migrate(p)) save(p);
    return p;
  } catch {
    return empty();
  }
}

export function save(p: Progress) {
  try { localStorage.setItem(KEY, JSON.stringify(p)); } catch { /* private browsing */ }
}

export const dayKey = (t = Date.now()) => {
  const d = new Date(t);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

function bump(p: Progress) {
  const k = dayKey();
  p.activity[k] = (p.activity[k] ?? 0) + 1;
}

/* ---------------- Spaced repetition ----------------
   Simplified version of the SM-2 algorithm (the one Anki uses).
   1 Again  -> back in 10 min, the card becomes "new" again
   2 Hard   -> interval × 1.2, the card gets slightly harder
   3 Good   -> 1 day, then 3 days, then interval × ease
   4 Easy   -> like Good but further out, the card gets easier */

export type Grade = 1 | 2 | 3 | 4;

export function schedule(s: CardState | undefined, g: Grade, now = Date.now()): CardState {
  const c: CardState = s ? { ...s } : { due: now, interval: 0, ease: 2.5, reps: 0, lapses: 0 };
  if (g === 1) {
    c.reps = 0; c.interval = 0; c.lapses++;
    c.ease = Math.max(1.3, c.ease - 0.2);
    c.due = now + 10 * 60_000;
    return c;
  }
  if (g === 2) {
    c.interval = Math.max(1, Math.round(c.interval * 1.2));
    c.ease = Math.max(1.3, c.ease - 0.15);
  } else if (g === 3) {
    c.interval = c.reps === 0 ? 1 : c.reps === 1 ? 3 : Math.round(c.interval * c.ease);
  } else {
    c.interval = c.reps === 0 ? 3 : Math.round(Math.max(c.interval, 1) * c.ease * 1.3);
    c.ease += 0.15;
  }
  c.reps++;
  c.due = now + c.interval * DAY;
  return c;
}

/** Label shown under each button: "dans 3 j" (in 3 days). */
export function preview(s: CardState | undefined, g: Grade) {
  const next = schedule(s, g);
  if (next.interval === 0) return 'dans 10 min';
  if (next.interval < 31) return `dans ${next.interval} j`;
  return `dans ${Math.round(next.interval / 30)} mois`;
}

export function gradeCard(id: string, g: Grade) {
  const p = load();
  p.cards[id] = schedule(p.cards[id], g);
  bump(p);
  save(p);
}

/** A card is "mastered" when it won't come back for at least a week. */
export const isMastered = (s?: CardState) => !!s && s.interval >= 7;
export const isDue = (s: CardState | undefined, now = Date.now()) => !s || s.due <= now;

/** Maximum number of new cards per session. */
export const NEW_PER_SESSION = 15;

/** Review queue: overdue cards first, then a few new ones. */
export function reviewQueue<T extends { id: string }>(cards: T[], p = load()) {
  const now = Date.now();
  const due = cards.filter((c) => p.cards[c.id] && p.cards[c.id].due <= now)
    .sort((a, b) => p.cards[a.id].due - p.cards[b.id].due);
  const fresh = cards.filter((c) => !p.cards[c.id]).slice(0, NEW_PER_SESSION);
  return [...due, ...fresh];
}

/* ---------------- Notes, quiz, activity ---------------- */

export function markRead(fiche: string, read = true) {
  const p = load();
  if (read) p.read[fiche] = Date.now(); else delete p.read[fiche];
  bump(p);
  save(p);
}

export function setLast(last: Progress['last']) {
  const p = load();
  p.last = last;
  save(p);
}

export function recordAnswer(fiche: string, right: boolean) {
  const p = load();
  const q = (p.quiz[fiche] ??= { right: 0, total: 0 });
  q.total++;
  if (right) q.right++;
  bump(p);
  save(p);
}

/** Consecutive days of activity, counting from today or yesterday. */
export function streak(p = load()) {
  // Step back one calendar day at a time (not 24 h) to stay correct across DST changes.
  const d = new Date();
  const key = () => dayKey(d.getTime());
  let n = 0;
  if (!p.activity[key()]) d.setDate(d.getDate() - 1);
  while (p.activity[key()]) { n++; d.setDate(d.getDate() - 1); }
  return n;
}

/* ---------------- Backup ----------------
   Progress only lives in this browser: export copies it to a file.
   On import, the file's contents are shown first, and a copy of the current
   progress is kept so the import can be undone. */

const EXPORTED = 'hub:exported';          // date of the last export
const BEFORE_IMPORT = 'hub:v1:avant-import'; // progress replaced by the last import

const getItem = (k: string) => { try { return localStorage.getItem(k); } catch { return null; } };
const setItem = (k: string, v: string) => { try { localStorage.setItem(k, v); } catch { /* private browsing */ } };

/** What a progress snapshot contains, in a few numbers. */
export function summary(p: Progress) {
  return {
    cards: Object.keys(p.cards).length,
    read: Object.keys(p.read).length,
    days: Object.keys(p.activity).length,
  };
}

export const isEmpty = (p: Progress) => { const s = summary(p); return !s.cards && !s.read && !s.days; };

/** Date of the last export (ms), or null if never exported from this browser. */
export function lastExport(): number | null {
  const v = Number(getItem(EXPORTED));
  return Number.isFinite(v) && v > 0 ? v : null;
}

export function exportJson() {
  const data = { app: 'learning-hub', exportedAt: Date.now(), ...load() };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `learning-hub-${dayKey()}.json`;
  document.body.append(a);
  a.click();
  a.remove();
  // Safari needs the link to stay around briefly after the click.
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  setItem(EXPORTED, String(Date.now()));
}

/** Reads a backup file without saving anything, so it can be previewed first. */
export async function readBackup(file: File): Promise<{ progress: Progress; exportedAt: number | null }> {
  if (file.size > 5_000_000) throw new Error('Fichier trop volumineux');
  const data = JSON.parse(await file.text());
  if (!data || typeof data !== 'object' || typeof data.cards !== 'object') throw new Error('Fichier non reconnu');
  const progress = sanitize(data);
  migrate(progress);
  return { progress, exportedAt: num(data.exportedAt) || null };
}

/** Replaces the progress, keeping the previous one aside. */
export function applyImport(p: Progress) {
  const current = getItem(KEY);
  if (current) setItem(BEFORE_IMPORT, current);
  save(p);
}

export const canUndoImport = () => getItem(BEFORE_IMPORT) !== null;

/** Restores the progress from before the last import. */
export function undoImport() {
  const before = getItem(BEFORE_IMPORT);
  if (before === null) return;
  setItem(KEY, before);
  try { localStorage.removeItem(BEFORE_IMPORT); } catch { /* rien */ }
}
