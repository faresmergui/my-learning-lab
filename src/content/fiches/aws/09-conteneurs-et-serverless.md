---
title: 'Conteneurs et serverless : ECS, EKS, Lambda'
chapter: 9
order: 1
duration: 13
tags:
- AWS SAA
- ECS
- Lambda
- serverless
cards:
- q: Différence entre ECS et EKS ?
  a: '**ECS** est l''orchestrateur de conteneurs propre à AWS, simple et très intégré. **EKS** est du **Kubernetes** managé : AWS gère le control plane, tu retrouves l''API et l''écosystème Kubernetes standard.'
- q: Qu'est-ce que Fargate ?
  a: 'Un mode d''exécution **sans serveur** pour ECS et EKS : tu déclares CPU et mémoire par tâche ou pod, AWS fournit la capacité. Plus de nœuds EC2 à gérer, à corriger ni à dimensionner.'
- q: Quelles sont les principales limites d'une fonction Lambda ?
  a: '**15 minutes** maximum par exécution, jusqu''à **10 Go** de mémoire (le CPU suit la mémoire), 10 Go d''espace `/tmp`, paquet de 250 Mo décompressé (ou image de 10 Go), et une **concurrence** limitée par compte et par région (1 000 par défaut, augmentable).'
- q: Qu'est-ce qu'un démarrage à froid et comment le réduire ?
  a: 'La première invocation d''un nouvel environnement doit charger le code et l''initialiser : quelques centaines de ms à quelques secondes. On le réduit avec la **provisioned concurrency** (environnements prêts à l''avance), **SnapStart** (Java, Python, .NET) ou un code d''initialisation plus léger.'
- q: À quoi sert API Gateway ?
  a: À exposer des API (REST, HTTP, WebSocket) devant Lambda ou d'autres services, avec authentification (IAM, Cognito, JWT), **limitation de débit**, clés d'API, cache et transformations. Les **HTTP APIs** sont plus simples et moins chères que les REST APIs.
- q: Qu'apporte Step Functions ?
  a: 'Un **orchestrateur** de workflows : enchaîner des étapes (Lambda, appels à des services AWS, attente, choix, parallélisme, nouvelles tentatives) décrites en machine à états, avec l''historique de chaque exécution.'
quiz:
- q: Un traitement vidéo dure 40 minutes par fichier. Quelle solution serverless ?
  options:
  - Lambda
  - Une tâche ECS sur Fargate déclenchée par un événement
  - API Gateway
  - Step Functions seul
  answer: 1
  explain: Lambda est limitée à 15 minutes. Fargate n'a pas cette limite et ne demande pas de serveur à gérer.
- q: Une équipe a déjà des manifestes et des charts Helm et veut rester portable. Quel orchestrateur ?
  options:
  - ECS
  - EKS
  - Elastic Beanstalk
  - App Runner
  answer: 1
  explain: 'EKS est du Kubernetes standard : les manifestes et Helm fonctionnent tels quels.'
- q: Une API Lambda a des temps de réponse irréguliers au premier appel après une période calme, ce qui gêne les utilisateurs. Que fais-tu ?
  options:
  - Augmenter le délai d'expiration
  - Activer la provisioned concurrency
  - Passer en EC2 obligatoirement
  - Diminuer la mémoire
  answer: 1
  explain: Des environnements pré-initialisés suppriment les démarrages à froid, pour un coût fixe.
level: intermédiaire
---

Entre la machine virtuelle EC2 et la fonction qui tourne quelques millisecondes, AWS propose toute une gamme où l'on gère de moins en moins de choses soi-même. L'examen demande de choisir le bon niveau : contrôle total, conteneurs, ou serverless.

> **Les outils cités dans cette fiche.**
> - **ECS** (Elastic Container Service) : l'orchestrateur de conteneurs d'AWS. Une **task definition** décrit les conteneurs, un **service** maintient N tâches.
> - **EKS** (Elastic Kubernetes Service) : Kubernetes managé par AWS.
> - **Fargate** : exécute des conteneurs ECS ou EKS sans nœuds à gérer.
> - **ECR** (Elastic Container Registry) : le registre d'images de conteneurs d'AWS, avec scan de vulnérabilités.
> - **Lambda** : exécute une fonction en réponse à un événement, facturée à la milliseconde.
> - **API Gateway** : un service qui expose et protège des API HTTP.
> - **Step Functions** : un orchestrateur de workflows en machine à états.
> - **serverless** : aucun serveur à gérer ni à dimensionner ; on paie à l'usage et ça monte en charge seul.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).
> - **ALB** : Application Load Balancer : le load balancer HTTP d'AWS.
> - **AZ** : une zone de disponibilité : un ou plusieurs datacenters indépendants dans une région.
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **SQS** : le service de files de messages d'AWS.
> - **SNS** : le service de notifications d'AWS, qui diffuse un message à plusieurs abonnés.
> - **VPC** : un réseau privé virtuel dans le cloud, isolé des autres clients.
> - **NAT** : la traduction d'adresses : plusieurs machines privées sortent sur Internet avec une seule adresse publique.

