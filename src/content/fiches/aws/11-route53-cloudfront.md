---
title: Route 53, CloudFront et Global Accelerator
chapter: 11
order: 1
duration: 12
tags:
- AWS SAA
- Route 53
- CloudFront
cards:
- q: Différence entre un enregistrement CNAME et un alias Route 53 ?
  a: 'Un **CNAME** pointe vers un autre nom et est interdit à l''**apex** du domaine (`shop.fr`). Un **alias** est propre à Route 53 : il pointe vers une ressource AWS (ALB, CloudFront, S3, API Gateway), fonctionne à l''apex et ses requêtes sont gratuites.'
- q: Quelles politiques de routage Route 53 existent ?
  a: '**simple**, **weighted** (pourcentages), **latency** (région la plus rapide), **failover** (principal/secours selon un health check), **geolocation** (pays ou continent de l''utilisateur), **geoproximity** (distance, avec biais), **multivalue** (plusieurs IP saines) et **IP-based** (plage du client).'
- q: Comment Route 53 détecte-t-il qu'un site est en panne ?
  a: Avec des **health checks** qui interrogent un point de terminaison (HTTP, HTTPS, TCP) depuis plusieurs régions, ou qui suivent une **alarme CloudWatch** (utile pour des ressources privées). Les politiques failover, latency, weighted… écartent les cibles en échec.
- q: Qu'est-ce qu'une OAC sur CloudFront ?
  a: '**Origin Access Control** : CloudFront signe ses requêtes vers le bucket S3, et la politique du bucket n''autorise que la distribution. Le bucket reste privé ; personne ne peut le lire en contournant CloudFront. (Remplace l''ancienne OAI.)'
- q: Comment vider le cache CloudFront après un déploiement ?
  a: 'Une **invalidation** (`/*` ou des chemins précis), facturée au-delà d''un quota gratuit. Mieux : des noms de fichiers **versionnés** (`app.3f2a.js`) qui changent à chaque version, avec un long TTL.'
- q: Différence entre CloudFront et Global Accelerator ?
  a: '**CloudFront** est un CDN : il **met en cache** du contenu HTTP au plus près des utilisateurs. **Global Accelerator** ne cache rien : il donne **deux IP anycast fixes** et fait entrer le trafic TCP/UDP sur le réseau d''AWS au plus près, avec bascule entre régions en quelques secondes.'
quiz:
- q: Tu veux envoyer 10 % des utilisateurs vers la nouvelle version d'une application. Quelle politique Route 53 ?
  options:
  - latency
  - weighted
  - geolocation
  - failover
  answer: 1
  explain: 'Deux enregistrements avec des poids 90 et 10. (Le TTL DNS ralentit les changements : un ALB à poids est plus réactif.)'
- q: Un site statique sur S3 doit être servi en HTTPS avec un domaine personnalisé, et le bucket ne doit pas être public. Solution ?
  options:
  - Rendre le bucket public avec l'hébergement de site
  - CloudFront avec une OAC et un certificat ACM en us-east-1
  - Un NLB devant S3
  - Route 53 seul
  answer: 1
  explain: CloudFront termine HTTPS (certificat ACM obligatoirement en us-east-1) et l'OAC garde le bucket privé.
- q: Un jeu en ligne en UDP a des joueurs dans le monde entier et doit basculer vite entre deux régions. Quel service ?
  options:
  - CloudFront
  - Global Accelerator
  - Route 53 geolocation
  - S3 Transfer Acceleration
  answer: 1
  explain: 'UDP, IP fixes, bascule rapide sans attendre l''expiration du cache DNS : c''est Global Accelerator.'
level: intermédiaire
---

Trois services placent tes applications près des utilisateurs du monde entier et les rendent résilientes à l'échelle d'une région : **Route 53** pour le DNS, **CloudFront** pour la diffusion de contenu et **Global Accelerator** pour le réseau. La fiche Réseaux sur le DNS explique le fonctionnement général des noms de domaine ; celle-ci se concentre sur ce qu'AWS ajoute.

> **Les outils cités dans cette fiche.**
> - **Route 53** : le service DNS d'AWS (enregistrement de domaines, zones, routage intelligent, health checks).
> - **zone hébergée** : l'ensemble des enregistrements d'un domaine ; **publique** (Internet) ou **privée** (visible dans des VPC).
> - **TTL** : la durée pendant laquelle une réponse DNS est gardée en cache par les clients.
> - **CloudFront** : le CDN (Content Delivery Network) d'AWS, plus de 600 points de présence.
> - **origine** : la source du contenu derrière CloudFront (bucket S3, ALB, serveur quelconque).
> - **Global Accelerator** : deux IP anycast fixes qui font entrer le trafic sur le réseau d'AWS au plus près de l'utilisateur.
> - **anycast** : la même adresse IP annoncée depuis de nombreux sites ; le réseau envoie chaque utilisateur au plus proche.
> - **Lambda@Edge** et **CloudFront Functions** : du code exécuté dans les points de présence pour modifier requêtes et réponses.
> - **EC2** : le service de machines virtuelles d'AWS.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **HTTPS** : HTTP chiffré par TLS.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **WAF** : un pare-feu applicatif qui filtre les requêtes web malveillantes.
> - **latence** : le délai entre une demande et sa réponse.
> - **NLB** : Network Load Balancer : le load balancer TCP/UDP d'AWS.

