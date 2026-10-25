---
title: 'VPC : sous-réseaux, routage et filtrage'
chapter: 3
order: 1
duration: 14
tags:
- AWS SAA
- VPC
- réseau
cards:
- q: Qu'est-ce qui rend un sous-réseau « public » ?
  a: Sa **table de routage** envoie `0.0.0.0/0` vers une **Internet Gateway**. Un sous-réseau privé n'a pas cette route ; il sort éventuellement par une **NAT Gateway** placée dans un sous-réseau public.
- q: Différence entre un security group et une NACL ?
  a: Le **security group** s'attache à une interface (instance), n'a que des règles d'**autorisation** et est **avec état** (la réponse est autorisée d'office). La **NACL** s'attache à un sous-réseau, a des règles Allow **et** Deny numérotées et est **sans état** (il faut aussi ouvrir le retour, ports éphémères).
- q: Combien d'adresses AWS réserve-t-il dans chaque sous-réseau ?
  a: '**Cinq** : la première (réseau), les trois suivantes (routeur, DNS, réservée) et la dernière. Un `/24` offre donc 251 adresses utilisables.'
- q: À quoi sert un VPC endpoint ?
  a: À joindre un service AWS **sans passer par Internet** ni par une NAT. Endpoint **gateway** (gratuit) pour S3 et DynamoDB ; endpoint **interface** (PrivateLink, payant) pour les autres services.
- q: Différence entre VPC peering et Transit Gateway ?
  a: Le **peering** relie deux VPC en direct, sans transitivité (A-B et B-C ne donnent pas A-C) et sans chevauchement d'adresses. **Transit Gateway** est un routeur central qui relie des dizaines de VPC et de connexions sur site.
- q: Comment relier un data center à AWS ?
  a: '**Site-to-Site VPN** (tunnel IPsec sur Internet, rapide à mettre en place) ou **Direct Connect** (lien privé dédié, débit stable, plusieurs semaines de délai). On combine souvent les deux : Direct Connect principal, VPN de secours.'
- q: Pourquoi une NAT Gateway par AZ ?
  a: Une NAT Gateway vit dans **une** AZ. Si elle tombe, les sous-réseaux privés des autres AZ qui passent par elle perdent Internet. Une par AZ évite ce point unique de panne (et les frais de trafic entre AZ).
quiz:
- q: Des instances dans un sous-réseau privé doivent télécharger des mises à jour sur Internet sans être joignables depuis Internet. Quelle solution ?
  options:
  - Leur donner une IP publique
  - Une NAT Gateway dans un sous-réseau public et une route `0.0.0.0/0` vers elle
  - Une Internet Gateway dans le sous-réseau privé
  - Un VPC peering
  answer: 1
  explain: La NAT ne laisse passer que les connexions initiées de l'intérieur.
- q: Tu dois bloquer une IP précise qui attaque ton application. Quel outil réseau du VPC le permet ?
  options:
  - Le security group
  - La NACL du sous-réseau
  - La table de routage
  - L'Internet Gateway
  answer: 1
  explain: Un security group ne sait qu'autoriser. La NACL accepte des règles Deny (WAF serait aussi une réponse au niveau HTTP).
- q: Des Lambda dans un VPC lisent beaucoup de données S3 et la facture NAT explose. Que fais-tu ?
  options:
  - Plus de NAT Gateways
  - Un VPC endpoint gateway pour S3
  - Sortir les Lambda du VPC sans réfléchir
  - Une Transit Gateway
  answer: 1
  explain: L'endpoint gateway S3 est gratuit et le trafic ne passe plus par la NAT, facturée au Go.
level: intermédiaire
---

Un **VPC** (Virtual Private Cloud) est ton réseau privé dans une région AWS. Tout ce qui a une adresse IP (instances, bases, load balancers, Lambda reliées au réseau) vit dans un VPC. La fiche Réseaux sur l'adressage et le CIDR donne les bases ; celle-ci les applique à AWS, où l'examen pose beaucoup de questions.

