---
title: CloudWatch, CloudTrail, Config et Systems Manager
chapter: 13
order: 1
duration: 12
tags:
- AWS SAA
- CloudWatch
- CloudTrail
cards:
- q: Différence entre CloudWatch et CloudTrail ?
  a: '**CloudWatch** surveille les **performances et l''état** : métriques, logs, alarmes, tableaux de bord. **CloudTrail** enregistre **qui a fait quoi** : chaque appel à l''API AWS (identité, action, IP, heure, résultat).'
- q: Pourquoi la mémoire d'une instance n'apparaît-elle pas dans CloudWatch par défaut ?
  a: 'AWS ne voit que ce que voit l''hyperviseur (CPU, réseau, disque). La **mémoire** et l''**espace disque** sont internes au système : il faut l''**agent CloudWatch** sur l''instance pour les envoyer, avec les logs.'
- q: Que fait AWS Config ?
  a: Il enregistre la **configuration** de chaque ressource et son **historique**, et vérifie des **règles** (« les volumes EBS sont chiffrés », « aucun security group n'ouvre le port 22 à tous »). Une non-conformité peut déclencher une **remédiation automatique**.
- q: Comment se connecter à une instance sans ouvrir le port 22 ni gérer de clés SSH ?
  a: '**Session Manager** (Systems Manager) : un shell dans le navigateur ou la CLI, autorisé par IAM, tracé et enregistrable, via l''agent SSM. Il faut le rôle d''instance adapté et un accès sortant (ou des endpoints) vers SSM.'
- q: Qu'est-ce qu'un trail d'organisation ?
  a: Un trail CloudTrail créé depuis le compte de gestion qui enregistre l'activité de **tous les comptes** de l'organisation dans un bucket central, que les comptes membres ne peuvent pas désactiver.
- q: Différence entre les événements de gestion et de données dans CloudTrail ?
  a: 'Les **événements de gestion** (créer une instance, modifier une politique) sont enregistrés par défaut. Les **événements de données** (lire un objet S3, appeler une Lambda) sont très nombreux : il faut les activer explicitement, et ils sont payants.'
quiz:
- q: Un security group a été ouvert à tout Internet hier soir. Comment savoir qui l'a fait ?
  options:
  - CloudWatch Metrics
  - CloudTrail (événement AuthorizeSecurityGroupIngress)
  - Trusted Advisor
  - VPC Flow Logs
  answer: 1
  explain: CloudTrail enregistre l'appel d'API avec l'identité. Config montrerait aussi l'historique de la ressource.
- q: Tu veux que tout bucket S3 rendu public soit automatiquement corrigé. Quel service ?
  options:
  - CloudTrail seul
  - Une règle AWS Config avec remédiation automatique (document SSM)
  - CloudWatch Logs
  - Inspector
  answer: 1
  explain: Config détecte la non-conformité et lance l'action corrective.
- q: Tu dois appliquer les correctifs de sécurité sur 300 instances chaque mois, avec un rapport. Quel outil ?
  options:
  - Des user data
  - Systems Manager Patch Manager avec une fenêtre de maintenance
  - CloudFormation
  - Un cron sur chaque instance
  answer: 1
  explain: Patch Manager applique des lignes de base de correctifs par groupe d'instances et rapporte la conformité.
level: intermédiaire
---

Une architecture bien conçue doit aussi être **observable** (on voit ce qui se passe) et **gouvernée** (on sait qui a changé quoi, et on vérifie que les règles sont respectées). AWS sépare ces besoins en plusieurs services aux noms proches, faciles à confondre à l'examen. La fiche DevOps sur l'observabilité donne les principes : métriques, logs, traces.

> **Les outils cités dans cette fiche.**
> - **CloudWatch** : métriques, logs, alarmes, tableaux de bord ; **CloudWatch agent** pour la mémoire, le disque et les logs des instances.
> - **CloudWatch Logs Insights** : un langage de requête pour chercher dans les logs.
> - **X-Ray** : le traçage des requêtes à travers les services (où passe le temps ?).
> - **CloudTrail** : le journal de tous les appels à l'API AWS.
> - **AWS Config** : l'inventaire, l'historique et la conformité de la configuration des ressources.
> - **Systems Manager** (SSM) : la boîte à outils d'exploitation des instances (Session Manager, Patch Manager, Run Command, Parameter Store).
> - **Trusted Advisor** : des recommandations automatiques (coûts, sécurité, limites, performance).
> - **CloudFormation** : l'outil d'infrastructure as code d'AWS, équivalent de Terraform propre à AWS.
> - **EC2** : le service de machines virtuelles d'AWS.
> - **ALB** : Application Load Balancer : le load balancer HTTP d'AWS.
> - **SNS** : le service de notifications d'AWS, qui diffuse un message à plusieurs abonnés.
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **SQL** : le langage de requête des bases de données relationnelles (PostgreSQL, MySQL).
> - **PCI** : le bus qui relie les cartes (réseau, GPU) à la carte mère.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.

## Comprendre : quatre questions, quatre services

| Question | Service |
| --- | --- |
| « Est-ce que ça marche, est-ce que c'est lent ? » | **CloudWatch** (et X-Ray) |
| « Qui a fait cette action ? » | **CloudTrail** |
| « À quoi ressemblait cette ressource avant, est-elle conforme ? » | **AWS Config** |
| « Comment agir sur mes instances ? » | **Systems Manager** |

## CloudWatch

- **Métriques** : chaque service publie les siennes (CPU d'EC2, requêtes d'ALB, erreurs de Lambda). Résolution standard 1 minute (5 minutes pour EC2 sans monitoring détaillé), **haute résolution** 1 seconde pour les métriques personnalisées.
- **Alarmes** : passent en `ALARM` quand une métrique franchit un seuil pendant N périodes ; actions : SNS, Auto Scaling, action EC2 (redémarrer, récupérer), Systems Manager. Les **alarmes composites** combinent plusieurs alarmes pour réduire le bruit.
- **Logs** : groupes de logs, rétention réglable (par défaut **pour toujours** : à changer), **filtres de métrique** (compter les « ERROR »), abonnements vers Lambda, Firehose ou OpenSearch, **Logs Insights** pour chercher.
- **Agent CloudWatch** : mémoire, disque, processus, fichiers de logs des instances.
- **Synthetics** (tests de parcours programmés), **RUM** (expérience réelle des utilisateurs), **Container Insights**, **Application Signals**.

```
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
```

## CloudTrail

- les **événements de gestion** sont gardés 90 jours dans l'historique, sans rien configurer ;
- un **trail** les envoie vers S3 (et CloudWatch Logs) pour les garder longtemps ; un **trail d'organisation** couvre tous les comptes ;
- les **événements de données** (S3, Lambda, DynamoDB) s'activent à part ;
- la **validation d'intégrité** des fichiers prouve qu'ils n'ont pas été modifiés ; le bucket va dans un compte de journaux séparé, avec Object Lock ;
- **CloudTrail Insights** signale les rafales inhabituelles d'appels ; **CloudTrail Lake** permet de les interroger en SQL.

## AWS Config

Config enregistre l'état de chaque ressource à chaque changement. On y ajoute des **règles** gérées (plus de 300) ou personnalisées, regroupées en **conformance packs** (par exemple CIS ou PCI DSS). Une règle non conforme peut lancer une **remédiation** (un document Systems Manager qui retire l'accès public, active le chiffrement…). Un **agrégateur** regroupe la conformité de tous les comptes et régions.

