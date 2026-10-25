# my-learning-hub

My personal site for learning and reviewing. Tech side: Kubernetes, Linux, Terraform, Ansible, security, networking, DevOps, Docker, AWS, OpenStack, observability and AI. Personal side: Japanese, badminton, Yu-Gi-Oh!, Valorant, piano, personal finance and chess.

Chapter-based learning paths, notes, flashcards with spaced repetition, quizzes and progress tracking. No account and no database: a static site that runs locally or on GitHub Pages.

> The site content is written in French. The detailed architecture guide is in French too: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Features

- **19 modules, 345 notes, 2,300+ flashcards**, a quiz for every note and a one-page summary per module.
- **Spaced repetition** (simplified SM-2, the algorithm behind Anki) with a 14-day review forecast.
- **Certification tracks** (CKA, AWS SAA, CKS, LFCS, Terraform Associate, Red Hat EX210) built on top of the existing notes.
- **Full-text search** with a ⌘K / Ctrl+K palette.
- **130+ animated SVG diagrams**, styled by the theme so they work in both visual moods (dark for Tech, paper for Perso).
- **Progress stays in the browser** (localStorage), with export / import to a JSON file.

## Stack

- [Astro](https://astro.build) 7, fully static: every page is rendered to HTML at build time.
- Content in Markdown with validated frontmatter (Astro content collections + Zod).
- A little TypeScript in the browser for progress, review sessions and search. No framework, no tracking.
- GitHub Actions for checks and deployment to GitHub Pages.

## Getting started

Requires **Node.js 22.12 or later** (`node -v` to check, `brew install node` otherwise).

```bash
npm install          # once, installs Astro and the checking tools
npm run dev          # runs the site at http://localhost:4321 with live reload
```

Other commands:

```bash
npm run build        # builds the final site into dist/
npm run preview      # serves dist/ to check the build
npm run check        # type-checks the code and the .astro pages
npm run check:links  # after a build: makes sure no internal link is broken
```

Before pushing: `npm run build`, then `npm run check`. The pipeline runs these checks again anyway.

## Project layout

```
src/content/modules/         one file per module (title, color, chapters)
src/content/fiches/          the notes, grouped by module, with their flashcards and quiz
src/content/syntheses/       one summary page per module
src/content/certifications/  target exams, linked to the notes that cover them
src/pages/                   the site's pages
src/lib/                     the logic (content, progress, spaced repetition, search)
src/styles/global.css        the whole design
tools/schemas/               scripts that generate the diagrams in the notes
tools/check-links.mjs        the internal link checker
.github/                     deployment pipeline, CodeQL, dependency review, Dependabot
design/maquette.html         the original mockup
docs/ARCHITECTURE.md         how the site is built, and why (in French)
```

## Deployment

Every push to `main` publishes the site to GitHub Pages through `.github/workflows/deploy.yml`. One-time setup in the GitHub repository: *Settings → Pages → Source*: **GitHub Actions**.

On every pull request and push, the pipeline runs `npm audit`, the type check, the build and the link check; nothing is published if any of them fails. CodeQL scans the code and the workflows, and dependency review blocks pull requests that add a vulnerable package. All actions are pinned to a commit SHA and kept up to date by Dependabot.

## Security

There is no server, account or database, so the risks live in the browser:

- a **Content Security Policy** allows scripts by hash only, so an injected script would not run;
- data embedded in pages is escaped, and hand-built HTML goes through an escaping helper;
- progress read from localStorage or an imported file is **sanitized** (expected fields and types only, internal URLs only, prototype keys ignored).

Details in the « La sécurité » section of [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Versions

See [CHANGELOG.md](CHANGELOG.md).
