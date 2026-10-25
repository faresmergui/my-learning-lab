---
title: 'Tester son code Ansible : lint, check et Molecule'
chapter: 10
order: 1
duration: 12
level: intermédiaire
tags:
- ansible-lint
- molecule
- tests
- idempotence
cards:
- q: Que vérifie ansible-lint ?
  a: 'Le code **sans l''exécuter** : syntaxe, FQCN manquants, tâches sans nom, `command` là où un module existe, droits de fichier oubliés, mauvaises pratiques. Il classe ses règles par profil, de `min` à `production`.'
- q: Qu'est-ce que Molecule ?
  a: 'Un outil qui teste un rôle **pour de vrai** : il crée une machine jetable (conteneur ou VM), y applique le rôle, vérifie l''idempotence et le résultat, puis détruit la machine.'
- q: Comment Molecule teste-t-il l'idempotence ?
  a: Il applique le rôle **deux fois**. Au second passage, aucune tâche ne doit être `changed` ; sinon le test échoue et liste les tâches fautives.
- q: Quelles sont les étapes de `molecule test` ?
  a: '`create` (la machine), `converge` (appliquer le rôle), `idempotence` (le réappliquer), `verify` (vérifier le résultat), `destroy` (tout supprimer), avec quelques étapes intermédiaires de nettoyage et de préparation.'
- q: Que fait `ansible-playbook --syntax-check` ?
  a: Il lit le playbook et signale les erreurs de syntaxe YAML ou de structure, **sans** se connecter aux machines. C'est le test le plus rapide.
- q: Quelle est la pyramide des tests Ansible, du plus rapide au plus complet ?
  a: '`yamllint` et `--syntax-check`, puis `ansible-lint`, puis `--check --diff` sur un environnement réel, puis Molecule (rôle appliqué sur une machine jetable), et enfin un déploiement en préproduction.'
quiz:
- q: 'ansible-lint signale `no-changed-when` sur une tâche `command: cat /etc/version`. Que corriger ?'
  options:
  - Remplacer par `shell`
  - Désactiver la règle
  - 'Ajouter `changed_when: false`, car la commande ne fait que lire'
  - Ajouter `ignore_errors`
  answer: 2
  explain: Sans `changed_when`, la tâche serait `changed` à chaque passage, ce qui fausse le récapitulatif et l'idempotence.
- q: Molecule échoue à l'étape `idempotence` sur une tâche `lineinfile`. Que signifie-t-il ?
  options:
  - Cette tâche modifie quelque chose à chaque passage, elle n'est pas idempotente
  - Le test de vérification a échoué
  - Le conteneur n'a pas démarré
  - Le rôle a une erreur de syntaxe
  answer: 0
  explain: 'Souvent une `regexp` qui ne correspond pas à la ligne écrite : Ansible la rajoute à chaque fois.'
- q: Pourquoi `--check` ne suffit-il pas à tester un rôle ?
  options:
  - Il modifie les machines
  - Certaines tâches dépendent du résultat de tâches précédentes qui, en simulation, n'ont rien fait
  - Il est trop lent
  - Il ne fonctionne pas avec les rôles
  answer: 1
  explain: 'Exemple : on ne peut pas démarrer en simulation un service dont le paquet n''est pas encore installé. Le mode check est un aperçu, pas un test.'
- q: Avec Molecule et le pilote Docker, que teste-t-on mal ?
  options:
  - Les handlers
  - Les templates
  - Les variables
  - Les services systemd, le noyau, le pare-feu, qui se comportent différemment dans un conteneur
  answer: 3
  explain: Pour ces cas, on utilise une image prévue pour systemd ou un pilote qui crée de vraies VM (Vagrant, OpenStack).
---

Un playbook se relance sans danger seulement s'il est bien écrit. Le seul moyen d'en être sûr avant la prod, c'est de le tester. Ansible a ses propres outils pour ça, du plus léger (relire le code automatiquement) au plus complet (appliquer un rôle sur une machine jetable et vérifier le résultat). On les enchaîne dans la CI.

> **Les outils cités dans cette fiche.**
> - **yamllint** : vérifie que le YAML est bien formé et uniformément écrit (indentation, guillemets, lignes trop longues).
> - **ansible-lint** : l'analyseur officiel du code Ansible, qui repère erreurs et mauvaises pratiques sans rien exécuter.
> - **Molecule** : l'outil officiel pour tester un rôle sur une machine jetable, de sa création à sa destruction.
> - **pilote** (driver) Molecule : ce qui crée la machine de test : Docker ou Podman (conteneurs), Vagrant, OpenStack ou un cloud (VM).
> - **Testinfra** : une bibliothèque Python qui vérifie l'état d'une machine (paquet installé, port ouvert) ; une alternative aux vérifications écrites en Ansible.
> - **pre-commit** : un outil qui lance des vérifications automatiquement avant chaque commit Git.

