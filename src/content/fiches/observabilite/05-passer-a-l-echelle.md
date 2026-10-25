---
title: 'Stockage long terme : Thanos, Mimir, VictoriaMetrics'
chapter: 5
order: 1
duration: 11
tags:
- Observabilité
- Prometheus
- Thanos
- Mimir
cards:
- q: Pourquoi un stockage long terme pour Prometheus ?
  a: Pour garder les métriques des **mois ou des années** (capacité, tendances, SLO), avoir une **vue globale** sur plusieurs clusters ou datacenters dans une seule requête, et rendre la supervision **hautement disponible** sans dépendre du disque d'un seul serveur.
- q: Comment fonctionne Thanos ?
  a: Un **sidecar** à côté de chaque Prometheus envoie les blocs de données vers un **stockage objet** (S3, Swift, Ceph RGW, GCS) et répond aux requêtes récentes. Le **Querier** interroge tous les sidecars et le **Store Gateway** (données anciennes) et **déduplique** les paires HA. Le **Compactor** compacte et sous-échantillonne. Le **Ruler** évalue les règles globales.
- q: Qu'est-ce que Grafana Mimir ?
  a: Une base de métriques **distribuée et multi-tenant** compatible Prometheus, issue de Cortex. Les Prometheus (ou Grafana Alloy, ou l'OpenTelemetry Collector) lui envoient les données en **remote_write** ; Mimir les répartit, les réplique, les stocke dans du stockage objet et répond en PromQL à grande échelle.
- q: Qu'est-ce que VictoriaMetrics ?
  a: Une base de séries temporelles compatible Prometheus (ingestion en remote_write, requêtes en PromQL étendu, MetricsQL), réputée pour sa **sobriété** en mémoire et en disque. Elle existe en version mono-nœud, très simple, et en cluster. vmagent peut remplacer Prometheus pour la collecte.
- q: Qu'est-ce que le multi-tenant dans Mimir ou Loki ?
  a: Plusieurs **locataires** (équipes, clients, environnements) partagent la même plateforme, chacun avec ses données isolées, ses limites (séries, débit) et ses quotas. Le locataire est indiqué par un en-tête HTTP (`X-Scope-OrgID`), généralement ajouté par une passerelle authentifiée.
quiz:
- q: Tu as 6 clusters Kubernetes avec chacun un Prometheus, et tu veux un seul tableau de bord global avec 1 an d'historique. Quelle architecture ?
  options:
  - Augmenter la rétention locale de chaque Prometheus à 1 an
  - Un stockage long terme commun (Thanos avec sidecars, ou Mimir/VictoriaMetrics en remote_write) sur du stockage objet, interrogé en PromQL par Grafana
  - Copier les disques tous les soirs
  - Un Prometheus central qui scrape tout à travers Internet
  answer: 1
  explain: La vue globale et la longue rétention sont précisément le rôle de ces systèmes.
- q: Une équipe envoie soudain 5 millions de nouvelles séries dans Mimir. Quel mécanisme protège les autres ?
  options:
  - Aucun
  - Les limites par locataire (séries actives, débit d'ingestion) qui rejettent l'excès de cette équipe seulement
  - Le redémarrage de Mimir
  - La compaction
  answer: 1
  explain: Les limites par tenant évitent qu'une explosion de cardinalité chez l'un dégrade la plateforme de tous.
level: intermédiaire
---

Un serveur Prometheus suffit pour un cluster et quelques semaines d'historique. Dès qu'on a plusieurs clusters, plusieurs datacenters, des besoins de rétention longue ou de haute disponibilité, il faut une couche de **stockage long terme** compatible Prometheus. Trois familles dominent : **Thanos**, **Grafana Mimir** et **VictoriaMetrics**. Toutes gardent PromQL et Grafana : seul le stockage change.

> **Les outils cités dans cette fiche.**
> - **Thanos** : un ensemble de composants qui ajoutent à Prometheus stockage objet, vue globale et déduplication.
> - **Grafana Mimir** : une base de métriques distribuée et multi-tenant compatible Prometheus (successeur de **Cortex**).
> - **VictoriaMetrics** : une base de séries temporelles compatible Prometheus, sobre en ressources ; **vmagent** : son agent de collecte.
> - **remote_write** : le protocole par lequel Prometheus envoie ses données à un autre système.
> - **stockage objet** : S3, Swift, Ceph RGW, GCS (voir les fiches AWS et OpenStack).
> - **Grafana Alloy** : l'agent de collecte de Grafana (métriques, logs, traces), successeur de Grafana Agent et de Promtail.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **stockage long terme** | un endroit où garder les métriques des mois ou des années, au-delà des quelques semaines d'un Prometheus |
| **stockage objet** | un stockage de fichiers accessibles par HTTP (S3, Swift), peu cher et presque illimité, mais plus lent qu'un disque local |
| **bloc** | un fichier de données Prometheus qui couvre 2 heures ; c'est l'unité envoyée vers le stockage objet |
| **compaction** | fusionner plusieurs petits blocs en un plus gros, plus rapide à lire |
| **déduplication** | quand deux Prometheus identiques collectent les mêmes données (pour la haute disponibilité), ne garder qu'une copie au moment de la lecture |
| **haute disponibilité** (HA) | le service continue de fonctionner si une machine tombe, parce qu'une autre fait le même travail |
| **ingester** | dans Mimir ou Loki, le composant qui reçoit les données récentes, les garde en mémoire, puis les écrit dans le stockage objet |
| **distributor** | le composant d'entrée qui vérifie les données reçues et les répartit entre les ingesters |
| **querier** | le composant qui exécute les requêtes en lisant les ingesters (données récentes) et le stockage objet (données anciennes) |
| **query-frontend** | le composant devant les queriers qui découpe les longues requêtes et met les résultats en cache |
| **réplication** | écrire chaque donnée sur plusieurs machines (souvent 3) pour ne rien perdre si l'une tombe |
| **tenant** (locataire) | une équipe ou un client isolé sur une plateforme partagée, avec ses propres données et limites |
| **microservices** (mode de déploiement) | chaque rôle (distributor, ingester, querier…) tourne séparément et se dimensionne indépendamment |

## Comment ça marche : le chemin d'une donnée dans Mimir

1. Chaque Prometheus collecte ses cibles comme d'habitude, puis **envoie** en continu ses nouvelles valeurs à Mimir par `remote_write` (une requête HTTP toutes les quelques secondes).
2. Le **distributor** reçoit le lot, vérifie les limites du tenant (nombre de séries, débit), et calcule pour chaque série quels **ingesters** doivent la garder (3 copies).
3. Les **ingesters** gardent les données récentes en mémoire et sur un petit disque de secours. Toutes les 2 heures, ils écrivent un **bloc** dans le **stockage objet**.
4. Un **compactor** fusionne les blocs, supprime les doublons et applique la rétention.
5. Quand Grafana demande « le débit des 30 derniers jours », le **query-frontend** découpe la période en morceaux d'un jour, les **queriers** lisent les ingesters pour les dernières heures et le stockage objet pour le reste, puis le résultat est assemblé et mis en cache.

Avec **Thanos**, l'étape 1 est différente : chaque Prometheus garde ses données et un sidecar copie ses blocs dans le stockage objet ; le **Querier** de Thanos interroge à la fois les sidecars (données récentes) et le stockage (données anciennes).

## Comprendre : deux façons de centraliser

```
A. Thanos (les Prometheus gardent la main)
Prometheus + sidecar ──► blocs toutes les 2 h ──► stockage objet ◄── Store Gateway
        ▲                                                              ▲
        └──────────── Thanos Querier (dédupliquera les paires HA) ─────┘ ◄── Grafana
                      Compactor : compaction et sous-échantillonnage (5 min, 1 h)

B. Mimir ou VictoriaMetrics (tout est poussé)
Prometheus / Alloy / vmagent / OTel Collector ──remote_write──► distributeur ──► ingesters ──► stockage objet
                                                                                    ▲
                                                           Grafana ──► query-frontend ┘ (PromQL)
```

## Comparer

| | Thanos | Mimir | VictoriaMetrics |
| --- | --- | --- | --- |
| modèle | sidecar ou receive, stockage objet | remote_write, microservices | remote_write ou scrape (vmagent), mono-nœud ou cluster |
| multi-tenant | possible (Receive) | natif, avec limites par tenant | cluster : oui |
| complexité | moyenne | élevée (plusieurs composants, souvent sur Kubernetes) | faible en mono-nœud |
| stockage | objet | objet | disque local (ou bloc) |
| requêtes | PromQL | PromQL | PromQL étendu (MetricsQL) |
| point fort | ajout progressif à des Prometheus existants | grande échelle, plateforme partagée | simplicité, sobriété |

Il existe aussi des offres gérées : Amazon Managed Service for Prometheus, Grafana Cloud, et les SaaS comme Datadog qui acceptent le format Prometheus.

## Envoyer en remote_write

```yaml
remote_write:
  - url: https://mimir.example.com/api/v1/push
    headers: { X-Scope-OrgID: equipe-plateforme }
    queue_config: { max_samples_per_send: 5000 }
    write_relabel_configs:
      - source_labels: [__name__]
        regex: "go_.*|process_.*"
        action: drop               # ne pas envoyer ce qui ne sert pas
```

Le relabeling à l'envoi est l'outil principal pour **réduire la facture** : supprimer les métriques inutiles, les étiquettes à forte cardinalité, ou agréger avant d'envoyer (recording rules).

## Exploiter la couche long terme

- **Cardinalité** : limites par tenant (séries actives, débit), tableaux de bord des plus grosses métriques, revue régulière.
- **Rétention par résolution** : données brutes 30 jours, 5 minutes pendant 6 mois, 1 heure pendant 2 ans (Thanos Compactor).
- **Stockage objet** : sur OpenStack, Swift ou Ceph RGW conviennent ; prévoir le cycle de vie et la supervision du bucket.
- **Requêtes lentes** : query-frontend avec cache et découpage des longues périodes, recording rules pour les tableaux de bord lourds.
- **Haute disponibilité** : réplication (Mimir réplique chaque série sur 3 ingesters), paires Prometheus dédupliquées (Thanos).

> **À retenir.** Un Prometheus seul est limité en rétention, en haute disponibilité et en vue globale. Thanos ajoute un sidecar qui envoie les blocs dans du stockage objet et un Querier qui fusionne et déduplique. Mimir et VictoriaMetrics reçoivent les données en remote_write ; Mimir est distribué et multi-tenant, VictoriaMetrics très simple et sobre. Tous gardent PromQL et Grafana. Le relabeling à l'envoi et les limites par tenant maîtrisent la cardinalité et les coûts.
