---
title: journald et les logs
chapter: 7
order: 1
duration: 7
level: intermédiaire
tags:
- LFCS
cards:
- q: Comment suivre en direct les logs d'un service ?
  a: '`journalctl -u nginx -f`.'
- q: Comment voir uniquement les erreurs depuis le dernier démarrage ?
  a: '`journalctl -b -p err` (`-p` filtre par priorité : `emerg` à `debug`).'
- q: Comment voir les logs du démarrage précédent, par exemple après un plantage ?
  a: '`journalctl -b -1`. Il faut que le journal soit persistant (dossier `/var/log/journal`).'
- q: Comment limiter la place prise par le journal ?
  a: '`SystemMaxUse=1G` dans `/etc/systemd/journald.conf`, ou ponctuellement `journalctl --vacuum-size=500M`.'
- q: À quoi sert logrotate ?
  a: 'À faire **tourner** les fichiers de `/var/log` : renommer, compresser et supprimer les anciens, selon les règles de `/etc/logrotate.d/`.'
quiz:
- q: Un serveur a redémarré tout seul cette nuit. Quelle commande aide le plus ?
  options:
  - journalctl -b -1 -e
  - journalctl -f
  - dmesg -w
  - tail /var/log/syslog
  answer: 0
  explain: '`-b -1` affiche le démarrage précédent, `-e` saute à la fin, juste avant le redémarrage. Cherche un `Out of memory`, un kernel panic ou un arrêt demandé.'
- q: Comment voir les logs de nginx entre 14 h et 14 h 30 aujourd'hui ?
  options:
  - journalctl -u nginx --since 14:00 --until 14:30
  - journalctl -u nginx -n 30
  - 'grep 14: /var/log/nginx'
  - journalctl --today nginx
  answer: 0
  explain: '`--since` et `--until` acceptent aussi `yesterday`, `-1h` ou une date complète.'
---

Sur une distribution avec systemd, **journald** collecte les logs des services, du noyau et du démarrage dans un journal indexé.

> **Les outils cités dans cette fiche.**
> - **journald** : le service de systemd qui collecte les logs ; **journalctl** est la commande pour les lire et les filtrer.
> - **dmesg** : affiche les messages du noyau (matériel, disques, OOM killer). `journalctl -k` donne la même chose.
> - **rsyslog** : l'ancien collecteur de logs, qui écrit des fichiers texte dans `/var/log` et sait les envoyer vers un serveur distant. Il cohabite souvent avec journald.
> - **logrotate** : archive, compresse et supprime les vieux fichiers de log pour qu'ils ne remplissent pas le disque.
> - **Loki** et **Elasticsearch** : bases qui centralisent les logs de toutes les machines et permettent d'y chercher.
> - **SIEM** (Security Information and Event Management) : outil de sécurité qui centralise les logs pour y détecter des attaques (connexions suspectes, élévations de droits). Exemples : Splunk, Wazuh, Elastic Security.
> - **PID** : le numéro unique d'un processus ; **SIGHUP** et **SIGUSR1** sont des signaux qu'on envoie à un processus, souvent pour lui demander de recharger sa configuration ou de rouvrir ses fichiers.
> - **démon** : un programme qui tourne en arrière-plan en permanence (sshd, dockerd).
> - **inode** : la fiche d'un fichier sous Linux (propriétaire, droits, emplacement des données), sans son nom.

## Les filtres essentiels

```bash
journalctl -u api -f                   # suivre un service
journalctl -u api --since -1h          # la dernière heure
journalctl -b -p warning               # avertissements et pire, depuis le boot
journalctl -k                          # messages du noyau (comme dmesg)
journalctl _PID=1234
journalctl -u api -o json-pretty -n 5  # format structuré
journalctl --list-boots
```

| Priorité | Niveau |
| --- | --- |
| 0 à 2 | `emerg`, `alert`, `crit` |
| 3 | `err` |
| 4 | `warning` |
| 5 à 7 | `notice`, `info`, `debug` |

## Persistance et taille

```ini
# /etc/systemd/journald.conf
[Journal]
Storage=persistent
SystemMaxUse=1G
```

```bash
journalctl --disk-usage
journalctl --vacuum-time=14d
```

## logrotate pour les fichiers classiques

```
/var/log/api/*.log {
    daily
    rotate 14
    compress
    missingok
    notifempty
    copytruncate
}
```

## Ce que journald change

Historiquement, chaque service écrivait ses fichiers texte dans `/var/log` et un démon (rsyslog) en collectait certains. **journald** capture tout ce qu'un service systemd écrit sur sa sortie standard et d'erreur, plus les messages du noyau, et le range dans un journal **indexé** avec des métadonnées : l'unité, le PID, l'utilisateur, la priorité, l'heure exacte, le numéro de démarrage.

C'est ce qui permet les filtres précis (`-u`, `_PID=`, `--since`, `-p`) sans `grep` approximatif. Les applications modernes n'ont donc plus besoin de gérer leurs fichiers de log : elles écrivent sur la sortie standard, et journald (ou Docker, ou Kubernetes) s'occupe du reste.

Le journal est binaire : on le lit avec `journalctl`, pas avec `cat`. Par défaut sur certaines distributions, il est stocké en mémoire (`/run/log/journal`) et **perdu au redémarrage** : `Storage=persistent` (ou la simple création de `/var/log/journal`) le garde sur disque. Indispensable pour comprendre pourquoi une machine a redémarré : `journalctl -b -1` montre le démarrage précédent.

## Lire un log efficacement

1. **Délimite dans le temps** : `--since "2026-10-22 14:00" --until "14:30"`, autour de l'incident.
2. **Filtre par gravité** : `-p err` d'abord, puis élargis.
3. **Cherche la première erreur**, pas la dernière : les erreurs en cascade qui suivent ne sont que des conséquences.
4. **Corrèle** : `journalctl --since … ` sans `-u` montre ce que faisait le reste du système au même moment (OOM killer, disque, réseau).

## Pourquoi faire tourner les logs

Un fichier de log grandit sans limite jusqu'à remplir le disque. **logrotate** (lancé chaque jour par un timer) archive le fichier courant, le compresse, et supprime les plus anciens. Le point délicat est que l'application garde son fichier **ouvert** : si logrotate se contente de le renommer, elle continue d'écrire dans l'ancien (même inode). D'où les deux stratégies : `copytruncate` (copier puis vider le fichier en place) ou `postrotate` (renommer, puis demander à l'appli de rouvrir ses fichiers, souvent avec `SIGHUP` ou `SIGUSR1`).

Sur une infra de plusieurs machines, les logs locaux ne suffisent pas : on les envoie vers un système central (Loki, Elasticsearch, un SIEM) pour chercher sur toutes les machines à la fois et les garder si une machine disparaît.

> **À retenir.** `copytruncate` évite de redémarrer l'appli mais peut perdre quelques lignes. Si l'appli sait rouvrir ses fichiers sur un signal, préfère `postrotate` avec ce signal.
