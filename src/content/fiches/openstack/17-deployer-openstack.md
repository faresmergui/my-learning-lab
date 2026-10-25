---
title: Déployer OpenStack
chapter: 17
order: 1
duration: 15
tags:
- OpenStack
- EX210
- Déploiement
- RHOSO
cards:
- q: Quels sont les principaux outils de déploiement d'OpenStack ?
  a: '**Kolla-Ansible** (services en conteneurs Docker/Podman déployés par Ansible, très répandu), **OpenStack-Ansible** (conteneurs LXC ou hôtes), **RHOSO** de Red Hat (control plane sur OpenShift par des opérateurs, data plane sur RHEL par Ansible), **Canonical OpenStack/Sunbeam** (snaps et Juju), **TripleO** (ancien outil Red Hat, abandonné) et **DevStack** (pour développer et tester seulement).'
- q: Comment est organisé Red Hat OpenStack Services on OpenShift (RHOSO) ?
  a: Le **control plane** (API, schedulers, bases Galera, RabbitMQ, OVN northd) tourne en **pods** sur un cluster OpenShift, géré par l'opérateur `openstack-operator` via une ressource `OpenStackControlPlane`. Le **data plane** (computes, nœuds réseau, Ceph HCI) reste sur des nœuds **RHEL** configurés par Ansible via `OpenStackDataPlaneNodeSet` et `OpenStackDataPlaneDeployment`.
- q: Que désignaient undercloud et overcloud dans TripleO ?
  a: L'**undercloud** était un mini-OpenStack d'installation (Ironic, Heat) qui déployait l'**overcloud**, le vrai cloud des utilisateurs. RHOSP 17.1 était la dernière version de ce modèle ; RHOSO 18 l'a remplacé par OpenShift et des opérateurs.
- q: Qu'est-ce que la cadence SLURP ?
  a: 'OpenStack sort deux versions par an (nommées `2025.1`, `2025.2`…). Une version sur deux est **SLURP** (Skip Level Upgrade Release Process, les `.1`) : on peut passer directement d''une SLURP à la suivante en sautant la version intermédiaire.'
- q: Quel est l'ordre général d'une mise à jour de version ?
  a: 'Lire les notes de version, sauvegarder les bases et la configuration, tester en préproduction, puis : mettre à jour le **control plane** service par service (migrations de base, `nova-manage db online_data_migrations`), ensuite les **computes** par lots (en migrant les VM si besoin), et enfin vérifier (`nova-status upgrade check`, tests de fumée).'
- q: Qu'est-ce qu'un nœud de déploiement Kolla-Ansible contient comme fichiers clés ?
  a: '`/etc/kolla/globals.yml` (choix : version, réseau, services activés, backend de stockage), `/etc/kolla/passwords.yml` (mots de passe générés par `kolla-genpwd`), un **inventaire** Ansible (`multinode`) qui place chaque service sur des groupes d''hôtes, et `/etc/kolla/config/` pour surcharger la configuration d''un service.'
quiz:
- q: Dans RHOSO, où regardes-tu l'état de l'API Nova ?
  options:
  - '`systemctl status openstack-nova-api` sur un contrôleur'
  - 'Dans OpenShift : `oc get pods -n openstack | grep nova-api` et `oc logs`'
  - Dans Horizon seulement
  - Sur un compute
  answer: 1
  explain: Le control plane de RHOSO est fait de pods OpenShift ; les computes, eux, font tourner des conteneurs Podman gérés par systemd (`edpm_nova_compute`).
- q: Pourquoi faut-il au moins trois contrôleurs ?
  options:
  - Pour les performances seulement
  - Pour garder le quorum de Galera, RabbitMQ (et des MON Ceph) si un nœud tombe
  - C'est une limite de licence
  - Pour Horizon
  answer: 1
  explain: Avec trois membres, la majorité (deux) reste disponible après la perte d'un nœud ; avec deux, une panne ou une coupure réseau peut tout bloquer.
level: intermédiaire
---

Personne n'installe OpenStack à la main en production : on utilise un **outil de déploiement** qui place les services sur les nœuds, génère la configuration et gère les mises à jour. Savoir lequel est utilisé chez toi dit où sont les fichiers de configuration, comment redémarrer un service et comment changer un réglage durablement. L'EX210 porte sur **RHOSO**, mais on retrouve les mêmes idées partout.

> **Les outils cités dans cette fiche.**
> - **Kolla-Ansible** : déploie OpenStack en conteneurs avec Ansible ; **Kolla** fournit les images.
> - **OpenStack-Ansible** (OSA) : un autre déploiement par Ansible, historiquement en conteneurs LXC.
> - **RHOSO** (Red Hat OpenStack Services on OpenShift) : la version Red Hat actuelle ; **RHOSP** : l'ancienne, basée sur TripleO.
> - **OpenShift** : la distribution Kubernetes de Red Hat ; **opérateur** : un programme qui gère une application dans Kubernetes (voir la fiche CRD et opérateurs).
> - **EDPM** (External Data Plane Management) : la partie de RHOSO qui configure les nœuds RHEL du data plane.
> - **DevStack** : un script qui installe un OpenStack de développement sur une seule machine.
> - **Galera** : le cluster MariaDB multi-maître ; **RabbitMQ** : la file de messages entre services.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **OVN** : Open Virtual Network : le moteur qui réalise les réseaux virtuels d'OpenStack (voir la fiche OVN).

