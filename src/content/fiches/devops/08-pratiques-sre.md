---
title: 'Pratiques SRE : SLO et budget d''erreur'
chapter: 8
order: 1
duration: 8
level: intermédiaire
tags:
- sre
cards:
- q: Différence entre SLI, SLO et SLA ?
  a: '**SLI** : l''indicateur mesuré (taux de requêtes réussies). **SLO** : l''objectif interne (99,9 % sur 30 jours). **SLA** : l''engagement contractuel, avec pénalités, toujours moins strict que le SLO.'
- q: Qu'est-ce qu'un budget d'erreur ?
  a: 'La part d''échec **autorisée** par le SLO : 100 % - 99,9 % = 0,1 %. Tant qu''il reste du budget, on livre. S''il est épuisé, on priorise la fiabilité.'
- q: Combien d'indisponibilité permet un SLO de 99,9 % sur 30 jours ?
  a: Environ **43 minutes** (30 j × 24 h × 60 min × 0,001 = 43,2 min).
- q: Qu'est-ce que le toil ?
  a: Le travail **manuel, répétitif, automatisable** et sans valeur durable (redémarrer un service à la main chaque semaine). Le SRE cherche à le limiter.
- q: Qu'est-ce qu'un postmortem « blameless » ?
  a: Une analyse d'incident qui cherche les **causes systémiques** (process, outils, alertes) plutôt qu'un coupable, pour que chacun ose dire ce qui s'est passé.
- q: Qu'est-ce qu'une alerte sur le burn rate ?
  a: Une alerte qui se déclenche quand le budget d'erreur est **consommé trop vite** (par exemple 14 fois le rythme normal sur 1 h), plutôt que sur un seuil fixe.
quiz:
- q: Ton équipe a épuisé son budget d'erreur à mi-mois. Que prévoit la pratique SRE ?
  options:
  - Rien, on continue
  - Geler les nouvelles fonctionnalités et prioriser la fiabilité
  - Augmenter le SLO
  - Baisser le SLA
  answer: 1
  explain: 'Le budget d''erreur sert de règle de décision partagée entre dev et ops : épuisé, on investit dans la stabilité jusqu''à le reconstituer.'
- q: Quel SLI est le plus pertinent pour une API ?
  options:
  - Le CPU des nœuds
  - La proportion de requêtes réussies en moins de 300 ms
  - Le nombre de pods
  - L'espace disque
  answer: 1
  explain: 'Un bon SLI mesure ce que vit l''utilisateur : disponibilité et latence des requêtes, pas les ressources internes.'
---

Le SRE (Site Reliability Engineering) traite la fiabilité comme un problème d'ingénierie, avec des chiffres.


> **Les termes et outils cités dans cette fiche.**
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.

## SLI, SLO, SLA

```
 SLI   ce qu'on mesure        requêtes OK / requêtes totales
 SLO   l'objectif interne     99,9 % sur 30 jours glissants
 SLA   le contrat client      99,5 %, avec pénalités
```

## Le budget d'erreur

| SLO | Indisponibilité autorisée sur 30 jours |
| --- | --- |
| 99 % | 7 h 12 |
| 99,5 % | 3 h 36 |
| 99,9 % | 43 min |
| 99,99 % | 4 min 19 |

Chaque neuf en plus coûte beaucoup plus cher. **100 % n'est jamais le bon objectif.**

