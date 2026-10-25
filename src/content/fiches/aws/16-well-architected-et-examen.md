---
title: Well-Architected et architectures types
chapter: 16
order: 1
duration: 11
tags:
- AWS SAA
- Well-Architected
- examen
cards:
- q: Quels sont les six piliers du Well-Architected Framework ?
  a: '**Excellence opérationnelle**, **sécurité**, **fiabilité**, **efficacité des performances**, **optimisation des coûts** et **durabilité**.'
- q: Que signifie « le moins d'effort d'exploitation » dans une question d'examen ?
  a: 'Il faut préférer le service **le plus managé** qui répond au besoin : Fargate plutôt qu''EC2, Aurora plutôt que MySQL sur EC2, DynamoDB plutôt qu''une base à gérer, une fonction intégrée plutôt qu''un script maison.'
- q: Quelle est l'architecture type d'un site statique mondial ?
  a: '**S3** (bucket privé) + **CloudFront** avec une **OAC** + certificat **ACM** (us-east-1) + **Route 53** alias. Ajouter **WAF** si besoin.'
- q: Quelle est l'architecture web classique à trois niveaux, hautement disponible ?
  a: '**Route 53** → **ALB** (sous-réseaux publics, 2 AZ) → **ASG** d''instances ou service ECS (sous-réseaux privés) → **RDS Multi-AZ** ou Aurora (sous-réseaux de données), **ElastiCache** pour les sessions, **NAT Gateway** par AZ.'
- q: À quoi ressemble une architecture serverless typique pour une API ?
  a: '**API Gateway** (HTTP API) → **Lambda** → **DynamoDB**, authentification **Cognito**, fichiers dans **S3** par URL présignée, traitements asynchrones par **SQS** ou **EventBridge**.'
quiz:
- q: « Une entreprise veut exécuter des conteneurs sans gérer de serveurs, avec le moins d'effort d'exploitation. » Réponse attendue ?
  options:
  - EC2 avec Docker
  - ECS sur Fargate
  - EKS avec des nœuds autogérés
  - Lambda dans tous les cas
  answer: 1
  explain: Fargate supprime la gestion des nœuds ; c'est la réponse type à « conteneurs sans serveurs ».
- q: Un énoncé exige « hautement disponible » et « le moins cher ». Une option propose une seule instance avec des snapshots, une autre deux instances dans deux AZ derrière un ALB, une troisième deux régions actives. Laquelle ?
  options:
  - Une instance avec snapshots
  - Deux instances dans deux AZ derrière un ALB
  - Deux régions actives
  - Aucune
  answer: 1
  explain: La première n'est pas hautement disponible, la troisième dépasse le besoin et coûte plus.
level: intermédiaire
---

Les fiches précédentes ont présenté chaque service. Cette dernière les assemble : le cadre **Well-Architected** qui sert de grille de lecture à tout l'examen, les **architectures types** qu'il faut savoir reconnaître, et la façon de lire une question. La page Certifications du site donne le format de l'examen et sa stratégie.

> **Les outils cités dans cette fiche.**
> - **AWS Well-Architected Framework** : les bonnes pratiques d'AWS, rangées en six piliers, avec un outil d'évaluation (Well-Architected Tool) dans la console.
> - **SAA-C03** : la version actuelle de l'examen Solutions Architect Associate.
> - Les autres services cités ont chacun leur fiche dans ce module.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **AZ** : une zone de disponibilité : un ou plusieurs datacenters indépendants dans une région.
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.
> - **CDN** : un réseau de serveurs répartis dans le monde qui servent le contenu au plus près des utilisateurs.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **SQS** : le service de files de messages d'AWS.
> - **SNS** : le service de notifications d'AWS, qui diffuse un message à plusieurs abonnés.

## Les six piliers

| Pilier | Question | Réponses typiques |
| --- | --- | --- |
| excellence opérationnelle | comment exploiter et améliorer ? | IaC, petits changements fréquents, runbooks, observabilité |
| sécurité | comment protéger ? | moindre privilège, rôles, chiffrement partout, traçabilité, défense en profondeur |
| fiabilité | comment résister et se rétablir ? | multi-AZ, Auto Scaling, découplage, sauvegardes testées |
| efficacité des performances | comment utiliser les bonnes ressources ? | services managés, serverless, cache, CDN, bon type d'instance |
| optimisation des coûts | comment payer juste ? | engagements, Spot, dimensionnement, cycle de vie, mesurer |
| durabilité | comment réduire l'impact ? | Graviton, serverless, éteindre l'inutile, régions plus vertes |

