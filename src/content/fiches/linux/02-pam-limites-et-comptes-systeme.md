---
title: PAM, limites de ressources et comptes système
chapter: 2
order: 3
duration: 10
tags:
- LFCS
- PAM
- ulimit
cards:
- q: À quoi sert PAM ?
  a: '**Pluggable Authentication Modules** : la couche qui décide comment on s''authentifie et ce qui se passe à l''ouverture d''une session, pour tous les programmes (login, sshd, sudo). Chaque programme a son fichier dans `/etc/pam.d/`.'
- q: Quels sont les quatre types de règles PAM ?
  a: '`auth` (prouver qui on est), `account` (le compte a-t-il le droit, maintenant ?), `password` (changer le mot de passe), `session` (préparer et fermer la session : limites, logs, montage).'
- q: Différence entre `required` et `requisite` dans PAM ?
  a: Les deux doivent réussir. En cas d'échec, `required` **continue** les autres modules puis refuse (l'utilisateur ne sait pas lequel a échoué), `requisite` **refuse tout de suite**.
- q: Où fixe-t-on le nombre maximal de fichiers ouverts pour un utilisateur ?
  a: 'Dans `/etc/security/limits.conf` ou un fichier de `limits.d/` : `alice soft nofile 4096` et `alice hard nofile 8192`. Le module `pam_limits` les applique à l''ouverture de session ; `ulimit -n` affiche la valeur.'
- q: Pourquoi `limits.conf` n'a-t-il aucun effet sur un service systemd ?
  a: 'Un service n''ouvre pas de session PAM. Ses limites se règlent dans l''unité : `LimitNOFILE=65536` dans `[Service]`.'
- q: Comment créer un compte système pour un service ?
  a: '`useradd --system --no-create-home --shell /usr/sbin/nologin monappli` : UID bas (sous 1000), pas de dossier personnel, pas de connexion possible.'
quiz:
- q: Une base de données refuse des connexions avec « Too many open files ». Elle tourne comme service systemd. Où corriges-tu ?
  options:
  - '`/etc/security/limits.conf`'
  - '`LimitNOFILE=` dans l''unité du service'
  - '`ulimit -n` dans ton shell'
  - '`/etc/login.defs`'
  answer: 1
  explain: 'Les services systemd ne passent pas par PAM. Après modification : `systemctl daemon-reload` puis redémarrage du service.'
- q: Que vaut la limite effective si `soft nofile 1024` et `hard nofile 4096` ?
  options:
  - 1024, que l'utilisateur peut monter jusqu'à 4096
  - 4096 toujours
  - 1024 et jamais plus
  - '5120'
  answer: 0
  explain: La limite soft s'applique ; l'utilisateur peut l'augmenter lui-même avec `ulimit` jusqu'à la limite hard, que seul root peut dépasser.
level: intermédiaire
---

La fiche sur sudo et les ACL couvrait qui a le droit de faire quoi. Il reste trois mécanismes que l'examen LFCS demande : **PAM**, qui contrôle la façon dont on se connecte ; les **limites de ressources** par utilisateur ; et les **comptes système**, ces utilisateurs qui ne sont pas des personnes.

> **Les outils cités dans cette fiche.**
> - **PAM** (Pluggable Authentication Modules) : un système de modules que tous les programmes de connexion appellent pour authentifier et ouvrir une session. Sa configuration est dans `/etc/pam.d/`.
> - **pam_pwquality** : un module PAM qui impose des règles de robustesse aux mots de passe.
> - **pam_faillock** : un module PAM qui bloque un compte après plusieurs échecs de connexion.
> - **pam_limits** : le module PAM qui applique les limites de `/etc/security/limits.conf`.
> - **ulimit** : la commande du shell qui affiche et modifie les limites de la session en cours.
> - **chage** : affiche et modifie les règles d'expiration du mot de passe d'un compte.
> - **ACL** : une liste de contrôle d'accès : qui a le droit de faire quoi sur une ressource.
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.
> - **UID** : le numéro qui identifie un utilisateur sous Linux (0 = root).

## Comprendre : PAM est une chaîne de contrôles

