---
title: Alertes utiles, SLO et astreinte
chapter: 14
order: 1
duration: 12
tags:
- Observabilité
- Alerting
- SLO
- SRE
cards:
- q: Qu'est-ce qu'une bonne alerte ?
  a: 'Une alerte qui est **urgente**, **réelle** et **actionnable** : quelqu''un doit agir maintenant, l''impact sur les utilisateurs est avéré ou imminent, et le message dit quoi faire (lien vers le runbook, tableau de bord, contexte). Tout le reste va dans un ticket ou un tableau de bord.'
- q: Pourquoi alerter sur les symptômes plutôt que sur les causes ?
  a: Parce que l'utilisateur subit les **symptômes** (erreurs, lenteur, indisponibilité), alors qu'une cause (CPU à 90 %, un pod redémarré) n'a souvent aucun impact. Alerter sur les symptômes réduit le bruit et ne rate pas les causes imprévues ; les causes servent au diagnostic, sur les tableaux de bord.
- q: Qu'est-ce qu'une alerte sur le taux de consommation du budget d'erreur (burn rate) ?
  a: 'Avec un SLO de 99,9 % sur 30 jours, le **budget d''erreur** est 0,1 % des requêtes. Le **burn rate** mesure la vitesse à laquelle on le consomme : à un burn rate de 14,4 sur une heure, on aurait épuisé 2 % du budget mensuel en une heure. On alerte (appel) sur un burn rate élevé sur des fenêtres courtes, et (ticket) sur un burn rate modéré sur des fenêtres longues.'
- q: Que contient un bon runbook ?
  a: Ce que mesure l'alerte et pourquoi elle compte, l'**impact** utilisateur, les **vérifications** à faire (commandes, tableaux de bord), les **actions** de remédiation connues (rollback, scaler, basculer), quand et à qui **escalader**, et les liens utiles. Il est court, à jour, et testé en conditions réelles.
- q: Qu'est-ce que la fatigue d'alerte et comment la réduire ?
  a: Quand les alertes sont trop nombreuses ou trop souvent fausses, l'équipe ne les lit plus, et rate la vraie. On la réduit en **supprimant** les alertes jamais suivies d'action, en alertant sur les symptômes, en **regroupant** et **inhibant**, en réglant `for` et les seuils, et en faisant une **revue régulière** des alertes.
- q: Différence entre une alerte qui appelle (page) et une alerte ticket ?
  a: 'Une **page** réveille quelqu''un : réservée à un impact utilisateur urgent. Un **ticket** (ou un message dans un canal) se traite pendant les heures de travail : disque plein dans trois jours, certificat qui expire dans 20 jours, budget d''erreur consommé lentement.'
quiz:
- q: L'alerte « CPU > 80 % » sonne 30 fois par semaine la nuit, sans jamais d'impact visible. Que fais-tu ?
  options:
  - Monter le seuil à 95 %
  - La supprimer comme alerte qui appelle, garder le CPU sur un tableau de bord, et alerter plutôt sur la latence et les erreurs du service (ou sur le SLO)
  - Ajouter une deuxième alerte
  - Couper toutes les alertes la nuit
  answer: 1
  explain: 'Une alerte sans action est du bruit : on alerte sur ce que vit l''utilisateur.'
