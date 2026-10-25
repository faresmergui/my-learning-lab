# my-learning-hub

Mon site personnel pour apprendre et réviser. Côté tech : Kubernetes, Linux, Terraform, Ansible, sécurité, réseaux, DevOps, Docker, AWS, OpenStack, observabilité et IA. Côté perso : japonais, badminton, Yu-Gi-Oh!, Valorant, piano, finances et échecs.

Parcours en chapitres, fiches, flashcards avec répétition espacée, quiz et suivi de progression. Pas de compte ni de base de données : un site statique, en local ou sur GitHub Pages.

## Lancer le site

Il faut **Node.js 22.12 ou plus récent** (`node -v` pour vérifier, `brew install node` sinon).

```bash
npm install      # une seule fois, installe Astro
npm run dev      # lance le site sur http://localhost:4321
```

Le site se recharge tout seul quand tu modifies un fichier.

Autres commandes :

```bash
npm run build        # génère le site final dans dist/
npm run preview      # sert le contenu de dist/ pour vérifier le build
npm run check        # vérifie les types et le format du code
npm run check:links  # après un build : vérifie qu'aucun lien interne n'est cassé
```

Avant de pousser : `npm run build` puis `npm run check`. La pipeline refait ces vérifications de toute façon.

## Où est quoi

```
src/content/modules/     un fichier par module (titre, couleur, chapitres)
src/content/fiches/      les fiches, rangées par module, avec leurs cartes et leur quiz
src/pages/               les pages du site
src/lib/                 la logique (contenu, progression, répétition espacée)
src/styles/global.css    tout le design
tools/schemas/           les scripts qui génèrent les schémas des fiches
tools/check-links.mjs    le vérificateur de liens internes
.github/                 la pipeline de déploiement, CodeQL, la revue des dépendances, Dependabot
design/maquette.html     la maquette d'origine
docs/ARCHITECTURE.md     comment le site est construit, et pourquoi
```

## Mettre en ligne

Chaque push sur `main` publie le site sur GitHub Pages, via la pipeline `.github/workflows/deploy.yml`. Une seule chose à faire la première fois : dans le dépôt GitHub, *Settings → Pages → Source* : **GitHub Actions**. Le détail (et pourquoi c'est sûr) est dans la section « La pipeline de déploiement » de [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

Les contrôles automatiques (types, liens, CodeQL, dépendances) sont décrits dans la section « Les contrôles automatiques » de [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). L'historique des versions est dans [CHANGELOG.md](CHANGELOG.md).

Pour écrire ou corriger une fiche, voir la section « Écrire du contenu » de [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Ma progression

Elle est enregistrée dans le navigateur (localStorage). Les boutons **Exporter / Importer** en bas de l'accueil permettent de la sauvegarder dans un fichier JSON ou de la passer sur une autre machine.
