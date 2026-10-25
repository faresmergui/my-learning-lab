---
title: Processus et signaux
chapter: 3
order: 1
duration: 9
level: intermédiaire
tags:
- LFCS
cards:
- q: Différence entre SIGTERM (15) et SIGKILL (9) ?
  a: '**SIGTERM** demande poliment l''arrêt : le programme peut finir proprement. **SIGKILL** est appliqué par le noyau, sans possibilité de l''intercepter ni de nettoyer.'
- q: À quoi sert souvent SIGHUP ?
  a: À demander à un service de **relire sa configuration** sans s'arrêter (nginx, sshd…). À l'origine, il signale la fermeture du terminal.
- q: Qu'est-ce qu'un processus zombie ?
  a: 'Un processus **terminé** dont le parent n''a pas encore lu le code de retour. Il ne consomme rien à part une entrée dans la table des processus. On ne le tue pas : il faut corriger ou arrêter le parent.'
- q: Que représente la valeur *nice* d'un processus ?
  a: Sa **priorité** CPU, de -20 (prioritaire) à 19 (gentil). `nice -n 10 cmd` lance, `renice -n 5 -p 1234` modifie. Seul root peut baisser la valeur.
- q: Comment garder une commande active après la fermeture du terminal ?
  a: '`nohup cmd &`, ou mieux `tmux` / `screen`. Pour un vrai service : une unité systemd.'
- q: Que signifie l'état `D` dans `ps` ?
  a: Sommeil **non interruptible**, en général en attente d'entrées-sorties (disque, NFS). Même SIGKILL n'agit pas tant que l'attente n'est pas terminée.
quiz:
- q: '`kill 1234` ne fait rien, le processus continue. Que faire ensuite ?'
  options:
  - Redémarrer le serveur
  - Attendre un peu, puis `kill -9 1234` si besoin
  - '`kill -1 1234`'
  - Supprimer `/proc/1234`
  answer: 1
  explain: SIGTERM laisse au programme le temps de s'arrêter. SIGKILL est le dernier recours, car il ne permet aucun nettoyage (fichiers temporaires, verrous).
- q: Quelle commande montre l'arbre des processus avec leurs parents ?
  options:
  - ps -ef --forest (ou pstree -p)
  - top -t
  - jobs -l
  - lsof -p
  answer: 0
  explain: Utile pour trouver le parent d'un zombie ou comprendre qui a lancé quoi.
---

Un processus est un programme en cours d'exécution, avec un **PID**, un parent (**PPID**), un utilisateur et un état.


> **Les termes et outils cités dans cette fiche.**
> - **NFS** : un protocole de partage de fichiers en réseau, monté comme un dossier local.
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.

## Observer

```bash
ps aux --sort=-%mem | head          # les plus gourmands en mémoire
ps -ef --forest                     # arbre parent / enfant
pgrep -a nginx                      # PID + commande
top                                 # ou htop, plus lisible
ls -l /proc/1234/cwd /proc/1234/exe # dossier courant et binaire
```

## Les états

| État | Signification |
| --- | --- |
| `R` | en cours d'exécution ou prêt |
| `S` | en sommeil, attend un événement |
| `D` | attente non interruptible (I/O) |
| `Z` | zombie, terminé mais non récupéré |
| `T` | arrêté (Ctrl+Z) |

<!-- schema:etats -->
<figure class="diagram"><svg viewBox="0 0 680 296" role="img" aria-label="Les états d&#x27;un processus" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g transform="translate(0,36)"><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="100" width="96" height="50" rx="9"/></g><text x="62.0" y="122.0" class="dg-t" text-anchor="middle" style="--d:0">fork()</text><text x="62.0" y="140.0" class="dg-s" text-anchor="middle" style="--d:0">création</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="170" y="100" width="120" height="50" rx="9"/></g><text x="230.0" y="122.0" class="dg-t" text-anchor="middle" style="--d:1">R</text><text x="230.0" y="140.0" class="dg-s" text-anchor="middle" style="--d:1">exécution / prêt</text><g class="dg-box dg-pop" style="--d:2"><rect x="360" y="14" width="130" height="50" rx="9"/></g><text x="425.0" y="36.0" class="dg-t" text-anchor="middle" style="--d:2">S</text><text x="425.0" y="54.0" class="dg-s" text-anchor="middle" style="--d:2">attend un événement</text><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="360" y="100" width="130" height="50" rx="9"/></g><text x="425.0" y="122.0" class="dg-t" text-anchor="middle" style="--d:2">D</text><text x="425.0" y="140.0" class="dg-s" text-anchor="middle" style="--d:2">attend une I/O</text><g class="dg-box dg-pop" style="--d:2"><rect x="360" y="186" width="130" height="50" rx="9"/></g><text x="425.0" y="208.0" class="dg-t" text-anchor="middle" style="--d:2">T</text><text x="425.0" y="226.0" class="dg-s" text-anchor="middle" style="--d:2">arrêté</text><g class="dg-box dg-ghost dg-pop" style="--d:3"><rect x="548" y="100" width="118" height="50" rx="9"/></g><text x="607.0" y="122.0" class="dg-t" text-anchor="middle" style="--d:3">Z</text><text x="607.0" y="140.0" class="dg-s" text-anchor="middle" style="--d:3">zombie</text><path d="M110 125 L168 125" class="dg-l" marker-end="url(#g3-n)"/><path d="M290 112 L330 112 L330 39 L358 39" class="dg-l" marker-end="url(#g3-n)" marker-start="url(#g3-n)"/><path d="M290 125 L358 125" class="dg-l a" marker-end="url(#g3-a)" marker-start="url(#g3-a)"/><path d="M290 138 L330 138 L330 211 L358 211" class="dg-l" marker-end="url(#g3-n)" marker-start="url(#g3-n)"/><path d="M230 98 C 240 -34, 596 -34, 607 98" class="dg-l c dash" marker-end="url(#g3-c)"/><text x="560" y="4" class="dg-ct" text-anchor="middle">exit()</text><text x="424" y="172" class="dg-s" text-anchor="middle">D : même kill -9 attend</text><text x="608" y="170" class="dg-s" text-anchor="middle">disparaît quand le</text><text x="608" y="184" class="dg-s" text-anchor="middle">parent fait wait()</text><text x="424" y="252" class="dg-s" text-anchor="middle">Ctrl+Z, SIGSTOP / SIGCONT</text></g></svg><figcaption>Beaucoup de processus en D signalent un problème de disque ou de réseau (NFS), pas de CPU.</figcaption></figure>
<!-- /schema:etats -->