## Les tests rapides

```bash
yamllint .
ansible-playbook site.yml --syntax-check
ansible-lint
```

Ces trois commandes ne touchent à aucune machine et tournent en quelques secondes. Elles attrapent l'indentation fausse, le module mal orthographié, la variable mal fermée.

## ansible-lint

ansible-lint applique des **règles** regroupées en **profils** de plus en plus exigeants : `min`, `basic`, `moderate`, `safety`, `shared`, `production`. On choisit son profil dans un fichier `.ansible-lint` :

```yaml
# .ansible-lint
profile: production
exclude_paths:
  - collections/
skip_list:
  - yaml[line-length]
```

Les règles que tu verras le plus :

| Règle | Ce qu'elle reproche | Correction |
| --- | --- | --- |
| `fqcn` | `copy` au lieu de `ansible.builtin.copy` | écrire le nom complet |
| `name[missing]` | une tâche sans `name` | lui donner un nom clair |
| `no-changed-when` | `command` toujours `changed` | `changed_when` adapté |
| `command-instead-of-module` | `command: systemctl restart` | utiliser le module `service` |
| `risky-file-permissions` | fichier créé sans `mode` | préciser `mode: "0644"` |
| `var-naming` | variable de rôle sans préfixe | `nginx_port`, pas `port` |
| `no-free-form` | `command: echo a` en ligne | arguments en dictionnaire |

Une ligne précise peut être exemptée avec un commentaire `# noqa: nom-de-la-règle`, à justifier. Mieux vaut quelques exceptions argumentées qu'une règle désactivée partout.

`ansible-lint --fix` corrige seul une partie des problèmes (FQCN, formatage YAML). Relis le diff avant de commiter.

## Le mode check en conditions réelles

