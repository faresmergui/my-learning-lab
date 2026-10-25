---
title: PromQL, règles et Alertmanager
chapter: 4
order: 1
duration: 13
tags:
- Observabilité
- Prometheus
- PromQL
- Alerting
cards:
- q: Différence entre un vecteur instantané et un vecteur d'intervalle ?
  a: Un **vecteur instantané** (`http_requests_total`) donne la dernière valeur de chaque série. Un **vecteur d'intervalle** (`http_requests_total[5m]`) donne toutes les valeurs des 5 dernières minutes ; il sert d'entrée aux fonctions comme `rate()`, `increase()` ou `avg_over_time()`.
- q: Que calcule `rate(http_requests_total[5m])` ?
  a: Le **débit moyen par seconde** du compteur sur les 5 dernières minutes, pour chaque série, en compensant les remises à zéro. On choisit un intervalle d'au moins **4 fois** l'intervalle de scrape. `increase()` donne le nombre total sur la période.
- q: Comment calculer le p99 de latence par service ?
  a: '`histogram_quantile(0.99, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m])))` : on prend le débit de chaque bucket, on **additionne** par `le` (et par service) en gardant l''étiquette `le`, puis on calcule le quantile.'
- q: À quoi servent les recording rules ?
  a: À **pré-calculer** régulièrement une requête coûteuse et à l'enregistrer comme une nouvelle série (`job:http_requests:rate5m`). Les tableaux de bord et alertes deviennent rapides, et les SLO sur de longues périodes deviennent possibles.
