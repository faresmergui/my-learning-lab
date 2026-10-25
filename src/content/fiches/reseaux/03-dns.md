---
title: DNS
chapter: 3
order: 1
duration: 10
level: intermédiaire
tags:
- fondamentaux
cards:
- q: Quels types d'enregistrements DNS faut-il connaître ?
  a: '`A` (IPv4), `AAAA` (IPv6), `CNAME` (alias vers un autre nom), `MX` (mail), `TXT` (texte, vérifications, SPF), `NS` (serveurs de la zone), `SRV` (service et port).'
- q: Que représente le TTL d'un enregistrement ?
  a: La durée en secondes pendant laquelle les résolveurs peuvent **garder la réponse en cache**. On le baisse quelques heures avant une migration pour qu'elle se propage vite.
- q: Pourquoi ne peut-on pas mettre un CNAME à la racine d'un domaine (`example.com`) ?
  a: Un CNAME ne peut cohabiter avec aucun autre enregistrement, or la racine a toujours `NS` et `SOA`. Les hébergeurs proposent des alias (ALIAS, ANAME, alias Route 53) à la place.
- q: Différence entre un résolveur récursif et un serveur faisant autorité ?
  a: Le **récursif** (celui de ton FAI, 1.1.1.1, CoreDNS) cherche la réponse pour toi et la met en cache. Le serveur **faisant autorité** détient la zone et donne la réponse officielle.
- q: À quoi sert `ndots:5` dans le `resolv.conf` d'un pod Kubernetes ?
  a: 'Un nom avec moins de 5 points est d''abord essayé avec chaque **domaine de recherche** (`.ns.svc.cluster.local`…). D''où beaucoup de requêtes inutiles pour les noms externes, sauf avec un point final : `api.example.com.`.'
- q: Comment se lit un nom de domaine comme `api.shop.fr.` ?
  a: 'De droite à gauche : la racine `.`, le TLD `fr`, le domaine `shop.fr` (la zone de l''entreprise), puis le nom `api` dans cette zone. Chaque niveau délègue le suivant.'
- q: Que signifient `NXDOMAIN` et `SERVFAIL` dans une réponse `dig` ?
  a: '`NXDOMAIN` : le nom n''existe pas (réponse officielle). `SERVFAIL` : le résolveur n''a pas réussi à obtenir de réponse (autorité injoignable, DNSSEC cassé…).'
- q: Pourquoi `getent hosts` peut-il donner une autre réponse que `dig` ?
  a: '`getent` suit l''ordre du système (`/etc/nsswitch.conf`) et lit `/etc/hosts` avant le DNS. `dig` interroge uniquement le serveur DNS.'
quiz:
- q: Tu changes l'IP d'un enregistrement A dont le TTL est de 86 400. Combien de temps certains clients peuvent-ils garder l'ancienne IP ?
  options:
  - Quelques secondes
  - Jusqu'à 24 heures
  - 1 heure maximum
  - Jusqu'au redémarrage du serveur DNS
  answer: 1
  explain: 86 400 s = 24 h. Baisse le TTL (par exemple à 300) la veille d'une migration, puis remonte-le une fois la migration faite.
- q: Quelle commande montre toute la chaîne de résolution, de la racine jusqu'à la réponse ?
  options:
  - dig +trace example.com
  - nslookup -debug
  - host -a example.com
  - ping example.com
  answer: 0
  explain: '`+trace` interroge les serveurs racine, puis ceux du TLD, puis ceux qui font autorité. Pratique pour voir où une délégation casse.'
- q: Tu viens de créer `new.shop.fr`, mais l'avais testé 2 minutes avant (introuvable). `dig` répond toujours NXDOMAIN. Explication probable ?
  options:
  - L'enregistrement est mal saisi
  - La réponse négative est en cache dans le résolveur
  - Le TTL de la zone est de 24 h
  - Il faut redémarrer CoreDNS
  answer: 1
  explain: Les réponses négatives ont aussi une durée de cache. Interroge directement l'autorité (`dig @ns…`) pour vérifier que l'enregistrement existe.
- q: '`dig api.interne` renvoie la bonne IP, mais l''appli se connecte à une ancienne adresse. Premier réflexe ?'
  options:
  - Vider le cache de CoreDNS
  - Vérifier `getent hosts api.interne` et `/etc/hosts`
  - Baisser le TTL
  - Passer en IPv6
  answer: 1
  explain: L'appli passe par la résolution du système, qui consulte `/etc/hosts` avant le DNS. Certaines applis gardent aussi leur propre cache.
---

Les machines communiquent avec des adresses IP, mais les humains et les fichiers de configuration utilisent des **noms** (`api.shop.fr`). Le **DNS** (Domain Name System) fait la traduction. C'est un annuaire mondial, réparti entre des millions de serveurs.

Presque toute connexion commence par une question DNS. Quand il tombe ou répond faux, tout semble tomber en même temps, d'où le dicton « c'est toujours le DNS ».


