---
title: TCP, UDP et les ports
chapter: 1
order: 2
duration: 9
level: intermédiaire
tags:
- fondamentaux
cards:
- q: À quoi sert un numéro de port ?
  a: À désigner **quel programme** doit recevoir les données sur une machine. L'IP amène le paquet à la bonne machine, le port l'amène au bon processus (443 pour le serveur web, 22 pour SSH…).
- q: Qu'est-ce qui identifie une connexion TCP de façon unique ?
  a: 'Le **quadruplet** : IP source, port source, IP destination, port destination (plus le protocole). C''est pour ça qu''un serveur peut avoir des milliers de clients sur le même port 443.'
- q: Que veut dire un port « en écoute » (LISTEN) ?
  a: Un programme a demandé au noyau de recevoir les connexions arrivant sur ce port. On le voit avec `ss -ltnp`. Sans processus en écoute, la connexion est refusée.
- q: Différence entre « connection refused » et « timeout » ?
  a: '**Refused** : la machine a répondu (RST) mais personne n''écoute sur ce port. **Timeout** : aucune réponse, souvent un pare-feu qui jette les paquets, une mauvaise route ou une machine éteinte.'
- q: Pourquoi DNS et la vidéo en direct utilisent-ils UDP ?
  a: 'UDP n''a ni connexion ni renvoi : c''est plus rapide et plus léger. Pour une petite question DNS ou une image vidéo qui sera vite périmée, attendre un renvoi ne sert à rien.'
- q: Qu'est-ce qu'un port éphémère ?
  a: Le port source, choisi au hasard par le système du client (en général entre 32768 et 60999 sous Linux) pour chaque nouvelle connexion sortante.
- q: Que signifie écouter sur `127.0.0.1:8080` plutôt que `0.0.0.0:8080` ?
  a: '`127.0.0.1` : seule la machine elle-même peut se connecter. `0.0.0.0` : toutes les interfaces, donc joignable depuis le réseau (si le pare-feu le permet).'
quiz:
- q: '`curl http://10.0.0.5:8080` répond immédiatement « Connection refused ». Que sais-tu ?'
  options:
  - La machine est éteinte
  - Un pare-feu bloque silencieusement
  - La machine est joignable mais rien n'écoute sur 8080
  - Le DNS est en panne
  answer: 2
  explain: Un refus immédiat vient de la machine elle-même (un paquet RST). Le réseau fonctionne, c'est le service qui n'écoute pas, ou écoute sur une autre IP ou un autre port.
- q: La même commande reste bloquée 2 minutes puis échoue. Piste la plus probable ?
  options:
  - Le service a planté
  - Un pare-feu jette les paquets sans répondre, ou la route est mauvaise
  - Le port est mal tapé
  - Le certificat a expiré
  answer: 1
  explain: Un timeout signifie que personne ne répond. Les pare-feu configurés en « drop » produisent exactement ce symptôme.
- q: Ton appli tourne dans une VM et répond avec `curl localhost:3000` depuis la VM, mais pas depuis ton poste. `ss -ltn` montre `127.0.0.1:3000`. Que faire ?
  options:
  - Ouvrir le port 3000 dans le pare-feu
  - Configurer l'appli pour écouter sur `0.0.0.0`
  - Changer de port
  - Redémarrer la VM
  answer: 1
  explain: L'appli n'écoute que sur l'interface locale. Tant qu'elle n'écoute pas sur l'interface réseau, le pare-feu n'y change rien.
- q: Pourquoi un serveur web peut-il servir 10 000 clients sur le seul port 443 ?
  options:
  - Il ouvre un port par client
  - Chaque connexion est distinguée par l'IP et le port source du client
  - Il fait du NAT interne
  - HTTP/2 multiplexe tout dans une connexion unique
  answer: 1
  explain: Côté serveur, le port est le même ; c'est le couple IP source + port source qui rend chaque connexion unique.
---

La fiche précédente a montré que l'IP amène un paquet jusqu'à la bonne **machine**. Il reste une question : sur cette machine tournent des dizaines de programmes, lequel doit recevoir le paquet ? C'est le rôle de la couche **transport** et de ses deux protagonistes, **TCP** et **UDP**.


> **Les termes et outils cités dans cette fiche.**
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **HTTPS** : HTTP chiffré par TLS.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **VXLAN** : une technique qui transporte des réseaux virtuels à l'intérieur de paquets UDP, pour relier des machines sur plusieurs serveurs.
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.
> - **proxy** : un intermédiaire qui reçoit les requêtes et les transmet à leur place.

## Les ports : le numéro d'appartement

Une machine a une adresse IP, comme un immeuble a une adresse. Les **ports** sont les numéros d'appartement : un nombre entre 0 et 65 535 qui désigne un programme précis.

| Port | Service habituel |
| --- | --- |
| 22 | SSH |
| 53 | DNS |
| 80 / 443 | HTTP / HTTPS |
| 5432 | PostgreSQL |
| 6443 | API Kubernetes |

