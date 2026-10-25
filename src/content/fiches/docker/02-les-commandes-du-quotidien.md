---
title: Les commandes du quotidien
chapter: 2
order: 1
duration: 10
tags:
- Docker
- CLI
cards:
- q: Différence entre `docker run`, `docker create` et `docker start` ?
  a: '`docker create` crée un conteneur sans le lancer, `docker start` lance un conteneur existant, `docker run` fait les deux (et télécharge l''image si besoin).'
- q: Comment entrer dans un conteneur qui tourne ?
  a: '`docker exec -it <nom> sh` (ou `bash` s''il existe). Cela lance un **nouveau** processus dans les namespaces du conteneur ; `docker attach` se branche sur le processus principal, à éviter.'
- q: Différence entre `docker stop` et `docker kill` ?
  a: '`stop` envoie **SIGTERM**, attend 10 s (réglable avec `-t`) puis envoie **SIGKILL**. `kill` envoie directement SIGKILL (ou le signal choisi avec `-s`).'
- q: Comment voir pourquoi un conteneur s'est arrêté ?
  a: '`docker ps -a` (statut et code de sortie), `docker logs <nom>`, et `docker inspect <nom> --format ''{{.State.ExitCode}} {{.State.OOMKilled}}''`. Code 137 = tué par SIGKILL (souvent la mémoire), 143 = SIGTERM, 1 = erreur de l''appli.'
- q: Comment faire le ménage sur une machine ?
  a: '`docker system df` pour voir, puis `docker container prune`, `docker image prune` (images sans tag) ou `docker image prune -a` (toutes les images inutilisées), `docker volume prune`, ou `docker system prune` pour tout ce qui est arrêté ou orphelin.'
- q: À quoi sert `--rm` ?
  a: 'À supprimer automatiquement le conteneur quand il s''arrête. Idéal pour une commande ponctuelle : `docker run --rm -it alpine sh`.'
quiz:
- q: Un conteneur s'arrête aussitôt lancé avec le code 0. Pourquoi, le plus souvent ?
  options:
  - Une erreur de réseau
  - Son processus principal s'est terminé normalement (une commande qui finit, un service lancé en arrière-plan)
  - Il manque de mémoire
  - L'image est corrompue
  answer: 1
  explain: Un conteneur vit tant que son processus principal vit. Un service doit tourner au premier plan (`nginx -g 'daemon off;'`).
- q: Comment copier un fichier de log depuis un conteneur vers l'hôte ?
  options:
  - '`docker exec cat` puis copier-coller'
  - '`docker cp web:/var/log/nginx/error.log .`'
  - '`docker commit`'
  - Impossible
  answer: 1
  explain: '`docker cp` fonctionne dans les deux sens, même sur un conteneur arrêté.'
level: intermédiaire
---

Une vingtaine de commandes couvrent presque tout l'usage quotidien de Docker. Les retenir par **objet** (conteneur, image, volume, réseau) et par **verbe** (ls, inspect, rm, prune) rend la CLI très régulière.

> **Les outils cités dans cette fiche.**
> - **docker CLI** : la commande `docker`, qui parle à l'API du démon dockerd.
> - **Docker Hub** : le registre public d'images par défaut (`docker.io`).
> - **SIGTERM** et **SIGKILL** : les signaux d'arrêt ; le premier demande poliment, le second tue immédiatement (voir la fiche Linux sur les processus).
> - **jq** : un outil qui lit et filtre du JSON en ligne de commande.
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.

## Comprendre : la grammaire de la CLI

```
docker <objet> <verbe> [options]
         │        └── ls, inspect, rm, prune, create…
         └── container, image, volume, network, system, builder
```

Les commandes courtes historiques restent valables : `docker ps` = `docker container ls`, `docker rmi` = `docker image rm`.

## Lancer

```bash
docker run -d --name web -p 8080:80 nginx:1.27          # en arrière-plan
docker run --rm -it alpine:3.20 sh                       # interactif, supprimé à la sortie
docker run -d --name api \
  -e NODE_ENV=production --env-file .env \
  -v donnees:/data -p 127.0.0.1:3000:3000 \
  --restart unless-stopped --memory 512m \
  registry.shop.fr/api:2.4.1
```

| Option | Rôle |
| --- | --- |
| `-d` | détaché (arrière-plan) |
| `-it` | interactif avec un terminal |
| `--name` | un nom lisible au lieu d'un nom aléatoire |
| `-p hôte:conteneur` | publier un port ; `127.0.0.1:` pour ne l'ouvrir qu'en local |
| `-e`, `--env-file` | variables d'environnement |
| `-v`, `--mount` | volumes et montages |
| `--restart` | `no`, `on-failure`, `unless-stopped`, `always` |
| `--rm` | supprimer à l'arrêt |
| `--entrypoint` | remplacer le point d'entrée de l'image |

## Observer

```bash
docker ps                      # en cours ; -a : tous ; -q : seulement les ID
docker logs -f --tail 100 web  # suivre les logs ; --since 10m
docker stats                   # CPU, mémoire, réseau en direct
docker top web                 # processus du conteneur
docker inspect web             # tout : IP, montages, variables, état
docker inspect -f '{{.NetworkSettings.IPAddress}}' web
docker port web                # ports publiés
docker events                  # ce que fait le démon, en direct
```

## Intervenir

```bash
docker exec -it web sh         # un shell dans le conteneur
docker exec web nginx -t       # une commande ponctuelle
docker cp web:/etc/nginx/nginx.conf .      # copier vers l'hôte (ou l'inverse)
docker stop web                # SIGTERM, puis SIGKILL après 10 s
docker restart web
docker rm -f web               # arrêter et supprimer
```

## Les images

```bash
docker pull postgres:17
docker images                  # = docker image ls
docker image inspect postgres:17
docker tag api:dev registry.shop.fr/api:2.4.1
docker push registry.shop.fr/api:2.4.1
docker rmi api:dev
docker save -o api.tar api:2.4.1 && docker load -i api.tar   # transfert sans registre
```

## Faire le ménage

Docker accumule vite : conteneurs arrêtés, images intermédiaires, volumes orphelins, cache de build.

```bash
docker system df                     # combien, où
docker container prune               # conteneurs arrêtés
docker image prune -a                # images inutilisées
docker volume prune                  # volumes sans conteneur (attention aux données)
docker builder prune                 # cache de build
docker system prune -a --volumes     # tout (à réserver aux machines de dev)
```

## Lire un code de sortie

| Code | Signification |
| --- | --- |
| 0 | le processus s'est terminé normalement |
| 1, 2… | erreur de l'application |
| 125 | Docker n'a pas pu lancer le conteneur (option invalide) |
| 126 / 127 | commande non exécutable / introuvable |
| 137 | tué par SIGKILL (souvent dépassement mémoire : vérifier `OOMKilled`) |
| 143 | arrêté par SIGTERM |

> **À retenir.** `docker <objet> <verbe>` : run, ps, logs, exec, inspect, stop, rm. `--rm` pour le ponctuel, `--restart unless-stopped` pour un service, `-p 127.0.0.1:` pour ne pas exposer. Un conteneur vit tant que son processus principal vit. `docker system df` puis `prune` pour récupérer de la place.
