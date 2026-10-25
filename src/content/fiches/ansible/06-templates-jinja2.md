---
title: 'Templates Jinja2 : générer des fichiers de configuration'
chapter: 6
order: 1
duration: 12
level: intermédiaire
tags:
- jinja2
- template
- filtres
cards:
- q: Que fait le module `template` ?
  a: Il lit un fichier `.j2` sur le nœud de contrôle, remplace les expressions Jinja2 par les valeurs des variables **de la machine visée**, puis dépose le résultat sur cette machine. Chaque serveur reçoit donc sa propre version.
- q: Différence entre `{{ ... }}` et `{% ... %}` ?
  a: '`{{ ... }}` **affiche** une valeur. `{% ... %}` est une **instruction** (condition `if`, boucle `for`) qui n''affiche rien elle-même.'
- q: Qu'est-ce qu'un filtre Jinja2 ?
  a: 'Une transformation appliquée à une valeur avec `|` : `{{ nom | upper }}`, `{{ liste | join('','') }}`, `{{ port | default(80) }}`. Ils s''enchaînent de gauche à droite.'
- q: À quoi sert le filtre `default` ?
  a: 'À donner une valeur de secours quand la variable n''est pas définie : `{{ workers | default(4) }}`. Sans lui, une variable absente fait échouer la tâche.'
- q: Pourquoi utiliser `validate` dans une tâche `template` ?
  a: 'Pour tester le fichier généré **avant** de remplacer l''ancien : `validate: nginx -t -c %s`. Si le test échoue, l''ancien fichier reste en place et le service ne casse pas.'
- q: Pourquoi mettre `{{ ansible_managed }}` en tête d'un template ?
  a: Pour écrire dans le fichier généré un commentaire du type « Géré par Ansible ». Celui qui l'ouvre sur le serveur sait qu'une modification à la main sera écrasée.
- q: Quand préférer `copy` à `template` ?
  a: Quand le fichier est **identique partout** et ne contient aucune variable. `copy` le dépose tel quel, sans passer par Jinja2.
quiz:
- q: Ton template contient `{{ db_password }}` mais la variable n'est pas définie pour une machine. Que se passe-t-il ?
  options:
  - Le texte `{{ db_password }}` est écrit tel quel
  - Une ligne vide est écrite
  - La tâche échoue avec « undefined variable »
  - Ansible demande la valeur
  answer: 2
  explain: 'Par défaut, une variable indéfinie est une erreur. C''est voulu : mieux vaut échouer que déposer une configuration incomplète.'
- q: Tu veux générer une ligne `server` par machine du groupe `web` dans la configuration de HAProxy. Qu'utilises-tu ?
  options:
  - Une boucle `{% for h in groups['web'] %}` dans le template
  - Une tâche `lineinfile` par machine
  - Un fichier écrit à la main
  - Le filtre `upper`
  answer: 0
  explain: La boucle parcourt la liste des machines du groupe ; `hostvars[h]` donne accès à leurs IP.
- q: Que donne `{{ ['a', 'b', 'c'] | join(', ') }}` ?
  options:
  - abc
  - Une erreur
  - '[''a'', ''b'', ''c'']'
  - a, b, c
  answer: 3
  explain: '`join` colle les éléments d''une liste avec le séparateur donné.'
- q: Un template de configuration nginx est faux et casserait le service. Comment éviter de le déployer ?
  options:
  - Mettre `ignore_errors`
  - Ajouter `validate` avec `nginx -t`
  - Utiliser `copy` à la place
  - Lancer avec `-vvv`
  answer: 1
  explain: '`validate` teste le fichier temporaire ; s''il est invalide, la tâche échoue et l''ancien fichier n''est pas touché.'
---

Les fichiers de configuration se ressemblent d'un serveur à l'autre mais ne sont jamais tout à fait identiques : une IP, un nombre de workers, une liste de membres de cluster. Plutôt que d'en écrire un par machine, on écrit un **template** avec des trous, et Ansible le remplit avec les variables de chaque machine. Le langage de ces trous s'appelle **Jinja2**.

> **Les outils cités dans cette fiche.**
> - **Jinja2** : un moteur de gabarits écrit en Python. Il remplace des expressions entre accolades par des valeurs et sait faire des conditions et des boucles.
> - **template** (module `ansible.builtin.template`) : génère un fichier à partir d'un `.j2` et le dépose sur la machine.
> - **filtre** : une fonction appliquée à une valeur avec le symbole `|` (barre verticale, ou « pipe »).
> - **nginx**, **HAProxy** : un serveur web et un répartiteur de charge, pris ici comme exemples de logiciels à configurer.
> - **ansible.utils**, **community.general** : des collections (paquets de modules et de filtres supplémentaires, chapitre 8).

## Un premier template

Les templates se rangent dans un dossier `templates/` et portent l'extension `.j2` :

