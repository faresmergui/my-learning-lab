// Prefix for internal links. Locally it is "/"; on GitHub Pages (project site)
// it is "/<repo-name>/". Astro reads it from `base` (astro.config.mjs).
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

/** Internal link: url('/tech/') gives '/tech/' locally and '/my-learning-hub/tech/' online. */
export const url = (path: string) => BASE + path;
