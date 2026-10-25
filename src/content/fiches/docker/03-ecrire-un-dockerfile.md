---
title: Écrire un Dockerfile
chapter: 3
order: 1
duration: 12
tags:
- Docker
- Dockerfile
cards:
- q: Différence entre `RUN`, `CMD` et `ENTRYPOINT` ?
  a: '`RUN` s''exécute **pendant le build** et crée une couche. `ENTRYPOINT` est le programme lancé au **démarrage** du conteneur ; `CMD` donne ses arguments par défaut (ou la commande entière s''il n''y a pas d''ENTRYPOINT). Les arguments de `docker run` remplacent `CMD`.'
- q: Pourquoi préférer la forme exec `CMD ["node", "server.js"]` à la forme shell `CMD node server.js` ?
  a: 'La forme exec lance le programme **directement** comme PID 1 : il reçoit SIGTERM et s''arrête proprement. La forme shell le lance via `/bin/sh -c`, qui ne transmet pas les signaux : `docker stop` attend 10 s puis tue.'
- q: Différence entre `COPY` et `ADD` ?
  a: '`COPY` copie des fichiers du contexte. `ADD` sait aussi décompresser une archive locale et télécharger une URL. On utilise `COPY` par défaut, `ADD` seulement pour ses fonctions précises.'
- q: Différence entre `ARG` et `ENV` ?
  a: '`ARG` est une variable **du build** (`--build-arg`), absente de l''image finale. `ENV` est une variable d''environnement **de l''image**, visible par le conteneur. Aucun des deux ne convient aux secrets.'
- q: Qu'est-ce que le contexte de build ?
  a: Le dossier envoyé au builder (le `.` de `docker build .`). `COPY` ne peut prendre que des fichiers de ce contexte. Un fichier `.dockerignore` en exclut ce qui est inutile ou sensible (`.git`, `node_modules`, `.env`).
- q: Comment passer un secret pendant le build sans qu'il reste dans l'image ?
  a: 'Avec un **secret BuildKit** : `RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci` et `docker build --secret id=npmrc,src=$HOME/.npmrc .`. Le fichier n''est monté que pendant cette instruction et n''est écrit dans aucune couche.'
quiz:
- q: '`docker stop` met toujours 10 secondes à arrêter ton conteneur. Cause probable ?'
  options:
  - Le réseau est lent
  - Le CMD en forme shell empêche l'appli de recevoir SIGTERM
  - L'image est trop grosse
  - Un volume est monté
  answer: 1
  explain: Passe à la forme exec (`CMD ["..."]`) ou ajoute `exec` dans le script d'entrée, ou un mini init (`--init`, tini).
- q: Tu écris `RUN apt-get update` puis, sur une autre ligne, `RUN apt-get install -y curl`. Quel risque ?
  options:
  - Aucun
  - La couche `update` peut être reprise du cache, ancienne, et l'installation échouer ou installer des versions périmées
  - L'image ne démarre pas
  - curl n'est pas installable
  answer: 1
  explain: On les met dans le même `RUN`, et on supprime `/var/lib/apt/lists/*` à la fin pour alléger la couche.
- q: Un mot de passe est passé par `ARG` puis utilisé dans un `RUN`. Est-il protégé ?
  options:
  - Oui, ARG n'est pas dans l'image
  - Non, il peut apparaître dans l'historique de l'image et les métadonnées du build
  - Oui, si on supprime le fichier après
  - Seulement en multi-stage
  answer: 1
  explain: '`docker history` peut révéler les valeurs. Les secrets passent par `--mount=type=secret`.'
level: intermédiaire
---

Un **Dockerfile** est la recette d'une image : une suite d'instructions exécutées dans l'ordre, chacune ajoutant une couche ou une métadonnée. Un bon Dockerfile donne une image reproductible, légère, rapide à reconstruire et qui s'arrête proprement.

> **Les outils cités dans cette fiche.**
> - **Dockerfile** : le fichier texte qui décrit comment construire une image.
> - **BuildKit** : le moteur de build moderne de Docker (par défaut), avec cache avancé, builds parallèles et secrets. **buildx** est la commande qui l'expose (`docker buildx build`).
> - **contexte de build** : le dossier envoyé au builder ; **.dockerignore** en exclut des fichiers.
> - **PID 1** : le premier processus du conteneur ; il doit relayer les signaux et récupérer les processus zombies.
> - **tini** : un mini système d'init qui joue ce rôle de PID 1 (`docker run --init` l'ajoute).
> - **SIGTERM** : le signal qui demande poliment à un processus de s'arrêter.