`ansible-playbook site.yml --check --diff --limit staging` joue le playbook en simulation sur de vraies machines. C'est un excellent **aperçu** avant une mise en production, mais pas un test complet : une tâche qui dépend d'une précédente (démarrer un service dont le paquet n'est pas encore installé) peut échouer ou mentir en simulation.

Deux réglages aident :

- `check_mode: false` sur une tâche de lecture pour qu'elle s'exécute vraiment même en `--check` (lire une version, par exemple) ;
- `when: not ansible_check_mode` pour sauter une tâche impossible à simuler.

## Molecule

Molecule crée une machine, y applique le rôle, vérifie, puis la détruit. Dans le dossier du rôle :

```
roles/nginx/molecule/default/
├── molecule.yml     # quelle machine créer, avec quel pilote
├── converge.yml     # le playbook qui applique le rôle
└── verify.yml       # les vérifications
```

```yaml
# molecule.yml
driver:
  name: docker
platforms:
  - name: debian12
    image: geerlingguy/docker-debian12-ansible   # image prévue pour systemd
    privileged: true
    command: /lib/systemd/systemd
  - name: rocky9
    image: geerlingguy/docker-rockylinux9-ansible
    privileged: true
    command: /usr/sbin/init
```

```yaml
# verify.yml
- name: Vérifier
  hosts: all
  tasks:
    - name: nginx répond
      ansible.builtin.uri:
        url: http://localhost:80
        status_code: 200
```

| Commande | Usage |
| --- | --- |
| `molecule test` | tout le cycle, de la création à la destruction (en CI) |
| `molecule converge` | crée la machine si besoin et applique le rôle (pendant le développement) |
| `molecule login -h debian12` | ouvre un shell dans la machine pour regarder |
| `molecule verify` | relance seulement les vérifications |
| `molecule destroy` | supprime les machines |

Le test d'**idempotence** est le plus précieux : Molecule applique le rôle une deuxième fois et échoue si une tâche affiche encore `changed`. C'est la preuve que ton rôle peut tourner tous les jours sans effet de bord.

Les conteneurs sont rapides mais ne sont pas de vraies machines : systemd, le noyau, le pare-feu ou les montages s'y comportent autrement. Pour ces rôles, un pilote qui crée de vraies VM, par exemple sur ton OpenStack, donne un test plus fidèle.

<!-- schema:etapes -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Du test le plus rapide au plus complet" style="--minw:560px"><defs><marker id="g4-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g4-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g4-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g4-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="24" width="150" height="62" rx="9"/></g><text x="89.0" y="52.0" class="dg-t" text-anchor="middle" style="--d:0">yamllint</text><text x="89.0" y="70.0" class="dg-s" text-anchor="middle" style="--d:0">--syntax-check</text><g class="dg-box dg-pop" style="--d:1"><rect x="182" y="24" width="150" height="62" rx="9"/></g><text x="257.0" y="52.0" class="dg-t" text-anchor="middle" style="--d:1">ansible-lint</text><text x="257.0" y="70.0" class="dg-s" text-anchor="middle" style="--d:1">profil production</text><path d="M166 55 L180 55" class="dg-l c" marker-end="url(#g4-c)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="350" y="24" width="150" height="62" rx="9"/></g><text x="425.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:2">--check --diff</text><text x="425.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="425.0" dy="0">sur un vrai</tspan><tspan x="425.0" dy="14">environnement</tspan></text><path d="M334 55 L348 55" class="dg-l c" marker-end="url(#g4-c)"/><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="518" y="24" width="150" height="62" rx="9"/></g><text x="593.0" y="52.0" class="dg-t" text-anchor="middle" style="--d:3">Molecule</text><text x="593.0" y="70.0" class="dg-s" text-anchor="middle" style="--d:3">machine jetable</text><path d="M502 55 L516 55" class="dg-l c" marker-end="url(#g4-c)"/><path d="M14 110 L664 110" class="dg-l dash" marker-end="url(#g4-n)"/><text x="14" y="128" class="dg-s" text-anchor="start">quelques secondes</text><text x="664" y="128" class="dg-s" text-anchor="end">plusieurs minutes, mais teste vraiment</text><text x="14" y="166" class="dg-zl" text-anchor="start">molecule test enchaîne</text><g class="dg-box dg-ghost dg-pop" style="--d:4"><rect x="14" y="178" width="118" height="40" rx="9"/></g><text x="73.0" y="203.0" class="dg-t" text-anchor="middle" style="--d:4">create</text><g class="dg-box dg-ghost dg-pop" style="--d:5"><rect x="146" y="178" width="118" height="40" rx="9"/></g><text x="205.0" y="203.0" class="dg-t" text-anchor="middle" style="--d:5">converge</text><path d="M134 198 L144 198" class="dg-l" marker-end="url(#g4-n)"/><g class="dg-box dg-a dg-pop" style="--d:6"><rect x="278" y="178" width="118" height="40" rx="9"/></g><text x="337.0" y="203.0" class="dg-t" text-anchor="middle" style="--d:6">idempotence</text><path d="M266 198 L276 198" class="dg-l" marker-end="url(#g4-n)"/><g class="dg-box dg-ghost dg-pop" style="--d:7"><rect x="410" y="178" width="118" height="40" rx="9"/></g><text x="469.0" y="203.0" class="dg-t" text-anchor="middle" style="--d:7">verify</text><path d="M398 198 L408 198" class="dg-l" marker-end="url(#g4-n)"/><g class="dg-box dg-ghost dg-pop" style="--d:8"><rect x="542" y="178" width="118" height="40" rx="9"/></g><text x="601.0" y="203.0" class="dg-t" text-anchor="middle" style="--d:8">destroy</text><path d="M530 198 L540 198" class="dg-l" marker-end="url(#g4-n)"/><text x="340" y="240" class="dg-s" text-anchor="middle" style="--d:9">idempotence : un deuxième passage ne doit rien changer</text></svg><figcaption>On lance les plus rapides à chaque commit, Molecule en CI à chaque merge request.</figcaption></figure>
<!-- /schema:etapes -->

## Tout enchaîner

Les tests rapides se lancent avant chaque commit avec pre-commit, et l'ensemble en CI à chaque merge request :

```yaml
# .gitlab-ci.yml (extrait)
lint:
  image: python:3.12
  script:
    - pip install ansible-core ansible-lint yamllint
    - yamllint .
    - ansible-lint

molecule:              # demande un runner qui a accès à Docker
  script:
    - pip install molecule molecule-plugins[docker]
    - cd roles/nginx && molecule test
```

> **À retenir.** Du plus rapide au plus complet : `yamllint` et `--syntax-check`, `ansible-lint` (profil `production`), `--check --diff` sur un environnement réel, puis Molecule qui applique le rôle sur une machine jetable et vérifie son idempotence. Un rôle qui passe Molecule deux fois sans `changed` peut tourner en prod sans crainte.
