---
title: Pare-feu et NAT
chapter: 6
order: 1
duration: 10
level: intermédiaire
tags:
- fondamentaux
cards:
- q: Qu'est-ce qu'un pare-feu *stateful* ?
  a: 'Il suit l''**état des connexions** : si une connexion sortante est autorisée, les réponses entrantes passent automatiquement, sans règle dédiée.'
- q: Différence entre SNAT et DNAT ?
  a: '**SNAT** modifie l''adresse **source** (des machines privées sortent sur Internet avec une IP publique). **DNAT** modifie l''adresse **destination** (redirection de port vers un serveur interne).'
- q: Différence entre un security group et une Network ACL sur AWS ?
  a: Le **security group** est stateful, attaché à une interface, avec des règles d'autorisation uniquement. La **NACL** est stateless, attachée à un sous-réseau, et accepte des règles de refus.
- q: Quel outil remplace iptables sur les distributions récentes ?
  a: '**nftables** (`nft`), souvent via une surcouche : `firewalld` (RHEL) ou `ufw` (Ubuntu).'
- q: Qu'est-ce qu'un NAT Gateway dans un VPC ?
  a: Un service qui permet aux machines des sous-réseaux **privés** de sortir sur Internet (mises à jour, API) sans être joignables depuis l'extérieur.
- q: Différence entre `drop` et `reject` côté client ?
  a: '`drop` : le paquet est jeté sans réponse, le client attend jusqu''au **timeout**. `reject` : le pare-feu répond, le client voit un **refus** immédiat.'
- q: Pourquoi une adresse privée ne peut-elle pas sortir sur Internet sans NAT ?
  a: 'Les routeurs d''Internet ne routent pas les plages privées : la réponse ne pourrait jamais revenir. Le SNAT remplace l''IP source par une IP publique.'
- q: Qu'est-ce que le conntrack ?
  a: La table du noyau Linux qui mémorise les connexions en cours. Elle permet le filtrage stateful et le NAT (pour traduire les réponses).
quiz:
- q: Tu ouvres le port 5432 en entrée dans un security group, mais rien en sortie. Les réponses de la base passent-elles ?
  options:
  - Non, il faut une règle sortante
  - Oui, le security group est stateful
  - Seulement en UDP
  - Seulement si la NACL l'autorise aussi en entrée
  answer: 1
  explain: 'Attention en revanche aux NACL, qui sont stateless : il faut y autoriser les ports éphémères (1024-65535) pour le retour.'
- q: Des instances dans un sous-réseau privé n'arrivent pas à télécharger des paquets. Que vérifier en premier ?
  options:
  - Que la table de routage du sous-réseau envoie `0.0.0.0/0` vers un NAT Gateway
  - Que les instances ont une IP publique
  - Le DNS public
  - Le MTU
  answer: 0
  explain: Sans route par défaut vers un NAT (ou un proxy), un sous-réseau privé n'a aucun accès à Internet.
- q: Sur AWS, ta NACL autorise l'entrée TCP 443 et la sortie TCP 443. Les clients HTTPS n'obtiennent jamais de réponse. Pourquoi ?
  options:
  - Le security group bloque
  - Les réponses partent vers les ports éphémères des clients, non autorisés en sortie
  - Il faut ouvrir le port 80
  - La NACL est stateful
  answer: 1
  explain: 'Une NACL est stateless : la réponse va du port 443 du serveur vers un port éphémère du client (1024-65535), qu''il faut autoriser en sortie.'
- q: Une VM dans un sous-réseau privé n'arrive pas à faire `apt update`. Elle n'a pas d'IP publique. Que vérifier ?
  options:
  - Le security group en entrée
  - La route 0.0.0.0/0 du sous-réseau vers une NAT Gateway
  - Le DNS du VPC
  - La clé SSH
  answer: 1
  explain: Sans IP publique, la sortie vers Internet passe forcément par un NAT. La route par défaut du sous-réseau doit y mener.
- q: Un partenaire doit autoriser ton cluster à appeler son API. Quelle IP lui donner ?
  options:
  - Les IP des pods
  - L'IP du load balancer d'entrée
  - L'IP publique de la NAT Gateway par laquelle le cluster sort
  - L'IP du serveur DNS
  answer: 2
  explain: Il voit l'IP source après SNAT, c'est-à-dire celle du NAT de sortie.
---

Un **pare-feu** décide quels paquets ont le droit de passer. Le **NAT** réécrit les adresses des paquets au passage. Les deux vivent souvent dans le même équipement (ta box, un routeur, le noyau Linux, une passerelle cloud) et sont derrière une bonne partie des « ça ne marche pas, mais seulement depuis là ».

