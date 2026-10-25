---
title: Volumes et données
chapter: 5
order: 1
duration: 10
tags:
- Docker
- volumes
cards:
- q: Quels sont les trois types de montages Docker ?
  a: Le **volume** (géré par Docker dans `/var/lib/docker/volumes`, le choix par défaut pour les données), le **bind mount** (un dossier précis de l'hôte, pratique en développement) et le **tmpfs** (en mémoire, effacé à l'arrêt).
- q: Que devient un volume quand on supprime le conteneur ?
  a: Il **reste**. `docker rm -v` supprime seulement les volumes anonymes du conteneur ; un volume nommé ne disparaît qu'avec `docker volume rm` ou `docker volume prune`.
- q: Pourquoi `--mount` plutôt que `-v` ?
  a: '`--mount type=bind,src=…,dst=…,readonly` est plus explicite. Avec `-v`, un chemin hôte inexistant est **créé vide** (dossier appartenant à root) au lieu de provoquer une erreur.'
- q: Comment sauvegarder un volume ?
  a: 'Lancer un conteneur temporaire qui monte le volume et un dossier de l''hôte, et archiver : `docker run --rm -v donnees:/data:ro -v $PWD:/backup alpine tar czf /backup/donnees.tgz -C /data .`. Pour une base, préférer son outil de dump (`pg_dump`).'
- q: Pourquoi un conteneur non root n'arrive-t-il pas à écrire dans un bind mount ?
  a: 'Les **UID** sont ceux de l''hôte : si le dossier appartient à root (UID 0) et que l''appli tourne en UID 1000, l''écriture est refusée. On ajuste le propriétaire du dossier ou l''utilisateur du conteneur (`--user`).'
quiz:
- q: Une base PostgreSQL en conteneur perd ses données à chaque recréation. Cause ?
  options:
  - Le port n'est pas publié
  - Ses données ne sont pas dans un volume
  - L'image est trop ancienne
  - Il manque `--rm`
  answer: 1
  explain: Sans volume sur `/var/lib/postgresql/data`, tout est dans la couche écrivable, supprimée avec le conteneur.
- q: En développement, tu veux voir tes modifications de code sans reconstruire l'image. Que montes-tu ?
  options:
  - Un volume nommé
  - Un bind mount du dossier du code
  - Un tmpfs
  - Rien, il faut reconstruire
  answer: 1
  explain: Le bind mount fait voir au conteneur les fichiers de l'hôte en direct ; en production, le code reste dans l'image.
level: intermédiaire
---

Un conteneur est jetable : tout ce qu'il écrit dans sa couche écrivable disparaît quand on le supprime. Les **données qui doivent survivre** (bases, fichiers envoyés par les utilisateurs, certificats) vont dans un montage. Bien choisir le type de montage évite les pertes de données et les problèmes de droits.

> **Les outils cités dans cette fiche.**
> - **volume** : un espace de stockage géré par Docker, indépendant du cycle de vie des conteneurs.
> - **bind mount** : un dossier ou fichier de l'hôte monté tel quel dans le conteneur.
> - **tmpfs** : un système de fichiers en mémoire vive.
> - **pilote de volume** (volume driver) : un plugin qui place les volumes ailleurs que sur le disque local (NFS, stockage cloud).
> - **UID** : le numéro d'un utilisateur Linux ; c'est lui, et non le nom, qui compte pour les droits sur les fichiers.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.
> - **namespace** : un espace de noms : dans Kubernetes, une partition du cluster ; sous Linux, une isolation du noyau.
> - **socket** : un point de communication réseau ou local entre deux programmes.

## Comprendre : trois façons de monter

<!-- schema:montages -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Volume, bind mount et tmpfs" style="--minw:560px"><defs><marker id="g8-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g8-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g8-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g8-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="129" y="22" class="dg-zl" text-anchor="middle">hôte</text><text x="551" y="22" class="dg-zl" text-anchor="middle">conteneur</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="14" y="36" width="230" height="52" rx="9"/></g><text x="129.0" y="59.0" class="dg-t" text-anchor="middle" style="--d:0">volume pgdata</text><text x="129.0" y="77.0" class="dg-s" text-anchor="middle" style="--d:0">/var/lib/docker/volumes/…</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="436" y="36" width="230" height="52" rx="9"/></g><text x="551.0" y="67.0" class="dg-t" text-anchor="middle" style="--d:0">/var/lib/postgresql/data</text><path d="M244 62 L434 62" class="dg-l c" marker-end="url(#g8-c)" style="--d:0"/><text x="339.0" y="54.0" class="dg-s" text-anchor="middle" style="--d:0">volume : géré par Docker, survit</text><g class="dg-box dg-pop" style="--d:1"><rect x="14" y="106" width="230" height="52" rx="9"/></g><text x="129.0" y="129.0" class="dg-t" text-anchor="middle" style="--d:1">dossier du projet</text><text x="129.0" y="147.0" class="dg-s" text-anchor="middle" style="--d:1">/home/fares/projet/src</text><g class="dg-box dg-pop" style="--d:1"><rect x="436" y="106" width="230" height="52" rx="9"/></g><text x="551.0" y="137.0" class="dg-t" text-anchor="middle" style="--d:1">/app/src</text><path d="M244 132 L434 132" class="dg-l" marker-end="url(#g8-n)" style="--d:1"/><text x="339.0" y="124.0" class="dg-s" text-anchor="middle" style="--d:1">bind mount : pratique en dev</text><g class="dg-box dg-pop" style="--d:2"><rect x="14" y="176" width="230" height="52" rx="9"/></g><text x="129.0" y="199.0" class="dg-t" text-anchor="middle" style="--d:2">mémoire</text><text x="129.0" y="217.0" class="dg-s" text-anchor="middle" style="--d:2">RAM</text><g class="dg-box dg-pop" style="--d:2"><rect x="436" y="176" width="230" height="52" rx="9"/></g><text x="551.0" y="207.0" class="dg-t" text-anchor="middle" style="--d:2">/tmp</text><path d="M244 202 L434 202" class="dg-l" marker-end="url(#g8-n)" style="--d:2"/><text x="339.0" y="194.0" class="dg-s" text-anchor="middle" style="--d:2">tmpfs : effacé à l&#x27;arrêt</text></svg><figcaption>Les données qui comptent vont dans un volume : elles survivent à la suppression du conteneur.</figcaption></figure>
<!-- /schema:montages -->

