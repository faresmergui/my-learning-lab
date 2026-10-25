---
title: Diagnostiquer le réseau
chapter: 5
order: 1
duration: 9
level: intermédiaire
tags:
- LFCS
cards:
- q: Quelles commandes remplacent `ifconfig` et `route` ?
  a: '`ip a` (adresses), `ip r` (routes), `ip link` (interfaces). Elles viennent du paquet iproute2.'
- q: Comment savoir quel processus écoute sur le port 443 ?
  a: '`ss -tlnp | grep :443` (en root pour voir les processus). `lsof -i :443` marche aussi.'
- q: Dans quel ordre Linux résout-il un nom ?
  a: Selon `/etc/nsswitch.conf`, en général `/etc/hosts` puis le DNS configuré dans `/etc/resolv.conf` (souvent géré par systemd-resolved).
- q: Différence entre « connection refused » et « timeout » ?
  a: '**Refused** : la machine répond, mais rien n''écoute sur ce port. **Timeout** : aucune réponse, souvent un pare-feu qui jette les paquets, ou une route manquante.'
- q: Comment voir les détails d'une requête HTTPS (DNS, TLS, en-têtes) ?
  a: '`curl -v https://site`, et `curl -o /dev/null -s -w ''%{time_connect} %{time_starttransfer}'' https://site` pour les temps.'
- q: Comment capturer le trafic vers un port précis ?
  a: '`tcpdump -i any -nn port 5432`, et `-w capture.pcap` pour l''ouvrir ensuite dans Wireshark.'
quiz:
- q: '`curl http://10.0.0.5:8080` répond « connection refused ». Où chercher en premier ?'
  options:
  - Le DNS
  - 'Le service sur 10.0.0.5 : tourne-t-il, et écoute-t-il sur la bonne adresse et le bon port ?'
  - La table de routage du client
  - Le certificat TLS
  answer: 1
  explain: 'Un refus vient de la machine cible. Vérifie `ss -tlnp` sur 10.0.0.5 : un service qui écoute seulement sur `127.0.0.1` refuse les connexions externes.'
- q: '`dig api.interne` donne la bonne IP, mais `curl api.interne` va ailleurs. Cause probable ?'
  options:
  - Une entrée dans /etc/hosts
  - Le pare-feu
  - Le MTU
  - Un proxy SOCKS
  answer: 0
  explain: '`dig` interroge directement le DNS, alors que les applis suivent `nsswitch.conf`, qui consulte d''abord `/etc/hosts`. `getent hosts api.interne` montre ce que voient les applis.'
---

Face à un problème réseau, on remonte les couches : interface, route, DNS, port, application.

> **Les outils cités dans cette fiche.**
> - **iproute2** : le paquet qui fournit `ip` (interfaces, adresses, routes) et `ss` (connexions et ports en écoute). Il remplace les anciens `ifconfig`, `route` et `netstat`.
> - **dig** : interroge directement un serveur DNS (le système qui traduit un nom en adresse IP) et affiche sa réponse brute. **getent hosts** montre au contraire ce que voient les applications, `/etc/hosts` compris.
> - **systemd-resolved** et **resolvectl** : le service local qui fait les résolutions DNS sur beaucoup de distributions, et la commande pour voir sa configuration.
> - **nc** (netcat) : ouvre une connexion brute vers un port ; avec `-z`, il teste juste si le port répond.
> - **mtr** : combine `ping` et `traceroute` pour montrer, routeur par routeur, la latence et les pertes de paquets.
> - **curl** : client HTTP en ligne de commande ; `-v` affiche tout l'échange (connexion, TLS, en-têtes).
> - **tcpdump** : capture les paquets qui passent sur une interface ; **Wireshark** est son équivalent graphique, pratique pour relire une capture `.pcap`.
> - **lsof** : liste les fichiers ouverts par les processus, sockets réseau compris.
> - **MTU** : taille maximale d'un paquet sur un lien (souvent 1500 octets). Un MTU mal réglé donne des connexions qui marchent pour les petites requêtes et bloquent sur les grosses.
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.
> - **TCP** : le protocole de transport fiable : connexion établie, données remises dans l'ordre et sans perte.
> - **UDP** : le protocole de transport sans connexion, rapide mais sans garantie de livraison (DNS, vidéo, VXLAN).

