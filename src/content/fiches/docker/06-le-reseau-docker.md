---
title: Le réseau Docker
chapter: 6
order: 1
duration: 11
tags:
- Docker
- réseau
cards:
- q: Quels sont les principaux pilotes réseau de Docker ?
  a: '**bridge** (réseau privé sur l''hôte, le défaut), **host** (le conteneur utilise directement le réseau de l''hôte), **none** (aucun réseau), **overlay** (réseau entre plusieurs hôtes, Swarm), **macvlan/ipvlan** (le conteneur a une adresse sur le réseau physique).'
- q: Pourquoi créer un réseau bridge plutôt qu'utiliser celui par défaut ?
  a: Sur un réseau **créé par l'utilisateur**, les conteneurs se trouvent **par leur nom** grâce au DNS intégré de Docker (127.0.0.11). Sur le bridge par défaut, il n'y a pas de résolution de nom, seulement des IP.
- q: Que fait `-p 8080:80` ?
  a: 'Docker ajoute une règle **NAT** (iptables ou nftables) : le trafic arrivant sur le port 8080 de l''hôte est redirigé vers le port 80 du conteneur. Sans adresse précisée, le port est ouvert sur **toutes** les interfaces de l''hôte.'
- q: Pourquoi un port publié par Docker contourne-t-il le pare-feu ufw ?
  a: 'Docker insère ses propres règles dans iptables, évaluées **avant** celles d''ufw. Un `-p 5432:5432` est donc joignable depuis Internet même si ufw le bloque. Solution : publier sur `127.0.0.1:` ou utiliser la chaîne `DOCKER-USER`.'
- q: Comment deux conteneurs d'applications différentes peuvent-ils se parler sans tout exposer ?
  a: En les connectant à un **même réseau** créé pour l'occasion (`docker network connect`). Seuls les conteneurs de ce réseau se voient ; rien n'est publié sur l'hôte.
quiz:
- q: Un conteneur `api` doit joindre une base `db`. Les deux sont sur le bridge par défaut et `db` ne se résout pas. Que fais-tu ?
  options:
  - Écrire l'IP de db en dur
  - Créer un réseau utilisateur et y connecter les deux conteneurs
  - Publier le port de db sur l'hôte
  - Passer en `--network host`
  answer: 1
  explain: Le DNS intégré ne fonctionne que sur les réseaux créés par l'utilisateur.
- q: Dans un conteneur, l'appli écoute sur `127.0.0.1:3000` et `-p 3000:3000` ne répond pas depuis l'hôte. Pourquoi ?
  options:
  - Le port est déjà pris
  - 127.0.0.1 est le loopback du conteneur ; l'appli doit écouter sur 0.0.0.0
  - Il faut `--network none`
  - Docker ne publie que le port 80
  answer: 1
  explain: 'Chaque conteneur a son propre namespace réseau : son 127.0.0.1 n''est pas celui de l''hôte.'
level: intermédiaire
---

Chaque conteneur a son **propre namespace réseau** : ses interfaces, son IP, ses ports, son 127.0.0.1. Docker les relie entre eux et au monde extérieur avec des réseaux virtuels et du NAT. Comprendre ce montage explique la plupart des « ça ne se connecte pas ». La fiche Réseaux sur le réseau des conteneurs décrit les mécanismes du noyau (veth, bridge, NAT) ; celle-ci donne la vue Docker.

> **Les outils cités dans cette fiche.**
> - **bridge** : un commutateur virtuel sur l'hôte (`docker0` pour le réseau par défaut) auquel les conteneurs sont branchés par des paires d'interfaces **veth**.
> - **NAT** : la traduction d'adresses qui permet aux conteneurs de sortir avec l'IP de l'hôte et à l'hôte de rediriger des ports vers eux.
> - **iptables** / **nftables** : le pare-feu du noyau Linux, que Docker programme pour le NAT et l'isolation.
> - **ufw** : une interface simplifiée d'iptables sur Ubuntu.
> - **DNS intégré** : un serveur DNS interne de Docker (`127.0.0.11`) qui résout les noms des conteneurs.
> - **overlay** : un réseau qui relie des conteneurs sur plusieurs hôtes, par encapsulation VXLAN.
> - **cluster** : un groupe de machines qui travaillent ensemble comme un seul système.
> - **UDP** : le protocole de transport sans connexion, rapide mais sans garantie de livraison (DNS, vidéo, VXLAN).

## Comprendre : le bridge

