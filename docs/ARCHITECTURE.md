# Comment le site est construit

Ce document explique chaque brique du projet et pourquoi elle a été choisie. Il évolue avec le site.

## Le principe en une phrase

Le contenu est écrit en **fichiers Markdown**, **Astro** les transforme en pages HTML, et ta **progression** est gardée dans ton navigateur.

```
 src/content/*.md  ──►  Astro (build)  ──►  pages HTML statiques  ──►  navigateur
   fiches, cartes,        vérifie et            une page par            JavaScript léger :
   quiz                   assemble              module et par fiche      révision, quiz, stats
                                                                         └─► localStorage
```

## Pourquoi ces choix

### Astro

Astro est un générateur de sites statiques : au moment du build, il lit le contenu et produit des pages HTML toutes prêtes. Il n'y a pas de serveur applicatif à faire tourner ni à maintenir.

- **Le contenu est un vrai citoyen.** Astro sait lire des dossiers de Markdown et vérifier leur structure (voir `src/content.config.ts`). Si une fiche a une erreur, le build le dit clairement.
- **Très peu de JavaScript.** Par défaut, Astro n'envoie aucun JS au navigateur. On n'en ajoute que là où il sert : la révision, le quiz, les compteurs.
- **Pas de framework à apprendre.** Les pages `.astro` ressemblent à du HTML avec un en-tête de code entre deux `---`. Le JS côté navigateur est du TypeScript simple, sans React ni Vue.
- **Facile à faire évoluer.** Si un jour on veut un composant React, un hébergement, ou une API, Astro sait le faire sans tout réécrire.

