---
title: Load balancing et proxys
chapter: 5
order: 1
duration: 10
level: intermédiaire
tags:
- fondamentaux
cards:
- q: Différence entre un load balancer L4 et L7 ?
  a: '**L4** répartit des connexions TCP/UDP sans lire leur contenu (rapide, tout protocole). **L7** comprend le HTTP : routage par chemin ou par en-tête, réécritures, terminaison TLS.'
- q: Quels algorithmes de répartition sont les plus courants ?
  a: '**Round robin** (chacun son tour), **least connections** (le moins chargé), **hash** (même client → même backend, par IP ou cookie).'
- q: À quoi servent les health checks d'un load balancer ?
  a: À retirer automatiquement un backend qui ne répond plus, puis à le remettre quand il redevient sain.
- q: Qu'est-ce qu'un reverse proxy ?
  a: 'Un serveur placé **devant** tes applis, qui reçoit les requêtes des clients et les transmet aux backends : nginx, HAProxy, Envoy, Traefik.'
- q: Comment le backend connaît-il l'IP réelle du client derrière un proxy ?
  a: Avec l'en-tête `X-Forwarded-For` en HTTP, ou le **PROXY protocol** en TCP. Le backend ne doit faire confiance à ces informations que si elles viennent de ses propres proxys.
- q: Qu'est-ce que le *connection draining* ?
  a: Quand un backend est retiré, le LB n'y envoie plus de nouvelles connexions mais laisse **finir** celles en cours, pendant un délai donné.
- q: Différence entre un proxy et un reverse proxy ?
  a: 'Le **proxy** agit pour les clients (sortie vers Internet). Le **reverse proxy** agit pour les serveurs : il reçoit le trafic entrant à leur place et le redistribue.'
- q: Pourquoi un L4 répartit-il mal du trafic gRPC ou HTTP/2 ?
  a: Ces protocoles font passer toutes les requêtes d'un client dans **une seule connexion**. Un L4 répartit des connexions, donc tout ce client va vers un seul serveur.
- q: Quel est le risque d'un health check qui vérifie toutes les dépendances ?
  a: 'Si une dépendance partagée ralentit (la base), **tous** les serveurs échouent au check en même temps et sont retirés : le site tombe entièrement.'
- q: Comment régler les timeouts dans une chaîne client → LB → proxy → appli ?
  a: Chaque étage doit attendre un peu plus longtemps que celui qu'il appelle, sinon il abandonne alors que l'étage suivant travaille encore (504).
quiz:
- q: Ton appli garde les sessions en mémoire, et les utilisateurs sont déconnectés au hasard. Pourquoi ?
  options:
  - Le DNS est trop lent
  - Le LB envoie les requêtes d'un même utilisateur vers des backends différents
  - Le certificat expire
  - Le MTU est trop petit
  answer: 1
  explain: 'La vraie solution : stocker les sessions en dehors (Redis, base). Les sessions collantes (affinité) sont un pansement, qui déséquilibre la charge.'
- q: Pendant un déploiement, quelques requêtes échouent à chaque fois. Que vérifier côté LB et appli ?
  options:
  - Le TTL DNS
  - Le draining du LB, l'arrêt propre sur SIGTERM et les readiness probes
  - Le nombre de zones
  - L'algorithme de hash
  answer: 1
  explain: L'appli doit finir ses requêtes avant de s'arrêter, et le LB doit cesser de lui en envoyer avant. Un `preStop` avec un court `sleep` aide souvent dans Kubernetes.
- q: Ton service gRPC a 4 réplicas derrière un NLB (L4). Un seul réplica est chargé à 100 %. Pourquoi ?
  options:
  - Le health check est cassé
  - Le client principal garde une seule connexion HTTP/2, que le L4 envoie à un seul réplica
  - Le NLB utilise round robin
  - Les 3 autres réplicas ne sont pas Ready
  answer: 1
  explain: gRPC multiplexe tout sur une connexion. Il faut un équilibrage L7 (Envoy, ALB en gRPC, service mesh) ou un équilibrage côté client.
