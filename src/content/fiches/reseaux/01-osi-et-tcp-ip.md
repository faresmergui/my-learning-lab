---
title: Modèle OSI et TCP/IP
chapter: 1
order: 1
duration: 10
level: intermédiaire
tags:
- fondamentaux
cards:
- q: Quelles couches OSI faut-il vraiment connaître au quotidien ?
  a: '**2** liaison (Ethernet, MAC, switch), **3** réseau (IP, routage), **4** transport (TCP, UDP, ports), **7** application (HTTP, DNS, SSH).'
- q: Comment s'établit une connexion TCP ?
  a: 'Par la **poignée de main en trois temps** : `SYN`, `SYN-ACK`, `ACK`. La fermeture se fait avec `FIN` (ou `RST` en cas de coupure brutale).'
- q: Différence entre TCP et UDP ?
  a: '**TCP** : connexion, ordre garanti, retransmission (HTTP, SSH, bases). **UDP** : pas de connexion ni de garantie, mais rapide (DNS, VoIP, QUIC/HTTP3).'
- q: Qu'est-ce que le MTU ?
  a: La taille maximale d'un paquet sur un lien, **1500 octets** en Ethernet classique. Les tunnels (VXLAN, VPN) ajoutent des en-têtes et réduisent le MTU disponible.
- q: Que signifie un `RST` reçu juste après un `SYN` ?
  a: La machine est joignable, mais **aucun service n'écoute** sur ce port. C'est le « connection refused ».
- q: Qu'est-ce que l'encapsulation ?
  a: 'Chaque couche **emballe** les données de la couche du dessus en ajoutant son en-tête : segment TCP → paquet IP → trame Ethernet.'
- q: Qu'est-ce que la MTU ?
  a: La **taille maximale** d'un paquet sur un lien, souvent 1 500 octets. Un tunnel ajoute un en-tête et peut la faire dépasser.
- q: 'Adresse IP ou adresse MAC : laquelle sert sur le réseau local ?'
  a: La **MAC** désigne le prochain saut sur le réseau local. L'**IP** désigne la destination finale.
- q: À quoi sert le port ?
  a: Désigner **quel programme** doit recevoir les données sur la machine (443 pour HTTPS, 22 pour SSH).
quiz:
- q: Un load balancer « L4 » travaille à quel niveau ?
  options:
  - Sur les adresses MAC
  - Sur les IP et les ports TCP/UDP, sans lire le contenu
  - Sur les URL et les en-têtes HTTP
  - Sur les noms DNS
  answer: 1
  explain: Un LB L7 lit le HTTP (chemin, en-têtes, cookies) et peut router selon le contenu. Un LB L4 ne voit que les connexions.
- q: Les petites requêtes passent dans un tunnel VPN, mais les gros transferts restent bloqués. Que soupçonner ?
  options:
  - Le DNS
  - Un problème de MTU (paquets trop gros, ICMP de fragmentation bloqués)
  - Un certificat expiré
  - Le TTL
  answer: 1
  explain: Teste avec `ping -M do -s 1400 hôte` en faisant varier la taille pour trouver le MTU qui passe.
- q: Les petites requêtes vers un service passent, les gros téléchargements se bloquent, et seulement à travers le VPN. Piste la plus probable ?
  options:
  - Le DNS
  - Un problème de MTU
  - Un port fermé
  - Un certificat expiré
  answer: 1
  explain: 'Le VPN ajoute un en-tête : les gros paquets dépassent la MTU et sont rejetés. Les petits passent.'
- q: '`ping 8.8.8.8` marche mais `curl https://google.com` échoue avec « Could not resolve host ». Quelle couche est en cause ?'
  options:
  - Physique
  - Réseau (routage)
  - DNS (résolution de nom)
  - TLS
  answer: 2
  explain: L'IP et la route fonctionnent (le ping passe). C'est la traduction du nom en adresse qui échoue.
---

Quand deux machines communiquent, beaucoup de choses doivent fonctionner en même temps : le câble ou le Wi-Fi, les adresses, les ports, le protocole de l'application. Les **modèles en couches** découpent ce problème en étages. Chaque étage a un rôle précis et ne s'occupe que de lui.

En pratique, ils servent surtout à **localiser une panne** : est-ce le câble, l'adresse, le port ou l'application ?


