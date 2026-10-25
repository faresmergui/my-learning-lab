---
title: Synthèse Ansible
description: "Inventaire, modules, playbooks, variables, Jinja2, conditions et erreurs, rôles, Vault, tests, performance et travail en équipe."
---

## Le modèle

- **Sans agent** : SSH + Python sur les machines, Ansible seulement sur le **nœud de contrôle**.
- Décrit un **état**, pas des actions : **idempotence**, un 2ᵉ passage = que des `ok`.
- Statuts : `ok`, `changed`, `failed`, `skipped`. Terraform **crée** (avec un state), Ansible **configure** (sans state).

## Inventaire

```yaml
all:
  children:
    prod:
      children:
        web: { hosts: { web1: { ansible_host: 10.0.1.11 } } }
        db:  { hosts: { db1: } }
```

- Groupes `all` et `ungrouped` toujours présents ; `children` = groupe de groupes.
- Motifs : `web:db` (union), `web:&prod` (intersection), `web:!web3` (exclusion).
- Dynamique : `openstack.cloud.openstack`, `amazon.aws.aws_ec2`, `keyed_groups` sur métadonnées ou tags, cache.
- `ansible-inventory -i inv --graph` / `--host web1`.

## Ad hoc et modules

```bash
ansible web -m ansible.builtin.ping
ansible db -m ansible.builtin.apt -a "name=htop" --become
ansible all -m ansible.builtin.setup -a "filter=*ipv4*"
```

- Toujours un module dédié plutôt que `command` / `shell`, toujours le **FQCN**.
- `command` et `shell` : `changed_when` et `failed_when` pour les rendre honnêtes.

## Playbooks

- Play = `hosts` + tâches, exécutées **tâche par tâche** sur toutes les machines (`linear`).
- **Handlers** : `notify`, seulement si `changed`, une fois en fin de play (`meta: flush_handlers` pour avant).
- Avant la prod : `--check --diff --limit web1` ; aussi `--tags`, `--start-at-task`, `-vvv`.

## Variables et facts

| Du plus faible… | …au plus fort |
| --- | --- |
| `defaults/` du rôle → `group_vars/all` → `group_vars/<groupe>` → `host_vars` | facts → `vars:` du play → `vars/` du rôle → `set_fact` / `register` → **`-e`** |

- Valeurs dans `group_vars` / `host_vars` **par environnement**, une variable à un seul endroit.
- Facts : `ansible_facts['os_family']`, `default_ipv4.address`, `memtotal_mb` ; `gather_facts: false` si inutiles.
- `hostvars[hote]` lit les variables d'une autre machine ; `groups['web']` liste un groupe.

## Jinja2

- `{{ }}` affiche, `{% if %}` / `{% for %}` décide et répète, `{# #}` commente, `|` filtre.
- Filtres : `default`, `join`, `length`, `int`, `bool`, `combine`, `map(attribute=)`, `selectattr`, `to_nice_yaml`, `regex_replace`, `password_hash`.
- `template` + `validate: nginx -t -c %s` + `{{ ansible_managed }}` ; `lookup` lit sur le nœud de contrôle.

## Conditions, boucles, erreurs

```yaml
when: ansible_facts['os_family'] == 'Debian'   # sans accolades
loop: "{{ users }}"                            # item, loop_control.label
until: r.status == 200
retries: 20
delay: 3
```

- Une liste passée au module vaut mieux qu'une `loop`.
- `block` / `rescue` / `always` = try / catch / finally ; finir `rescue` par `fail` pour rester en échec.
- `assert` pour les prérequis ; `any_errors_fatal`, `max_fail_percentage` ; `ignore_errors` en dernier recours.

## Rôles et collections

- Rôle : `tasks/ handlers/ templates/ files/ defaults/ vars/ meta/`, entrées dans `defaults/main.yml` **préfixées**.
- `roles:` / `import_role` statique, `include_role` dynamique (when, loop).
- Collections `namespace.nom` : `ansible.builtin`, `ansible.posix`, `community.general`, `openstack.cloud`, `amazon.aws`, `kubernetes.core`.
- `requirements.yml` avec **versions figées**, `ansible-galaxy install -r`.

## Secrets

```bash
ansible-vault create|edit|view|encrypt|rekey group_vars/prod/vault.yml
ansible-playbook site.yml --vault-id prod@~/.ansible/vault-pass.sh
```

- `main.yml` en clair : `db_password: "{{ vault_db_password }}"` ; `vault.yml` chiffré.
- `no_log: true` sur les tâches sensibles ; mot de passe Vault hors du dépôt (script, trousseau, variable CI masquée).
- Secret poussé en clair = **compromis**, on le change. Gros besoins : HashiCorp Vault, Secrets Manager, Barbican par lookup.

## Tester

- `yamllint` → `--syntax-check` → `ansible-lint` (profil `production`, `# noqa` justifié) → `--check --diff` → **Molecule**.
- Molecule : create → converge → **idempotence** → verify → destroy ; conteneurs systemd ou VM pour les rôles système.

## Performance et grand parc

```ini
[defaults]
forks = 30
gathering = smart
fact_caching = jsonfile
callbacks_enabled = ansible.posix.profile_tasks
[ssh_connection]
pipelining = True
```

- `serial: [1, "20%", "100%"]` + `max_fail_percentage: 0` : canari puis lots, handlers à chaque lot.
- `strategy: free`, `run_once`, `delegate_to`, `async` / `poll`, Mitogen, ansible-pull.

## En équipe

- Prod par **merge request** et CI (job prod `when: manual`), jamais depuis un poste.
- **Execution environment** (ansible-builder, ansible-navigator) : mêmes versions partout.
- **AWX** / Automation Platform : projets, inventaires, identifiants cachés, job templates, workflows, surveys, plannings, droits, historique.
- Terraform crée et pose des métadonnées → inventaire dynamique → Ansible configure → ArgoCD déploie les applis sur Kubernetes. Pas d'Ansible dans `local-exec`.
