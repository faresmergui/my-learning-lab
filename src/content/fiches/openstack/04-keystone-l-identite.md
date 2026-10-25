---
title: 'Keystone : l''identité'
chapter: 4
order: 1
duration: 13
tags:
- OpenStack
- EX210
- Keystone
cards:
- q: Quelle est la hiérarchie des objets Keystone ?
  a: 'Un **domaine** contient des **projets**, des **utilisateurs** et des **groupes**. On donne un **rôle** à un utilisateur ou à un groupe **sur** un projet (ou un domaine, ou le système) : c''est une **affectation de rôle** (role assignment).'
- q: Quels sont les rôles par défaut et leur portée ?
  a: '**reader** (lecture), **member** (créer et gérer les ressources du projet), **manager** (gérer certains aspects du projet, selon les services) et **admin**. Ils s''appliquent sur un projet, un domaine ou le **système** (`--system all`, l''administration du cloud entier).'
- q: Qu'est-ce qu'un jeton scopé ?
  a: 'Un jeton lié à une **portée** : un projet (pour gérer ses ressources), un domaine (pour gérer ses utilisateurs et projets) ou le système (administration globale). Un jeton non scopé ne sert qu''à découvrir ses projets.'
- q: Que sont les clés Fernet et pourquoi les faire tourner ?
  a: Les jetons Keystone sont chiffrés et signés avec des **clés Fernet** stockées sur chaque nœud Keystone (`/etc/keystone/fernet-keys/`). On les fait **tourner** régulièrement (nouvelle clé principale, anciennes gardées pour valider les jetons en cours) ; toutes les instances Keystone doivent avoir les **mêmes** clés.
- q: Comment relier Keystone à un annuaire d'entreprise ?
  a: Par un **domaine** dédié configuré avec le pilote **LDAP** (Active Directory, Red Hat IdM/FreeIPA) dans un fichier `keystone.<domaine>.conf`, ou par **fédération** (SAML, OpenID Connect) avec des règles de correspondance (mapping).
