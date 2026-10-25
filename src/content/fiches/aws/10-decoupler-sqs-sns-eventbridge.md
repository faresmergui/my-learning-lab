---
title: 'Découpler : SQS, SNS, EventBridge, Kinesis'
chapter: 10
order: 1
duration: 12
tags:
- AWS SAA
- SQS
- SNS
- EventBridge
cards:
- q: Différence entre une file SQS standard et FIFO ?
  a: '**Standard** : débit quasi illimité, livraison **au moins une fois**, ordre non garanti. **FIFO** : ordre garanti par groupe de messages, **exactement une fois** (déduplication), débit limité (300 messages/s, 3 000 par lots, davantage en mode haut débit).'
- q: Qu'est-ce que le délai de visibilité (visibility timeout) ?
  a: Quand un consommateur reçoit un message, celui-ci devient **invisible** pour les autres pendant ce délai (30 s par défaut). S'il n'est pas supprimé avant la fin, il réapparaît et sera traité de nouveau. Il doit être plus long que le temps de traitement.
- q: À quoi sert une dead-letter queue ?
  a: À mettre de côté les messages qui ont échoué **N fois** (`maxReceiveCount`) au lieu de les retraiter sans fin. On les analyse, puis on les renvoie dans la file principale (redrive) une fois le bug corrigé.
- q: Qu'est-ce que le schéma fan-out SNS + SQS ?
  a: Un message publié sur un **topic SNS** est copié dans **plusieurs files SQS** abonnées. Chaque service consommateur a sa file, traite à son rythme et ne perd rien s'il est arrêté.
- q: Qu'apporte EventBridge par rapport à SNS ?
  a: Un **bus d'événements** avec des **règles de filtrage** sur le contenu, plus de 20 types de cibles, les événements des services AWS et de SaaS tiers, l'archivage et le rejeu, un registre de schémas et un **Scheduler** (tâches planifiées).
- q: Différence entre Kinesis Data Streams et Data Firehose ?
  a: '**Data Streams** : un flux temps réel où tes consommateurs lisent et relisent les données (rétention 24 h à 365 jours), à dimensionner (shards) ou en on-demand. **Firehose** : un tuyau entièrement managé qui livre les données, éventuellement transformées, vers S3, Redshift, OpenSearch ou un service tiers, avec un léger tampon.'
quiz:
- q: Une commande doit déclencher en parallèle la facturation, l'envoi d'un email et la mise à jour du stock, chacun à son rythme. Architecture ?
  options:
  - Trois appels HTTP synchrones
  - Un topic SNS avec trois files SQS abonnées
  - Une seule file SQS FIFO lue par les trois services
  - Kinesis Firehose
  answer: 1
  explain: 'Fan-out : chaque service a sa file et peut être lent ou en panne sans bloquer les autres.'
- q: Les messages d'une file sont traités deux fois. Les consommateurs mettent 60 s par message. Cause probable ?
  options:
  - La file est FIFO
  - Le délai de visibilité (30 s) est plus court que le traitement
  - Il manque une DLQ
  - Le long polling est activé
  answer: 1
  explain: Le message redevient visible pendant le traitement et un autre consommateur le prend. On augmente le délai (ou on le prolonge pendant le traitement).
- q: Les opérations bancaires d'un même compte doivent être traitées dans l'ordre, sans doublon. Quel service ?
  options:
  - SQS standard
  - SQS FIFO avec l'ID du compte comme MessageGroupId
  - SNS standard
  - Kinesis Firehose
  answer: 1
  explain: L'ordre est garanti par groupe ; des comptes différents sont traités en parallèle.
level: intermédiaire
---

Quand un service appelle directement un autre, une lenteur ou une panne se propage : c'est le **couplage fort**. Mettre une file ou un bus d'événements entre les deux permet à chacun d'avancer à son rythme, d'absorber les pics et de ne rien perdre. L'examen y revient sans cesse, avec des questions du type « comment rendre cette architecture plus résiliente ? ».

> **Les outils cités dans cette fiche.**
> - **SQS** (Simple Queue Service) : une file de messages ; un producteur dépose, un consommateur retire.
> - **SNS** (Simple Notification Service) : un service de publication-abonnement ; un message publié sur un **topic** est envoyé à tous les abonnés (files SQS, Lambda, HTTP, email, SMS).
> - **EventBridge** : un bus d'événements avec des règles de routage sur le contenu.
> - **Kinesis Data Streams** : un flux de données temps réel, lu par plusieurs consommateurs. **Data Firehose** : livre un flux vers un stockage.
> - **Amazon MQ** : des courtiers ActiveMQ ou RabbitMQ managés, pour les applications qui parlent déjà ces protocoles.
> - **DLQ** (dead-letter queue) : une file qui reçoit les messages qui n'ont pas pu être traités.
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **latence** : le délai entre une demande et sa réponse.

