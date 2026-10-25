---
title: RAID, NFS, swap et quotas
chapter: 6
order: 2
duration: 12
tags:
- LFCS
- mdadm
- NFS
- swap
cards:
- q: Différence entre RAID 0, 1, 5 et 10 ?
  a: '**0** : découpe sur plusieurs disques, rapide mais aucune tolérance. **1** : miroir, supporte la perte d''un disque. **5** : parité répartie, au moins 3 disques, supporte la perte d''un disque. **10** : miroirs découpés, au moins 4 disques, rapide et tolérant.'
- q: Comment créer un RAID 1 logiciel et suivre son état ?
  a: '`mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc`, puis `cat /proc/mdstat` et `mdadm --detail /dev/md0`. Enregistrer la config avec `mdadm --detail --scan >> /etc/mdadm/mdadm.conf`.'
- q: Un RAID est-il une sauvegarde ?
  a: '**Non.** Il protège contre la panne d''un disque, pas contre une suppression, un ransomware ou un incendie : l''erreur est recopiée sur tous les disques à l''instant.'
- q: Comment partager un dossier en NFS ?
  a: 'Sur le serveur : une ligne dans `/etc/exports` (`/srv/partage 10.0.0.0/24(rw,sync,no_subtree_check)`), puis `exportfs -ra`. Sur le client : `mount -t nfs serveur:/srv/partage /mnt/partage`.'
- q: Que fait l'option `root_squash` de NFS ?
  a: Elle transforme le root du client en utilisateur anonyme (`nobody`) sur le partage. Sans elle, n'importe quel root d'une machine cliente serait root sur les fichiers partagés. C'est le défaut.
- q: Comment ajouter un fichier d'échange (swap) permanent ?
  a: '`fallocate -l 2G /swapfile`, `chmod 600`, `mkswap /swapfile`, `swapon /swapfile`, puis la ligne `/swapfile none swap sw 0 0` dans `/etc/fstab`. Vérifier avec `swapon --show`.'
- q: Différence entre limite soft et hard d'un quota disque ?
  a: La **soft** peut être dépassée pendant un délai de grâce (7 jours par défaut) ; la **hard** est un plafond absolu, l'écriture échoue au-delà.
quiz:
- q: '`cat /proc/mdstat` affiche `[U_]` pour `md0`. Que se passe-t-il ?'
  options:
  - Tout va bien
  - Un des deux disques du miroir est sorti du RAID
  - Le RAID se crée
  - Le disque est plein
  answer: 1
  explain: '`U` = disque actif, `_` = disque manquant. On remplace le disque puis `mdadm /dev/md0 --add /dev/sdX` et la reconstruction démarre.'
- q: Un montage NFS dans `/etc/fstab` bloque le démarrage quand le serveur est éteint. Quelle option aide ?
  options:
  - '`noexec`'
  - '`_netdev,nofail`'
  - '`ro`'
  - '`defaults`'
  answer: 1
  explain: '`_netdev` attend le réseau, `nofail` laisse le démarrage continuer si le montage échoue.'
level: intermédiaire
---

La fiche sur les disques et LVM couvrait les partitions, les volumes et les montages. L'examen LFCS ajoute quatre sujets de stockage : protéger contre la panne d'un disque (**RAID**), partager un dossier sur le réseau (**NFS**), ajouter de la mémoire d'échange (**swap**) et limiter l'espace de chaque utilisateur (**quotas**).

> **Les outils cités dans cette fiche.**
> - **RAID** (Redundant Array of Independent Disks) : plusieurs disques combinés pour aller plus vite, survivre à une panne, ou les deux.
> - **mdadm** : l'outil Linux qui crée et gère un RAID **logiciel** (fait par le noyau, sans carte RAID).
> - **NFS** (Network File System) : un protocole pour monter sur une machine un dossier qui se trouve sur une autre.
> - **swap** : un espace disque que le noyau utilise comme mémoire de secours quand la RAM est pleine.
> - **quota** : une limite d'espace disque ou de nombre de fichiers, par utilisateur ou par groupe.
> - **fstab** : le fichier `/etc/fstab`, qui liste ce qui doit être monté au démarrage.
> - **LVM** : le gestionnaire de volumes de Linux, qui découpe et regroupe des disques de façon souple.
> - **UID** : le numéro qui identifie un utilisateur sous Linux (0 = root).
> - **OOM** : out of memory : la mémoire est épuisée, le noyau tue un processus pour en libérer.
> - **nœud** : une machine (physique ou virtuelle) membre d'un cluster.

