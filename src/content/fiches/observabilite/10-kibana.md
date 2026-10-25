---
title: Kibana et OpenSearch Dashboards
chapter: 10
order: 1
duration: 10
tags:
- Observabilité
- Kibana
- Elastic
- OpenSearch
cards:
- q: À quoi sert Discover dans Kibana ?
  a: 'À **explorer les documents** d''une data view (anciennement *index pattern*) : choisir la période, filtrer avec **KQL** ou des filtres cliquables, afficher les champs utiles en colonnes, voir l''histogramme du volume, et ouvrir un document pour en voir tous les champs.'
- q: Qu'est-ce que KQL ?
  a: 'Le **Kibana Query Language** : `service.name : "commandes" and http.response.status_code >= 500 and not url.path : "/healthz"`. Simple, avec autocomplétion des champs. Kibana propose aussi **Lucene**, et **ES|QL**, un langage en tubes (`FROM logs-* | WHERE … | STATS count() BY service.name`) pour les analyses plus poussées.'
- q: Qu'est-ce qu'une data view ?
  a: La description de **quels index** Kibana interroge (`logs-*`, `logs-commandes-*`) et de quel champ sert d'horodatage. Discover, les visualisations et les tableaux de bord s'appuient dessus.
- q: Comment construire une visualisation dans Kibana ?
  a: 'Avec **Lens**, l''éditeur par glisser-déposer : choisir un champ (par exemple `http.response.status_code`), une agrégation (comptage, moyenne, percentile), une répartition (par service, par code) et un type de graphique. Les visualisations se regroupent dans des **dashboards** avec filtres partagés.'
- q: Qu'est-ce qu'OpenSearch Dashboards ?
  a: 'Le fork de Kibana associé à **OpenSearch** (proposé notamment par Amazon OpenSearch Service). Même logique : Discover, visualisations, tableaux de bord, alertes par plugin, avec ses propres langages (DQL proche de KQL, PPL, SQL).'
quiz:
- q: Quelle requête KQL affiche les erreurs 5xx de l'API commandes, hors sondes de santé ?
  options:
  - '`commandes 500`'
  - '`service.name : "commandes" and http.response.status_code >= 500 and not url.path : "/healthz"`'
  - '`SELECT * FROM commandes`'
  - '`{app="commandes"} |= "500"`'
  answer: 1
  explain: KQL filtre sur des champs nommés (ici au format ECS) ; la dernière proposition est du LogQL (Loki).
- q: Un tableau de bord Kibana met une minute à charger sur 90 jours. Que fais-tu ?
  options:
  - Ajouter des panneaux
  - Réduire la période par défaut, agréger sur des champs keyword, utiliser des index de résumés (transforms ou rollups) pour le long terme, et vérifier que les données froides ne sont pas sollicitées inutilement
  - Supprimer les replicas
  - Passer en texte libre
  answer: 1
  explain: Les requêtes sur de longues périodes touchent des tiers de stockage lents ; les vues résumées sont faites pour cela.
level: intermédiaire
---

**Kibana** est l'interface de la stack Elastic : on y cherche dans les logs, on construit des tableaux de bord, on gère les alertes, les agents (Fleet), l'APM et la sécurité. Si ton entreprise utilise Elasticsearch ou OpenSearch, c'est l'outil que tu ouvriras pendant un incident pour retrouver la ligne de log qui explique tout.

> **Les outils cités dans cette fiche.**
> - **Kibana** : l'interface web de la stack Elastic.
> - **KQL** (Kibana Query Language) : le langage de filtre simple de Kibana ; **Lucene** : l'ancienne syntaxe de requête ; **ES|QL** : le langage de requête en tubes d'Elasticsearch.
> - **data view** : la définition des index que Kibana interroge.
> - **Lens** : l'éditeur de visualisations par glisser-déposer.
> - **OpenSearch Dashboards** : l'équivalent de Kibana pour OpenSearch.
> - **APM** (Application Performance Monitoring) : la supervision des performances applicatives (traces, transactions).

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **Discover** | l'écran de Kibana pour lire et filtrer les documents un par un |
| **data view** | le choix des index à interroger (`logs-*`) et du champ de date |
| **filtre** | une condition ajoutée par un clic (« service.name est commandes ») qui s'applique à toute la page |
| **KQL** | la syntaxe de recherche simple : `champ : valeur and autre_champ >= 500` |
| **agrégation** | un calcul sur beaucoup de documents : compter, faire une moyenne, trouver les valeurs les plus fréquentes |
| **visualisation** | un graphique construit à partir d'agrégations |
| **dashboard** | une page qui réunit plusieurs visualisations avec des filtres communs |
| **règle** (rule) | une recherche évaluée régulièrement qui déclenche une alerte |
| **connecteur** | la destination d'une alerte (Slack, e-mail, PagerDuty, webhook) |
| **space** | un espace de travail séparé dans Kibana, avec ses propres objets et droits |
| **NDJSON** | un format d'export : un objet JSON par ligne |

