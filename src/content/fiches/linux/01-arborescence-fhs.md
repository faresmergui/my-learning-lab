---
title: 'L''arborescence : où est quoi'
chapter: 1
order: 2
duration: 7
level: intermédiaire
tags:
- LFCS
cards:
- q: Que trouve-t-on dans `/etc`, `/var` et `/opt` ?
  a: '`/etc` : la **configuration**. `/var` : les données qui **changent** (logs, caches, bases, files d''attente). `/opt` : les logiciels tiers installés à part.'
- q: Que sont `/proc` et `/sys` ?
  a: Des systèmes de fichiers **virtuels** fournis par le noyau. `/proc` expose les processus et des réglages (`/proc/meminfo`, `/proc/<pid>/`). `/sys` expose les périphériques et pilotes.
- q: Différence entre `/tmp` et `/var/tmp` ?
  a: '`/tmp` est souvent vidé au redémarrage (parfois en RAM, tmpfs). `/var/tmp` survit aux redémarrages.'
- q: Comment trouver les fichiers de plus de 100 Mo sous `/var` ?
  a: '`find /var -type f -size +100M -exec ls -lh {} +` ou, pour les dossiers, `du -xh /var --max-depth=2 | sort -h | tail`.'
- q: Où sont les binaires des paquets et ceux installés à la main ?
  a: '`/usr/bin` pour les paquets du système, `/usr/local/bin` pour ce que tu installes toi-même. Sur les distributions récentes, `/bin` est un lien vers `/usr/bin`.'
quiz:
- q: Le disque racine est plein. Quel dossier est le suspect numéro un ?
  options:
  - /etc
  - /var (logs, caches, images de conteneurs)
  - /proc
  - /boot
  answer: 1
  explain: Logs non tournés, caches de paquets et images Docker ou containerd s'accumulent dans `/var`. `du -xh /var --max-depth=1 | sort -h` trouve le coupable.
- q: Comment voir la ligne de commande complète du processus 1234 ?
  options:
  - cat /proc/1234/cmdline | tr '\0' ' '
  - cat /etc/1234
  - ls /sys/1234
  - cat /var/run/1234
  answer: 0
  explain: Les arguments y sont séparés par des caractères nuls, d'où le `tr`. `ps -o args= -p 1234` donne le même résultat.
---

Linux suit une convention, la **FHS** (Filesystem Hierarchy Standard). La connaître évite de chercher au hasard.

| Dossier | Contenu |
| --- | --- |
| `/etc` | configuration du système et des services |
| `/var` | données variables : `/var/log`, `/var/lib` (bases, Docker), `/var/cache` |
| `/usr` | programmes et bibliothèques du système (`/usr/bin`, `/usr/lib`) |
| `/usr/local` | ce que tu installes à la main |
| `/opt` | logiciels tiers autonomes |
| `/home`, `/root` | dossiers des utilisateurs, et de root |
| `/tmp` | fichiers temporaires, vidé au redémarrage |
| `/proc`, `/sys` | vues virtuelles du noyau |
| `/dev` | périphériques (`/dev/sda`, `/dev/null`) |
| `/boot` | noyau et chargeur de démarrage |


> **Les termes et outils cités dans cette fiche.**
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **image** : le modèle figé (système de fichiers et réglages) à partir duquel on lance un conteneur.

## Explorer

```bash
du -xh /var --max-depth=1 | sort -h      # qui prend de la place
find /etc -name '*.conf' -mtime -1       # configs modifiées depuis 24 h
head -5 /proc/meminfo
ls -l /proc/$$/fd                         # fichiers ouverts par ton shell
```

## Pourquoi cette organisation

L'arborescence trie les fichiers selon **leur nature**, pas selon le logiciel qui les utilise. Sous Windows, un programme range souvent tout dans son dossier ; sous Linux, nginx a son binaire dans `/usr/sbin`, sa configuration dans `/etc/nginx`, ses logs dans `/var/log/nginx` et ses données dans `/var/lib/nginx`.

Ça paraît éparpillé, mais c'est ce qui rend l'administration prévisible :

- **sauvegarder la configuration** de toute la machine, c'est sauvegarder `/etc` ;
- **un disque qui se remplit**, c'est presque toujours `/var` (logs, images Docker, bases) ;
- **`/usr` peut être en lecture seule** ou remplacé d'un bloc lors d'une mise à jour, puisqu'il ne contient rien de propre à la machine ;
- `/tmp` peut être en mémoire (tmpfs) et disparaître au redémarrage.

## Les dossiers « virtuels »

`/proc` et `/sys` ne sont pas sur le disque : le noyau les **fabrique à la volée** quand tu les lis. `/proc/1234/` décrit le processus 1234 (sa commande, sa mémoire, ses fichiers ouverts), `/proc/meminfo` l'état de la mémoire, `/sys/class/net/` les interfaces réseau. C'est là que des outils comme `ps`, `free` ou `top` vont chercher leurs informations.

`/dev` contient des fichiers spéciaux qui représentent des **périphériques**. Écrire dans `/dev/null` jette les données ; lire `/dev/urandom` donne de l'aléatoire ; `/dev/sda` est le premier disque entier. C'est le principe Unix « tout est fichier » : on manipule un disque ou un terminal avec les mêmes outils que du texte.

## Où trouver quoi, en pratique

| Je cherche | Je regarde |
| --- | --- |
| la config d'un service | `/etc/<service>/`, puis `systemctl cat <service>` |
| ses logs | `journalctl -u <service>`, sinon `/var/log/<service>/` |
| ses données | `/var/lib/<service>/` |
| où est un binaire | `command -v nginx` |
| à quel paquet appartient un fichier | `dpkg -S /usr/sbin/nginx` ou `rpm -qf /usr/sbin/nginx` |

> **À retenir.** Les sauvegardes concernent surtout `/etc` (la config) et `/var/lib` (les données). Le reste se réinstalle.