> **Les outils cités dans cette fiche.**
> - **VPC** : un réseau virtuel isolé, avec sa plage d'adresses (par exemple `10.0.0.0/16`), dans une région.
> - **sous-réseau** (subnet) : une tranche du VPC, rattachée à **une** AZ.
> - **table de routage** : la liste des routes d'un sous-réseau (« pour aller vers telle plage, passe par tel équipement »).
> - **Internet Gateway** (IGW) : la porte du VPC vers Internet, dans les deux sens.
> - **NAT Gateway** : permet aux machines privées de **sortir** vers Internet sans être joignables de l'extérieur.
> - **security group** : un pare-feu attaché à chaque interface réseau. **NACL** (Network ACL) : un pare-feu attaché au sous-réseau.
> - **VPC endpoint** et **PrivateLink** : un accès privé aux services AWS ou à ceux d'un autre compte, sans passer par Internet.
> - **Transit Gateway** : un routeur central régional pour relier de nombreux VPC et réseaux d'entreprise.
> - **Direct Connect** : un lien physique privé entre ton data center et AWS.
> - **load balancer** : un répartiteur de charge qui distribue les requêtes entre plusieurs serveurs.
> - **CIDR** : la notation d'une plage d'adresses : 10.0.0.0/24 = 256 adresses de 10.0.0.0 à 10.0.0.255.
> - **ALB** : Application Load Balancer : le load balancer HTTP d'AWS.
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **SQS** : le service de files de messages d'AWS.
> - **ECR** : le registre d'images de conteneurs d'AWS.
> - **latence** : le délai entre une demande et sa réponse.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.

## Comprendre : un VPC typique