- q: Avec un SLO de 99,9 %, quelle règle d'alerte est la plus pertinente pour réveiller quelqu'un ?
  options:
  - Une erreur 500 isolée
  - Un burn rate supérieur à 14,4 à la fois sur 1 heure et sur 5 minutes
  - Un taux d'erreurs de 0,05 % sur 30 jours
  - Le CPU à 90 %
  answer: 1
  explain: La double fenêtre (longue pour la significativité, courte pour vérifier que c'est encore en cours) est la recette classique du livre SRE de Google.
level: intermédiaire
---

Collecter des données et dessiner des tableaux de bord ne sert à rien si les **alertes** sont mal pensées : trop nombreuses, on les ignore ; trop rares, on découvre les pannes par les utilisateurs. Cette fiche rassemble ce qui marche, quel que soit l'outil (Alertmanager, Grafana, Centreon, Datadog, Kibana) : alerter sur les symptômes, s'appuyer sur des SLO, écrire des runbooks, et organiser l'astreinte.

> **Les outils cités dans cette fiche.**
> - **SLI** (Service Level Indicator) : la mesure de fiabilité (part de requêtes réussies, part de requêtes en moins de 300 ms).
> - **SLO** (Service Level Objective) : l'objectif sur cette mesure (99,9 % sur 30 jours) ; **budget d'erreur** : ce qu'on s'autorise à rater (0,1 %).
> - **burn rate** : la vitesse de consommation du budget d'erreur.
> - **runbook** : la fiche de procédure liée à une alerte.
> - **PagerDuty**, **Opsgenie**, **Grafana OnCall/IRM**, **Squadcast** : des outils d'astreinte (plannings, appels, escalades).
> - **Sloth** et **Pyrra** : des outils qui génèrent les règles Prometheus des SLO.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **astreinte** (on-call) | la permanence pendant laquelle une personne doit répondre aux alertes, y compris la nuit |
| **page** | une alerte qui appelle ou fait sonner le téléphone de l'astreinte |
| **SLI** | l'indicateur mesuré, toujours sous forme de proportion : « requêtes réussies / requêtes totales » |
| **SLO** | l'objectif sur cet indicateur, sur une période : « 99,9 % sur 30 jours glissants » |
| **budget d'erreur** | ce que le SLO autorise à rater : 0,1 % des requêtes, soit environ 43 minutes d'indisponibilité totale par mois |
| **burn rate** | la vitesse à laquelle on consomme ce budget, par rapport à la vitesse « normale » qui l'épuiserait pile en 30 jours |
| **fenêtre** | la période sur laquelle on calcule un taux (5 minutes, 1 heure, 6 heures) |
| **acquitter** | dire à l'outil « je prends en charge », ce qui arrête les rappels et l'escalade |
| **escalade** | si personne n'acquitte dans le délai, l'alerte passe à la personne suivante (le remplaçant, puis le responsable) |
| **postmortem** | le compte rendu après incident : chronologie, causes, ce qui a bien ou mal marché, actions |

## Comment ça marche : calculer un burn rate

Prenons un SLO de **99,9 %** sur 30 jours : le budget d'erreur est de **0,1 %** des requêtes.

1. Sur la dernière heure, on mesure **1,44 %** d'erreurs.
2. Burn rate = taux d'erreurs observé / budget = 1,44 / 0,1 = **14,4**. On consomme le budget 14,4 fois plus vite que prévu.
3. À ce rythme, une heure consomme 14,4 × (1 h / 720 h) = **2 %** du budget du mois, et le budget entier serait épuisé en à peu près **2 jours**.
4. La règle vérifie aussi la fenêtre de **5 minutes** : si le taux y est également élevé, le problème est toujours en cours, on appelle l'astreinte. S'il est retombé, l'incident est fini et on évite une page inutile.

Ce calcul a deux avantages sur un simple seuil : il tient compte de l'importance réelle (un SLO à 99 % tolère dix fois plus d'erreurs qu'un SLO à 99,9 %), et il réagit vite aux pannes franches tout en détectant aussi les dégradations lentes avec des fenêtres plus longues.

## Comprendre : de la mesure à l'action

```
données ──► tableau de bord  (regarder quand on veut)
       └──► alerte ticket    (à traiter dans les heures ou jours)
       └──► alerte page      (quelqu'un agit maintenant)
                 │
          message : quoi, impact, depuis quand, lien runbook, lien tableau de bord
                 │
          outil d'astreinte : planning, appel, escalade si pas d'acquittement
```

Trois questions avant de créer une alerte : **faut-il agir maintenant ?** **les utilisateurs sont-ils touchés ?** **la personne réveillée saura-t-elle quoi faire ?** Si l'une des réponses est non, ce n'est pas une page.

## Symptômes d'abord

| Alerter (page) sur | Plutôt que sur |
| --- | --- |
| taux d'erreurs du service, latence p99, sonde externe en échec | CPU, mémoire, un pod redémarré |
| budget d'erreur consommé trop vite | chaque erreur 500 isolée |
| file d'attente qui ne se vide plus (travail bloqué) | taille de la file à un instant |

Exceptions utiles en ticket : **disque plein prévu** (`predict_linear`), **certificat qui expire**, **sauvegarde ratée**, **capacité** bientôt atteinte : pas d'impact maintenant, mais il faut agir avant.

## Les SLO et le burn rate

```
SLO : 99,9 % des requêtes réussies sur 30 jours → budget d'erreur = 0,1 %
burn rate 1    = on consomme exactement le budget en 30 jours
burn rate 14,4 = on consomme 2 % du budget en 1 heure (épuisé en ~2 jours)
burn rate 6    = 5 % du budget en 6 heures
```

| Fenêtre longue | Fenêtre courte | Burn rate | Action |
| --- | --- | --- | --- |
| 1 h | 5 min | 14,4 | page |
| 6 h | 30 min | 6 | page |
| 3 jours | 6 h | 1 | ticket |

```yaml
- alert: SLODisponibiliteCommandes
  expr: |
    (1 - sum(rate(http_requests_total{service="commandes",code!~"5.."}[1h]))
         / sum(rate(http_requests_total{service="commandes"}[1h]))) > (14.4 * 0.001)
    and
    (1 - sum(rate(http_requests_total{service="commandes",code!~"5.."}[5m]))
         / sum(rate(http_requests_total{service="commandes"}[5m]))) > (14.4 * 0.001)
  labels: { severity: page }
  annotations: { runbook_url: https://wiki.example.com/runbooks/slo-commandes }
```

Des outils comme **Sloth** ou **Pyrra** (Prometheus), et les SLO intégrés de Datadog, Grafana ou Kibana, génèrent ces règles à partir d'une simple définition du SLO.

## Le message et le runbook

```text
[PAGE] commandes : 3,2 % d'erreurs 5xx depuis 14:02 (SLO 99,9 %, budget consommé 9 %)
Impact : paiements refusés pour environ 1 client sur 30
Tableau de bord : https://grafana…/commandes  ·  Runbook : https://wiki…/slo-commandes
Changements récents : déploiement commandes v2.14 à 13:55
```

Un **runbook** utile : ce que mesure l'alerte, l'impact, les vérifications, les remédiations connues (rollback en premier si un déploiement est en cause), l'escalade. Les alertes sans runbook ne devraient pas passer la revue.

## Organiser l'astreinte

- Un **planning** clair avec un remplaçant, une **escalade** automatique si personne n'acquitte.
- Un **canal** d'incident, un responsable de l'incident désigné quand c'est sérieux.
- Une **revue hebdomadaire** des alertes : combien, lesquelles réveillent, lesquelles ne mènent à rien.
- Un **postmortem** sans recherche de coupable après chaque incident significatif, avec des actions suivies.
- Mesurer la charge : nombre de pages par semaine et par nuit ; au-delà de quelques-unes, il faut réduire.

> **À retenir.** Une page doit être urgente, réelle et actionnable ; le reste va en ticket ou sur un tableau de bord. Alerter sur les symptômes (erreurs, latence, sondes, SLO) plutôt que sur les causes. Les SLO donnent un budget d'erreur, et les alertes de burn rate sur deux fenêtres (14,4 sur 1 h et 5 min) détectent ce qui compte. Chaque alerte a un message clair et un runbook. L'astreinte s'organise avec planning, escalade, revue régulière des alertes et postmortems.