- q: Que fait le champ `for` d'une règle d'alerte ?
  a: Il impose que la condition soit vraie **pendant toute la durée** indiquée avant de déclencher (l'alerte passe de `pending` à `firing`). Il évite d'alerter sur un pic passager ; trop long, il retarde la détection.
- q: Que font le groupement, l'inhibition et le silence dans Alertmanager ?
  a: Le **groupement** (`group_by`) fusionne les alertes liées en une notification (toutes les alertes d'un cluster). L'**inhibition** masque des alertes quand une autre plus grave est active (pas d'alerte « service lent » si « datacenter injoignable » est active). Le **silence** coupe temporairement des alertes (maintenance).
quiz:
- q: Quelle requête donne le taux d'erreurs 5xx en pourcentage par service ?
  options:
  - '`http_requests_total{code=~"5.."}`'
  - '`sum by (service) (rate(http_requests_total{code=~"5.."}[5m])) / sum by (service) (rate(http_requests_total[5m])) * 100`'
  - '`avg(http_requests_total)`'
  - '`count(http_requests_total)`'
  answer: 1
  explain: On compare des débits (rate) et on agrège par service des deux côtés pour que les étiquettes correspondent.
- q: Pendant une coupure réseau d'un datacenter, l'équipe reçoit 400 notifications. Quel réglage d'Alertmanager aurait le plus aidé ?
  options:
  - Augmenter le repeat_interval
  - Un group_by par datacenter et une règle d'inhibition qui masque les alertes des services quand l'alerte « datacenter injoignable » est active
  - Supprimer Alertmanager
  - Baisser le scrape_interval
  answer: 1
  explain: Groupement et inhibition transforment une avalanche en une ou deux notifications utiles.
level: intermédiaire
---

Collecter des métriques ne sert à rien si on ne sait pas les interroger. **PromQL** est le langage de requête de Prometheus, repris par Grafana, Mimir, Thanos et VictoriaMetrics, et compris aussi par d'autres outils. Il sert à la fois aux tableaux de bord, aux règles pré-calculées et aux alertes, que **Alertmanager** route ensuite vers les bonnes personnes.

> **Les outils cités dans cette fiche.**
> - **PromQL** : le langage de requête de Prometheus.
> - **recording rule** : une requête calculée régulièrement et enregistrée comme nouvelle série.
> - **alerting rule** : une requête dont le résultat déclenche une alerte.
> - **Alertmanager** : le composant qui regroupe, route, déduplique et envoie les alertes.
> - **PagerDuty** et **Opsgenie** : des services de gestion d'astreinte (appels, escalade).

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **vecteur** | en PromQL, un ensemble de séries : la requête `up` renvoie un vecteur avec une valeur par cible |
| **sélecteur** | la partie entre accolades qui choisit les séries : `{job="api", code="500"}` |
| **regex** (expression régulière) | un motif de texte : `code=~"5.."` veut dire « un code qui commence par 5 suivi de deux caractères » |
| **fonction** | un calcul appliqué aux séries : `rate`, `increase`, `avg_over_time`… |
| **agrégation** | regrouper plusieurs séries en une : `sum by (service)` additionne toutes les séries d'un même service |
| **règle** (rule) | une requête que Prometheus calcule lui-même à intervalle régulier, pour enregistrer un résultat ou déclencher une alerte |
| **sévérité** | le niveau de gravité d'une alerte (`page` pour réveiller quelqu'un, `warning` ou `ticket` pour plus tard) |
| **runbook** | la fiche de procédure qui explique quoi faire quand l'alerte sonne |
| **receiver** | dans Alertmanager, une destination de notification (un canal Slack, une adresse e-mail, un service d'astreinte) |
| **route** | la règle d'Alertmanager qui choisit le receiver selon les étiquettes de l'alerte |
| **matcher** | une condition sur une étiquette, comme `severity="page"` |
| **promtool** | l'outil en ligne de commande fourni avec Prometheus pour vérifier et tester les règles |

## Comment ça marche : la vie d'une alerte

1. **Évaluation** : toutes les 30 secondes, Prometheus calcule la requête de la règle (par exemple, le taux d'erreurs de chaque service).
2. **Condition vraie** : pour le service `commandes`, le résultat dépasse 5 %. L'alerte passe en état **pending** (en attente).
3. **Durée** : si la condition reste vraie pendant toute la durée `for` (10 minutes), l'alerte passe en **firing** (déclenchée). Si elle redevient fausse avant, elle retourne à **inactive** sans prévenir personne.
4. **Envoi** : Prometheus envoie l'alerte, avec ses étiquettes et annotations, à Alertmanager, et la renvoie régulièrement tant qu'elle est active.
5. **Regroupement** : Alertmanager attend `group_wait` (30 s) pour regrouper les alertes semblables arrivées en même temps, puis choisit la **route** selon les étiquettes.
6. **Notification** : le receiver envoie le message (Slack, PagerDuty…). Si l'alerte dure, un rappel part après `repeat_interval`.
7. **Résolution** : quand la condition redevient fausse, Prometheus cesse de l'envoyer ; Alertmanager envoie un message « résolu » si c'est configuré.

<!-- schema:vie -->
<figure class="diagram"><svg viewBox="0 0 680 210" role="img" aria-label="La vie d&#x27;une alerte" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="30" width="118" height="64" rx="9"/></g><text x="73.0" y="59.0" class="dg-t" text-anchor="middle" style="--d:0">inactive</text><text x="73.0" y="77.0" class="dg-s" text-anchor="middle" style="--d:0">condition fausse</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="148" y="30" width="118" height="64" rx="9"/></g><text x="207.0" y="52.0" class="dg-t" text-anchor="middle" style="--d:1">pending</text><text x="207.0" y="70.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="207.0" dy="0">vraie depuis</tspan><tspan x="207.0" dy="14">moins que for</tspan></text><path d="M132 62 L146 62" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="282" y="30" width="118" height="64" rx="9"/></g><text x="341.0" y="52.0" class="dg-t" text-anchor="middle" style="--d:2">firing</text><text x="341.0" y="70.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="341.0" dy="0">vraie pendant</tspan><tspan x="341.0" dy="14">for (10 min)</tspan></text><path d="M266 62 L280 62" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="416" y="30" width="118" height="64" rx="9"/></g><text x="475.0" y="52.0" class="dg-t" text-anchor="middle" style="--d:3">Alertmanager</text><text x="475.0" y="70.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="475.0" dy="0">regroupe (30 s),</tspan><tspan x="475.0" dy="14">choisit la route</tspan></text><path d="M400 62 L414 62" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-ok dg-pop" style="--d:4"><rect x="550" y="30" width="118" height="64" rx="9"/></g><text x="609.0" y="59.0" class="dg-t" text-anchor="middle" style="--d:4">receiver</text><text x="609.0" y="77.0" class="dg-s" text-anchor="middle" style="--d:4">Slack, PagerDuty…</text><path d="M534 62 L548 62" class="dg-l c" marker-end="url(#g2-c)"/><path d="M207 94 C 207 150, 73 150, 73 96" class="dg-l dash" marker-end="url(#g2-n)"/><text x="140" y="162" class="dg-s" text-anchor="middle">redevient fausse avant 10 min :</text><text x="140" y="176" class="dg-s" text-anchor="middle">personne n&#x27;est prévenu</text><text x="475" y="126" class="dg-s" text-anchor="middle">silences et inhibitions</text><text x="475" y="140" class="dg-s" text-anchor="middle">agissent ici</text><path d="M475 112 L475 96" class="dg-l" marker-end="url(#g2-n)"/></svg><figcaption>La durée for évite de réveiller quelqu&#x27;un pour un pic de quelques secondes.</figcaption></figure>
<!-- /schema:vie -->

Les **silences** et **inhibitions** s'appliquent à l'étape 5 : l'alerte existe toujours dans Prometheus, mais Alertmanager ne la notifie pas.

## Comprendre : sélectionner, calculer, agréger

```
http_requests_total{service="api", code=~"5.."}          sélection (étiquettes, regex)
rate(  …  [5m])                                           calcul sur un intervalle
sum by (service) (  …  )                                  agrégation en gardant service
… / … * 100                                               opération entre vecteurs
```

| Élément | Exemples |
| --- | --- |
| sélecteurs | `{job="node"}`, `{code!="200"}`, `{path=~"/api/.*"}` |
| intervalles | `[5m]`, `[1h]`, avec `offset 1d` pour comparer à la veille |
| fonctions sur counters | `rate`, `irate` (très réactif), `increase` |
| fonctions sur gauges | `avg_over_time`, `max_over_time`, `deriv`, `predict_linear` |
| agrégations | `sum`, `avg`, `max`, `min`, `count`, `topk`, `quantile`, avec `by (…)` ou `without (…)` |
| histogrammes | `histogram_quantile(0.99, sum by (le) (rate(…_bucket[5m])))` |
| absence | `absent(up{job="api"})` : alerte si plus aucune donnée |

## Les requêtes utiles au quotidien

```promql
# débit de requêtes par service
sum by (service) (rate(http_requests_total[5m]))

# taux d'erreurs en %
sum by (service) (rate(http_requests_total{code=~"5.."}[5m]))
  / sum by (service) (rate(http_requests_total[5m])) * 100

# p99 de latence
histogram_quantile(0.99, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m])))

# CPU utilisé par hôte, en %
100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100

# disque plein dans moins de 4 heures (au rythme actuel)
predict_linear(node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}[6h], 4*3600) < 0

# les 5 pods qui consomment le plus de mémoire
topk(5, sum by (pod) (container_memory_working_set_bytes{container!=""}))
```

## Règles d'enregistrement et d'alerte

```yaml
groups:
  - name: api
    rules:
      - record: service:http_requests:rate5m
        expr: sum by (service) (rate(http_requests_total[5m]))
      - alert: TauxErreursEleve
        expr: |
          sum by (service) (rate(http_requests_total{code=~"5.."}[5m]))
            / sum by (service) (rate(http_requests_total[5m])) > 0.05
        for: 10m
        labels: { severity: page }
        annotations:
          summary: "{{ $labels.service }} : plus de 5 % d'erreurs"
          runbook_url: https://wiki.example.com/runbooks/taux-erreurs
```

```bash
promtool check rules rules/api.yml        # valider en CI
promtool test rules tests/api_test.yml    # tester les alertes avec des séries simulées
```

Une alerte passe par trois états : `inactive`, `pending` (condition vraie depuis moins que `for`) et `firing`.

## Alertmanager : du signal à la bonne personne

```yaml
route:
  receiver: equipe-plateforme
  group_by: [alertname, cluster]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - matchers: [ severity="page" ]
      receiver: astreinte-pagerduty
    - matchers: [ team="data" ]
      receiver: equipe-data
inhibit_rules:
  - source_matchers: [ alertname="ClusterInjoignable" ]
    target_matchers: [ severity=~"warning|page" ]
    equal: [ cluster ]
receivers:
  - name: astreinte-pagerduty
    pagerduty_configs: [ { routing_key: <secret> } ]
  - name: equipe-plateforme
    slack_configs: [ { channel: "#alertes-plateforme" } ]
```

| Mécanisme | Effet |
| --- | --- |
| `group_by` et `group_wait` | une notification pour un groupe d'alertes liées |
| routes | qui reçoit quoi selon les étiquettes (sévérité, équipe) |
| `repeat_interval` | rappel si l'alerte dure |
| inhibition | masquer les conséquences quand la cause est connue |
| silence | couper pendant une maintenance (`amtool silence add`) |

> **À retenir.** PromQL sélectionne des séries par étiquettes, calcule sur des intervalles (`rate` et `increase` pour les counters), agrège avec `sum by` et compare des vecteurs. Percentiles avec `histogram_quantile` sur des buckets additionnés. Recording rules pour pré-calculer, alerting rules avec `for`, une sévérité et un lien de runbook, testées avec promtool. Alertmanager groupe, route selon les étiquettes, inhibe les conséquences et gère les silences.
