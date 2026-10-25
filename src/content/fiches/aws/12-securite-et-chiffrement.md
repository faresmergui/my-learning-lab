---
title: Chiffrement, secrets et services de sécurité
chapter: 12
order: 1
duration: 13
tags:
- AWS SAA
- KMS
- WAF
- GuardDuty
cards:
- q: Qu'est-ce que le chiffrement par enveloppe de KMS ?
  a: KMS ne chiffre pas tes données directement (limite de 4 Ko). Il génère une **clé de données**, que le service utilise pour chiffrer localement, puis il la renvoie **chiffrée par la clé KMS**. Pour déchiffrer, on demande à KMS de déchiffrer la clé de données, ce qui passe par IAM et laisse une trace dans CloudTrail.
- q: Différence entre une clé KMS gérée par AWS et une clé gérée par le client ?
  a: La clé **gérée par AWS** (`aws/s3`, `aws/ebs`) est créée et utilisée automatiquement par un service ; on ne contrôle pas sa politique. La clé **gérée par le client** a une **politique de clé** à toi (qui peut l'utiliser, y compris depuis d'autres comptes), une rotation réglable et peut être désactivée.
- q: Secrets Manager ou Parameter Store ?
  a: '**Secrets Manager** : fait pour les secrets, avec **rotation automatique** (RDS, Redshift, ou une Lambda), réplication entre régions, facturé par secret. **Parameter Store** (Systems Manager) : configuration et secrets simples (`SecureString` chiffré par KMS), gratuit en niveau standard, sans rotation intégrée.'
- q: Que protège AWS WAF et où se place-t-il ?
  a: Les applications web contre les attaques **HTTP** (injection SQL, XSS, robots, limitation de débit par IP, blocage par pays) avec des règles gérées ou personnalisées. Il s'attache à **CloudFront, ALB, API Gateway, AppSync, Cognito, App Runner**.
- q: Shield Standard ou Shield Advanced ?
  a: '**Standard** : gratuit et automatique, contre les attaques DDoS réseau courantes (couches 3 et 4). **Advanced** : payant, protection renforcée, équipe de réponse AWS (SRT), protection contre la hausse de facture due à l''attaque, visibilité détaillée.'
- q: Que font GuardDuty, Inspector et Macie ?
  a: '**GuardDuty** détecte les **menaces** en analysant CloudTrail, les VPC Flow Logs, le DNS (et plus : EKS, S3, RDS, Lambda). **Inspector** cherche les **vulnérabilités** dans les instances, images ECR et Lambda. **Macie** trouve les **données sensibles** (données personnelles, cartes bancaires) dans S3.'
- q: À quoi sert Security Hub ?
  a: À **centraliser** les alertes de GuardDuty, Inspector, Macie, Config et d'outils tiers, et à vérifier la conformité à des standards (CIS, AWS Foundational Security Best Practices), sur tous les comptes de l'organisation.
quiz:
- q: Une application stocke un mot de passe de base de données qui doit changer tous les 30 jours sans intervention. Quel service ?
  options:
  - Parameter Store standard
  - Secrets Manager avec rotation automatique
  - Une variable d'environnement Lambda
  - Un fichier chiffré dans S3
  answer: 1
  explain: La rotation intégrée met à jour la base et le secret ; l'application lit toujours la version courante.
- q: Une API publique subit des milliers de requêtes par seconde depuis quelques IP. Quelle réponse rapide ?
  options:
  - Shield Advanced obligatoirement
  - Une règle WAF de limitation de débit (rate-based) sur l'ALB ou CloudFront
  - Une NACL par IP pour chaque attaquant
  - Agrandir les instances
  answer: 1
  explain: La règle rate-based bloque automatiquement les IP qui dépassent un seuil.
- q: Tu veux être alerté si des identifiants IAM sont utilisés depuis une IP malveillante connue. Quel service ?
  options:
  - Inspector
  - GuardDuty
  - Macie
  - Trusted Advisor
  answer: 1
  explain: GuardDuty analyse CloudTrail avec des listes de menaces et de l'apprentissage automatique.
level: intermédiaire
---

Après IAM et le réseau, la sécurité AWS repose sur trois piliers : **chiffrer** les données, **garder les secrets** hors du code, et **détecter** ce qui se passe mal. L'examen demande surtout de reconnaître quel service répond à quel besoin. La fiche Sécurité sur la gestion des secrets explique les principes généraux.