> **Les outils et sigles cités dans cette fiche.**
> - **netfilter** : la partie du noyau Linux qui filtre et réécrit les paquets. On ne le manipule jamais directement, mais via **nftables** (l'outil moderne, commande `nft`) ou **iptables** (l'ancien, encore très présent).
> - **ufw** (Ubuntu) et **firewalld** (Red Hat, Fedora) : des surcouches plus simples qui écrivent les règles netfilter à ta place.
> - **conntrack** : la table où le noyau mémorise les connexions en cours ; c'est elle qui rend un pare-feu « stateful ».
> - **ICMP** : le protocole des messages de contrôle réseau, utilisé par `ping` (`echo-request`) et pour signaler des erreurs.
> - **Security group** et **NACL** (Network Access Control List) : les deux pare-feu d'AWS, le premier attaché à une machine (stateful), le second à un sous-réseau (stateless).
> - **Internet Gateway** et **NAT Gateway** : dans un réseau cloud (VPC), la porte vers Internet pour les sous-réseaux publics, et le service de NAT qui permet aux sous-réseaux privés de sortir.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **ACL** : une liste de contrôle d'accès : qui a le droit de faire quoi sur une ressource.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.

## Le pare-feu : un vigile avec une liste

Un pare-feu examine chaque paquet et le compare à une liste de **règles**, dans l'ordre. Chaque règle décrit des critères (IP source, IP destination, protocole, port, interface) et une action :

