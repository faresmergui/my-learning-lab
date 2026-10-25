---
title: Routage, passerelle et ARP
chapter: 2
order: 2
duration: 9
level: intermédiaire
tags:
- fondamentaux
cards:
- q: Comment une machine décide-t-elle où envoyer un paquet ?
  a: Elle consulte sa **table de routage** et prend la route la plus précise (le masque le plus long) qui contient l'IP de destination. Si la destination est sur son réseau local, elle l'envoie directement ; sinon, à une passerelle.
- q: Qu'est-ce que la passerelle par défaut ?
  a: 'La route `0.0.0.0/0` (`default`) : le routeur à qui envoyer tout ce qui ne correspond à aucune autre route. Sans elle, seul le réseau local est joignable.'
- q: À quoi sert ARP ?
  a: À trouver l'adresse **MAC** qui correspond à une IP **sur le réseau local**. Les trames Ethernet sont adressées en MAC, pas en IP.
- q: Quand on envoie un paquet vers Internet, quelle adresse MAC de destination met-on ?
  a: Celle de la **passerelle**, pas celle du serveur distant. L'IP de destination reste celle du serveur ; la MAC change à chaque saut.
- q: Que montre `traceroute` ?
  a: La liste des routeurs traversés jusqu'à la destination, saut par saut, avec le temps de réponse de chacun. Les `* * *` sont des routeurs qui ne répondent pas, ce qui n'est pas forcément une panne.
- q: Pourquoi faut-il une route retour ?
  a: 'Un paquet qui arrive doit pouvoir repartir : si la machine d''en face n''a pas de route vers ton réseau, la réponse part ailleurs et la connexion échoue (timeout).'
quiz:
- q: Une VM a l'IP 10.0.1.15/24 et aucune route `default`. Que peut-elle joindre ?
  options:
  - Tout Internet
  - Seulement les machines en 10.0.1.0/24
  - Seulement sa passerelle
  - Rien du tout
  answer: 1
  explain: Sans passerelle par défaut, seules les adresses de son propre sous-réseau sont joignables directement.
- q: 'Table de routage : `default via 10.0.0.1`, `10.20.0.0/16 via 10.0.0.254`, `10.20.5.0/24 via 10.0.0.200`. Par où part un paquet vers 10.20.5.9 ?'
  options:
  - 10.0.0.1
  - 10.0.0.254
  - 10.0.0.200
  - Directement
  answer: 2
  explain: 'La route la plus précise gagne : /24 est plus long que /16 et que /0.'
- q: Depuis le serveur A, tu fais `ping` vers B dans un autre réseau. Les paquets arrivent chez B (vu dans `tcpdump`), mais A ne reçoit aucune réponse. Piste ?
  options:
  - Le DNS de A
  - B n'a pas de route retour vers le réseau de A
  - Le port est fermé
  - L'ARP de A est corrompu
  answer: 1
  explain: Le routage marche dans un sens, pas dans l'autre. Vérifie `ip route get <IP de A>` sur B.
---

La fiche précédente a découpé les adresses en réseaux. Reste à comprendre comment un paquet passe d'un réseau à l'autre jusqu'à sa destination. C'est le **routage**, et il repose sur une idée simple : chaque machine ne connaît que **le prochain saut**, jamais le chemin complet.


> **Les termes et outils cités dans cette fiche.**
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.
> - **NAT** : la traduction d'adresses : plusieurs machines privées sortent sur Internet avec une seule adresse publique.
> - **VPN** : un tunnel chiffré qui relie un poste ou un site à un réseau privé à travers Internet.
> - **VPC** : un réseau privé virtuel dans le cloud, isolé des autres clients.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.

## L'analogie du centre de tri

Un paquet IP voyage comme une lettre de centre de tri en centre de tri. Chaque centre regarde l'adresse, consulte son tableau (« tout ce qui va vers Lyon, envoie-le au camion n°3 ») et passe la lettre au suivant. Aucun centre ne connaît le trajet entier.

Ce tableau, c'est la **table de routage**. Chaque machine en a une, ton portable comme un routeur d'opérateur.

## Lire une table de routage

```bash
$ ip route
default via 10.0.1.1 dev eth0               # tout le reste → la passerelle
10.0.1.0/24 dev eth0 proto kernel src 10.0.1.15   # mon réseau local : en direct
172.17.0.0/16 dev docker0                   # le réseau des conteneurs Docker
```