## Les architectures à reconnaître

### Le site statique mondial

```
Route 53 (alias) ─► CloudFront (ACM us-east-1, WAF) ─► S3 privé (OAC)
```

### L'application web à trois niveaux

```
Route 53 ─► ALB (public, 2 AZ) ─► ASG ou ECS Fargate (privé, 2 AZ)
                                        │ sessions ─► ElastiCache
                                        └──────────► RDS Multi-AZ / Aurora (sous-réseaux de données)
            sortie Internet ─► NAT Gateway par AZ ; S3 par endpoint gateway
```

### L'API serverless

```
Client ─► API Gateway (Cognito) ─► Lambda ─► DynamoDB
                                     └─► SQS ─► Lambda (traitements lents)
Fichiers : URL présignée ─► S3 ─► notification ─► Lambda
```

### Le traitement par événements

```
S3 / application ─► EventBridge ou SNS ─► plusieurs SQS ─► consommateurs (Lambda, ECS)
                                               └─► DLQ
```

### L'analyse de données

```
Sources ─► Kinesis Data Streams / Firehose ─► S3 (data lake, Glue Data Catalog)
                                                 └─► Athena (SQL à la demande) / Redshift / QuickSight
```

### Le réseau d'entreprise

```
Data center ─ Direct Connect (+ VPN de secours) ─► Transit Gateway ─► VPC des comptes
DNS hybride : Route 53 Resolver (endpoints entrants et sortants)
```

## Lire une question

Les énoncés contiennent presque toujours un **mot-clé décisif** :

| Mot-clé | Ce qu'il oriente |
| --- | --- |
| « le moins d'effort d'exploitation » | le service le plus managé (Fargate, Aurora, DynamoDB, fonction native) |
| « le plus économique » | Spot, Savings Plans, classes froides S3, serverless pour un trafic faible |
| « hautement disponible » | multi-AZ |
| « reprise si une région tombe » | réplication inter-région, Route 53 failover, stratégie DR adaptée au RTO |
| « découpler », « absorber des pics » | SQS (et SNS pour plusieurs abonnés) |
| « latence la plus faible pour des utilisateurs mondiaux » | CloudFront, Global Accelerator, Route 53 latency, Aurora Global |
| « sans exposer à Internet » | sous-réseau privé, VPC endpoint, PrivateLink |
| « chiffrer et contrôler les clés » | SSE-KMS avec clé gérée par le client |
| « temporaire », « accès d'une application » | rôle IAM |
| « ordre », « pas de doublon » | SQS FIFO |

Méthode : lis la **dernière phrase** (ce qu'on te demande), repère les **contraintes** (coût, effort, délai, sécurité), **élimine** les réponses qui en violent une, puis choisis la **plus simple** parmi les restantes. Une réponse qui « marche » mais ajoute un serveur à gérer perd souvent face à un service managé.

## Les confusions fréquentes

- Multi-AZ (disponibilité) et read replica (lecture).
- Security group (avec état, Allow) et NACL (sans état, Allow et Deny).
- CloudWatch (performances), CloudTrail (qui a fait quoi), Config (configuration et conformité).
- CloudFront (cache) et Global Accelerator (IP fixes, sans cache).
- EBS (une AZ, une instance), EFS (partagé Linux), FSx (Windows, Lustre, NetApp), S3 (objets).
- SQS (file), SNS (diffusion), EventBridge (routage d'événements), Kinesis (flux relisible).
- Secrets Manager (rotation) et Parameter Store (configuration).
- SCP (plafond d'un compte) et politique IAM (droits d'une identité).

> **À retenir.** Six piliers : opérations, sécurité, fiabilité, performance, coûts, durabilité. Savoir reconnaître le site statique, l'appli trois niveaux, l'API serverless, le traitement par événements et le réseau hybride. Dans chaque question, trouver le mot-clé décisif, éliminer ce qui viole une contrainte, choisir le plus simple et le plus managé.
