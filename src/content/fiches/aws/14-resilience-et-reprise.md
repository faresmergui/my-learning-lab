---
title: Résilience et reprise après sinistre
chapter: 14
order: 1
duration: 12
tags:
- AWS SAA
- reprise
- RPO
- RTO
cards:
- q: Que signifient RPO et RTO ?
  a: Le **RPO** (Recovery Point Objective) est la quantité maximale de données qu'on accepte de perdre, exprimée en temps (« 15 minutes de données »). Le **RTO** (Recovery Time Objective) est la durée maximale d'interruption acceptée (« reprise en 1 heure »).
- q: Quelles sont les quatre stratégies de reprise, de la moins chère à la plus chère ?
  a: '**Backup and restore** (heures), **pilot light** (le cœur, les données, est répliqué ; le reste est créé lors de la reprise : dizaines de minutes), **warm standby** (une copie réduite tourne en permanence et monte en charge : minutes), **multi-site active-active** (les deux régions servent le trafic : quasi zéro).'
- q: Haute disponibilité et reprise après sinistre, est-ce la même chose ?
  a: '**Non.** La haute disponibilité résiste aux pannes courantes (une instance, une AZ) dans une région, automatiquement. La reprise après sinistre répond à la perte d''une **région** ou à une corruption des données (rançongiciel, suppression), avec une procédure et des tests.'
- q: Que fait AWS Elastic Disaster Recovery ?
  a: Il réplique **en continu, au niveau bloc**, des serveurs (sur site ou EC2) vers une zone de transit peu coûteuse dans une région AWS, et lance des instances complètes en quelques minutes lors d'une reprise ou d'un exercice.
- q: Pourquoi la réplication ne remplace-t-elle pas la sauvegarde ?
  a: 'Une réplication copie **aussi les erreurs** : une table supprimée ou des fichiers chiffrés par un rançongiciel le sont aussitôt dans la copie. Il faut des **sauvegardes ponctuelles**, idéalement dans un autre compte, verrouillées (Vault Lock, Object Lock).'
- q: À quoi sert AWS Fault Injection Service ?
  a: 'À injecter volontairement des pannes (arrêter des instances, couper une AZ, ajouter de la latence) pour **vérifier** que l''architecture résiste vraiment : c''est l''ingénierie du chaos.'
quiz:
- q: Une application interne tolère une journée d'arrêt et la perte de 24 h de données. Budget minimal. Stratégie ?
  options:
  - Multi-site
  - Warm standby
  - Backup and restore avec sauvegardes copiées dans une autre région
  - Pilot light
  answer: 2
  explain: Un RTO et un RPO longs autorisent la stratégie la moins chère.
- q: Un RTO de 15 minutes et un RPO de quelques secondes sont exigés pour une base Aurora et une flotte web. Quelle stratégie au meilleur coût ?
  options:
  - Backup and restore
  - 'Pilot light : Aurora Global Database répliquée, instances créées à la demande'
  - 'Warm standby : Aurora Global Database et un ASG réduit dans la région de secours, Route 53 failover'
  - Aucune, impossible sur AWS
  answer: 2
  explain: Le pilot light risque de dépasser 15 minutes pour créer et démarrer toute la flotte ; le warm standby n'a qu'à monter en charge.
- q: Un rançongiciel a chiffré des volumes EBS, et les snapshots du même compte ont été supprimés par l'attaquant. Qu'aurait-il fallu ?
  options:
  - Plus de snapshots dans le même compte
  - Copier les sauvegardes dans un autre compte avec un coffre AWS Backup verrouillé
  - Multi-AZ
  - Un plus gros volume
  answer: 1
  explain: Un compte séparé et Vault Lock mettent les sauvegardes hors de portée d'un compte compromis.
level: intermédiaire
---

Tout finit par tomber en panne : un disque, une instance, une AZ, plus rarement une région entière, ou une erreur humaine qui efface des données. Le domaine « architectures résilientes » de l'examen demande de choisir le **bon niveau de protection** pour un besoin donné, sans payer pour plus que nécessaire.

> **Les outils cités dans cette fiche.**
> - **RPO** : combien de données on accepte de perdre. **RTO** : combien de temps on accepte d'être arrêté.
> - **AWS Backup** : centralise les sauvegardes et leurs copies vers d'autres régions ou comptes.
> - **AWS Elastic Disaster Recovery** (DRS) : réplication continue de serveurs entiers pour une reprise en minutes.
> - **Aurora Global Database**, **DynamoDB Global Tables**, **réplication S3** : réplication des données entre régions.
> - **Route 53 Application Recovery Controller** : contrôles de bascule et vérifications de préparation pour les applications multi-région.
> - **AWS Fault Injection Service** (FIS) : injecte des pannes pour tester la résilience.
> - **ASG** : Auto Scaling Group : un groupe d'instances EC2 dont le nombre s'ajuste automatiquement.
> - **ALB** : Application Load Balancer : le load balancer HTTP d'AWS.
> - **RDS** : le service de bases de données relationnelles gérées d'AWS.
> - **EFS** : le système de fichiers partagé (NFS) d'AWS.
> - **AMI** : l'image de disque à partir de laquelle on démarre une instance EC2.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **KMS** : le service de gestion des clés de chiffrement.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).

## Comprendre : du plus fréquent au plus rare

