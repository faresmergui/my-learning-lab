---
title: 'Rôles et collections : réutiliser et partager'
chapter: 8
order: 1
duration: 13
level: intermédiaire
tags:
- rôles
- collections
- galaxy
- FQCN
cards:
- q: Qu'est-ce qu'un rôle Ansible ?
  a: 'Un dossier à structure fixe (`tasks/`, `handlers/`, `templates/`, `defaults/`…) qui regroupe tout ce qu''il faut pour configurer **une chose** : nginx, PostgreSQL, un agent de supervision. On l''applique à des machines comme une brique.'
- q: Qu'est-ce qu'une collection ?
  a: Un **paquet de distribution** qui contient des modules, des plugins, des filtres et des rôles, sous un nom `namespace.collection` (ex. `community.general`, `openstack.cloud`). C'est l'unité qu'on installe depuis Galaxy.
- q: Que veut dire FQCN ?
  a: '*Fully Qualified Collection Name* : le nom complet d''un module, collection comprise, comme `ansible.builtin.copy`. Il évite toute ambiguïté si deux collections ont un module du même nom.'
- q: Différence entre `import_role` et `include_role` ?
  a: '`import_role` est **statique** : chargé à la lecture du playbook, ses tâches héritent des tags et conditions. `include_role` est **dynamique** : chargé au moment de l''exécution, il peut dépendre d''une variable ou d''une boucle.'
- q: À quoi sert `requirements.yml` ?
  a: À lister les rôles et collections dont le projet a besoin, avec leurs **versions**. `ansible-galaxy install -r requirements.yml` installe le tout, pareil sur tous les postes et en CI.
- q: Où mettre les valeurs qu'un utilisateur du rôle doit pouvoir changer ?
  a: Dans `defaults/main.yml`, avec un commentaire par variable. C'est le contrat public du rôle, et sa priorité la plus faible permet de tout surcharger depuis l'inventaire.
- q: Comment préfixer les variables d'un rôle `nginx` ?
  a: 'Par le nom du rôle : `nginx_port`, `nginx_workers`. Toutes les variables sont globales pour une machine, le préfixe évite qu''un autre rôle écrase les tiennes.'
quiz:
- q: Où place-t-on les tâches principales d'un rôle ?
  options:
  - roles/nginx/main.yml
  - roles/nginx/playbook.yml
  - roles/nginx/tasks/main.yml
  - roles/nginx/defaults/tasks.yml
  answer: 2
  explain: 'Chaque dossier du rôle a son `main.yml`, chargé automatiquement : `tasks/main.yml`, `handlers/main.yml`, `defaults/main.yml`…'
- q: Tu veux appliquer le rôle `monitoring` seulement si la variable `with_monitoring` est vraie, décidée pendant le play. Que choisis-tu ?
  options:
  - '`include_role` avec `when`'
  - '`import_playbook`'
  - Un handler
  - '`roles:` en tête du play'
  answer: 0
  explain: '`include_role` est évalué à l''exécution et accepte facilement conditions et boucles.'
- q: Ton playbook utilise `openstack.cloud.server`. Un collègue a l'erreur « couldn't resolve module ». Que lui manque-t-il probablement ?
  options:
  - Python 3
  - Un inventaire dynamique
  - Les droits sudo
  - La collection `openstack.cloud`, à installer avec ansible-galaxy
  answer: 3
  explain: Les modules hors `ansible.builtin` viennent de collections ; le paquet `ansible-core` seul ne les contient pas. D'où l'intérêt d'un `requirements.yml`.
- q: Pourquoi figer les versions dans requirements.yml ?
  options:
  - C'est obligatoire pour Galaxy
  - Pour qu'une nouvelle version d'une collection ne change pas le comportement de la prod sans prévenir
  - Pour chiffrer les rôles
  - Pour aller plus vite
  answer: 1
  explain: 'Comme pour les providers Terraform ou les images Docker : une version figée rend le résultat reproductible.'
---

Au bout de quelques playbooks, on recopie les mêmes tâches : installer nginx ici, là, et encore là. Un **rôle** range ces tâches, leurs templates et leurs variables par défaut dans un dossier réutilisable. Une **collection** va plus loin : c'est un paquet qu'on installe, qui peut contenir des rôles mais aussi des modules et des plugins. Comprendre les deux, c'est comprendre comment l'écosystème Ansible est organisé.

> **Les outils cités dans cette fiche.**
> - **rôle** : un dossier à structure normalisée qui configure un composant (nginx, PostgreSQL, Docker…).
> - **collection** : un paquet nommé `namespace.nom` qui distribue des modules, plugins, filtres et rôles.
> - **ansible-core** : le moteur Ansible minimal, avec seulement les modules `ansible.builtin`.
> - **ansible** (le paquet) : ansible-core plus une sélection d'environ 80 collections de la communauté.
> - **Ansible Galaxy** (galaxy.ansible.com) : le dépôt public de rôles et collections ; **ansible-galaxy** est la commande qui les installe.
> - **Automation Hub** : l'équivalent de Galaxy chez Red Hat, avec des collections certifiées et supportées (abonnement).
> - **FQCN** : le nom complet d'un module, collection comprise (`ansible.builtin.template`).

