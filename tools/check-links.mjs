// Vérifie, après `npm run build`, que chaque lien interne du site mène à une page qui existe.
// Usage : node tools/check-links.mjs [dossier] (par défaut dist/).
// Le préfixe des liens (BASE_PATH, ex. /my-learning-hub) est lu comme dans astro.config.mjs.
import { readdirSync, readFileSync, existsSync, statSync } from 'node:fs';
import { join, dirname, normalize } from 'node:path';

const root = process.argv[2] ?? 'dist';
const base = (process.env.BASE_PATH ?? '').replace(/\/$/, '');

const pages = [];
const walk = (dir) => {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p);
    else if (name.endsWith('.html')) pages.push(p);
  }
};
walk(root);

const broken = new Map();
for (const page of pages) {
  const html = readFileSync(page, 'utf8');
  for (const [, link] of html.matchAll(/(?:href|src)="([^"#?]*)/g)) {
    if (!link || /^(https?:|mailto:|data:|javascript:)/.test(link)) continue;
    let target;
    if (link.startsWith('/')) {
      if (base && !link.startsWith(base + '/') && link !== base) { broken.set(link, page); continue; }
      target = join(root, link.slice(base.length));
    } else {
      target = normalize(join(dirname(page), link));
    }
    if (existsSync(target) && statSync(target).isDirectory()) target = join(target, 'index.html');
    if (!existsSync(target)) broken.set(link, page);
  }
}

if (broken.size) {
  console.error(`${broken.size} lien(s) interne(s) cassé(s) :`);
  for (const [link, page] of [...broken].slice(0, 30)) console.error(`  ${link}  (dans ${page})`);
  if (broken.size > 30) console.error(`  … et ${broken.size - 30} autres`);
  process.exit(1);
}
console.log(`${pages.length} pages vérifiées, aucun lien interne cassé.`);
