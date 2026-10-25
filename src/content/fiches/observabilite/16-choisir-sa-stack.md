---
title: Construire sa stack d'observabilité
chapter: 16
order: 1
duration: 11
tags:
- Observabilité
- Architecture
cards:
- q: Qu'est-ce que la stack LGTM ?
  a: 'La stack open source de Grafana Labs : **Loki** (logs), **Grafana** (visualisation), **Tempo** (traces) et **Mimir** (métriques), souvent avec **Alloy** comme agent et **Pyroscope** pour les profils. Tous utilisent du stockage objet et se relient dans Grafana.'
- q: Quels critères pour choisir une stack d'observabilité ?
  a: Les **besoins** (cloud native ou parc classique, logs plein texte ou par service), les **volumes** (séries, Go de logs par jour, traces), le **coût total** (licence ou SaaS, infrastructure, temps humain), les **compétences** de l'équipe, la **conformité** (où vont les données), et l'**existant** (Centreon déjà en place, Elastic pour la sécurité).
- q: Pourquoi instrumenter avec OpenTelemetry même si l'on choisit un fournisseur ?
  a: Parce que l'instrumentation (dans le code et les agents) est le plus long à changer. Avec OpenTelemetry et le Collector, l'application produit des données **neutres** ; le Collector décide où les envoyer, et changer de stockage ou envoyer à deux destinations pendant une migration devient une simple configuration.
- q: Qu'est-ce que l'observabilité « as code » ?
  a: 'Gérer dans Git, revus en merge request et déployés automatiquement : les **règles d''alerte** (PrometheusRule, monitors Datadog en Terraform), les **tableaux de bord** (JSON, provisioning, ConfigMaps), les **SLO** (Sloth, Pyrra), la configuration des **agents** et des **Collectors**, et les **runbooks**.'
- q: Quelle architecture type pour une entreprise avec un parc classique et des clusters Kubernetes ?
  a: '**Centreon** (ou Zabbix) pour le réseau, le matériel et les applications classiques ; **Prometheus** dans chaque cluster, envoyé dans **Mimir**, **Thanos** ou **VictoriaMetrics** ; **Loki** ou **Elasticsearch** pour les logs ; **Tempo** pour les traces via OpenTelemetry ; **Grafana** comme interface commune ; **Alertmanager** et un outil d''astreinte pour notifier.'
quiz:
- q: Une équipe de 4 personnes sans temps pour exploiter une stack, 30 services sur un cloud public, budget correct. Quel choix est le plus raisonnable ?
  options:
  - Construire Mimir, Loki et Tempo en microservices
  - Une plateforme SaaS (Datadog, Grafana Cloud, Elastic Cloud…) alimentée par OpenTelemetry, avec un suivi régulier des coûts
  - Rien, les logs suffisent
  - Nagios seul
  answer: 1
  explain: 'Le temps humain est un coût : sans capacité d''exploitation, le SaaS est souvent moins cher au total, et OpenTelemetry garde la porte ouverte.'
- q: Pourquoi l'auto-hébergé devient-il souvent plus intéressant à grande échelle ?
  options:
  - Il est toujours gratuit
  - Parce que la facture SaaS croît avec les volumes (hôtes, séries, logs, traces) alors qu'une stack interne bien exploitée a un coût surtout fixe ; à condition d'avoir l'équipe pour l'opérer
  - Il est plus simple
  - Il n'a pas besoin de stockage
  answer: 1
  explain: Le point de bascule dépend des volumes et du coût de l'équipe ; il se calcule, il ne se devine pas.
level: intermédiaire
---

Elastic, Centreon, Kibana, Grafana, Datadog, Loki, Prometheus, Tempo, OpenTelemetry… Après avoir vu chaque outil, reste la question de ton travail réel : **lesquels assembler**, et comment les faire vivre. Il n'y a pas de stack idéale, mais il y a une méthode, quelques architectures types et des erreurs à éviter.

> **Les outils cités dans cette fiche.**
> - **LGTM** : Loki, Grafana, Tempo, Mimir, la stack open source de Grafana Labs.
> - **Pyroscope** : l'outil de profilage continu de Grafana Labs.
> - **OpenTelemetry Collector** : l'agent et la passerelle neutres qui reçoivent et routent tous les signaux.
> - **Sloth** et **Pyrra** : des générateurs de règles de SLO pour Prometheus.
> - **TCO** (Total Cost of Ownership) : le coût total, licences ou abonnement, infrastructure et temps humain compris.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **stack** | l'ensemble des outils assemblés pour un besoin (collecte, stockage, visualisation, alertes) |
| **auto-hébergé** | installé et exploité par ton équipe, sur tes serveurs ou ton cloud |
| **SaaS** | un service en ligne opéré par le fournisseur, payé à l'usage |
| **neutre** (vendor-neutral) | qui ne dépend pas d'un fournisseur : on peut changer de destination sans réinstrumenter |
| **observabilité as code** | règles, tableaux de bord et configuration gérés dans Git et déployés automatiquement |
| **convention de nommage** | des noms d'étiquettes et de services communs à toutes les équipes, pour que les données se recoupent |
| **TCO** | le coût total : abonnement ou licences, serveurs, stockage, et temps passé par l'équipe |