## Route 53

### Les enregistrements

| Type | Rôle |
| --- | --- |
| A / AAAA | nom vers IPv4 / IPv6 |
| CNAME | nom vers un autre nom (pas à l'apex) |
| **alias** (propre à AWS) | nom vers une ressource AWS, à l'apex aussi, sans frais de requête |
| MX, TXT, NS, SOA, CAA | messagerie, vérifications, délégation, autorité de certification |

### Les politiques de routage

| Politique | Répond | Usage |
| --- | --- | --- |
| simple | une ou plusieurs valeurs, sans contrôle de santé | cas de base |
| **weighted** | selon des poids | canary, migration progressive |
| **latency** | la région la plus rapide pour ce client | applis multi-région |
| **failover** | le principal, sinon le secours | reprise active-passive |
| **geolocation** | selon le pays ou continent | contenu localisé, obligations légales |
| geoproximity | selon la distance, avec un biais réglable | déplacer du trafic entre régions |
| multivalue | jusqu'à 8 réponses saines au hasard | répartition simple côté DNS |
| IP-based | selon la plage IP du client | réseaux d'opérateurs connus |

Une politique geolocation a besoin d'un enregistrement **par défaut**, sinon les utilisateurs hors des zones listées n'obtiennent aucune réponse.

### Health checks

Ils testent un point de terminaison depuis plusieurs régions, ou combinent d'autres health checks, ou suivent une **alarme CloudWatch** (pour une ressource privée qu'Internet ne peut pas joindre). Un TTL court (60 s) accélère la bascule, au prix de plus de requêtes.

### Zones privées et résolution hybride

Une **zone privée** associée à un VPC résout des noms internes (`db.shop.internal`). **Route 53 Resolver** avec des **endpoints entrants et sortants** relie le DNS du VPC et celui du data center : les serveurs sur site résolvent les noms AWS, et inversement.

## CloudFront

```
Utilisateur Tokyo ─► point de présence Tokyo ── cache ? ── oui ─► réponse en ms
                                                 │ non
                                                 ▼
                                    Regional edge cache ─► origine (S3 Paris, ALB)
```

| Fonction | À retenir |
| --- | --- |
| origines | S3 (avec **OAC**), ALB, EC2, API Gateway, MediaStore, toute URL ; **groupes d'origines** avec bascule |
| comportements | des règles par chemin (`/api/*` sans cache vers l'ALB, `/static/*` en cache vers S3) |
| cache | TTL, **cache policies** (ce qui entre dans la clé de cache), invalidations |
| HTTPS | certificat **ACM en us-east-1**, redirection HTTP vers HTTPS |
| sécurité | WAF, Shield Standard inclus, **restriction géographique**, **URL et cookies signés** pour du contenu privé |
| code en bordure | **CloudFront Functions** (léger : en-têtes, redirections) ; **Lambda@Edge** (plus complet) |

CloudFront réduit la latence, mais aussi la **charge** de l'origine et souvent la **facture** : le transfert de CloudFront vers Internet est moins cher que celui d'EC2 ou de S3 directement.

## Global Accelerator

- **deux IP anycast statiques** pour ton application, quelle que soit la région ;
- le trafic entre sur le réseau privé d'AWS au point le plus proche, puis va vers des ALB, NLB, instances ou Elastic IP dans une ou plusieurs régions ;
- **bascule en quelques secondes** entre régions selon la santé, sans dépendre du cache DNS ;
- pour TCP et UDP : jeux, VoIP, IoT, ou clients qui exigent des IP fixes à autoriser.

## Choisir

```
Nom de domaine, routage selon santé, latence ou pays ..... Route 53
Contenu web et statique, cache, HTTPS, protection ........ CloudFront
IP fixes mondiales, TCP/UDP, bascule rapide .............. Global Accelerator
Envoyer de gros fichiers vers S3 depuis loin ............. S3 Transfer Acceleration
```

> **À retenir.** Route 53 : alias pour les ressources AWS (et l'apex), politiques weighted, latency, failover, geolocation avec health checks, zones privées et Resolver pour l'hybride. CloudFront met en cache au plus près, garde S3 privé avec une OAC, demande un certificat ACM en us-east-1. Global Accelerator donne deux IP fixes et bascule en secondes, sans cache.
