---
title: Synthèse Observabilité
description: "Signaux, métriques, Prometheus et PromQL, stockage long terme, Grafana, logs, Loki, Elastic et Kibana, traces et OpenTelemetry, Centreon, Datadog, alerting."
---

## Les fondamentaux

- **Monitoring** : surveiller des seuils connus. **Observabilité** : comprendre l'imprévu à partir de données riches.
- Signaux : **métriques**, **logs**, **traces**, profils, événements (déploiements).
- **Signaux dorés** : latence, trafic, erreurs, saturation. **RED** pour les services, **USE** pour les ressources.
- Boîte noire (sondes) + boîte blanche (ce que le système expose).
- **Cardinalité** : pas d'identifiants uniques en étiquette, nulle part.

## Métriques

| Type | Usage |
| --- | --- |
| counter | `rate()`, `increase()` |
| gauge | valeur, `avg`, `max` |
| histogram | `histogram_quantile()` sur des buckets additionnés |
| summary | percentiles non agrégeables |

- Percentiles plutôt que moyennes. Pull (Prometheus) et push (Datadog, OTLP).

## Prometheus et PromQL

```promql
sum by (service) (rate(http_requests_total{code=~"5.."}[5m])) / sum by (service) (rate(http_requests_total[5m]))
histogram_quantile(0.99, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m])))
predict_linear(node_filesystem_avail_bytes[6h], 4*3600) < 0
up == 0
```

- Scrape de `/metrics`, découverte de services, relabeling ; exporters (node, blackbox, snmp, kube-state-metrics).
- Recording rules, alerting rules (`for`, sévérité, runbook), `promtool test rules`.
- Alertmanager : `group_by`, routes, inhibition, silences.
- Long terme et vue globale : **Thanos** (sidecar + objet), **Mimir** (remote_write, multi-tenant), **VictoriaMetrics** (sobre).

## Grafana

- Visualise sans stocker ; Explore ; liens métriques → logs → traces.
- Tableau de bord : état utilisateur en haut, détail, ressources ; variables, unités, annotations, liens.
- En code : JSON dans Git, provisioning, Terraform, ConfigMaps.

## Logs

- JSON, un événement par ligne, `level`, `service`, `trace_id`, aucun secret.
- Agents : Fluent Bit, Vector, Alloy, Filebeat/Elastic Agent, OTel Collector.
- Coût : filtrer à la source, échantillonner, rétention par classe, compter avec des métriques.

| | Loki | Elasticsearch |
| --- | --- | --- |
| indexe | étiquettes | tous les champs |
| coût | faible | élevé |
| plein texte longue période | lent | rapide |
| requêtes | LogQL | KQL, Lucene, ES\|QL |

- **LogQL** : `{app="x"} |= "error" | json | status >= 500` ; `sum by (app) (rate({…} |= "error" [5m]))`.
- **Elasticsearch** : index, shards, replicas ; data streams et ILM (hot → warm → cold → delete) ; vert / jaune / rouge.
- **Kibana** : Discover, KQL, Lens, dashboards, règles, Fleet, spaces.

## Traces et OpenTelemetry

- Trace = arbre de **spans** ; propagation par `traceparent` à chaque saut.
- OpenTelemetry : SDK, auto-instrumentation, **OTLP**, **Collector** (receivers → processors → exporters).
- **Tail sampling** pour garder erreurs et lenteurs ; Tempo ou Jaeger pour stocker.

## Centreon et Datadog

- **Centreon** : hôtes et services, plugins (0 OK, 1 WARNING, 2 CRITICAL, 3 UNKNOWN), pollers, SOFT puis HARD, dépendances parent/enfant, downtimes, acquittements, SNMPv3.
- **Datadog** : agent + intégrations, tags `env`/`service`/`version`, monitors en Terraform ; coût lié aux hôtes, à la cardinalité et aux volumes.

## Bien alerter

- Page = urgente, réelle, actionnable ; le reste en ticket ou tableau de bord.
- Symptômes plutôt que causes ; **SLO** et **burn rate** (14,4 sur 1 h et 5 min → page).
- Message clair + runbook ; planning, escalade, revue des alertes, postmortems.

## Kubernetes et OpenStack

- Kubernetes : kube-prometheus-stack (node_exporter, kube-state-metrics, cAdvisor, mixins), ingress, événements.
- OpenStack : hôtes, services et agents, Galera, RabbitMQ, OVN, libvirt, Ceph, capacité, test de fumée, logs par request-id.
- Dead man's switch pour surveiller la supervision.

## Choisir sa stack

- Par couche, avec une instrumentation neutre (OpenTelemetry).
- LGTM auto-hébergé · parc mixte (Centreon + Prometheus/Grafana + Elastic) · SaaS pour petite équipe.
- Tout en code, conventions communes, cardinalité et coûts suivis, revue régulière.