> **Les termes et outils cités dans cette fiche.**
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.
> - **UDP** : le protocole de transport sans connexion, rapide mais sans garantie de livraison (DNS, vidéo, VXLAN).
> - **TLS** : le protocole qui chiffre une connexion et prouve l'identité du serveur par un certificat.
> - **ICMP** : le protocole de messages de contrôle du réseau, utilisé par ping et traceroute.
> - **VLAN** : un réseau local virtuel : plusieurs réseaux isolés sur les mêmes commutateurs.
> - **ARP** : le protocole qui trouve l'adresse MAC correspondant à une adresse IP sur le réseau local.

## L'analogie du courrier

Envoyer une requête web ressemble à envoyer une lettre :

| Étape du courrier | Couche réseau | Ce qu'elle apporte |
| --- | --- | --- |
| Le texte de la lettre | **Application** (HTTP, DNS, SSH) | Le contenu, dans une langue que les deux comprennent |
| Le nom du destinataire dans l'immeuble | **Transport** (TCP, UDP) | Le **port** : quel programme doit recevoir |
| L'adresse postale | **Réseau** (IP) | L'**adresse IP** : quelle machine, même à l'autre bout du monde |
| Le facteur de quartier | **Liaison** (Ethernet, Wi-Fi) | L'adresse **MAC** : le prochain saut sur le réseau local |
| La route et le camion | **Physique** | Les signaux électriques, radio ou lumineux |

## Les deux modèles

Le modèle **OSI** a 7 couches, c'est le modèle théorique. Le modèle **TCP/IP** en a 4, c'est celui qu'utilise vraiment Internet. On mélange souvent les deux : on dit « couche 4 » pour le transport et « couche 7 » pour l'application.

| Couche OSI | TCP/IP | Exemples | Outils de diagnostic |
| --- | --- | --- | --- |
| 7 Application | Application | HTTP, DNS, SSH, TLS | `curl`, `dig` |
| 4 Transport | Transport | TCP, UDP, ports | `ss`, `nc` |
| 3 Réseau | Internet | IP, ICMP, routage | `ip r`, `ping`, `traceroute` |
| 2 Liaison | Accès réseau | Ethernet, MAC, VLAN, ARP | `ip neigh`, `bridge` |
| 1 Physique | Accès réseau | câble, Wi-Fi, fibre | `ethtool` |

Les couches 5 et 6 d'OSI (session, présentation) sont en pratique intégrées à l'application.

## L'encapsulation

<!-- schema:encapsulation -->
<figure class="diagram"><svg viewBox="0 0 680 230" role="img" aria-label="L&#x27;encapsulation" style="--minw:560px"><defs><marker id="g8-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g8-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g8-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g8-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="20" y="44" class="dg-zl" text-anchor="start">application</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="366" y="20" width="300" height="36" rx="9"/></g><text x="516.0" y="43.0" class="dg-s" text-anchor="middle" style="--d:0">données HTTP</text><text x="20" y="94" class="dg-zl" text-anchor="start">transport</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="290" y="70" width="70" height="36" rx="9"/></g><text x="325.0" y="93.0" class="dg-s" text-anchor="middle" style="--d:1">TCP</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="366" y="70" width="300" height="36" rx="9"/></g><text x="516.0" y="93.0" class="dg-s" text-anchor="middle" style="--d:1">données HTTP</text><text x="20" y="144" class="dg-zl" text-anchor="start">réseau</text><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="214" y="120" width="70" height="36" rx="9"/></g><text x="249.0" y="143.0" class="dg-s" text-anchor="middle" style="--d:2">IP</text><g class="dg-box dg-pop" style="--d:2"><rect x="290" y="120" width="70" height="36" rx="9"/></g><text x="325.0" y="143.0" class="dg-s" text-anchor="middle" style="--d:2">TCP</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="366" y="120" width="300" height="36" rx="9"/></g><text x="516.0" y="143.0" class="dg-s" text-anchor="middle" style="--d:2">données HTTP</text><text x="20" y="194" class="dg-zl" text-anchor="start">liaison</text><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="138" y="170" width="70" height="36" rx="9"/></g><text x="173.0" y="193.0" class="dg-s" text-anchor="middle" style="--d:3">Eth</text><g class="dg-box dg-pop" style="--d:3"><rect x="214" y="170" width="70" height="36" rx="9"/></g><text x="249.0" y="193.0" class="dg-s" text-anchor="middle" style="--d:3">IP</text><g class="dg-box dg-pop" style="--d:3"><rect x="290" y="170" width="70" height="36" rx="9"/></g><text x="325.0" y="193.0" class="dg-s" text-anchor="middle" style="--d:3">TCP</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="366" y="170" width="300" height="36" rx="9"/></g><text x="516.0" y="193.0" class="dg-s" text-anchor="middle" style="--d:3">données HTTP</text><text x="340" y="222" class="dg-s" text-anchor="middle">chaque couche ajoute son en-tête (en rouge) devant ce qu&#x27;elle reçoit</text></svg><figcaption>Chaque couche ajoute son en-tête devant ce qu&#x27;elle reçoit. Un tunnel (VXLAN, VPN) en ajoute d&#x27;autres : le MTU utile baisse.</figcaption></figure>
<!-- /schema:encapsulation -->