```jinja
# templates/nginx.conf.j2
# {{ ansible_managed }}
user www-data;
worker_processes {{ ansible_facts['processor_vcpus'] }};

events {
    worker_connections {{ nginx_worker_connections | default(1024) }};
}

http {
    server {
        listen {{ nginx_port }};
        server_name {{ inventory_hostname }};
    }
}
```

```yaml
- name: Générer la configuration nginx
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    mode: "0644"
    validate: nginx -t -c %s
  notify: Recharger nginx
```

Le rendu se fait **sur le nœud de contrôle**, avec les variables de la machine visée. Sur une machine à 4 vCPU, la ligne devient `worker_processes 4;`. Le module compare ensuite avec le fichier présent : s'il est identique, la tâche est `ok` et le handler ne part pas.

`validate` est la ceinture de sécurité : Ansible écrit le résultat dans un fichier temporaire (le `%s`), lance la commande de test, et ne remplace le vrai fichier que si elle réussit.

## Les trois syntaxes

| Syntaxe | Rôle | Exemple |
| --- | --- | --- |
| `{{ ... }}` | afficher une valeur | `{{ nginx_port }}` |
| `{% ... %}` | instruction (if, for) | `{% if tls_enabled %}` |
| `{# ... #}` | commentaire, absent du résultat | `{# à revoir #}` |

## Conditions et boucles

```jinja
{% if tls_enabled | default(false) %}
    listen 443 ssl;
    ssl_certificate     /etc/ssl/{{ inventory_hostname }}.crt;
    ssl_certificate_key /etc/ssl/{{ inventory_hostname }}.key;
{% endif %}

upstream app {
{% for hote in groups['app'] %}
    server {{ hostvars[hote]['ansible_facts']['default_ipv4']['address'] }}:8080;
{% endfor %}
}
```

Les boucles servent surtout à lister des membres : serveurs d'un pool, nœuds d'un cluster etcd ou Galera, règles de pare-feu. Pour un dictionnaire, on parcourt les paires : `{% for nom, port in services.items() %}`.

Les lignes `{% ... %}` laissent parfois des lignes vides dans le résultat. Écrire `{%-` ou `-%}` supprime les espaces et retours à la ligne du côté du tiret.

## Les filtres les plus utiles

| Filtre | Effet | Exemple |
| --- | --- | --- |
| `default(x)` | valeur de secours | `{{ port \| default(80) }}` |
| `upper`, `lower` | majuscules, minuscules | `{{ env \| upper }}` |
| `join(',')` | liste vers texte | `{{ dns \| join(' ') }}` |
| `length` | taille d'une liste | `{{ groups['web'] \| length }}` |
| `int`, `bool` | conversion de type | `{{ "8080" \| int }}` |
| `to_nice_yaml`, `to_json` | dictionnaire vers YAML ou JSON | `{{ config \| to_nice_yaml }}` |
| `combine` | fusionner deux dictionnaires | `{{ defauts \| combine(perso) }}` |
| `map(attribute='x')` | extraire un champ de chaque élément | `{{ users \| map(attribute='name') }}` |
| `selectattr` | filtrer une liste | `{{ users \| selectattr('admin') }}` |
| `regex_replace` | remplacer par expression régulière | `{{ nom \| regex_replace('-', '_') }}` |
| `password_hash('sha512')` | hacher un mot de passe pour `/etc/shadow` | module `user` |
| `ansible.utils.ipaddr` | calculs d'adresses IP | `{{ '10.0.1.0/24' \| ansible.utils.ipaddr('net') }}` |

Les filtres s'utilisent aussi **dans les tâches**, pas seulement dans les fichiers `.j2` : `name: "{{ paquets | join(' ') }}"`.

Pour tester un filtre sans écrire de playbook : `ansible localhost -m ansible.builtin.debug -a "msg={{ [3,1,2] | sort }}"`.

## Les lookups

Un **lookup** va chercher une donnée **sur le nœud de contrôle** : un fichier, une variable d'environnement, un secret dans un coffre.

```yaml
- name: Autoriser ma clé SSH
  ansible.posix.authorized_key:
    user: deploy
    key: "{{ lookup('ansible.builtin.file', 'cles/deploy.pub') }}"
```

Retiens la différence : un **filtre** transforme une valeur, un **lookup** en produit une à partir d'une source extérieure. Les lookups reviennent au chapitre 9 pour lire des secrets.

## Bonnes pratiques

- **Peu de logique dans les templates** : si un `.j2` devient un programme, calcule plutôt les valeurs dans des variables.
- Toujours `{{ ansible_managed }}` en tête, pour décourager les modifications à la main.
- `validate` dès que le logiciel sait tester sa configuration (`nginx -t`, `sshd -t`, `visudo -cf`, `haproxy -c -f`).
- Lancer d'abord avec `--check --diff` : le diff montre exactement les lignes qui changeront.

> **À retenir.** Un template `.j2` est rendu sur le nœud de contrôle avec les variables de chaque machine, puis comparé au fichier en place. `{{ }}` affiche, `{% %}` décide ou répète, `|` filtre. `default` évite les variables manquantes, `validate` évite de casser un service avec une configuration fausse.
