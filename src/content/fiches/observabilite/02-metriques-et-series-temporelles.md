---
title: Métriques et séries temporelles
chapter: 2
order: 1
duration: 10
tags:
- Observabilité
- Métriques
cards:
- q: Qu'est-ce qu'une série temporelle ?
  a: Une suite de couples **(horodatage, valeur)** pour une métrique et un ensemble d'étiquettes donnés. `http_requests_total{service="api", code="500"}` est une série ; changer une étiquette crée une autre série.
- q: Quels sont les quatre types de métriques de Prometheus ?
  a: '**Counter** (compteur qui ne fait que monter, remis à zéro au redémarrage : requêtes, erreurs, octets), **gauge** (valeur qui monte et descend : mémoire, température, file d''attente), **histogram** (répartit les mesures dans des tranches, *buckets*, pour calculer des percentiles côté serveur) et **summary** (percentiles calculés par le client, non agrégeables).'
- q: Pourquoi la moyenne de latence est-elle trompeuse ?
  a: 'Parce qu''elle cache la **traîne** : avec 99 requêtes à 50 ms et une à 5 s, la moyenne vaut 100 ms, alors qu''un utilisateur sur cent attend 5 s. On suit des **percentiles** (p95, p99), calculés à partir d''histogrammes.'
- q: Différence entre modèle pull et modèle push ?
  a: En **pull**, le système de supervision va **chercher** les métriques sur chaque cible à intervalle régulier (Prometheus, Centreon par ses sondes). En **push**, les agents **envoient** leurs métriques à un collecteur (Datadog, StatsD, OpenTelemetry, Graphite). Le pull détecte facilement qu'une cible ne répond plus ; le push traverse plus facilement les pare-feu et convient aux tâches courtes.
- q: Que sont la résolution et la rétention ?
  a: 'La **résolution** est l''intervalle entre deux points (15 s, 1 min). La **rétention** est la durée de conservation. Les données anciennes sont souvent **sous-échantillonnées** (downsampling) : points toutes les 5 minutes puis toutes les heures, pour garder des tendances sur des mois à moindre coût.'
quiz:
- q: Le compteur `http_requests_total` passe de 15 000 à 120 après un redémarrage du pod. Comment Prometheus le gère-t-il dans `rate()` ?
  options:
  - Il calcule un débit négatif
  - rate() détecte la remise à zéro d'un counter et la compense automatiquement
  - Il supprime la série
  - Il faut redémarrer Prometheus
  answer: 1
  explain: C'est pourquoi on n'utilise rate() et increase() que sur des counters, jamais sur des gauges.
- q: Tu veux le p99 de latence agrégé sur 20 pods. Quel type de métrique faut-il ?
  options:
  - Un summary dans chaque pod
  - Un histogram, dont les buckets s'additionnent entre pods avant de calculer le percentile
  - Une gauge
  - Un counter seul
  answer: 1
  explain: On ne peut pas faire la moyenne de percentiles ; les buckets d'histogrammes, eux, s'additionnent.
level: intermédiaire
---

La métrique est le signal de base de toute supervision : peu coûteuse, facile à agréger, idéale pour les tableaux de bord et les alertes. Comprendre comment elle est représentée (séries, étiquettes, types) évite les deux erreurs les plus fréquentes : des calculs faux (moyenne de percentiles, `rate` sur une gauge) et une cardinalité qui explose.

> **Les outils cités dans cette fiche.**
> - **série temporelle** : une suite de valeurs horodatées.
> - **TSDB** (Time Series Database) : une base optimisée pour les séries temporelles (Prometheus, VictoriaMetrics, InfluxDB, Graphite, RRD de Centreon).
> - **étiquette** (label, tag) : une paire clé-valeur qui précise une métrique (`service="api"`).
> - **percentile** (p95, p99) : la valeur sous laquelle se trouvent 95 % ou 99 % des mesures.
> - **StatsD** et **Graphite** : des systèmes historiques de métriques en push.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **horodatage** (timestamp) | la date et l'heure exactes d'une mesure, souvent en secondes depuis le 1er janvier 1970 (« temps Unix ») |
| **scrape** | l'action, pour Prometheus, d'aller lire la page de métriques d'un service ; on dit « scraper une cible » |
| **intervalle de collecte** | le temps entre deux lectures (15 s, 30 s, 1 min) : c'est la finesse des graphiques |
| **bucket** | une « tranche » d'un histogramme : « nombre de requêtes de moins de 100 ms », « de moins de 500 ms »… |
| **remise à zéro** (reset) | quand un compteur repart de 0 parce que le programme a redémarré |
| **sous-échantillonnage** (downsampling) | remplacer des points très rapprochés par un point moyen toutes les 5 minutes ou toutes les heures, pour garder l'historique à moindre coût |
| **rétention** | la durée pendant laquelle on garde les données avant de les supprimer |
| **Pushgateway** | un intermédiaire de Prometheus où les tâches courtes (scripts, sauvegardes) déposent leurs métriques avant de s'arrêter |
| **OTLP** | le protocole d'envoi de données d'OpenTelemetry (voir la fiche traces) |

