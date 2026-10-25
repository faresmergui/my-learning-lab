---
title: Le réseau des conteneurs
chapter: 7
order: 1
duration: 9
level: intermédiaire
tags:
- Docker
cards:
- q: Sur quoi repose l'isolation réseau d'un conteneur ?
  a: 'Sur un **network namespace** Linux : le conteneur a ses propres interfaces, routes et règles. Une paire **veth** le relie à l''hôte.'
- q: Comment fonctionne le réseau `bridge` par défaut de Docker ?
  a: Chaque conteneur est relié par une paire veth au pont `docker0`. Il sort vers l'extérieur grâce à un **SNAT** sur l'IP de l'hôte.
- q: Que fait `-p 8080:80` ?
  a: 'Il publie le port 80 du conteneur sur le port 8080 de l''hôte, avec une règle **DNAT**. Par défaut sur toutes les interfaces : `-p 127.0.0.1:8080:80` pour se limiter à la machine.'
- q: Pourquoi les conteneurs d'un réseau Docker personnalisé se trouvent-ils par leur nom ?
  a: Docker fournit un **DNS intégré** sur les réseaux créés par l'utilisateur (et dans Compose). Sur le bridge par défaut, ce n'est pas le cas.
- q: Que fait `--network host` ?
  a: Le conteneur utilise **directement** le réseau de l'hôte, sans isolation ni NAT. Performant, mais il peut écouter sur n'importe quel port de l'hôte.
- q: Qu'est-ce qu'un namespace réseau ?
  a: 'Une pile réseau isolée du noyau Linux : interfaces, routes, règles de pare-feu et ports propres. Chaque conteneur en a une, ce qui lui permet d''écouter sur 80 sans gêner les autres.'
- q: Qu'est-ce qu'une paire veth ?
  a: Deux interfaces virtuelles reliées comme les deux bouts d'un câble. Un bout dans le conteneur (`eth0`), l'autre sur l'hôte, branché au bridge.
- q: Pourquoi un port publié avec `-p` peut-il contourner ufw ?
  a: Docker insère ses propres règles NAT et de transfert, évaluées avant celles d'ufw. Le trafic vers le conteneur ne passe pas par la chaîne `input` qu'ufw filtre.
- q: Pourquoi `api` peut-il joindre `db:5432` dans Compose sans `ports:` ?
  a: Les deux sont sur le même réseau de projet. `ports:` sert uniquement à exposer un port **vers l'hôte**.
quiz:
- q: Tu publies un conteneur avec `-p 5432:5432` sur un serveur ayant un pare-feu ufw qui bloque le 5432. La base est-elle joignable depuis Internet ?
  options:
  - Non, ufw la protège
  - Souvent oui, car les règles NAT de Docker passent avant celles d'ufw
  - Seulement en IPv6
  - Seulement depuis le même réseau
  answer: 1
  explain: 'Un piège classique : Docker insère ses propres règles. Publie sur `127.0.0.1` si le port ne doit pas être exposé, ou filtre dans la chaîne `DOCKER-USER`.'
- q: Deux conteneurs Compose, `api` et `db`, sont dans le même projet. Quelle adresse `api` doit-il utiliser pour joindre la base ?
  options:
  - localhost:5432
  - db:5432
  - 172.17.0.1:5432
  - host.docker.internal:5432
  answer: 1
  explain: Compose crée un réseau dédié avec un DNS. `localhost` désigne le conteneur `api` lui-même.
- q: Ton conteneur `api` doit joindre une base PostgreSQL installée directement sur l'hôte Linux. `localhost:5432` échoue. Pourquoi ?
  options:
  - PostgreSQL n'écoute pas
  - '`localhost` désigne le conteneur lui-même, qui a son propre namespace réseau'
  - Il faut publier le port 5432
  - Le DNS de Docker est en panne
  answer: 1
  explain: Utilise l'IP du bridge (`172.17.0.1`) ou `host.docker.internal` via `extra_hosts`, et vérifie que PostgreSQL écoute sur cette interface.
- q: Deux conteneurs lancés avec `docker run` sans option réseau n'arrivent pas à se joindre par leur nom. Pourquoi ?
  options:
  - Le bridge par défaut ne fournit pas de DNS entre conteneurs
  - Ils sont dans des namespaces différents
  - Il manque `-p`
  - Il faut le mode host
  answer: 0
  explain: 'Crée un réseau (`docker network create app`) et lance-les avec `--network app` : le DNS intégré résoudra leurs noms.'
