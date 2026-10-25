---
title: Adressage IP et CIDR
chapter: 2
order: 1
duration: 11
level: intermédiaire
tags:
- fondamentaux
cards:
- q: Combien d'adresses contient un `/24` ? Et un `/16` ?
  a: 'Un `/24` : 2⁸ = **256** adresses (254 utilisables pour des hôtes). Un `/16` : 2¹⁶ = **65 536**.'
- q: Quelles sont les plages d'adresses privées (RFC 1918) ?
  a: '`10.0.0.0/8`, `172.16.0.0/12` et `192.168.0.0/16`.'
- q: L'adresse `10.0.12.200` est-elle dans `10.0.8.0/21` ?
  a: 'Oui. Un `/21` couvre 8 blocs de /24 : de `10.0.8.0` à `10.0.15.255`.'
- q: Combien d'adresses AWS réserve-t-il dans chaque sous-réseau ?
  a: '**5** : la première (réseau), les trois suivantes (routeur, DNS, réservée) et la dernière. Un `/28` n''offre donc que 11 adresses utilisables.'
- q: Pourquoi bien choisir les plages d'un VPC dès le départ ?
  a: Deux réseaux qui se **chevauchent** ne peuvent pas être reliés (peering, VPN, transit). Et un cluster Kubernetes consomme beaucoup d'IP pour ses pods.
- q: Que veut dire `0.0.0.0/0` ?
  a: '**Toutes** les adresses IPv4. Dans une table de routage, c''est la route par défaut. Dans une règle de pare-feu, c''est « tout le monde ».'
- q: Combien d'adresses dans un /26 ?
  a: 2^(32−26) = **64** adresses.
- q: Que fait une machine pour joindre une IP hors de son sous-réseau ?
  a: Elle envoie le paquet à sa **passerelle** (routeur par défaut).
- q: Pourquoi deux réseaux qui se chevauchent posent-ils problème ?
  a: 'Une même adresse existe des deux côtés : on ne peut pas savoir **où** envoyer le paquet. On ne peut pas les relier proprement.'
- q: Quelle plage couvre 10.0.8.0/21 ?
  a: De **10.0.8.0 à 10.0.15.255** (2 048 adresses, 8 blocs de 256).
- q: Combien d'adresses utilisables dans un /24 ?
  a: '**254** : la première (réseau) et la dernière (broadcast) sont réservées. Les clouds en réservent parfois plus.'
quiz:
- q: Tu as besoin de 4 sous-réseaux de taille égale dans `10.20.0.0/16`, le plus grands possible. Quel masque ?
  options:
  - /17
  - /18
  - /20
  - /24
  answer: 1
  explain: 'Chaque bit de masque en plus divise par deux. Il faut 2 bits pour 4 sous-réseaux : /16 + 2 = /18, soit 16 384 adresses chacun.'
- q: Ton VPC est en `10.0.0.0/16` et le réseau d'un partenaire aussi. Que se passe-t-il si tu veux un peering ?
  options:
  - Ça fonctionne
  - C'est impossible tant que les plages se chevauchent
  - Il suffit d'un NAT Gateway
  - Il faut passer en IPv6 sur un seul côté
  answer: 1
  explain: Le routage ne peut pas savoir de quel côté se trouve `10.0.1.5`. D'où l'intérêt d'un plan d'adressage pour toute l'entreprise.
- q: Ton VPC est en 10.0.0.0/16 et le réseau du bureau aussi. Tu veux les relier par VPN. Que se passe-t-il ?
  options:
  - Ça marche directement
  - 'Conflit : les plages se chevauchent'
  - Il faut juste ouvrir le pare-feu
  - Il faut un DNS commun
  answer: 1
  explain: Les mêmes adresses existent des deux côtés, le routage est impossible sans NAT complexe. D'où l'importance de choisir des plages distinctes dès le départ.
- q: Une machine en 192.168.1.10/24 veut joindre 192.168.2.5. Que fait-elle ?
  options:
  - Elle lui parle directement
  - Elle envoie à sa passerelle
  - Elle abandonne
  - Elle demande au DNS
  answer: 1
  explain: '192.168.2.5 n''est pas dans 192.168.1.0/24 : le paquet part vers la passerelle.'