## Comprendre : les rôles des nœuds

```
                 ┌────────── contrôleurs (×3) ──────────┐
                 │ API, schedulers, conductors, Horizon │
                 │ Galera, RabbitMQ, memcached          │
                 │ OVN northd / bases NB et SB          │
                 │ HAProxy + VIP (keepalived/Pacemaker)  │
                 └──────────────────────────────────────┘
réseaux : gestion (API internes) · stockage · tenant (Geneve) · externe (IP flottantes) · IPMI
                 ┌─────────── computes (×N) ────────────┐
                 │ nova-compute, libvirt/QEMU            │
                 │ ovn-controller, ovs, metadata agent   │
                 │ (en HCI : OSD Ceph)                    │
                 └──────────────────────────────────────┘
          nœuds réseau (gateway OVN) · nœuds de stockage Ceph · nœuds Ironic éventuels
```

Les trois contrôleurs ne sont pas là pour la performance mais pour le **quorum** : Galera et RabbitMQ (comme etcd dans Kubernetes) ont besoin d'une majorité de membres vivants.

## Les outils côte à côte

| Outil | Services | Configuration | Redémarrer un service |
| --- | --- | --- | --- |
| Kolla-Ansible | conteneurs Docker/Podman | `/etc/kolla/globals.yml`, `/etc/kolla/config/` → `/etc/kolla/<service>/` sur les nœuds | `docker restart nova_api` ou `kolla-ansible reconfigure -t nova` |
| OpenStack-Ansible | conteneurs LXC ou hôtes | `/etc/openstack_deploy/user_variables.yml` | `systemctl restart nova-api` dans le conteneur |
| RHOSO 18 | pods OpenShift + Podman sur RHEL | CR `OpenStackControlPlane` (champ `customServiceConfig`), `OpenStackDataPlaneNodeSet` | `oc delete pod` (recréé), `systemctl restart edpm_nova_compute` |
| RHOSP 16/17 (TripleO) | conteneurs Podman | templates Heat + `openstack overcloud deploy` | `systemctl restart tripleo_nova_api` |
| DevStack | processus systemd | `local.conf` | `systemctl restart devstack@n-api` |

La règle d'or : **ne pas modifier à la main** un fichier généré (`nova.conf` dans un conteneur) ; il serait écrasé au prochain déploiement. On change la source (globals.yml, la CR, le template) et on relance l'outil.

## Kolla-Ansible en bref

```bash
kolla-genpwd                                  # remplit passwords.yml
kolla-ansible -i multinode bootstrap-servers  # prépare les hôtes
kolla-ansible -i multinode prechecks
kolla-ansible -i multinode deploy
kolla-ansible -i multinode post-deploy        # génère admin-openrc.sh
kolla-ansible -i multinode reconfigure -t neutron   # après un changement de config
kolla-ansible -i multinode upgrade            # nouvelle version
```

## RHOSO en bref

```bash
oc get openstackcontrolplane -n openstack          # état global du control plane
oc get pods -n openstack                           # un pod par service (nova-api-0, keystone-…, galera-0…)
oc edit openstackcontrolplane openstack-control-plane   # changer une config (customServiceConfig)
oc get openstackdataplanenodeset,openstackdataplanedeployment -n openstack
oc rsh -n openstack openstackclient                # pod client avec la CLI openstack
```

Un changement dans la CR est appliqué par l'opérateur, qui redémarre les pods concernés. Pour le data plane, on crée un nouvel `OpenStackDataPlaneDeployment` qui rejoue les rôles Ansible sur les nœuds.

## Les mises à jour

| Type | Exemple | Risque |
| --- | --- | --- |
| mise à jour mineure | correctifs dans la même version | faible : images ou paquets plus récents |
| montée de version | 2025.1 → 2025.2 | migrations de base, changements de configuration |
| saut SLURP | 2025.1 → 2026.1 | possible directement entre deux SLURP |

Ordre classique : sauvegarder les bases (`mysqldump` ou sauvegarde Galera) et la configuration, monter le control plane (services compatibles avec les computes de la version précédente grâce aux **versions RPC** épinglées), puis les computes par lots, et enfin lever les épinglages et lancer les migrations en ligne (`nova-manage db online_data_migrations`).

> **À retenir.** Contrôleurs par trois pour le quorum (Galera, RabbitMQ, OVN), computes en nombre, réseaux séparés. Kolla-Ansible et OpenStack-Ansible déploient avec Ansible, RHOSO met le control plane dans OpenShift (opérateurs, CR) et le data plane sur RHEL (EDPM), TripleO c'était l'undercloud et l'overcloud. On change la source de la configuration, jamais le fichier généré. Les montées de version suivent l'ordre control plane puis computes, avec sauvegarde avant, et SLURP permet de sauter une version.
