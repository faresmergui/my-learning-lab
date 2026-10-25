---
title: Loki et LogQL
chapter: 8
order: 1
duration: 11
tags:
- Observabilité
- Loki
- LogQL
- Grafana
cards:
- q: Quelle est l'idée centrale de Loki ?
  a: '**N''indexer que les étiquettes**, pas le contenu des logs. Les lignes sont compressées en blocs (chunks) dans du stockage objet ; une requête choisit d''abord des flux par étiquettes, puis lit et filtre leur contenu. Résultat : un stockage bien moins cher qu''Elasticsearch, au prix de recherches plein texte plus lentes sur de gros volumes.'
- q: Qu'est-ce qu'un flux (stream) dans Loki ?
  a: 'L''ensemble des logs qui partagent **exactement les mêmes étiquettes** (`{namespace="api", app="commandes", env="prod"}`). Comme pour Prometheus, chaque combinaison d''étiquettes crée un flux : trop d''étiquettes ou des étiquettes à forte cardinalité (pod, user_id) dégradent Loki.'
- q: Quelle est la structure d'une requête LogQL ?
  a: 'Un **sélecteur de flux** entre accolades (`{app="commandes"}`), puis une **chaîne de filtres** : filtres de ligne (`|= "error"`, `!= "healthz"`, `|~ "regex"`), parseurs (`| json`, `| logfmt`, `| pattern`), filtres sur champs (`| status >= 500`) et mise en forme (`| line_format`).'
- q: Comment faire une métrique à partir de logs avec LogQL ?
  a: 'En entourant la requête d''une fonction sur intervalle : `sum by (app) (rate({env="prod"} |= "error" [5m]))` donne le nombre de lignes d''erreur par seconde et par application ; `quantile_over_time(0.99, {app="api"} | json | unwrap duration_ms [5m])` calcule un percentile depuis un champ.'
- q: Que sont les structured metadata de Loki ?
  a: 'Des paires clé-valeur attachées à chaque ligne **sans créer de flux** : on y met les champs à forte cardinalité utiles au filtrage (trace_id, pod, user_id), au lieu d''en faire des étiquettes.'
quiz:
- q: Ton Loki ralentit et refuse des écritures avec « maximum active stream limit exceeded ». Cause probable ?
  options:
  - Trop de lignes
  - Une étiquette à forte cardinalité (pod, request_id, user_id) qui crée un flux par valeur ; la transformer en structured metadata ou en champ du contenu
  - Le disque est plein
  - Grafana est trop vieux
  answer: 1
  explain: 'Peu d''étiquettes, à faible cardinalité : c''est la règle d''or de Loki.'
- q: Quelle requête trouve les requêtes de l'API commandes de plus de 2 secondes ?
  options:
  - '`{app="commandes"} > 2`'
  - '`{app="commandes"} | json | duration_ms > 2000`'
  - '`commandes AND slow`'
  - '`rate(commandes[2s])`'
  answer: 1
  explain: On sélectionne le flux, on parse le JSON, puis on filtre sur le champ extrait.
level: intermédiaire
---

**Loki** est le stockage de logs de Grafana Labs, pensé « comme Prometheus, mais pour les logs » : mêmes étiquettes, même découverte Kubernetes, même Grafana. Son choix fondateur est de **ne pas indexer le contenu** des logs, ce qui le rend beaucoup moins cher à faire tourner qu'Elasticsearch, à condition de bien choisir ses étiquettes.

> **Les outils cités dans cette fiche.**
> - **Loki** : le système de stockage de logs de Grafana Labs, indexé par étiquettes.
> - **LogQL** : le langage de requête de Loki, inspiré de PromQL.
> - **chunk** : un bloc compressé de lignes de logs d'un même flux.
> - **stockage objet** : S3, Swift, Ceph RGW, GCS, où Loki range ses chunks et son index.
> - **Promtail** : l'ancien agent de Loki, remplacé par **Grafana Alloy** ; Fluent Bit, Vector et l'OpenTelemetry Collector savent aussi envoyer à Loki.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **flux** (stream) | tous les logs qui ont exactement les mêmes étiquettes, par exemple ceux de l'application `commandes` en `prod` |
| **étiquette** (label) | une paire clé-valeur qui identifie un flux ; c'est la seule chose que Loki indexe |
| **chunk** | un paquet compressé de lignes d'un même flux, couvrant quelques minutes à quelques heures |
| **index** (dans Loki) | une petite table qui dit « pour telles étiquettes et telle période, les lignes sont dans tels chunks » |
| **filtre de ligne** | `\|= "error"` garde les lignes qui contiennent « error » ; `!=` les exclut ; `\|~` utilise une regex |
| **parseur** | `\| json` ou `\| logfmt` transforment la ligne en champs que l'on peut filtrer (`\| status >= 500`) |
| **structured metadata** | des informations attachées à chaque ligne sans créer de nouveau flux (bonne place pour un trace_id) |
| **ruler** | le composant de Loki qui évalue des règles d'alerte écrites en LogQL |
| **compactor** | le composant qui réorganise l'index et supprime les données plus vieilles que la rétention |

