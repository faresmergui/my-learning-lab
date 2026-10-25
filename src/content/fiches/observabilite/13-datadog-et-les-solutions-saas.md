---
title: Datadog et les plateformes SaaS
chapter: 13
order: 1
duration: 11
tags:
- Observabilité
- Datadog
- SaaS
cards:
- q: Comment Datadog collecte-t-il les données ?
  a: 'Par le **Datadog Agent** installé sur chaque hôte (ou en DaemonSet sur Kubernetes, avec le **Cluster Agent**), qui collecte métriques système, logs, traces (APM), processus et **intégrations** (plus de 800 : bases, files, serveurs web, clouds). Il **pousse** tout vers la plateforme SaaS. Les intégrations cloud (AWS, Azure, GCP) lisent aussi les API des fournisseurs.'
- q: Pourquoi les tags sont-ils centraux dans Datadog ?
  a: 'Toutes les données (métriques, logs, traces) portent des **tags** (`env:prod`, `service:commandes`, `version:2.14`, `team:plateforme`) qui servent à filtrer, regrouper et **relier** les signaux. Le **Unified Service Tagging** (`env`, `service`, `version`) est la base : sans lui, on ne passe pas facilement d''une métrique aux logs puis à la trace.'
- q: Quels sont les principaux produits de Datadog ?
  a: '**Infrastructure** (métriques, hôtes, conteneurs), **APM** (traces et performance applicative), **Log Management**, **Synthetics** (sondes boîte noire et parcours navigateur), **RUM** (expérience réelle des utilisateurs dans le navigateur ou l''appli mobile), **monitors** (alertes), **SLO**, **dashboards**, ainsi que des produits de sécurité et d''incidents.'
- q: Qu'est-ce qu'une métrique personnalisée chez Datadog et pourquoi surveiller leur nombre ?
  a: 'Une métrique envoyée par ton application ou une intégration non standard. Datadog facture notamment selon le nombre de **combinaisons nom + tags** distinctes : un tag à forte cardinalité (`user_id`, `pod_name` sur une métrique custom) multiplie la facture. Outils : *Metrics without Limits* pour ne garder que les tags utiles.'
- q: Quels sont les avantages et les inconvénients d'une plateforme SaaS ?
  a: '**Avantages** : rien à exploiter, mise en route rapide, tout intégré et relié (métriques, logs, traces, RUM), fonctionnalités avancées (anomalies, corrélations). **Inconvénients** : **coût** qui grimpe vite avec le volume et la cardinalité, données envoyées à l''extérieur (conformité), dépendance au fournisseur.'
quiz:
- q: La facture Datadog a doublé après l'ajout d'un tag `customer_id` sur une métrique de requêtes. Pourquoi ?
  options:
  - Bug de facturation
  - Chaque valeur de customer_id crée une nouvelle combinaison de métrique personnalisée, facturée ; il faut retirer ce tag de la métrique (le garder dans les logs ou traces) ou limiter les tags indexés
  - Datadog a changé ses prix
  - Le tag est mal orthographié
  answer: 1
  explain: Comme pour Prometheus, la cardinalité est le premier facteur de coût, ici directement sur la facture.
- q: Comment éviter de dépendre entièrement d'un fournisseur SaaS pour l'instrumentation ?
  options:
  - Ne rien instrumenter
  - 'Instrumenter avec OpenTelemetry (SDK et Collector) et exporter vers Datadog : changer de destination devient une modification du Collector, pas du code'
  - Utiliser seulement des captures d'écran
  - Écrire un agent maison
  answer: 1
  explain: Datadog accepte l'OTLP ; l'instrumentation reste portable.
level: intermédiaire
---

**Datadog** est la plateforme d'observabilité SaaS la plus connue : un agent par machine, et l'on obtient métriques, logs, traces, sondes et tableaux de bord reliés entre eux, sans rien héberger. Avec **New Relic**, **Dynatrace**, **Splunk Observability**, **Elastic Cloud** ou **Grafana Cloud**, ces offres sont une alternative (ou un complément) aux stacks auto-hébergées. Le principal sujet, en pratique, est souvent... la **facture**.

