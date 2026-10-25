---
title: Synthèse AWS
description: "Régions, IAM, VPC, calcul, stockage, bases, découplage, sécurité, reprise et coûts : les choix à connaître pour concevoir sur AWS."
---

## Les fondations

- Une **région** contient plusieurs **AZ** isolées ; la production tient sur **au moins deux AZ**.
- Globaux : IAM, Route 53, CloudFront, Organizations. Par AZ : sous-réseau, instance, volume EBS.
- Responsabilité partagée : AWS sécurise **le** cloud, toi ce qui est **dans** le cloud.
- `aws sts get-caller-identity` : qui suis-je ? Toujours vérifier la région.

## IAM

| Règle | |
| --- | --- |
| défaut | tout est refusé |
| Allow | ouvre |
| Deny explicite | gagne toujours (identité, ressource, SCP, limite) |

- **Rôles** partout (instances, Lambda, pods, CI par OIDC, humains par IAM Identity Center) ; pas de clés stockées.
- **SCP** : plafond d'un compte, root compris, n'accorde rien. **Permissions boundary** : plafond d'une identité.
- Accès entre comptes : politique de ressource ou rôle endossé (`sts:AssumeRole`).

## VPC

```
public  : route 0.0.0.0/0 → Internet Gateway   (ALB, NAT)
privé   : route 0.0.0.0/0 → NAT Gateway de l'AZ (applis)
données : pas de route Internet                 (RDS)
```

| | Security group | NACL |
| --- | --- | --- |
| niveau | interface | sous-réseau |
| règles | Allow | Allow + Deny numérotées |
| état | avec état | sans état (ports éphémères) |

- Endpoint **gateway** gratuit : S3, DynamoDB. Endpoint **interface** (PrivateLink) : les autres.
- Peering (sans transitivité) ; **Transit Gateway** pour beaucoup de VPC ; **VPN** rapide, **Direct Connect** stable.
- 5 adresses réservées par sous-réseau ; VPC Flow Logs pour comprendre un refus.

## Calcul

- Type `m7g.large` : famille, génération, attribut (g = Graviton), taille. `t` burstable, `m` général, `c` calcul, `r` mémoire.
- AMI pour les logiciels, user data pour la configuration ; **IMDSv2** obligatoire.
- Instance store : rapide, effacé à l'arrêt. Placement **cluster** (latence), **spread** (séparer), **partition** (Kafka).
- **ALB** couche 7 (chemin, hôte) ; **NLB** couche 4, IP fixe ; **GWLB** appliances.
- **ASG** : min, desired, max ; health check **ELB** ; target tracking par défaut, planifié pour les pics connus.
- ECS (simple) ou EKS (Kubernetes) ; **Fargate** sans nœuds ; **Lambda** 15 min, 10 Go, provisioned concurrency contre le démarrage à froid.

## Stockage

| Besoin | Service |
| --- | --- |
| objets, sauvegardes, data lake | **S3** |
| disque d'une instance (une AZ) | **EBS** gp3, io2 si critique |
| fichiers partagés Linux, multi-AZ | **EFS** |
| Windows, Lustre, NetApp | **FSx** |

- S3 : Standard, Intelligent-Tiering, IA, Glacier Instant / Flexible / Deep Archive ; **cycle de vie**.
- Protection : versioning, **Object Lock** (compliance), réplication CRR/SRR, Block Public Access, SSE-KMS.
- EBS : snapshot pour changer d'AZ ou de région. **AWS Backup** + Vault Lock pour centraliser.

## Bases de données

| | Multi-AZ | Read replica |
| --- | --- | --- |
| but | disponibilité | lecture, reprise régionale |
| réplication | synchrone | asynchrone |
| bascule | automatique | promotion manuelle |

- **Aurora** : 6 copies sur 3 AZ, 15 réplicas, Serverless v2, **Global Database** (RPO ~1 s).
- **DynamoDB** : clé de partition variée, on-demand ou provisioned, GSI, TTL, Streams, Global Tables, **DAX**.
- **ElastiCache** Redis/Valkey (sessions, classements) ; **RDS Proxy** pour Lambda.
- Redshift (entrepôt), DocumentDB (MongoDB), Neptune (graphe), Timestream (séries temporelles).

## Découpler

| Besoin | Service |
| --- | --- |
| file, absorber un pic | **SQS** (visibility timeout > traitement, DLQ, idempotence) |
| ordre et pas de doublon | **SQS FIFO** (MessageGroupId) |
| un événement, plusieurs abonnés | **SNS** + SQS (fan-out) |
| routage par contenu, événements AWS | **EventBridge** |
| flux temps réel relisible | **Kinesis Data Streams** |
| livrer un flux dans S3 | **Data Firehose** |

## DNS et diffusion

- Route 53 **alias** (apex, ressources AWS) ; politiques weighted, latency, failover, geolocation (+ défaut), multivalue.
- **CloudFront** : cache mondial, **OAC** vers S3 privé, ACM en **us-east-1**, WAF, URL signées.
- **Global Accelerator** : 2 IP anycast fixes, TCP/UDP, bascule en secondes, sans cache.

## Sécurité

- **KMS** : chiffrement d'enveloppe, politique de clé, rotation, tracé dans CloudTrail.
- **Secrets Manager** (rotation) ; **Parameter Store** (configuration).
- **WAF** (HTTP, rate-based) ; **Shield** Standard gratuit, Advanced pour le critique.
- **GuardDuty** menaces, **Inspector** failles, **Macie** données sensibles, **Security Hub** centralise.
- **Cognito** : user pools (connexion, JWT), identity pools (identifiants AWS).

## Observabilité et gouvernance

| Question | Service |
| --- | --- |
| ça marche, c'est lent ? | CloudWatch (agent pour mémoire et disque) |
| qui a fait quoi ? | CloudTrail (trail d'organisation) |
| configuration, conformité ? | Config (règles, remédiation) |
| agir sur les instances ? | Systems Manager (Session Manager, Patch Manager) |

## Reprise après sinistre

| Stratégie | RPO | RTO | Coût |
| --- | --- | --- | --- |
| backup and restore | heures | heures | faible |
| pilot light | minutes | dizaines de min | moyen |
| warm standby | secondes | minutes | élevé |
| multi-site | ~0 | ~0 | le plus élevé |

La réplication copie aussi les erreurs : des sauvegardes isolées (autre compte, Vault Lock) restent indispensables. Tester avec FIS.

## Coûts

- Base stable : **Savings Plans** (Compute si l'usage change) ; interruptible : **Spot** ; Graviton et gp3.
- Réseau facturé : entre AZ, entre régions, vers Internet, **NAT au Go** → endpoints gateway, CloudFront.
- S3 cycle de vie, rétention des logs, volumes non attachés supprimés.
- Tags de coûts, **Budgets** (alertes, actions), Cost Explorer, Cost Anomaly Detection, Compute Optimizer.