## Comment ça marche : une recherche dans Discover

1. Tu choisis une **data view** (`logs-*`) et une période (« 15 dernières minutes »).
2. Tu tapes une requête KQL et ajoutes des filtres. Kibana traduit le tout en une requête Elasticsearch (en JSON).
3. Elasticsearch cherche dans les index concernés, grâce à l'index inversé, et renvoie deux choses : les **documents** les plus récents qui correspondent (affichés en liste) et une **agrégation** par tranche de temps (l'histogramme du volume en haut).
4. Tu cliques sur un document pour voir tous ses champs ; un clic sur une valeur ajoute un filtre (« ne garder que ce pod »), et la recherche est relancée.

Une visualisation fonctionne de la même façon, mais demande seulement des **agrégations** (« nombre de documents par code HTTP et par minute ») au lieu des documents eux-mêmes.

## Comprendre : les espaces de Kibana

```
Kibana
 ├─ Discover        chercher et lire les documents (logs)
 ├─ Dashboards      tableaux de bord (Lens, cartes, métriques)
 ├─ Observability   logs, métriques d'infrastructure, APM, uptime/synthetics, SLO
 ├─ Security        SIEM : règles de détection, alertes, enquêtes
 ├─ Alerts & rules  règles d'alerte et connecteurs (Slack, e-mail, PagerDuty, webhook)
 ├─ Fleet           gestion des Elastic Agents
 └─ Stack Management : data views, ILM, templates, rôles, espaces (spaces)
```

## Chercher : KQL et ES|QL

```text
# KQL dans Discover
service.name : "commandes" and log.level : "error"
http.response.status_code >= 500 and not url.path : "/healthz"
kubernetes.namespace : "prod-*" and message : "timeout"
trace.id : "4bf92f3577b34da6a3ce929d0e0e4736"
```

```text
# ES|QL : analyser
FROM logs-*
| WHERE http.response.status_code >= 500 AND @timestamp > NOW() - 1 hour
| STATS erreurs = COUNT(*) BY service.name
| SORT erreurs DESC
| LIMIT 10
```

Bonnes habitudes dans Discover : **réduire la période** d'abord, filtrer sur des champs `keyword` plutôt que chercher du texte partout, ajouter les colonnes utiles (`service.name`, `log.level`, `message`), et enregistrer les recherches fréquentes.

## Visualiser

- **Lens** : glisser un champ, choisir l'agrégation (comptage, somme, moyenne, percentile, valeurs uniques) et la répartition ; Kibana propose le type de graphique.
- **Dashboards** : regrouper les visualisations, avec des **filtres** et une période partagés, des contrôles (listes déroulantes de services) et des liens vers Discover.
- **Exemples utiles** : volume de logs par niveau et par service, top des erreurs, codes HTTP dans le temps, latence p95 depuis un champ de durée.

## Alerter

Les **règles** de Kibana surveillent une requête (seuil sur un comptage KQL ou ES|QL, anomalie, absence de données) à intervalle régulier et déclenchent des **actions** via des connecteurs. Comme pour Grafana, mieux vaut des alertes qui demandent une action, un lien vers le runbook et une sévérité claire.

## Gérer les accès

- **Spaces** : des espaces séparés par équipe, avec leurs tableaux de bord et data views.
- **Rôles** : droits par index (lecture de `logs-commandes-*` seulement), voire par champ ou par document.
- **SSO** : SAML ou OIDC vers l'annuaire de l'entreprise.
- Les objets (tableaux de bord, recherches) s'exportent en **NDJSON** pour être versionnés ou copiés d'un environnement à l'autre.

## Kibana ou Grafana ?

| | Kibana | Grafana |
| --- | --- | --- |
| sources | Elasticsearch seulement | des dizaines (dont Elasticsearch) |
| point fort | recherche et lecture des logs, SIEM, APM intégré | tableaux de bord multi-sources, métriques |
| tableaux de bord en code | export NDJSON, API | JSON, provisioning, Terraform |

Beaucoup d'équipes utilisent les deux : Kibana pour fouiller les logs, Grafana pour les tableaux de bord qui mélangent métriques Prometheus et données Elasticsearch.

> **À retenir.** Kibana est l'interface de la stack Elastic : Discover pour chercher dans les logs (avec KQL, Lucene ou ES|QL), Lens et les dashboards pour visualiser, des règles et connecteurs pour alerter, plus Fleet, APM et SIEM. Réduire la période et filtrer sur des champs keyword. Spaces et rôles pour séparer les équipes, export NDJSON pour versionner. OpenSearch Dashboards est son équivalent côté OpenSearch, et Grafana le complète pour les tableaux de bord multi-sources.
