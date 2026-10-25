---
title: Conditions, boucles et gestion des erreurs
chapter: 7
order: 1
duration: 13
level: intermédiaire
tags:
- when
- loop
- block
- rescue
- failed_when
cards:
- q: Comment écrire une condition sur une tâche ?
  a: 'Avec `when`, suivi d''une expression **sans** accolades : `when: ansible_facts[''os_family''] == ''Debian''`. Si elle est fausse, la tâche est `skipped`.'
- q: Comment répéter une tâche sur une liste ?
  a: 'Avec `loop: [a, b, c]` (ou une variable de liste). Dans la tâche, l''élément courant s''appelle `item`.'
- q: À quoi servent `block`, `rescue` et `always` ?
  a: '`block` regroupe des tâches ; si l''une échoue, `rescue` s''exécute (comme un `catch`) ; `always` s''exécute dans tous les cas (comme un `finally`).'
- q: Différence entre `failed_when` et `ignore_errors` ?
  a: '`failed_when` **redéfinit** ce qu''est un échec (ex. : le code retour 2 est normal). `ignore_errors` laisse la tâche échouer mais continue quand même, en l''affichant en rouge.'
- q: À quoi sert `changed_when` ?
  a: 'À dire quand une tâche a réellement changé quelque chose. Pour une commande qui ne fait que lire, `changed_when: false` évite un faux `changed` à chaque passage.'
- q: Comment attendre qu'un service réponde avant de continuer ?
  a: 'Avec `until`, `retries` et `delay` : la tâche est rejouée jusqu''à ce que la condition soit vraie, par exemple un `uri` qui renvoie 200.'
- q: 'Que fait `any_errors_fatal: true` ?'
  a: Arrête le play sur **toutes** les machines dès qu'une seule échoue. Utile quand continuer laisserait un cluster dans un état incohérent.
quiz:
- q: 'Tu écris `when: "{{ install_nginx }}"`. Que dit Ansible ?'
  options:
  - Un avertissement, car `when` attend une expression sans accolades
  - Une erreur fatale
  - Il ignore la condition
  - Rien, c'est la bonne syntaxe
  answer: 0
  explain: '`when` est déjà évalué comme du Jinja2. On écrit `when: install_nginx`.'
- q: La commande `grep -q motif fichier` renvoie 1 quand le motif est absent, ce qui est un cas normal pour toi. Comment éviter que la tâche échoue ?
  options:
  - '`changed_when: false`'
  - '`ignore_errors: true`'
  - '`failed_when: resultat.rc > 1` avec `register: resultat`'
  - '`when: false`'
  answer: 2
  explain: Seul un code supérieur à 1 (vraie erreur de grep) compte comme échec. `ignore_errors` masquerait aussi les vraies erreurs.
- q: Une migration de base de données échoue au milieu d'un `block`. Tu veux restaurer la sauvegarde puis remettre l'application en ligne dans tous les cas. Où mets-tu chaque action ?
  options:
  - Restauration dans `always`, remise en ligne dans `rescue`
  - Restauration dans `rescue`, remise en ligne dans `always`
  - Les deux dans `rescue`
  - Les deux après le block, avec `ignore_errors`
  answer: 1
  explain: '`rescue` ne tourne qu''en cas d''échec (restaurer) ; `always` tourne quoi qu''il arrive (remettre en ligne).'
- q: Tu crées trois utilisateurs avec `loop`. Comment accéder à leur nom dans la tâche ?
  options:
  - '`{{ loop.index }}`'
  - '`{{ user }}`'
  - '`{{ loop }}`'
  - '`{{ item }}` ou `{{ item.name }}` si ce sont des dictionnaires'
  answer: 3
  explain: 'L''élément courant est `item` ; on peut le renommer avec `loop_control: loop_var`.'
---

Une vraie infrastructure n'est jamais homogène : deux distributions, des serveurs avec ou sans disque de données, des commandes qui échouent parfois. Ansible offre trois outils pour s'y adapter : les **conditions** (faire ou ne pas faire une tâche), les **boucles** (la faire plusieurs fois) et la **gestion d'erreurs** (décider quoi faire quand ça rate).

> **Les outils cités dans cette fiche.**
> - **when** : la condition d'une tâche, une expression Jinja2 évaluée pour chaque machine.
> - **loop** : répète une tâche pour chaque élément d'une liste ; l'élément courant s'appelle `item`.
> - **block / rescue / always** : regroupent des tâches et gèrent leur échec, comme un `try / catch / finally` en programmation.
> - **register** : garde le résultat d'une tâche dans une variable (vu au chapitre 5).
> - **uri** : un module qui envoie une requête HTTP, souvent utilisé pour tester qu'un service répond.
> - **code retour** (`rc`) : le nombre renvoyé par une commande Linux ; 0 veut dire succès, le reste une erreur ou un cas particulier.

## Les conditions avec when

```yaml
- name: Installer nginx sur Debian
  ansible.builtin.apt:
    name: nginx
  when: ansible_facts['os_family'] == 'Debian'

- name: Installer nginx sur Rocky
  ansible.builtin.dnf:
    name: nginx
  when: ansible_facts['os_family'] == 'RedHat'
```