> **Les outils cités dans cette fiche.**
> - **KMS** (Key Management Service) : crée et protège les clés de chiffrement ; elles ne quittent jamais KMS en clair.
> - **CloudHSM** : un module matériel de sécurité dédié (HSM), dont tu es seul à contrôler les clés.
> - **Secrets Manager** : stocke des secrets et les fait **tourner** automatiquement.
> - **Parameter Store** : la partie de Systems Manager qui stocke configuration et secrets simples.
> - **ACM** (Certificate Manager) : certificats TLS gratuits et renouvelés automatiquement pour les services AWS.
> - **WAF** (Web Application Firewall) : filtre les requêtes HTTP. **Shield** : protection contre les attaques DDoS (déni de service distribué).
> - **GuardDuty**, **Inspector**, **Macie**, **Security Hub** et **Detective** : détection des menaces, des vulnérabilités, des données sensibles, centralisation et enquête.
> - **Cognito** : gère les utilisateurs d'une application (inscription, connexion, fédération avec Google ou un annuaire).
> - **RDS** : le service de bases de données relationnelles gérées d'AWS.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **ECS** : le service d'exécution de conteneurs d'AWS.
> - **EKS** : le service Kubernetes managé d'AWS.
> - **CSI** : le standard des pilotes de stockage de Kubernetes.
> - **ALB** : Application Load Balancer : le load balancer HTTP d'AWS.
> - **OWASP** : une fondation qui publie les références de sécurité des applications web.
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.

## Chiffrer avec KMS

```
Service (S3, EBS, RDS) ── « génère une clé de données » ──► KMS (clé KMS, ne sort jamais)
        ◄── clé en clair + même clé chiffrée ──
chiffre les données avec la clé en clair, l'efface de la mémoire,
stocke la clé chiffrée à côté des données
```

| Type de clé | Contrôle | Usage |
| --- | --- | --- |
| gérée par AWS (`aws/ebs`) | aucun sur la politique | chiffrement par défaut, rien à faire |
| **gérée par le client** | politique de clé, rotation, désactivation, accès entre comptes | le cas standard en entreprise |
| clé importée ou **CloudHSM** | tu fournis ou gardes le matériel de clé | exigences réglementaires fortes |

Points clés :

- la **politique de clé** décide qui peut l'utiliser ; sans elle, même un administrateur IAM n'y a pas accès ;
- **rotation automatique** annuelle (ou réglable) : les anciennes versions restent pour déchiffrer ;
- une clé KMS est **régionale** ; les **clés multi-région** existent pour la reprise après sinistre ;
- chaque usage est tracé dans **CloudTrail** : on sait qui a déchiffré quoi ;
- supprimer une clé impose un délai de 7 à 30 jours, car tout ce qu'elle chiffrait devient illisible.

## Garder les secrets

| | Secrets Manager | Parameter Store |
| --- | --- | --- |
| rotation automatique | oui (RDS, Aurora, Redshift, DocumentDB, ou Lambda) | non |
| réplication multi-région | oui | non |
| coût | par secret et par appel | gratuit en standard |
| pour | mots de passe de bases, clés d'API tierces | configuration, chemins hiérarchiques, secrets simples |

Les deux s'appellent par API avec un rôle IAM, et s'intègrent à ECS, EKS (pilote CSI), Lambda et CloudFormation.

## Protéger les applications exposées

- **WAF** sur CloudFront, ALB, API Gateway : règles gérées par AWS (OWASP Top 10, IP de mauvaise réputation, robots), règles **rate-based**, blocage par pays, règles sur en-têtes et corps.
- **Shield Standard** (gratuit) contre les DDoS réseau ; **Shield Advanced** pour les cibles critiques, avec l'équipe de réponse et la protection des coûts.
- **Firewall Manager** applique les mêmes règles WAF, Shield et security groups à tous les comptes de l'organisation.
- **Network Firewall** : un pare-feu managé au niveau du VPC (filtrage par domaine, inspection).

## Détecter

| Service | Ce qu'il trouve | Sources |
| --- | --- | --- |
| **GuardDuty** | activité malveillante : identifiants volés, minage de cryptomonnaie, connexions vers des serveurs malveillants | CloudTrail, Flow Logs, DNS, EKS, S3, RDS, Lambda |
| **Inspector** | vulnérabilités connues (CVE) et exposition réseau | instances EC2, images ECR, Lambda |
| **Macie** | données sensibles et buckets mal protégés | S3 |
| **Detective** | enquête : relie les événements autour d'une alerte | GuardDuty, CloudTrail, Flow Logs |
| **Security Hub** | tableau central et conformité | tous les précédents + Config + tiers |
| **IAM Access Analyzer** | ressources partagées hors du compte, droits inutilisés | politiques |

On les active **dans tous les comptes et toutes les régions** depuis un compte d'administration délégué, et on envoie les alertes vers EventBridge pour réagir automatiquement (isoler une instance, ouvrir un ticket).

## Les utilisateurs d'une application

**Cognito** a deux parties : les **user pools** (annuaire d'utilisateurs, connexion, MFA, fédération Google, Apple, SAML, OIDC ; délivre des jetons JWT) et les **identity pools** (échangent ces jetons contre des identifiants AWS temporaires, pour qu'une appli mobile écrive directement dans S3, par exemple).

> **À retenir.** KMS protège des clés qui ne sortent jamais, par chiffrement d'enveloppe ; la politique de clé décide qui les utilise et CloudTrail trace chaque usage. Secrets Manager quand il faut la rotation, Parameter Store pour la configuration. WAF filtre le HTTP, Shield contre le DDoS. GuardDuty détecte les menaces, Inspector les failles, Macie les données sensibles, Security Hub centralise.
