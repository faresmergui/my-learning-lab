---
title: Les secrets avec Ansible Vault
chapter: 9
order: 1
duration: 12
level: intermédiaire
tags:
- vault
- secrets
- no_log
cards:
- q: Qu'est-ce qu'Ansible Vault ?
  a: La fonction intégrée à Ansible qui **chiffre** des fichiers ou des valeurs avec un mot de passe (AES-256). Le fichier chiffré peut aller dans Git ; Ansible le déchiffre en mémoire au moment de l'exécution.
- q: Quelle convention pour ranger des variables chiffrées ?
  a: 'Un fichier `vault.yml` chiffré contient `vault_db_password`, et le fichier en clair `main.yml` à côté contient `db_password: "{{ vault_db_password }}"`. On voit quelles variables existent sans déchiffrer.'
- q: Comment fournir le mot de passe Vault sans le taper ?
  a: Avec `--vault-password-file` qui pointe vers un fichier protégé ou vers un **script** qui va chercher le mot de passe ailleurs (trousseau macOS, coffre d'entreprise, variable de CI).
- q: 'À quoi sert `no_log: true` ?'
  a: À **masquer** les arguments et le résultat d'une tâche dans la sortie et les logs. Sans lui, un mot de passe passé à un module peut apparaître en clair avec `-v`.
- q: Qu'est-ce qu'un vault ID ?
  a: Une étiquette qui associe un mot de passe à un usage (`dev`, `prod`). On peut chiffrer avec des mots de passe différents par environnement et les fournir tous au lancement.
- q: Quelle limite principale d'Ansible Vault ?
  a: 'Un seul mot de passe partagé déchiffre tout : pas de droits fins, pas de trace de qui a lu quoi, et changer le mot de passe oblige à rechiffrer (`ansible-vault rekey`). D''où l''intérêt d''un vrai coffre pour les gros besoins.'
quiz:
- q: Un collègue a commité `group_vars/prod/vault.yml` en clair par erreur et l'a poussé. Quelle est la bonne réaction ?
  options:
  - Considérer les secrets comme compromis, les changer, puis chiffrer
  - Supprimer le fichier du dépôt
  - Rien, le dépôt est privé
  - Chiffrer le fichier et refaire un commit
  answer: 0
  explain: 'L''historique Git garde l''ancienne version. Chiffrer après coup ne protège pas ce qui a déjà été publié : il faut faire tourner les secrets.'
- q: Tu veux voir quelles variables existent dans les group_vars de prod sans avoir le mot de passe Vault. Quelle organisation le permet ?
  options:
  - Utiliser des extra vars
  - Tout chiffrer dans un seul fichier
  - Mettre les secrets dans le playbook
  - Fichier en clair qui référence `vault_*`, et valeurs dans un vault.yml chiffré
  answer: 3
  explain: Le fichier en clair sert de sommaire ; seul le contenu sensible est chiffré.
- q: Une tâche `user` reçoit un mot de passe. Que faut-il ajouter pour qu'il n'apparaisse jamais dans la sortie, même en -vvv ?
  options:
  - '`--check`'
  - '`changed_when: false`'
  - '`no_log: true`'
  - '`become: true`'
  answer: 2
  explain: '`no_log` remplace les détails de la tâche par un message de censure.'
- q: Ton équipe a déjà HashiCorp Vault. Comment Ansible peut-il y lire un secret ?
  options:
  - Avec ansible-vault decrypt
  - Avec un lookup de la collection `community.hashi_vault`
  - En copiant le secret dans group_vars
  - Il ne peut pas
  answer: 1
  explain: Le lookup interroge le coffre à l'exécution ; le secret ne passe jamais par le dépôt Git.
---

Un playbook a besoin de secrets : mots de passe de bases, clés d'API, certificats. Les écrire en clair dans `group_vars` et les pousser sur Git, c'est les donner à tous ceux qui ont accès au dépôt, pour toujours, car Git garde l'historique. **Ansible Vault** chiffre ces secrets pour qu'ils puissent vivre dans le dépôt sans être lisibles. Pour des besoins plus larges, Ansible sait aussi lire dans un vrai coffre-fort de secrets.

> **Les outils cités dans cette fiche.**
> - **Ansible Vault** : la fonction de chiffrement intégrée à Ansible, pilotée par la commande `ansible-vault`. Rien à voir avec HashiCorp Vault malgré le nom.
> - **AES-256** : un algorithme de chiffrement symétrique standard : la même clé chiffre et déchiffre.
> - **HashiCorp Vault** : un serveur de gestion de secrets (droits par équipe, journal d'accès, secrets temporaires). **OpenBao** est sa variante open source.
> - **AWS Secrets Manager**, **Barbican** : les services de secrets d'AWS et d'OpenStack.
> - **lookup** : une fonction qui va chercher une donnée à l'exécution, ici un secret dans un coffre (vu au chapitre 6).
> - **no_log** : une option de tâche qui cache ses arguments et son résultat dans la sortie.

## Les commandes

```bash
ansible-vault create group_vars/prod/vault.yml   # créer un fichier chiffré
ansible-vault edit   group_vars/prod/vault.yml   # le modifier (ouvre $EDITOR)
ansible-vault view   group_vars/prod/vault.yml   # le lire
ansible-vault encrypt fichier.yml                # chiffrer un fichier existant
ansible-vault decrypt fichier.yml                # le remettre en clair (à éviter)
ansible-vault rekey  fichier.yml                 # changer le mot de passe
```

Un fichier chiffré ressemble à ceci, ce qui ne dit rien de son contenu :

```
$ANSIBLE_VAULT;1.1;AES256
6638643965326334316162356164386135303139373038636631373737376461...
```

Au lancement, il faut fournir le mot de passe :

```bash
ansible-playbook site.yml --ask-vault-pass                # le taper
ansible-playbook site.yml --vault-password-file ~/.vault_pass  # le lire dans un fichier
```

## Ranger les secrets proprement

La convention la plus répandue sépare le **nom** des variables de leur **valeur** :

```yaml
# group_vars/prod/main.yml  (en clair)
db_user: app
db_password: "{{ vault_db_password }}"
api_token: "{{ vault_api_token }}"
```

```yaml
# group_vars/prod/vault.yml  (chiffré)
vault_db_password: "Xk2...q9"
vault_api_token: "ghp_..."
```

Grâce au préfixe `vault_`, un `grep db_password` trouve tout de suite d'où vient la valeur, et les relectures de code se font sans déchiffrer.

On peut aussi chiffrer **une seule valeur** dans un fichier en clair :

```bash
ansible-vault encrypt_string 'Xk2...q9' --name 'vault_db_password'
```

C'est pratique pour un ou deux secrets, mais les fichiers entiers se relisent et se modifient plus facilement.

## Un mot de passe par environnement

Avec les **vault IDs**, dev et prod n'ont pas le même mot de passe : un développeur peut déchiffrer dev sans pouvoir lire la prod.

```bash
ansible-vault create --vault-id prod@prompt group_vars/prod/vault.yml
ansible-playbook site.yml --vault-id dev@~/.vault_dev --vault-id prod@prompt
```

## Ne pas laisser fuiter le secret ailleurs

Chiffrer le fichier ne suffit pas : le secret peut réapparaître en clair à l'exécution.

- **Dans la sortie** : avec `-v`, Ansible affiche les arguments des modules. Ajoute `no_log: true` sur les tâches qui manipulent un secret.
- **Sur le disque des serveurs** : un template qui écrit un mot de passe doit avoir des droits stricts (`mode: "0600"`, bon propriétaire).
- **Dans le dépôt** : ajoute le fichier de mot de passe Vault au `.gitignore`, et un outil de détection de secrets en CI (comme **gitleaks**, qui cherche des motifs de clés dans les commits).
- **Dans les messages d'erreur** : `debug: var=` sur un secret l'affiche en clair, même en mode normal.

```yaml
- name: Créer l'utilisateur de la base
  community.postgresql.postgresql_user:
    name: "{{ db_user }}"
    password: "{{ db_password }}"
  no_log: true
```

`no_log` rend aussi le débogage plus dur, puisqu'on ne voit plus le détail d'un échec. Une astuce : `no_log: "{{ not (debug_secrets | default(false)) }}"`, à activer ponctuellement sur un environnement de test.

## Le mot de passe Vault lui-même

C'est le secret qui protège tous les autres. Ne le laisse pas dans un fichier en clair sur ton disque si tu peux l'éviter : `--vault-password-file` accepte un **script exécutable**, qui imprime le mot de passe.

```bash
#!/bin/sh
# ~/.ansible/vault-pass.sh : lit le mot de passe dans le trousseau macOS
security find-generic-password -a ansible -s vault-prod -w
```

En CI, le mot de passe est une variable protégée et masquée du pipeline, écrite dans un fichier temporaire le temps du job.

## Quand passer à un vrai coffre

Ansible Vault est simple et suffit pour une petite équipe. Ses limites apparaissent avec la taille : un mot de passe partagé, pas de droits par équipe, pas de journal de qui a lu quoi, et une rotation manuelle. Un coffre dédié règle ces points, et Ansible le lit avec un lookup :

```yaml
db_password: "{{ lookup('community.hashi_vault.vault_kv2_get', 'apps/facturation').secret.password }}"
```

| | Ansible Vault | Coffre dédié (HashiCorp Vault, Secrets Manager, Barbican) |
| --- | --- | --- |
| Où vit le secret | dans Git, chiffré | dans le coffre, jamais dans Git |
| Droits | un mot de passe pour tout | par équipe, par application |
| Audit | aucun | journal de chaque lecture |
| Rotation | `rekey` et rechiffrement à la main | automatisable, secrets temporaires possibles |
| Mise en place | immédiate | un service à installer et à maintenir |

Une combinaison fréquente : le coffre détient les secrets, et Ansible Vault ne protège plus que le jeton d'accès au coffre.

> **À retenir.** Ansible Vault chiffre les secrets pour qu'ils puissent vivre dans Git. Range-les dans un `vault.yml` chiffré, référencés par des `vault_*` dans un fichier en clair. `no_log: true` sur les tâches sensibles, le mot de passe Vault hors du dépôt. Un secret poussé en clair est compromis : on le change. Pour des droits fins et un audit, un vrai coffre lu par lookup.