| | Volume | Bind mount | tmpfs |
| --- | --- | --- | --- |
| géré par | Docker | toi (chemin de l'hôte) | le noyau, en RAM |
| survit au conteneur | oui | oui (c'est l'hôte) | non |
| portable | oui (nom) | dépend du chemin de l'hôte | oui |
| usage | données de production | développement, fichiers de config | secrets temporaires, cache rapide |
| volume vide au premier montage | rempli avec le contenu de l'image à cet endroit | **masque** le contenu de l'image | vide |

## Les commandes

```bash
docker volume create pgdata
docker run -d --name db -e POSTGRES_PASSWORD=secret \
  --mount type=volume,src=pgdata,dst=/var/lib/postgresql/data postgres:17

docker run -d --name web \
  --mount type=bind,src="$PWD/site",dst=/usr/share/nginx/html,readonly nginx:1.27

docker run --rm --mount type=tmpfs,dst=/tmp,tmpfs-size=64m alpine df -h /tmp

docker volume ls
docker volume inspect pgdata         # emplacement réel, pilote, labels
docker volume rm pgdata
docker volume prune                  # volumes sans conteneur : attention
```

La forme courte `-v pgdata:/var/lib/postgresql/data` fait la même chose. Sa différence piégeuse : `-v /chemin/inexistant:/app` **crée** un dossier vide appartenant à root sur l'hôte, alors que `--mount` refuse avec une erreur claire.

## Les droits sur les fichiers

Les noms d'utilisateurs ne comptent pas, seuls les **UID** comptent, et ils sont **partagés** avec l'hôte (sauf en mode rootless ou avec les user namespaces).

```bash
docker run --rm -v "$PWD/out:/out" --user "$(id -u):$(id -g)" alpine touch /out/test
ls -ln out/        # le fichier appartient à ton UID, pas à root
```

Sur Red Hat avec SELinux, un bind mount demande souvent l'option `:z` (partagé) ou `:Z` (privé) pour que le contexte SELinux soit ajusté (fiche Linux sur SELinux).

## Sauvegarder et restaurer

```bash
# Sauvegarder un volume
docker run --rm -v pgdata:/data:ro -v "$PWD":/backup alpine \
  tar czf /backup/pgdata-$(date +%F).tgz -C /data .

# Restaurer dans un nouveau volume
docker volume create pgdata2
docker run --rm -v pgdata2:/data -v "$PWD":/backup alpine \
  tar xzf /backup/pgdata-2026-10-23.tgz -C /data
```

Pour une base de données en marche, une copie des fichiers peut être incohérente : on utilise son outil (`pg_dump`, `mysqldump`) ou on arrête le conteneur avant la copie.

## Les bonnes pratiques

- **Volumes nommés** pour les données ; jamais de données importantes dans la couche écrivable.
- **Bind mounts en lecture seule** (`readonly`, `:ro`) pour la configuration.
- **Pas de bind mount** de dossiers sensibles de l'hôte (`/`, `/etc`, et surtout `/var/run/docker.sock`, qui donne le contrôle total de Docker, donc de l'hôte).
- Un conteneur en **lecture seule** (`--read-only`) avec un tmpfs pour `/tmp` et des volumes là où il doit écrire : plus sûr et plus prévisible.
- Dans Kubernetes, les volumes Docker sont remplacés par les PersistentVolumes et `emptyDir` (module Kubernetes, chapitre Stockage).

> **À retenir.** Volume pour les données (géré par Docker, survit au conteneur), bind mount pour le développement et la configuration, tmpfs pour le temporaire en mémoire. Préférer `--mount`, plus explicite. Les droits dépendent des UID partagés avec l'hôte. Ne jamais monter le socket Docker sans raison forte.