## Comment ça marche : écrire puis chercher

**À l'écriture**

1. L'agent envoie un lot de lignes avec leurs étiquettes, par exemple `{app="commandes", env="prod"}`.
2. Le **distributor** vérifie les limites et transmet chaque flux à des **ingesters** (en plusieurs copies).
3. L'ingester ajoute les lignes au chunk en cours de ce flux, en mémoire. Quand le chunk est plein ou assez vieux, il le **compresse** et l'écrit dans le stockage objet, et met à jour l'**index**.

**À la lecture**, pour `{app="commandes"} |= "timeout"` sur la dernière heure :

1. Loki consulte l'index : quels chunks correspondent à `app="commandes"` sur cette heure ? Cette étape est très rapide car l'index est petit.
2. Il télécharge ces chunks (et lit les lignes encore en mémoire dans les ingesters).
3. Il les décompresse et **parcourt chaque ligne** pour garder celles qui contiennent « timeout », en parallèle sur plusieurs queriers.

D'où la règle : plus le sélecteur d'étiquettes est précis, moins Loki a de chunks à lire, et plus la requête est rapide. Une recherche de texte sur tous les logs d'un mois oblige à tout relire.

## Comprendre : indexer peu, lire vite

<!-- schema:flux -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="Loki : indexer peu, lire vite" style="--minw:560px"><defs><marker id="g5-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g5-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g5-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g5-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="14" y="16" class="dg-zl" text-anchor="start">écriture</text><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="24" width="140" height="50" rx="9"/></g><text x="84.0" y="54.0" class="dg-t" text-anchor="middle" style="--d:0">logs entrants</text><g class="dg-box dg-pop" style="--d:1"><rect x="200" y="24" width="170" height="50" rx="9"/></g><text x="285.0" y="46.0" class="dg-t" text-anchor="middle" style="--d:1">distributor</text><text x="285.0" y="64.0" class="dg-s" text-anchor="middle" style="--d:1">vérifie, répartit</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="416" y="24" width="250" height="50" rx="9"/></g><text x="541.0" y="46.0" class="dg-t" text-anchor="middle" style="--d:2">ingesters</text><text x="541.0" y="64.0" class="dg-s" text-anchor="middle" style="--d:2">regroupent par flux, compressent</text><path d="M154 49 L198 49" class="dg-l c" marker-end="url(#g5-c)"/><path d="M370 49 L414 49" class="dg-l c" marker-end="url(#g5-c)"/><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="220" y="120" width="260" height="52" rx="9"/></g><text x="350.0" y="143.0" class="dg-t" text-anchor="middle" style="--d:3">stockage objet</text><text x="350.0" y="161.0" class="dg-s" text-anchor="middle" style="--d:3">chunks + petit index (étiquettes)</text><path d="M540 74 L540 98 L420 98 L420 118" class="dg-l c" marker-end="url(#g5-c)"/><text x="14" y="212" class="dg-zl" text-anchor="start">lecture</text><g class="dg-box dg-pop" style="--d:4"><rect x="14" y="222" width="120" height="50" rx="9"/></g><text x="74.0" y="244.0" class="dg-t" text-anchor="middle" style="--d:4">Grafana</text><text x="74.0" y="262.0" class="dg-s" text-anchor="middle" style="--d:4">LogQL</text><g class="dg-box dg-pop" style="--d:5"><rect x="170" y="222" width="170" height="50" rx="9"/></g><text x="255.0" y="244.0" class="dg-t" text-anchor="middle" style="--d:5">query-frontend</text><text x="255.0" y="262.0" class="dg-s" text-anchor="middle" style="--d:5">découpe la période</text><g class="dg-box dg-a dg-pop" style="--d:6"><rect x="386" y="206" width="280" height="82" rx="9"/></g><text x="526.0" y="230.0" class="dg-t" text-anchor="middle" style="--d:6">queriers</text><text x="526.0" y="248.0" class="dg-s" text-anchor="middle" style="--d:6"><tspan x="526.0" dy="0">1. choisir les flux par étiquettes</tspan><tspan x="526.0" dy="14">2. lire leurs chunks</tspan><tspan x="526.0" dy="14">3. filtrer le contenu en parallèle</tspan></text><path d="M134 247 L168 247" class="dg-l a" marker-end="url(#g5-a)"/><path d="M340 247 L384 247" class="dg-l a" marker-end="url(#g5-a)"/><path d="M450 206 L450 190 L300 190 L300 174" class="dg-l a" marker-end="url(#g5-a)"/></svg><figcaption>Seules les étiquettes sont indexées ; le contenu est filtré à la lecture, d&#x27;où l&#x27;importance de bien choisir les étiquettes.</figcaption></figure>
<!-- /schema:flux -->

| | Loki | Elasticsearch |
| --- | --- | --- |
| indexe | les étiquettes seulement | tous les champs (index inversé) |
| coût de stockage | faible (objet compressé) | élevé (index, répliques, disques rapides) |
| recherche plein texte sur des mois | lente | rapide |
| requête typique | « logs d'erreur de ce service, cette heure-ci » | « cette chaîne dans tous les logs de l'année » |
| exploitation | simple en mono-binaire, distribuée à grande échelle | cluster à dimensionner finement |

## Choisir les étiquettes

- **Oui** : `cluster`, `env`, `namespace`, `app`/`service`, `level` éventuellement : peu de valeurs, stables.
- **Non** : `pod`, `request_id`, `user_id`, `trace_id`, adresse IP : ils vont dans le **contenu** ou en **structured metadata**.
- Viser des flux qui reçoivent un volume raisonnable ; des milliers de petits flux sont moins efficaces que quelques gros.

## LogQL par l'exemple

```logql
# erreurs du service commandes, sans le bruit des sondes
{env="prod", app="commandes"} |= "error" != "healthz"

# parser le JSON et filtrer sur des champs
{app="commandes"} | json | level="error" and http_status >= 500

# mettre en forme pour la lecture
{app="commandes"} | json | line_format "{{.http_status}} {{.msg}} ({{.order_id}})"

# retrouver une trace
{app="commandes"} | trace_id="4bf92f3577b34da6a3ce929d0e0e4736"

# métrique : lignes d'erreur par seconde, par application
sum by (app) (rate({env="prod"} |= "error" [5m]))

# p99 de durée depuis un champ des logs
quantile_over_time(0.99, {app="commandes"} | json | unwrap duration_ms [5m]) by (app)
```

Les requêtes de métriques LogQL servent aussi de **règles d'alerte** dans le **ruler** de Loki (même format que Prometheus, envoyées à Alertmanager).

## Déployer et exploiter

| Mode | Pour qui |
| --- | --- |
| monolithique (un binaire) | petits volumes, test |
| simple scalable (lecture, écriture, backend) | la plupart des équipes |
| microservices | très grands volumes, plateforme multi-tenant |

- Stockage dans un bucket objet (S3, Swift ou Ceph RGW sur OpenStack), avec rétention par le **compactor** (globale ou par flux).
- **Limites** par tenant : débit d'ingestion, nombre de flux actifs, taille des requêtes.
- **Cache** des résultats et des chunks pour les tableaux de bord.
- Superviser Loki lui-même (il expose ses métriques Prometheus) : flux actifs, débit, erreurs d'ingestion, latence des requêtes.

> **À retenir.** Loki n'indexe que les étiquettes et range des chunks compressés dans du stockage objet : stockage bon marché, recherche plein texte plus lente sur de très gros volumes. Peu d'étiquettes à faible cardinalité ; les identifiants vont dans le contenu ou en structured metadata. LogQL : sélecteur de flux, filtres de ligne, parseurs (json, logfmt), filtres de champs, et fonctions de métriques (rate, quantile_over_time) utilisables en alertes. Déploiement monolithique, simple scalable ou microservices.
