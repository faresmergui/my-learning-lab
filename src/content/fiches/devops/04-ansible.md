---
title: 'Ansible : automatiser la configuration (résumé)'
chapter: 4
order: 1
duration: 4
level: intermédiaire
tags:
- ansible
cards:
- q: Que veut dire qu'une tâche Ansible est **idempotente** ?
  a: 'La lancer une ou dix fois donne le même résultat : si l''état voulu est déjà là, elle ne change rien et affiche `ok` au lieu de `changed`.'
- q: Pourquoi éviter `command` ou `shell` quand un module existe ?
  a: 'Ces modules ne sont **pas idempotents** par défaut : ils relancent la commande à chaque fois et marquent `changed`. Un module dédié (`apt`, `copy`, `user`) vérifie l''état d''abord.'
- q: Qu'est-ce qu'un handler ?
  a: 'Une tâche déclenchée par `notify`, exécutée **une seule fois, à la fin du play**, et seulement si une tâche a changé quelque chose. Typiquement : redémarrer un service.'
- q: Comment tester un playbook sans rien modifier ?
  a: '`ansible-playbook site.yml --check --diff` : simulation, avec le détail des changements prévus.'
- q: Comment chiffrer un fichier de secrets ?
  a: Avec `ansible-vault encrypt group_vars/prod/vault.yml`, puis `--ask-vault-pass` ou `--vault-password-file` au lancement.
- q: Quelle variable gagne en cas de conflit ?
  a: Les **extra vars** (`-e`) ont toujours la priorité la plus haute. Les `defaults` d'un rôle ont la plus basse.
- q: À quoi sert `serial` dans un play ?
  a: 'À faire un **déploiement progressif** : `serial: 2` traite les hôtes deux par deux, pour ne jamais couper tout le parc en même temps.'
- q: Pourquoi éviter `command` et `shell` dans Ansible ?
  a: Ils s'exécutent **à chaque fois** et cassent l'idempotence. Sinon, ajouter `creates:` ou `changed_when:`.
- q: Quand un handler s'exécute-t-il ?
  a: Seulement si une tâche qui le notifie est **changed**, et **une seule fois** à la fin du play.
- q: Où mettre les valeurs par défaut d'un rôle ?
  a: Dans `roles/x/defaults/main.yml`, la priorité la plus basse, facile à surcharger.
quiz:
- q: 'Ta tâche `shell: echo ''x'' >> /etc/conf` ajoute une ligne à chaque exécution. Quel module utiliser ?'
  options:
  - '`command`'
  - '`lineinfile`'
  - '`raw`'
  - '`script`'
  answer: 1
  explain: '`lineinfile` vérifie si la ligne existe déjà et ne l''ajoute qu''une fois : c''est idempotent.'
- q: Tu modifies trois fichiers de config Nginx dans un play. Combien de fois le handler `restart nginx` est-il exécuté ?
  options:
  - Trois fois
  - Une fois, à la fin du play
  - Zéro fois
  - Une fois après chaque tâche
  answer: 1
  explain: 'Un handler notifié plusieurs fois ne s''exécute qu''une seule fois, à la fin du play. Utilise `meta: flush_handlers` pour le forcer plus tôt.'
---

**Ansible** est un outil de **gestion de configuration** : au lieu de te connecter à dix serveurs pour installer les mêmes paquets et copier les mêmes fichiers, tu décris une fois l'état voulu en YAML, et Ansible l'applique partout en SSH. Il a désormais **son propre module de 12 chapitres** : cette fiche n'en garde que l'essentiel, pour situer Ansible dans la boîte à outils DevOps.

> **Les termes et outils cités dans cette fiche.**
> - **Ansible** : l'outil d'automatisation open source de Red Hat, écrit en Python, qui configure des machines à partir de fichiers YAML.
> - **SSH** : le protocole de connexion à distance qu'Ansible utilise pour parler aux serveurs.
> - **Terraform** : l'outil qui crée l'infrastructure (réseaux, VM, DNS) et en garde la trace dans un state.
> - **CI** : l'intégration continue, qui construit, teste et applique automatiquement chaque modification de code.
> - **ArgoCD** : un outil GitOps qui synchronise en continu un cluster Kubernetes avec un dépôt Git.

## L'essentiel en une minute

| Notion | En une phrase | Chapitre du module |
| --- | --- | --- |
| Sans agent, idempotent | SSH + Python sur les machines ; un 2ᵉ passage ne change rien | [1. Comprendre Ansible](../../ansible/01-comprendre-ansible/) |
| Inventaire | la liste des machines en groupes, statique ou dynamique (OpenStack, AWS) | [2. L'inventaire](../../ansible/02-l-inventaire/) |
| Modules | une action précise et vérifiée ; éviter `command` et `shell` | [3. Ad hoc et modules](../../ansible/03-ad-hoc-et-modules/) |
| Playbooks et handlers | des tâches dans l'ordre, un redémarrage seulement si quelque chose a changé | [4. Les playbooks](../../ansible/04-les-playbooks/) |
| Variables | `group_vars` par environnement, `-e` gagne toujours | [5. Variables et facts](../../ansible/05-variables-et-facts/) |
| Templates | des fichiers de configuration générés par machine avec Jinja2 | [6. Templates Jinja2](../../ansible/06-templates-jinja2/) |
| Conditions et erreurs | `when`, `loop`, `block / rescue` | [7. Conditions, boucles, erreurs](../../ansible/07-conditions-boucles-erreurs/) |
| Rôles | des briques réutilisables, des collections versionnées | [8. Rôles et collections](../../ansible/08-roles-et-collections/) |
| Secrets | Ansible Vault, `no_log`, un vrai coffre pour les gros besoins | [9. Ansible Vault](../../ansible/09-secrets-ansible-vault/) |
| Tests | ansible-lint et Molecule, qui prouve l'idempotence | [10. Tester](../../ansible/10-tester-son-code-ansible/) |
| Grand parc | `forks`, pipelining, `serial` pour déployer par lots | [11. Performance](../../ansible/11-performance-et-grandes-infras/) |
| En équipe | CI, AWX, execution environments | [12. Ansible en équipe](../../ansible/12-ansible-en-equipe/) |

## Sa place dans la chaîne DevOps

**Terraform crée** les machines, **Ansible les configure**, **ArgoCD déploie** les applications sur Kubernetes. Ansible tourne idéalement dans la CI, après une merge request relue, avec `--check --diff` comme aperçu avant la prod. Le chapitre 12 du module détaille ce partage des rôles.

> **À retenir.** Ansible décrit un état voulu et l'applique en SSH, sans agent ; l'idempotence est son principe central. Pour tout le reste, va au [module Ansible](../../ansible/) et à sa [synthèse](../../ansible/synthese/).