- q: Après la mise en place de nginx, l'appli redirige sans fin vers HTTPS. Que manque-t-il probablement ?
  options:
  - '`proxy_read_timeout`'
  - '`X-Forwarded-Proto` transmis à l''appli'
  - Un upstream supplémentaire
  - '`least_conn`'
  answer: 1
  explain: 'nginx termine TLS et parle en HTTP à l''appli. Sans `X-Forwarded-Proto: https`, l''appli croit que le client est en HTTP et le redirige.'
- q: Pendant un déploiement, quelques clients reçoivent des erreurs de connexion coupée. Quel réglage regarder en priorité ?
  options:
  - L'algorithme de répartition
  - Le draining des backends retirés
  - La taille du certificat
  - Le TTL DNS
  answer: 1
  explain: Si un serveur est retiré sans laisser finir ses connexions, les requêtes en cours sont coupées.
---

Dès qu'une appli tourne sur plusieurs serveurs, il faut quelque chose devant pour **répartir** les clients et **écarter** les serveurs en panne. C'est le **load balancer** (répartiteur de charge). Le **reverse proxy** est un cousin proche : un serveur qui reçoit les requêtes à la place des applis et les leur transmet. En pratique, nginx, HAProxy, Envoy ou Traefik font les deux.

> **Les outils et sigles cités dans cette fiche.**
> - **L4** et **L7** : couche 4 (transport : TCP, UDP, ports) et couche 7 (application : HTTP) du modèle OSI, vu dans la première fiche du module.
> - **nginx**, **HAProxy**, **Envoy**, **Traefik** : logiciels de reverse proxy et de load balancing. nginx est le plus répandu, HAProxy est réputé pour ses performances, Envoy est au cœur des service mesh, Traefik se configure tout seul à partir de Docker ou Kubernetes.
> - **AWS NLB** et **AWS ALB** : les load balancers gérés d'AWS, le premier en L4 (Network), le second en L7 (Application).
> - **IPVS** : répartiteur L4 intégré au noyau Linux, utilisé notamment par kube-proxy.
> - **HTTP/2** et **gRPC** : HTTP/2 fait passer plusieurs requêtes dans une seule connexion ; gRPC est un protocole d'appel entre services construit dessus.
> - **Redis** : base de données en mémoire, très rapide, souvent utilisée pour stocker les sessions et le cache.
> - **PROXY protocol** : une petite ligne ajoutée au début de la connexion par un load balancer L4 pour transmettre l'IP réelle du client au serveur.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **hachage** : calculer une empreinte d'un contenu ; impossible de revenir au contenu à partir de l'empreinte.
> - **HTTPS** : HTTP chiffré par TLS.

## Proxy, reverse proxy : qui représente qui ?

- Un **proxy** (dit « forward ») agit pour le compte des **clients** : le proxy d'entreprise par lequel passent tous les postes pour sortir sur Internet.
- Un **reverse proxy** agit pour le compte des **serveurs** : il est devant eux, reçoit tout le trafic entrant et le redistribue. Le client ne voit jamais les vrais serveurs.

Ce qu'un reverse proxy apporte :

- un **point d'entrée unique** (une IP, un nom, un certificat) pour plusieurs services ;
- la **terminaison TLS**, pour que les applis n'aient pas à gérer les certificats ;
- la **répartition** de charge et l'éviction des serveurs malades ;
- du **routage** par nom ou par chemin, du cache, de la compression, de la limitation de débit.

## L4 ou L7 : à quel étage il travaille

On reprend les couches de la première fiche. Un load balancer peut travailler à deux niveaux :

- **L4 (transport)** : il ne voit que des IP et des ports. Il prend une **connexion** TCP entrante et la relaie telle quelle vers un serveur. Il ne sait pas ce qu'elle contient. Rapide et universel : HTTP, bases de données, n'importe quel protocole.
- **L7 (application)** : il comprend HTTP. Il lit chaque **requête** (nom, chemin, en-têtes, cookies) et peut décider en fonction : `/api` vers un service, `/` vers un autre. Il doit pour cela déchiffrer TLS.