> **Les termes et outils cités dans cette fiche.**
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.

## Un nom se lit de droite à gauche

`api.shop.fr.` se lit comme une adresse postale à l'envers :

- `.` (souvent invisible) : la **racine**, le sommet de l'annuaire ;
- `fr` : le **TLD** (domaine de premier niveau), géré par l'AFNIC ;
- `shop.fr` : le **domaine**, acheté par l'entreprise, qui en gère la **zone** ;
- `api` : un nom dans cette zone, choisi librement par l'entreprise.

Personne ne connaît tout l'annuaire. Chaque niveau sait seulement **à qui déléguer** le niveau suivant. C'est ce qui permet au système de tenir à l'échelle d'Internet.

## Deux rôles à ne pas confondre

- Le **résolveur récursif** : celui à qui ta machine pose la question (la box, celui du FAI, `1.1.1.1`, `8.8.8.8`, CoreDNS dans Kubernetes). Il ne détient aucune zone ; il **va chercher** la réponse pour toi, puis la garde en **cache**.
- Le **serveur faisant autorité** : celui qui détient la zone (`shop.fr`) et donne la réponse officielle. Chez un hébergeur DNS, Route 53, Cloudflare…

Ta machine ne parle qu'au récursif. Elle trouve son adresse dans `/etc/resolv.conf` (ou via `resolvectl status` avec systemd-resolved).

## Une résolution complète

