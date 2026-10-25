---
title: Maîtriser les coûts
chapter: 15
order: 1
duration: 12
tags:
- AWS SAA
- coûts
- FinOps
cards:
- q: Quels sont les modèles d'achat d'EC2 ?
  a: '**À la demande** (aucun engagement), **Savings Plans** (engagement d''une dépense horaire sur 1 ou 3 ans, jusqu''à ~72 % de remise), **instances réservées** (engagement sur un type précis), **Spot** (capacité inutilisée, jusqu''à ~90 % de remise, mais reprise avec 2 minutes de préavis) et **hôtes dédiés** (licences, conformité).'
- q: Compute Savings Plan ou EC2 Instance Savings Plan ?
  a: Le **Compute Savings Plan** s'applique à toute famille, région, système, et aussi à Fargate et Lambda (~66 % max). L'**EC2 Instance Savings Plan** est lié à une famille dans une région, mais la remise est plus forte (~72 % max).
- q: Pour quelles charges utiliser Spot ?
  a: 'Les charges **interruptibles** ou **sans état** : traitements par lots, CI, rendu, analyse, nœuds Kubernetes tolérants, workers SQS. Jamais une base de données unique ou une tâche qui ne peut pas reprendre.'
- q: Quels transferts réseau sont facturés ?
  a: 'Les données **entrantes** depuis Internet sont gratuites. Sont facturés : la **sortie vers Internet**, le trafic **entre régions**, le trafic **entre AZ** (dans les deux sens), et le passage par une **NAT Gateway** (au Go). Le trafic dans une même AZ par IP privée est gratuit.'
- q: Quels outils pour suivre et maîtriser les dépenses ?
  a: '**Cost Explorer** (analyse et prévisions), **AWS Budgets** (alertes et actions au dépassement), **Cost Anomaly Detection** (détecte les dérives), **Cost and Usage Report** / Data Exports (détail ligne à ligne), les **tags de répartition des coûts**, et **Compute Optimizer** (redimensionnement).'
