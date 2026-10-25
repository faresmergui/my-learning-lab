---
title: AWS SAA
name: AWS Certified Solutions Architect – Associate
org: Amazon Web Services
order: 2
color: "#ff9900"
description: Concevoir sur AWS des architectures sûres, résilientes, performantes et économes.
officialUrl: https://aws.amazon.com/certification/certified-solutions-architect-associate/
checked: 22 octobre 2026
format:
  - { label: Type, value: "QCM (une ou plusieurs bonnes réponses), en centre d'examen ou en ligne surveillé" }
  - { label: Durée, value: "130 minutes" }
  - { label: Questions, value: "65, dont 15 non notées (en test pour les futures versions)" }
  - { label: Score pour réussir, value: "720 sur 1 000" }
  - { label: Version, value: "SAA-C03" }
  - { label: Validité, value: "3 ans" }
domains:
  - name: Concevoir des architectures sécurisées
    weight: 30
    fiches: [aws/01-regions-zones-et-responsabilite, aws/02-iam-et-organizations, aws/03-vpc-et-reseau, aws/12-securite-et-chiffrement, securite/02-gestion-des-secrets, securite/07-tls-et-pki]
  - name: Concevoir des architectures résilientes
    weight: 26
    fiches: [aws/05-load-balancing-et-auto-scaling, aws/08-bases-de-donnees, aws/10-decoupler-sqs-sns-eventbridge, aws/11-route53-cloudfront, aws/14-resilience-et-reprise, aws/13-observabilite-et-gouvernance, reseaux/05-load-balancing-et-proxys]
  - name: Concevoir des architectures performantes
    weight: 24
    fiches: [aws/04-ec2, aws/06-s3, aws/07-ebs-efs-fsx, aws/08-bases-de-donnees, aws/09-conteneurs-et-serverless, aws/11-route53-cloudfront, reseaux/02-adressage-et-cidr]
  - name: Concevoir des architectures optimisées en coûts
    weight: 20
    fiches: [aws/15-maitriser-les-couts, aws/06-s3]
---

## Ce que l'examen vérifie vraiment

La SAA ne demande pas de cliquer dans la console : chaque question décrit une **situation** (« une entreprise veut… avec le moins d'effort d'exploitation possible ») et propose plusieurs architectures. Il faut choisir celle qui respecte **toutes** les contraintes de l'énoncé. C'est un examen de compromis entre sécurité, disponibilité, performance et coût.

Le module AWS du site suit ces quatre domaines, et sa dernière fiche (« Well-Architected et architectures types ») rassemble les architectures à reconnaître et les mots-clés des énoncés.

## Les pièges

- **Les mots-clés de l'énoncé.** « Le moins d'effort d'exploitation » pointe vers un service managé ; « le moins cher » vers Spot, S3 en classe froide, ou du serverless ; « hautement disponible » vers plusieurs zones de disponibilité. Souligne-les mentalement avant de lire les réponses.
- **Deux réponses correctes, une meilleure.** Souvent, plusieurs architectures marchent. Une seule respecte toutes les contraintes, ou le fait plus simplement.
- **Confondre haute disponibilité et reprise après sinistre.** Multi-AZ protège d'une panne de zone ; une copie dans une autre région protège d'une panne régionale.
- **Les questions à réponses multiples.** L'énoncé dit combien de réponses choisir : il faut toutes les bonnes pour gagner le point.

## À connaître par cœur

| Besoin | Réponse type |
| --- | --- |
| Donner des droits à une instance ou à un pod | un **rôle IAM**, jamais des clés d'accès stockées |
| Sortir sur Internet depuis un sous-réseau privé | une **NAT Gateway** dans un sous-réseau public |
| Découpler deux services | une file **SQS** |
| Diffuser un événement à plusieurs abonnés | **SNS** (ou EventBridge) |
| Base relationnelle hautement disponible | **RDS Multi-AZ** ; pour lire plus, des réplicas de lecture |
| Contenu statique servi vite partout | **S3 + CloudFront** |
| Charge imprévisible, pas de serveur à gérer | **Lambda**, **Fargate** |

## Se préparer

- Lire tout le module AWS, puis sa synthèse.
- Réviser les cartes de cette certification (bouton en haut de la page) jusqu'à les maîtriser.
- Construire soi-même, dans un compte d'essai avec un budget d'alerte, l'application à trois niveaux et l'API serverless.
- Passer des examens blancs (questions officielles d'entraînement d'AWS Skill Builder) et relire chaque erreur.

## Stratégie le jour J

1. Lis la **dernière phrase** de la question d'abord : c'est elle qui dit ce qu'on te demande.
2. Élimine les réponses qui violent une contrainte, puis choisis la plus simple parmi celles qui restent.
3. Marque les questions longues ou douteuses et reviens-y : 130 minutes pour 65 questions laisse environ 2 minutes par question.
