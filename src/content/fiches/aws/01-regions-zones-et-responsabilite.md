---
title: Régions, zones et responsabilité partagée
chapter: 1
order: 1
duration: 10
tags:
- AWS SAA
- fondations
cards:
- q: Différence entre une région et une zone de disponibilité ?
  a: 'Une **région** est une zone géographique (`eu-west-3` = Paris) indépendante des autres. Elle contient plusieurs **zones de disponibilité** (AZ) : des groupes de data centers séparés physiquement, reliés par un réseau rapide. Une panne d''une AZ ne touche pas les autres.'
- q: Pourquoi déployer sur au moins deux AZ ?
  a: 'Pour survivre à la panne d''un data center entier. C''est la base de la haute disponibilité sur AWS : instances, sous-réseaux et bases réparties sur plusieurs AZ.'
- q: Que dit le modèle de responsabilité partagée ?
  a: AWS est responsable de la sécurité **du** cloud (bâtiments, matériel, hyperviseur, réseau physique). Le client est responsable de la sécurité **dans** le cloud (IAM, données, chiffrement, configuration réseau, système des instances).
- q: Quels services sont globaux et non régionaux ?
  a: '**IAM**, **Route 53**, **CloudFront** et **Organizations** notamment. La plupart des autres (EC2, RDS, VPC…) sont régionaux : une ressource créée à Paris n''existe pas en Irlande.'
- q: Qu'est-ce qu'un point de présence (edge location) ?
  a: Un site plus petit qu'une région, dans de nombreuses villes, utilisé par **CloudFront** et **Route 53** pour répondre au plus près des utilisateurs.
- q: Sur quels critères choisir une région ?
  a: Les **obligations légales** (où les données doivent rester), la **latence** vers les utilisateurs, les **services disponibles** (tous ne sont pas partout) et le **prix**, qui varie d'une région à l'autre.
quiz:
- q: Une entreprise doit garder ses données de santé en France. Que fais-tu ?
  options:
  - Déployer dans toutes les régions
  - Choisir `eu-west-3` (Paris) et ne pas répliquer hors de France
  - Utiliser seulement CloudFront
  - Déployer dans `us-east-1`, la moins chère
  answer: 1
  explain: La conformité passe avant le prix. Les données restent dans la région choisie tant qu'on ne les copie pas ailleurs.
- q: Qui doit appliquer les correctifs du système d'une instance EC2 ?
  options:
  - AWS
  - Le client
  - Personne, c'est automatique
  - Le support AWS
  answer: 1
  explain: Sur EC2, tout ce qui est au-dessus de l'hyperviseur est à toi. Sur un service managé comme RDS, AWS gère le système et le moteur.
level: intermédiaire
---

Avant de construire quoi que ce soit sur AWS (Amazon Web Services), il faut comprendre trois idées : où tournent les ressources (régions et zones), qui est responsable de quoi, et comment on parle à AWS. Elles reviennent dans presque toutes les questions de la certification Solutions Architect.

> **Les outils cités dans cette fiche.**
> - **AWS** : le cloud d'Amazon, plus de 200 services loués à l'usage (serveurs, stockage, bases, réseau…).
> - **région** : une zone géographique (Paris, Irlande, Virginie) avec son propre ensemble de services.
> - **AZ** (Availability Zone, zone de disponibilité) : un ou plusieurs data centers isolés au sein d'une région.
> - **console** : l'interface web d'AWS. **AWS CLI** : la commande `aws`, pour faire la même chose en ligne de commande.
> - **SDK** : les bibliothèques qui permettent à un programme (Python, Go…) d'appeler AWS.
> - **ARN** (Amazon Resource Name) : l'identifiant unique d'une ressource, par exemple `arn:aws:s3:::mon-bucket`.
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).
> - **WAF** : un pare-feu applicatif qui filtre les requêtes web malveillantes.
> - **VPC** : un réseau privé virtuel dans le cloud, isolé des autres clients.
> - **EC2** : le service de machines virtuelles d'AWS.
> - **AMI** : l'image de disque à partir de laquelle on démarre une instance EC2.
> - **RDS** : le service de bases de données relationnelles gérées d'AWS.

## Comprendre : la géographie d'AWS

```
Région eu-west-3 (Paris)
├── AZ eu-west-3a   ← data center(s) A
├── AZ eu-west-3b   ← data center(s) B, à plusieurs km
└── AZ eu-west-3c
        reliées par un réseau privé à faible latence
Points de présence (CloudFront, Route 53) : des centaines de villes
```

| Niveau | Rôle | Panne qui la touche |
| --- | --- | --- |
| point de présence | cache et DNS au plus près | rare, transparent |
| AZ | héberge instances, volumes, sous-réseaux | incendie, coupure électrique d'un site |
| région | regroupe les AZ, isolée des autres | très rare (incident régional) |

Règle d'or : une architecture de production tient sur **au moins deux AZ**. Survivre à la perte d'une **région** entière demande une architecture multi-région, plus chère, réservée aux besoins critiques (fiche sur la reprise après sinistre).

## Global ou régional ?

| Portée | Services |
| --- | --- |
| global | IAM, Route 53, CloudFront, Organizations, WAF pour CloudFront |
| régional | VPC, EC2 (AMI), RDS, S3 (le nom est global, les données sont dans une région), Lambda… |
| par AZ | sous-réseau, instance EC2, volume EBS |

Un piège classique : un volume EBS est lié à **une AZ**. Il ne peut pas être attaché à une instance d'une autre AZ sans passer par un snapshot.

## La responsabilité partagée

| AWS s'occupe de | Tu t'occupes de |
| --- | --- |
| bâtiments, électricité, matériel | qui a accès à quoi (IAM) |
| hyperviseur, réseau physique | chiffrement et sauvegarde de tes données |
| le système et le moteur des services managés (RDS, Lambda) | groupes de sécurité, règles réseau |
| | système et correctifs de tes instances EC2 |

Plus un service est **managé**, plus AWS en prend une part : sur EC2 tu gères le système, sur RDS seulement la base et ses accès, sur Lambda seulement ton code et ses droits.

## Parler à AWS

Tout passe par une **API** : la console, la CLI, Terraform et les SDK ne font qu'appeler cette API, avec une identité IAM.

```bash
aws configure sso                     # se connecter avec un compte d'entreprise (recommandé)
aws sts get-caller-identity           # « qui suis-je ? » : compte et rôle utilisés
aws ec2 describe-instances --region eu-west-3 --output table
aws s3 ls
```

Chaque appel est **régional** : si tu ne vois pas une ressource, vérifie d'abord la région (`--region` ou la variable `AWS_REGION`).

## Choisir une région

1. **Conformité** : où les données ont-elles le droit d'être ?
2. **Latence** : près des utilisateurs.
3. **Services** : le service voulu existe-t-il dans cette région ?
4. **Prix** : il varie d'une région à l'autre, parfois de 10 à 20 %.

> **À retenir.** Une région contient plusieurs AZ isolées ; la production tient sur au moins deux AZ. IAM, Route 53 et CloudFront sont globaux, presque tout le reste est régional, et un volume EBS est lié à une AZ. AWS sécurise le cloud, toi ce que tu mets dedans.