<!-- schema:budget -->
<figure class="diagram"><svg viewBox="0 0 680 260" role="img" aria-label="La consommation du budget d&#x27;erreur" style="--minw:560px"><defs><marker id="g24-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g24-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g24-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g24-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><line x1="60" y1="210.0" x2="630" y2="210.0" class="dg-court"/><line x1="60" y1="210.0" x2="60" y2="30.0" class="dg-court"/><text x="52" y="214.0" class="dg-s" text-anchor="end">0 %</text><text x="52" y="124.0" class="dg-s" text-anchor="end">50 %</text><text x="52" y="34.0" class="dg-s" text-anchor="end">100 %</text><text x="60" y="228.0" class="dg-s" text-anchor="middle">j0</text><text x="250" y="228.0" class="dg-s" text-anchor="middle">j10</text><text x="440" y="228.0" class="dg-s" text-anchor="middle">j20</text><text x="630" y="228.0" class="dg-s" text-anchor="middle">j30</text><path d="M60 30.0 L 630 210.0" class="dg-l dash"/><text x="459" y="170.4" class="dg-s" text-anchor="start">rythme régulier</text><path d="M60 30.0 L 212 51.6 L 231 138.0 L 364 159.6 L 392.5 210.0" class="dg-l a thick draw" pathLength="1"/><circle cx="231" cy="138.0" r="5" class="dg-dot dg-a dg-pop"/><text x="243" y="158.0" class="dg-at" text-anchor="start">incident : alerte burn rate</text><text x="386.5" y="188.0" class="dg-at" text-anchor="end">budget épuisé :</text><text x="386.5" y="203.0" class="dg-at" text-anchor="end">gel des features</text><text x="64" y="20" class="dg-s" text-anchor="start">budget d&#x27;erreur restant · SLO 99,9 % sur 30 jours (43 min)</text></svg><figcaption>Une alerte sur la vitesse de consommation prévient bien avant que le budget soit vide.</figcaption></figure>
<!-- /schema:budget -->

## Les rituels

- **Alertes sur le burn rate** plutôt que sur des seuils de ressources.
- **Postmortem blameless** après chaque incident notable : chronologie, causes, actions avec responsable et date.
- **Réduire le toil** : chaque tâche manuelle répétée est candidate à l'automatisation.

## Comprendre SLI, SLO et SLA

- Le **SLI** (*indicator*) est une **mesure** de ce que vit l'utilisateur, exprimée en proportion de « bons » événements : requêtes réussies sur requêtes totales, requêtes de moins de 300 ms sur requêtes totales. On évite le CPU ou la mémoire : un utilisateur ne les ressent pas directement.
- Le **SLO** (*objective*) est l'**objectif** fixé pour ce SLI sur une période : « 99,9 % des requêtes réussies sur 30 jours glissants ». C'est un objectif interne, fixé par l'équipe et le produit.
- Le **SLA** (*agreement*) est un **engagement contractuel** envers les clients, avec des pénalités. Il est toujours **moins** strict que le SLO, pour garder une marge.

## Le budget d'erreur, avec des chiffres

Un SLO de 99,9 % autorise 0,1 % d'échecs. Avec 10 millions de requêtes par mois, c'est un **budget** de 10 000 requêtes en erreur. Tant qu'il en reste, l'équipe peut prendre des risques : livrer vite, expérimenter. S'il est épuisé, on donne la priorité à la fiabilité (correctifs, tests, automatisation) jusqu'à ce qu'il se reconstitue.

C'est ce qui rend le débat objectif : ni les développeurs (« on veut livrer ») ni les ops (« on veut de la stabilité ») n'ont raison par principe, c'est le budget qui tranche.

## Le burn rate, expliqué

Le **burn rate** est la vitesse à laquelle on consomme le budget. Un burn rate de 1 consomme exactement le budget sur les 30 jours. Un burn rate de 14 le consommerait en environ 2 jours.

On alerte sur le burn rate plutôt que sur un taux d'erreur brut parce que ça lie l'alerte à l'impact réel :

- burn rate **élevé sur une fenêtre courte** (14× sur 1 h) : une panne en cours, il faut réveiller quelqu'un ;
- burn rate **modéré sur une fenêtre longue** (1× ou 2× sur 3 jours) : une dégradation lente, un ticket suffit.

## Le postmortem sans reproche

*Blameless* ne veut pas dire sans responsabilité. L'idée est que si une personne a pu supprimer la base de prod avec une commande, le problème est le **système** qui l'a permis (pas de confirmation, droits trop larges, pas de sauvegarde testée), et c'est lui qu'on corrige. Chercher un coupable pousse les gens à cacher les erreurs, et on perd l'information qui permettrait d'éviter la suivante.

## Le toil

Le *toil* est le travail manuel, répétitif, sans valeur durable, qui grandit avec le service : relancer un job à la main, créer des comptes, nettoyer un disque. Le SRE vise à le maintenir sous environ 50 % du temps de l'équipe, le reste allant à l'ingénierie qui le réduit.

> **À retenir.** Le budget d'erreur transforme le débat « livrer ou stabiliser » en une décision chiffrée.
