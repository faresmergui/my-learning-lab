---
title: HTTP et TLS côté réseau
chapter: 4
order: 1
duration: 9
level: intermédiaire
tags:
- fondamentaux
cards:
- q: Que signifient les familles de codes HTTP ?
  a: '**2xx** succès, **3xx** redirection, **4xx** erreur du **client** (requête invalide, non autorisé, introuvable), **5xx** erreur du **serveur**.'
- q: Différence entre 401 et 403 ?
  a: '**401** : tu n''es pas authentifié (ou ton jeton est invalide). **403** : tu es authentifié, mais tu n''as pas le droit.'
- q: Différence entre 502, 503 et 504 ?
  a: '**502** : le proxy a reçu une réponse invalide du backend. **503** : service indisponible (aucun backend sain, surcharge). **504** : le backend n''a pas répondu à temps.'
- q: Qu'apporte HTTP/2, et HTTP/3 ?
  a: '**HTTP/2** : plusieurs requêtes en parallèle sur une seule connexion TCP, en-têtes compressés. **HTTP/3** : la même chose sur **QUIC** (UDP), sans blocage quand un paquet est perdu.'
- q: À quoi sert le SNI dans TLS ?
  a: Le client envoie le **nom du site** dès le début de la connexion TLS. Le serveur peut ainsi choisir le bon certificat quand plusieurs sites partagent une même IP.
- q: Que signifie « HTTP est sans état » ?
  a: Le serveur ne garde aucun souvenir entre deux requêtes. Pour savoir qui tu es, le client renvoie à chaque requête un cookie ou un jeton.
- q: À quoi sert l'en-tête `Host` ?
  a: 'À dire quel site on demande. Une même IP peut héberger de nombreux sites : le serveur ou le proxy choisit le bon grâce à `Host`.'
- q: Pourquoi les proxys ajoutent-ils `X-Forwarded-For` ?
  a: Parce que l'appli voit l'IP du proxy comme source. L'en-tête transmet l'IP réelle du client.
- q: Qu'apporte HTTP/2 par rapport à HTTP/1.1 ?
  a: 'Le **multiplexage** : plusieurs requêtes en parallèle sur une seule connexion, au lieu d''une à la fois par connexion.'
quiz:
- q: Ton Ingress renvoie 502 Bad Gateway. Où chercher ?
  options:
  - Dans le navigateur du client
  - 'Entre le proxy et le backend : pod en erreur, mauvais port, protocole (HTTP contre HTTPS)'
  - Dans le DNS public
  - Dans le certificat du client
  answer: 1
  explain: Le proxy fonctionne mais n'obtient pas de réponse valide. Vérifie le `targetPort`, les logs du pod, et si le backend attend du HTTPS.
- q: Une API renvoie 429. Que faut-il faire côté client ?
  options:
  - Réessayer immédiatement en boucle
  - Ralentir et réessayer plus tard, en respectant l'en-tête `Retry-After`
  - Changer d'adresse IP
  - Passer en HTTP/1.0
  answer: 1
  explain: 429 = trop de requêtes. Un backoff exponentiel avec un peu d'aléatoire évite de saturer le serveur.
- q: '`curl -w` donne : dns=0.004 tcp=0.020 tls=0.045 ttfb=1.900 total=1.950. Où chercher ?'
  options:
  - Le DNS
  - Le réseau entre client et serveur
  - L'application ou sa base de données
  - Le certificat TLS
  answer: 2
  explain: 'Tout est rapide jusqu''à TLS. Ensuite 1,85 s d''attente avant le premier octet : le serveur traite la requête lentement.'
- q: Tu mets un Ingress devant un service qui écoute en HTTPS sur 8443. Toutes les requêtes renvoient 502. Cause probable ?
  options:
  - Le DNS ne pointe pas vers l'Ingress
  - L'Ingress parle HTTP en clair à un backend qui attend du TLS
  - Les pods ne sont pas Ready
  - Le client n'a pas de certificat
  answer: 1
  explain: 502 = réponse invalide du backend. Un désaccord HTTP/HTTPS entre proxy et backend en est la cause la plus fréquente.
