---
title: Load balancers et Auto Scaling
chapter: 5
order: 1
duration: 12
tags:
- AWS SAA
- ELB
- Auto Scaling
cards:
- q: Différence entre ALB et NLB ?
  a: 'L''**ALB** (Application Load Balancer) travaille en HTTP/HTTPS (couche 7) : routage par chemin, nom d''hôte, en-tête, WebSocket, gRPC. Le **NLB** (Network Load Balancer) travaille en TCP/UDP (couche 4) : millions de requêtes, latence très faible, **IP fixe** par AZ, garde l''IP du client.'
- q: À quoi sert un Gateway Load Balancer ?
  a: À faire passer le trafic par des **appliances réseau** (pare-feu, IDS) de façon transparente, en répartissant la charge entre elles (protocole GENEVE).
- q: Qu'est-ce qu'un groupe cible (target group) et un health check ?
  a: Le **groupe cible** est la liste des destinations (instances, IP, Lambda) d'un load balancer. Le **health check** interroge régulièrement chaque cible ; une cible en échec ne reçoit plus de trafic.
- q: Quelles sont les trois valeurs d'un Auto Scaling group ?
  a: '**min**, **max** et **desired** (souhaitée). Le groupe garde toujours entre min et max instances, et remplace automatiquement celles qui tombent en panne.'
- q: Quelles politiques de scaling existent ?
  a: '**target tracking** (garder une métrique à une cible, par exemple 50 % de CPU : le plus simple), **step scaling** (paliers selon une alarme), **scheduled** (à heure fixe) et **predictive** (anticipe à partir de l''historique).'
- q: Qu'est-ce que le connection draining (deregistration delay) ?
  a: Le délai pendant lequel une cible retirée du load balancer **termine ses requêtes en cours** sans en recevoir de nouvelles (300 s par défaut). Évite de couper des utilisateurs lors d'un scale-in ou d'un déploiement.
quiz:
- q: Un client doit autoriser ton service dans son pare-feu par adresse IP fixe. Quel load balancer ?
  options:
  - ALB
  - NLB avec une Elastic IP par AZ
  - Classic Load Balancer
  - CloudFront
  answer: 1
  explain: L'ALB change d'IP ; le NLB peut avoir une IP statique par AZ. (Global Accelerator donne aussi deux IP fixes mondiales.)
- q: Le trafic monte chaque lundi à 8 h et l'application met 5 minutes à démarrer. Quelle politique ajoutes-tu ?
  options:
  - Une politique planifiée (ou prédictive) avant 8 h
  - Réduire le max
  - Supprimer les health checks
  - Un NLB
  answer: 0
  explain: Une politique réactive arriverait trop tard ; on augmente la capacité avant le pic connu.
- q: '`/api/*` doit aller vers un service et `/images/*` vers un autre, derrière le même nom de domaine. Que choisis-tu ?'
  options:
  - Deux NLB
  - Un ALB avec des règles par chemin vers deux groupes cibles
  - Route 53 seul
  - Un Gateway Load Balancer
  answer: 1
  explain: Le routage par chemin est une fonction de couche 7, donc de l'ALB.
level: intermédiaire
---

Une seule instance est un point de panne unique et ne suit pas la charge. On met donc un **load balancer** devant plusieurs instances réparties sur plusieurs AZ, et un **Auto Scaling group** qui ajuste leur nombre. Ce duo est au cœur du domaine « architectures résilientes » de l'examen. La fiche Réseaux sur le load balancing explique les principes ; celle-ci donne les choix propres à AWS.

> **Les outils cités dans cette fiche.**
> - **ELB** (Elastic Load Balancing) : la famille des load balancers managés d'AWS : **ALB**, **NLB**, **GWLB**.
> - **groupe cible** (target group) : l'ensemble des destinations d'un load balancer, avec son health check.
> - **Auto Scaling group** (ASG) : un groupe d'instances dont AWS maintient le nombre et qu'il ajuste à la charge.
> - **launch template** : le modèle (AMI, type, réseau, user data, rôle) utilisé pour créer chaque instance du groupe.
> - **ACM** (AWS Certificate Manager) : fournit et renouvelle gratuitement les certificats TLS utilisés par les load balancers et CloudFront.
> - **CloudWatch** : le service de métriques et d'alarmes d'AWS (fiche Observabilité).
> - **AZ** : une zone de disponibilité : un ou plusieurs datacenters indépendants dans une région.
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **HTTPS** : HTTP chiffré par TLS.
> - **TCP** : le protocole de transport fiable : connexion établie, données remises dans l'ordre et sans perte.
> - **UDP** : le protocole de transport sans connexion, rapide mais sans garantie de livraison (DNS, vidéo, VXLAN).
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.
> - **OIDC** : OpenID Connect, le standard de connexion par un fournisseur d'identité, qui délivre des jetons signés.
> - **EC2** : le service de machines virtuelles d'AWS.

## Comprendre : l'architecture de base

