---
title: Synthèse Docker
description: "Conteneurs, commandes, Dockerfile, images légères, volumes, réseau, Compose, registres, sécurité et débogage."
---

## Ce qu'est un conteneur

- Un **processus de l'hôte**, isolé par les **namespaces** (pid, net, mnt, uts, ipc, user), limité par les **cgroups** (CPU, mémoire, pids), lancé sur les **couches** d'une image.
- Il partage le **noyau** de l'hôte : isolation plus légère qu'une VM.
- Couches en lecture seule et partagées + une couche écrivable perdue à la suppression.
- `docker` → `dockerd` → `containerd` → `runc` ; images **OCI** compatibles partout.

## Les commandes

```bash
docker run -d --name web -p 127.0.0.1:8080:80 --restart unless-stopped --memory 512m nginx:1.27
docker run --rm -it alpine:3.20 sh
docker ps -a; docker logs -f --tail 100 web; docker stats; docker inspect web
docker exec -it web sh; docker cp web:/etc/nginx/nginx.conf .
docker stop web    # SIGTERM puis SIGKILL après 10 s
docker system df; docker system prune
```

| Code | Sens |
| --- | --- |
| 0 | fin normale (souvent : service lancé en arrière-plan) |
| 1 | erreur de l'appli |
| 137 | SIGKILL, souvent `OOMKilled` |
| 143 | SIGTERM |

## Le Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev
COPY . .
USER node
HEALTHCHECK CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "server.js"]
```

- Du plus stable au plus changeant pour le **cache**.
- `RUN` au build ; `ENTRYPOINT` (programme) + `CMD` (arguments) au démarrage, en **forme exec**.
- `.dockerignore`, versions figées, `USER` non root, secrets par `--mount=type=secret` (jamais ARG ou ENV).
- Un commentaire `#` sur sa propre ligne.

## Des images légères

- `RUN rm` dans une couche suivante n'allège rien : **multi-stage** (`COPY --from=build`).
- Bases : slim (défaut), alpine (attention à musl), distroless (sans shell), scratch (binaire statique).
- CI : cache externe (`--cache-from/--cache-to type=registry`), `--platform linux/amd64,linux/arm64`.

## Volumes et réseau

| Montage | Pour |
| --- | --- |
| volume nommé | données (survit au conteneur) |
| bind mount | dev, configuration en lecture seule |
| tmpfs | temporaire en mémoire |

- `--mount` plus sûr que `-v` ; les droits dépendent des **UID** ; `:z` avec SELinux.
- Un **réseau créé par l'utilisateur** par application : DNS par nom de conteneur.
- L'appli écoute sur `0.0.0.0` ; publier sur `127.0.0.1:` ce qui n'est pas public : **Docker passe avant ufw**.
- `--network container:<nom> nicolaka/netshoot` pour déboguer.

## Compose

```bash
docker compose up -d --build; docker compose ps; docker compose logs -f api
docker compose exec api sh; docker compose config; docker compose down   # -v efface les volumes
```

- Services joignables par leur nom ; `depends_on` + `condition: service_healthy`.
- `.env` pour les variables (`${VAR:?}` obligatoire), `compose.override.yaml` pour le dev, `profiles` pour l'optionnel.
- Une seule machine : au-delà, Kubernetes.

## Registres

- `registre/espace/dépôt:tag@sha256:…` ; défaut `docker.io/library/…:latest`.
- Tag **mobile**, digest **fixe** : déployer une version immuable, jamais `latest`.
- En entreprise : Harbor, ECR, GitLab, GHCR ; cache proxy (limites de Docker Hub), rétention, scan, signature **cosign**, SBOM.

## Sécurité

```bash
docker run --user 1000:1000 --read-only --tmpfs /tmp --cap-drop ALL \
  --security-opt no-new-privileges --memory 512m --pids-limit 200 image:1.0
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 image:1.0
```

- `--privileged`, le **socket Docker** et le groupe `docker` = root sur l'hôte.
- Rootless ou Podman sur les machines partagées ; reconstruire les images chaque semaine.

## Exploiter

- `daemon.json` : rotation des logs (`max-size`, `max-file`), `live-restore`, `default-address-pools`, `registry-mirrors`.
- HEALTHCHECK + `--restart unless-stopped` + limites.
- Méthode : `ps -a` → `logs` → `inspect` → `exec` → netshoot / `docker debug` → `events`.
- `exec format error` : mauvaise architecture ; service d'entreprise injoignable : plage Docker qui chevauche.