- q: Un utilisateur reçoit 403 sur `/admin`. Qu'en déduis-tu ?
  options:
  - Il n'est pas connecté
  - Il est identifié mais n'a pas les droits
  - La page n'existe pas
  - Le serveur est en panne
  answer: 1
  explain: 401 = on ne sait pas qui tu es ; 403 = on sait qui tu es, mais c'est interdit.
---

HTTP est le langage du web et de la plupart des API. Côté infra, tu ne l'écris pas, mais tu passes ton temps à **lire** ses requêtes, ses codes de réponse et ses temps de réponse pour savoir qui est en tort : le client, le proxy, le réseau ou l'application.


> **Les termes et outils cités dans cette fiche.**
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **JSON** : un format texte de données en paires « clé : valeur », lisible par les humains et les programmes.
> - **HTTPS** : HTTP chiffré par TLS.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).

## Le principe : une question, une réponse

Le client envoie une **requête**, le serveur renvoie une **réponse**. Chaque échange est indépendant : le serveur ne se souvient de rien entre deux requêtes (on dit que HTTP est **sans état**). Les sessions de connexion reposent donc sur des **cookies** ou des **jetons** que le client renvoie à chaque fois.

Une requête contient :

- une **méthode** : `GET` (lire), `POST` (créer, envoyer), `PUT`/`PATCH` (modifier), `DELETE` ;
- un **chemin** : `/api/health` ;
- des **en-têtes** : des lignes `Nom: valeur` qui donnent le contexte ;
- éventuellement un **corps** (le JSON envoyé, un fichier…).

La réponse contient un **code** de statut, des en-têtes et un corps.

## Anatomie d'une requête

```bash
curl -v https://shop.example.com/api/health
# > GET /api/health HTTP/2           ← méthode, chemin, version
# > Host: shop.example.com           ← quel site on demande
# > User-Agent: curl/8.x
# < HTTP/2 200                       ← la réponse : code 200
# < content-type: application/json
# < server: envoy                    ← qui a produit la réponse
```

Avec `-v`, les lignes `>` sont envoyées, les lignes `<` reçues. Les lignes `*` racontent la connexion (DNS, TCP, TLS) : c'est souvent là que se lit le problème.

Les en-têtes utiles côté infra :

| En-tête | Rôle |
| --- | --- |
| `Host` | le nom du site demandé. Une seule IP peut héberger cent sites : le serveur choisit grâce à lui |
| `X-Forwarded-For` / `X-Forwarded-Proto` | ajoutés par les proxys pour transmettre l'IP réelle du client et le protocole d'origine |
| `Server`, `Via` | qui a généré ou relayé la réponse |
| `Cache-Control` | ce qui peut être mis en cache, et combien de temps |
| `Authorization` | le jeton d'authentification |

## Les codes à connaître par cœur