---

Un conteneur a l'air d'avoir sa propre carte réseau, sa propre IP et ses propres ports. Pourtant il tourne sur la même machine que les autres. Cette fiche montre l'astuce : tout repose sur des briques du noyau Linux que tu connais déjà en partie (interfaces, routage, NAT), simplement assemblées automatiquement par Docker.


> **Les termes et outils cités dans cette fiche.**
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.

## Les briques du noyau

**Le namespace réseau.** Linux peut créer plusieurs « piles réseau » indépendantes sur une même machine. Chacune a ses propres interfaces, sa table de routage, ses règles de pare-feu et ses ports. Un conteneur vit dans **son** namespace : il peut écouter sur le port 80 sans gêner un autre conteneur qui écoute lui aussi sur 80. Vu de l'intérieur, c'est une machine à part.

**La paire veth.** Un namespace isolé ne parle à personne. Pour le relier, Docker crée une **paire veth** : deux interfaces virtuelles reliées comme les deux bouts d'un câble. Un bout (`eth0`) est placé dans le conteneur, l'autre (`vethXXXX`) reste sur l'hôte.

**Le bridge.** Sur l'hôte, tous les bouts `veth` sont branchés sur un **bridge** (`docker0`), un switch virtuel. Les conteneurs branchés dessus sont sur le même réseau local (`172.17.0.0/16` par défaut) et se parlent directement. Le bridge a lui-même une IP (`172.17.0.1`) qui sert de **passerelle** aux conteneurs.

**Le NAT.** Pour sortir sur Internet, les conteneurs passent par leur passerelle, puis l'hôte fait un **SNAT** (masquerade) : le paquet sort avec l'IP de l'hôte. Pour entrer, `-p` ajoute un **DNAT**.

## Ce qui se passe sous le capot