- q: Comment réduire la facture S3 sans rien perdre ?
  a: Choisir la bonne **classe** (Intelligent-Tiering si l'accès est inconnu), des règles de **cycle de vie** vers IA et Glacier, l'**expiration** des anciennes versions et des envois multipart inachevés, et un **endpoint gateway** pour éviter la NAT.
quiz:
- q: Un cluster de traitement d'images tourne la nuit, les tâches peuvent être reprises si elles sont interrompues. Option la moins chère ?
  options:
  - Instances réservées
  - Instances Spot
  - À la demande
  - Hôtes dédiés
  answer: 1
  explain: Les charges interruptibles sont le cas idéal pour Spot, souvent mélangé à un peu d'à la demande dans l'ASG.
- q: Une entreprise utilise EC2, Fargate et Lambda en continu et prévoit de changer de familles d'instances. Quel engagement ?
  options:
  - EC2 Instance Savings Plan
  - Compute Savings Plan
  - Instances réservées standard
  - Aucun
  answer: 1
  explain: Le Compute Savings Plan suit la dépense quel que soit le service de calcul, la famille ou la région.
- q: La facture de NAT Gateway représente 30 % du total, surtout à cause de transferts vers S3 et DynamoDB. Que fais-tu ?
  options:
  - Une NAT Gateway par sous-réseau
  - Des VPC endpoints gateway pour S3 et DynamoDB
  - Passer en IPv6
  - Supprimer les sous-réseaux privés
  answer: 1
  explain: Les endpoints gateway sont gratuits et sortent ce trafic de la NAT.
level: intermédiaire
---

Sur AWS, on paie ce qu'on utilise, ce qui veut dire aussi ce qu'on oublie d'éteindre. Le domaine « architectures optimisées en coûts » de l'examen représente 20 % de la note. La bonne nouvelle : les mêmes leviers reviennent toujours.

> **Les outils cités dans cette fiche.**
> - **Savings Plans** : un engagement de dépense horaire sur 1 ou 3 ans, en échange d'une remise.
> - **instances réservées** (RI) : l'ancien modèle d'engagement, lié à un type d'instance ; encore utilisé pour RDS, ElastiCache, Redshift, OpenSearch.
> - **Spot** : la capacité EC2 inutilisée, vendue avec une forte remise, que AWS peut reprendre.
> - **Cost Explorer**, **AWS Budgets**, **Cost Anomaly Detection** : analyser, alerter, détecter les dérives.
> - **Compute Optimizer** : recommande la bonne taille d'instance, de volume ou de Lambda.
> - **FinOps** : la pratique qui rend chaque équipe responsable de ses coûts cloud.
> - **CDN** : un réseau de serveurs répartis dans le monde qui servent le contenu au plus près des utilisateurs.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **nœud** : une machine (physique ou virtuelle) membre d'un cluster.
> - **ASG** : Auto Scaling Group : un groupe d'instances EC2 dont le nombre s'ajuste automatiquement.
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **EBS** : les disques réseau attachés aux instances EC2.
> - **IOPS** : le nombre d'opérations de lecture ou d'écriture qu'un disque fait par seconde.
> - **EFS** : le système de fichiers partagé (NFS) d'AWS.

## Comprendre : les quatre leviers

1. **Ne payer que ce qui sert** : éteindre, supprimer, dimensionner juste.
2. **Payer moins cher ce qui sert** : engagements, Spot, Graviton, classes de stockage.
3. **Choisir une architecture économe** : serverless pour un trafic irrégulier, cache, CDN.
4. **Voir et responsabiliser** : tags, budgets, alertes, rapports par équipe.

## Les modèles d'achat du calcul

| Modèle | Remise max (indicative) | Engagement | Pour |
| --- | --- | --- | --- |
| à la demande | — | aucun | court terme, imprévisible, tests |
| **Compute Savings Plan** | ~66 % | dépense horaire, 1 ou 3 ans | toute charge de calcul stable (EC2, Fargate, Lambda) |
| EC2 Instance Savings Plan | ~72 % | famille et région | flotte stable bien connue |
| instances réservées | ~72 % | type, région (option convertible) | RDS, ElastiCache, Redshift… |
| **Spot** | ~90 % | aucun, mais interruption possible (préavis de 2 min) | lots, CI, workers, nœuds tolérants |
| hôte dédié | — | serveur physique pour toi | licences liées au matériel, conformité |

La stratégie habituelle : une **base** couverte par des Savings Plans, les **pics** en à la demande, le **travail interruptible** en Spot, le tout dans des ASG à types d'instances mélangés. Les processeurs **Graviton** ajoutent environ 20 % d'économie à performance égale.

## Le stockage

- S3 : bonne classe, **Intelligent-Tiering** si l'accès est inconnu, cycle de vie, expiration des anciennes versions et des envois inachevés.
- EBS : passer de **gp2 à gp3** (environ 20 % moins cher), supprimer les **volumes non attachés** et les vieux snapshots, réduire les IOPS provisionnées inutiles.
- EFS : classes IA et Archive avec cycle de vie.
- Logs CloudWatch : fixer une **rétention** (par défaut, ils sont gardés pour toujours).

## Le réseau, piège classique

| Trafic | Coût |
| --- | --- |
| Internet vers AWS | gratuit |
| dans une même AZ, IP privées | gratuit |
| **entre AZ** | facturé dans les deux sens |
| **entre régions** | facturé |
| **AWS vers Internet** | facturé (moins cher via CloudFront) |
| **NAT Gateway** | à l'heure **et** au Go traité |

Leviers : **endpoints gateway** (S3, DynamoDB) au lieu de la NAT, **CloudFront** devant les contenus servis à Internet, garder les échanges intenses dans la même AZ quand la résilience le permet, une NAT par AZ plutôt qu'un trafic qui traverse les AZ.

## Les architectures économes

- **Serverless** (Lambda, Fargate, DynamoDB on-demand, Aurora Serverless v2) pour un trafic faible ou irrégulier : on ne paie pas l'inactivité.
- **Auto Scaling** et **arrêt planifié** des environnements de développement la nuit et le week-end (Instance Scheduler).
- **Cache** (CloudFront, ElastiCache) pour soulager des bases coûteuses.
- **Découplage** (SQS) pour dimensionner sur la charge moyenne plutôt que sur le pic.

## Voir et piloter

- **Tags de répartition des coûts** (`equipe`, `projet`, `env`) imposés par des **tag policies** de l'organisation.
- **AWS Budgets** : alerte à 80 % du budget, et **actions** (appliquer une politique restrictive, arrêter des instances).
- **Cost Explorer** : par service, compte, tag ; prévisions ; recommandations de Savings Plans.
- **Cost Anomaly Detection** : alerte sur une hausse inhabituelle (une boucle Lambda, un transfert imprévu).
- **Compute Optimizer** et **Trusted Advisor** : instances surdimensionnées, ressources inutilisées.
- **Facturation consolidée** d'Organizations : les remises de volume et les Savings Plans se partagent entre comptes.

> **À retenir.** Couvrir la base stable avec des Savings Plans (Compute si l'usage bouge), mettre l'interruptible en Spot, préférer Graviton et gp3. Classe et cycle de vie sur S3, rétention sur les logs. Le réseau coûte : entre AZ, entre régions, vers Internet et par la NAT ; endpoints gateway et CloudFront réduisent la note. Tags, budgets et détection d'anomalies pour savoir qui dépense quoi.
