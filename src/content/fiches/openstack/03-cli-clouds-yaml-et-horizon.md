---
title: La CLI, clouds.yaml et Horizon
chapter: 3
order: 1
duration: 10
tags:
- OpenStack
- EX210
- CLI
cards:
- q: Comment indiquer à la CLI à quel cloud se connecter ?
  a: Avec un fichier **`clouds.yaml`** (dans `~/.config/openstack/` ou le dossier courant) et `--os-cloud <nom>` ou la variable `OS_CLOUD`. L'ancienne méthode est un fichier **openrc** qui exporte des variables `OS_*`.
- q: Comment obtenir des sorties exploitables par un script ?
  a: '`-f value -c <colonne>` (valeur brute), `-f json` ou `-f yaml`, et `-c` pour choisir les colonnes : `openstack server show web1 -f value -c status`.'
- q: Comment voir les appels HTTP faits par la CLI ?
  a: '`--debug` : la CLI affiche chaque requête (URL, en-têtes) et réponse, dont le **request-id** à chercher dans les logs des services.'
- q: Où mettre le mot de passe pour ne pas l'écrire dans `clouds.yaml` ?
  a: 'Dans un fichier séparé **`secure.yaml`** (même structure, fusionné avec clouds.yaml), ou mieux : utiliser des **application credentials** (identifiant et secret dédiés, révocables, limités à un projet et à des rôles).'
- q: Comment vérifier rapidement qui on est et sur quel projet ?
  a: '`openstack token issue` (jeton, projet, expiration) et `openstack catalog list` (services et endpoints visibles). `openstack versions show` affiche les versions d''API.'
quiz:
- q: Un script doit récupérer seulement l'ID d'un réseau nommé `prod-net`. Quelle commande ?
  options:
  - '`openstack network list`'
  - '`openstack network show prod-net -f value -c id`'
  - '`openstack network show prod-net --debug`'
  - '`neutron net-show prod-net`'
  answer: 1
  explain: '`-f value -c id` donne la valeur seule, sans tableau à découper.'
- q: Tu gères trois clouds (dev, préprod, prod). Méthode la plus sûre pour ne pas te tromper ?
  options:
  - Un seul openrc que tu modifies
  - Trois entrées dans clouds.yaml et `--os-cloud` explicite (ou un prompt qui affiche OS_CLOUD)
  - Copier les variables à la main
  - Utiliser seulement Horizon
  answer: 1
  explain: Un nom de cloud explicite dans chaque commande ou visible dans le prompt évite de lancer une suppression sur la prod par erreur.
level: intermédiaire
---

On peut tout faire dans **Horizon**, l'interface web, mais l'exploitation au quotidien, l'automatisation et l'examen EX210 se font en **ligne de commande**. Le client unifié `openstack` remplace les anciens clients par service (`nova`, `neutron`, `cinder`), même si on les croise encore dans de vieilles procédures.

> **Les outils cités dans cette fiche.**
> - **python-openstackclient** : la commande `openstack`, qui parle à toutes les API.
> - **clouds.yaml** : le fichier de configuration qui décrit un ou plusieurs clouds (URL de Keystone, région, identifiants).
> - **openrc** : un script shell qui exporte des variables `OS_*` ; l'ancienne méthode, encore générée par Horizon.
> - **application credential** : un couple identifiant/secret créé par un utilisateur pour un projet, avec des rôles limités, révocable sans toucher au mot de passe.
> - **Horizon** : le tableau de bord web d'OpenStack.
> - **openstacksdk** : la bibliothèque Python sur laquelle reposent la CLI, Ansible et beaucoup d'outils.
> - **RHOSO** : Red Hat OpenStack Services on OpenShift, la version actuelle d'OpenStack chez Red Hat.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **load balancer** : un répartiteur de charge qui distribue les requêtes entre plusieurs serveurs.
> - **hyperviseur** : le logiciel qui fait tourner des machines virtuelles sur un serveur physique (KVM, VMware ESXi).
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.