Le premier chiffre dit déjà beaucoup : **2xx** ça a marché, **3xx** va voir ailleurs, **4xx** la faute est côté client, **5xx** la faute est côté serveur (ou d'un intermédiaire).

| Code | Sens | Piste typique |
| --- | --- | --- |
| 200 / 201 / 204 | OK, créé, pas de contenu | rien à faire |
| 301 / 302 / 308 | redirection | boucle HTTP ↔ HTTPS ? |
| 400 | requête invalide | format, en-têtes |
| 401 / 403 | non authentifié / authentifié mais interdit | jeton, droits |
| 404 | introuvable | chemin, règle d'Ingress, mauvais `Host` |
| 429 | trop de requêtes | limite de débit |
| 500 | erreur de l'appli | logs de l'appli |
| 502 | le proxy a reçu une réponse invalide du backend | mauvais port, HTTP vs HTTPS, pod qui crashe |
| 503 | aucun backend disponible | pods pas Ready, surcharge |
| 504 | le backend a mis trop de temps | timeouts, requêtes longues |

502, 503 et 504 sont presque toujours renvoyés **par un proxy** (load balancer, Ingress) et non par ton application. L'appli peut très bien ne jamais avoir vu la requête.

## Les versions de HTTP

| Version | Transport | Ce qui change |
| --- | --- | --- |
| HTTP/1.1 | TCP | une requête à la fois par connexion ; les navigateurs ouvrent 6 connexions en parallèle |
| HTTP/2 | TCP + TLS | plusieurs requêtes **en même temps** sur une seule connexion (multiplexage) |
| HTTP/3 | QUIC sur UDP | évite qu'un paquet perdu bloque toutes les requêtes ; connexion plus rapide |

## Mesurer où part le temps

Une requête « lente » peut l'être à cinq endroits différents. `curl` sait chronométrer chaque étape :

```bash
curl -o /dev/null -s -w 'dns=%{time_namelookup} tcp=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total}\n' \
  https://shop.example.com
```

<!-- schema:waterfall -->
<figure class="diagram"><svg viewBox="0 0 680 220" role="img" aria-label="Où part le temps d&#x27;une requête HTTPS" style="--minw:560px"><defs><marker id="g12-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g12-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g12-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g12-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="20" y="40" width="48.627450980392155" height="24" rx="4"/></g><text x="76.62745098039215" y="57" class="dg-s" text-anchor="start" style="--d:0">DNS · 20 ms</text><g class="dg-box dg-pop" style="--d:1"><rect x="68.62745098039215" y="70" width="72.94117647058823" height="24" rx="4"/></g><text x="149.5686274509804" y="87" class="dg-s" text-anchor="start" style="--d:1">TCP · 30 ms</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="141.5686274509804" y="100" width="109.41176470588235" height="24" rx="4"/></g><text x="258.98039215686276" y="117" class="dg-s" text-anchor="start" style="--d:2">TLS · 45 ms</text><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="250.98039215686273" y="130" width="291.7647058823529" height="24" rx="4"/></g><text x="396.8627450980392" y="147" class="dg-s" text-anchor="middle" style="--d:3">attente serveur · 120 ms</text><g class="dg-box dg-ok dg-pop" style="--d:4"><rect x="542.7450980392157" y="160" width="97.25490196078431" height="24" rx="4"/></g><text x="534.7450980392157" y="177" class="dg-s" text-anchor="end" style="--d:4">téléchargement · 40 ms</text><line x1="542.7450980392157" y1="30" x2="542.7450980392157" y2="196" class="dg-court"/><text x="542.7450980392157" y="210" class="dg-at" text-anchor="middle">ttfb</text><text x="640" y="210" class="dg-s" text-anchor="end">total</text><text x="20" y="24" class="dg-s" text-anchor="start">time_namelookup → time_connect → time_appconnect → time_starttransfer → time_total</text></svg><figcaption>Ici, c&#x27;est l&#x27;attente serveur qui domine : il faut regarder l&#x27;application, pas le réseau.</figcaption></figure>
<!-- /schema:waterfall -->

Les valeurs sont **cumulées** depuis le début :

- `dns` élevé : résolution lente (résolveur, `ndots` dans Kubernetes) ;
- `tcp − dns` élevé : la distance ou un réseau chargé (c'est un aller-retour) ;
- `tls − tcp` élevé : la poignée de main TLS (deux allers-retours en TLS 1.2, un en 1.3) ;
- `ttfb − tls` élevé : le **serveur réfléchit**, c'est l'application ou sa base de données ;
- `total − ttfb` élevé : la réponse est grosse ou le débit faible.

## TLS côté réseau

HTTPS, c'est HTTP à l'intérieur d'un tunnel **TLS** chiffré (la fiche suivante explique TLS en détail). Ce qui compte ici, c'est **où** ce tunnel s'arrête. Un proxy placé devant l'appli a trois options :

| Mode | Ce que fait le proxy | Conséquence |
| --- | --- | --- |
| **Terminaison** | il déchiffre, puis parle en clair au backend | il peut lire et router selon le chemin ; le certificat est sur le proxy |
| **Ré-chiffrement** | il déchiffre, puis rechiffre vers le backend | même chose, mais le trafic interne reste chiffré |
| **Passthrough** | il ne déchiffre rien, il route selon le **SNI** (le nom demandé, visible au début de TLS) | le certificat est sur le backend ; le proxy ne voit pas le chemin |

Un 502 juste après avoir mis un proxy devant un service est souvent un désaccord de protocole : le proxy parle HTTP à un backend qui attend HTTPS, ou l'inverse.

> **À retenir.** 4xx : la requête est en cause ; 5xx : le serveur ou un intermédiaire. 502, 503 et 504 viennent presque toujours d'un proxy : regarde l'en-tête `server` et les logs du proxy avant ceux de l'appli, et utilise `curl -w` pour savoir quelle étape est lente.