<!-- schema:marches -->
<figure class="diagram"><svg viewBox="0 0 680 206" role="img" aria-label="Diagnostiquer le réseau, marche par marche" style="--minw:560px"><defs><marker id="g4-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g4-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g4-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g4-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="120" width="122" height="58" rx="9"/></g><text x="75.0" y="146.0" class="dg-t" text-anchor="middle" style="--d:0">1 interface</text><text x="75.0" y="164.0" class="dg-s" text-anchor="middle" style="--d:0">ip -br a</text><g class="dg-box dg-pop" style="--d:1"><rect x="146" y="96" width="122" height="58" rx="9"/></g><text x="207.0" y="122.0" class="dg-t" text-anchor="middle" style="--d:1">2 route</text><text x="207.0" y="140.0" class="dg-s" text-anchor="middle" style="--d:1">ip r get 1.1.1.1</text><path d="M136 148 L144 136" class="dg-l c" marker-end="url(#g4-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="278" y="72" width="122" height="58" rx="9"/></g><text x="339.0" y="98.0" class="dg-t" text-anchor="middle" style="--d:2">3 DNS</text><text x="339.0" y="116.0" class="dg-s" text-anchor="middle" style="--d:2">dig +short api</text><path d="M268 124 L276 112" class="dg-l c" marker-end="url(#g4-c)"/><g class="dg-box dg-pop" style="--d:3"><rect x="410" y="48" width="122" height="58" rx="9"/></g><text x="471.0" y="74.0" class="dg-t" text-anchor="middle" style="--d:3">4 port</text><text x="471.0" y="92.0" class="dg-s" text-anchor="middle" style="--d:3">nc -zv api 443</text><path d="M400 100 L408 88" class="dg-l c" marker-end="url(#g4-c)"/><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="542" y="24" width="122" height="58" rx="9"/></g><text x="603.0" y="50.0" class="dg-t" text-anchor="middle" style="--d:4">5 appli</text><text x="603.0" y="68.0" class="dg-s" text-anchor="middle" style="--d:4">curl -v https://…</text><path d="M532 76 L540 64" class="dg-l c" marker-end="url(#g4-c)"/><text x="340" y="196" class="dg-s" text-anchor="middle">on monte une marche seulement si la précédente est bonne</text></svg><figcaption>Chaque marche répond à une couche différente. Sauter une marche fait perdre du temps.</figcaption></figure>
<!-- /schema:marches -->

## 1. Interface et adresse

```bash
ip -br a              # résumé lisible
ip link show eth0
```

## 2. Routes

```bash
ip r
ip route get 10.20.0.15   # par où partira ce paquet
```

## 3. DNS

```bash
dig +short api.example.com
dig @1.1.1.1 api.example.com    # interroger un serveur précis
getent hosts api.example.com    # ce que voient vraiment les applis
resolvectl status               # avec systemd-resolved
```

## 4. Le port est-il joignable ?

```bash
ss -tlnp                         # ce qui écoute localement
nc -zv 10.0.0.5 5432             # tester un port distant
mtr -rwc 20 10.0.0.5             # pertes et latence, saut par saut
```

## 5. L'application

```bash
curl -v https://api.example.com/health
curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' https://api.example.com
```

## En dernier recours

```bash
tcpdump -i any -nn host 10.0.0.5 and port 5432
```

| Symptôme | Piste |
| --- | --- |
| `Name or service not known` | DNS, `/etc/hosts` |
| `Connection refused` | rien n'écoute, ou écoute sur 127.0.0.1 |
| `Connection timed out` | pare-feu, security group, route |
| `No route to host` | route manquante, ou un pare-feu qui rejette activement |

## Pourquoi cet ordre

Chaque étape dépend de la précédente : pas de route sans interface configurée, pas de connexion sans route, pas de requête HTTP sans connexion TCP. En testant **de bas en haut**, la première étape qui échoue désigne la couche fautive, et tu évites de déboguer l'application alors que le câble est débranché. Les fiches du module Réseaux (couches, routage, TCP/UDP, DNS) détaillent chaque notion.

## Lire les sorties

**`ip -br a`** : chaque interface, son état et ses adresses.

```
lo     UNKNOWN  127.0.0.1/8
eth0   UP       10.0.1.15/24     ← l'interface est active, avec une IP dans 10.0.1.0/24
docker0 DOWN    172.17.0.1/16    ← normal si aucun conteneur ne tourne
```

Une interface `DOWN` ou sans adresse IPv4 explique tout le reste.

**`ip r`** : il faut une ligne `default via …` pour sortir du réseau local. `ip route get <IP>` dit quelle interface et quelle passerelle seront utilisées pour une destination précise.

**`ss -tlnp`** : la colonne `Local Address:Port` dit **sur quelle adresse** le service écoute. `127.0.0.1:5432` = seulement en local ; `0.0.0.0:5432` ou `*:5432` = toutes les interfaces.

**`nc -zv`** : `succeeded` = le port répond ; `refused` = la machine répond mais rien n'écoute ; rien pendant longtemps = timeout, probablement un pare-feu.

## tcpdump, sans peur

`tcpdump` affiche les paquets qui passent réellement sur une interface. Il répond à la question la plus utile : **le paquet arrive-t-il ?**

```bash
tcpdump -i any -nn port 443        # -nn : ne pas traduire IP et ports en noms
# 10:02:01 IP 10.0.1.20.51234 > 10.0.1.15.443: Flags [S]    ← un SYN arrive
# 10:02:01 IP 10.0.1.15.443 > 10.0.1.20.51234: Flags [S.]   ← on répond SYN-ACK
```

- Des `[S]` qui arrivent sans `[S.]` en retour : le paquet arrive, mais le serveur ne répond pas (pare-feu local, rien n'écoute, route retour).
- Des `[R]` (reset) en réponse : port fermé.
- Rien du tout : le paquet est bloqué **avant** la machine (security group, routeur, mauvaise IP).

Lance-le des deux côtés si tu peux : là où le paquet disparaît, il y a le problème.

> **À retenir.** Un service qui écoute sur `127.0.0.1:8080` n'est joignable que depuis la machine elle-même. Regarde la colonne d'adresse de `ss -tlnp` : `0.0.0.0` ou `*` veut dire toutes les interfaces.
