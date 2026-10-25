---
title: Les principes du CI/CD
chapter: 2
order: 1
duration: 9
level: intermédiaire
tags:
- ci/cd
cards:
- q: Différence entre Continuous Delivery et Continuous Deployment ?
  a: '**Delivery** : chaque commit produit un artefact prêt à partir en prod, mais la mise en prod reste **manuelle**. **Deployment** : la mise en prod est **automatique** si tout passe.'
- q: Que veut dire « build once, deploy many » ?
  a: On construit l'artefact (image Docker, binaire) **une seule fois**, puis on promeut **le même** de dev à prod. Seule la configuration change entre environnements.
- q: Pourquoi taguer les images avec le SHA du commit plutôt que `latest` ?
  a: 'Le SHA est **immuable et traçable** : on sait exactement quel code tourne et on peut revenir en arrière. `latest` change sans prévenir.'
- q: Qu'est-ce que le principe « fail fast » dans un pipeline ?
  a: Mettre les vérifications **rapides et fréquemment en échec** en premier (lint, tests unitaires) pour un retour en quelques minutes, avant les étapes longues.
- q: Qu'est-ce que le trunk-based development ?
  a: Tout le monde intègre sur `main` **très souvent** (au moins une fois par jour), avec des branches courtes et des feature flags pour le code pas encore prêt.
- q: Livraison continue vs déploiement continu
  a: '**Livraison** : chaque version est prête, un humain décide. **Déploiement** : chaque version qui passe part en prod automatiquement.'
- q: Les 4 mesures DORA
  a: Fréquence de déploiement, délai de mise en production, taux d'échec des changements, temps de restauration.
- q: Pourquoi les tests instables (flaky) sont-ils dangereux ?
  a: Ils apprennent à l'équipe à **ignorer le rouge**, et une vraie régression finit par passer.
quiz:
- q: Ton pipeline reconstruit l'image Docker à chaque environnement (dev, staging, prod). Quel est le risque ?
  options:
  - Aucun
  - La prod peut tourner un artefact différent de celui testé en staging
  - Les tests sont plus lents
  - Le registry sera plein
  answer: 1
  explain: Deux builds du même commit peuvent différer (dépendances, image de base mise à jour). On teste un artefact, on déploie ce même artefact.
- q: Ton pipeline dure 40 minutes et les développeurs ne regardent plus les résultats. Première action ?
  options:
  - Supprimer les tests
  - Paralléliser et placer lint et tests unitaires en premier
  - Lancer le pipeline seulement la nuit
  - Passer en Continuous Deployment
  answer: 1
  explain: Un retour rapide est la condition pour que la CI serve. On parallélise, on met en cache et on met les vérifications rapides en tête.
---

**CI** veut dire *Continuous Integration* (intégration continue) : à chaque modification poussée dans Git, un serveur construit le projet et lance les tests automatiquement. **CD** veut dire *Continuous Delivery* ou *Deployment* (livraison ou déploiement continu) : ce qui a passé les tests est prêt à partir en production, voire y part tout seul. Les outils qui font tourner ces étapes s'appellent des **moteurs de CI** : GitLab CI, GitHub Actions, Jenkins. L'enchaînement des étapes s'appelle un **pipeline**.

Le CI/CD n'est pas un outil, c'est une façon de livrer : **petit, souvent, automatiquement**.


> **Les termes et outils cités dans cette fiche.**
> - **SHA** : une famille de fonctions de hachage : une empreinte unique calculée à partir d'un contenu.
> - **commit** : un instantané enregistré des modifications dans Git, avec un message et un auteur.
> - **MR** : merge request : la demande de fusion d'une branche dans GitLab, avec revue de code (pull request sur GitHub).
> - **branche** : une ligne de développement parallèle dans Git.

## Les trois niveaux