## Comprendre : file, publication-abonnement, flux

| Modèle | Un message va à | Exemple |
| --- | --- | --- |
| **file** (SQS) | **un** consommateur parmi plusieurs | répartir des tâches de traitement d'images |
| **publication-abonnement** (SNS, EventBridge) | **tous** les abonnés | « commande créée » vers facturation, stock, email |
| **flux** (Kinesis) | tous les lecteurs, qui peuvent **relire** | clics, télémétrie, logs en temps réel |

## SQS

```
Producteurs ──► [ file SQS ] ──► Consommateurs (ASG, Lambda, ECS)
                    │ après 5 échecs
                    ▼
                 [ DLQ ]
```

| Réglage | Rôle |
| --- | --- |
| **visibility timeout** | durée d'invisibilité après réception ; plus long que le traitement |
| **long polling** (`WaitTimeSeconds` jusqu'à 20) | attendre un message au lieu de réponses vides : moins de requêtes, moins cher |
| **rétention** | de 1 minute à 14 jours (4 jours par défaut) |
| **delay queue** | retarder la visibilité des nouveaux messages (jusqu'à 15 min) |
| taille | 1 Mo par message (256 Ko avant août 2025) ; au-delà, l'objet va dans S3 et le message porte la référence |
| **DLQ** | après `maxReceiveCount` échecs |

Le consommateur doit **supprimer** le message après traitement, sinon il réapparaît. Avec une file standard, un message peut arriver deux fois : le traitement doit être **idempotent** (le refaire ne change rien).

Le nombre de messages en attente (`ApproximateNumberOfMessagesVisible`) est une excellente métrique pour **scaler** les consommateurs.

## SNS

- un topic, des abonnés : SQS, Lambda, HTTP(S), email, SMS, notifications mobiles, Firehose ;
- **filtres d'abonnement** : chaque abonné ne reçoit que les messages qui l'intéressent (par attribut ou contenu) ;
- topics **FIFO** (avec des files SQS FIFO) quand l'ordre compte.

Le schéma **fan-out** (SNS vers plusieurs SQS) est la réponse classique pour « un événement, plusieurs traitements indépendants et fiables ».

## EventBridge

```json
{
  "source": ["shop.commandes"],
  "detail-type": ["CommandeCreee"],
  "detail": { "montant": [{ "numeric": [">", 1000] }] }
}
```

Une **règle** comme celle-ci envoie à une cible (Lambda, Step Functions, SQS, un autre compte…) seulement les commandes de plus de 1 000 €. EventBridge reçoit aussi les événements des **services AWS** (une instance arrêtée, un objet S3 créé, un échec de build) et de SaaS (Zendesk, Datadog). Il sait **archiver et rejouer** des événements, et **EventBridge Scheduler** remplace les tâches cron.

**EventBridge Pipes** relie une source (SQS, DynamoDB Streams, Kinesis) à une cible avec filtrage et enrichissement, sans code de liaison.

## Kinesis

| | Data Streams | Data Firehose |
| --- | --- | --- |
| rôle | flux temps réel à consommer | livraison vers un stockage |
| consommateurs | tes applis (Lambda, KCL, Flink) | aucun à écrire |
| relire | oui, pendant la rétention | non |
| latence | ~70-200 ms | quelques secondes (tampon) |
| capacité | shards ou on-demand | automatique |

L'ordre est garanti **par clé de partition** dans un shard.

## Choisir

```
Répartir du travail, absorber un pic ................. SQS
Ordre strict et pas de doublon ........................ SQS FIFO
Un événement, plusieurs abonnés ....................... SNS (+ SQS = fan-out)
Routage par contenu, événements AWS ou SaaS ........... EventBridge
Données en continu, temps réel, relecture ............. Kinesis Data Streams
Charger un flux dans S3 ou Redshift ................... Data Firehose
Appli existante en JMS, AMQP, MQTT .................... Amazon MQ
```

> **À retenir.** Découpler = mettre une file ou un bus entre les services. SQS : un consommateur par message, visibility timeout plus long que le traitement, DLQ, consommateurs idempotents ; FIFO pour l'ordre. SNS + SQS pour le fan-out, EventBridge pour router par contenu et capter les événements AWS, Kinesis pour les flux temps réel.