Alternatives écartées : un site en HTML pur (il faudrait dupliquer le menu et le design sur chaque page), Next.js (plus lourd, pensé pour des applis avec serveur), une appli avec base de données (inutile tant que tu es seul à l'utiliser).

### Le contenu en Markdown

Chaque fiche est un fichier `.md` lisible tel quel, versionnable dans Git, et modifiable dans n'importe quel éditeur (Neovim, VS Code, ou même Obsidian si tu ouvres `src/content/` comme coffre). Les flashcards et le quiz d'une fiche sont dans **le même fichier**, dans l'en-tête : quand tu relis une notion, tu relis aussi ses questions.

### La progression dans le navigateur

Ta progression (cartes, fiches lues, réponses aux quiz, jours d'activité) est un petit objet JSON stocké dans le `localStorage` du navigateur, sous la clé `hub:v1`.

- **Avantage :** zéro installation, zéro serveur, ça marche hors ligne.
- **Limite :** elle est liée à ce navigateur. Vider les données du navigateur l'efface. D'où la sauvegarde sur l'accueil :
  - **Exporter** télécharge un fichier `learning-hub-AAAA-MM-JJ.json`. La date du dernier export est retenue (clé `hub:exported`), et l'accueil l'affiche en rouge si rien n'a été exporté depuis 14 jours.
  - **Importer** lit d'abord le fichier, le vérifie (`sanitize()`), puis affiche ce qu'il contient avant de remplacer quoi que ce soit. La progression remplacée est gardée sous la clé `hub:v1:avant-import`, et le bouton **Annuler le dernier import** la remet en place.

Tout l'accès passe par `src/lib/progress.ts` (`load()` / `save()`). Le jour où tu voudras synchroniser entre plusieurs appareils, il suffira de changer ces deux fonctions.

## La répétition espacée

Chaque carte a un état : un intervalle en jours, un facteur de facilité et une date de prochaine révision. Quand tu notes une carte :

| Note | Effet |
| --- | --- |
| 1 · À revoir | revient dans 10 min et repart de zéro, la carte devient plus dure |
| 2 · Difficile | intervalle × 1,2 |
| 3 · Bien | 1 jour, puis 3 jours, puis intervalle × facilité (2,5 au départ) |
| 4 · Facile | plus loin que Bien, et la carte devient plus facile |

C'est une version simplifiée de **SM-2**, l'algorithme d'Anki. Une carte est considérée comme **maîtrisée** quand elle ne revient pas avant 7 jours. Une session reprend les cartes en retard et au plus 15 nouvelles, dans un ordre mélangé à chaque fois.

L'avancement d'un module = (fiches lues + cartes maîtrisées) / (fiches + cartes).

## Les fichiers importants

| Fichier | Rôle |
| --- | --- |
| `src/content.config.ts` | Le format attendu des modules et des fiches |
| `src/lib/content.ts` | Lit le contenu au build : tri, regroupement par chapitre, cartes, quiz |
| `src/lib/progress.ts` | Progression et répétition espacée (navigateur) |
| `src/lib/stats.ts` | Compteurs et pourcentages affichés (navigateur) |
| `src/layouts/Base.astro` | Squelette de toutes les pages : menu, polices, palette ⌘K |
| `src/pages/index.astro` | Accueil : révisions du jour, terminal, stats, heatmap |
| `src/pages/[module]/index.astro` | Page d'un module (une page générée par module) |
| `src/pages/[module]/[fiche].astro` | Page d'une fiche |
| `src/pages/reviser.astro` | Flashcards (`?module=…` ou `?fiche=…` pour filtrer) |
| `src/pages/quiz.astro` | Quiz de 10 questions au hasard (mêmes filtres) |
| `src/styles/global.css` | Le design, repris de la maquette |

Les crochets dans `[module]` signifient « une page par valeur » : Astro génère `/kubernetes/`, `/linux/`, etc. à partir des fichiers de `src/content/modules/`.

## Les deux ambiances

Toutes les couleurs sont des variables CSS (`--bg`, `--accent`, `--text`…) définies en haut de `global.css`. Les pages de l'univers Perso ajoutent la classe `perso` sur `<body>`, qui redéfinit ces variables : fond papier, polices japonaises. Changer une couleur à un seul endroit la change partout.

## Écrire du contenu

### Ajouter un module

Crée `src/content/modules/<slug>.md`. Le nom du fichier devient l'adresse (`/<slug>/`).

```yaml
---
title: Ansible
universe: tech          # tech ou perso
code: an                # texte de l'icône
color: "#ee0000"
order: 7                # position dans l'univers
description: Une phrase affichée sur la carte du module.
objective: Optionnel, affiché sous le titre.
chapters:
  - Inventaires
  - Playbooks
---
```

### Ajouter une fiche

Crée `src/content/fiches/<module>/<nom>.md`. Préfixer le nom par le numéro de chapitre (`03-...`) aide à s'y retrouver, mais c'est `chapter` qui compte.

```yaml
---
title: Les Deployments
chapter: 3              # numéro dans la liste des chapitres du module
order: 1                # position dans le chapitre
duration: 5             # minutes, optionnel
level: intermédiaire    # optionnel
tags: [CKA]
cards:
  - q: Question, en Markdown simple (`code`, **gras**)
    a: Réponse
quiz:
  - q: La question
    options: [Réponse A, Réponse B, Réponse C]
    answer: 1           # index de la bonne réponse, à partir de 0
    explain: Pourquoi, affiché après la réponse
---

Le corps de la fiche, en Markdown : titres ##, listes, tableaux, blocs de code…

> **Piège classique.** Une citation devient un encadré rouge.
```

Astuces :

- Mets les questions ou réponses entre guillemets si elles contiennent `:` suivi d'un espace (règle du format YAML).
- Pour comparer deux notions côte à côte : `<div class="compare"><div><b>A</b><span>…</span></div><div><b>B</b><span>…</span></div></div>`.
- La progression d'une carte est liée au texte de sa question : la reformuler la fait repartir de zéro. Si tu sais qu'une question va évoluer, donne-lui un `id:` fixe dès sa création.

## Les schémas

Les schémas des fiches sont des dessins SVG écrits directement dans le Markdown, entre deux commentaires `<!-- schema:nom -->` et `<!-- /schema:nom -->`. Ils ne contiennent aucune couleur en dur : chaque forme porte une classe (`dg-box`, `dg-l`…) stylée dans `global.css` avec les variables du thème. Un même schéma s'affiche donc bien en Tech (sombre) comme en Perso (papier), et prend la couleur du module grâce à `--c`.

Ils sont générés par les scripts Python de `tools/schemas/` :

- `svg.py` : les briques (boîte, zone, flèche, texte) ;
- `inject.py` : place le schéma dans la fiche, ou le remplace s'il existe déjà ;
- `sch_*.py` : les schémas, un fichier par groupe de modules.

Pour modifier un schéma, change son script puis relance-le, par exemple `python3 tools/schemas/sch_k8s.py`. Les fiches ne sont touchées qu'entre leurs deux commentaires : le reste de ton texte n'est jamais modifié.

Les schémas s'animent quand ils arrivent à l'écran (flèches qui se dessinent, boîtes qui apparaissent). Si macOS est réglé sur « Réduire les animations », ils s'affichent directement.

## Les synthèses

Chaque module peut avoir une page d'aide-mémoire : `/<module>/synthese/`. La liste de toutes les synthèses est sur `/syntheses/` (entrée « Synthèses » du menu).

- Le texte est dans `src/content/syntheses/<module>.md`, avec le même nom de fichier que le module. Un fichier absent = pas de bouton « Synthèse » sur le module.
- Le sommaire de gauche est construit à partir des titres `##` du fichier, et suit la section en cours de lecture.
- Pour le japonais, la page ajoute l'**explorateur de kanji** (`src/components/KanjiExplorer.astro`). Les kanji sont dans `src/data/kanji.ts`, une ligne par kanji : `kanji|on|kun|sens`. Pour ajouter le N3, il suffit de remplir la liste `N3` du même fichier : l'onglet s'active tout seul.

## Le parcours et le sommaire

Sur ordinateur, le parcours d'un module et le sommaire d'une synthèse restent à l'écran et ne bougent jamais quand on fait défiler le contenu :

- la colonne de gauche (`.path-col`) est en `position: sticky` avec une hauteur fixe, celle de la fenêtre (`calc(100vh - 56px)`). Son bas est donc toujours visible ;
- la liste à l'intérieur a sa propre barre de défilement (`overflow-y: auto`), et `overscroll-behavior: contain` empêche la page de défiler quand on arrive au bout de la liste ;
- le fil d'Ariane et le titre sont dans la colonne de droite (`.main-col`) : la colonne de gauche commence tout en haut et n'a rien au-dessus d'elle qui pourrait la décaler.

Il n'y a plus de script de calcul de hauteur : tout est en CSS (`src/styles/global.css`, bloc `@media (min-width: 901px)`). Sur mobile, les colonnes s'empilent et le contenu passe au-dessus du parcours.

## Les couleurs des synthèses

Les pages de synthèse ne demandent rien de spécial dans le Markdown : la couleur vient du CSS (fin de `src/styles/global.css`). Chaque section (un titre `##` et tout ce qui le suit) reçoit une couleur `--s`, qui tourne sur une palette de six teintes ; elle colore le numéro de section, l'en-tête des tableaux, leur première colonne, les blocs de code et le gras. Le sommaire reprend les mêmes couleurs. Une marge vide en bas de page (`.syn-end`) permet à la dernière section de remonter en haut de l'écran quand on clique dessus dans le sommaire.

## L'explorateur de kanji

La synthèse de japonais inclut `src/components/KanjiExplorer.astro`, alimenté par `src/data/kanji.ts` (une ligne `kanji|on|kun|sens` par kanji, rangés par niveau JLPT). Les onglets de niveau et la recherche masquent les tuiles avec l'attribut `hidden`. Une règle globale `[hidden] { display: none !important; }` garantit que ce masquage l'emporte sur les `display: grid` ou `flex` des composants : c'était la cause du bug où le choix de niveau et la recherche semblaient sans effet.

## La sécurité

Le site n'a ni serveur, ni compte, ni base de données : il n'y a rien à pirater côté serveur. Les risques sont dans le navigateur, et chaque protection est simple.

- **CSP (Content Security Policy)** : `astro.config.mjs` ajoute dans chaque page une règle qui dit au navigateur d'où le contenu a le droit de venir. Les scripts sont autorisés un par un par leur empreinte : un script glissé dans une page (une attaque XSS) ne s'exécuterait pas. Seules les polices Google sont autorisées à l'extérieur. Les styles en ligne restent permis, car Shiki (la coloration du code) en a besoin.
- **Les données injectées dans les pages** : les cartes et le quiz sont mis dans la page en JSON via `jsonForScript()` (`src/lib/content.ts`), qui échappe le caractère `<`. Une carte qui contiendrait `</script>` ne peut donc pas casser la page.
- **La palette ⌘K** construit sa liste de résultats en HTML : tout texte y passe par `esc()` (`src/lib/html.ts`).
- **La progression** (localStorage ou fichier importé) est relue par `sanitize()` dans `src/lib/progress.ts` : seuls les champs attendus, avec le bon type, sont gardés. Le lien « reprendre » n'accepte qu'une adresse interne au site (jamais `javascript:`, ni `//autre-site` ou `/\autre-site`, que les navigateurs lisent comme un autre site). Les clés spéciales comme `__proto__` sont ignorées. Un fichier importé de plus de 5 Mo est refusé.
- **Les dépendances** sont peu nombreuses (Astro et marked), aux versions exactes de `package-lock.json`. La pipeline lance `npm audit` et s'arrête en cas de faille sérieuse, et Dependabot propose les mises à jour.

Limite connue : GitHub Pages ne permet pas d'ajouter des en-têtes HTTP. La CSP passe donc par une balise `<meta>`, ce qui ne permet pas d'empêcher l'affichage du site dans une iframe d'un autre site. Ce n'est pas grave ici : il n'y a ni bouton sensible ni donnée à voler.

## Les liens internes

Tous les liens internes passent par `url()` (`src/lib/url.ts`) : `url('/tech/')`. En local, cela donne `/tech/` ; sur GitHub Pages, où le site vit dans un sous-dossier, cela donne `/my-learning-hub/tech/`. Le préfixe vient de `base` dans `astro.config.mjs`, rempli par la pipeline. Si tu écris un nouveau lien dans une page `.astro`, utilise `url()` ; un lien écrit en dur `/...` marcherait en local mais pas en ligne.

## La pipeline de déploiement

Le fichier `.github/workflows/deploy.yml` est une pipeline GitHub Actions. Elle se lance toute seule :

- **sur une pull request** : elle installe les dépendances, lance `npm audit` et construit le site. Rien n'est publié ; tu vois juste si tout passe (coche verte) ou non.
- **sur un push sur `main`** (ou à la main, onglet *Actions* puis *Run workflow*) : mêmes étapes, puis publication sur GitHub Pages. Il faut environ une minute.

Ce qui la rend sûre :

- **Aucun secret** : la publication utilise un jeton temporaire fourni par GitHub (OIDC), valable pour ce seul déploiement. Il n'y a pas de mot de passe à stocker ni à faire fuiter.
- **Droits minimaux** : par défaut le workflow peut seulement lire le code. Seul le job `deploy` reçoit le droit d'écrire sur Pages, et il ne tourne que sur `main`, jamais sur une pull request.
- **Actions figées** : chaque action externe est référencée par son empreinte (SHA) et non par un tag, qui peut être déplacé par quelqu'un d'autre. Dependabot (`.github/dependabot.yml`) ouvre une PR chaque semaine quand une nouvelle version sort.
- **Installation contrôlée** : `npm ci --ignore-scripts` installe exactement les versions du lockfile, sans laisser les paquets exécuter de code à l'installation.

## Les contrôles automatiques

Trois workflows tournent sur GitHub, en plus de Dependabot :

| Workflow | Quand | Ce qu'il vérifie |
| --- | --- | --- |
| `deploy.yml` | chaque PR et chaque push sur `main` | `npm audit` (failles connues), `npm run check` (types TypeScript et pages `.astro`), le build, puis `npm run check:links` : chaque lien interne du site construit, avec le préfixe de GitHub Pages, doit mener à une page qui existe. Un seul échec et rien n'est publié. |
| `codeql.yml` | chaque PR, chaque push sur `main`, et chaque lundi | **CodeQL**, l'analyseur de sécurité de GitHub : il cherche dans le code TypeScript et dans les workflows les erreurs qui mènent à une faille (HTML injecté sans échappement, workflow qui exécute du texte venu d'une PR…). Les alertes sont dans *Security → Code scanning*. |
| `dependency-review.yml` | chaque PR | Compare les dépendances avant et après la PR, et la bloque si elle ajoute un paquet avec une faille connue sérieuse. Utile surtout pour les PR de Dependabot. |

Les trois workflows ont été passés à **zizmor**, un vérificateur de sécurité des workflows GitHub Actions (droits trop larges, actions non figées, injection de texte dans les commandes) : aucun problème trouvé.

Réglages à activer une fois dans le dépôt GitHub (*Settings*) :

- *Code security* : **Secret scanning** et **Push protection**. GitHub refuse alors un push qui contiendrait un mot de passe ou une clé d'API.
- *Rules → Rulesets → New branch ruleset* sur `main` : cocher **Restrict deletions** et **Block force pushes**, pour qu'un historique publié ne puisse être ni effacé ni réécrit. La règle « Require status checks to pass » n'est utile que si tu passes par des pull requests : elle bloquerait tes push directs sur `main`.

### Mise en route (une seule fois)

1. Pousse le dépôt sur GitHub (avec le dossier `.github/`).
2. Dans le dépôt : *Settings → Pages → Build and deployment → Source* : choisis **GitHub Actions**.
3. Conseillé : *Settings → Environments → github-pages* : limite les déploiements à la branche `main` (normalement déjà réglé par GitHub).
4. Fais un push sur `main` : le site apparaît à l'adresse `https://<ton-compte>.github.io/my-learning-hub/` (lien aussi visible dans l'onglet *Actions*).