## Systems Manager

| Fonction | Rôle |
| --- | --- |
| **Session Manager** | shell sans SSH ni bastion, autorisé par IAM, tracé |
| **Run Command** | lancer une commande sur des centaines d'instances |
| **Patch Manager** + **Maintenance Windows** | correctifs planifiés et rapport de conformité |
| **State Manager** | maintenir une configuration (agent installé, service actif) |
| **Inventory** | logiciels installés sur chaque instance |
| **Automation** | runbooks (redémarrer, créer une AMI, remédier) |
| **Parameter Store** | configuration et secrets simples |

Les instances doivent avoir l'**agent SSM** (préinstallé sur Amazon Linux et les AMI récentes) et un rôle avec `AmazonSSMManagedInstanceCore`.

## Infrastructure as code et conseils

- **CloudFormation** décrit l'infrastructure en YAML ou JSON (**stacks**, **change sets** pour prévisualiser, **StackSets** pour déployer dans plusieurs comptes et régions, détection de dérive). Le **CDK** génère du CloudFormation depuis du code (TypeScript, Python). Terraform reste une alternative courante.
- **Trusted Advisor** : instances sous-utilisées, ports ouverts, MFA root absent, limites de service proches.
- **AWS Health Dashboard** : les incidents AWS qui touchent **tes** ressources, avec des événements EventBridge.
- **Compute Optimizer** : propose des tailles d'instances, de volumes ou de Lambda selon l'usage réel.

> **À retenir.** CloudWatch pour l'état et les performances (l'agent pour la mémoire et le disque, une rétention de logs à fixer), CloudTrail pour qui a fait quoi (trail d'organisation vers un compte de journaux), Config pour l'historique et la conformité avec remédiation, Systems Manager pour agir sur les instances sans SSH (Session Manager, Patch Manager).