## Configurer l'accès

```yaml
# ~/.config/openstack/clouds.yaml
clouds:
  prod:
    auth:
      auth_url: https://keystone.cloud.shop.fr:5000/v3
      username: fares
      project_name: shop-prod
      user_domain_name: Default
      project_domain_name: Default
    region_name: regionOne
    interface: public
    identity_api_version: 3
  ci:
    auth_type: v3applicationcredential
    auth:
      auth_url: https://keystone.cloud.shop.fr:5000/v3
      application_credential_id: "1c2e…"
      application_credential_secret: "…"
```

```bash
export OS_CLOUD=prod            # ou --os-cloud prod à chaque commande
openstack token issue           # qui suis-je, sur quel projet, jusqu'à quand
openstack catalog list          # services et endpoints
```

Le mot de passe va dans `secure.yaml` (même structure) ou est demandé à chaque fois ; les automates utilisent des **application credentials**. Sous RHOSO, les administrateurs travaillent souvent depuis le pod `openstackclient` : `oc rsh -n openstack openstackclient`.

## La grammaire de la CLI

```
openstack <objet> <action> [options] [nom ou ID]
            │        └── list, show, create, set, unset, delete, add, remove
            └── server, flavor, image, network, subnet, port, router, floating ip,
                volume, security group, project, user, role, quota, stack, loadbalancer…
```

```bash
openstack server list --long
openstack server show web1
openstack server create --flavor m1.small --image rocky-9 --network app-net \
  --key-name fares --security-group web web1
openstack server set --property role=web web1
openstack server delete web1
```

Les noms ne sont pas forcément **uniques** : en cas de doublon, la CLI refuse et demande l'ID. Dans les scripts, on travaille par ID.

## Des sorties utilisables

```bash
openstack server list -f json | jq -r '.[] | select(.Status=="ERROR") | .ID'
openstack server show web1 -f value -c status
openstack flavor list -c Name -c VCPUs -c RAM
openstack server list --all-projects --host compute-07     # (admin) instances d'un hôte
openstack server list --status ERROR --all-projects
```

| Option | Effet |
| --- | --- |
| `-f table/json/yaml/value/csv` | format |
| `-c <colonne>` | ne garder que certaines colonnes |
| `--long` | plus de colonnes |
| `--all-projects` | (admin) tous les projets |
| `--debug` | requêtes HTTP détaillées, avec le request-id |
| `--os-compute-api-version 2.95` | une micro-version d'API plus récente, pour des fonctions récentes |

## Déboguer un appel

```bash
openstack --debug server show web1 2>&1 | grep -iE "REQ:|RESP:|x-openstack-request-id"
```

Chaque réponse porte un **`x-openstack-request-id`** (`req-…`). C'est le fil qui relie l'action de l'utilisateur aux lignes de logs des services : on le cherche dans les logs de nova-api, conductor, compute (fiche « Déboguer OpenStack »).

## Horizon

Horizon reprend l'essentiel : instances, volumes, réseaux avec une **topologie** graphique, piles Heat, load balancers, et l'administration (projets, utilisateurs, flavors, hyperviseurs). Il est pratique pour :

- **voir** la topologie réseau d'un projet ;
- ouvrir la **console** d'une instance (noVNC) quand SSH ne répond pas ;
- télécharger un fichier **openrc** ou **clouds.yaml** prêt à l'emploi.

Pour tout ce qui doit être reproductible, on reste sur la CLI, Terraform ou Ansible.

> **À retenir.** `clouds.yaml` + `OS_CLOUD` (ou `--os-cloud`), mots de passe dans `secure.yaml`, application credentials pour les automates. `openstack <objet> <action>` ; `-f value -c` ou `-f json` dans les scripts ; IDs plutôt que noms. `--debug` montre les requêtes et le request-id à chercher dans les logs. Horizon pour la topologie et la console.
