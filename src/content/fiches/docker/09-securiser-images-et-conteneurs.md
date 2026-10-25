---
title: Sécuriser images et conteneurs
chapter: 9
order: 1
duration: 11
tags:
- Docker
- sécurité
- Trivy
cards:
- q: Pourquoi faire tourner un conteneur en non root ?
  a: Sans user namespaces, **root dans le conteneur est root sur l'hôte** (même UID 0). Une faille d'évasion ou un montage mal choisi donne alors tout. `USER` dans le Dockerfile ou `--user` au lancement réduisent fortement l'impact.
- q: Que fait `--privileged` et pourquoi l'éviter ?
  a: 'Il donne **toutes** les capabilities, l''accès à tous les périphériques et désactive seccomp et AppArmor : le conteneur peut presque tout faire sur l''hôte. On donne plutôt la capability précise nécessaire (`--cap-add NET_ADMIN`).'
- q: Pourquoi le socket Docker est-il si sensible ?
  a: 'Qui peut parler à `/var/run/docker.sock` peut lancer un conteneur privilégié qui monte `/` de l''hôte : c''est l''**équivalent de root**. Le monter dans un conteneur, ou mettre un utilisateur dans le groupe `docker`, revient à lui donner root.'
- q: Qu'est-ce que le mode rootless ?
  a: 'Le démon Docker (ou Podman) tourne **sous un utilisateur ordinaire** et utilise les user namespaces : root dans le conteneur correspond à un UID non privilégié sur l''hôte. Une évasion ne donne pas root sur la machine.'
- q: Comment scanner une image pour les vulnérabilités ?
  a: '`trivy image registry.shop.fr/api:2.4.1` (ou Grype, Docker Scout, le scan du registre). En CI : `--severity HIGH,CRITICAL --exit-code 1` pour bloquer, et `--ignore-unfixed` pour ne pas bloquer sur ce qui n''a pas de correctif.'
- q: Quelles options de `docker run` durcissent un conteneur ?
  a: '`--user 1000:1000`, `--read-only` (+ `--tmpfs /tmp`), `--cap-drop ALL` (+ `--cap-add` du strict nécessaire), `--security-opt no-new-privileges`, des limites `--memory`, `--cpus`, `--pids-limit`, et ne publier que les ports nécessaires.'
quiz:
- q: Un outil de supervision demande à monter `/var/run/docker.sock`. Que réponds-tu ?
  options:
  - C'est sans risque en lecture seule
  - 'C''est un accès équivalent à root sur l''hôte : à n''accepter que pour un outil de confiance, ou via un proxy qui filtre l''API'
  - Il faut juste `--read-only`
  - Impossible techniquement
  answer: 1
  explain: Même monté `:ro`, le socket permet d'appeler toute l'API. Un proxy de socket peut n'autoriser que la lecture des informations.
- q: Trivy trouve 300 vulnérabilités dans une image basée sur `python:3.13`. Premier levier ?
  options:
  - Ignorer le rapport
  - Passer à une base plus petite (`-slim` ou distroless) et reconstruire régulièrement
  - Désactiver le scan
  - Ajouter un pare-feu
  answer: 1
  explain: La plupart viennent de paquets inutiles de la base. Moins de paquets, moins de failles ; une reconstruction régulière récupère les correctifs.
level: intermédiaire
---

Un conteneur isole, mais moins qu'une machine virtuelle : il partage le noyau de l'hôte. Sa sécurité repose donc sur deux choses : une **image** propre (peu de composants, à jour, de source connue) et un **lancement** qui retire les droits inutiles. La fiche Sécurité sur les conteneurs explique les mécanismes du noyau ; celle-ci donne la liste de contrôle pratique pour Docker.