## Comprendre : qui gère quoi

| | EC2 | ECS/EKS sur EC2 | ECS/EKS sur Fargate | Lambda |
| --- | --- | --- | --- | --- |
| système et correctifs | toi | toi (nœuds) | AWS | AWS |
| dimensionner les serveurs | toi | toi | AWS | AWS |
| unité | instance | conteneur | conteneur | fonction |
| durée max | illimitée | illimitée | illimitée | 15 minutes |
| facturation | à la seconde, allumée | instances | vCPU et mémoire de la tâche | requêtes + durée × mémoire |

## ECS

```
Cluster ECS
└── Service « api » (desired 4, derrière un ALB)
    └── Tâches (task definition api:12)
        ├── conteneur api      image ECR, 0,5 vCPU, 1 Go
        └── conteneur envoy    sidecar
```

Points à connaître :

- deux **launch types** : **EC2** (tes instances, plus de contrôle, moins cher à grande échelle) et **Fargate** ;
- **task role** : le rôle IAM des conteneurs (leurs droits sur AWS) ; **task execution role** : le rôle qu'utilise ECS pour tirer l'image et écrire les logs ;
- le service s'intègre à l'ALB (chaque tâche est une cible) et à l'auto scaling ;
- **capacity providers** pour mélanger Fargate et Fargate Spot.

## EKS

AWS gère le control plane (API server, etcd) sur plusieurs AZ. Toi, tu choisis comment fournir les nœuds : **managed node groups**, **Karpenter** (qui crée les nœuds à la demande), **Fargate** ou **EKS Auto Mode** (AWS gère aussi les nœuds). Les pods obtiennent des droits AWS par **EKS Pod Identity** ou **IRSA**. Tout ce que le module Kubernetes enseigne s'applique.

## Lambda

```python
def handler(event, context):
    # event : la requête API Gateway, le message SQS, l'objet S3 créé…
    return {"statusCode": 200, "body": "ok"}
```

| Notion | À retenir |
| --- | --- |
| déclencheurs | API Gateway, ALB, S3, SQS, SNS, EventBridge, DynamoDB Streams, Kinesis… |
| mémoire | de 128 Mo à 10 Go ; le CPU est proportionnel |
| durée | 15 minutes maximum |
| concurrence | 1 000 par région par défaut ; **reserved** (garantie et plafond pour une fonction), **provisioned** (pré-initialisée) |
| invocation | **synchrone** (API), **asynchrone** (S3, SNS : nouvelles tentatives, destination d'échec), **par lots** (SQS, Kinesis) |
| dans un VPC | pour joindre une base privée ; il faut une NAT ou des endpoints pour sortir |
| code | zip ou **image de conteneur** ; **layers** pour partager des bibliothèques |
| URL | **function URL** pour un point d'accès HTTPS simple sans API Gateway |

## API Gateway

| Type | Pour |
| --- | --- |
| **HTTP API** | la plupart des API : simple, rapide, moins chère, JWT |
| **REST API** | fonctions avancées : clés d'API et plans d'usage, cache, transformations, WAF, endpoints privés |
| **WebSocket API** | temps réel (chat, notifications) |

Protection : **throttling** (requêtes par seconde), authentification par IAM, **Cognito** ou un **authorizer Lambda**, et WAF devant les REST APIs.

## Les autres options

- **Step Functions** : workflows avec étapes, nouvelles tentatives, attente humaine ; mode **Express** pour les flux courts et nombreux.
- **App Runner** : déployer un conteneur web sans rien configurer (load balancer, TLS et scaling inclus).
- **Elastic Beanstalk** : une plateforme qui déploie une appli sur EC2 avec load balancer et Auto Scaling, en gardant l'accès aux ressources.
- **AWS Batch** : des files de tâches de calcul longues, sur EC2 ou Fargate, éventuellement en Spot.

> **À retenir.** Plus on monte (EC2, conteneurs sur EC2, Fargate, Lambda), moins on gère et plus on paie à l'usage. ECS est simple et propre à AWS, EKS est Kubernetes standard ; Fargate supprime les nœuds. Lambda : 15 minutes, 10 Go, concurrence limitée, démarrage à froid réduit par la provisioned concurrency. API Gateway expose et protège les API, Step Functions orchestre.
