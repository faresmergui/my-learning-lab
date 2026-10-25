// Préfixe des liens internes. En local il vaut "/" ; sur GitHub Pages (site de projet)
// il vaut "/<nom-du-dépôt>/". Astro le lit dans `base` (astro.config.mjs).
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

/** Lien interne : url('/tech/') donne '/tech/' en local et '/my-learning-hub/tech/' en ligne. */
export const url = (path: string) => BASE + path;
