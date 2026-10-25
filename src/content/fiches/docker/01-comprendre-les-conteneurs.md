---
title: Ce qu'est vraiment un conteneur
chapter: 1
order: 1
duration: 11
tags:
- Docker
- namespaces
- cgroups
cards:
- q: Qu'est-ce qu'un conteneur, techniquement ?
  a: Un **processus Linux ordinaire**, isolé par des **namespaces** (ce qu'il voit), limité par des **cgroups** (ce qu'il consomme), et qui démarre sur le système de fichiers d'une **image**. Il n'y a ni noyau ni machine virtuelle à lui.
- q: Quels namespaces isolent un conteneur ?
  a: '**pid** (ses propres numéros de processus), **net** (interfaces, IP, ports), **mnt** (points de montage), **uts** (nom d''hôte), **ipc** (mémoire partagée), **user** (correspondance des utilisateurs) et **cgroup**.'
- q: À quoi servent les cgroups ?
  a: 'À **limiter et mesurer** les ressources d''un groupe de processus : CPU, mémoire, entrées-sorties disque, nombre de processus. `docker run --memory 512m --cpus 1.5` les utilise.'
- q: Comment est construite une image ?
  a: En **couches** en lecture seule empilées (une par instruction qui modifie les fichiers). Au lancement, Docker ajoute une **couche écrivable** propre au conteneur, par-dessus (système de fichiers **overlay**). Plusieurs conteneurs partagent les mêmes couches de base.
- q: Quelle chaîne de programmes lance un conteneur avec Docker ?
  a: '`docker` (client) → **dockerd** (le démon, l''API) → **containerd** (gère images et conteneurs) → **runc** (crée le processus avec namespaces et cgroups, puis s''efface). Kubernetes parle directement à containerd via CRI.'
- q: Qu'est-ce que l'OCI ?
  a: 'L''**Open Container Initiative** : les standards ouverts du format d''**image**, du **runtime** et de la **distribution**. Une image construite avec Docker tourne avec Podman, containerd ou Kubernetes.'
quiz:
- q: Un conteneur Linux peut-il faire tourner un programme compilé pour Windows sur un hôte Linux ?
  options:
  - Oui, c'est le principe
  - Non, il partage le noyau Linux de l'hôte
  - Oui, avec une image plus grosse
  - Seulement avec Compose
  answer: 1
  explain: Un conteneur n'apporte pas de noyau. Docker Desktop sur Mac et Windows fait tourner une petite VM Linux pour cette raison.
- q: Tu lances 10 conteneurs depuis la même image de 500 Mo. Combien d'espace disque environ ?
  options:
  - 5 Go
  - 500 Mo plus ce que chaque conteneur écrit
  - 50 Mo
  - Impossible à savoir
  answer: 1
  explain: Les couches de l'image sont partagées ; seule la couche écrivable de chaque conteneur s'ajoute.
level: intermédiaire
---

Le mot « conteneur » fait penser à une petite machine virtuelle. C'est trompeur, et cette confusion explique beaucoup de surprises (« pourquoi mon conteneur voit-il la mémoire de l'hôte ? », « pourquoi root dans le conteneur est-il dangereux ? »). Cette fiche montre ce qu'il y a vraiment sous un `docker run`. La fiche Linux « Gérer des conteneurs et des machines virtuelles » donne déjà les premières commandes.

> **Les outils cités dans cette fiche.**
> - **Docker** : l'outil qui a rendu les conteneurs simples à construire, distribuer et lancer. Il comprend un client (`docker`) et un démon (`dockerd`).
> - **namespace** : un mécanisme du noyau Linux qui donne à un processus sa propre **vue** d'une ressource (processus, réseau, fichiers…).
> - **cgroup** (control group) : un mécanisme du noyau qui **limite et mesure** les ressources d'un groupe de processus.
> - **overlayfs** : le système de fichiers qui empile des couches en lecture seule et une couche écrivable.
> - **containerd** : le gestionnaire de conteneurs utilisé par Docker et par Kubernetes. **runc** : le petit programme qui crée réellement le conteneur.
> - **OCI** (Open Container Initiative) : les standards ouverts des images et des runtimes.
> - **Podman** : une alternative à Docker, sans démon, compatible avec les mêmes images.
> - **hyperviseur** : le logiciel qui fait tourner des machines virtuelles sur un serveur physique (KVM, VMware ESXi).
> - **PID** : le numéro qui identifie un processus en cours d'exécution.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **ECS** : le service d'exécution de conteneurs d'AWS.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.