## Les signaux

| Signal | N° | Usage |
| --- | --- | --- |
| `SIGHUP` | 1 | recharger la config |
| `SIGINT` | 2 | Ctrl+C |
| `SIGKILL` | 9 | arrêt forcé, impossible à intercepter |
| `SIGTERM` | 15 | arrêt propre (défaut de `kill`) |
| `SIGSTOP` / `SIGCONT` | 19 / 18 | mettre en pause / reprendre |

```bash
kill 1234            # SIGTERM
kill -HUP $(pgrep -o nginx)
pkill -f 'python worker.py'
```

> **Piège classique.** Utiliser `kill -9` par réflexe. Le programme n'a aucune chance de vider ses buffers ou de libérer ses verrous, ce qui peut corrompre des données.

## Tâches en arrière-plan

```bash
long_cmd &      # lancer en arrière-plan
jobs            # lister
fg %1           # ramener au premier plan
# Ctrl+Z puis bg : mettre en pause, puis relancer en arrière-plan
```

## Comment naît un processus

Sous Linux, tout processus est créé par un autre, son **parent**. Le shell qui lance `ls` se **duplique** (`fork`), puis la copie se **remplace** par le programme `ls` (`exec`). Au sommet de l'arbre, il y a le PID 1 (systemd sur un serveur, ou le processus principal dans un conteneur), lancé par le noyau au démarrage.

Chaque processus hérite de son parent : l'utilisateur, les variables d'environnement, le répertoire courant, les fichiers ouverts. C'est pour ça qu'une variable `export`ée dans ton shell est visible par les programmes que tu lances, mais pas par un service systemd.

## Zombies et orphelins

Quand un processus se termine, il ne disparaît pas tout à fait : il laisse son **code de retour**, en attendant que son parent le lise (`wait`). Entre les deux, c'est un **zombie** (`Z`). Il ne consomme rien sauf une ligne dans la table des processus. Quelques zombies passagers sont normaux ; des milliers indiquent un parent bogué qui ne fait jamais `wait`. On ne peut pas tuer un zombie (il est déjà mort) : il faut corriger ou redémarrer son **parent**.

Si le parent meurt d'abord, l'enfant devient **orphelin** et est adopté par le PID 1, qui s'occupera de le récupérer. Dans un conteneur, si ton application est PID 1 et ne sait pas faire ce travail, les zombies s'accumulent : c'est le rôle de petits init comme `tini` (`docker run --init`).

## L'état D : le processus qu'on ne peut pas tuer

Un processus en `D` attend une opération d'entrée-sortie dans le noyau (un disque lent, un montage NFS qui ne répond plus). Même `SIGKILL` attend la fin de cette opération. Beaucoup de processus en `D` font grimper le **load average** sans consommer de CPU : la cause est le stockage, pas le processeur.

## Ce qu'un signal fait vraiment

Un signal est une **notification** envoyée à un processus. Pour la plupart (`SIGTERM`, `SIGHUP`, `SIGINT`), le programme peut définir ce qu'il fait : terminer proprement, recharger sa config, ignorer. Seuls `SIGKILL` et `SIGSTOP` sont appliqués directement par le noyau, sans que le programme ait son mot à dire.

C'est exactement ce que font systemd et Kubernetes à l'arrêt : `SIGTERM` d'abord, un délai de grâce (90 s par défaut pour systemd, 30 s dans Kubernetes), puis `SIGKILL` si le processus est toujours là. Une appli qui ignore `SIGTERM` est donc tuée brutalement à chaque déploiement.

Pour qu'un programme survive à la fermeture de ta session SSH (qui envoie `SIGHUP`), utilise `nohup`, `tmux`, ou mieux, un service systemd.

> **À retenir.** Envoie `SIGTERM` d'abord et laisse le programme finir proprement ; `SIGKILL` seulement en dernier recours. Un zombie attend que son parent lise son code de retour, un processus en `D` attend le disque : ni l'un ni l'autre ne se règle avec `kill -9`.