---

Une adresse IPv4 est un nombre de **32 bits**, écrit en quatre nombres de 0 à 255 : `10.0.12.200`. Une partie de l'adresse désigne le **réseau** (le quartier), le reste désigne la **machine** dans ce réseau (la maison). La notation **CIDR** dit où se trouve la frontière entre les deux.


> **Les termes et outils cités dans cette fiche.**
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.
> - **nœud** : une machine (physique ou virtuelle) membre d'un cluster.
> - **VPC** : un réseau privé virtuel dans le cloud, isolé des autres clients.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **VPN** : un tunnel chiffré qui relie un poste ou un site à un réseau privé à travers Internet.
> - **CNI** : le standard des plugins réseau de Kubernetes (Calico, Cilium…), qui donnent une adresse IP à chaque pod.

## Lire une notation CIDR

`10.0.8.0/21` se lit : « les **21 premiers bits** sont fixes et désignent le réseau ». Il reste 32 − 21 = 11 bits pour les machines, soit 2¹¹ = 2 048 adresses.

Le calcul en pratique : **nombre d'adresses = 2^(32 − masque)**.

| Masque | Adresses | Exemple d'usage |
| --- | --- | --- |
| `/32` | 1 | une seule IP (règle de pare-feu) |
| `/28` | 16 | petit sous-réseau (bastion) |
| `/24` | 256 | sous-réseau classique |
| `/20` | 4 096 | sous-réseau de nœuds Kubernetes |
| `/16` | 65 536 | un VPC |
| `/8` | 16,7 millions | `10.0.0.0/8` en entier |

Astuce : chaque bit en moins **double** la taille. `/24` = 256, `/23` = 512, `/22` = 1 024…

<!-- schema:cidr -->
<figure class="diagram"><svg viewBox="0 0 680 200" role="img" aria-label="Lire un préfixe CIDR" style="--minw:560px"><defs><marker id="g9-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g9-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g9-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g9-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="340" y="24" class="dg-tl" text-anchor="middle">10.0.8.0/21</text><g class="dg-box dg-c dg-pop"><rect x="30" y="46" width="17" height="34" rx="3"/></g><text x="38.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="49" y="46" width="17" height="34" rx="3"/></g><text x="57.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="68" y="46" width="17" height="34" rx="3"/></g><text x="76.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="87" y="46" width="17" height="34" rx="3"/></g><text x="95.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="106" y="46" width="17" height="34" rx="3"/></g><text x="114.5" y="68.0" class="dg-s" text-anchor="middle">1</text><g class="dg-box dg-c dg-pop"><rect x="125" y="46" width="17" height="34" rx="3"/></g><text x="133.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="144" y="46" width="17" height="34" rx="3"/></g><text x="152.5" y="68.0" class="dg-s" text-anchor="middle">1</text><g class="dg-box dg-c dg-pop"><rect x="163" y="46" width="17" height="34" rx="3"/></g><text x="171.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="190" y="46" width="17" height="34" rx="3"/></g><text x="198.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="209" y="46" width="17" height="34" rx="3"/></g><text x="217.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="228" y="46" width="17" height="34" rx="3"/></g><text x="236.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="247" y="46" width="17" height="34" rx="3"/></g><text x="255.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="266" y="46" width="17" height="34" rx="3"/></g><text x="274.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="285" y="46" width="17" height="34" rx="3"/></g><text x="293.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="304" y="46" width="17" height="34" rx="3"/></g><text x="312.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="323" y="46" width="17" height="34" rx="3"/></g><text x="331.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="350" y="46" width="17" height="34" rx="3"/></g><text x="358.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="369" y="46" width="17" height="34" rx="3"/></g><text x="377.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="388" y="46" width="17" height="34" rx="3"/></g><text x="396.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="407" y="46" width="17" height="34" rx="3"/></g><text x="415.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-c dg-pop"><rect x="426" y="46" width="17" height="34" rx="3"/></g><text x="434.5" y="68.0" class="dg-s" text-anchor="middle">1</text><g class="dg-box dg-pop"><rect x="445" y="46" width="17" height="34" rx="3"/></g><text x="453.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="464" y="46" width="17" height="34" rx="3"/></g><text x="472.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="483" y="46" width="17" height="34" rx="3"/></g><text x="491.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="510" y="46" width="17" height="34" rx="3"/></g><text x="518.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="529" y="46" width="17" height="34" rx="3"/></g><text x="537.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="548" y="46" width="17" height="34" rx="3"/></g><text x="556.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="567" y="46" width="17" height="34" rx="3"/></g><text x="575.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="586" y="46" width="17" height="34" rx="3"/></g><text x="594.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="605" y="46" width="17" height="34" rx="3"/></g><text x="613.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="624" y="46" width="17" height="34" rx="3"/></g><text x="632.5" y="68.0" class="dg-s" text-anchor="middle">0</text><g class="dg-box dg-pop"><rect x="643" y="46" width="17" height="34" rx="3"/></g><text x="651.5" y="68.0" class="dg-s" text-anchor="middle">0</text><text x="237.5" y="104" class="dg-ct" text-anchor="middle">21 bits réseau : fixes</text><text x="520" y="104" class="dg-t" text-anchor="middle">11 bits hôtes</text><text x="340" y="140" class="dg-s" text-anchor="middle">2¹¹ = 2048 adresses : de 10.0.8.0 à 10.0.15.255</text><text x="340" y="160" class="dg-s" text-anchor="middle">plus le préfixe est grand, plus le réseau est petit</text></svg><figcaption>Le nombre après le / dit combien de bits, en partant de la gauche, désignent le réseau.</figcaption></figure>
<!-- /schema:cidr -->