| | L4 (TCP/UDP) | L7 (HTTP) |
| --- | --- | --- |
| Voit | IP, ports | URL, en-têtes, cookies |
| Unité répartie | une connexion | une requête |
| Routage | par port | par hôte, chemin, en-tête |
| TLS | passe tel quel | souvent terminé au LB |
| Exemples | AWS NLB, IPVS, HAProxy en mode TCP | AWS ALB, nginx, Envoy, Traefik |

<!-- schema:l4l7 -->
<figure class="diagram"><svg viewBox="0 0 680 260" role="img" aria-label="Load balancer L4 ou L7" style="--minw:560px"><defs><marker id="g13-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g13-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g13-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g13-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="316" height="232" rx="12" class="dg-zone "/><text x="26" y="32" class="dg-zl" text-anchor="start">L4 : TCP / UDP</text><g class="dg-box dg-pop" style="--d:0"><rect x="30" y="104" width="90" height="48" rx="9"/></g><text x="75.0" y="133.0" class="dg-t" text-anchor="middle" style="--d:0">client</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="146" y="98" width="90" height="60" rx="9"/></g><text x="191.0" y="125.0" class="dg-t" text-anchor="middle" style="--d:1">NLB</text><text x="191.0" y="143.0" class="dg-s" text-anchor="middle" style="--d:1">IP + port</text><g class="dg-box dg-pop" style="--d:2"><rect x="256" y="46" width="60" height="40" rx="9"/></g><text x="286.0" y="71.0" class="dg-t" text-anchor="middle" style="--d:2">srv</text><path d="M236 128 L246 128 L246 66 L254 66" class="dg-l c" marker-end="url(#g13-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="256" y="108" width="60" height="40" rx="9"/></g><text x="286.0" y="133.0" class="dg-t" text-anchor="middle" style="--d:2">srv</text><path d="M236 128 L246 128 L246 128 L254 128" class="dg-l c" marker-end="url(#g13-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="256" y="170" width="60" height="40" rx="9"/></g><text x="286.0" y="195.0" class="dg-t" text-anchor="middle" style="--d:2">srv</text><path d="M236 128 L246 128 L246 190 L254 190" class="dg-l c" marker-end="url(#g13-c)"/><path d="M120 128 L144 128" class="dg-l c" marker-end="url(#g13-c)"/><text x="172" y="232" class="dg-s" text-anchor="middle">TLS passe tel quel</text><rect x="350" y="14" width="316" height="232" rx="12" class="dg-zone dg-zc"/><text x="362" y="32" class="dg-zl" text-anchor="start">L7 : HTTP</text><g class="dg-box dg-pop" style="--d:3"><rect x="366" y="104" width="80" height="48" rx="9"/></g><text x="406.0" y="133.0" class="dg-t" text-anchor="middle" style="--d:3">client</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="466" y="92" width="90" height="72" rx="9"/></g><text x="511.0" y="118.0" class="dg-t" text-anchor="middle" style="--d:4">ALB</text><text x="511.0" y="136.0" class="dg-s" text-anchor="middle" style="--d:4"><tspan x="511.0" dy="0">lit host,</tspan><tspan x="511.0" dy="14">chemin, en-têtes</tspan></text><g class="dg-box dg-pop" style="--d:5"><rect x="578" y="44" width="74" height="50" rx="9"/></g><text x="615.0" y="66.0" class="dg-t" text-anchor="middle" style="--d:5">/</text><text x="615.0" y="84.0" class="dg-s" text-anchor="middle" style="--d:5">web</text><g class="dg-box dg-pop" style="--d:5"><rect x="578" y="162" width="74" height="50" rx="9"/></g><text x="615.0" y="184.0" class="dg-t" text-anchor="middle" style="--d:5">/api</text><text x="615.0" y="202.0" class="dg-s" text-anchor="middle" style="--d:5">api</text><path d="M446 128 L464 128" class="dg-l c" marker-end="url(#g13-c)"/><path d="M556 116 L566 116 L566 69 L576 69" class="dg-l c" marker-end="url(#g13-c)"/><path d="M556 140 L566 140 L566 187 L576 187" class="dg-l c" marker-end="url(#g13-c)"/><text x="508" y="232" class="dg-s" text-anchor="middle">TLS terminé au LB</text></svg><figcaption>Un L4 répartit des connexions, un L7 comprend les requêtes HTTP et peut router selon le contenu.</figcaption></figure>
<!-- /schema:l4l7 -->

Une conséquence utile : avec HTTP/2 ou gRPC, un client ouvre **une seule** connexion et y fait passer toutes ses requêtes. Un L4 enverra donc tout ce client vers **un seul** serveur. Pour répartir requête par requête, il faut un L7.

## Les algorithmes de répartition

| Algorithme | Principe | Quand l'utiliser |
| --- | --- | --- |
| round robin | chacun son tour | requêtes homogènes |
| least connections | le serveur qui a le moins de connexions en cours | requêtes de durée variable |
| hash (IP, cookie, en-tête) | un même client va toujours au même serveur | cache local, sessions collantes |
| pondéré | certains serveurs reçoivent plus | machines de tailles différentes |

Les **sessions collantes** (sticky sessions) dépannent une appli qui garde les sessions en mémoire, mais elles déséquilibrent la charge et perdent les sessions quand un serveur tombe. Mieux vaut stocker les sessions ailleurs (Redis, base).

## Les health checks

Le LB interroge régulièrement chaque serveur (par exemple `GET /healthz` toutes les 5 s). Après quelques échecs, il le **retire** de la rotation ; après quelques succès, il le remet.

Le choix de l'endpoint compte :

- trop **superficiel** (le process répond, mais la base est inaccessible) : le LB envoie du trafic à un serveur qui ne sert que des erreurs ;
- trop **profond** (il vérifie toutes les dépendances) : une base lente fait sortir **tous** les serveurs d'un coup, et le site tombe entièrement.

Dans Kubernetes, c'est exactement la distinction entre **readiness** (« puis-je recevoir du trafic ? ») et **liveness** (« dois-je être redémarré ? »).

## Un reverse proxy nginx, ligne par ligne

```nginx
upstream api {                               # le groupe de serveurs
    least_conn;                              # algorithme
    server 10.10.16.11:8080 max_fails=3 fail_timeout=10s;
    server 10.10.16.12:8080 max_fails=3 fail_timeout=10s;
}

server {
    listen 443 ssl;                          # écoute HTTPS
    server_name shop.example.com;            # répond pour ce Host
    ssl_certificate     /etc/ssl/shop.crt;   # terminaison TLS ici
    ssl_certificate_key /etc/ssl/shop.key;

    location /api/ {                         # routage L7 par chemin
        proxy_pass http://api;               # vers le groupe, en clair
        proxy_set_header Host $host;         # garder le nom d'origine
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # IP réelle du client
        proxy_set_header X-Forwarded-Proto $scheme;                   # le client était en HTTPS
        proxy_read_timeout 30s;              # temps max d'attente de la réponse
    }
}
```

Sans les en-têtes `X-Forwarded-*`, l'appli croit que tous les clients ont l'IP du proxy et qu'ils arrivent en HTTP, ce qui provoque des journaux inutilisables et des boucles de redirection vers HTTPS.

## Les réglages qui comptent

- **Timeouts cohérents** tout le long de la chaîne : chaque étage doit attendre un peu **plus** que celui qu'il appelle (client > LB > proxy > appli). Sinon un étage abandonne alors que l'autre travaille encore, et le client reçoit un 504.
- **Draining** (ou *connection draining*) : avant de retirer un serveur (déploiement, réduction), on arrête de lui envoyer de nouvelles connexions et on laisse finir celles en cours.
- **Keepalive** vers les backends : réutiliser les connexions évite de refaire les poignées de main TCP et TLS à chaque requête.
- **IP du client** : derrière un L4 qui ne termine pas la connexion, l'IP source peut être conservée ; derrière un L7, il faut `X-Forwarded-For` ou le **PROXY protocol**.

> **À retenir.** Un L4 répartit des connexions sans les comprendre ; un L7 lit chaque requête HTTP et peut router selon son contenu. Les health checks décident qui reçoit du trafic, et les timeouts se règlent de bout en bout : si le LB coupe à 60 s et l'appli met 90 s, le client reçoit un 504 alors que l'appli a fini son travail.