## RAID logiciel avec mdadm

| Niveau | Disques min. | Pannes tolérées | Espace utile | Usage |
| --- | --- | --- | --- | --- |
| RAID 0 | 2 | aucune | 100 % | vitesse, données jetables |
| RAID 1 | 2 | 1 | 50 % | système, petits serveurs |
| RAID 5 | 3 | 1 | (n-1)/n | stockage, lecture surtout |
| RAID 10 | 4 | 1 par miroir | 50 % | bases de données |

```bash
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc
cat /proc/mdstat                 # état et progression de la synchronisation
mdadm --detail /dev/md0

mkfs.ext4 /dev/md0 && mount /dev/md0 /data
mdadm --detail --scan >> /etc/mdadm/mdadm.conf   # pour retrouver le RAID au démarrage
update-initramfs -u                              # (Debian/Ubuntu)
```

Remplacer un disque en panne :

```bash
mdadm /dev/md0 --fail /dev/sdc --remove /dev/sdc
# changer le disque physiquement, puis :
mdadm /dev/md0 --add /dev/sdd    # la reconstruction démarre, à suivre dans /proc/mdstat
```

Un RAID n'est **pas une sauvegarde** : un fichier supprimé l'est aussitôt sur tous les disques.

## Partager un dossier avec NFS

```bash
# Serveur
apt install nfs-kernel-server            # (nfs-utils sur Red Hat)
mkdir -p /srv/partage
echo "/srv/partage 10.0.0.0/24(rw,sync,no_subtree_check)" >> /etc/exports
exportfs -ra                             # recharger les partages
exportfs -v                              # les lister avec leurs options

# Client
apt install nfs-common
showmount -e 10.0.0.2                    # voir ce que le serveur partage
mount -t nfs 10.0.0.2:/srv/partage /mnt/partage
```

```
# /etc/fstab côté client
10.0.0.2:/srv/partage  /mnt/partage  nfs  defaults,_netdev,nofail  0 0
```

Les options importantes :

- `rw` ou `ro` : lecture-écriture ou lecture seule ;
- `sync` : le serveur confirme l'écriture une fois les données sur disque (plus sûr) ;
- `root_squash` (défaut) : le root du client devient anonyme sur le partage. `no_root_squash` est à éviter sauf besoin précis.

NFS ne chiffre pas et fait confiance aux numéros d'utilisateur (UID) : on le réserve à un réseau privé, et les UID doivent correspondre entre les machines.

## Ajouter du swap

```bash
free -h && swapon --show
fallocate -l 2G /swapfile
chmod 600 /swapfile              # personne d'autre ne doit lire la mémoire échangée
mkswap /swapfile
swapon /swapfile
echo "/swapfile none swap sw 0 0" >> /etc/fstab
```

Le swap évite qu'un pic de mémoire déclenche l'OOM killer, mais une machine qui swappe beaucoup devient très lente. Le paramètre `vm.swappiness` (fiche sur les paquets et sysctl) règle la tendance à l'utiliser. Kubernetes ne gère le swap des nœuds qu'avec une configuration explicite : par défaut, on le désactive sur les nœuds.

## Les quotas disque

Sur un système de fichiers ext4 :

```bash
# 1. Activer l'option dans /etc/fstab : defaults,usrquota,grpquota
mount -o remount /home
quotacheck -cugm /home          # crée les fichiers de quota
quotaon /home

# 2. Fixer une limite : 5 Go soft, 6 Go hard, sans limite de nombre de fichiers
setquota -u alice 5G 6G 0 0 /home
quota -u alice                  # ce qu'elle utilise
repquota -a                     # rapport pour tous
```

Sur **XFS** (défaut de Red Hat), les quotas s'activent au montage (`uquota`) et se gèrent avec `xfs_quota -x -c 'limit bsoft=5g bhard=6g alice' /home`.

> **À retenir.** RAID 1 et 5 survivent à un disque, RAID 0 à aucun, et aucun RAID ne remplace une sauvegarde ; `/proc/mdstat` montre l'état. NFS : `/etc/exports` + `exportfs -ra`, `root_squash` par défaut, `_netdev,nofail` dans fstab. Swap : `mkswap`, `swapon`, fstab. Quotas : option `usrquota`, `quotaon`, `setquota`.
