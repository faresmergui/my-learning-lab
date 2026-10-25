---
title: Utilisateurs, sudo et ACL
chapter: 2
order: 2
duration: 8
level: intermédiaire
tags:
- LFCS
cards:
- q: Où sont définis les utilisateurs et leurs mots de passe ?
  a: '`/etc/passwd` pour les comptes (UID, shell, dossier), `/etc/shadow` pour les mots de passe hachés (lisible par root seulement), `/etc/group` pour les groupes.'
- q: Comment ajouter un utilisateur existant à un groupe sans retirer les autres ?
  a: '`usermod -aG docker fares`. Sans `-a`, la liste des groupes secondaires est **remplacée**.'
- q: Pourquoi modifier sudoers avec `visudo` ?
  a: '`visudo` vérifie la syntaxe avant d''enregistrer. Une erreur dans `/etc/sudoers` peut bloquer tout accès sudo.'
- q: À quoi servent les ACL ?
  a: À donner des droits à **plusieurs utilisateurs ou groupes** sur un fichier, au-delà du trio propriétaire / groupe / autres. `setfacl -m u:alice:rw fichier`.
- q: Comment voir sous quel utilisateur et quels groupes tu agis ?
  a: '`id`. Après un ajout à un groupe, il faut une nouvelle session (ou `newgrp`) pour qu''il soit pris en compte.'
quiz:
- q: Tu ajoutes `fares` au groupe `docker`, mais `docker ps` refuse toujours l'accès. Pourquoi ?
  options:
  - Il faut redémarrer Docker
  - La session actuelle n'a pas encore le nouveau groupe
  - Le groupe docker n'existe pas
  - Il faut le mot de passe root
  answer: 1
  explain: Les groupes sont lus à l'ouverture de session. Reconnecte-toi ou lance `newgrp docker`.
- q: Quelle ligne sudoers permet au groupe `ops` de redémarrer nginx, et rien d'autre ?
  options:
  - '%ops ALL=(ALL) ALL'
  - '%ops ALL=(root) /usr/bin/systemctl restart nginx'
  - 'ops ALL=NOPASSWD: ALL'
  - '%ops nginx=ALL'
  answer: 1
  explain: Le `%` désigne un groupe. Limiter la commande exacte suit le principe du moindre privilège.
---

Linux identifie chaque utilisateur par un **UID** et chaque groupe par un **GID**. Les noms ne sont que des étiquettes.


> **Les termes et outils cités dans cette fiche.**
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).
> - **hachage** : calculer une empreinte d'un contenu ; impossible de revenir au contenu à partir de l'empreinte.
> - **ACL** : une liste de contrôle d'accès : qui a le droit de faire quoi sur une ressource.

## Les fichiers de base

```bash
grep fares /etc/passwd
# fares:x:1000:1000:Fares:/home/fares:/bin/zsh
#   nom  │ UID  GID  commentaire  dossier   shell
#        └ mot de passe dans /etc/shadow
id fares
```

## Gérer les comptes

```bash
useradd -m -s /bin/bash -G devops alice   # -m crée le dossier personnel
passwd alice
usermod -aG docker alice                  # -a : ajoute sans remplacer
userdel -r alice                          # -r supprime aussi son dossier
```

## sudo

```bash
visudo -f /etc/sudoers.d/ops
# %ops ALL=(root) /usr/bin/systemctl restart nginx, /usr/bin/journalctl
sudo -l                                   # ce que tu as le droit de faire
```

> **À retenir.** Ajoute tes règles dans `/etc/sudoers.d/` plutôt que dans `/etc/sudoers` : plus lisible, et plus facile à gérer avec Ansible.

## Ce qu'est vraiment un utilisateur

Pour le noyau, un utilisateur n'est qu'un **nombre** (UID). Le nom `fares` est une traduction stockée dans `/etc/passwd`. Conséquences pratiques :

- **UID 0, c'est root**, quel que soit le nom ;
- les UID sous 1000 sont des **comptes système** (`www-data`, `postgres`, `nobody`) : ils n'ont pas de mot de passe, souvent pas de shell (`/usr/sbin/nologin`), et servent à faire tourner un service avec des droits limités. Si nginx est compromis, l'attaquant n'a que les droits de `www-data` ;
- quand tu copies des fichiers vers une autre machine ou que tu montes un volume dans un conteneur, ce sont les **numéros** qui voyagent. Le fichier de l'UID 1000 appartiendra à « celui qui a l'UID 1000 » de l'autre côté, quel que soit son nom.

Le mot de passe (sous forme de hash) est dans `/etc/shadow`, lisible seulement par root. `/etc/group` liste les groupes et leurs membres.

## Pourquoi sudo plutôt que root

`su -` ouvre un shell root : tout ce qui suit est fait « par root », sans trace de qui était derrière. `sudo commande` exécute **une** commande avec des droits élevés, après avoir vérifié que **toi** tu en as le droit, et la journalise (`journalctl _COMM=sudo`). On peut aussi limiter les commandes autorisées, comme dans l'exemple ci-dessus.

Attention aux droits faussement limités : autoriser `sudo vim`, `sudo less` ou `sudo tar` revient à donner un shell root, car ces programmes savent lancer des commandes. Le site GTFOBins recense ces cas.

Un changement de groupe (`usermod -aG docker alice`) ne prend effet qu'à la **prochaine connexion** d'alice : ses sessions ouvertes gardent l'ancienne liste. Et appartenir au groupe `docker` équivaut à être root, puisqu'on peut lancer un conteneur qui monte `/`.

## Quand utiliser des ACL

Le modèle classique n'a qu'**un** propriétaire et **un** groupe par fichier. Dès qu'il faut « alice en écriture, l'équipe data en lecture, le reste rien », il ne suffit plus. Les ACL ajoutent des règles pour des utilisateurs ou groupes supplémentaires. À utiliser avec parcimonie : elles sont invisibles au premier coup d'œil (juste un `+`) et oubliées lors des copies si on ne passe pas `cp -a` ou `rsync -A`.

## Les ACL

```bash
setfacl -m u:alice:rw rapport.csv
setfacl -d -m g:data:rwx /srv/data    # -d : droits par défaut pour les nouveaux fichiers
getfacl rapport.csv
```

Un `+` à la fin des droits dans `ls -l` (`-rw-rw-r--+`) signale une ACL.