### Publier une version

Une version est un **tag** git sur un commit de `main`, par exemple `v1.0.0`. Le site en ligne ne change pas (il suit toujours `main`), mais le tag marque un état stable auquel revenir. Avant de tagger : pipeline verte sur `main`, numéro mis à jour dans `package.json` et une entrée dans `CHANGELOG.md`. Ensuite, sur GitHub : *Releases → Draft a new release*, crée le tag `v1.0.0` sur `main` et colle l'entrée du changelog.

À savoir : sur GitHub Pages, le site est **public**, même si le dépôt est privé (sauf avec une offre GitHub payante). Ta progression, elle, reste dans ton navigateur et n'est jamais envoyée en ligne. Ta progression locale (`localhost`) et celle du site en ligne sont séparées : utilise *Exporter / Importer* pour passer de l'une à l'autre.

## La recherche

La palette (⌘K, Ctrl+K, ou le bouton « Recherche » du menu, et la loupe sur téléphone) cherche à deux endroits :

1. **Les pages** (modules, fiches, synthèses) : leur titre. La liste vient de `/palette.json` (`src/pages/palette.json.ts`), téléchargé à la première ouverture de la palette.
2. **Le texte de toutes les fiches**, dès 3 lettres tapées. Au build, `src/pages/search.json.ts` appelle `buildSearchIndex()` (`src/lib/search.ts`), qui découpe chaque fiche à ses titres `##`, retire la mise en forme et produit `/search.json` : une entrée par section, avec le lien vers le bon titre de la fiche. Les cartes de révision sont incluses.

