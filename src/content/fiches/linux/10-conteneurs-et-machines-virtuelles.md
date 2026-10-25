---
title: Gérer des conteneurs et des machines virtuelles
chapter: 10
order: 1
duration: 11
tags:
- LFCS
- Podman
- Docker
- KVM
cards:
- q: Différence entre un conteneur et une machine virtuelle ?
  a: 'Un **conteneur** est un processus isolé qui partage le noyau de l''hôte : léger, démarre en une seconde. Une **machine virtuelle** a son propre noyau sur du matériel simulé : plus lourde, mais plus isolée et peut faire tourner un autre système.'
- q: Quelles commandes de base pour lancer et suivre un conteneur ?
  a: '`podman run -d --name web -p 8080:80 nginx` (ou `docker run`), puis `podman ps`, `podman logs -f web`, `podman exec -it web sh`, `podman stop web` et `podman rm web`.'
- q: Comment garder les données d'un conteneur quand on le supprime ?
  a: 'Avec un **volume** ou un montage : `-v donnees:/var/lib/postgresql/data` (volume nommé) ou `-v /srv/web:/usr/share/nginx/html:ro` (dossier de l''hôte). Tout le reste disparaît avec le conteneur.'
- q: Comment faire redémarrer un conteneur avec la machine ?
  a: 'Avec Docker : `--restart unless-stopped`. Avec Podman : un fichier **Quadlet** (`.container` dans `/etc/containers/systemd/`) qui devient un service systemd.'
- q: Quelles commandes virsh pour gérer des machines virtuelles ?
  a: '`virsh list --all` (toutes les VM), `virsh start`, `virsh shutdown` (arrêt propre), `virsh destroy` (coupure brutale), `virsh autostart` (démarrer avec l''hôte), `virsh dominfo` (détails).'
- q: Comment vérifier que le processeur supporte la virtualisation matérielle ?
  a: '`grep -E -c ''vmx|svm'' /proc/cpuinfo` (plus de 0 = oui) et `lsmod | grep kvm` pour voir si le module KVM est chargé.'
quiz:
- q: Tu lances `podman run -d -p 8080:80 nginx` mais `curl localhost:8080` ne répond pas. Première vérification ?
  options:
  - Réinstaller podman
  - '`podman ps` puis `podman logs <id>`'
  - Redémarrer la machine
  - Changer d'image
  answer: 1
  explain: On vérifie que le conteneur tourne encore et ce qu'il a affiché. Un conteneur qui s'arrête aussitôt n'apparaît qu'avec `podman ps -a`.
- q: Une VM ne répond plus du tout à `virsh shutdown`. Que fais-tu ?
  options:
  - '`virsh undefine`'
  - '`virsh destroy`, l''équivalent de débrancher la prise'
  - Supprimer son disque
  - '`virsh autostart`'
  answer: 1
  explain: '`destroy` coupe la VM sans la supprimer. `undefine` effacerait sa définition, ce qui n''est pas ce qu''on veut.'
level: intermédiaire
---

Un administrateur Linux fait aujourd'hui tourner une bonne partie de ses services dans des **conteneurs** ou des **machines virtuelles**. L'examen LFCS demande de savoir lancer, inspecter et arrêter les deux depuis la ligne de commande. Cette fiche donne les gestes de base ; un futur module Docker pourra aller plus loin sur les images et leur construction.

