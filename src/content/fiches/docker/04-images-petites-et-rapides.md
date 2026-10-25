---
title: Des images petites et rapides
chapter: 4
order: 1
duration: 11
tags:
- Docker
- multi-stage
- BuildKit
cards:
- q: Qu'est-ce qu'un build multi-stage ?
  a: 'Un Dockerfile avec plusieurs `FROM` : une première étape **compile** avec tous les outils, la dernière ne **copie** que le résultat (`COPY --from=build`). L''image finale ne contient ni compilateur ni sources.'
- q: Quelles images de base pour une image finale légère ?
  a: '**alpine** (~5 Mo, musl au lieu de glibc), **-slim** des distributions (Debian réduite), **distroless** (seulement l''appli et ses bibliothèques, sans shell) ou **scratch** (vide, pour un binaire statique Go ou Rust).'
- q: Pourquoi alpine peut-il poser problème ?
  a: 'Il utilise **musl** au lieu de glibc : certains binaires précompilés (modules Python, Node natifs) ne marchent pas ou se compilent lentement, et quelques comportements (DNS, performances) diffèrent. `-slim` est souvent plus simple.'
- q: Comment partager le cache de build entre les machines de CI ?
  a: 'Avec le cache externe de BuildKit : `docker buildx build --cache-from type=registry,ref=reg/api:cache --cache-to type=registry,ref=reg/api:cache,mode=max` (ou `type=gha` sur GitHub Actions).'
- q: À quoi sert `RUN --mount=type=cache` ?
  a: 'À garder un **dossier de cache** (paquets npm, pip, apt, modules Go) d''un build à l''autre **sans** l''inclure dans l''image : `RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt`.'
- q: Comment construire une image pour amd64 et arm64 à la fois ?
  a: '`docker buildx build --platform linux/amd64,linux/arm64 -t reg/api:2.4 --push .` : buildx construit les deux et publie un **index multi-architecture** ; chaque machine tire la bonne variante.'
quiz:
- q: Une image Go fait 900 Mo car elle contient tout le SDK. Comment la réduire au maximum ?
  options:
  - Utiliser alpine pour tout
  - 'Multi-stage : compiler dans golang, copier le binaire statique dans scratch ou distroless'
  - Compresser l'image
  - Supprimer le SDK avec un RUN rm à la fin
  answer: 1
  explain: Un `RUN rm` ajoute une couche mais ne retire rien des couches précédentes. Le multi-stage ne garde que le binaire (souvent moins de 20 Mo).
- q: Le build en CI réinstalle toutes les dépendances à chaque fois alors qu'elles ne changent pas. Que fais-tu ?
  options:
  - Désactiver BuildKit
  - Un cache externe (registry ou gha) et l'ordre COPY des manifestes puis install
  - Mettre les dépendances dans le dépôt Git
  - '`--no-cache`'
  answer: 1
  explain: 'Les machines de CI sont souvent neuves : sans cache externe, chaque build repart de zéro.'
level: intermédiaire
---

Une image de 1,5 Go se télécharge lentement, démarre lentement sur un nouveau nœud, coûte en stockage et contient des centaines de paquets avec autant de failles potentielles. Une image de 50 Mo fait la même chose. Cette fiche montre comment y arriver et comment rendre les builds rapides.

> **Les outils cités dans cette fiche.**
> - **multi-stage build** : plusieurs étapes `FROM` dans un même Dockerfile, dont seule la dernière forme l'image finale.
> - **alpine** : une distribution Linux minuscule (basée sur musl et BusyBox). **musl** et **glibc** : deux bibliothèques C, la base de presque tout programme.
> - **distroless** : des images de Google sans shell ni gestionnaire de paquets, avec juste l'environnement d'exécution.
> - **scratch** : l'image vide de Docker.
> - **buildx** : la commande qui pilote BuildKit (builds multi-architecture, cache externe).
> - **dive** : un outil qui affiche le contenu de chaque couche pour repérer ce qui prend de la place.
> - **nœud** : une machine (physique ou virtuelle) membre d'un cluster.
> - **SDK** : une bibliothèque de code fournie pour utiliser un service depuis un langage de programmation.
> - **namespace** : un espace de noms : dans Kubernetes, une partition du cluster ; sous Linux, une isolation du noyau.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.