Chaque ligne dit : « pour cette plage de destinations, passe par cette interface, éventuellement via ce routeur ».

- Une ligne **sans `via`** : la destination est sur le même réseau local. On l'envoie directement.
- Une ligne **avec `via`** : on confie le paquet à ce routeur, qui se débrouillera.
- La ligne **`default`** (équivalente à `0.0.0.0/0`) : la **passerelle par défaut**, pour tout ce qui ne correspond à rien d'autre.

Quand plusieurs routes conviennent, la **plus précise** gagne (le masque le plus long). C'est la règle du « longest prefix match ».

```bash
ip route get 8.8.8.8        # quelle route serait utilisée pour cette IP ?
# 8.8.8.8 via 10.0.1.1 dev eth0 src 10.0.1.15
```

## Le dernier mètre : ARP et les adresses MAC

Sur un réseau local (Ethernet, Wi-Fi), les cartes réseau ne s'adressent pas par IP mais par **adresse MAC** (`52:54:00:ab:12:9f`), gravée dans chaque carte. Pour envoyer un paquet à 10.0.1.20, la machine doit donc connaître sa MAC.

C'est le rôle d'**ARP** : la machine crie sur le réseau local « qui a 10.0.1.20 ? », et la bonne machine répond « c'est moi, ma MAC est … ». La réponse est gardée en cache.

```bash
ip neigh          # le cache ARP : IP ↔ MAC des voisins
```

Point clé : pour joindre un serveur sur Internet, la machine ne cherche **pas** la MAC du serveur (il est loin). Elle cherche la MAC de **la passerelle**. Le paquet garde l'IP du serveur comme destination, mais la trame Ethernet est adressée à la passerelle. À chaque saut, l'en-tête Ethernet est remplacé ; l'en-tête IP, lui, reste le même (sauf en cas de NAT).

| Ce qui change à chaque saut | Ce qui reste du début à la fin |
| --- | --- |
| MAC source et destination | IP source et destination (hors NAT) |
| | ports, données |

## Le voyage complet d'un paquet

Ton poste (10.0.1.15) ouvre `https://51.15.2.10` :

1. La table de routage dit : 51.15.2.10 n'est pas local, donc `default via 10.0.1.1`.
2. ARP donne la MAC de 10.0.1.1 (la box ou le routeur).
3. Le paquet part vers la passerelle, qui consulte **sa** table et l'envoie au routeur suivant de l'opérateur.
4. Chaque routeur fait pareil, en décrémentant le **TTL** IP (un compteur de sauts qui évite les boucles infinies).
5. Le dernier routeur est sur le réseau du serveur : il fait un ARP et livre le paquet.
6. La **réponse** fait le chemin inverse, avec la table de routage du serveur. Si celui-ci n'a pas de route vers toi, la réponse se perd.

## Voir le chemin

```bash
traceroute 51.15.2.10        # chaque routeur traversé, avec sa latence
mtr 51.15.2.10               # la même chose en continu, avec le taux de perte
```

`traceroute` exploite le TTL : il envoie des paquets avec un TTL de 1, puis 2, puis 3… Chaque routeur qui tombe à zéro renvoie un message d'erreur, et se dévoile. Des `* * *` signifient seulement qu'un routeur ne répond pas à ces messages ; si les sauts suivants répondent, il n'y a pas de panne.

## Les pannes de routage typiques

| Symptôme | Cause fréquente |
| --- | --- |
| rien hors du réseau local ne répond | pas de route `default`, ou mauvaise passerelle |
| `Network is unreachable` | aucune route ne correspond à la destination |
| un réseau précis injoignable, le reste OK | route manquante vers ce réseau (VPN, peering de VPC) |
| le paquet arrive (vu par `tcpdump`) mais pas de réponse | pas de **route retour** chez le destinataire |
| deux réseaux avec la même plage ne se parlent pas | chevauchement d'adresses : le routage ne peut pas choisir |

Dans le cloud, ces tables de routage existent aussi, mais au niveau des **sous-réseaux** : une *route table* AWS associée à un sous-réseau joue exactement ce rôle (`0.0.0.0/0 → Internet Gateway` pour un sous-réseau public, `→ NAT Gateway` pour un privé).

> **À retenir.** Chaque machine ne connaît que le prochain saut : la route la plus précise de sa table, sinon la passerelle par défaut. ARP traduit l'IP du prochain saut en MAC sur le réseau local. Et une connexion a toujours besoin d'une route **dans les deux sens**.