## Pourquoi les masques « tombent juste » sur /8, /16, /24

Chaque nombre de l'adresse fait 8 bits. Un `/24` fixe donc exactement les trois premiers nombres : `192.168.1.0/24` contient toutes les adresses de `192.168.1.0` à `192.168.1.255`. Un `/16` fixe les deux premiers : `10.20.0.0/16` va de `10.20.0.0` à `10.20.255.255`.

Pour les autres masques, il faut compter. `10.0.8.0/21` couvre 2 048 adresses, donc 8 blocs de 256 : de `10.0.8.0` à `10.0.15.255`.

## Les adresses réservées dans un sous-réseau

Dans chaque sous-réseau, la **première** adresse désigne le réseau lui-même et la **dernière** sert de diffusion (broadcast). Un `/24` offre donc 254 adresses utilisables. Les clouds en réservent souvent quelques-unes de plus (AWS en garde 5 par sous-réseau : routeur, DNS, etc.).

## Le masque et la passerelle

Quand une machine veut parler à une IP, elle regarde si cette IP est **dans son propre sous-réseau** grâce au masque :

- **Oui** : elle lui parle directement, sur le réseau local.
- **Non** : elle envoie le paquet à sa **passerelle** (le routeur par défaut), qui se charge de le faire suivre.

C'est pour cela qu'un mauvais masque provoque des pannes étranges : la machine croit qu'une IP est locale alors qu'elle ne l'est pas, ou l'inverse.

## Les plages à connaître