Chaque couche **emballe** ce que lui donne la couche du dessus en ajoutant sa propre étiquette (un **en-tête**) :

1. L'application produit une requête HTTP.
2. TCP l'emballe dans un **segment** avec les ports source et destination.
3. IP l'emballe dans un **paquet** avec les adresses IP source et destination.
4. Ethernet l'emballe dans une **trame** avec les adresses MAC du prochain saut.

À l'arrivée, chaque couche retire son emballage et passe le reste à la couche du dessus. Un **tunnel** (VPN, overlay Kubernetes) ajoute un emballage de plus : le paquet grossit, et s'il dépasse la taille maximale autorisée (la **MTU**, souvent 1 500 octets), il doit être découpé ou est rejeté. C'est la source de pannes étranges où les petites requêtes passent et les grosses bloquent.

## TCP en un coup d'œil

<!-- schema:tcp -->
<figure class="diagram"><svg viewBox="0 0 680 260" role="img" aria-label="Une connexion TCP" style="--minw:560px"><defs><marker id="g7-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g7-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g7-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g7-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="40" y="14" width="120" height="40" rx="9"/></g><text x="100.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:0">client</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="400" y="14" width="120" height="40" rx="9"/></g><text x="460.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:0">serveur</text><line x1="100" y1="54" x2="100" y2="250" class="dg-grid"/><line x1="460" y1="54" x2="460" y2="250" class="dg-grid"/><path d="M102 78 L458 78" class="dg-l c" marker-end="url(#g7-c)" style="--d:0"/><text x="280.0" y="71.0" class="dg-s" text-anchor="middle" style="--d:0">SYN</text><path d="M458 110 L102 110" class="dg-l c" marker-end="url(#g7-c)" style="--d:1"/><text x="280.0" y="103.0" class="dg-s" text-anchor="middle" style="--d:1">SYN-ACK</text><path d="M102 142 L458 142" class="dg-l c" marker-end="url(#g7-c)" style="--d:2"/><text x="280.0" y="135.0" class="dg-s" text-anchor="middle" style="--d:2">ACK</text><path d="M102 182 L458 182" class="dg-l ok thick" marker-end="url(#g7-ok)" marker-start="url(#g7-ok)" style="--d:3"/><text x="280.0" y="175.0" class="dg-s" text-anchor="middle" style="--d:3">données</text><path d="M102 226 L458 226" class="dg-l" marker-end="url(#g7-n)" style="--d:4"/><text x="280.0" y="219.0" class="dg-s" text-anchor="middle" style="--d:4">FIN</text><text x="476" y="114" class="dg-s" text-anchor="start">poignée de main</text><text x="476" y="128" class="dg-s" text-anchor="start">en 3 temps : 1 RTT</text><text x="476" y="230" class="dg-s" text-anchor="start">fermeture</text></svg><figcaption>Un RST à la place du SYN-ACK : le port est fermé. Pas de réponse du tout : un pare-feu filtre.</figcaption></figure>
<!-- /schema:tcp -->

TCP établit une **connexion** avant d'envoyer des données : c'est la poignée de main en trois temps (SYN, SYN-ACK, ACK). Ensuite, il numérote les données, vérifie qu'elles arrivent et renvoie ce qui s'est perdu. La fiche suivante détaille TCP et UDP.

```bash
ss -tan state established | head   # connexions TCP établies
ss -s                              # résumé par état
```

## Diagnostiquer couche par couche

| Couche | Question | Commande |
| --- | --- | --- |
| Liaison | La carte réseau est-elle active ? | `ip -br link` |
| Réseau | Ai-je une IP ? Une route ? La passerelle répond-elle ? | `ip -br a`, `ip r`, `ping <passerelle>` |
| Réseau | Le nom se résout-il ? (DNS, utilisé avant tout le reste) | `dig +short nom` |
| Transport | Le port est-il ouvert ? | `nc -zv hôte 443` |
| Application | Le service répond-il correctement ? | `curl -v https://hôte` |

> **À retenir.** Quand « le réseau ne marche pas », remonte les couches dans l'ordre : lien, IP et route, DNS, port, application. Chaque outil répond à une couche précise, et la première couche qui échoue est celle à corriger.