<!-- schema:bridge -->
<figure class="diagram"><svg viewBox="0 0 680 330" role="img" aria-label="Le réseau bridge de Docker" style="--minw:560px"><defs><marker id="g9-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g9-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g9-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g9-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="40" width="110" height="40" rx="9"/></g><text x="69.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:0">Internet</text><rect x="160" y="10" width="506" height="310" rx="12" class="dg-zone "/><text x="172" y="28" class="dg-zl" text-anchor="start">hôte</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="190" y="40" width="190" height="40" rx="9"/></g><text x="285.0" y="65.0" class="dg-s" text-anchor="middle" style="--d:1">eth0 · 203.0.113.10</text><path d="M124 60 L188 60" class="dg-l a" marker-end="url(#g9-a)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="240" y="130" width="340" height="46" rx="9"/></g><text x="410.0" y="150.0" class="dg-t" text-anchor="middle" style="--d:2">bridge br-shop</text><text x="410.0" y="168.0" class="dg-s" text-anchor="middle" style="--d:2">172.18.0.1</text><path d="M285 80 L285 128" class="dg-l a" marker-end="url(#g9-a)"/><text x="296" y="104" class="dg-s" text-anchor="start">NAT : port 8080 → 172.18.0.2:80</text><g class="dg-box dg-pop" style="--d:3"><rect x="200" y="238" width="170" height="52" rx="9"/></g><text x="285.0" y="261.0" class="dg-t" text-anchor="middle" style="--d:3">web</text><text x="285.0" y="279.0" class="dg-s" text-anchor="middle" style="--d:3">172.18.0.2:80</text><g class="dg-box dg-pop" style="--d:4"><rect x="450" y="238" width="170" height="52" rx="9"/></g><text x="535.0" y="261.0" class="dg-t" text-anchor="middle" style="--d:4">db</text><text x="535.0" y="279.0" class="dg-s" text-anchor="middle" style="--d:4">172.18.0.3:5432</text><path d="M285 176 L285 236" class="dg-l c" marker-end="url(#g9-c)" marker-start="url(#g9-c)"/><path d="M535 176 L535 236" class="dg-l c" marker-end="url(#g9-c)" marker-start="url(#g9-c)"/><text x="293" y="212" class="dg-s" text-anchor="start">veth</text><text x="543" y="212" class="dg-s" text-anchor="start">veth</text><text x="413" y="310" class="dg-s" text-anchor="middle" style="--d:5">web et db se joignent par leur nom (DNS de Docker)</text></svg><figcaption>Seul le port publié est joignable depuis l&#x27;extérieur ; entre conteneurs, on passe par le bridge.</figcaption></figure>
<!-- /schema:bridge -->

- en **sortie**, le conteneur passe par le bridge puis par un NAT avec l'IP de l'hôte ;
- en **entrée**, rien n'arrive au conteneur sauf ce qui est **publié** avec `-p` ;
- entre conteneurs du même réseau, tout passe, directement par les IP internes.

## Les pilotes

| Pilote | Comportement | Usage |
| --- | --- | --- |
| **bridge** (créé par toi) | réseau privé, DNS par nom | le cas normal |
| bridge par défaut (`docker0`) | réseau privé, **sans** DNS par nom | à éviter |
| **host** | pas d'isolation réseau, ports de l'hôte directement | performances, outils réseau |
| **none** | seulement le loopback | tâches sans réseau |
| **overlay** | plusieurs hôtes (Swarm) | clusters Docker Swarm |
| **macvlan** / **ipvlan** | une IP sur le réseau physique | applis qui doivent apparaître comme une machine du LAN |

## Les commandes

```bash
docker network create shop
docker run -d --name db  --network shop -e POSTGRES_PASSWORD=secret postgres:17
docker run -d --name api --network shop -p 127.0.0.1:3000:3000 \
  -e DATABASE_URL=postgres://postgres:secret@db:5432/postgres api:dev

docker network ls
docker network inspect shop            # sous-réseau, conteneurs connectés
docker network connect autre-reseau api   # un conteneur peut être sur plusieurs réseaux
docker exec api getent hosts db        # tester la résolution
```

Un **alias** réseau (`--network-alias base`) donne plusieurs noms à un même conteneur, ou un même nom à plusieurs conteneurs (répartition simple par DNS).

## Publier des ports

| Écriture | Effet |
| --- | --- |
| `-p 8080:80` | port 80 du conteneur sur le port 8080 de **toutes** les interfaces |
| `-p 127.0.0.1:8080:80` | seulement en local sur l'hôte |
| `-p 8080:80/udp` | en UDP |
| `-P` | tous les ports `EXPOSE` sur des ports aléatoires |

Deux pièges fréquents :

1. **L'appli écoute sur 127.0.0.1 dans le conteneur** : elle n'est joignable que depuis le conteneur lui-même. Elle doit écouter sur `0.0.0.0`.
2. **Docker contourne ufw** : ses règles iptables passent avant. Une base publiée avec `-p 5432:5432` est ouverte à Internet sur un serveur, même avec ufw actif. On publie sur `127.0.0.1`, on ne publie pas du tout les services internes, ou on filtre dans la chaîne `DOCKER-USER`.

## Déboguer

```bash
docker exec api cat /etc/resolv.conf         # DNS utilisé (127.0.0.11 sur un réseau utilisateur)
docker exec api wget -qO- http://db:5432 || true
docker run --rm -it --network container:api nicolaka/netshoot   # outils réseau dans le namespace de api
ss -tlnp | grep docker-proxy                 # sur l'hôte : ports publiés
sudo iptables -t nat -L DOCKER -n            # règles NAT créées par Docker
```

L'image **netshoot** contient `dig`, `curl`, `tcpdump`, `ss`, `mtr` : la lancer dans le namespace réseau d'un conteneur sans outils (`--network container:<nom>`) permet de le diagnostiquer sans modifier son image.

> **À retenir.** Créer un réseau par application : les conteneurs s'y trouvent par leur nom. Seul ce qui est publié avec `-p` est joignable de l'extérieur ; publier sur `127.0.0.1` ce qui n'a pas à être public, car Docker passe avant ufw. Dans le conteneur, l'appli écoute sur `0.0.0.0`. netshoot dans le namespace d'un conteneur pour déboguer.
