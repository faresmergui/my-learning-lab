---
title: GitLab CI en pratique
chapter: 3
order: 1
duration: 9
level: intermédiaire
tags:
- gitlab
cards:
- q: Différence entre `cache` et `artifacts` dans GitLab CI ?
  a: '`cache` **accélère** les jobs (dépendances comme `node_modules`), sans garantie qu''il soit là. `artifacts` **transmet des fichiers** entre jobs et étapes, de façon fiable.'
- q: À quoi sert le mot-clé `needs` ?
  a: 'À créer un **graphe de dépendances** : le job démarre dès que les jobs listés sont finis, sans attendre la fin de toute l''étape précédente.'
- q: Pourquoi utiliser `rules` plutôt que `only/except` ?
  a: '`rules` est plus expressif (conditions sur variables, fichiers modifiés, `when`) et c''est la syntaxe recommandée. `only/except` n''est plus développé.'
- q: Comment lancer un job uniquement sur une merge request ?
  a: '`rules: - if: $CI_PIPELINE_SOURCE == "merge_request_event"`.'
- q: Différence entre une variable **protected** et **masked** ?
  a: '**Protected** : disponible seulement sur les branches et tags protégés. **Masked** : sa valeur est cachée dans les logs. Un secret de prod est souvent les deux.'
- q: À quoi servent `extends` et `include` ?
  a: '`extends` réutilise un job modèle (souvent caché, nom commençant par `.`). `include` importe des fichiers YAML d''autres fichiers ou projets.'
- q: Comment empêcher deux déploiements simultanés sur le même environnement ?
  a: 'Avec `resource_group: production` : les jobs du même groupe s''exécutent **un par un**.'
quiz:
- q: Ton job `test` ne trouve pas le binaire construit par le job `build`. Que manque-t-il le plus probablement ?
  options:
  - Un `cache`
  - 'Des `artifacts: paths` dans `build`'
  - Un `image` différent
  - Un `tag` de runner
  answer: 1
  explain: Chaque job démarre dans un environnement propre. Pour transmettre un fichier de manière fiable, il faut le déclarer en artefact.
- q: Tu veux que le job `deploy-prod` ne parte qu'à la main, et seulement sur `main`. Quelle règle ?
  options:
  - '`when: always`'
  - '`rules: - if: $CI_COMMIT_BRANCH == "main"` avec `when: manual`'
  - '`only: tags`'
  - '`allow_failure: true`'
  answer: 1
  explain: 'Une règle qui filtre sur la branche, combinée à `when: manual`, ajoute un bouton de lancement dans le pipeline.'
- q: Ton pipeline se lance deux fois pour chaque push sur une branche avec MR ouverte. Comment l'éviter ?
  options:
  - Supprimer les MR
  - 'Ajouter des `workflow: rules` qui choisissent entre pipeline de branche et de MR'
  - 'Ajouter `needs: []`'
  - 'Mettre `interruptible: true`'
  answer: 1
  explain: 'Les `workflow: rules` décident si un pipeline est créé. On y évite les doublons branche + MR.'
---

GitLab CI se pilote entièrement depuis `.gitlab-ci.yml` à la racine du dépôt.

> **GitLab** est une plateforme d'hébergement de dépôts Git (comme GitHub), qu'on peut utiliser sur gitlab.com ou installer chez soi. **GitLab CI** est son moteur de CI/CD intégré : il lit un fichier du dépôt et lance les étapes décrites à chaque push.


> **Les termes et outils cités dans cette fiche.**
> - **CD** : le déploiement (ou la livraison) continu : ce qui a passé la CI est déployé automatiquement.
> - **branche** : une ligne de développement parallèle dans Git.
> - **MR** : merge request : la demande de fusion d'une branche dans GitLab, avec revue de code (pull request sur GitHub).
> - **artefact** : un fichier produit par une étape du pipeline (binaire, image, rapport) et transmis aux suivantes.
> - **OIDC** : OpenID Connect, le standard de connexion par un fournisseur d'identité, qui délivre des jetons signés.

## Un pipeline complet

```yaml
stages: [test, build, deploy]

workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH

.node:
  image: node:22
  cache:
    key:
      files: [package-lock.json]
    paths: [node_modules/]

lint:
  extends: .node
  stage: test
  script: [npm ci, npm run lint]

build:
  extends: .node
  stage: build
  script: [npm ci, npm run build]
  artifacts:
    paths: [dist/]

deploy-prod:
  stage: deploy
  needs: [build]
  resource_group: production
  environment: production
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual
  script: ./deploy.sh dist/
```

