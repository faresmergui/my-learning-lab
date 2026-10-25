---
title: Monitoring, observabilité et signaux clés
chapter: 1
order: 1
duration: 11
tags:
- Observabilité
- Monitoring
- SRE
cards:
- q: Différence entre monitoring et observabilité ?
  a: Le **monitoring** surveille des choses connues à l'avance (le disque, le CPU, le service répond-il ?) et alerte quand un seuil est franchi. L'**observabilité** est la capacité à **comprendre un comportement imprévu** à partir des données produites par le système (métriques, logs, traces riches), sans avoir à ajouter de code. Le premier dit *que* ça va mal, la seconde aide à comprendre *pourquoi*.
- q: Quels sont les signaux de l'observabilité ?
  a: Les **métriques** (des nombres agrégés dans le temps), les **logs** (des événements détaillés), les **traces** (le parcours d'une requête entre services) et, de plus en plus, les **profils** (où le code passe son temps CPU ou mémoire). Les événements (déploiements, changements) complètent le tableau.
- q: Que sont les quatre signaux dorés (golden signals) ?
  a: 'Les quatre mesures à suivre pour tout service vu par ses utilisateurs, selon le livre SRE de Google : **latence** (temps de réponse, en séparant succès et erreurs), **trafic** (requêtes par seconde), **erreurs** (taux d''échecs) et **saturation** (à quel point la ressource la plus contrainte est pleine).'
- q: Que sont les méthodes RED et USE ?
  a: '**RED** pour les services : *Rate* (débit), *Errors* (erreurs), *Duration* (durée). **USE** pour les ressources (CPU, disque, réseau, mémoire) : *Utilization* (taux d''occupation), *Saturation* (file d''attente, travail en attente), *Errors* (erreurs matérielles ou système).'
- q: Supervision boîte noire ou boîte blanche ?
  a: '**Boîte noire** : on teste le service de l''extérieur, comme un utilisateur (sonde HTTP, ping, test de bout en bout). **Boîte blanche** : on lit ce que le système expose de l''intérieur (métriques applicatives, logs, traces). Il faut les deux : la boîte noire dit si l''utilisateur souffre, la boîte blanche dit pourquoi.'
- q: Qu'est-ce que la cardinalité ?
  a: 'Le nombre de **combinaisons différentes** de valeurs d''étiquettes pour une métrique (ou d''index pour des logs). Une étiquette `user_id` ou `request_id` crée des millions de séries : la mémoire, le stockage et le coût explosent. C''est le premier piège de toutes les stacks d''observabilité.'
quiz:
- q: Le CPU des serveurs est à 30 %, mais les utilisateurs se plaignent de lenteurs. Qu'est-ce que ce cas montre ?
  options:
  - Que le monitoring est inutile
  - Qu'il faut mesurer ce que vit l'utilisateur (latence, erreurs côté service, sonde boîte noire) et pas seulement les ressources
  - Qu'il faut un seuil CPU à 20 %
  - Que les utilisateurs se trompent
  answer: 1
  explain: 'Les signaux de ressources (USE) ne suffisent pas : la latence et les erreurs (RED, golden signals) sont ce que voit l''utilisateur.'
- q: Un développeur ajoute l'étiquette `session_id` à une métrique de requêtes. Quel est le risque ?
  options:
  - Aucun
  - 'Une explosion de cardinalité : une série par session, qui sature la mémoire et le stockage de Prometheus (ou fait exploser la facture d''un SaaS)'
  - Des métriques plus précises sans coût
  - Une perte de données
  answer: 1
  explain: Les identifiants uniques vont dans les logs ou les traces, pas dans les étiquettes de métriques.
level: intermédiaire
---

Avant de choisir entre Prometheus, Elastic, Centreon ou Datadog, il faut savoir **ce qu'on veut voir** et **pourquoi**. Cette fiche pose le vocabulaire et les méthodes communs à tous les outils du module : la différence entre surveiller et comprendre, les types de signaux, et les quelques mesures qui comptent vraiment pour un service. La fiche « Observabilité » du module DevOps en donnait un aperçu ; ce module va beaucoup plus loin.

> **Les outils cités dans cette fiche.**
> - **monitoring** (supervision) : surveiller des indicateurs connus et alerter sur des seuils.
> - **observabilité** : la capacité à comprendre l'état interne d'un système à partir de ce qu'il produit.
> - **SRE** (Site Reliability Engineering) : l'approche de Google qui applique l'ingénierie à l'exploitation (SLO, budget d'erreur).
> - **SLO** (Service Level Objective) : un objectif de fiabilité mesurable, par exemple 99,9 % de requêtes réussies sur 30 jours.
> - **sonde** (probe) : un test automatique qui interroge le service de l'extérieur.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **latence** | le temps que met le service à répondre à une requête, mesuré en millisecondes |
| **débit** (ou trafic) | le nombre de requêtes traitées par seconde |
| **percentile** (p50, p95, p99) | p99 = 300 ms veut dire que 99 % des requêtes ont répondu en moins de 300 ms ; le 1 % restant est plus lent. p50 est la médiane |
| **5xx** | les codes de réponse HTTP d'erreur côté serveur (500 erreur interne, 502 mauvaise passerelle, 503 indisponible, 504 délai dépassé) |
| **timeout** | une requête abandonnée parce que la réponse n'est pas arrivée dans le délai fixé |
| **seuil** | une valeur limite (« disque à plus de 90 % ») au-delà de laquelle on considère qu'il y a un problème |
| **alerte** | une notification automatique envoyée quand une condition est remplie (seuil dépassé, service injoignable) |
| **tableau de bord** (dashboard) | une page de graphiques qui montre l'état d'un système en un coup d'œil |
| **agréger** | résumer beaucoup de mesures en une seule (somme, moyenne, maximum) sur une période ou un groupe de machines |
| **échantillonner** | ne garder qu'une partie des données (par exemple 1 trace sur 10) pour réduire le coût |
| **étiquette** (label, tag) | une information attachée à une mesure, comme `service="api"` ou `env="prod"`, qui permet de filtrer et regrouper |
| **instrumenter** | ajouter dans le code ou autour de lui ce qu'il faut pour qu'il produise des métriques, des logs et des traces |

