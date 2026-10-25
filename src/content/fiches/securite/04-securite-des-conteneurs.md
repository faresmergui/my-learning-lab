---
title: Sécurité des conteneurs
chapter: 4
order: 1
duration: 10
level: intermédiaire
tags:
- CKS
- DevSecOps
cards:
- q: Un conteneur est-il une frontière de sécurité aussi forte qu'une VM ?
  a: Non. Les conteneurs partagent le **noyau** de l'hôte. Une faille du noyau ou une mauvaise config (mode privilégié, socket Docker monté) peut permettre d'en sortir.
- q: Pourquoi ne pas lancer un conteneur en root ?
  a: Si l'appli est compromise, l'attaquant est root **dans** le conteneur, et beaucoup plus près d'être root sur l'hôte en cas de faille d'isolation. `USER 10001` dans le Dockerfile.
- q: Pourquoi monter `/var/run/docker.sock` dans un conteneur est-il dangereux ?
  a: 'Il donne le contrôle total du démon Docker, donc de l''**hôte** : on peut lancer un conteneur privilégié qui monte `/`.'
- q: Qu'est-ce qu'une image *distroless* ?
  a: 'Une image qui ne contient que l''appli et ses dépendances d''exécution : **pas de shell ni de gestionnaire de paquets**. Moins de failles et moins d''outils pour un attaquant.'
- q: Comment scanner une image à la recherche de vulnérabilités connues ?
  a: '`trivy image registry.local/api:2.1` (ou Grype). À lancer dans la CI, et régulièrement sur les images déjà en production.'
- q: Pourquoi utiliser un build multi-étapes ?
  a: Pour compiler dans une image complète et ne copier que le **binaire** dans une image finale minimale. Les outils de build ne partent pas en prod.
- q: Pourquoi un conteneur isole-t-il moins qu'une VM ?
  a: Tous les conteneurs partagent le **noyau** de l'hôte. Une VM a son propre noyau. Une faille du noyau ou un conteneur trop privilégié peut mener à l'hôte.
