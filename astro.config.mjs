// @ts-check
import { defineConfig } from 'astro/config';

// Fully static site: every page is rendered to HTML at build time.
// SITE_URL and BASE_PATH come from the deployment pipeline
// (.github/workflows/deploy.yml). Locally, the site lives at the root "/".
export default defineConfig({
  site: process.env.SITE_URL,
  base: process.env.BASE_PATH || '/',
  markdown: {
    // Syntax highlighting for code blocks (Shiki, bundled with Astro).
    shikiConfig: { theme: 'tokyo-night' },
  },
  devToolbar: { enabled: false },
  security: {
    // Content Security Policy (CSP), added to every page as a <meta> tag.
    // Scripts are allowed one by one by their hash: a script injected into a page
    // would not run. Styles keep 'unsafe-inline' because Shiki (code highlighting)
    // and the module colors use inline styles; that is a much lower risk than for scripts.
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