> **Les outils cités dans cette fiche.**
> - **capabilities** : les droits de root découpés en morceaux (`NET_ADMIN`, `SYS_ADMIN`, `CHOWN`…), qu'on peut donner ou retirer un par un.
> - **seccomp** : un filtre des appels système ; Docker en applique un par défaut. **AppArmor** / **SELinux** : limitent les fichiers et ressources accessibles.
> - **user namespaces** et **mode rootless** : root dans le conteneur ne correspond plus à root sur l'hôte.
> - **Trivy**, **Grype**, **Docker Scout** : des scanners de vulnérabilités d'images.
> - **Hadolint** : un analyseur de Dockerfile qui signale les mauvaises pratiques.
> - **CVE** : l'identifiant public d'une vulnérabilité connue.
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **socket** : un point de communication réseau ou local entre deux programmes.
> - **cgroups** : le mécanisme du noyau Linux qui limite et mesure les ressources (CPU, mémoire) d'un groupe de processus.
> - **démon** : un programme qui tourne en arrière-plan en permanence (sshd, dockerd).
> - **TLS** : le protocole qui chiffre une connexion et prouve l'identité du serveur par un certificat.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.

## Comprendre : où sont les risques

| Risque | Exemple | Parade |
| --- | --- | --- |
| image vulnérable | une bibliothèque avec une CVE critique | base minimale, scan, reconstruction régulière |
| image piégée | image inconnue de Docker Hub avec un mineur | images officielles ou internes, signatures |
| secret dans l'image | clé d'API dans une couche | secrets BuildKit, scan de secrets |
| conteneur trop puissant | `--privileged`, root, socket Docker monté | non root, capabilities retirées, pas de socket |
| évasion vers l'hôte | faille du noyau ou du runtime | correctifs, rootless, gVisor pour le non fiable |
| déni de service | un conteneur qui prend toute la mémoire | limites cgroups |

## Une image saine

1. **Base officielle ou interne**, version figée, la plus petite possible (slim, distroless).
2. **Multi-stage** : aucun compilateur, aucune source dans l'image finale.
3. **`USER` non root** et fichiers de l'appli non modifiables par cet utilisateur.
4. **Aucun secret** dans les couches (vérifier avec `docker history` et un scanner de secrets).
5. **Scan** à chaque build et **reconstruction régulière** (chaque semaine) pour récupérer les correctifs de la base, même si le code n'a pas changé.

```bash
hadolint Dockerfile
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 registry.shop.fr/api:2.4.1
trivy image --scanners secret registry.shop.fr/api:2.4.1
```

## Un lancement durci

```bash
docker run -d --name api \
  --user 1000:1000 \
  --read-only --tmpfs /tmp:size=64m \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --memory 512m --cpus 1 --pids-limit 200 \
  -p 127.0.0.1:3000:3000 \
  registry.shop.fr/api:2.4.1
```

| Option | Empêche |
| --- | --- |
| `--user` | d'agir en root si l'appli est compromise |
| `--read-only` | de modifier les binaires ou de déposer un outil |
| `--cap-drop ALL` | d'utiliser les pouvoirs de root inutiles |
| `no-new-privileges` | de regagner des droits via un binaire SUID |
| `--memory`, `--pids-limit` | d'épuiser l'hôte (fuite mémoire, fork bomb) |
| `127.0.0.1:` | d'exposer le port à tout le réseau |

En Compose, les mêmes réglages s'écrivent `user:`, `read_only: true`, `cap_drop: [ALL]`, `security_opt: [no-new-privileges:true]`.

## Ce qu'il ne faut jamais faire sans raison forte

- `--privileged` : presque tous les droits sur l'hôte.
- Monter `/var/run/docker.sock` : **équivalent root** sur l'hôte. Mettre un utilisateur dans le groupe `docker` aussi.
- `--network host` et `--pid host` : plus d'isolation réseau ou des processus.
- Monter `/`, `/etc` ou `/proc` de l'hôte.

## Le démon lui-même

- Garder Docker et containerd **à jour** (les failles du runtime permettent des évasions).
- Envisager le **mode rootless** (ou Podman, sans démon root) sur les machines partagées.
- Ne jamais exposer l'API Docker sur le réseau sans TLS mutuel (port 2375 sans chiffrement = machine compromise).
- Journaliser les actions du démon et centraliser les logs.
- Dans Kubernetes, ces réglages deviennent le `securityContext` et Pod Security (module Kubernetes, chapitre 8).

> **À retenir.** Image minimale, figée, multi-stage, non root, sans secret, scannée et reconstruite régulièrement. Lancement avec `--user`, `--read-only`, `--cap-drop ALL`, `no-new-privileges` et des limites. `--privileged`, le socket Docker et le groupe `docker` valent root sur l'hôte.