<!-- schema:niveaux -->
<figure class="diagram"><svg viewBox="0 0 680 200" role="img" aria-label="CI, Continuous Delivery, Continuous Deployment" style="--minw:560px"><defs><marker id="g18-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g18-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g18-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g18-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="100" width="98" height="54" rx="9"/></g><text x="63.0" y="132.0" class="dg-t" text-anchor="middle" style="--d:0">commit</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="125" y="100" width="98" height="54" rx="9"/></g><text x="174.0" y="124.0" class="dg-t" text-anchor="middle" style="--d:1">lint + tests</text><text x="174.0" y="142.0" class="dg-s" text-anchor="middle" style="--d:1">quelques min</text><path d="M112 127 L124 127" class="dg-l c" marker-end="url(#g18-c)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="236" y="100" width="98" height="54" rx="9"/></g><text x="285.0" y="124.0" class="dg-t" text-anchor="middle" style="--d:2">build</text><text x="285.0" y="142.0" class="dg-s" text-anchor="middle" style="--d:2">image:3f2a9c1</text><path d="M223 127 L235 127" class="dg-l c" marker-end="url(#g18-c)"/><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="347" y="100" width="98" height="54" rx="9"/></g><text x="396.0" y="124.0" class="dg-t" text-anchor="middle" style="--d:3">scan</text><text x="396.0" y="142.0" class="dg-s" text-anchor="middle" style="--d:3">deps, image</text><path d="M334 127 L346 127" class="dg-l c" marker-end="url(#g18-c)"/><g class="dg-box dg-pop" style="--d:4"><rect x="458" y="100" width="98" height="54" rx="9"/></g><text x="507.0" y="124.0" class="dg-t" text-anchor="middle" style="--d:4">staging</text><text x="507.0" y="142.0" class="dg-s" text-anchor="middle" style="--d:4">tests intégr.</text><path d="M445 127 L457 127" class="dg-l c" marker-end="url(#g18-c)"/><g class="dg-box dg-a dg-pop" style="--d:5"><rect x="569" y="100" width="98" height="54" rx="9"/></g><text x="618.0" y="124.0" class="dg-t" text-anchor="middle" style="--d:5">prod</text><text x="618.0" y="142.0" class="dg-s" text-anchor="middle" style="--d:5">même image</text><path d="M556 127 L568 127" class="dg-l c" marker-end="url(#g18-c)"/><path d="M125 80 L445 80" class="dg-l c" marker-end="url(#g18-c)" marker-start="url(#g18-c)"/><text x="285.0" y="72" class="dg-ct" text-anchor="middle">CI : à chaque commit</text><path d="M125 40 L556 40" class="dg-l ok" marker-end="url(#g18-ok)" marker-start="url(#g18-ok)"/><text x="340.5" y="32" class="dg-okt" text-anchor="middle">Continuous Delivery : prêt pour la prod, bouton manuel</text><path d="M125 184 L666 184" class="dg-l a" marker-end="url(#g18-a)" marker-start="url(#g18-a)"/><text x="395.5" y="176" class="dg-at" text-anchor="middle">Continuous Deployment : jusqu&#x27;en prod, automatiquement</text></svg><figcaption>La différence se joue sur la dernière marche : la mise en prod est-elle manuelle ou automatique ?</figcaption></figure>
<!-- /schema:niveaux -->

## Un pipeline type

1. **Lint et tests unitaires** : quelques minutes, le premier filtre.
2. **Build** de l'artefact, tagué avec le SHA du commit.
3. **Scan** sécurité (dépendances, image).
4. **Tests d'intégration** sur un environnement éphémère.
5. **Déploiement** en staging, puis promotion du **même** artefact en prod.

## Les bonnes pratiques

- **Pipeline as code** : la définition vit dans le dépôt, versionnée et relue comme le reste.
- **Artefact immuable** : `registry/app:3f2a9c1`, jamais `latest` en prod.
- **Configuration externe** : variables d'environnement, ConfigMaps, secrets, pas de rebuild par environnement.
- **Pipeline rapide** : visez moins de 10 minutes pour le retour d'une MR.

## Intégration, livraison, déploiement

- **Intégration continue (CI)** : chaque changement est fusionné souvent dans la branche principale, et **vérifié automatiquement** (build, tests). Le but est de découvrir les conflits et régressions tôt, quand ils sont petits.
- **Livraison continue** : chaque version qui passe la CI est **prête** à partir en production, mais un humain décide quand.
- **Déploiement continu** : chaque version qui passe la CI **part** en production sans intervention.

On peut faire de la livraison continue sans déploiement continu : c'est même le cas le plus courant.

## Pourquoi « petit et souvent »

Un changement petit est **facile à relire, à tester et à annuler**. Quand une mise en production contient trois semaines de travail et casse, il faut trouver lequel des cinquante commits est fautif. Quand elle en contient un, la cause est évidente. Livrer souvent réduit donc le risque, contrairement à l'intuition.

## Les mesures DORA

Quatre indicateurs, issus des travaux DORA, servent à mesurer une chaîne de livraison :

| Mesure | Question |
| --- | --- |
| Fréquence de déploiement | À quelle fréquence livre-t-on en production ? |
| Délai de mise en production | Combien de temps entre un commit et la production ? |
| Taux d'échec des changements | Quelle part des déploiements provoque un incident ? |
| Temps de restauration | Combien de temps pour rétablir le service après un incident ? |

Les équipes les plus performantes sont bonnes **sur les quatre à la fois** : vitesse et stabilité ne s'opposent pas.

## Ce qui ralentit un pipeline

- Tests lents lancés en série : les paralléliser, et lancer les plus rapides d'abord.
- Dépendances téléchargées à chaque fois : utiliser le **cache**.
- Build complet pour un changement de documentation : règles de déclenchement par chemin.
- Tests instables (« flaky ») : ils apprennent à l'équipe à ignorer le rouge. Les corriger ou les isoler vite.

> **À retenir.** Un artefact, construit une fois, testé, puis promu tel quel. C'est la base de tout le reste.
