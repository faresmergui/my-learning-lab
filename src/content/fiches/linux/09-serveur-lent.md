---
title: Diagnostiquer un serveur lent
chapter: 9
order: 1
duration: 10
level: intermédiaire
tags:
- LFCS
cards:
- q: Que représente le *load average* ?
  a: Le nombre moyen de processus **en train de tourner ou en attente** (CPU, ou I/O en état `D`) sur 1, 5 et 15 minutes. À comparer au nombre de cœurs (`nproc`).
- q: Dans `free -h`, la mémoire « libre » est presque nulle. Est-ce un problème ?
  a: Pas forcément. Linux utilise la RAM libre comme **cache** disque. Regarde la colonne **available**, qui inclut le cache récupérable.
- q: Que signifie un `%wa` (iowait) élevé dans `top` ?
  a: Le CPU attend le **disque** (ou le réseau pour NFS). Le goulot est le stockage, pas le calcul. `iostat -x 1` montre quel disque sature.
- q: Comment savoir si le noyau a tué un processus faute de mémoire ?
  a: '`dmesg -T | grep -i ''out of memory''` ou `journalctl -k | grep -i oom` : l''OOM killer indique le processus tué et sa consommation.'
- q: À quoi sert `strace` ?
  a: 'À voir les **appels système** d''un processus : fichiers ouverts, connexions, attentes. `strace -p 1234 -f -e trace=network` pour se limiter au réseau.'
- q: Quelle est la méthode USE ?
  a: Pour chaque ressource (CPU, mémoire, disque, réseau), regarder l'**Utilisation**, la **Saturation** (file d'attente) et les **Erreurs**.
quiz:
- q: Load average à 16 sur une machine à 4 cœurs, mais le CPU est à 10 %. Que soupçonner ?
  options:
  - Un processus qui boucle
  - Des processus bloqués en attente d'I/O (état D)
  - Un manque de swap
  - Rien d'anormal
  answer: 1
  explain: Le load average compte aussi les processus en attente d'I/O. Vérifie `%wa` dans `top`, `iostat -x 1`, et cherche les processus en `D` avec `ps -eo state,pid,cmd | grep '^D'`.
- q: Le serveur ralentit, et `vmstat 1` montre des valeurs non nulles en continu dans `si` et `so`. Qu'est-ce que ça veut dire ?
  options:
  - Le CPU est saturé
  - 'Le système swappe : il manque de mémoire vive'
  - Le réseau est saturé
  - Le disque est plein
  answer: 1
  explain: '`si`/`so` = swap in / swap out. Un swap actif en continu dégrade fortement les performances : trouve qui consomme la mémoire.'
---

« Le serveur rame » : avant de redémarrer, cinq minutes de mesures disent souvent tout.