| Plage | Usage |
| --- | --- |
| `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | réseaux **privés** : non routés sur Internet, réutilisables partout |
| `127.0.0.0/8` | boucle locale (`127.0.0.1`, la machine elle-même) |
| `169.254.0.0/16` | lien local (métadonnées cloud : `169.254.169.254`) |
| `100.64.0.0/10` | CGNAT, parfois utilisé pour les pods |

Une adresse privée ne sort pas telle quelle sur Internet : il faut un **NAT** (voir la fiche pare-feu et NAT).

## Un plan d'adressage pour un VPC

<!-- schema:vpc -->
<figure class="diagram"><svg viewBox="0 0 680 280" role="img" aria-label="Un plan d&#x27;adressage sur trois zones" style="--minw:560px"><defs><marker id="g10-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g10-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g10-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g10-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="652" height="254" rx="12" class="dg-zone dg-zc"/><text x="26" y="32" class="dg-zl" text-anchor="start">VPC shop-prod · 10.10.0.0/16</text><text x="220" y="52" class="dg-zl" text-anchor="middle">zone a</text><text x="390" y="52" class="dg-zl" text-anchor="middle">zone b</text><text x="560" y="52" class="dg-zl" text-anchor="middle">zone c</text><text x="30" y="88" class="dg-t" text-anchor="start">public</text><text x="30" y="104" class="dg-s" text-anchor="start">load balancers, NAT</text><g class="dg-box dg-pop" style="--d:0"><rect x="150" y="66" width="140" height="52" rx="9"/></g><text x="220.0" y="97.0" class="dg-s" text-anchor="middle" style="--d:0">10.10.0.0/24</text><g class="dg-box dg-pop" style="--d:1"><rect x="320" y="66" width="140" height="52" rx="9"/></g><text x="390.0" y="97.0" class="dg-s" text-anchor="middle" style="--d:1">10.10.1.0/24</text><g class="dg-box dg-pop" style="--d:2"><rect x="490" y="66" width="140" height="52" rx="9"/></g><text x="560.0" y="97.0" class="dg-s" text-anchor="middle" style="--d:2">10.10.2.0/24</text><text x="30" y="154" class="dg-t" text-anchor="start">privé</text><text x="30" y="170" class="dg-s" text-anchor="start">nœuds et pods</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="150" y="132" width="140" height="52" rx="9"/></g><text x="220.0" y="163.0" class="dg-s" text-anchor="middle" style="--d:1">10.10.16.0/20</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="320" y="132" width="140" height="52" rx="9"/></g><text x="390.0" y="163.0" class="dg-s" text-anchor="middle" style="--d:2">10.10.32.0/20</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="490" y="132" width="140" height="52" rx="9"/></g><text x="560.0" y="163.0" class="dg-s" text-anchor="middle" style="--d:3">10.10.48.0/20</text><text x="30" y="220" class="dg-t" text-anchor="start">données</text><text x="30" y="236" class="dg-s" text-anchor="start">bases</text><g class="dg-box dg-pop" style="--d:2"><rect x="150" y="198" width="140" height="52" rx="9"/></g><text x="220.0" y="229.0" class="dg-s" text-anchor="middle" style="--d:2">10.10.64.0/24</text><g class="dg-box dg-pop" style="--d:3"><rect x="320" y="198" width="140" height="52" rx="9"/></g><text x="390.0" y="229.0" class="dg-s" text-anchor="middle" style="--d:3">10.10.65.0/24</text><g class="dg-box dg-pop" style="--d:4"><rect x="490" y="198" width="140" height="52" rx="9"/></g><text x="560.0" y="229.0" class="dg-s" text-anchor="middle" style="--d:4">10.10.66.0/24</text></svg><figcaption>Les sous-réseaux privés sont larges (/20) car les pods consomment beaucoup d&#x27;adresses.</figcaption></figure>
<!-- /schema:vpc -->

Les règles d'un bon plan :

1. Choisir une plage qui **ne chevauche pas** les autres réseaux auxquels on se connectera (bureau, autres VPC, VPN). Deux réseaux qui se chevauchent ne peuvent pas être reliés proprement.
2. Découper en sous-réseaux **par rôle** (public, privé, base de données) et **par zone**.
3. Prévoir large : agrandir un sous-réseau existant est difficile, en créer un nouveau est facile.

```bash
ipcalc 10.10.16.0/20
python3 -c "import ipaddress; print(ipaddress.ip_address('10.0.12.200') in ipaddress.ip_network('10.0.8.0/21'))"
```

## Et IPv6 ?

IPv6 utilise **128 bits** (`2001:db8::1`). Le principe du préfixe est le même (`/64` est la taille standard d'un sous-réseau), mais l'espace est si grand qu'on ne manque jamais d'adresses et qu'on a moins besoin de NAT.

> **À retenir.** Nombre d'adresses = 2^(32 − masque). Une IP hors de ton sous-réseau passe par la passerelle. Et prévois large pour les sous-réseaux de pods : avec certains CNI (comme celui d'AWS), chaque pod consomme une vraie IP du VPC.