<!-- schema:bridge -->
<figure class="diagram"><svg viewBox="0 0 680 290" role="img" aria-label="Le réseau bridge de Docker" style="--minw:560px"><defs><marker id="g15-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g15-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g15-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g15-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="40" y="14" width="220" height="82" rx="12" class="dg-zone dg-zc"/><text x="52" y="32" class="dg-zl" text-anchor="start">netns conteneur A</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="80" y="40" width="140" height="40" rx="9"/></g><text x="150.0" y="65.0" class="dg-s" text-anchor="middle" style="--d:0">eth0 10.0.0.2</text><path d="M150 80 L150 136" class="dg-l c" marker-end="url(#g15-c)" marker-start="url(#g15-c)"/><text x="150.0" y="112.0" class="dg-s" text-anchor="middle">veth</text><rect x="300" y="14" width="220" height="82" rx="12" class="dg-zone dg-zc"/><text x="312" y="32" class="dg-zl" text-anchor="start">netns conteneur B</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="340" y="40" width="140" height="40" rx="9"/></g><text x="410.0" y="65.0" class="dg-s" text-anchor="middle" style="--d:1">eth0 10.0.0.3</text><path d="M410 80 L410 136" class="dg-l c" marker-end="url(#g15-c)" marker-start="url(#g15-c)"/><text x="410.0" y="112.0" class="dg-s" text-anchor="middle">veth</text><g class="dg-box dg-pop" style="--d:2"><rect x="40" y="138" width="480" height="44" rx="9"/></g><text x="280.0" y="157.0" class="dg-t" text-anchor="middle" style="--d:2">pont docker0</text><text x="280.0" y="175.0" class="dg-s" text-anchor="middle" style="--d:2">un switch virtuel sur l&#x27;hôte</text><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="560" y="138" width="106" height="44" rx="9"/></g><text x="613.0" y="157.0" class="dg-t" text-anchor="middle" style="--d:3">iptables</text><text x="613.0" y="175.0" class="dg-s" text-anchor="middle" style="--d:3">SNAT</text><g class="dg-box dg-pop" style="--d:4"><rect x="400" y="222" width="266" height="52" rx="9"/></g><text x="533.0" y="245.0" class="dg-t" text-anchor="middle" style="--d:4">eth0 de l&#x27;hôte</text><text x="533.0" y="263.0" class="dg-s" text-anchor="middle" style="--d:4">→ Internet</text><path d="M520 160 L558 160" class="dg-l" marker-end="url(#g15-n)"/><path d="M613 182 L613 220" class="dg-l a" marker-end="url(#g15-a)"/><text x="40" y="240" class="dg-s" text-anchor="start">A et B se parlent directement par le pont.</text><text x="40" y="256" class="dg-s" text-anchor="start">Pour sortir, la source est réécrite avec l&#x27;IP de l&#x27;hôte.</text></svg><figcaption>Chaque conteneur a son namespace réseau, relié au pont par une paire veth.</figcaption></figure>
<!-- /schema:bridge -->

Le trajet d'une requête `curl` lancée depuis un conteneur vers Internet :

1. dans le conteneur, la route `default via 172.17.0.1` envoie le paquet sur `eth0` ;
2. il ressort de l'autre côté de la paire veth, sur l'hôte, dans le bridge `docker0` ;
3. l'hôte route le paquet vers sa carte réseau réelle ;
4. la règle de masquerade remplace l'IP source `172.17.0.5` par l'IP de l'hôte ;
5. la réponse revient, le conntrack fait la traduction inverse et la renvoie au conteneur.

```bash
docker network ls
docker network inspect bridge          # plage, passerelle, conteneurs branchés
ip link show type veth                 # les bouts côté hôte
ip -br a show docker0                  # le bridge et son IP
nsenter -t $(docker inspect -f '{{.State.Pid}}' api) -n ip a   # vue depuis le conteneur
nft list ruleset | grep -i masq        # le NAT de sortie
```

## Publier un port : `-p`

Par défaut, un conteneur n'est **pas joignable** de l'extérieur de l'hôte : son IP `172.17.x` n'existe que sur la machine. `-p 8080:80` crée une règle **DNAT** : ce qui arrive sur le port 8080 de l'hôte est réécrit vers le port 80 du conteneur.

| Option | Effet |
| --- | --- |
| `-p 8080:80` | port 8080 de **toutes** les interfaces de l'hôte → port 80 du conteneur |
| `-p 127.0.0.1:8080:80` | seulement depuis l'hôte lui-même |
| pas de `-p` | joignable seulement par les autres conteneurs du même réseau |

Attention : Docker insère ses règles NAT **avant** celles de `ufw` ou `firewalld`. Un port publié avec `-p` est donc joignable même si ufw semble le bloquer. Pour une base de données, publie sur `127.0.0.1` ou ne publie rien.

## Les modes réseau Docker

| Mode | Isolation | Usage |
| --- | --- | --- |
| `bridge` (défaut) | oui, NAT vers l'extérieur | cas général |
| réseau utilisateur (`docker network create`) | oui, avec **DNS** entre conteneurs | Compose, applis multi-conteneurs |
| `host` | aucune : le conteneur utilise directement le réseau de l'hôte | performance, outils réseau |
| `none` | totale, juste `lo` | traitements sans réseau |

La différence entre le bridge par défaut et un réseau utilisateur est importante : sur un réseau utilisateur, Docker fournit un **petit serveur DNS** (à l'adresse `127.0.0.11` dans chaque conteneur) qui résout le **nom des conteneurs et des services**. Sur le bridge par défaut, il n'y en a pas : il faudrait connaître les IP, qui changent à chaque redémarrage.

## Compose

Compose crée automatiquement un réseau utilisateur par projet. Chaque service y est joignable par **son nom**.

```yaml
services:
  api:
    image: registry.local/api:2.1
    ports: ["127.0.0.1:8080:8080"]      # publié, mais seulement en local
    environment: { DATABASE_URL: postgres://db:5432/shop }   # « db » = nom du service
  db:
    image: postgres:17
    # pas de ports : joignable seulement par api, via le réseau du projet
```

Note que `api` parle à `db` sur le port **5432 du conteneur**, directement sur le réseau du projet : il n'y a pas besoin de `ports:` pour ça. `ports:` ne sert qu'à exposer vers l'hôte.

> **Piège classique.** `localhost` dans un conteneur désigne le conteneur lui-même, pas l'hôte ni un autre conteneur, parce que chaque conteneur a son propre namespace et donc son propre `lo`. Utilise le nom du service, ou `host.docker.internal` pour l'hôte (Docker Desktop, ou à déclarer avec `extra_hosts` sous Linux).

> **À retenir.** Un conteneur, c'est un namespace réseau relié par une paire veth à un bridge, avec du NAT pour sortir (SNAT) et pour entrer (`-p`, DNAT). Les réseaux utilisateur et Compose ajoutent un DNS qui résout les noms des services.