Quelques formes à connaître :

| Condition | Vraie si |
| --- | --- |
| `when: activer_tls` | la variable vaut vrai |
| `when: not activer_tls` | elle vaut faux |
| `when: app_version is defined` | la variable existe |
| `when: "'web' in group_names"` | la machine est dans le groupe web |
| `when: resultat.rc != 0` | la commande enregistrée a échoué |
| `when: resultat is changed` | la tâche enregistrée a changé quelque chose |
| une liste sous `when:` | **toutes** les conditions sont vraies (ET) |
| `when: a or b` | au moins une est vraie (OU) |

Piège classique : `when` attend une expression **sans** accolades. Et si la valeur vient d'un texte (`"false"` passé en `-e`), convertis-la : `when: activer_tls | bool`.

## Les boucles avec loop

```yaml
- name: Créer les comptes de l'équipe
  ansible.builtin.user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
    shell: /bin/bash
  loop:
    - { name: alice, groups: sudo }
    - { name: bob,   groups: docker }
  loop_control:
    label: "{{ item.name }}"   # n'affiche que le nom dans la sortie
```

Bon réflexe : beaucoup de modules acceptent **directement une liste**, ce qui est plus rapide qu'une boucle (une seule transaction au lieu d'une par élément) :

```yaml
- name: Installer les outils
  ansible.builtin.apt:
    name: [curl, jq, htop]
```

Les anciennes formes `with_items`, `with_dict`… fonctionnent encore mais `loop` est la forme moderne. Pour un dictionnaire : `loop: "{{ mon_dict | dict2items }}"`, puis `item.key` et `item.value`.

## Dire ce qui est un succès

Les modules `command` et `shell` ne savent pas ce que fait ta commande : par défaut, code retour 0 = succès et chaque passage est `changed`. On corrige avec deux mots-clés :

```yaml
- name: Vérifier si l'utilisateur existe en base
  ansible.builtin.command: psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='app'"
  register: role_app
  changed_when: false                 # lire ne change rien
  failed_when: role_app.rc != 0        # explicite : seul un vrai échec de psql compte

- name: Créer l'utilisateur s'il manque
  ansible.builtin.command: createuser app
  when: role_app.stdout != '1'
```

C'est ce qui rend des commandes brutes **idempotentes** : le deuxième passage n'affiche que des `ok` et `skipped`.

## Réessayer jusqu'à ce que ça marche

```yaml
- name: Attendre que l'application réponde
  ansible.builtin.uri:
    url: "http://{{ inventory_hostname }}:8080/health"
    status_code: 200
  register: sante
  until: sante.status == 200
  retries: 20
  delay: 3          # 20 essais, 3 s d'écart : 1 minute maximum
```

Pour attendre simplement qu'un port s'ouvre (après un redémarrage, par exemple), le module `wait_for` est plus simple.

## block, rescue et always

```yaml
- name: Mise à jour du schéma
  block:
    - name: Sauvegarder la base
      ansible.builtin.command: pg_dump -Fc app -f /backup/avant-maj.dump
    - name: Lancer la migration
      ansible.builtin.command: /opt/app/bin/migrate
  rescue:
    - name: Restaurer la sauvegarde
      ansible.builtin.command: pg_restore -c -d app /backup/avant-maj.dump
    - name: Signaler l'échec
      ansible.builtin.fail:
        msg: "Migration échouée sur {{ inventory_hostname }}, base restaurée"
  always:
    - name: Remettre l'application en ligne
      ansible.builtin.service:
        name: app
        state: started
```

Un `block` sert aussi à appliquer un `when`, un `become` ou des `tags` à plusieurs tâches d'un coup.

Attention : si `rescue` réussit, Ansible considère l'erreur comme **traitée** et la machine continue le play. Pour qu'elle reste en échec, termine le `rescue` par un module `fail`, comme ci-dessus.

## Contrôler l'arrêt

| Réglage | Effet |
| --- | --- |
| comportement par défaut | la machine en échec sort du play, les autres continuent |
| `ignore_errors: true` | la tâche échoue mais la machine continue ; à réserver aux cas vraiment sans importance |
| `any_errors_fatal: true` | une seule machine en échec arrête tout le monde |
| `max_fail_percentage: 20` | arrête si plus de 20 % des machines échouent (utile avec `serial`, chapitre 11) |
| `ansible.builtin.assert` | échoue volontairement si une condition n'est pas remplie, pour vérifier les prérequis tôt |

```yaml
- name: Vérifier les prérequis
  ansible.builtin.assert:
    that:
      - ansible_facts['memtotal_mb'] >= 4000
      - app_version is defined
    fail_msg: "Machine trop petite ou version non précisée"
```

> **À retenir.** `when` décide, sans accolades ; `loop` répète avec `item`, mais une liste passée directement au module est plus rapide. `changed_when` et `failed_when` rendent les commandes honnêtes et idempotentes. `block / rescue / always` permet un vrai plan de repli, et `assert` vérifie les prérequis avant de casser quoi que ce soit.
