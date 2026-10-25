---
title: Docker Compose
chapter: 7
order: 1
duration: 11
tags:
- Docker
- Compose
cards:
- q: À quoi sert Docker Compose ?
  a: 'À décrire dans un fichier `compose.yaml` une application **multi-conteneurs** (services, réseaux, volumes, variables) et à la lancer d''une commande : `docker compose up -d`.'
- q: Que crée Compose automatiquement ?
  a: Un **réseau** par projet où chaque service est joignable par **son nom**, les volumes déclarés, et des noms de conteneurs préfixés par le nom du projet (le dossier par défaut, ou `-p`, ou `name:`).
- q: '`depends_on` attend-il que la base soit prête ?'
  a: 'Par défaut, il attend seulement que le conteneur soit **démarré**. Avec `condition: service_healthy` et un `healthcheck` sur la base, Compose attend qu''elle soit **saine** avant de lancer le service dépendant.'
- q: Comment avoir une configuration différente en dev et en prod ?
  a: 'Un `compose.yaml` commun et un `compose.override.yaml` (lu automatiquement) pour le dev, ou des fichiers explicites : `docker compose -f compose.yaml -f compose.prod.yaml up -d`. Aussi les **profiles** pour activer des services optionnels.'
- q: Différence entre `docker compose down` et `down -v` ?
  a: '`down` arrête et supprime conteneurs et réseaux ; les **volumes restent**. `down -v` supprime aussi les volumes nommés du projet : les données sont perdues.'
- q: Comment Compose lit-il les variables comme `${TAG}` ?
  a: Depuis l'environnement du shell, puis le fichier `.env` du dossier du projet. `${TAG:-latest}` donne une valeur par défaut, `${DB_PASS:?obligatoire}` provoque une erreur si elle manque.
quiz:
- q: L'API démarre avant que PostgreSQL accepte les connexions et plante. Correction propre ?
  options:
  - Un `sleep 10` dans l'API
  - 'Un healthcheck sur la base et `depends_on: {db: {condition: service_healthy}}`'
  - Lancer les services à la main dans l'ordre
  - '`restart: always` seulement'
  answer: 1
  explain: Compose attend alors l'état sain. L'API doit tout de même savoir se reconnecter, car la base peut redémarrer plus tard.
- q: Tu as modifié le Dockerfile de l'API. `docker compose up -d` lance encore l'ancienne version. Pourquoi ?
  options:
  - Compose ne gère pas les Dockerfile
  - L'image existante est réutilisée ; il faut `up -d --build` (ou `docker compose build`)
  - Il faut `down -v`
  - Le cache réseau
  answer: 1
  explain: Compose ne reconstruit pas de lui-même une image déjà présente.
level: intermédiaire
---

Une application réelle, c'est rarement un seul conteneur : une API, une base, un cache, un worker, un proxy. Les lancer un par un avec de longues commandes `docker run` devient vite ingérable. **Docker Compose** décrit tout cela dans un fichier YAML versionné avec le code. C'est l'outil standard pour le développement local, les tests et les petits déploiements sur une seule machine.

> **Les outils cités dans cette fiche.**
> - **Docker Compose** : l'outil qui lance une application multi-conteneurs depuis un fichier `compose.yaml`. On l'utilise avec `docker compose` (la version 2, intégrée à Docker).
> - **service** : dans Compose, un conteneur (ou plusieurs répliques) décrit avec son image, ses ports, ses volumes et ses variables.
> - **projet** : l'ensemble des services d'un fichier Compose, isolés des autres projets par un préfixe de nom.
> - **healthcheck** : une commande qui indique si un conteneur est vraiment prêt.
> - **Valkey** / **Redis** : des bases clé-valeur en mémoire, souvent utilisées comme cache.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **proxy** : un intermédiaire qui reçoit les requêtes et les transmet à leur place.
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.

## Un fichier complet

```yaml
# compose.yaml
name: shop

services:
  db:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:?à définir dans .env}
      POSTGRES_DB: shop
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10

  cache:
    image: valkey/valkey:8

  api:
    build: ./api                      # construit depuis ./api/Dockerfile
    image: registry.shop.fr/api:${TAG:-dev}
    environment:
      DATABASE_URL: postgres://postgres:${DB_PASSWORD}@db:5432/shop
      CACHE_URL: redis://cache:6379
    depends_on:
      db: { condition: service_healthy }
      cache: { condition: service_started }
    ports:
      - "127.0.0.1:3000:3000"
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: "1", memory: 512M }

  worker:
    image: registry.shop.fr/api:${TAG:-dev}
    command: ["node", "worker.js"]
    depends_on: [db, cache]
    profiles: [jobs]                  # lancé seulement avec --profile jobs

volumes:
  pgdata:
```

```
# .env (jamais commité)
DB_PASSWORD=change-moi
TAG=2.4.1
```

## Les commandes

```bash
docker compose up -d               # créer et lancer (reconstruire avec --build)
docker compose ps
docker compose logs -f api
docker compose exec api sh
docker compose run --rm api npm test   # une commande ponctuelle dans un nouveau conteneur
docker compose pull && docker compose up -d   # mettre à jour les images
docker compose up -d --scale worker=3 --profile jobs
docker compose config              # le fichier final, variables remplacées : très utile
docker compose down                # tout arrêter (volumes gardés) ; -v : volumes supprimés
```

## Comprendre : ce que Compose fait pour toi

- un **réseau** `shop_default` où `db`, `cache`, `api` se trouvent par leur nom ;
- des **volumes** préfixés (`shop_pgdata`) ;
- l'**ordre de démarrage** selon `depends_on`, et l'attente de l'état sain avec `condition: service_healthy` ;
- la **recréation** seulement des services dont la configuration ou l'image a changé.

`depends_on` règle le démarrage, pas la vie de l'application : si la base redémarre plus tard, l'API doit savoir se reconnecter.

## Développement et production

| Besoin | Moyen |
| --- | --- |
| configuration de dev automatique | `compose.override.yaml`, lu en plus de `compose.yaml` |
| fichier de prod explicite | `docker compose -f compose.yaml -f compose.prod.yaml up -d` |
| services optionnels (outils, jobs) | `profiles` |
| recharger le code en direct | bind mount en dev, ou `develop: watch` (synchronisation automatique) |
| secrets | `secrets:` (montés en fichiers dans `/run/secrets/`) plutôt que des variables |

```yaml
# compose.override.yaml (dev)
services:
  api:
    volumes: ["./api/src:/app/src"]
    environment: { LOG_LEVEL: debug }
```

## Compose, Swarm ou Kubernetes ?

Compose gère **une seule machine**. Pour plusieurs machines, la haute disponibilité et le passage à l'échelle automatique, on passe à un orchestrateur : **Kubernetes** dans la plupart des entreprises (des outils comme Kompose traduisent un fichier Compose en manifestes), ou Docker Swarm, plus simple mais peu utilisé. Compose reste l'outil idéal pour le poste du développeur et la CI (lancer une base de test le temps des tests).

> **À retenir.** Un `compose.yaml` décrit services, volumes et réseaux ; `docker compose up -d` lance tout, `down` arrête (et `-v` efface les données). Les services se trouvent par leur nom. `depends_on` avec `service_healthy` pour l'ordre, `.env` pour les variables, override et profiles pour adapter. `docker compose config` montre le fichier réellement appliqué.