## Comprendre : pourquoi `RUN rm` ne suffit pas

```dockerfile
RUN apt-get install -y build-essential   # couche 1 : +250 Mo
RUN make                                  # couche 2
RUN apt-get purge -y build-essential      # couche 3 : marque les fichiers supprimés
```

Les couches sont empilées : la couche 3 **masque** les fichiers, mais la couche 1 les contient toujours et l'image pèse toujours 250 Mo de plus. Pour réellement ne pas embarquer les outils, il faut soit tout faire dans **un seul `RUN`**, soit utiliser le **multi-stage**.

## Le multi-stage

```dockerfile
# syntax=docker/dockerfile:1
# --- Étape 1 : compilation ---
FROM golang:1.25 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/api ./cmd/api

# --- Étape 2 : image finale ---
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/api /api
USER nonroot
ENTRYPOINT ["/api"]
```

Le même principe vaut pour toutes les technologies :

| Langage | Étape de build | Image finale |
| --- | --- | --- |
| Go, Rust | SDK complet | `scratch` ou `distroless/static` |
| Java | JDK + Maven/Gradle | JRE (`eclipse-temurin:21-jre`) ou distroless java |
| Node.js | `node` avec dépendances de dev, `npm run build` | `node:22-slim` avec `npm ci --omit=dev` |
| Python | compilation des roues (`pip wheel`) | `python:3.13-slim` + roues installées |
| front-end | `node`, `npm run build` | `nginx:alpine` avec les fichiers statiques |

`docker build --target build .` permet de s'arrêter à une étape (pour lancer les tests, par exemple).

## Choisir l'image de base

| Base | Taille | Shell | Pour |
| --- | --- | --- | --- |
| `debian`, `ubuntu` | 70-120 Mo | oui | outils, compatibilité maximale |
| `*-slim` | 30-80 Mo | oui | bon compromis par défaut |
| `alpine` | 5-10 Mo | oui (BusyBox) | très léger, attention à musl |
| `distroless` | 2-20 Mo | **non** | production, surface d'attaque minimale |
| `scratch` | 0 | non | binaire statique |

Sans shell, `docker exec … sh` est impossible : on débogue avec `docker debug` ou un **conteneur éphémère** qui partage les namespaces (`kubectl debug` dans Kubernetes).

## Des builds rapides

1. **Ordre des instructions** : manifestes de dépendances, installation, puis code.
2. **`.dockerignore`** pour un contexte petit.
3. **Montages de cache** BuildKit, gardés entre builds mais absents de l'image :

```dockerfile
RUN --mount=type=cache,target=/root/.npm npm ci
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends libpq5
```

4. **Cache externe** en CI, où chaque machine est neuve :

```bash
docker buildx build \
  --cache-from type=registry,ref=registry.shop.fr/api:cache \
  --cache-to   type=registry,ref=registry.shop.fr/api:cache,mode=max \
  -t registry.shop.fr/api:2.4.1 --push .
```

5. **Étapes parallèles** : BuildKit construit en même temps les étapes indépendantes d'un multi-stage.

## Plusieurs architectures

Les Mac récents et les instances Graviton sont en **arm64**, beaucoup de serveurs en **amd64**. Une image construite sur un Mac M peut refuser de démarrer sur un serveur Intel (`exec format error`).

```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t registry.shop.fr/api:2.4.1 --push .
docker buildx imagetools inspect registry.shop.fr/api:2.4.1   # les variantes publiées
```

## Mesurer

```bash
docker images api                    # taille finale
docker image history api:2.4.1       # taille par couche
dive api:2.4.1                       # exploration couche par couche
```

> **À retenir.** Supprimer dans une couche suivante n'allège rien : multi-stage ou un seul `RUN`. Image finale slim, distroless ou scratch selon le besoin. Builds rapides : ordre des instructions, `.dockerignore`, `--mount=type=cache`, cache externe en CI. `buildx --platform` pour publier amd64 et arm64 ensemble.