Quand tu te connectes en SSH ou lances `sudo`, le programme ne vérifie pas lui-même ton mot de passe. Il demande à PAM, qui lit le fichier du programme (`/etc/pam.d/sshd`, `/etc/pam.d/sudo`) et passe par une suite de modules, comme des contrôles successifs à l'entrée d'un bâtiment.

```
# /etc/pam.d/common-auth (extrait, Debian)
auth   requisite   pam_faillock.so preauth
auth   [success=1 default=ignore]  pam_unix.so nullok
auth   requisite   pam_deny.so
auth   required    pam_permit.so
```

Chaque ligne a trois parties : le **type**, le **contrôle** et le **module**.

| Type | Question posée |
| --- | --- |
| `auth` | es-tu bien qui tu dis être ? |
| `account` | ce compte a-t-il le droit d'entrer maintenant (expiré, bloqué, horaires) ? |
| `password` | règles pour changer le mot de passe |
| `session` | que préparer à l'entrée et à la sortie (limites, logs, dossier) ? |

| Contrôle | Si le module échoue | Si le module réussit |
| --- | --- | --- |
| `required` | refus, mais on continue la chaîne | on continue |
| `requisite` | refus immédiat | on continue |
| `sufficient` | on continue | accès accordé tout de suite (si rien n'a échoué avant) |
| `optional` | sans effet | sans effet |

Une erreur dans un fichier PAM peut **empêcher toute connexion**, root compris. Avant d'en modifier un, garde une session root ouverte dans un autre terminal pour pouvoir revenir en arrière.

## Des usages courants

```
# Robustesse des mots de passe : /etc/security/pwquality.conf
minlen = 12
minclass = 3

# Blocage après 5 échecs pendant 15 minutes : /etc/security/faillock.conf
deny = 5
unlock_time = 900
```

```bash
faillock --user alice            # voir les échecs
faillock --user alice --reset    # débloquer
chage -l alice                   # expiration du mot de passe
chage -M 90 -W 7 alice           # changement tous les 90 jours, alerte 7 jours avant
```

## Les limites de ressources

Un utilisateur ou un programme qui ouvre trop de fichiers ou lance trop de processus peut gêner toute la machine. Les limites fixent un plafond **par session**.

```
# /etc/security/limits.d/90-appli.conf
# domaine   type   élément   valeur
alice       soft   nofile    4096
alice       hard   nofile    8192
@dev        hard   nproc     500
*           hard   core      0
```

- **soft** : la limite appliquée ; l'utilisateur peut l'augmenter lui-même jusqu'à la valeur hard.
- **hard** : le plafond, que seul root peut dépasser.
- éléments courants : `nofile` (fichiers ouverts), `nproc` (processus), `core` (taille des fichiers de crash), `memlock`.

```bash
ulimit -a          # toutes les limites de ma session
ulimit -n          # fichiers ouverts
ulimit -Sn 8192    # monter la limite soft (jusqu'au hard)
```

Le piège classique : ces limites passent par **pam_limits**, donc par une session de connexion. Un service lancé par systemd n'en ouvre pas : on règle ses limites dans l'unité, par exemple `LimitNOFILE=65536` dans la section `[Service]`.

## Les comptes système

Beaucoup de comptes dans `/etc/passwd` ne sont pas des personnes : `www-data`, `postgres`, `systemd-network`… Ils permettent de lancer chaque service avec **ses propres droits** au lieu de root.

```bash
useradd --system --no-create-home --shell /usr/sbin/nologin monappli
getent passwd monappli
# monappli:x:998:998::/home/monappli:/usr/sbin/nologin
```

- UID **sous 1000** (les bornes sont dans `/etc/login.defs`) ;
- shell `nologin` : personne ne peut ouvrir une session avec ;
- pas de mot de passe utilisable.

Pour bloquer un compte humain sans le supprimer : `usermod -L alice` (verrouille le mot de passe) et `chage -E 0 alice` (fait expirer le compte, ce qui bloque aussi les connexions par clé SSH).

> **À retenir.** PAM est une chaîne de modules par programme dans `/etc/pam.d/` ; une erreur peut bloquer toutes les connexions, donc garde une session root ouverte. Les limites de `limits.conf` valent pour les sessions, pas pour les services systemd (`LimitNOFILE=`). Un service tourne sous un compte système sans shell ni mot de passe.