## La structure d'un rôle

`ansible-galaxy role init roles/nginx` crée ce squelette :

```
roles/nginx/
├── defaults/main.yml   # variables modifiables (priorité la plus faible)
├── vars/main.yml       # constantes internes (priorité forte)
├── tasks/main.yml      # les tâches
├── handlers/main.yml   # les handlers
├── templates/          # fichiers .j2
├── files/              # fichiers copiés tels quels
├── meta/main.yml       # auteur, plateformes, dépendances
└── README.md           # comment l'utiliser
```

On n'écrit jamais de chemin complet dans un rôle : `src: nginx.conf.j2` cherche tout seul dans `templates/` du rôle, `src: index.html` dans `files/`.

Un rôle bien écrit a un **contrat clair** : ses variables d'entrée sont toutes dans `defaults/main.yml`, préfixées par le nom du rôle et commentées.

```yaml
# roles/nginx/defaults/main.yml
nginx_port: 80             # port d'écoute
nginx_workers: auto        # nombre de processus ; auto = un par CPU
nginx_sites: []            # liste de { name, server_name, root }
```

Depuis ansible-core 2.11, on peut aussi décrire ces entrées dans `meta/argument_specs.yml` : Ansible vérifie alors les types et les valeurs obligatoires avant d'exécuter le rôle.

## Utiliser un rôle

Trois façons, du plus simple au plus souple :

```yaml
- name: Serveurs web
  hosts: web
  roles:                       # 1. en tête du play
    - common
    - role: nginx
      vars:
        nginx_port: 8080

  tasks:
    - name: Rôle statique      # 2. chargé à la lecture
      ansible.builtin.import_role:
        name: hardening

    - name: Rôle dynamique     # 3. chargé à l'exécution
      ansible.builtin.include_role:
        name: monitoring
      when: with_monitoring | bool
```

| | `roles:` / `import_role` | `include_role` |
| --- | --- | --- |
| Chargement | au démarrage | au moment d'arriver à la tâche |
| Tags et `when` | appliqués à chaque tâche du rôle | appliqués à l'inclusion elle-même |
| Boucle (`loop`) | impossible | possible |
| `--list-tasks` montre ses tâches | oui | non |

Règle simple : **statique par défaut**, dynamique quand le rôle dépend d'une valeur connue seulement pendant le play. Même logique pour les fichiers de tâches avec `import_tasks` et `include_tasks`.

## Les dépendances entre rôles

Dans `meta/main.yml`, un rôle peut en exiger un autre :

```yaml
dependencies:
  - role: common
```

Le rôle `common` sera exécuté avant. C'est pratique mais ça cache des choses : beaucoup d'équipes préfèrent lister les rôles explicitement dans le playbook, pour voir l'ordre d'un coup d'œil.

## Les collections

Depuis Ansible 2.10, la plupart des modules ne sont plus dans le moteur mais dans des collections. Quelques-unes que tu croiseras :

| Collection | Contenu |
| --- | --- |
| `ansible.builtin` | les modules de base, toujours présents (`copy`, `template`, `apt`, `service`…) |
| `ansible.posix` | `firewalld`, `mount`, `authorized_key`, `sysctl` |
| `community.general` | des centaines de modules divers |
| `openstack.cloud` | serveurs, réseaux, volumes OpenStack et l'inventaire dynamique |
| `amazon.aws` | EC2, S3, l'inventaire dynamique AWS |
| `kubernetes.core` | appliquer des manifestes, installer des charts Helm |
| `community.postgresql`, `community.mysql` | bases, utilisateurs, droits |

C'est pour ça qu'on écrit les modules avec leur **FQCN** : `ansible.builtin.copy` plutôt que `copy`. On sait d'où vient le module, et `ansible-lint` le demande (chapitre 10).

## Figer ses dépendances

```yaml
# collections/requirements.yml
collections:
  - name: openstack.cloud
    version: ">=2.2.0,<3.0.0"
  - name: community.general
    version: "9.5.0"
roles:
  - name: geerlingguy.docker
    version: "7.4.1"
```

```bash
ansible-galaxy install -r collections/requirements.yml
ansible-galaxy collection list      # ce qui est installé, et où
```

Un `ansible.cfg` à la racine du projet peut indiquer où installer (`collections_path = ./collections`), pour que chaque projet ait ses propres versions.

## Écrire ou réutiliser ?

Galaxy regorge de rôles prêts à l'emploi (ceux de Jeff Geerling, `geerlingguy.*`, sont une référence). Avant d'en adopter un : regarde s'il est maintenu, lis ses `defaults`, et fige sa version. Pour un composant central de ton infra, un rôle maison simple et compris par l'équipe vaut souvent mieux qu'un rôle générique couvrant dix distributions.

> **À retenir.** Un rôle range tout ce qui configure un composant, avec ses entrées publiques dans `defaults/main.yml`, préfixées par son nom. Une collection est le paquet qu'on installe, et chaque module s'écrit avec son FQCN. Les versions des rôles et collections se figent dans `requirements.yml`, comme n'importe quelle dépendance.