<!-- schema:asg -->
<figure class="diagram"><svg viewBox="0 0 680 340" role="img" aria-label="L&#x27;architecture de base : ALB et Auto Scaling" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="270" y="14" width="140" height="36" rx="9"/></g><text x="340.0" y="37.0" class="dg-t" text-anchor="middle" style="--d:0">Internet</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="200" y="78" width="280" height="50" rx="9"/></g><text x="340.0" y="100.0" class="dg-t" text-anchor="middle" style="--d:1">ALB</text><text x="340.0" y="118.0" class="dg-s" text-anchor="middle" style="--d:1">sous-réseaux publics, AZ a + AZ b</text><path d="M340 50 L340 76" class="dg-l a" marker-end="url(#g3-a)"/><rect x="14" y="176" width="652" height="150" rx="12" class="dg-zone dg-zc"/><path d="M340 128 L340 152" class="dg-l c"/><path d="M105 152 L585 152" class="dg-l c"/><text x="350" y="146" class="dg-s" text-anchor="start">health checks /health</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="40" y="206" width="130" height="48" rx="9"/></g><text x="105.0" y="227.0" class="dg-t" text-anchor="middle" style="--d:2">instance</text><text x="105.0" y="245.0" class="dg-s" text-anchor="middle" style="--d:2">AZ a · privé</text><path d="M105 152 L105 204" class="dg-l c" marker-end="url(#g3-c)"/><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="200" y="206" width="130" height="48" rx="9"/></g><text x="265.0" y="227.0" class="dg-t" text-anchor="middle" style="--d:3">instance</text><text x="265.0" y="245.0" class="dg-s" text-anchor="middle" style="--d:3">AZ a · privé</text><path d="M265 152 L265 204" class="dg-l c" marker-end="url(#g3-c)"/><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="360" y="206" width="130" height="48" rx="9"/></g><text x="425.0" y="227.0" class="dg-t" text-anchor="middle" style="--d:4">instance</text><text x="425.0" y="245.0" class="dg-s" text-anchor="middle" style="--d:4">AZ b · privé</text><path d="M425 152 L425 204" class="dg-l c" marker-end="url(#g3-c)"/><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="520" y="206" width="130" height="48" rx="9"/></g><text x="585.0" y="227.0" class="dg-t" text-anchor="middle" style="--d:5">instance</text><text x="585.0" y="245.0" class="dg-s" text-anchor="middle" style="--d:5">AZ b · privé</text><path d="M585 152 L585 204" class="dg-l c" marker-end="url(#g3-c)"/><text x="340" y="286" class="dg-ct" text-anchor="middle" style="--d:6">groupe cible géré par un Auto Scaling group : min 2, desired 4, max 10</text><text x="340" y="306" class="dg-s" text-anchor="middle" style="--d:6">launch template : AMI, m7g.large, rôle IAM, user data</text></svg><figcaption>Une instance qui échoue au health check est retirée puis remplacée ; l&#x27;ASG garde le nombre voulu.</figcaption></figure>
<!-- /schema:asg -->

Les instances n'ont pas d'IP publique : seul le load balancer est exposé. Leur security group n'accepte que le security group du load balancer.

## Choisir son load balancer

| | ALB | NLB | GWLB |
| --- | --- | --- | --- |
| couche | 7 (HTTP, HTTPS, gRPC, WebSocket) | 4 (TCP, UDP, TLS) | 3 (paquets IP) |
| routage | chemin, hôte, en-têtes, méthode, query string | port | vers des appliances |
| IP fixe | non | oui, une par AZ | — |
| IP du client | dans `X-Forwarded-For` | conservée | conservée |
| cibles | instances, IP, Lambda | instances, IP, ALB | appliances |
| cas typique | applis web, microservices | très haut débit, protocole non HTTP, IP fixe | pare-feu tiers centralisé |

Le **Classic Load Balancer** est l'ancienne génération : on ne le choisit plus.

Fonctions à connaître :

- **terminaison TLS** avec un certificat ACM ; **SNI** pour plusieurs domaines sur le même ALB ;
- **sticky sessions** (cookie) pour garder un utilisateur sur la même cible ;
- **cross-zone load balancing** : répartir également entre toutes les cibles de toutes les AZ (actif par défaut sur l'ALB) ;
- l'ALB peut **authentifier** les utilisateurs (Cognito ou OIDC) avant de transmettre.

## Auto Scaling

Un ASG fait deux choses :

1. **maintenir** le nombre d'instances : une instance en échec (health check EC2 ou ELB) est remplacée ;
2. **ajuster** ce nombre entre `min` et `max` selon des politiques.

| Politique | Fonctionnement | Quand |
| --- | --- | --- |
| **target tracking** | garde une métrique à une valeur (CPU 50 %, requêtes par cible) | par défaut |
| **step scaling** | ajoute ou retire N instances selon des paliers d'alarme | réglage fin |
| **scheduled** | change min, max, desired à heure fixe | pics connus |
| **predictive** | prévoit à partir de deux semaines d'historique | charge cyclique |

Réglages importants :

- **health check ELB** sur le groupe : sinon une instance dont l'appli ne répond plus mais dont la VM tourne n'est pas remplacée ;
- **warm-up** et **cooldown** : laisser le temps à une nouvelle instance de démarrer avant de mesurer de nouveau ;
- **instance refresh** : remplacer progressivement toutes les instances après un changement de launch template (nouvelle AMI) ;
- **lifecycle hooks** : exécuter une action (vider un cache, envoyer des logs) au lancement ou avant la suppression d'une instance ;
- **mixed instances policy** : mélanger plusieurs types d'instances et du **Spot** dans le même groupe, pour réduire les coûts.

## Les pièges

- Démarrage lent : si une instance met 10 minutes à être prête, le scaling réactif arrive trop tard. Réponses : AMI préparée, politique planifiée ou prédictive, **warm pool** (instances pré-initialisées et arrêtées).
- Sessions en mémoire : une instance supprimée emporte les sessions. On les stocke dans ElastiCache ou DynamoDB, et l'application devient **sans état**.
- `min = 1` dans une seule AZ : ce n'est pas de la haute disponibilité.

> **À retenir.** ALB pour HTTP et le routage par chemin ou par hôte, NLB pour TCP/UDP, l'IP fixe et la performance, GWLB pour les appliances. Un ASG remplace les instances malades (health check ELB) et suit la charge, en target tracking par défaut, en planifié pour les pics connus. Des instances sans état, sur au moins deux AZ, derrière le load balancer.