| Panne | Fréquence | Réponse |
| --- | --- | --- |
| instance, processus | courante | Auto Scaling, health checks, plusieurs instances |
| AZ | rare | **multi-AZ** partout (ASG, ALB, RDS Multi-AZ, EFS) |
| région | très rare | **reprise multi-région** selon RPO et RTO |
| données corrompues ou supprimées | dépend des humains et des attaquants | **sauvegardes ponctuelles** isolées, versioning, Object Lock |

Le multi-AZ est la **base** ; le multi-région est un **choix d'affaires**, qui se justifie par le coût d'une interruption.

## Les quatre stratégies

<!-- schema:dr -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="Les quatre stratégies de reprise" style="--minw:560px"><defs><marker id="g5-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g5-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g5-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g5-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><path d="M60 262 L664 262" class="dg-l" marker-end="url(#g5-n)"/><path d="M60 262 L60 16" class="dg-l" marker-end="url(#g5-n)"/><text x="664" y="284" class="dg-s" text-anchor="end">rapidité de reprise</text><text x="70" y="20" class="dg-s" text-anchor="start">coût</text><path d="M120 232 C 300 200, 450 150, 590 56" class="dg-l c dash"/><circle cx="120" cy="232" r="8" class="dg-dot dg-c dg-pop" style="--d:0"/><text x="120" y="202" class="dg-t" text-anchor="middle" style="--d:0">Backup &amp; restore</text><text x="120" y="216" class="dg-s" text-anchor="middle" style="--d:0">RTO : heures</text><circle cx="270" cy="182" r="8" class="dg-dot dg-c dg-pop" style="--d:1"/><text x="270" y="152" class="dg-t" text-anchor="middle" style="--d:1">Pilot light</text><text x="270" y="166" class="dg-s" text-anchor="middle" style="--d:1">RTO : dizaines de min</text><circle cx="430" cy="122" r="8" class="dg-dot dg-c dg-pop" style="--d:2"/><text x="430" y="92" class="dg-t" text-anchor="middle" style="--d:2">Warm standby</text><text x="430" y="106" class="dg-s" text-anchor="middle" style="--d:2">RTO : minutes</text><circle cx="590" cy="56" r="8" class="dg-dot dg-c dg-pop" style="--d:3"/><text x="590" y="86" class="dg-t" text-anchor="middle" style="--d:3">Multi-site actif-actif</text><text x="590" y="100" class="dg-s" text-anchor="middle" style="--d:3">RTO et RPO ≈ 0</text></svg><figcaption>Plus la reprise est rapide, plus on paie une infrastructure qui attend.</figcaption></figure>
<!-- /schema:dr -->

| Stratégie | Dans la région de secours | RPO | RTO |
| --- | --- | --- | --- |
| **Backup and restore** | seulement les sauvegardes (snapshots, AMI copiées) | heures | heures |
| **Pilot light** | les **données** répliquées (base, S3) ; serveurs éteints ou absents, IaC prête | secondes à minutes | dizaines de minutes |
| **Warm standby** | une **copie complète réduite** qui tourne ; on l'agrandit | secondes | minutes |
| **Multi-site** | une copie complète qui **sert déjà** du trafic | quasi nul | quasi nul |

Les briques de chaque stratégie :

- données : AWS Backup avec copie inter-région, S3 CRR, Aurora Global Database, DynamoDB Global Tables, read replica RDS inter-région ;
- calcul : AMI copiées, CloudFormation ou Terraform prêts, ASG à faible capacité, Elastic Disaster Recovery ;
- trafic : Route 53 **failover** ou **latency** avec health checks, Global Accelerator, Application Recovery Controller.

## Les règles qui comptent

1. **La réplication n'est pas une sauvegarde** : elle copie aussi les suppressions et le chiffrement par un rançongiciel.
2. **Isoler les sauvegardes** : un autre compte, un coffre AWS Backup avec **Vault Lock**, Object Lock sur S3.
3. **Tout en code** : une région de secours se reconstruit avec l'IaC, pas à la main un soir de crise.
4. **Penser aux dépendances** : quotas de service dans la région de secours, clés KMS multi-région, secrets répliqués, certificats ACM, DNS.
5. **Tester** : un plan jamais exercé ne fonctionne pas. Exercices de bascule réguliers et pannes injectées avec **FIS**.
6. **Bascule de données** : décider qui déclenche, comment éviter que les deux régions écrivent en même temps (« split brain »), comment revenir ensuite.

## Les mécanismes de résilience au quotidien

- **Découpler** (SQS) pour absorber les pics et les pannes d'un consommateur.
- **Nouvelles tentatives avec attente exponentielle** et **délais d'expiration** côté client.
- **Limitation de débit** (API Gateway, WAF) pour ne pas être submergé.
- **Dégradation gracieuse** : servir une page en cache (CloudFront) si l'origine tombe.
- **Quotas** de service surveillés (Service Quotas, Trusted Advisor) : un plafond atteint est une panne.

> **À retenir.** Multi-AZ pour les pannes courantes, multi-région pour la perte d'une région, sauvegardes isolées pour les erreurs et les attaques. Quatre stratégies de reprise, du moins cher au plus rapide : backup and restore, pilot light, warm standby, multi-site. Le RPO dicte la réplication des données, le RTO ce qui tourne déjà dans la région de secours. Un plan non testé ne compte pas.