## Comprendre : choisir par couche

```
INSTRUMENTATION   OpenTelemetry (SDK, auto-instrumentation) · bibliothèques Prometheus · logs JSON
COLLECTE          OTel Collector · Alloy · Fluent Bit / Vector · Elastic Agent · Datadog Agent · pollers Centreon
STOCKAGE          métriques : Prometheus → Mimir / Thanos / VictoriaMetrics   (ou Datadog, Elastic)
                  logs      : Loki  ou  Elasticsearch / OpenSearch           (ou Datadog Logs)
                  traces    : Tempo · Jaeger · Elastic APM                     (ou Datadog APM)
VISUALISATION     Grafana · Kibana · Datadog
ALERTE            Alertmanager · Grafana Alerting · Kibana rules · Datadog monitors · Centreon
ASTREINTE         PagerDuty · Opsgenie · Grafana IRM
```

Garder l'instrumentation et la collecte **neutres** (OpenTelemetry) laisse la liberté de changer le stockage plus tard.

## Trois architectures types

| Profil | Stack | Pourquoi |
| --- | --- | --- |
| cloud native auto-hébergé | Prometheus + Mimir (ou Thanos, VictoriaMetrics), Loki, Tempo, Grafana, Alertmanager, OTel Collector | open source, stockage objet bon marché, PromQL partout |
| entreprise avec parc mixte | Centreon pour réseau, matériel et applications classiques ; stack Prometheus/Grafana pour Kubernetes et OpenStack ; Elasticsearch pour les logs et la sécurité | chaque outil sur son terrain, Grafana comme vue commune |
| petite équipe, cloud public | SaaS (Datadog, Grafana Cloud, Elastic Cloud…) alimenté par OpenTelemetry | pas d'exploitation, mise en route rapide, coûts à surveiller |

## Loki ou Elasticsearch pour les logs ?

| Besoin | Plutôt |
| --- | --- |
| logs d'applications et de Kubernetes, recherche par service et période | Loki |
| coût de stockage minimal, stockage objet | Loki |
| recherche plein texte rapide sur des mois, analyses complexes | Elasticsearch |
| sécurité (SIEM), conformité, audit | Elasticsearch / OpenSearch |
| équipe déjà experte Elastic | Elasticsearch |

## Faire vivre la stack

- **Tout en code** : règles, tableaux de bord, SLO, configuration des agents, dans Git, déployés par la CI ou ArgoCD.
- **Des conventions** partagées : noms de services, étiquettes (`env`, `service`, `team`), format des logs, conventions sémantiques OpenTelemetry.
- **Une offre de plateforme** : les équipes applicatives ajoutent un `ServiceMonitor`, une annotation d'auto-instrumentation et reçoivent tableaux de bord et alertes de base.
- **La cardinalité et les coûts** suivis comme un budget : top des métriques et des émetteurs de logs, limites par équipe.
- **La supervision de la supervision** : dead man's switch, alertes sur l'ingestion, haute disponibilité des composants critiques.
- **La revue régulière** : alertes inutiles supprimées, tableaux de bord abandonnés archivés, runbooks mis à jour après chaque incident.

## Les erreurs classiques

1. Tout collecter « au cas où » : facture et bruit sans valeur.
2. Multiplier les outils sans lien : trois interfaces pour un incident.
3. Des tableaux de bord pour tout et des alertes sur les causes plutôt que sur les symptômes.
4. Oublier les logs et traces dans la conception d'une application : on les ajoute pendant l'incident, trop tard.
5. Ne pas surveiller la plateforme d'observabilité elle-même.

## Pour aller plus loin

La certification **Prometheus Certified Associate** (PCA) de la Linux Foundation, celle d'**OpenTelemetry** (OTCA), les certifications **Elastic** ou **Datadog**, et l'administration **Centreon** valident ces compétences. Mais le meilleur entraînement reste ton propre environnement : un tableau de bord RED par service, un SLO sur l'API la plus importante, et une revue des alertes avec l'équipe.

> **À retenir.** Choisir par couche (instrumentation, collecte, stockage, visualisation, alerte, astreinte) et garder l'instrumentation neutre avec OpenTelemetry. Trois profils types : LGTM auto-hébergé, parc mixte (Centreon plus Prometheus/Grafana plus Elastic), SaaS pour une petite équipe. Loki pour des logs bon marché par service, Elasticsearch pour le plein texte, la sécurité et l'analyse. Tout gérer en code, partager des conventions, suivre la cardinalité et les coûts, superviser la supervision, et revoir régulièrement alertes et tableaux de bord.