<!-- schema:dag -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Étapes et needs dans GitLab CI" style="--minw:560px"><defs><marker id="g19-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g19-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g19-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g19-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="16" y="14" width="200" height="222" rx="12" class="dg-zone "/><text x="28" y="32" class="dg-zl" text-anchor="start">stage test</text><g class="dg-box dg-pop" style="--d:0"><rect x="30" y="50" width="172" height="50" rx="9"/></g><text x="116.0" y="80.0" class="dg-t" text-anchor="middle" style="--d:0">lint</text><g class="dg-box dg-pop" style="--d:1"><rect x="30" y="124" width="172" height="50" rx="9"/></g><text x="116.0" y="154.0" class="dg-t" text-anchor="middle" style="--d:1">unit</text><rect x="246" y="14" width="200" height="222" rx="12" class="dg-zone "/><text x="258" y="32" class="dg-zl" text-anchor="start">stage build</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="260" y="50" width="172" height="50" rx="9"/></g><text x="346.0" y="80.0" class="dg-t" text-anchor="middle" style="--d:2">build</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="260" y="124" width="172" height="50" rx="9"/></g><text x="346.0" y="154.0" class="dg-t" text-anchor="middle" style="--d:3">docker</text><rect x="476" y="14" width="200" height="222" rx="12" class="dg-zone "/><text x="488" y="32" class="dg-zl" text-anchor="start">stage deploy</text><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="490" y="50" width="172" height="50" rx="9"/></g><text x="576.0" y="72.0" class="dg-t" text-anchor="middle" style="--d:4">deploy-prod</text><text x="576.0" y="90.0" class="dg-s" text-anchor="middle" style="--d:4">manuel · main</text><path d="M202 75 L258 75" class="dg-l c" marker-end="url(#g19-c)"/><text x="230.0" y="69.0" class="dg-s" text-anchor="middle">needs</text><path d="M432 75 L488 75" class="dg-l c" marker-end="url(#g19-c)"/><text x="460.0" y="69.0" class="dg-s" text-anchor="middle">needs</text><text x="116" y="220" class="dg-s" text-anchor="middle">cache : node_modules</text><text x="346" y="220" class="dg-s" text-anchor="middle">artifacts : dist/</text><text x="576" y="220" class="dg-s" text-anchor="middle">resource_group</text></svg><figcaption>Avec needs, build démarre dès que lint a fini, sans attendre unit.</figcaption></figure>
<!-- /schema:dag -->

## Les mots-clés à connaître

| Mot-clé | Rôle |
| --- | --- |
| `rules` | quand le job existe et comment il se lance |
| `needs` | démarrer sans attendre toute l'étape |
| `cache` | accélérer, sans garantie |
| `artifacts` | transmettre des fichiers, fiable |
| `extends`, `include` | réutiliser, factoriser |
| `environment` | suivre les déploiements dans GitLab |
| `resource_group` | un déploiement à la fois |

## Comprendre l'exécution

Un **pipeline** est lancé à chaque événement (push, merge request, tag, planification). Il contient des **jobs**, regroupés en **étapes** (`stages`). Par défaut, les étapes s'enchaînent : tous les jobs de `test` doivent réussir avant que `build` commence.

Chaque job tourne sur un **runner** (une machine qui exécute les jobs), dans un **conteneur neuf** créé à partir de l'`image` indiquée. Le dépôt y est cloné, le `script` exécuté ligne par ligne, et si une ligne renvoie une erreur, le job échoue. À la fin, le conteneur est détruit : **rien ne persiste** d'un job à l'autre, sauf ce que tu transmets explicitement.

D'où la différence fondamentale entre les deux mécanismes de transmission :

| | `cache` | `artifacts` |
| --- | --- | --- |
| Rôle | accélérer (ne pas retélécharger les dépendances) | transmettre un résultat au job suivant |
| Garantie | aucune : peut être absent ou périmé | oui, pour les jobs des étapes suivantes |
| Exemple | `node_modules/`, cache pip | `dist/`, rapport de tests, plan Terraform |

Le job doit donc toujours **fonctionner sans le cache** (d'où le `npm ci` même quand `node_modules` est en cache), juste plus lentement.

## Lire le pipeline d'exemple

- **`workflow: rules`** décide si un pipeline est créé : ici, pour une merge request, ou pour une branche **sans** merge request ouverte. Sans ça, un push sur une branche avec MR créerait deux pipelines identiques.
- **`.node`** commence par un point : c'est un **modèle** caché, pas un job. `extends: .node` en hérite (image et cache), pour ne pas le répéter.
- **`needs: [build]`** crée un lien direct : `deploy-prod` démarre dès que `build` a fini, sans attendre les autres jobs de l'étape, et récupère ses artefacts.
- **`rules` avec `when: manual`** : le job n'existe que sur `main`, et attend un clic.
- **`resource_group: production`** : deux déploiements en prod ne peuvent jamais tourner en même temps, même si deux pipelines arrivent coup sur coup.
- **`environment`** : GitLab garde l'historique de ce qui a été déployé où, et permet de redéployer une version précédente.

## Les variables et les secrets

GitLab fournit des variables prédéfinies (`$CI_COMMIT_SHA`, `$CI_COMMIT_BRANCH`, `$CI_PIPELINE_SOURCE`…) et tu peux en définir dans les paramètres du projet. Pour un secret, coche **masquée** (cachée dans les logs) et **protégée** (disponible seulement sur les branches protégées, donc pas sur une MR venue de n'importe qui). Mieux encore pour le cloud : l'authentification OIDC avec `id_tokens`, qui évite de stocker une clé (fiche sur les secrets du module Sécurité).

> **À retenir.** Cache pour la vitesse, artefacts pour transmettre. Et `rules` partout, plus de `only/except`.
