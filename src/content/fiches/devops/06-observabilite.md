---
title: 'Observabilité : métriques, logs, traces'
chapter: 6
order: 1
duration: 9
level: intermédiaire
tags:
- prometheus
- observabilité
cards:
- q: Quels sont les trois piliers de l'observabilité ?
  a: Les **métriques** (chiffres agrégés dans le temps), les **logs** (événements détaillés) et les **traces** (le parcours d'une requête entre services).
- q: Prometheus fonctionne-t-il en push ou en pull ?
  a: 'En **pull** : il vient **scraper** l''endpoint `/metrics` des cibles à intervalle régulier. Le Pushgateway existe pour les jobs courts, en exception.'
- q: Différence entre counter, gauge et histogram ?
  a: '**Counter** : ne fait que monter (requêtes totales). **Gauge** : monte et descend (mémoire utilisée). **Histogram** : répartit des valeurs dans des buckets (latences).'
- q: Pourquoi ne jamais afficher un counter brut ?
  a: 'Sa valeur ne fait qu''augmenter et repart à zéro au redémarrage. On regarde son **taux** : `rate(http_requests_total[5m])`.'
- q: Que mesure la méthode RED ?
  a: 'Pour un service : **Rate** (requêtes par seconde), **Errors** (taux d''erreur), **Duration** (latence). La méthode **USE** (Utilisation, Saturation, Erreurs) sert pour les ressources.'
- q: Qu'est-ce que la cardinalité et pourquoi elle pose problème ?
  a: Le nombre de séries distinctes, une par combinaison de labels. Un label comme `user_id` ou `request_id` crée des millions de séries et fait exploser Prometheus.
- q: Quel est le rôle d'OpenTelemetry ?
  a: Un **standard ouvert** et un ensemble de SDK et de collecteurs pour produire métriques, logs et traces, indépendamment de l'outil de stockage.
quiz:
- q: Quelle requête donne la latence p95 d'un service ?
  options:
  - '`avg(http_request_duration_seconds)`'
  - '`histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))`'
  - '`max(http_request_duration_seconds_count)`'
  - '`rate(http_request_duration_seconds_sum[5m])`'
  answer: 1
  explain: On calcule le taux par bucket, on agrège en gardant le label `le`, puis `histogram_quantile` estime le 95e percentile.
- q: Ta mémoire Prometheus explose après l'ajout d'une métrique. Cause la plus probable ?
  options:
  - Intervalle de scrape trop long
  - Un label à forte cardinalité (ID utilisateur, URL complète)
  - Trop d'alertes
  - Grafana mal configuré
  answer: 1
  explain: Chaque valeur de label crée une nouvelle série. Les ID et les URL non normalisées sont les coupables habituels.
---

La supervision répond à « est-ce que ça marche ? ». L'observabilité répond à « **pourquoi** ça ne marche pas ? ».

> **Les outils cités dans cette fiche.**
> - **Prometheus** : base de données de métriques (des nombres mesurés dans le temps) ; **Grafana** : tableaux de bord qui les affichent.
> - **Loki** et **Elasticsearch** : stockent les logs et permettent d'y chercher. Loki est plus léger, Elasticsearch plus puissant pour la recherche plein texte.
> - **Tempo** et **Jaeger** : stockent les **traces**, c'est-à-dire le trajet d'une requête à travers plusieurs services, avec le temps passé dans chacun.
> - **Alertmanager** : envoie les alertes de Prometheus aux bonnes personnes ; **PagerDuty** : service d'astreinte qui appelle la personne de garde.
> - **OpenTelemetry** : un standard et des bibliothèques pour produire métriques, logs et traces depuis le code, quel que soit l'outil qui les stocke ensuite.
> - **latence** : le délai entre une demande et sa réponse.
> - **SQL** : le langage de requête des bases de données relationnelles (PostgreSQL, MySQL).

## Les trois piliers

| Pilier | Question | Outils courants |
| --- | --- | --- |
| Métriques | combien, à quelle vitesse ? | Prometheus, Grafana |
| Logs | que s'est-il passé exactement ? | Loki, Elasticsearch |
| Traces | où la requête a-t-elle perdu du temps ? | Tempo, Jaeger |

<!-- schema:prometheus -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="L&#x27;architecture Prometheus" style="--minw:560px"><defs><marker id="g22-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g22-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g22-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g22-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="20" width="140" height="50" rx="9"/></g><text x="84.0" y="42.0" class="dg-t" text-anchor="middle" style="--d:0">api</text><text x="84.0" y="60.0" class="dg-s" text-anchor="middle" style="--d:0">/metrics</text><path d="M256 120 L210 120 L210 45 L156 45" class="dg-l c" marker-end="url(#g22-c)"/><g class="dg-box dg-pop" style="--d:1"><rect x="14" y="90" width="140" height="50" rx="9"/></g><text x="84.0" y="112.0" class="dg-t" text-anchor="middle" style="--d:1">worker</text><text x="84.0" y="130.0" class="dg-s" text-anchor="middle" style="--d:1">/metrics</text><path d="M256 120 L210 120 L210 115 L156 115" class="dg-l c" marker-end="url(#g22-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="14" y="160" width="140" height="50" rx="9"/></g><text x="84.0" y="182.0" class="dg-t" text-anchor="middle" style="--d:2">node-exporter</text><text x="84.0" y="200.0" class="dg-s" text-anchor="middle" style="--d:2">/metrics</text><path d="M256 120 L210 120 L210 185 L156 185" class="dg-l c" marker-end="url(#g22-c)"/><text x="212" y="236" class="dg-s" text-anchor="middle">scrape (pull)</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="258" y="88" width="150" height="64" rx="9"/></g><text x="333.0" y="110.0" class="dg-t" text-anchor="middle" style="--d:3">Prometheus</text><text x="333.0" y="128.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="333.0" dy="0">stocke, évalue</tspan><tspan x="333.0" dy="14">les règles</tspan></text><g class="dg-box dg-pop" style="--d:4"><rect x="470" y="20" width="196" height="52" rx="9"/></g><text x="568.0" y="43.0" class="dg-t" text-anchor="middle" style="--d:4">Grafana</text><text x="568.0" y="61.0" class="dg-s" text-anchor="middle" style="--d:4">tableaux de bord</text><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="470" y="100" width="196" height="52" rx="9"/></g><text x="568.0" y="123.0" class="dg-t" text-anchor="middle" style="--d:4">Alertmanager</text><text x="568.0" y="141.0" class="dg-s" text-anchor="middle" style="--d:4">regroupe, route</text><g class="dg-box dg-pop" style="--d:5"><rect x="470" y="180" width="196" height="52" rx="9"/></g><text x="568.0" y="211.0" class="dg-t" text-anchor="middle" style="--d:5">Slack, PagerDuty</text><path d="M408 110 L440 110 L440 46 L468 46" class="dg-l" marker-end="url(#g22-n)"/><text x="440.0" y="78.4" class="dg-s" text-anchor="middle">PromQL</text><path d="M408 126 L468 126" class="dg-l a" marker-end="url(#g22-a)"/><path d="M568 152 L568 178" class="dg-l a" marker-end="url(#g22-a)"/></svg><figcaption>Prometheus vient chercher les métriques. Grafana les affiche, Alertmanager prévient.</figcaption></figure>
<!-- /schema:prometheus -->

## PromQL, l'essentiel

```promql
# Requêtes par seconde, par service
sum by (service) (rate(http_requests_total[5m]))

# Taux d'erreur en %
100 * sum(rate(http_requests_total{code=~"5.."}[5m]))
    / sum(rate(http_requests_total[5m]))

# Latence p95
histogram_quantile(0.95,
  sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

## Alerter sur les symptômes

- Alerte sur ce que **l'utilisateur ressent** (erreurs, latence), pas sur le CPU à 80 %.
- Chaque alerte doit être **actionnable**, avec un lien vers un runbook.
- Alertmanager regroupe, déduplique et route les alertes (Slack, PagerDuty).

## Comprendre les trois piliers avec un exemple

Le site est lent depuis 14 h.

- Les **métriques** le montrent : la latence p95 est passée de 200 ms à 2 s, seulement sur `/checkout`. Les métriques sont des **nombres** mesurés à intervalles réguliers. Elles sont peu coûteuses, faciles à agréger et à alerter, mais elles ne disent pas **pourquoi**.
- Les **traces** suivent une requête à travers tous les services qu'elle traverse. Celle de `/checkout` montre que 1,8 s sont passées dans l'appel au service `payment`, et dans celui-ci dans une requête SQL.
- Les **logs** de `payment` à cette heure-là donnent le détail : « lock wait timeout » sur une table.

Chaque pilier répond à une question différente, et on passe de l'un à l'autre. C'est pourquoi on relie les trois par un identifiant commun (le *trace ID* écrit dans les logs) et par des labels communs (le nom du service). **OpenTelemetry** est le standard qui permet d'instrumenter une appli une fois pour produire les trois.

## Comment fonctionne Prometheus

Prometheus vient **chercher** les métriques (*pull*) : chaque appli expose une page `/metrics` en texte, et Prometheus la lit toutes les 15 ou 30 secondes. Chaque ligne est une **série** : un nom, des labels, une valeur.

```
http_requests_total{service="api", code="200"} 10432
http_requests_total{service="api", code="500"} 17
```

Les types à connaître :

| Type | Ce que c'est | Comment le lire |
| --- | --- | --- |
| **counter** | un compteur qui ne fait que monter (requêtes, erreurs) | jamais tel quel : `rate()` donne le **débit par seconde** |
| **gauge** | une valeur qui monte et descend (mémoire, file d'attente) | directement |
| **histogram** | une répartition en tranches (`le` = « inférieur ou égal ») | `histogram_quantile()` pour un percentile |

Un counter brut ne dit rien (« 10 432 depuis le démarrage »), et il repart à zéro quand l'appli redémarre : `rate()` gère ces remises à zéro.

## Les percentiles plutôt que la moyenne

La **p95** est la latence sous laquelle se trouvent 95 % des requêtes. Une moyenne de 150 ms peut cacher 5 % d'utilisateurs qui attendent 3 s. Ce sont souvent les plus gros clients (paniers plus lourds) : on suit donc p50, p95 et p99.

## Pourquoi pas d'identifiant unique dans un label

Chaque combinaison de labels crée une **série** distincte que Prometheus doit stocker. Un label `user_id` ou `request_id` crée des millions de séries (la *cardinalité* explose) et fait tomber Prometheus. Les identifiants vont dans les **logs** et les **traces**, pas dans les métriques.

> **À retenir.** Un counter se lit avec `rate()`. Et un label ne doit jamais contenir un identifiant unique.
