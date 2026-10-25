---
title: Projets, quotas et partage de ressources
chapter: 5
order: 1
duration: 11
tags:
- OpenStack
- EX210
- quotas
cards:
- q: Comment voir et modifier les quotas d'un projet ?
  a: '`openstack quota show --usage <projet>` (limites et consommation) et `openstack quota set --instances 50 --cores 200 --ram 409600 --volumes 100 --gigabytes 5000 --floating-ips 20 <projet>`. Chaque service (Nova, Neutron, Cinder) applique les siens.'
- q: Comment rendre une flavor disponible pour un seul projet ?
  a: La créer **privée** (`--private`) puis `openstack flavor set --project <projet> <flavor>`. Les flavors publiques sont visibles par tous les projets.
- q: Quelles visibilités peut avoir une image Glance ?
  a: '**public** (tout le cloud, réservé aux admins), **private** (le projet propriétaire), **shared** (le propriétaire ajoute des projets **membres**, qui doivent accepter) et **community** (visible par tous sans apparaître dans les listes par défaut).'
- q: Comment partager un réseau avec certains projets seulement ?
  a: 'Avec une règle **RBAC Neutron** : `openstack network rbac create --target-project <projet> --action access_as_shared --type network <réseau>`. `--share` le partage avec **tous** les projets ; `access_as_external` permet à un projet de s''en servir comme réseau externe pour ses routeurs.'
- q: Pourquoi définir des quotas même sur un cloud interne ?
  a: Pour éviter qu'un projet (ou un script en boucle) consomme toute la capacité, pour prévoir la capacité et pour refléter ce que chaque équipe a « acheté ». Sans quota, une erreur de Terraform peut créer des centaines d'instances.
quiz:
- q: Un utilisateur obtient « Quota exceeded for cores » alors qu'il n'a que 3 instances. Que vérifies-tu ?
  options:
  - Le réseau
  - '`openstack quota show --usage` du projet : les vCPU des flavors utilisées dépassent le quota de cores'
  - Les clés Fernet
  - Glance
  answer: 1
  explain: Le quota porte sur la somme des vCPU (et de la RAM), pas seulement sur le nombre d'instances.
- q: L'équipe réseau a créé `transit-net` et deux projets (et seulement eux) doivent y brancher des instances. Que fais-tu ?
  options:
  - '`openstack network set --share`'
  - Une règle RBAC `access_as_shared` par projet cible
  - Copier le réseau dans chaque projet
  - Donner le rôle admin aux deux projets
  answer: 1
  explain: '`--share` ouvrirait le réseau à tout le cloud ; la règle RBAC cible précisément les projets.'
level: intermédiaire
---

Un cloud est **multi-tenant** : chaque équipe a ses projets, ses ressources, ses limites. L'administrateur décide combien chacun peut consommer (quotas) et quelles ressources communes sont partagées (flavors, images, réseaux). L'examen EX210 demande d'organiser des projets pour un client et de gérer des réseaux partagés.

> **Les outils cités dans cette fiche.**
> - **quota** : la limite de ressources d'un projet (instances, vCPU, RAM, volumes, Go, IP flottantes, ports, réseaux…).
> - **flavor** : le gabarit d'une instance (vCPU, RAM, disque, propriétés).
> - **RBAC Neutron** : des règles qui partagent un réseau, un QoS policy ou un security group avec d'autres projets.
> - **unified limits** : le nouveau système de limites centralisé dans Keystone, qui remplace progressivement les quotas de chaque service.
> - **scheduler** : le composant qui décide où placer une charge de travail (sur quel nœud ou quel hôte).
> - **hyperviseur** : le logiciel qui fait tourner des machines virtuelles sur un serveur physique (KVM, VMware ESXi).
> - **GPU** : le processeur graphique, qui fait énormément de calculs en parallèle (IA, rendu).
> - **VLAN** : un réseau local virtuel : plusieurs réseaux isolés sur les mêmes commutateurs.
> - **LDAP** : le protocole des annuaires d'entreprise (Active Directory, FreeIPA).

## Comprendre : isolation et partage

```
Projet shop-prod                Projet shop-dev              Ressources de l'admin
├── instances, volumes          ├── instances               ├── flavors publiques (m1.small…)
├── réseau privé app-net        ├── réseau privé dev-net    ├── flavors privées (gpu.large → shop-prod)
├── routeur → réseau externe    └── …                       ├── images publiques (rocky-9, ubuntu-24.04)
└── quotas : 200 vCPU, 400 Go                               └── réseau externe « public » (IP flottantes)
                                                                réseau provider partagé par RBAC
```