> **Les outils cités dans cette fiche.**
> - **Docker** : l'outil qui a popularisé les conteneurs ; il passe par un service (`dockerd`) qui tourne en root.
> - **Podman** : un équivalent de Docker, mêmes commandes, mais sans service central et capable de tourner sans root. C'est l'outil par défaut de Red Hat.
> - **image** : le modèle en lecture seule d'un conteneur (système de fichiers et commande de démarrage), téléchargé depuis un **registre** comme Docker Hub.
> - **Quadlet** : un format de fichier qui transforme un conteneur Podman en service systemd.
> - **KVM** (Kernel-based Virtual Machine) : la virtualisation intégrée au noyau Linux, qui utilise les instructions du processeur prévues pour ça.
> - **libvirt** et **virsh** : la couche qui gère les machines virtuelles (KVM et d'autres) et sa commande.
> - **virt-install** : crée une nouvelle machine virtuelle en ligne de commande.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.

## Comprendre : conteneur ou machine virtuelle

```
Machine virtuelle                      Conteneur
┌──────────┐ ┌──────────┐              ┌────────┐ ┌────────┐
│  appli   │ │  appli   │              │ appli  │ │ appli  │
│  noyau   │ │  noyau   │              └────────┘ └────────┘
└──────────┘ └──────────┘              ─── noyau de l'hôte ───
─── hyperviseur (KVM) ───
```

| | Conteneur | Machine virtuelle |
| --- | --- | --- |
| noyau | celui de l'hôte | le sien |
| démarrage | une seconde | des dizaines de secondes |
| taille | quelques dizaines de Mo | plusieurs Go |
| isolation | bonne, mais noyau partagé | forte |
| autre OS (Windows) | non | oui |

## Les conteneurs avec Podman ou Docker

Les commandes sont les mêmes : remplace `podman` par `docker` si c'est ce qui est installé.

```bash
podman pull docker.io/library/nginx:1.27
podman run -d --name web -p 8080:80 \
  -v /srv/site:/usr/share/nginx/html:ro nginx:1.27
podman ps                 # en cours (-a : aussi les arrêtés)
podman logs -f web
podman exec -it web sh    # un shell dans le conteneur
podman inspect web        # tout le détail (IP, montages, variables)
podman stop web && podman rm web
podman images && podman rmi nginx:1.27
```

| Option | Effet |
| --- | --- |
| `-d` | en arrière-plan |
| `-p 8080:80` | port 8080 de l'hôte vers le port 80 du conteneur |
| `-v hôte:conteneur` | monter un dossier ou un volume ; `:ro` en lecture seule |
| `-e CLE=valeur` | variable d'environnement |
| `--restart unless-stopped` | (Docker) relancer après une panne ou un redémarrage |

Tout ce qu'un conteneur écrit hors d'un volume **disparaît** avec lui. Les données d'une base vont toujours dans un volume.

### Un conteneur qui démarre avec la machine (Podman)

```ini
# /etc/containers/systemd/web.container
[Container]
Image=docker.io/library/nginx:1.27
PublishPort=8080:80
Volume=/srv/site:/usr/share/nginx/html:ro

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl start web          # Quadlet a créé le service web.service
```

## Les machines virtuelles avec KVM et virsh

```bash
grep -E -c 'vmx|svm' /proc/cpuinfo     # le processeur sait-il virtualiser ?
lsmod | grep kvm
```

```bash
virsh list --all                       # toutes les VM, allumées ou non
virsh start vm-test
virsh shutdown vm-test                 # arrêt propre (demande à l'OS invité)
virsh destroy vm-test                  # coupure immédiate
virsh autostart vm-test                # démarrer avec l'hôte
virsh dominfo vm-test                  # CPU, mémoire, état
virsh console vm-test                  # console série (sortie : Ctrl+])
```

Créer une VM depuis une image :

```bash
virt-install --name vm-test --memory 2048 --vcpus 2 \
  --disk size=20 --cdrom /srv/iso/debian-13.iso \
  --os-variant debian13 --network network=default --graphics none
```

Attention aux deux commandes qui se ressemblent : `virsh destroy` **éteint** la VM, `virsh undefine` **supprime sa définition** (ses disques restent, mais il faudra la recréer).

> **À retenir.** Conteneur = processus isolé sur le noyau de l'hôte, VM = son propre noyau. `podman run -d -p -v`, puis `ps`, `logs`, `exec`, et les données dans un volume. Pour les VM : `virsh list --all`, `start`, `shutdown` (propre) ou `destroy` (brutal), `autostart`.