> **Les outils cités dans cette fiche.**
> - **SaaS** (Software as a Service) : un logiciel utilisé en ligne, opéré par le fournisseur.
> - **Datadog Agent** : l'agent qui collecte et envoie les données à Datadog ; **Cluster Agent** : son complément pour Kubernetes.
> - **APM** : la supervision des performances applicatives par les traces.
> - **RUM** (Real User Monitoring) : la mesure de l'expérience réelle des utilisateurs dans leur navigateur ou leur appli.
> - **Synthetics** : des tests automatiques qui simulent un utilisateur (API, parcours navigateur).
> - **New Relic**, **Dynatrace**, **Splunk Observability** : d'autres plateformes SaaS d'observabilité.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **agent** | le programme Datadog installé sur chaque machine (ou en pod sur chaque nœud Kubernetes) qui collecte et envoie les données |
| **intégration** | un module prêt à l'emploi pour une technologie (PostgreSQL, nginx, AWS) qui sait quelles métriques et quels logs récupérer |
| **tag** | une étiquette `clé:valeur` attachée à toutes les données (`env:prod`, `service:commandes`) |
| **métrique personnalisée** (custom metric) | une métrique qui ne vient pas d'une intégration standard ; chaque combinaison nom + tags compte dans la facture |
| **monitor** | une règle d'alerte dans Datadog |
| **APM** | la partie qui reçoit et affiche les traces des applications |
| **ingérer / indexer** | ingérer = recevoir les logs (facturé au volume) ; indexer = les rendre cherchables pendant la rétention (facturé en plus, au nombre d'événements) |
| **archive** et **réhydratation** | envoyer les logs dans un bucket à toi pour pas cher, puis les recharger dans Datadog à la demande pour une enquête |
| **RUM** | la mesure de ce que vivent les vrais utilisateurs dans leur navigateur (temps de chargement, erreurs JavaScript) |
| **Synthetics** | des tests automatiques lancés depuis plusieurs pays qui simulent un utilisateur |

## Comment ça marche : de l'agent à l'alerte

1. L'**agent** démarre sur l'hôte, détecte les logiciels présents (autodiscovery : « il y a un PostgreSQL dans ce conteneur ») et active les **intégrations** correspondantes.
2. Toutes les 15 secondes, il collecte les métriques système et celles des intégrations ; il lit aussi les logs et reçoit les traces envoyées par les applications sur le même hôte.
3. Il ajoute les **tags** de l'hôte et du conteneur (`env`, `service`, `kube_namespace`, `availability-zone`), regroupe, compresse et **pousse** le tout vers Datadog en HTTPS.
4. La plateforme stocke chaque type de donnée, relie métriques, logs et traces par leurs tags et le trace_id.
5. Les **monitors** sont évalués en continu côté Datadog ; quand l'un se déclenche, il envoie la notification, avec des liens vers le tableau de bord, les logs et les traces concernés.

Tu n'exploites aucun serveur : seul l'agent tourne chez toi. En contrepartie, tout ce que l'agent envoie est facturé selon le volume et le nombre de combinaisons de tags.

## Comprendre : un agent, une plateforme

```
hôtes, VM, conteneurs                         plateforme Datadog (SaaS)
 Datadog Agent ── métriques, logs, traces ──► Infrastructure · APM · Logs · Synthetics · RUM
 (+ Cluster Agent sur Kubernetes)                 │ tout relié par les tags env/service/version
 intégrations : nginx, PostgreSQL, Kafka…         ├─ monitors (alertes) → Slack, PagerDuty, e-mail
API cloud : AWS, Azure, GCP ─────────────────────►├─ dashboards, notebooks, SLO
navigateur / mobile (RUM) ───────────────────────►└─ corrélations, anomalies, incidents
```

## Les tags, la clé de tout

```yaml
# datadog.yaml (extrait) et variables d'environnement d'un conteneur
tags: [ "env:prod", "team:plateforme", "region:eu-west-3" ]
# dans le déploiement Kubernetes :
#   DD_ENV=prod  DD_SERVICE=commandes  DD_VERSION=2.14
#   labels: tags.datadoghq.com/env, tags.datadoghq.com/service, tags.datadoghq.com/version
```

Avec le **Unified Service Tagging**, un pic de latence sur `service:commandes` mène en un clic aux traces de cette version, puis aux logs de ces traces, puis à l'hôte. C'est ce qui fait gagner du temps pendant un incident.

## Monitors : les alertes

| Type de monitor | Exemple |
| --- | --- |
| métrique (seuil) | `avg(last_5m):avg:system.cpu.user{env:prod} by {host} > 90` |
| anomalie, prévision | trafic anormal par rapport à la saisonnalité habituelle ; disque plein dans 48 h |
| APM | taux d'erreurs ou latence p99 d'un service |
| logs | plus de 100 logs `status:error` sur `service:commandes` en 5 min |
| composite | alerter seulement si deux conditions sont vraies |
| synthetics | une API ou un parcours de connexion échoue depuis plusieurs lieux |
| SLO | budget d'erreur consommé trop vite (burn rate) |

Les monitors et tableaux de bord se gèrent **en code** avec le provider **Terraform Datadog** (`datadog_monitor`, `datadog_dashboard_json`), revus en MR comme le reste.

## Maîtriser les coûts

La facturation combine plusieurs dimensions (hôtes, conteneurs, métriques personnalisées, volume de logs ingérés et indexés, spans indexés, tests synthetics, sessions RUM). Les leviers :

- **Cardinalité** des métriques personnalisées : pas d'identifiants en tag ; *Metrics without Limits* pour choisir les tags indexés.
- **Logs** : ingérer peut coûter moins cher qu'indexer ; filtres d'exclusion, index séparés avec des rétentions différentes, archives dans un bucket S3 et réhydratation à la demande.
- **APM** : règles d'échantillonnage et de rétention des traces.
- **Suivi** : le tableau de bord d'utilisation et des alertes sur la consommation, par équipe (tags `team`).

## SaaS ou auto-hébergé

| Critère | SaaS (Datadog…) | Auto-hébergé (Prometheus, Grafana, Loki, Elastic…) |
| --- | --- | --- |
| mise en route | heures | jours à semaines |
| exploitation | aucune | une équipe doit l'opérer |
| coût | variable, croît avec le volume | infrastructure + temps humain, plus prévisible |
| données | chez le fournisseur | chez toi (conformité, souveraineté) |
| fonctionnalités | très intégrées (RUM, anomalies, sécurité) | à assembler soi-même |

Le bon compromis passe souvent par **OpenTelemetry** : on instrumente une fois, de façon neutre, et le Collector envoie là où on veut, SaaS ou interne, voire les deux pendant une migration.

> **À retenir.** Datadog collecte par un agent (et le Cluster Agent sur Kubernetes) plus des intégrations cloud, et relie métriques, logs, traces, synthetics et RUM grâce aux tags, surtout env, service et version. Les monitors couvrent seuils, anomalies, logs, APM, SLO et se gèrent en Terraform. Le coût dépend des hôtes, de la cardinalité des métriques personnalisées et des volumes de logs et de traces : filtrer, échantillonner, archiver. Le SaaS évite l'exploitation mais coûte plus quand le volume grandit et sort les données ; OpenTelemetry garde l'instrumentation portable.
