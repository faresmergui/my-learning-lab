---
title: 'Bases de données : RDS, Aurora, DynamoDB, ElastiCache'
chapter: 8
order: 1
duration: 14
tags:
- AWS SAA
- RDS
- DynamoDB
cards:
- q: Différence entre Multi-AZ et read replica sur RDS ?
  a: '**Multi-AZ** : une copie **synchrone** en attente dans une autre AZ, pour la **disponibilité** (bascule automatique en une à deux minutes, même nom DNS) ; elle ne sert pas les lectures (sauf cluster Multi-AZ à deux lecteurs). **Read replica** : copie **asynchrone** lisible, pour la **performance** en lecture, éventuellement dans une autre région, promouvable en base principale.'
- q: Qu'apporte Aurora par rapport à RDS classique ?
  a: Un stockage distribué sur 3 AZ (6 copies), qui grandit seul jusqu'à 128 To ; jusqu'à 15 réplicas avec un retard de quelques millisecondes ; bascule en moins de 30 s ; **Global Database** (réplication mondiale en moins d'une seconde) et **Serverless v2** (capacité ajustée à la seconde). Compatible MySQL et PostgreSQL.
- q: Comment choisir la clé de partition d'une table DynamoDB ?
  a: Une clé avec **beaucoup de valeurs différentes**, réparties uniformément (identifiant d'utilisateur, de commande). Une clé à peu de valeurs (statut, date du jour) concentre le trafic sur une partition « chaude » et provoque du throttling.
- q: Différence entre les modes de capacité DynamoDB ?
  a: '**On-demand** : on paie par requête, aucun réglage, idéal pour un trafic imprévisible. **Provisioned** : on fixe des unités de lecture et d''écriture (avec auto scaling), moins cher pour un trafic stable.'
- q: À quoi sert DAX ?
  a: '**DynamoDB Accelerator** : un cache en mémoire devant DynamoDB, compatible avec l''API, qui ramène les lectures à quelques **microsecondes**. Inutile pour les écritures.'
- q: Redis/Valkey ou Memcached dans ElastiCache ?
  a: '**Redis/Valkey** : structures de données riches, persistance, réplication, Multi-AZ avec bascule, pub/sub, sessions et classements. **Memcached** : cache simple multithread, sans persistance ni réplication.'
- q: À quoi sert RDS Proxy ?
  a: À **mutualiser les connexions** à une base RDS ou Aurora. Très utile avec Lambda, qui ouvrirait sinon des milliers de connexions ; il réduit aussi le temps de bascule et peut imposer l'authentification IAM.
quiz:
- q: Une base PostgreSQL doit survivre à la panne d'une AZ sans intervention. Que fais-tu ?
  options:
  - Une read replica
  - Activer Multi-AZ
  - Des snapshots quotidiens
  - Un cache ElastiCache
  answer: 1
  explain: Multi-AZ bascule automatiquement. Une read replica demanderait une promotion, et serait en retard (asynchrone).
- q: Un site de vente a des millions de paniers à lire et écrire en quelques millisecondes, avec des pics énormes et imprévisibles. Quelle base ?
  options:
  - RDS MySQL
  - DynamoDB en mode on-demand
  - Redshift
  - Neptune
  answer: 1
  explain: Accès par clé, échelle quasi illimitée, aucun serveur à dimensionner.
- q: Les rapports d'analyse ralentissent la base de production RDS. Solution la plus simple ?
  options:
  - Multi-AZ
  - Une read replica pour les rapports
  - Augmenter le stockage
  - DAX
  answer: 1
  explain: Les lectures lourdes vont sur la réplique ; l'instance Multi-AZ en attente n'est pas lisible.
- q: Il faut une reprise dans une autre région avec un RPO d'une seconde et un RTO d'une minute pour une base MySQL. Quel choix ?
  options:
  - Snapshots copiés chaque nuit
  - Aurora Global Database
  - Multi-AZ
  - Une read replica dans la même région
  answer: 1
  explain: Aurora Global Database réplique en général en moins d'une seconde et promeut la région secondaire en environ une minute.
level: intermédiaire
---

AWS propose une quinzaine de bases de données managées. L'examen demande surtout de **choisir la bonne** selon le besoin et de la rendre résiliente. Avant de comparer, une distinction : une base **relationnelle** range les données en tables liées avec SQL ; une base **NoSQL** est optimisée pour un type d'accès précis (par clé, en document, en graphe) et pour grandir sans limite.

> **Les outils cités dans cette fiche.**
> - **RDS** (Relational Database Service) : des bases relationnelles managées (PostgreSQL, MySQL, MariaDB, Oracle, SQL Server) ; AWS gère le système, les correctifs, les sauvegardes.
> - **Aurora** : la base relationnelle d'AWS, compatible MySQL et PostgreSQL, avec un stockage distribué maison.
> - **DynamoDB** : une base NoSQL clé-valeur et document, serverless, à latence de quelques millisecondes à n'importe quelle échelle.
> - **ElastiCache** : des caches en mémoire managés (**Redis**, **Valkey**, **Memcached**).
> - **RPO** (Recovery Point Objective) : combien de données on accepte de perdre. **RTO** (Recovery Time Objective) : combien de temps on accepte d'être arrêté.
> - **cluster** : un groupe de machines qui travaillent ensemble comme un seul système.
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **KMS** : le service de gestion des clés de chiffrement.
> - **jeton** : une chaîne secrète qui prouve qu'on est authentifié, à durée limitée.

## Comprendre : quelle base pour quel besoin

| Besoin | Service |
| --- | --- |
| relationnel classique, SQL, transactions | **RDS** ou **Aurora** |
| accès par clé, échelle énorme, serverless | **DynamoDB** |
| cache, sessions, classements | **ElastiCache** (Redis, Valkey), DAX devant DynamoDB |
| entrepôt de données, analyse SQL sur des To | **Redshift** |
| documents compatibles MongoDB | **DocumentDB** |
| graphe (réseau social, fraude) | **Neptune** |
| séries temporelles | **Timestream** |
| clé-valeur compatible Cassandra | **Keyspaces** |
| registre immuable et vérifiable | **QLDB** (en fin de vie) ou une table avec historique |

## RDS : la haute disponibilité et la lecture

<!-- schema:rds -->
<figure class="diagram"><svg viewBox="0 0 680 270" role="img" aria-label="RDS : Multi-AZ et réplicas de lecture" style="--minw:560px"><defs><marker id="g4-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g4-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g4-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g4-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="30" y="104" width="190" height="60" rx="9"/></g><text x="125.0" y="131.0" class="dg-t" text-anchor="middle" style="--d:0">principale</text><text x="125.0" y="149.0" class="dg-s" text-anchor="middle" style="--d:0">AZ a · lecture et écriture</text><g class="dg-box dg-ok dg-pop" style="--d:1"><rect x="470" y="20" width="196" height="56" rx="9"/></g><text x="568.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:1">secours Multi-AZ</text><text x="568.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:1">AZ b · non lisible</text><g class="dg-box dg-pop" style="--d:2"><rect x="470" y="106" width="196" height="56" rx="9"/></g><text x="568.0" y="131.0" class="dg-t" text-anchor="middle" style="--d:2">read replica</text><text x="568.0" y="149.0" class="dg-s" text-anchor="middle" style="--d:2">AZ c · lisible</text><g class="dg-box dg-pop" style="--d:3"><rect x="470" y="192" width="196" height="56" rx="9"/></g><text x="568.0" y="217.0" class="dg-t" text-anchor="middle" style="--d:3">read replica</text><text x="568.0" y="235.0" class="dg-s" text-anchor="middle" style="--d:3">eu-west-1 · promouvable</text><path d="M220 124 L330 124 L330 48 L468 48" class="dg-l ok thick" marker-end="url(#g4-ok)"/><path d="M220 134 L468 134" class="dg-l dash" marker-end="url(#g4-n)"/><path d="M220 144 L330 144 L330 220 L468 220" class="dg-l dash" marker-end="url(#g4-n)"/><text x="400" y="40" class="dg-okt" text-anchor="middle">synchrone</text><text x="400" y="68" class="dg-s" text-anchor="middle">bascule auto</text><text x="400" y="126" class="dg-s" text-anchor="middle">asynchrone</text><text x="400" y="212" class="dg-s" text-anchor="middle">asynchrone</text></svg><figcaption>Le Multi-AZ sert à la disponibilité, les réplicas à la lecture et à la reprise dans une autre région.</figcaption></figure>
<!-- /schema:rds -->

| | Multi-AZ | Read replica |
| --- | --- | --- |
| objectif | disponibilité | performance en lecture, reprise régionale |
| réplication | synchrone | asynchrone (retard possible) |
| lisible | non (sauf « Multi-AZ DB cluster » à deux lecteurs) | oui |
| bascule | automatique, même nom DNS | manuelle (promotion), nouveau nom |

Autres points RDS :

- **sauvegardes automatiques** : jusqu'à 35 jours, restauration **à la seconde près** (point-in-time) dans une **nouvelle** instance ; **snapshots manuels** gardés jusqu'à suppression ;
- **chiffrement** au repos avec KMS, à décider à la création (sinon : snapshot, copie chiffrée, restauration) ;
- **authentification IAM** pour MySQL et PostgreSQL, et mots de passe gérés dans Secrets Manager avec rotation ;
- **RDS Proxy** pour mutualiser les connexions (Lambda) et accélérer les bascules ;
- **autoscaling du stockage** pour éviter le disque plein.

## Aurora : RDS en mieux, à un prix plus élevé

- stockage partagé sur **3 AZ, 6 copies**, qui se répare seul et grandit jusqu'à 128 To ;
- jusqu'à **15 réplicas** de lecture derrière un **reader endpoint** ; bascule en moins de 30 s ;
- **Aurora Serverless v2** : capacité ajustée finement à la charge, pour un trafic irrégulier ;
- **Global Database** : une région principale, jusqu'à 10 secondaires en lecture, réplication typiquement sous la seconde, promotion en environ une minute ;
- **Backtrack** (MySQL) : revenir en arrière dans le temps sans restauration ; **clones** rapides pour les tests.

## DynamoDB : la base sans serveur

Une table a une **clé de partition** (et éventuellement une **clé de tri**). On lit par clé, ou par plage sur la clé de tri.

| Notion | À retenir |
| --- | --- |
| clé de partition | forte variété de valeurs pour éviter les partitions chaudes |
| index secondaires | **GSI** (autre clé, à tout moment) ; **LSI** (même partition, autre tri, à la création) |
| capacité | **on-demand** (imprévisible) ou **provisioned** + auto scaling (stable, moins cher) |
| cohérence | lectures « eventually consistent » par défaut, « strongly consistent » en option |
| **TTL** | suppression automatique des éléments expirés (sessions, jetons) |
| **Streams** | flux des modifications, pour déclencher une Lambda |
| **Global Tables** | réplication multi-région active-active |
| sauvegarde | **PITR** (35 jours, à la seconde) et sauvegardes à la demande |
| **DAX** | cache en microsecondes pour les lectures |

DynamoDB ne fait pas de jointures ni de requêtes SQL arbitraires : on conçoit la table **à partir des questions** que l'application posera.

## ElastiCache : soulager la base

Deux usages typiques :

- **cache-aside** : l'application cherche d'abord dans le cache, sinon lit la base et remplit le cache (avec une durée de vie) ;
- **sessions** et données partagées entre instances sans état.

Redis et Valkey offrent réplication, Multi-AZ avec bascule, persistance et structures riches (listes, ensembles triés pour des classements). Memcached reste un cache simple, multithread, sans réplication. Il existe aussi une version **serverless**.

> **À retenir.** Multi-AZ pour la disponibilité (synchrone, bascule auto), read replicas pour la lecture et la reprise régionale (asynchrone). Aurora ajoute un stockage sur 3 AZ, 15 réplicas, Serverless v2 et Global Database. DynamoDB pour l'accès par clé à grande échelle, avec une bonne clé de partition, on-demand si le trafic est imprévisible. ElastiCache ou DAX pour soulager les lectures.