> **Les outils cités dans cette fiche.**
> - **uptime** : depuis quand la machine tourne, et sa charge moyenne (load average).
> - **vmstat** : un résumé par seconde du CPU, de la mémoire, du swap et des entrées/sorties disque.
> - **mpstat**, **pidstat**, **iostat**, **sar** : outils du paquet **sysstat**. `mpstat` détaille l'usage CPU par cœur, `pidstat` par processus, `iostat` l'activité de chaque disque, `sar` le réseau (et garde un historique si on l'active).
> - **top** (ou **htop**, plus lisible) : la liste des processus qui consomment le plus, mise à jour en direct. **iotop** fait la même chose pour le disque.
> - **free** : l'état de la mémoire ; **swap** : zone du disque utilisée comme mémoire de secours, bien plus lente que la RAM.
> - **strace** : affiche les appels système d'un processus (ouvrir un fichier, se connecter…), pour voir ce qu'il fait ou sur quoi il bloque. Il ralentit le processus, donc à utiliser brièvement en production.
> - **lsof** : liste les fichiers et sockets ouverts par un processus. **nstat** et **ss -ti** donnent les compteurs réseau, dont les retransmissions TCP.
> - **OOM killer** (Out Of Memory) : le mécanisme du noyau qui tue un processus quand la mémoire est épuisée.
> - **MTU** : la taille maximale d'un paquet sur un lien réseau (souvent 1 500 octets).
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.
> - **hyperviseur** : le logiciel qui fait tourner des machines virtuelles sur un serveur physique (KVM, VMware ESXi).

## La séquence des 60 secondes

```bash
uptime                 # load average sur 1, 5, 15 min
dmesg -T | tail        # OOM killer, erreurs disque, réseau
vmstat 1 5             # r (file CPU), si/so (swap), wa (attente I/O)
mpstat -P ALL 1 3      # un cœur saturé ?
pidstat 1 3            # qui consomme le CPU
iostat -xz 1 3         # %util et temps d'attente par disque
free -h                # regarde la colonne available
sar -n DEV 1 3         # débit réseau
top                    # vue d'ensemble
```

## Lire les signaux

| Constat | Ressource en cause | Suite |
| --- | --- | --- |
| `%us` élevé, `r` > nombre de cœurs | CPU | `pidstat`, profiler l'appli |
| `%wa` élevé, `%util` disque proche de 100 | disque | `iotop`, requêtes lentes |
| `si`/`so` non nuls, available faible | mémoire | `ps aux --sort=-%mem`, fuite ? |
| `Out of memory` dans dmesg | mémoire | processus tué, revoir les limites |
| retransmissions TCP | réseau | `ss -ti`, `nstat`, MTU |

## Creuser un processus

```bash
pidstat -p 1234 1
lsof -p 1234 | wc -l              # nombre de fichiers ouverts
strace -p 1234 -f -tt -e trace=file,network
grep -E 'VmRSS|Threads' /proc/1234/status
```

## Les quatre ressources

Un serveur lent, c'est presque toujours **une** ressource saturée parmi quatre : **CPU**, **mémoire**, **disque**, **réseau**. La méthode **USE** (Brendan Gregg) propose de regarder pour chacune : l'**utilisation** (à quel point elle est occupée), la **saturation** (y a-t-il une file d'attente ?) et les **erreurs**.

## Comprendre le load average

`uptime` affiche trois nombres, la charge moyenne sur 1, 5 et 15 minutes. C'est le nombre moyen de processus qui **veulent** tourner (état `R`) **ou** qui attendent le disque (état `D`). On le compare au **nombre de cœurs** (`nproc`) : un load de 4 sur 8 cœurs est confortable, sur 2 cœurs il y a une file d'attente. Comparer les trois valeurs dit si la situation empire (1 min > 15 min) ou se calme.

Un load élevé avec un CPU peu utilisé pointe vers le **disque** (beaucoup de processus en `D`), pas vers le processeur.

## La mémoire : ne pas lire « free »

Linux utilise la mémoire libre comme **cache disque** : c'est normal et souhaitable, ce cache est rendu dès qu'une appli en a besoin. La colonne `free` de `free -h` est donc souvent faible sur un serveur sain. La bonne colonne est **`available`** : ce qui peut réellement être donné aux applications.

Quand la mémoire manque vraiment :

1. le système **swappe** (déplace de la mémoire sur le disque) : `si`/`so` non nuls dans `vmstat`, et tout ralentit fortement ;
2. en dernier recours, l'**OOM killer** tue le processus jugé le plus coupable. On le voit dans `dmesg` (`Out of memory: Killed process …`). Dans un conteneur, la même chose arrive quand la **limite** de mémoire est atteinte (`OOMKilled` dans Kubernetes).

## Lire `vmstat 1`

```
procs ---memory--- --swap-- ---io--- -system-- ------cpu-----
 r  b   free  cache  si  so  bi   bo   in   cs us sy id wa st
 9  0   210M  3.1G    0   0   5   20  900 1200 92  6  2  0  0
```

- `r` = 9 processus prêts, sur une machine de 4 cœurs : file d'attente CPU ;
- `us` 92 % : le temps est passé dans le code des applis (sinon `sy` élevé = noyau, `wa` élevé = attente disque) ;
- `st` (steal) élevé sur une VM : l'hyperviseur donne le CPU à d'autres VM, le problème est chez l'hébergeur.

## Le disque

`iostat -xz 1` : `%util` proche de 100 % signifie que le disque est occupé en permanence, et `await` (en ms) dit combien de temps attend chaque opération. Quelques ms sur SSD est normal ; des dizaines ou centaines indiquent une saturation. `iotop` montre quel processus en est responsable.

> **À retenir.** Mesure d'abord, agis ensuite. Redémarrer fait disparaître le symptôme, mais aussi toutes les preuves.