Par défaut, un projet ne voit **rien** des autres. Le partage est toujours **explicite**.

## Les quotas

```bash
openstack quota show --usage shop-prod
openstack quota set --instances 50 --cores 200 --ram 409600 shop-prod          # Nova (RAM en Mo)
openstack quota set --volumes 100 --gigabytes 5000 --snapshots 200 shop-prod   # Cinder
openstack quota set --floating-ips 20 --ports 500 --routers 5 shop-prod        # Neutron
openstack quota set --gigabytes 2000 --volume-type ssd shop-prod               # par type de volume
openstack quota list --compute                                                  # vue d'ensemble
```

| Service | Quotas courants |
| --- | --- |
| Nova | `instances`, `cores`, `ram`, `key-pairs`, `server-groups` |
| Cinder | `volumes`, `gigabytes`, `snapshots`, `backups`, et par type de volume |
| Neutron | `networks`, `subnets`, `ports`, `routers`, `floating-ips`, `secgroups`, `secgroup-rules` |
| Octavia | `loadbalancers`, `listeners`, `pools` |

Les valeurs par défaut des nouveaux projets se règlent avec `openstack quota set --class default` (Nova, Cinder) ou dans la configuration de Neutron. `-1` veut dire illimité.

## Les flavors

```bash
openstack flavor create --vcpus 4 --ram 8192 --disk 40 --public m1.large
openstack flavor create --vcpus 16 --ram 65536 --disk 100 --private gpu.large
openstack flavor set --project shop-prod gpu.large           # accès pour ce projet
openstack flavor set --property hw:cpu_policy=dedicated gpu.large
openstack flavor list --all
```

Les **propriétés** (extra specs) d'une flavor guident le scheduler et l'hyperviseur : CPU dédiés, NUMA, huge pages, agrégats, GPU (fiche « Nova : placement et scheduling »). Une flavor ne se **modifie** pas pour ses valeurs de base : on en crée une nouvelle, et on redimensionne les instances (`server resize`).

## Les images partagées

```bash
openstack image set --visibility shared rocky-9-hardened
openstack image add project rocky-9-hardened shop-dev       # le propriétaire invite
openstack image set --accept rocky-9-hardened               # (dans shop-dev) le membre accepte
openstack image member list rocky-9-hardened
```

| Visibilité | Qui la voit |
| --- | --- |
| `public` | tout le cloud (admin seulement pour la créer) |
| `private` | le projet propriétaire |
| `shared` | le propriétaire et les projets membres qui ont accepté |
| `community` | tout le monde, sans encombrer les listes |

## Les réseaux partagés

```bash
# Partager avec un seul projet
openstack network rbac create --type network --action access_as_shared \
  --target-project shop-dev transit-net
# Permettre à un projet d'utiliser un réseau comme externe (routeur, IP flottantes)
openstack network rbac create --type network --action access_as_external \
  --target-project shop-dev public-2
openstack network rbac list
# Partager avec tous
openstack network set --share transit-net
```

Un réseau **provider** partagé (par exemple un VLAN de l'entreprise) permet aux instances d'avoir directement une IP du réseau physique, sans routeur ni IP flottante.

## Organiser un client

Une procédure type, qui couvre l'objectif EX210 « Create a Red Hat OpenStack Platform domain for a client organization » :

1. créer le **domaine** du client ;
2. créer ses **projets** (dev, prod) dans ce domaine ;
3. créer ou relier ses **utilisateurs** et **groupes** (LDAP si besoin) ;
4. donner les **rôles** (admin de domaine à un responsable, member aux équipes) ;
5. fixer les **quotas** ;
6. ouvrir les **flavors privées**, **images** et **réseaux** partagés nécessaires.

Pour fermer un projet proprement : `openstack project cleanup --project shop-old --dry-run`, puis sans `--dry-run`, avant de supprimer le projet (sinon ses ressources restent orphelines).

> **À retenir.** Un projet est isolé ; tout partage est explicite. `quota show --usage` puis `quota set` par service (vCPU et RAM comptent, pas seulement les instances). Flavors privées + `flavor set --project`. Images `shared` avec invitation acceptée. Réseaux partagés par RBAC `access_as_shared` (ou `access_as_external`) plutôt que `--share` pour tous. `project cleanup` avant de supprimer un projet.