## Comment ça marche : le trajet d'une donnée

Quel que soit l'outil, une donnée d'observabilité suit toujours le même chemin, en cinq étapes :

1. **Produire** : l'application, le système ou l'équipement génère la donnée. Un serveur web compte ses requêtes, écrit une ligne de log à chaque erreur, chronomètre chaque appel.
2. **Collecter** : un **agent** (petit programme installé sur la machine) ou un serveur central vient chercher ou reçoit ces données. Exemples : Prometheus qui interroge les services toutes les 30 secondes, Fluent Bit qui lit les fichiers de logs, l'agent Datadog qui envoie tout à son service en ligne.
3. **Stocker** : les données sont rangées dans une base adaptée (base de séries temporelles pour les métriques, moteur de recherche pour les logs, stockage de traces), avec une durée de conservation.
4. **Exploiter** : on les interroge pour dessiner des tableaux de bord et explorer un problème.
5. **Alerter** : des règles évaluées en continu déclenchent des notifications vers les bonnes personnes.

Chaque outil du module se place sur une ou plusieurs de ces étapes. Centreon et Datadog en couvrent presque toutes ; Prometheus collecte, stocke et évalue les alertes ; Grafana ne fait qu'exploiter.

## Comprendre : savoir que ça va mal, puis pourquoi

```
         « est-ce que ça va ? »                    « pourquoi ça ne va pas ? »
MONITORING ─────────────────────────────  OBSERVABILITÉ ───────────────────────────────
seuils connus, tableaux de bord, alertes   explorer des données riches, poser des questions
disque > 90 %, service down, CPU élevé      « quelles requêtes sont lentes, depuis quand,
                                              pour quels clients, sur quelle version ? »
```

Un système simple et stable se supervise bien avec du monitoring classique (Centreon, Nagios, Zabbix). Un système distribué (microservices, Kubernetes, cloud) a des pannes **imprévues** : il faut pouvoir creuser, et donc de l'observabilité.

## Les signaux

| Signal | Ce que c'est | Bon pour | Outils typiques |
| --- | --- | --- | --- |
| métriques | nombres dans le temps, agrégés | tendances, alertes, tableaux de bord | Prometheus, Datadog, Centreon |
| logs | événements texte ou JSON détaillés | le détail d'un problème, l'audit | Loki, Elasticsearch, Datadog Logs |
| traces | parcours d'une requête, étape par étape | latence dans les microservices | Tempo, Jaeger, Elastic APM, Datadog APM |
| profils | où le code consomme CPU et mémoire | optimisation fine | Pyroscope, Parca |
| événements | déploiements, changements de config | relier un incident à un changement | annotations Grafana, Datadog Events |

Chaque signal a un coût différent : une métrique coûte peu et se garde longtemps, un log coûte cher à indexer, une trace complète est très riche mais souvent **échantillonnée**.

## Les méthodes : quoi mesurer

**Les quatre signaux dorés** (pour un service exposé aux utilisateurs) :

| Signal | Exemple de mesure |
| --- | --- |
| latence | p50, p95, p99 du temps de réponse (succès et erreurs séparés) |
| trafic | requêtes par seconde |
| erreurs | part des réponses 5xx, des timeouts |
| saturation | file d'attente, pool de connexions plein, mémoire proche de la limite |

**RED** pour chaque service (Rate, Errors, Duration) et **USE** pour chaque ressource (Utilization, Saturation, Errors) : deux grilles faciles à retenir pour ne rien oublier.

## Boîte noire et boîte blanche

- **Boîte noire** : une sonde qui appelle `https://api.example.com/health` toutes les 30 secondes depuis l'extérieur (Blackbox exporter, Datadog Synthetics, un contrôle HTTP Centreon). Elle voit ce que voit l'utilisateur, y compris le DNS, le TLS et le load balancer.
- **Boîte blanche** : les métriques, logs et traces produits par l'application et l'infrastructure. Ils expliquent la cause.

## Les pièges communs à tous les outils

- **La cardinalité** : trop de combinaisons d'étiquettes ou de champs indexés font exploser mémoire, stockage et facture.
- **Trop d'alertes** : une alerte doit demander une action ; le reste va dans un tableau de bord.
- **Mesurer ce qui est facile** (CPU) plutôt que ce qui compte (l'expérience utilisateur).
- **Des signaux isolés** : sans lien entre métriques, logs et traces (même service, même identifiant de trace), on perd du temps à passer d'un outil à l'autre.

> **À retenir.** Le monitoring dit que ça va mal, l'observabilité aide à comprendre pourquoi. Les signaux : métriques, logs, traces, profils et événements, chacun avec son coût. Les quatre signaux dorés (latence, trafic, erreurs, saturation), RED pour les services, USE pour les ressources. Combiner boîte noire (sondes) et boîte blanche (ce que le système expose). Surveiller la cardinalité, alerter seulement sur ce qui demande une action, et relier les signaux entre eux.