Ces numéros ne sont que des **conventions**. Rien n'empêche de faire tourner SSH sur 2222. Les ports sous 1024 sont dits « privilégiés » : sous Linux, il faut des droits particuliers pour écouter dessus.

Une connexion a **deux** ports. Le serveur écoute sur un port connu (443). Le client, lui, utilise un **port éphémère** tiré au hasard (par exemple 51 234). Une connexion est donc identifiée par quatre valeurs :

```
10.0.0.12:51234  ──►  51.15.2.10:443
 IP client : port      IP serveur : port
```

C'est grâce à ce quadruplet qu'un serveur distingue des milliers de clients sur le même port 443, et qu'un même navigateur peut ouvrir plusieurs onglets vers le même site.

## Écouter sur un port

Un programme serveur demande au noyau : « envoie-moi ce qui arrive sur le port 8080 ». On dit qu'il **écoute** (état `LISTEN`). Il choisit aussi **sur quelle adresse** il écoute, et c'est une source de confusion fréquente :

| Adresse d'écoute | Qui peut se connecter |
| --- | --- |
| `127.0.0.1:8080` | seulement la machine elle-même |
| `10.0.0.5:8080` | les clients qui passent par cette interface |
| `0.0.0.0:8080` (ou `*:8080`, `[::]:8080`) | tout le monde, sur toutes les interfaces |

```bash
ss -ltnp      # TCP en écoute (l=listen, t=tcp, n=numérique, p=processus)
ss -lunp      # même chose pour UDP
ss -tnp       # connexions TCP établies en ce moment
```

## TCP : la conversation fiable

TCP fonctionne comme un appel téléphonique : on établit la ligne, on parle, on raccroche.

1. **Établir la connexion** : la poignée de main en trois temps. Le client envoie `SYN` (« on se parle ? »), le serveur répond `SYN-ACK` (« d'accord »), le client confirme `ACK`. Ça coûte un aller-retour avant le moindre octet utile.
2. **Transmettre** : TCP découpe les données en segments numérotés. Le destinataire accuse réception. Ce qui n'est pas acquitté à temps est **renvoyé**. Les données arrivent donc **complètes et dans l'ordre**, même si le réseau en perd une partie.
3. **Réguler** : TCP ralentit quand le réseau sature (contrôle de congestion) et quand le destinataire ne suit pas (contrôle de flux).
4. **Fermer** : échange de `FIN` des deux côtés, ou `RST` pour couper brutalement.

Le prix de cette fiabilité, c'est de la **latence** : la poignée de main, les attentes d'acquittement et les renvois. Si un paquet se perd, tout ce qui suit attend qu'il soit renvoyé.

## UDP : la carte postale

UDP envoie des messages indépendants (des **datagrammes**) sans connexion, sans accusé de réception, sans renvoi. Si un message se perd, UDP ne le sait même pas : c'est à l'application de gérer.

Pourquoi l'utiliser ? Parce que c'est plus **rapide** et plus **simple** :

- **DNS** : une question, une réponse, dans un seul petit paquet. Si rien ne revient, le client repose la question.
- **Vidéo, voix, jeux** : une image arrivée en retard ne sert plus à rien, mieux vaut passer à la suivante.
- **QUIC** (la base de HTTP/3) : il reconstruit la fiabilité au-dessus d'UDP, mais à sa manière, pour éviter les défauts de TCP.

| | TCP | UDP |
| --- | --- | --- |
| Connexion | oui (SYN, SYN-ACK, ACK) | non |
| Fiabilité, ordre | garantis | non |
| Latence | plus élevée | minimale |
| Exemples | HTTP/1 et 2, SSH, bases de données | DNS, VoIP, QUIC, VXLAN |

## Lire les erreurs de connexion

C'est là que ces notions deviennent utiles au quotidien. Les messages d'erreur disent **où** le problème se situe :

| Message | Ce qui s'est passé | Où chercher |
| --- | --- | --- |
| `Connection refused` | la machine a répondu `RST` : personne n'écoute sur ce port | le service est-il lancé ? sur le bon port ? sur `0.0.0.0` ? |
| `Connection timed out` | aucune réponse du tout | pare-feu qui jette, mauvaise route, machine éteinte |
| `No route to host` | le système ou un routeur sait que la destination est injoignable | table de routage, pare-feu qui rejette |
| `Connection reset by peer` | la connexion existait puis a été coupée brutalement | crash de l'appli, proxy, timeout côté serveur |
| `Name or service not known` | échec **avant** le réseau : le nom ne se résout pas | DNS (fiche DNS) |

Pour tester un port sans outil applicatif :

```bash
nc -vz 10.0.0.5 5432          # TCP : le port répond-il ?
curl -v telnet://10.0.0.5:5432 # alternative si nc est absent
```

> **À retenir.** L'IP trouve la machine, le port trouve le programme. « Refused » veut dire que le réseau marche mais que rien n'écoute ; « timeout » veut dire que quelque chose, souvent un pare-feu, avale les paquets.