Ce fichier pèse environ 1,4 Mo (environ 450 Ko compressé) : le navigateur ne le télécharge qu'à la **première recherche**, puis le garde en mémoire. Les pages restent donc aussi légères qu'avant. La recherche ignore les accents et la casse, exige que tous les mots soient présents, et classe en premier les sections dont le titre contient les mots.

Pourquoi pas un outil comme Pagefind ? Il serait plus puissant sur un très gros site, mais il ajoute une dépendance et une étape de build, et il a besoin de WebAssembly, qu'il faudrait autoriser dans la CSP. Pour quelques centaines de sections, un index JSON fait maison suffit.

## Le poids des pages

Les compteurs (accueil, menu, cartes de module, tableau de bord) ont besoin de la liste de tous les modules, fiches et cartes. Cette liste n'est plus recopiée dans chaque page : elle est générée une fois dans `/hub-index.json` (`src/pages/hub-index.json.ts`) et lue par `loadIndex()` (`src/lib/stats.ts`). Le navigateur la télécharge une fois puis la garde en cache. Résultat : le site est passé de 39 Mo à environ 9 Mo à l'époque (environ 15 Mo aujourd'hui, avec 345 fiches), et une page pèse en moyenne 25 Ko au lieu de 145 Ko.

Seules trois pages embarquent encore leurs données, parce qu'elles en ont besoin en entier : Réviser (toutes les cartes), Quiz (toutes les questions) et Progression (le texte des cartes difficiles).

## Les certifications

La page **Certifications** (`/certifications/`) organise les fiches existantes autour des examens visés, sans dupliquer le contenu. Chaque examen est un fichier `src/content/certifications/<id>.md` :

- l'en-tête décrit le **format** de l'examen (durée, seuil, validité…), le lien officiel, la date de vérification, et les **domaines** du programme avec leur poids, la liste des fiches qui les couvrent (`module/fichier`) et, dans `missing`, ce que le site ne couvre pas encore ;
- le texte en dessous est la synthèse « jour J » : ce qui est vérifié, les pièges, ce qu'il faut savoir par cœur, la stratégie.

Une fiche citée qui n'existe pas fait échouer le build (`certFiches()` dans `src/lib/content.ts`), ce qui évite les liens morts après un renommage.

Le navigateur calcule la préparation (fiches lues + cartes maîtrisées, comme pour les modules) et coche les fiches lues dans chaque domaine. **Réviser** et **Quiz** acceptent `?cert=<id>` pour ne garder que les cartes et questions des fiches liées ; les filtres de ces pages proposent aussi chaque certification. Les synthèses « jour J » sont listées sur la page Synthèses et incluses dans la recherche.

Pour ajouter une certification, copie un fichier existant, change l'en-tête et les fiches, et c'est tout : la page, les filtres et la recherche suivent.