- q: Que sont les capabilities Linux ?
  a: Les pouvoirs de root découpés en morceaux (ouvrir un port < 1024, changer l'heure, administrer le réseau…). On peut les retirer individuellement à un processus.
- q: Pourquoi `RUN rm .env` après `COPY .env` ne protège-t-il rien ?
  a: Chaque instruction crée une couche. Le fichier reste lisible dans la couche du `COPY`. Utilise `RUN --mount=type=secret`.
quiz:
- q: Quel Dockerfile est le plus sûr ?
  options:
  - '`FROM ubuntu:latest` puis `apt install` de tout ce qui peut servir'
  - Un build multi-étapes, image finale distroless, `USER` non root, tag de version fixe
  - '`FROM alpine` en root avec `chmod 777`'
  - '`FROM scratch` avec le code source'
  answer: 1
  explain: 'Image minimale, version épinglée, utilisateur non root : on réduit à la fois les failles et ce qu''un attaquant pourrait utiliser.'
- q: Trivy remonte 40 CVE dans ton image, dont 2 critiques. Par quoi commencer ?
  options:
  - Ignorer, c'est normal
  - Les 2 critiques, en regardant si un correctif existe et si le composant est réellement utilisé
  - Les 40 en même temps
  - Changer de scanner
  answer: 1
  explain: Priorise par gravité, par exploitabilité et par présence d'un correctif. Souvent, mettre à jour l'image de base en corrige la majorité.
- q: Un outil de monitoring demande `--privileged` « pour fonctionner ». Quelle est la meilleure réponse ?
  options:
  - Accepter, c'est un outil connu
  - Chercher les capabilities ou montages précis dont il a besoin et ne donner que ceux-là
  - Le lancer en root sans --privileged
  - Le lancer avec --net=host
  answer: 1
  explain: '`--privileged` revient à donner root sur l''hôte. La plupart des outils documentent les capabilities réellement nécessaires.'
- q: Trivy affiche 140 CVE sur ton image basée sur `debian:12`. Par quoi commencer ?
  options:
  - Corriger les 140 une par une
  - Ignorer, c'est normal
  - Passer à une image plus minimale et traiter d'abord les critiques avec correctif dans des composants utilisés
  - Désactiver le scan
  answer: 2
  explain: Une image minimale supprime d'un coup la plupart des paquets concernés. Ensuite, on priorise par gravité, correctif disponible et exposition réelle.
- q: Un attaquant exécute du code dans ton conteneur `--read-only --cap-drop=ALL --user 10001`. Qu'est-ce qui lui est le plus difficile ?
  options:
  - Lire les variables d'environnement
  - Installer des outils et gagner des droits sur l'hôte
  - Faire des requêtes réseau sortantes
  - Consommer du CPU
  answer: 1
  explain: 'Ces options l''empêchent d''écrire sur le disque et de disposer de droits root. Les variables restent lisibles et le réseau ouvert : d''où les NetworkPolicies et une bonne gestion des secrets en plus.'
---

Un conteneur **n'est pas une machine virtuelle**. Une VM a son propre noyau ; un conteneur est un simple processus de l'hôte, isolé par des mécanismes du noyau Linux partagé. Cette différence explique toutes les bonnes pratiques de cette fiche : si l'isolation cède, l'attaquant se retrouve sur l'hôte.


> **Les termes et outils cités dans cette fiche.**
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.
> - **PID** : le numéro qui identifie un processus en cours d'exécution.
> - **UID** : le numéro qui identifie un utilisateur sous Linux (0 = root).
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **socket** : un point de communication réseau ou local entre deux programmes.

## Ce qui isole un conteneur

| Mécanisme | Ce qu'il fait |
| --- | --- |
| **namespaces** | le processus a sa propre vue : ses PID, son réseau, ses points de montage, son nom d'hôte |
| **cgroups** | limitent ce qu'il consomme : CPU, mémoire, nombre de processus |
| **capabilities** | découpent les pouvoirs de root en morceaux (`NET_BIND_SERVICE`, `SYS_ADMIN`…) qu'on peut retirer un à un |
| **seccomp** | filtre les appels système autorisés vers le noyau |
| **AppArmor / SELinux** | limitent les fichiers et ressources accessibles |

Tout ça s'ajoute, mais ne vaut pas l'isolation d'une VM : tous les conteneurs parlent au **même noyau**. Une faille du noyau, ou un conteneur lancé avec trop de droits, peut permettre une **évasion** (*container escape*) vers l'hôte, et de là vers tous les autres conteneurs.

## Root dans un conteneur, c'est root sur l'hôte (presque)

Par défaut, l'utilisateur `root` dans un conteneur est le **même** `root` (UID 0) que sur l'hôte, simplement privé de certaines capabilities. S'il réussit à sortir de son isolation, ou si on lui a monté un répertoire de l'hôte, il agit en root. D'où la règle : faire tourner l'application avec un **utilisateur non privilégié** (`USER` dans le Dockerfile).

## Construire une image saine

```dockerfile
# Étape 1 : build, avec tous les outils de compilation
FROM golang:1.25 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/api ./cmd/api

# Étape 2 : image finale minimale, sans shell ni gestionnaire de paquets
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/api /api
USER nonroot:nonroot
ENTRYPOINT ["/api"]
```

| Bonne pratique | Pourquoi |
| --- | --- |
| Image de base minimale (distroless, alpine) | moins de paquets, donc moins de CVE et moins d'outils pour un attaquant (pas de shell, pas de `curl`) |
| Tag fixe, voire digest `@sha256:…` | build reproductible, pas de surprise si le tag change |
| Utilisateur non root | limite l'impact d'une compromission |
| Multi-étapes | les compilateurs et les sources ne partent pas en prod |
| `.dockerignore` | pas de `.git` ni de `.env` dans l'image |

<!-- schema:multistage -->
<figure class="diagram"><svg viewBox="0 0 680 210" role="img" aria-label="Un build multi-étapes" style="--minw:560px"><defs><marker id="g6-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g6-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g6-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g6-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="300" height="182" rx="12" class="dg-zone "/><text x="26" y="32" class="dg-zl" text-anchor="start">étape build</text><g class="dg-box dg-pop" style="--d:0"><rect x="30" y="44" width="268" height="40" rx="9"/></g><text x="164.0" y="61.0" class="dg-t" text-anchor="middle" style="--d:0">golang:1.25</text><text x="164.0" y="79.0" class="dg-s" text-anchor="middle" style="--d:0">compilateur, sources, cache</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="30" y="96" width="268" height="40" rx="9"/></g><text x="164.0" y="113.0" class="dg-t" text-anchor="middle" style="--d:1">go build</text><text x="164.0" y="131.0" class="dg-s" text-anchor="middle" style="--d:1">→ /out/api</text><text x="164" y="170" class="dg-s" text-anchor="middle">≈ 900 Mo, jamais déployée</text><rect x="366" y="14" width="300" height="182" rx="12" class="dg-zone dg-zc"/><text x="378" y="32" class="dg-zl" text-anchor="start">image finale</text><g class="dg-box dg-ok dg-pop" style="--d:2"><rect x="382" y="44" width="268" height="40" rx="9"/></g><text x="516.0" y="61.0" class="dg-t" text-anchor="middle" style="--d:2">distroless:nonroot</text><text x="516.0" y="79.0" class="dg-s" text-anchor="middle" style="--d:2">pas de shell, pas de paquets</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="382" y="96" width="268" height="40" rx="9"/></g><text x="516.0" y="113.0" class="dg-t" text-anchor="middle" style="--d:3">/api</text><text x="516.0" y="131.0" class="dg-s" text-anchor="middle" style="--d:3">le binaire seul</text><text x="516" y="170" class="dg-okt" text-anchor="middle">≈ 20 Mo, utilisateur non root</text><path d="M298 116 L380 116" class="dg-l c flow" marker-end="url(#g6-c)"/><text x="339.0" y="136.0" class="dg-s" text-anchor="middle">COPY --from</text></svg><figcaption>Les outils de build restent dans la première étape. L&#x27;image déployée ne contient que le binaire.</figcaption></figure>
<!-- /schema:multistage -->

Une image est un empilement de **couches**. Un fichier ajouté dans une couche puis supprimé dans la suivante reste **lisible** dans la première : `COPY .env` puis `RUN rm .env` ne cache rien. Les secrets de build passent par `RUN --mount=type=secret`, qui ne laisse aucune trace dans l'image.

## À l'exécution : retirer tout ce qui ne sert pas

```bash
docker run --read-only --cap-drop=ALL --security-opt no-new-privileges \
  --user 10001 -p 8080:8080 registry.local/api:2.1
```

| Option | Effet |
| --- | --- |
| `--read-only` | le système de fichiers est en lecture seule : un attaquant ne peut pas déposer d'outils |
| `--cap-drop=ALL` | retire toutes les capabilities ; on rajoute seulement celles nécessaires |
| `no-new-privileges` | empêche de regagner des droits via un binaire setuid |
| `--user 10001` | un UID sans privilèges, qui ne correspond à aucun compte de l'hôte |

Ce qu'on ne fait jamais sans raison très forte, et pourquoi :

| Option | Pourquoi c'est dangereux |
| --- | --- |
| `--privileged` | rend presque toutes les protections inactives : accès aux périphériques, toutes les capabilities. Équivaut à root sur l'hôte |
| monter `/var/run/docker.sock` | permet de piloter Docker, donc de lancer un conteneur `--privileged` qui monte `/` de l'hôte |
| `--net=host`, `--pid=host` | supprime l'isolation réseau ou des processus |
| monter `/` ou `/etc` de l'hôte | accès direct aux fichiers de l'hôte |

Dans Kubernetes, on retrouve exactement ces réglages dans le `securityContext` du pod (`runAsNonRoot`, `readOnlyRootFilesystem`, `capabilities.drop: [ALL]`, `allowPrivilegeEscalation: false`), et le profil Pod Security `restricted` les impose.

## Scanner les vulnérabilités

Un scanner compare la liste des paquets de l'image à une base de **CVE** connues.

```bash
trivy image --severity HIGH,CRITICAL registry.local/api:2.1
trivy image --ignore-unfixed registry.local/api:2.1   # seulement ce qui a un correctif
```

Comment lire le résultat sans paniquer :

- une image Debian complète affiche souvent des dizaines de CVE ; beaucoup sont dans des paquets que ton appli n'utilise jamais ;
- priorise : **critique ou haute**, **avec correctif disponible**, dans un composant **réellement exposé** ;
- la correction la plus efficace est souvent de **changer d'image de base** (plus récente, plus petite) plutôt que de traiter les CVE une par une.

> **À retenir.** Un conteneur partage le noyau de l'hôte : moins il a de droits, moins une évasion coûte cher. Image minimale, utilisateur non root, capabilities retirées, jamais de `--privileged` ni de socket Docker monté. Et une image saine aujourd'hui sera vulnérable dans trois mois : reconstruis régulièrement pour récupérer les correctifs.