## Comprendre : un processus avec des œillères

<!-- schema:oeilleres -->
<figure class="diagram"><svg viewBox="0 0 680 280" role="img" aria-label="Un conteneur est un processus isolé" style="--minw:560px"><defs><marker id="g6-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g6-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g6-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g6-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="652" height="254" rx="12" class="dg-zone "/><text x="26" y="32" class="dg-zl" text-anchor="start">hôte Linux</text><g class="dg-box dg-pop" style="--d:0"><rect x="30" y="44" width="180" height="140" rx="9"/></g><text x="120.0" y="104.0" class="dg-t" text-anchor="middle" style="--d:0">processus de l&#x27;hôte</text><text x="120.0" y="122.0" class="dg-s" text-anchor="middle" style="--d:0"><tspan x="120.0" dy="0">sshd, systemd…</tspan><tspan x="120.0" dy="14">vue normale</tspan></text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="230" y="44" width="200" height="140" rx="9"/></g><text x="330.0" y="83.0" class="dg-t" text-anchor="middle" style="--d:1">conteneur « web »</text><text x="330.0" y="101.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="330.0" dy="0">processus nginx</tspan><tspan x="330.0" dy="14"></tspan><tspan x="330.0" dy="14">namespaces : se croit seul</tspan><tspan x="330.0" dy="14">cgroups : 512 Mo, 1 CPU</tspan><tspan x="330.0" dy="14">racine : son image</tspan></text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="448" y="44" width="200" height="140" rx="9"/></g><text x="548.0" y="83.0" class="dg-t" text-anchor="middle" style="--d:2">conteneur « api »</text><text x="548.0" y="101.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="548.0" dy="0">processus node</tspan><tspan x="548.0" dy="14"></tspan><tspan x="548.0" dy="14">namespaces : se croit seul</tspan><tspan x="548.0" dy="14">cgroups : 1 Go, 2 CPU</tspan><tspan x="548.0" dy="14">racine : son image</tspan></text><path d="M120 184 L120 210" class="dg-l a" marker-end="url(#g6-a)"/><path d="M330 184 L330 210" class="dg-l a" marker-end="url(#g6-a)"/><path d="M548 184 L548 210" class="dg-l a" marker-end="url(#g6-a)"/><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="30" y="212" width="620" height="40" rx="9"/></g><text x="340.0" y="237.0" class="dg-t" text-anchor="middle" style="--d:3">un seul noyau Linux, partagé par tous</text></svg><figcaption>Pas de machine virtuelle : les namespaces limitent ce qu&#x27;il voit, les cgroups ce qu&#x27;il consomme.</figcaption></figure>
<!-- /schema:oeilleres -->

Depuis l'hôte, `ps aux` montre les processus nginx et node comme les autres. Depuis le conteneur, nginx croit être le processus numéro 1 d'une machine vide.

| | Machine virtuelle | Conteneur |
| --- | --- | --- |
| noyau | le sien | celui de l'hôte |
| isolation | matérielle (hyperviseur) | logicielle (namespaces, cgroups) |
| démarrage | dizaines de secondes | quelques centaines de millisecondes |
| taille typique | Go | Mo à centaines de Mo |
| frontière de sécurité | forte | plus fine : une faille du noyau touche tous les conteneurs |

## Les namespaces : ce que le conteneur voit

| Namespace | Isole | Conséquence |
| --- | --- | --- |
| `pid` | les numéros de processus | l'appli est le PID 1 du conteneur |
| `net` | interfaces, IP, routes, ports | chaque conteneur peut écouter sur le port 80 |
| `mnt` | les points de montage | il voit le système de fichiers de l'image |
| `uts` | le nom d'hôte | `hostname` renvoie l'ID du conteneur |
| `ipc` | la mémoire partagée | pas d'échange avec les autres processus |
| `user` | les identifiants d'utilisateur | root dans le conteneur peut être un simple utilisateur sur l'hôte (mode rootless) |

## Les cgroups : ce que le conteneur consomme

```bash
docker run -d --name api --memory 512m --cpus 1.5 --pids-limit 200 node:22-alpine
docker stats api          # consommation en direct
```

Sans limite, un conteneur peut prendre toute la mémoire de l'hôte. S'il dépasse sa limite mémoire, le noyau le tue (**OOM kill**, code de sortie 137). Attention : des commandes comme `free` dans le conteneur affichent souvent la mémoire de l'**hôte**, pas la limite ; certains anciens runtimes (Java avant la version 10) se trompaient ainsi de taille de mémoire.

## Les images : des couches empilées

<!-- schema:couches -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Les couches d&#x27;une image" style="--minw:560px"><defs><marker id="g7-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g7-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g7-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g7-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-a dg-pop" style="--d:0"><rect x="40" y="16" width="182" height="38" rx="9"/></g><text x="131.0" y="40.0" class="dg-s" text-anchor="middle" style="--d:0">écriture conteneur 1</text><g class="dg-box dg-a dg-pop" style="--d:0"><rect x="238" y="16" width="182" height="38" rx="9"/></g><text x="329.0" y="40.0" class="dg-s" text-anchor="middle" style="--d:0">écriture conteneur 2</text><rect x="30" y="66" width="400" height="168" rx="12" class="dg-zone dg-zc"/><text x="42" y="84" class="dg-zl" text-anchor="start">image · lecture seule</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="40" y="92" width="380" height="38" rx="9"/></g><text x="230.0" y="116.0" class="dg-t" text-anchor="middle" style="--d:1">COPY app/ /app</text><text x="444" y="115" class="dg-s" text-anchor="start" style="--d:1">couche 4 : change à chaque commit</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="40" y="138" width="380" height="38" rx="9"/></g><text x="230.0" y="162.0" class="dg-t" text-anchor="middle" style="--d:2">RUN npm ci</text><text x="444" y="161" class="dg-s" text-anchor="start" style="--d:2">couche 3 : dépendances</text><g class="dg-box dg-pop" style="--d:3"><rect x="40" y="184" width="380" height="38" rx="9"/></g><text x="230.0" y="208.0" class="dg-t" text-anchor="middle" style="--d:3">node:22-alpine</text><text x="444" y="207" class="dg-s" text-anchor="start" style="--d:3">couches 1-2 : image de base, partagée</text><text x="444" y="39" class="dg-s" text-anchor="start">disparaît avec le conteneur</text></svg><figcaption>Deux conteneurs partagent les mêmes couches en lecture ; chacun n&#x27;écrit que dans sa propre couche.</figcaption></figure>
<!-- /schema:couches -->

- Les couches sont en **lecture seule** et identifiées par leur empreinte (`sha256:…`) : deux images qui partagent une base ne la stockent qu'une fois.
- Modifier un fichier d'une couche basse le **copie** dans la couche écrivable (copy-on-write).
- Tout ce que le conteneur écrit hors d'un **volume** disparaît quand on le supprime.

```bash
docker image history nginx:1.27     # les couches et leur taille
docker system df                    # espace utilisé par images, conteneurs, volumes
```

## Qui fait quoi

```
docker (CLI) ──API──► dockerd ──► containerd ──► containerd-shim ──► runc ──► processus
                       │
                       └── build (BuildKit), réseau, volumes
```

- **dockerd** offre l'API et les fonctions de confort (build, réseaux, volumes).
- **containerd** gère le cycle de vie des images et des conteneurs ; Kubernetes l'utilise directement, sans Docker.
- **runc** crée le processus avec ses namespaces et cgroups, puis se retire.

Comme tout suit les standards **OCI**, une image construite avec Docker tourne partout : Podman, Kubernetes, ECS, OpenStack Zun ou Magnum.

> **À retenir.** Un conteneur est un processus de l'hôte, isolé par les namespaces, limité par les cgroups, lancé sur les couches d'une image. Il partage le noyau de l'hôte : isolation plus légère qu'une VM. Les couches sont partagées et en lecture seule ; ce qui est écrit hors volume disparaît avec le conteneur. Docker passe par containerd et runc, et les images OCI tournent partout.
