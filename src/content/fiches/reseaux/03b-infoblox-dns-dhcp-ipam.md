---
title: 'DNS, DHCP et IPAM en entreprise : Infoblox'
chapter: 3
order: 2
duration: 10
level: intermédiaire
tags:
- Infoblox
- DDI
- IPAM
- DHCP
cards:
- q: Que veut dire DDI ?
  a: '**DNS, DHCP et IPAM** : les trois services qui gèrent les adresses et les noms d''un réseau. Infoblox est l''un des principaux éditeurs de solutions DDI.'
- q: Qu'est-ce que l'IPAM ?
  a: '*IP Address Management* : l''inventaire de tous les réseaux et de toutes les adresses IP (lesquelles sont libres, attribuées, à qui). Il remplace le tableur d''adresses que tout le monde oublie de mettre à jour.'
- q: À quoi sert le DHCP ?
  a: À attribuer automatiquement une adresse IP, un masque, une passerelle et des serveurs DNS aux machines qui arrivent sur le réseau, pour une durée limitée (le **bail**).
- q: Qu'est-ce que le Grid Infoblox ?
  a: L'ensemble des appliances Infoblox d'une entreprise, gérées comme un seul système depuis un **Grid Master** qui détient la base et la réplique vers les autres membres.
- q: Comment automatise-t-on Infoblox ?
  a: 'Par son API REST, **WAPI** : réserver la prochaine IP libre d''un réseau, créer un enregistrement DNS… Il existe un provider Terraform et une collection Ansible (`infoblox.nios_modules`).'
- q: Pourquoi relier IPAM, DNS et DHCP ?
  a: 'Une même action met tout à jour : réserver une IP crée l''enregistrement DNS correspondant et évite qu''un DHCP la distribue à une autre machine. Fini les conflits d''adresses et les enregistrements orphelins.'
quiz:
- q: Terraform crée une VM et doit lui donner une IP fixe sans conflit. Quelle approche avec Infoblox ?
  options:
  - Choisir une IP au hasard dans le réseau
  - Demander la prochaine IP libre à Infoblox via son API ou son provider Terraform
  - Utiliser toujours la même IP
  - Laisser le DHCP choisir puis noter l'IP à la main
  answer: 1
  explain: L'IPAM sait quelles adresses sont libres et réserve celle qu'il donne, DNS compris.
- q: Dans un Grid Infoblox, quel membre détient la base de configuration de référence ?
  options:
  - Chaque membre a la sienne
  - Le Grid Master
  - Le serveur DHCP le plus proche
  - Aucun, tout est dans les fichiers de zone
  answer: 1
  explain: Le Grid Master centralise la configuration et la réplique vers les autres membres.
- q: Une machine obtient une adresse déjà utilisée par un serveur configuré à la main. Quel manque est en cause ?
  options:
  - Le DNS est trop lent
  - L'adresse fixe n'était pas réservée dans l'IPAM, donc exclue du DHCP
  - Le TTL est trop court
  - Le serveur n'a pas de nom
  answer: 1
  explain: Sans réservation, le DHCP considère l'adresse comme libre et peut la distribuer.
---

La fiche précédente explique comment fonctionne le DNS. Dans une entreprise, il faut aussi **distribuer les adresses** (DHCP) et **savoir lesquelles sont prises** (IPAM). Ces trois services ensemble s'appellent le **DDI** (*DNS, DHCP, IPAM*). **Infoblox** est l'éditeur le plus répandu dans ce domaine : il vend des appliances (physiques, virtuelles ou dans le cloud) qui rendent ces trois services, gérées depuis une console et une API uniques. Son système s'appelle **NIOS**, et son offre cloud **BloxOne** (aujourd'hui Infoblox Universal DDI).

## Les trois services

| Service | Question à laquelle il répond | Exemple |
| --- | --- | --- |
| **DNS** | quelle IP pour ce nom ? | `api.shop.lan` → `10.0.12.20` |
| **DHCP** | quelle IP donner à cette machine qui arrive ? | un portable reçoit `10.0.30.57` pour 8 heures |
| **IPAM** | quelles adresses sont libres, et à qui sont les autres ? | `10.0.12.0/24` : 41 utilisées, 3 réservées, 210 libres |

Sans outil, on se retrouve avec un serveur DNS d'un côté, un DHCP de l'autre et un tableur d'adresses à côté, jamais à jour. Résultat : des **conflits d'adresses** (deux machines avec la même IP), des enregistrements DNS qui pointent vers des machines disparues, et personne ne sait si `10.0.12.50` est libre.

## Ce qu'apporte une solution DDI

Les trois services partagent **la même base**. Quand on réserve une adresse pour un serveur, Infoblox :

1. la marque comme utilisée dans l'IPAM ;
2. crée les enregistrements DNS (le nom vers l'IP, et l'IP vers le nom) ;
3. l'exclut des plages du DHCP pour qu'elle ne soit jamais distribuée à une autre machine.

Une seule opération, trois services cohérents. L'IPAM découvre aussi les adresses réellement utilisées sur le réseau, ce qui révèle les machines configurées à la main sans être déclarées.

## Le Grid

Une entreprise a plusieurs appliances Infoblox : DNS dans chaque datacenter, DHCP dans chaque site. Elles forment un **Grid**, géré comme un seul système :

- le **Grid Master** détient la base de configuration et la réplique vers les autres ;
- les **membres** rendent les services (DNS, DHCP) au plus près des utilisateurs ;
- un **Grid Master Candidate** peut prendre le relais si le maître tombe.

On configure tout depuis le Grid Master (interface web ou API), jamais membre par membre.

## L'automatiser : WAPI, Terraform et Ansible

Pour un DevOps, l'intérêt principal est l'**API REST d'Infoblox, WAPI**. Elle permet par exemple de demander « la prochaine IP libre de ce réseau » au moment de créer une VM :

```bash
curl -u "$USER:$PASS" -X POST \
  "https://infoblox.lan/wapi/v2.12/record:host" \
  -H "Content-Type: application/json" \
  -d '{"name":"web3.shop.lan","ipv4addrs":[{"ipv4addr":"func:nextavailableip:10.0.12.0/24"}]}'
```

Cet enregistrement **host** réserve l'adresse et crée le DNS en même temps. Le même travail se fait avec :

- le **provider Terraform** `infobloxopen/infoblox` : la VM et son IP sont créées dans le même `apply`, et supprimées ensemble ;
- la collection **Ansible** `infoblox.nios_modules`, ou le plugin de lookup `nios_next_ip`.

C'est ce qui évite le ticket « peux-tu me donner une IP ? » envoyé à l'équipe réseau avant chaque déploiement.

## Et dans le cloud ou Kubernetes ?

Les clouds publics ont leur propre DNS (Route 53, Cloud DNS) et attribuent eux-mêmes les IP de leurs VPC. Infoblox sert alors à garder une **vue unique** des adresses entre le datacenter et les clouds, pour éviter les plages qui se chevauchent quand on relie les deux par VPN. Dans Kubernetes, **ExternalDNS** sait créer les enregistrements des Services et des Ingress directement dans Infoblox.

> **À retenir.** DDI = DNS + DHCP + IPAM sur une même base, et Infoblox en est l'éditeur de référence. Le Grid Master centralise la configuration. Pour un DevOps, tout passe par l'API WAPI, le provider Terraform ou la collection Ansible : réserver une IP crée son DNS et la protège du DHCP en une seule opération.