<!-- schema:vpc -->
<figure class="diagram"><svg viewBox="0 0 680 360" role="img" aria-label="Un VPC typique sur deux zones" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="652" height="334" rx="12" class="dg-zone dg-zc"/><text x="26" y="32" class="dg-zl" text-anchor="start">VPC 10.0.0.0/16 · eu-west-3</text><g class="dg-box dg-a dg-pop" style="--d:0"><rect x="290" y="26" width="100" height="36" rx="9"/></g><text x="340.0" y="49.0" class="dg-s" text-anchor="middle" style="--d:0">Internet Gateway</text><rect x="30" y="80" width="306" height="254" rx="12" class="dg-zone "/><text x="42" y="98" class="dg-zl" text-anchor="start">AZ a</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="46" y="106" width="274" height="62" rx="9"/></g><text x="183.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:1">public · 10.0.0.0/24</text><text x="183.0" y="145.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="183.0" dy="0">ALB, NAT Gateway</tspan><tspan x="183.0" dy="14">0.0.0.0/0 → IGW</tspan></text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="46" y="180" width="274" height="62" rx="9"/></g><text x="183.0" y="201.0" class="dg-t" text-anchor="middle" style="--d:2">privé · 10.0.10.0/24</text><text x="183.0" y="219.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="183.0" dy="0">instances applicatives</tspan><tspan x="183.0" dy="14">0.0.0.0/0 → NAT</tspan></text><g class="dg-box dg-pop" style="--d:3"><rect x="46" y="254" width="274" height="62" rx="9"/></g><text x="183.0" y="275.0" class="dg-t" text-anchor="middle" style="--d:3">données · 10.0.20.0/24</text><text x="183.0" y="293.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="183.0" dy="0">RDS</tspan><tspan x="183.0" dy="14">pas de route Internet</tspan></text><path d="M340 62 L340 94 L183 94 L183 104" class="dg-l a" marker-end="url(#g2-a)" style="--d:1"/><rect x="344" y="80" width="306" height="254" rx="12" class="dg-zone "/><text x="356" y="98" class="dg-zl" text-anchor="start">AZ b</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="360" y="106" width="274" height="62" rx="9"/></g><text x="497.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:1">public · 10.0.1.0/24</text><text x="497.0" y="145.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="497.0" dy="0">ALB, NAT Gateway</tspan><tspan x="497.0" dy="14">0.0.0.0/0 → IGW</tspan></text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="360" y="180" width="274" height="62" rx="9"/></g><text x="497.0" y="201.0" class="dg-t" text-anchor="middle" style="--d:2">privé · 10.0.11.0/24</text><text x="497.0" y="219.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="497.0" dy="0">instances applicatives</tspan><tspan x="497.0" dy="14">0.0.0.0/0 → NAT</tspan></text><g class="dg-box dg-pop" style="--d:3"><rect x="360" y="254" width="274" height="62" rx="9"/></g><text x="497.0" y="275.0" class="dg-t" text-anchor="middle" style="--d:3">données · 10.0.21.0/24</text><text x="497.0" y="293.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="497.0" dy="0">RDS</tspan><tspan x="497.0" dy="14">pas de route Internet</tspan></text><path d="M340 62 L340 94 L497 94 L497 104" class="dg-l a" marker-end="url(#g2-a)" style="--d:1"/></svg><figcaption>Seuls les sous-réseaux publics ont une route vers l&#x27;IGW ; le privé sort par la NAT, les données ne sortent pas.</figcaption></figure>
<!-- /schema:vpc -->

Un sous-réseau n'est ni public ni privé par nature : c'est **sa table de routage** qui décide. Une instance d'un sous-réseau public a aussi besoin d'une **IP publique** (ou d'une Elastic IP) pour être jointe.

## Choisir ses plages

- Un VPC accepte de `/16` à `/28`. Prends large (un `/16`) : on ne peut pas réduire, seulement ajouter des plages.
- Évite les plages déjà utilisées dans l'entreprise ou d'autres VPC : deux réseaux qui se chevauchent ne peuvent **pas** être reliés.
- AWS réserve **5 adresses** par sous-réseau.

## Filtrer : security groups et NACL

| | Security group | NACL |
| --- | --- | --- |
| s'applique à | une interface (instance, base, ALB) | un sous-réseau entier |
| règles | Allow seulement | Allow et Deny, numérotées, la première qui correspond gagne |
| état | **avec état** : la réponse passe d'office | **sans état** : ouvrir aussi les ports éphémères (1024-65535) au retour |
| défaut | tout refusé en entrée, tout permis en sortie | NACL par défaut : tout permis |
| source possible | IP, plage, **autre security group** | IP ou plage seulement |

La force des security groups : on peut écrire « la base accepte le port 5432 depuis le security group de l'application », sans aucune IP. On s'en sert pour presque tout ; la NACL sert de filet (bloquer une plage d'IP, isoler un sous-réseau).

## Joindre les services AWS en privé

Sans endpoint, une instance privée qui parle à S3 passe par la NAT Gateway, facturée au Go.

| Endpoint | Services | Coût |
| --- | --- | --- |
| **gateway** | S3, DynamoDB | gratuit, une entrée dans la table de routage |
| **interface** (PrivateLink) | presque tous les autres (SQS, Secrets Manager, ECR…) | à l'heure et au Go, une interface dans tes sous-réseaux |

PrivateLink sert aussi à **exposer ton propre service** à d'autres comptes sans relier les réseaux.

## Relier des VPC entre eux

| Solution | Quand |
| --- | --- |
| **VPC peering** | quelques VPC ; pas de transitivité, pas de chevauchement |
| **Transit Gateway** | beaucoup de VPC, plusieurs comptes, VPN et Direct Connect au même endroit |
| **PrivateLink** | exposer un seul service, pas tout le réseau |

## Relier son data center

| Solution | Mise en place | Débit et latence | Chiffré |
| --- | --- | --- | --- |
| **Site-to-Site VPN** | minutes | variable (Internet) | oui (IPsec) |
| **Direct Connect** | semaines | stable, jusqu'à 100 Gbit/s | non par défaut (ajouter MACsec ou un VPN par-dessus) |

Pour la résilience : deux connexions Direct Connect sur deux sites, ou Direct Connect + VPN de secours.

## Voir ce qui passe

Les **VPC Flow Logs** enregistrent chaque flux accepté ou refusé (IP, ports, action) vers CloudWatch Logs ou S3. C'est le premier outil pour comprendre un « ça ne se connecte pas » : un `REJECT` désigne un security group ou une NACL. **Reachability Analyzer** vérifie, sans envoyer de paquet, si un chemin est possible entre deux ressources.

> **À retenir.** C'est la table de routage qui rend un sous-réseau public (route vers l'IGW) ou privé (route vers une NAT, ou aucune). Security group : avec état, Allow seulement, s'appuie sur d'autres groupes. NACL : sans état, Allow et Deny, au niveau du sous-réseau. Endpoint gateway gratuit pour S3 et DynamoDB, Transit Gateway pour beaucoup de VPC, Direct Connect pour un lien privé stable.