<!-- schema:resolution -->
<figure class="diagram"><svg viewBox="0 0 680 260" role="img" aria-label="Une résolution DNS complète" style="--minw:560px"><defs><marker id="g11-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g11-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g11-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g11-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="14" y="100" width="100" height="52" rx="9"/></g><text x="64.0" y="123.0" class="dg-t" text-anchor="middle" style="--d:0">appli</text><text x="64.0" y="141.0" class="dg-s" text-anchor="middle" style="--d:0">api.shop.fr ?</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="154" y="100" width="130" height="52" rx="9"/></g><text x="219.0" y="123.0" class="dg-t" text-anchor="middle" style="--d:1">résolveur</text><text x="219.0" y="141.0" class="dg-s" text-anchor="middle" style="--d:1">récursif · cache</text><g class="dg-box dg-pop" style="--d:2"><rect x="430" y="20" width="220" height="60" rx="9"/></g><text x="540.0" y="47.0" class="dg-t" text-anchor="middle" style="--d:2">racine .</text><text x="540.0" y="65.0" class="dg-s" text-anchor="middle" style="--d:2">« .fr : voir là »</text><path d="M284 108 L360 108 L360 44 L428 44" class="dg-l c" marker-end="url(#g11-c)" style="--d:2"/><circle cx="400" cy="44" r="9" class="dg-dot dg-c dg-pop" style="--d:2"/><text x="400" y="48" class="dg-w" text-anchor="middle" style="--d:2">2</text><g class="dg-box dg-pop" style="--d:3"><rect x="430" y="100" width="220" height="60" rx="9"/></g><text x="540.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:3">serveur .fr</text><text x="540.0" y="145.0" class="dg-s" text-anchor="middle" style="--d:3">« shop.fr : voir là »</text><path d="M284 116 L360 116 L360 124 L428 124" class="dg-l c" marker-end="url(#g11-c)" style="--d:3"/><circle cx="400" cy="124" r="9" class="dg-dot dg-c dg-pop" style="--d:3"/><text x="400" y="128" class="dg-w" text-anchor="middle" style="--d:3">3</text><g class="dg-box dg-ok dg-pop" style="--d:4"><rect x="430" y="180" width="220" height="60" rx="9"/></g><text x="540.0" y="200.0" class="dg-t" text-anchor="middle" style="--d:4">shop.fr</text><text x="540.0" y="218.0" class="dg-s" text-anchor="middle" style="--d:4"><tspan x="540.0" dy="0">faisant autorité</tspan><tspan x="540.0" dy="14">« 51.15.2.10 »</tspan></text><path d="M284 124 L360 124 L360 204 L428 204" class="dg-l c" marker-end="url(#g11-c)" style="--d:4"/><circle cx="400" cy="204" r="9" class="dg-dot dg-c dg-pop" style="--d:4"/><text x="400" y="208" class="dg-w" text-anchor="middle" style="--d:4">4</text><path d="M114 120 L152 120" class="dg-l c" marker-end="url(#g11-c)"/><circle cx="133" cy="120" r="9" class="dg-dot dg-c dg-pop"/><text x="133" y="124" class="dg-w" text-anchor="middle">1</text><path d="M152 136 L116 136" class="dg-l ok thick" marker-end="url(#g11-ok)"/><text x="134" y="176" class="dg-s" text-anchor="middle">réponse,</text><text x="134" y="190" class="dg-s" text-anchor="middle">mise en cache</text><text x="134" y="204" class="dg-s" text-anchor="middle">selon le TTL</text></svg><figcaption>Le résolveur fait tout le travail. La prochaine fois, il répondra depuis son cache tant que le TTL n&#x27;est pas écoulé.</figcaption></figure>
<!-- /schema:resolution -->

1. L'appli demande `api.shop.fr` au résolveur.
2. S'il n'a rien en cache, il demande à la **racine**, qui répond « je ne sais pas, mais `.fr` est géré par ces serveurs ».
3. Il demande aux serveurs de `.fr` : « `shop.fr` est délégué à ces serveurs-là ».
4. Il demande aux serveurs faisant autorité de `shop.fr`, qui donnent l'IP.
5. Il renvoie la réponse à l'appli et la garde en cache.

En pratique, les étapes 2 et 3 sont presque toujours en cache, et la résolution prend quelques millisecondes.

## Le cache et le TTL

Chaque réponse porte un **TTL** (Time To Live) en secondes : la durée pendant laquelle on a le droit de la garder en cache. Il y a des caches **partout** : le résolveur, le système (systemd-resolved), parfois l'application elle-même (Java, certains navigateurs).

Conséquence directe : quand tu changes un enregistrement, **l'ancien reste visible** jusqu'à l'expiration du TTL dans chaque cache. Avec un TTL de 86 400 s, certains clients verront l'ancienne IP pendant 24 h. D'où la règle : baisser le TTL (300 s par exemple) **la veille** d'une migration, migrer, puis le remonter.

Les réponses négatives (« ce nom n'existe pas », `NXDOMAIN`) sont aussi mises en cache. Si tu crées un enregistrement juste après l'avoir demandé, il peut rester « introuvable » quelques minutes.

## Les enregistrements

Une zone contient des **enregistrements** de différents types :

| Type | Rôle | Exemple |
| --- | --- | --- |
| `A` / `AAAA` | nom → IPv4 / IPv6 | `api  A  10.10.1.20` |
| `CNAME` | alias : « va voir ce nom-là » | `www  CNAME  shop.example.com.` |
| `MX` | serveur de mail du domaine | `@  MX 10  mail.example.com.` |
| `TXT` | texte libre | SPF, vérification de domaine, ACME |
| `NS` | serveurs faisant autorité de la zone | délégation |
| `SRV` | service + port | `_sip._tcp` |
| `PTR` | IP → nom (résolution inverse) | `20.1.10.10.in-addr.arpa` |

Deux subtilités du `CNAME` :

- il ne peut **cohabiter avec aucun autre** enregistrement du même nom. Or la racine d'un domaine (`example.com`) porte toujours `NS` et `SOA` : pas de CNAME possible là. Les hébergeurs proposent des « alias » (ALIAS, ANAME, alias Route 53) qui contournent la règle ;
- le point final (`shop.example.com.`) dit « ce nom est complet ». Sans lui, certains outils ajoutent le nom de la zone derrière.

## Diagnostiquer

La démarche : **qu'est-ce que voit mon appli**, puis **qu'est-ce que dit la source officielle**, et comparer.

```bash
getent hosts api.example.com          # ce que voit l'appli (inclut /etc/hosts)
dig +short api.example.com            # réponse du résolveur configuré
dig api.example.com @8.8.8.8          # comparer avec un autre résolveur
dig api.example.com @ns1.hebergeur.net  # interroger directement l'autorité
dig +trace example.com                # toute la chaîne depuis la racine
dig -x 10.10.1.20                     # résolution inverse
```

Dans la sortie complète de `dig`, regarde le **status** (`NOERROR`, `NXDOMAIN` = le nom n'existe pas, `SERVFAIL` = le résolveur n'a pas pu obtenir de réponse) et le TTL restant à côté de chaque réponse.

Piège classique : `/etc/hosts` est consulté **avant** le DNS (selon `/etc/nsswitch.conf`). Une vieille ligne oubliée dedans gagne sur tout le reste, et `dig` ne la voit pas, alors que `getent` si.

## Dans Kubernetes

Chaque pod utilise **CoreDNS** comme résolveur. Chaque Service reçoit un nom automatique :

```
api                                → api.<ns>.svc.cluster.local   (même namespace)
api.shop                           → api.shop.svc.cluster.local   (autre namespace)
db-0.db.shop.svc.cluster.local     → un pod précis d'un StatefulSet
```

Les noms courts marchent grâce aux **domaines de recherche** du `resolv.conf` du pod : le système essaie `api.<ns>.svc.cluster.local`, puis `api.svc.cluster.local`, etc. Avec l'option `ndots:5`, un nom qui contient moins de 5 points passe d'abord par toute cette liste. Un nom externe comme `api.stripe.com` génère donc plusieurs requêtes inutiles avant la bonne. Le point final (`api.stripe.com.`) l'évite.

> **À retenir.** Ta machine parle à un résolveur qui cache tout selon le TTL. Avant une migration, baisse le TTL un jour à l'avance. En cas de doute, compare ce que voit l'appli (`getent`), le résolveur (`dig`) et l'autorité (`dig @ns…`).