## Un premier Dockerfile commenté

```dockerfile
# syntax=docker/dockerfile:1
# Image de base, version figée
FROM node:22-alpine

# Dossier de travail (créé s'il n'existe pas)
WORKDIR /app

# Les dépendances d'abord : cette couche reste en cache tant qu'elles ne changent pas
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Le code ensuite, car il change souvent
COPY . .

ENV NODE_ENV=production
# Documentation : le port écouté (ne publie rien)
EXPOSE 3000
# Ne pas tourner en root
USER node

HEALTHCHECK --interval=30s CMD wget -qO- http://localhost:3000/health || exit 1
# Forme exec : le processus reçoit SIGTERM
CMD ["node", "server.js"]
```

Attention : dans un Dockerfile, un commentaire doit être **sur sa propre ligne**. Un `#` placé après une instruction ferait partie de ses arguments.

```bash
docker build -t api:dev .
docker run --rm -p 3000:3000 api:dev
```

## Les instructions

| Instruction | Moment | Rôle |
| --- | --- | --- |
| `FROM` | build | image de départ ; plusieurs `FROM` = multi-stage |
| `RUN` | build | exécuter une commande, crée une couche |
| `COPY` / `ADD` | build | copier depuis le contexte (ADD : archives et URL en plus) |
| `WORKDIR` | build et exécution | dossier courant |
| `ARG` | build | variable de build (`--build-arg`) |
| `ENV` | build et exécution | variable d'environnement de l'image |
| `USER` | build et exécution | utilisateur des instructions suivantes et du conteneur |
| `EXPOSE` | métadonnée | port documenté (ne publie rien) |
| `VOLUME` | métadonnée | dossier destiné à un volume |
| `LABEL` | métadonnée | informations (version, source, mainteneur) |
| `HEALTHCHECK` | exécution | commande de vérification de santé |
| `ENTRYPOINT` / `CMD` | exécution | ce qui est lancé au démarrage |

## ENTRYPOINT et CMD

```dockerfile
ENTRYPOINT ["python", "-m", "outil"]
CMD ["--help"]
```

- `docker run outil` lance `python -m outil --help` ;
- `docker run outil rapport --mois 10` lance `python -m outil rapport --mois 10`.

ENTRYPOINT fixe le programme, CMD donne les arguments remplaçables. Un **script d'entrée** (`entrypoint.sh`) qui prépare des choses doit finir par `exec "$@"` pour que l'appli devienne PID 1 et reçoive les signaux.

## Le cache de build

Docker réutilise une couche si l'instruction **et** tout ce qui la précède n'ont pas changé (pour `COPY`, le contenu des fichiers copiés). Dès qu'une couche change, **toutes les suivantes** sont reconstruites. D'où la règle : **ce qui change rarement en haut, ce qui change souvent en bas**.

```dockerfile
# Mauvais : tout changement de code relance npm ci
COPY . .
RUN npm ci

# Bon : npm ci n'est relancé que si les dépendances changent
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

## Les bonnes habitudes

- **Figer les versions** : `FROM python:3.13-slim`, pas `python:latest` ; idéalement par empreinte (`@sha256:…`) en production.
- **Un seul `RUN` par logique**, et nettoyer dans la même instruction :

```dockerfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
```

- **.dockerignore** : `.git`, `node_modules`, `*.log`, `.env`, `dist` : un contexte plus petit, un build plus rapide, aucun secret envoyé.
- **`USER` non root** à la fin.
- **Pas de secrets** dans `ARG`, `ENV` ou un fichier copié : utiliser les secrets BuildKit.

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```

```bash
docker build --secret id=npmrc,src=$HOME/.npmrc -t api .
```

- **Un processus par conteneur** : l'appli au premier plan, ses logs sur la sortie standard.

> **À retenir.** Un Dockerfile s'écrit du plus stable au plus changeant pour profiter du cache. `RUN` agit au build, `ENTRYPOINT` et `CMD` au démarrage, en forme exec pour recevoir SIGTERM. Versions figées, `.dockerignore`, `USER` non root, et les secrets par `--mount=type=secret`, jamais par ARG ou ENV.
