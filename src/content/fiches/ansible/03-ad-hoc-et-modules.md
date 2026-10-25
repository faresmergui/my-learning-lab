---
title: Commandes ad hoc et modules du quotidien
chapter: 3
order: 1
duration: 10
level: intermédiaire
tags:
- modules
- ad hoc
- FQCN
cards:
- q: Qu'est-ce qu'une commande ad hoc ?
  a: 'Une action ponctuelle lancée avec la commande `ansible`, sans écrire de playbook : `ansible web -m ping`. Pratique pour vérifier ou dépanner, pas pour configurer durablement.'
- q: Que vérifie le module `ping` ?
  a: Qu'Ansible peut se connecter en SSH **et** exécuter Python sur la machine. Ce n'est pas un ping ICMP.
- q: Pourquoi préférer un module dédié à `shell` ou `command` ?
  a: Les modules dédiés (`apt`, `copy`, `service`…) sont **idempotents** et savent dire s'ils ont changé quelque chose. `shell` exécute la commande à chaque fois et répond toujours `changed`.
- q: Différence entre `command` et `shell` ?
  a: '`command` lance un programme sans passer par un shell (pas de `|`, `>`, `$VAR`), donc plus sûr. `shell` passe par `/bin/sh` et permet pipes et redirections.'
- q: Que veut dire FQCN ?
  a: '*Fully Qualified Collection Name* : le nom complet d''un module, collection comprise, comme `ansible.builtin.copy`. Il évite toute ambiguïté entre deux modules du même nom.'
- q: Comment lire la documentation d'un module en local ?
  a: '`ansible-doc ansible.builtin.copy` : paramètres, valeurs par défaut et exemples. `ansible-doc -l` liste les modules installés.'
quiz:
- q: Tu veux savoir rapidement si les 30 serveurs web répondent à Ansible. Quelle commande ?
  options:
  - ansible-playbook ping.yml
  - ansible web -m ping
  - ping web
  - ssh web ping
  answer: 1
  explain: Une commande ad hoc avec le module ping teste SSH et Python sur tout le groupe.
- q: 'Une tâche `shell: echo ''x'' >> /etc/fichier` est lancée trois fois. Que contient le fichier ?'
  options:
  - Une ligne x
  - Trois lignes x
  - Rien
  - Une erreur
  answer: 1
  explain: '`shell` n''est pas idempotent : la ligne est ajoutée à chaque passage. `lineinfile` règle le problème.'
- q: Quel module garantit qu'une ligne est présente une seule fois dans un fichier ?
  options:
  - ansible.builtin.copy
  - ansible.builtin.lineinfile
  - ansible.builtin.shell
  - ansible.builtin.file
  answer: 1
  explain: '`lineinfile` vérifie si la ligne existe avant de l''ajouter ou de la modifier.'
---

Un **module** est la plus petite unité de travail d'Ansible : un programme qui sait faire une chose précise (installer un paquet, copier un fichier, démarrer un service) en vérifiant d'abord si c'est nécessaire. Ansible en fournit des centaines. Tout ce que tu écris ensuite, playbooks et rôles, n'est qu'une façon d'enchaîner des modules.

> **Les outils cités dans cette fiche.**
> - **module** : un petit programme qu'Ansible envoie sur la machine pour faire une action précise, en vérifiant d'abord si elle est nécessaire.
> - **commande ad hoc** : une commande `ansible` qui lance un seul module, sans écrire de playbook.
> - **FQCN** : le nom complet d'un module, collection comprise, comme `ansible.builtin.copy`.
> - **collection** : un paquet de modules et de plugins (`ansible.posix`, `community.general`, `openstack.cloud`), détaillé au chapitre 8.
> - **apt / dnf** : les gestionnaires de paquets de Debian-Ubuntu et de Red Hat-Rocky ; **systemd** est le gestionnaire de services des Linux modernes.
> - **become** : l'élévation de privilèges d'Ansible, par défaut via **sudo** (exécuter une commande en root).

## Les commandes ad hoc

La commande `ansible` lance un seul module sur un groupe de machines, sans fichier :

```bash
ansible web -i inventaires/prod -m ansible.builtin.ping
ansible web -m ansible.builtin.command -a "uptime"
ansible db  -m ansible.builtin.apt -a "name=htop state=present" --become
ansible all -m ansible.builtin.setup -a "filter=ansible_distribution*"
```

- `-m` choisit le module, `-a` lui passe ses arguments ;
- `--become` exécute en root (via sudo) ;
- `-f 20` lance 20 machines en parallèle au lieu de 5.

C'est l'outil idéal pour **vérifier** ou **dépanner** (« quelle version du noyau partout ? »). Pour une configuration durable, on écrit un playbook : il se relit, se versionne et se rejoue.

## Les modules à connaître

| Besoin | Module |
| --- | --- |
| paquets | `ansible.builtin.apt`, `ansible.builtin.dnf`, ou `ansible.builtin.package` (générique) |
| fichiers | `copy` (dépose un fichier), `template` (fichier généré), `file` (droits, dossiers, liens) |
| une ligne dans un fichier | `lineinfile`, `blockinfile` pour un bloc |
| services | `ansible.builtin.service` ou `ansible.builtin.systemd` |
| utilisateurs | `ansible.builtin.user`, `ansible.builtin.group`, `ansible.posix.authorized_key` |
| récupérer un fichier | `get_url`, `unarchive` |
| commandes | `command`, `shell` (en dernier recours) |
| informations | `setup` (les facts), `stat` (un fichier existe-t-il ?) |

## Pourquoi éviter `shell`

`shell` et `command` exécutent ce qu'on leur donne, à chaque passage, et répondent toujours `changed`. On perd l'idempotence et le rapport devient illisible. Quand c'est inévitable, on rend la tâche idempotente soi-même :

```yaml
- name: Initialiser la base une seule fois
  ansible.builtin.command: /opt/app/bin/init-db
  args:
    creates: /var/lib/app/.initialized   # ne s'exécute pas si ce fichier existe
```

ou on indique quand la tâche a vraiment changé quelque chose avec `changed_when`.

## Le nom complet des modules

Depuis Ansible 2.10, les modules sont rangés en **collections**. Le nom complet (FQCN) indique la collection : `ansible.builtin.copy`, `community.general.ufw`, `openstack.cloud.server`. Écrire seulement `copy` marche encore, mais ansible-lint le signale : le nom complet évite les surprises si deux collections ont un module du même nom.

> **À retenir.** Un module fait une chose et vérifie d'abord si c'est utile. Les commandes ad hoc servent à vérifier et dépanner, les playbooks à configurer. Préférer toujours un module dédié à `shell`, et écrire les noms complets (`ansible.builtin.copy`).