- **accept** : le paquet passe ;
- **drop** : il est jeté en silence (le client attendra jusqu'au **timeout**) ;
- **reject** : il est refusé avec une réponse (le client voit un **refus** immédiat).

Si aucune règle ne correspond, c'est la **politique par défaut** qui s'applique. Une bonne pratique : tout refuser par défaut et n'ouvrir que le nécessaire (*default deny*).

On distingue aussi le sens du trafic : **entrant** (ingress, vers la machine), **sortant** (egress, depuis la machine), et **transféré** (forward, qui traverse la machine, comme sur un routeur ou un hôte Docker).

## Stateful ou stateless : la question du retour

Une connexion, c'est un aller **et** un retour. Quand ton serveur appelle une API sur le port 443, la réponse revient vers un **port éphémère** du serveur (par exemple 51 234). Il faut donc que le retour soit autorisé aussi.

- Un pare-feu **stateful** (à états) se souvient des connexions qu'il a vues passer (le *conntrack* sous Linux). Le retour d'une connexion autorisée passe **automatiquement**. C'est le cas de la plupart des pare-feu modernes.
- Un pare-feu **stateless** examine chaque paquet isolément. Il faut écrire une règle pour l'aller **et** une pour le retour, souvent en ouvrant toute la plage des ports éphémères.

| | Stateful | Stateless |
| --- | --- | --- |
| Retour des connexions | automatique | à autoriser explicitement |
| Exemples | security group AWS, nftables avec `ct state`, firewalld, ufw | NACL AWS, ACL de routeur |

Le piège classique sur AWS : une NACL qui autorise l'entrée sur 443 mais pas la **sortie** vers les ports 1024-65535. Les requêtes arrivent, les réponses sont bloquées.

## nftables : refus par défaut, ligne par ligne

Sous Linux, le filtrage est fait par le noyau (**netfilter**). On le configure avec `nftables` (le moderne), `iptables` (l'ancien), ou des surcouches plus simples comme `ufw` et `firewalld`.

```
table inet filter {
  chain input {                                   # trafic entrant vers la machine
    type filter hook input priority 0; policy drop;   # par défaut : jeter
    ct state established,related accept           # les retours de connexions connues
    iif lo accept                                 # la machine se parle à elle-même
    tcp dport { 22, 443 } accept                  # SSH et HTTPS ouverts
    icmp type echo-request limit rate 5/second accept  # ping, limité
  }
}
```

Sans la ligne `ct state established,related accept`, la machine ne recevrait même pas les réponses à ses propres requêtes sortantes : c'est elle qui rend ce pare-feu « stateful ».

```bash
nft list ruleset                   # toutes les règles nftables
firewall-cmd --list-all            # avec firewalld
ufw status verbose                 # avec ufw
```

## Le NAT : réécrire les adresses

Les adresses privées (`10.x`, `172.16-31.x`, `192.168.x`) ne sont **pas routables** sur Internet : un paquet qui part avec une telle adresse source ne trouverait jamais le chemin du retour. Le **NAT** (Network Address Translation) résout ça en réécrivant les adresses au passage.

**SNAT (le NAT source), pour sortir.** Ta box ou une NAT Gateway remplace l'IP privée source par son IP **publique**, et note la correspondance dans une table. Quand la réponse revient, elle fait la traduction inverse. C'est ainsi que tous les appareils d'une maison, ou toutes les VM privées d'un VPC, sortent sur Internet avec une seule IP publique. Le *masquerading* est un SNAT qui prend automatiquement l'IP de l'interface de sortie.

**DNAT (le NAT destination), pour entrer.** On réécrit l'IP et le port de **destination** pour envoyer le trafic vers une machine interne. C'est la « redirection de port » de la box, le `-p 8080:80` de Docker, ou ce que fait un Service Kubernetes.

```
SNAT  pod / VM privée 10.10.16.11 ──► NAT ──► Internet voit 35.180.x.x
DNAT  Internet → 35.180.x.x:443   ──► NAT ──► 10.10.16.11:8080
```

<!-- schema:nat -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="SNAT et DNAT" style="--minw:560px"><defs><marker id="g14-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g14-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g14-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g14-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="170" y="22" class="dg-ct" text-anchor="middle">SNAT : sortir vers Internet</text><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="60" width="120" height="52" rx="9"/></g><text x="74.0" y="83.0" class="dg-t" text-anchor="middle" style="--d:0">serveur privé</text><text x="74.0" y="101.0" class="dg-s" text-anchor="middle" style="--d:0">10.0.1.5</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="170" y="60" width="110" height="52" rx="9"/></g><text x="225.0" y="83.0" class="dg-t" text-anchor="middle" style="--d:1">NAT</text><text x="225.0" y="101.0" class="dg-s" text-anchor="middle" style="--d:1">203.0.113.7</text><g class="dg-box dg-ghost dg-pop" style="--d:2"><rect x="14" y="160" width="266" height="52" rx="9"/></g><text x="147.0" y="183.0" class="dg-s" text-anchor="middle" style="--d:2">src 10.0.1.5 → src 203.0.113.7</text><text x="147.0" y="201.0" class="dg-s" text-anchor="middle" style="--d:2">la source est réécrite</text><path d="M134 86 L168 86" class="dg-l c" marker-end="url(#g14-c)"/><path d="M280 86 L318 86" class="dg-l c flow" marker-end="url(#g14-c)"/><text x="322" y="90" class="dg-s" text-anchor="start">Internet</text><line x1="340" y1="30" x2="340" y2="230" class="dg-grid"/><text x="510" y="22" class="dg-ct" text-anchor="middle">DNAT : entrer depuis Internet</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="370" y="60" width="110" height="52" rx="9"/></g><text x="425.0" y="83.0" class="dg-t" text-anchor="middle" style="--d:3">IP publique</text><text x="425.0" y="101.0" class="dg-s" text-anchor="middle" style="--d:3">:443</text><g class="dg-box dg-pop" style="--d:4"><rect x="540" y="60" width="126" height="52" rx="9"/></g><text x="603.0" y="83.0" class="dg-t" text-anchor="middle" style="--d:4">serveur privé</text><text x="603.0" y="101.0" class="dg-s" text-anchor="middle" style="--d:4">10.0.1.5:8443</text><g class="dg-box dg-ghost dg-pop" style="--d:5"><rect x="370" y="160" width="296" height="52" rx="9"/></g><text x="518.0" y="183.0" class="dg-s" text-anchor="middle" style="--d:5">dst 203.0.113.7:443 → dst 10.0.1.5:8443</text><text x="518.0" y="201.0" class="dg-s" text-anchor="middle" style="--d:5">la destination est réécrite</text><path d="M480 86 L538 86" class="dg-l c flow" marker-end="url(#g14-c)"/></svg><figcaption>SNAT pour sortir (box, NAT gateway), DNAT pour exposer un service (redirection de port, Service NodePort).</figcaption></figure>
<!-- /schema:nat -->

Conséquences pratiques :

- derrière un NAT, une machine peut **sortir** mais personne ne peut l'**appeler** directement : c'est un effet de bord protecteur, mais ce n'est pas un pare-feu ;
- un service externe voit **l'IP du NAT**, pas la tienne : c'est cette IP qu'il faut faire autoriser chez un partenaire (d'où l'intérêt d'une IP de sortie fixe) ;
- la table de traduction a une taille limitée : des milliers de connexions sortantes vers une même destination peuvent l'épuiser (*port exhaustion*), ce qui donne des échecs de connexion aléatoires.

## Dans le cloud

```
Internet ──► Internet Gateway ──► sous-réseau public (LB, NAT Gateway)
                                        │
                     sous-réseau privé ─┘ route 0.0.0.0/0 → NAT Gateway
```

- Un sous-réseau est **public** parce que sa table de routage envoie `0.0.0.0/0` vers l'**Internet Gateway**, et que ses machines ont une IP publique.
- Un sous-réseau **privé** envoie `0.0.0.0/0` vers une **NAT Gateway** : sortie possible, entrée impossible.
- Les **security groups** (stateful, attachés aux instances) et les **NACL** (stateless, attachées aux sous-réseaux) s'ajoutent par-dessus. Un paquet doit passer **les deux**.

## Diagnostiquer un blocage

1. Le service écoute-t-il ? `ss -ltnp` sur le serveur.
2. Le paquet arrive-t-il ? `tcpdump -ni any port 443` sur le serveur, pendant un essai.
3. S'il n'arrive pas : règles en amont (security group, NACL, pare-feu d'entreprise, route).
4. S'il arrive sans réponse : pare-feu local, route retour, ou l'appli.
5. Timeout = probablement un **drop** ; refus immédiat = rien n'écoute ou un **reject**.

> **À retenir.** Un pare-feu stateful laisse passer tout seul le retour des connexions ; un stateless non. Le SNAT permet aux machines privées de sortir sous une IP publique, le DNAT fait entrer du trafic vers une machine interne. « Ça marche depuis ma machine, pas depuis le serveur » cache souvent une règle de sortie ou l'absence de NAT : teste toujours depuis la machine concernée.
