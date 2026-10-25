---
title: 'L''inventaire : dire à Ansible quelles machines gérer'
chapter: 2
order: 1
duration: 10
level: intermédiaire
tags:
- inventaire
- groupes
- inventaire dynamique
cards:
- q: Qu'est-ce que l'inventaire Ansible ?
  a: La liste des machines gérées, rangées en **groupes**, avec éventuellement des variables par hôte ou par groupe. Ansible ne touche qu'aux machines de l'inventaire.
- q: Quels sont les deux groupes qui existent toujours ?
  a: '`all` (toutes les machines) et `ungrouped` (celles qui ne sont dans aucun groupe).'
- q: Comment faire un groupe de groupes ?
  a: 'Avec `children` : un groupe `prod` peut contenir les groupes `web` et `db`. Une variable posée sur `prod` s''applique à toutes leurs machines.'
- q: À quoi sert `ansible_host` ?
  a: 'À donner l''adresse réelle d''une machine quand son nom dans l''inventaire n''est pas résolvable : `web1 ansible_host=10.0.1.11`.'
- q: Qu'est-ce qu'un inventaire dynamique ?
  a: Un inventaire généré à la volée en interrogeant une source (OpenStack, AWS, VMware…) via un **plugin d'inventaire**. Les VM créées ou supprimées apparaissent sans modifier de fichier.
- q: Comment voir ce qu'Ansible comprend de l'inventaire ?
  a: '`ansible-inventory -i inventaire --graph` (l''arbre des groupes) ou `--list` (tout, en JSON, avec les variables).'
quiz:
- q: Une machine est dans les groupes `web` et `prod`. Une commande ciblant `prod` la touche-t-elle ?
  options:
  - Non, seulement `web`
  - Oui
  - Seulement si `prod` est déclaré en premier
  - Seulement avec `--all`
  answer: 1
  explain: Une machine peut appartenir à plusieurs groupes, et elle est concernée par chacun.
- q: Tu crées et supprimes des VM plusieurs fois par jour sur OpenStack. Quel inventaire choisir ?
  options:
  - Un fichier INI mis à jour à la main
  - Un inventaire dynamique avec le plugin OpenStack
  - Le fichier /etc/hosts
  - Aucun, Ansible les trouve seul
  answer: 1
  explain: 'Le plugin interroge l''API OpenStack à chaque lancement : l''inventaire est toujours à jour.'
- q: Que cible le motif `web:&prod` ?
  options:
  - Les machines de web ou de prod
  - Les machines à la fois dans web et dans prod
  - Les machines de web sauf prod
  - Rien, c'est une erreur
  answer: 1
  explain: '`:` fait l''union, `:&` l''intersection et `:!` l''exclusion.'
---

L'**inventaire** est la liste des machines qu'Ansible a le droit de gérer. C'est un simple fichier (ou un script, ou un plugin) qui range les machines en **groupes** : `web`, `db`, `prod`… Les playbooks ne visent jamais une adresse IP en dur : ils visent un groupe, et l'inventaire dit qui est dedans.

> **Les outils cités dans cette fiche.**
> - **inventaire** : le fichier (ou le plugin) qui liste les machines gérées et les range en groupes.
> - **INI** : un format de fichier simple en sections `[groupe]` et lignes `clé=valeur`, l'autre format d'inventaire avec YAML.
> - **plugin d'inventaire** : un composant qui construit l'inventaire en interrogeant une source (API OpenStack, AWS, VMware…).
> - **ansible-inventory** : la commande qui affiche l'inventaire tel qu'Ansible le comprend.
> - **group_vars / host_vars** : des dossiers de variables par groupe ou par machine, chargés automatiquement (détaillés au chapitre 5).
> - **AWS** : le cloud public d'Amazon ; **EC2** est son service de machines virtuelles.

## Un inventaire statique

Le format YAML est le plus lisible :

```yaml
# inventaires/prod/hosts.yml
all:
  children:
    web:
      hosts:
        web1: { ansible_host: 10.0.1.11 }
        web2: { ansible_host: 10.0.1.12 }
    db:
      hosts:
        db1: { ansible_host: 10.0.2.21 }
    prod:
      children:
        web:
        db:
      vars:
        ansible_user: deploy
```

Le format INI existe aussi et se rencontre souvent :

```ini
[web]
web1 ansible_host=10.0.1.11
web2 ansible_host=10.0.1.12

[db]
db1 ansible_host=10.0.2.21

[prod:children]
web
db
```

Quelques variables de connexion reviennent tout le temps :

| Variable | Rôle |
| --- | --- |
| `ansible_host` | adresse réelle si le nom n'est pas résolvable |
| `ansible_user` | utilisateur SSH |
| `ansible_port` | port SSH s'il n'est pas 22 |
| `ansible_python_interpreter` | chemin de Python sur la cible |

## Organiser les variables

Plutôt que de tout mettre dans le fichier d'inventaire, on range les variables à côté, dans deux dossiers qu'Ansible lit automatiquement :

```
inventaires/prod/
├── hosts.yml
├── group_vars/
│   ├── all.yml        # pour toutes les machines
│   └── web.yml        # pour le groupe web
└── host_vars/
    └── db1.yml        # pour db1 seulement
```

Avoir un dossier d'inventaire **par environnement** (`dev`, `staging`, `prod`) est la façon la plus simple de séparer les environnements : le même playbook, lancé avec `-i inventaires/staging`, cible d'autres machines avec d'autres valeurs.

## Cibler des machines

Dans une commande ou un playbook, `hosts:` accepte des motifs :

| Motif | Cible |
| --- | --- |
| `web` | le groupe web |
| `web:db` | web **ou** db |
| `web:&prod` | à la fois dans web **et** dans prod |
| `prod:!db` | prod **sauf** db |
| `web1` | une seule machine |

Et `--limit` restreint un lancement sans modifier le playbook : `ansible-playbook site.yml --limit web1`.

## L'inventaire dynamique

Dans un cloud, les machines naissent et disparaissent. Maintenir un fichier à la main devient impossible. Un **plugin d'inventaire** interroge l'API du cloud à chaque lancement et construit les groupes à partir des métadonnées (nom, tags, projet) :

```yaml
# inventaires/openstack.yml
plugin: openstack.cloud.openstack
expand_hostvars: true
keyed_groups:
  - key: openstack.metadata.role   # une VM avec la métadonnée role=web va dans le groupe role_web
    prefix: role
```

Le principe est le même pour AWS (`amazon.aws.aws_ec2`, groupes par tags) ou VMware. Pour vérifier le résultat :

```bash
ansible-inventory -i inventaires/openstack.yml --graph
```

> **À retenir.** L'inventaire range les machines en groupes, et les playbooks visent des groupes. Un dossier d'inventaire par environnement, avec ses `group_vars` et `host_vars`, garde les choses claires. Dans un cloud, un inventaire dynamique évite de maintenir des listes d'IP à la main.