## Comment ça marche : d'un compteur à un graphique

Prenons un serveur web qui compte ses requêtes.

1. Dans le programme, une variable `http_requests_total` augmente de 1 à chaque requête. Elle ne redescend jamais (c'est un **counter**).
2. Toutes les 30 secondes, le système de supervision lit sa valeur : 15 000, puis 15 060, puis 15 150…
3. Il enregistre chaque lecture avec son horodatage : c'est la **série temporelle**.
4. Pour afficher « requêtes par seconde », on ne trace pas la valeur brute (qui ne fait que monter) mais sa **pente** : (15 150 − 15 060) / 30 s = 3 requêtes par seconde. C'est exactement ce que calcule la fonction `rate()` de Prometheus.
5. Si le serveur redémarre, le compteur repart de 0 ; la fonction le détecte et ne compte pas une chute négative.

Pour une **gauge** (mémoire utilisée), on trace directement la valeur lue. Pour un **histogramme**, le programme maintient un compteur par tranche de durée ; en comparant les tranches, on retrouve combien de requêtes sont lentes, d'où les percentiles.

## Comprendre : une métrique, des séries

```
nom              étiquettes                                    valeur   horodatage
http_requests_total{service="api", method="GET", code="200"}   15342    1729758000
http_requests_total{service="api", method="GET", code="500"}      12    1729758000
http_requests_total{service="api", method="POST", code="200"}   2210    1729758000
```

Chaque combinaison d'étiquettes est une **série** distincte. Le nombre de séries d'une métrique est le produit des valeurs possibles de ses étiquettes : 50 services × 5 méthodes × 10 codes × 30 pods = 75 000 séries. Ajoute une étiquette `user_id` et on passe à des millions.

**Règle** : une étiquette doit avoir un nombre de valeurs **borné et faible** (service, méthode, code, zone). Les identifiants uniques (utilisateur, requête, session, adresse IP) vont dans les logs et les traces.

## Les types de métriques

| Type | Évolution | Exemples | Comment l'exploiter |
| --- | --- | --- | --- |
| counter | ne fait que monter (remise à zéro au redémarrage) | requêtes, erreurs, octets envoyés | `rate()`, `increase()` |
| gauge | monte et descend | mémoire utilisée, connexions actives, file d'attente | valeur brute, `avg`, `max` |
| histogram | compte les mesures par tranche (buckets) | durée des requêtes, taille des réponses | `histogram_quantile()` |
| summary | percentiles calculés par l'application | durée (ancien usage) | lire tel quel, non agrégeable |

Un histogramme Prometheus produit en réalité plusieurs séries : `_bucket{le="0.1"}`, `_bucket{le="0.5"}`, … (nombre de mesures inférieures ou égales à la borne), `_sum` et `_count`. Les **histogrammes natifs** des versions récentes de Prometheus rendent cela plus compact et plus précis.

## Pourquoi des percentiles

```
99 requêtes à 50 ms + 1 requête à 5 000 ms
moyenne = 99,5 ms        ← tout semble aller bien
p99     = 5 000 ms       ← un utilisateur sur cent attend 5 secondes
```

Les SLO de latence s'expriment presque toujours en percentiles (« 99 % des requêtes en moins de 300 ms »). Et on ne fait **jamais la moyenne de percentiles** de plusieurs instances : on additionne les buckets puis on calcule le percentile.

## Pull ou push

| | Pull | Push |
| --- | --- | --- |
| qui initie | le serveur interroge la cible | l'agent envoie |
| exemples | Prometheus, sondes Centreon | Datadog, OpenTelemetry (OTLP), StatsD, Graphite |
| cible tombée | visible immédiatement (`up == 0`) | il faut détecter l'absence de données |
| réseau | le serveur doit joindre les cibles | les agents doivent joindre le collecteur |
| tâches courtes (batch) | peu adapté (Pushgateway) | naturel |

Dans la pratique, les stacks modernes mélangent les deux : Prometheus scrape, mais reçoit aussi en `remote_write` ; l'OpenTelemetry Collector reçoit en push et peut aussi scraper.

## Résolution, rétention, coût

- **Intervalle de collecte** : 15 à 60 s pour la plupart des métriques ; 10 s pour les plus critiques ; 1 à 5 min pour les métriques lentes (disque).
- **Rétention** : quelques semaines en local ; des mois ou des années dans un stockage long terme, avec **sous-échantillonnage**.
- **Coût** = nombre de séries actives × fréquence × durée : la cardinalité reste le premier levier, avant la fréquence.

> **À retenir.** Une métrique est découpée en séries par ses étiquettes ; leur nombre (cardinalité) doit rester borné : pas d'identifiants uniques en étiquette. Counter (rate, increase), gauge (valeur), histogram (percentiles agrégeables), summary (non agrégeable). Suivre des percentiles plutôt que des moyennes, et additionner les buckets avant de calculer un percentile. Pull (Prometheus) et push (Datadog, OpenTelemetry) coexistent. Résolution et rétention se règlent selon le besoin, avec sous-échantillonnage pour le long terme.
