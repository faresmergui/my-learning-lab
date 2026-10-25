// @ts-check
import { defineConfig } from 'astro/config';

// Site 100 % statique : chaque page est générée en HTML au build.
// SITE_URL et BASE_PATH sont fournis par la pipeline de déploiement
// (.github/workflows/deploy.yml). En local, le site vit à la racine « / ».
export default defineConfig({
  site: process.env.SITE_URL,
  base: process.env.BASE_PATH || '/',
  markdown: {
    // Coloration syntaxique des blocs de code (Shiki, inclus dans Astro).
    shikiConfig: { theme: 'tokyo-night' },
  },
  devToolbar: { enabled: false },
  security: {
    // Politique de sécurité du contenu (CSP), ajoutée dans une balise <meta> de chaque page.
    // Les scripts sont autorisés un par un par leur empreinte (hash) : un script injecté
    // dans une page ne s'exécuterait pas. Les styles gardent 'unsafe-inline' parce que
    // Shiki (coloration du code) et les couleurs de module utilisent des styles en ligne ;
    // c'est un risque bien plus faible que pour les scripts.
    csp: {
      directives: [
        "default-src 'self'",
        "img-src 'self' data:",
        "font-src 'self' https://fonts.gstatic.com",
        "connect-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
      ],
      styleDirective: { resources: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'] },
    },
  },
});