- q: À quoi servent les application credentials ?
  a: À donner à un script ou une CI un accès **limité à un projet et à certains rôles** (et même à certaines API avec des règles d'accès), avec une date d'expiration, sans exposer le mot de passe. Révocables à tout moment.
quiz:
- q: Une nouvelle équipe doit gérer elle-même ses utilisateurs et ses projets, sans voir ceux des autres. Que crées-tu ?
  options:
  - Un projet partagé
  - Un domaine dédié, avec un utilisateur qui a le rôle admin (ou manager) sur ce domaine
  - Un utilisateur admin système
  - Un groupe dans le domaine Default
  answer: 1
  explain: Le domaine est la frontière d'administration ; l'admin de domaine gère ses projets et utilisateurs sans droits sur le reste du cloud.
- q: Après l'ajout d'un troisième nœud Keystone, une requête sur trois échoue avec 401. Cause probable ?
  options:
  - memcached est plein
  - 'Les clés Fernet du nouveau nœud diffèrent : il ne sait pas valider les jetons des autres'
  - Le catalogue est vide
  - Le mot de passe a expiré
  answer: 1
  explain: Les clés doivent être identiques et distribuées ensemble après chaque rotation.
- q: Tu donnes à un utilisateur le rôle member sur un groupe plutôt qu'à lui directement. Avantage ?
  options:
  - Aucun
  - Quand il change d'équipe, on change ses groupes (souvent synchronisés depuis LDAP), sans retoucher les affectations de chaque projet
  - C'est obligatoire
  - Les jetons durent plus longtemps
  answer: 1
  explain: Les affectations par groupe se gèrent beaucoup mieux à l'échelle.
level: intermédiaire
---

**Keystone** est la porte d'entrée de tout OpenStack. Chaque requête porte un **jeton** délivré par Keystone, chaque service lui demande si ce jeton est valide et quels rôles il donne. Il tient aussi le **catalogue** des services. L'examen EX210 lui consacre un domaine entier : domaines, projets, rôles, annuaire d'entreprise, clés de jetons.

> **Les outils cités dans cette fiche.**
> - **domaine** : un espace qui contient projets, utilisateurs et groupes ; la frontière d'administration.
> - **projet** : l'unité qui possède les ressources et les quotas.
> - **rôle** : un ensemble de droits (`reader`, `member`, `manager`, `admin`) donné sur une portée.
> - **jeton** (token) : la preuve d'identité temporaire jointe à chaque appel d'API.
> - **Fernet** : le format des jetons Keystone, chiffrés avec des clés partagées entre les nœuds.
> - **LDAP** : le protocole des annuaires d'entreprise ; **Red Hat IdM** (FreeIPA) et **Active Directory** en sont des exemples.
> - **fédération** : déléguer l'authentification à un fournisseur d'identité externe par **SAML** ou **OpenID Connect**.
> - **oslo.policy** : la bibliothèque qui décide, dans chaque service, quel rôle peut faire quelle action.
> - **hyperviseur** : le logiciel qui fait tourner des machines virtuelles sur un serveur physique (KVM, VMware ESXi).
> - **RBAC** : le contrôle d'accès par rôles : on donne des droits à des rôles, puis des rôles aux personnes ou programmes.
> - **RHOSO** : Red Hat OpenStack Services on OpenShift, la version actuelle d'OpenStack chez Red Hat.

## Comprendre : qui, où, avec quels droits

```
Domaine « shop »
├── Projets : shop-dev, shop-prod
├── Utilisateurs : fares, alice
└── Groupes : devops (fares, alice)

Affectations de rôles :
  groupe devops  → member  sur shop-dev
  groupe devops  → reader  sur shop-prod
  fares          → member  sur shop-prod
  fares          → admin   sur le domaine shop
```

Un rôle n'a de sens **que sur une portée**. Les trois portées :

| Portée | Pour | Exemple |
| --- | --- | --- |
| **projet** | gérer les ressources d'un projet | créer des instances dans `shop-prod` |
| **domaine** | gérer les projets, utilisateurs, groupes d'un domaine | créer un projet pour une nouvelle équipe |
| **système** | administrer le cloud entier | gérer les hyperviseurs, les flavors publiques |

Les politiques récentes (« secure RBAC ») utilisent vraiment ces portées et les rôles **reader**, **member**, **manager**, **admin**. Les anciens déploiements donnaient `admin` sur un projet et cela valait administration globale : c'est un piège de sécurité à connaître.

## Les commandes

```bash
openstack domain create --description "Client Shop" shop
openstack project create --domain shop shop-prod
openstack user create --domain shop --password-prompt --email fares@shop.fr fares
openstack group create --domain shop devops
openstack group add user --group-domain shop --user-domain shop devops fares

openstack role add --group devops --group-domain shop --project shop-prod --project-domain shop member
openstack role add --user fares --user-domain shop --domain shop admin
openstack role add --user ops --system all reader           # lecture sur tout le cloud

openstack role assignment list --user fares --user-domain shop --names
openstack role create support                               # un rôle personnalisé
openstack implied role create member --implied-role reader  # member implique reader
```

Un **rôle personnalisé** (`support`) n'a d'effet que si des **politiques** le mentionnent (fiche « Sécuriser un cloud »).

## Les jetons et les clés Fernet

```bash
openstack token issue
openstack --os-project-name shop-prod token issue     # changer de portée
```

Un jeton Fernet n'est **pas stocké** : il est chiffré et signé avec une clé symétrique, et n'importe quel nœud Keystone qui a les **mêmes clés** peut le valider. Les clés vivent dans `/etc/keystone/fernet-keys/` :

| Fichier | Rôle |
| --- | --- |
| `0` | clé **en attente** (staged), deviendra la prochaine principale |
| le plus grand numéro | clé **principale** : chiffre les nouveaux jetons |
| les autres | clés **secondaires** : valident les jetons encore en cours |

```bash
keystone-manage fernet_rotate --keystone-user keystone --keystone-group keystone
# puis copier le dossier identique sur tous les nœuds Keystone
```

La rotation doit être **régulière** (une clé volée ne sert qu'un temps) et **synchronisée** sur tous les nœuds. Sous RHOSO et Kolla, l'opérateur ou un job planifié s'en charge ; il faut savoir vérifier qu'elle a lieu. Le nombre de clés gardées (`max_active_keys`) doit couvrir la durée de vie des jetons (une heure par défaut, `[token] expiration`).

## L'annuaire d'entreprise

Deux approches :

1. **Un domaine LDAP** : on active `domain_specific_drivers_enabled = true`, puis un fichier par domaine.

```ini
# /etc/keystone/domains/keystone.corp.conf
[identity]
driver = ldap
[ldap]
url = ldaps://idm.corp.shop.fr
user = uid=keystone,cn=users,cn=accounts,dc=corp,dc=shop,dc=fr
password = …
suffix = dc=corp,dc=shop,dc=fr
user_tree_dn = cn=users,cn=accounts,dc=corp,dc=shop,dc=fr
user_objectclass = person
group_tree_dn = cn=groups,cn=accounts,dc=corp,dc=shop,dc=fr
group_objectclass = groupOfNames
use_tls = false
tls_cacertfile = /etc/pki/ca-trust/source/anchors/idm-ca.crt
```

Les utilisateurs et groupes restent dans l'annuaire (en lecture seule) ; on leur donne des rôles dans OpenStack. C'est le cas de l'objectif EX210 « Manage an integrated IdM back-end configuration ».

2. **La fédération** (SAML ou OpenID Connect avec Keycloak, Entra ID…) : l'utilisateur s'authentifie chez le fournisseur d'identité, et des règles de **mapping** transforment ses attributs (groupes) en groupes et projets Keystone.

## Les application credentials

```bash
openstack application credential create --role member --expiration 2027-01-01T00:00:00 \
  --description "CI GitLab shop-prod" ci-shop
openstack application credential list
openstack application credential delete ci-shop
```

Elles sont liées à l'utilisateur et au projet de création, avec au plus ses rôles. Les **règles d'accès** (`--access-rules`) peuvent même limiter à certaines API (par exemple seulement lire des objets Swift).

> **À retenir.** Domaine contient projets, utilisateurs, groupes ; un rôle se donne sur une portée (projet, domaine, système). reader, member, manager, admin ; attention à l'ancien « admin de projet = admin du cloud ». Jetons Fernet validés par des clés partagées qu'il faut faire tourner et synchroniser. Annuaire d'entreprise par un domaine LDAP ou par fédération. Application credentials pour les automates.
