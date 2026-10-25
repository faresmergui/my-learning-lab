---
title: Synthèse OpenStack
description: "Architecture, Keystone, Glance, Nova, Neutron/OVN, Cinder, Ceph, Swift, Heat, Octavia, déploiement, exploitation, sécurité, supervision et débogage."
---

## Ce qu'est OpenStack

- Un ensemble de services qui transforme des serveurs en **cloud privé** en libre-service, piloté par API.
- Chaque service a une **API REST**, s'authentifie auprès de **Keystone**, stocke son état dans **MariaDB/Galera** et se coordonne par **RabbitMQ**.
- Deux versions par an (`2025.1`, `2025.2`…) ; les `.1` sont **SLURP** (saut d'une version possible).

| Service | Rôle | Équivalent AWS |
| --- | --- | --- |
| Keystone | identité, jetons, catalogue | IAM |
| Glance | images | AMI |
| Nova (+ Placement) | instances, scheduling | EC2 |
| Neutron (OVN) | réseaux, routeurs, IP flottantes, groupes de sécurité | VPC |
| Cinder | volumes | EBS |
| Swift / RGW | objet | S3 |
| Heat | orchestration | CloudFormation |
| Octavia | load balancers | ELB |
| Designate, Barbican, Manila, Ironic | DNS, secrets, partages, bare metal | Route 53, KMS, EFS, metal |

## Architecture

- **Contrôleurs ×3** (API sans état, Galera, RabbitMQ, OVN NB/SB en quorum, HAProxy + VIP), **computes ×N** (nova-compute, libvirt/QEMU, ovn-controller), stockage Ceph, réseaux séparés (gestion, stockage, tenant Geneve, externe).
- Une requête : client → Keystone (jeton) → API du service → base + RabbitMQ → agent sur le nœud.

## CLI et identité

```bash
export OS_CLOUD=prod                    # entrée de ~/.config/openstack/clouds.yaml
openstack token issue; openstack catalog list
openstack --debug server list           # requêtes HTTP et request-id
```

- **Domaine** → **projets** → utilisateurs et groupes ; rôles **reader, member, manager, admin** en portée **projet, domaine ou système**.
- Jetons **Fernet** : clés identiques sur tous les contrôleurs, rotation régulière.
- Domaine adossé à **LDAP/IdM** pour un client ; **identifiants d'application** pour les robots.
- Quotas par projet ; partage de réseaux et d'images par **RBAC** ou `--share`/`--public`.

## Images et instances

- Glance : `qcow2` ou **raw** (obligatoire pour les clones copy-on-write sur Ceph), propriétés `hw_*`, visibilité public/private/shared/community.
- Flavor = vCPU, RAM, disque + extra specs (`hw:cpu_policy=dedicated`, hugepages, agrégats).
- cloud-init lit **user data** et métadonnées (169.254.169.254 ou config drive).
- États : BUILD → ACTIVE ; SHUTOFF, ERROR, VERIFY_RESIZE.
- Scheduling : **Placement** (inventaire, ratios, traits) puis filtres et poids ; agrégats, AZ, server groups (affinité).

## Réseau

- Réseau, sous-réseau, port, routeur, IP flottante, groupe de sécurité (état, entrée fermée par défaut), port security.
- **Provider** (VLAN/flat du datacenter) vs **self-service** (Geneve par projet).
- **OVN** : `neutron-server` → base **NB** (logique) → `ovn-northd` → base **SB** (flux) → `ovn-controller` sur chaque nœud → OVS.
- Debug : `ovn-nbctl show`, `ovn-sbctl show`, `ovn-trace`, namespace `ovnmeta-*`.

## Stockage

- **Cinder** : types de volumes (backend, QoS, chiffrement LUKS, multi-attach) ; snapshot = même backend, **backup** = autre stockage.
- **Ceph** : MON, MGR, OSD ; pools `images`, `volumes`, `vms`, `backups` ; une clé cephx par service ; `ceph -s`, `ceph health detail`, `ceph osd tree`, `ceph df` ; `noout` avant une maintenance ; HCI = réserver CPU et RAM aux OSD.
- **Swift** : compte / conteneur / objet, proxy et rings, cohérence éventuelle, SLO pour les gros fichiers, s3api ; RGW de Ceph sert souvent l'API Swift.

## Heat et Octavia

- HOT : `parameters`, `resources`, `outputs` ; `get_param`, `get_resource`, `get_attr` créent le graphe de dépendances ; environnements (`-e`) et `resource_registry`.
- `stack update --dry-run` avant de changer ; en échec : `stack failures list`, `stack event list --nested-depth 5`.
- Octavia : load balancer (VIP) → listener → pool (+ health monitor) → membres ; provider **amphora** (L7, TLS via Barbican) ou **ovn** (L4, instantané) ; `loadbalancer status show`.

## Déployer et exploiter

| Outil | Où changer la configuration |
| --- | --- |
| Kolla-Ansible | `globals.yml`, `/etc/kolla/config/` puis `reconfigure` |
| RHOSO | CR `OpenStackControlPlane` (`customServiceConfig`), `OpenStackDataPlaneNodeSet` |
| OpenStack-Ansible | `user_variables.yml` |

- Ne jamais modifier un fichier généré ; changer la source et relancer l'outil.
- Galera : `wsrep_cluster_status Primary`, bootstrap depuis le nœud au plus grand seqno. RabbitMQ : files sans consommateur.
- Sauvegarder bases, configuration, clés Fernet, bases OVN, clé maître Barbican ; tester la restauration.
- Arrêt : instances, computes, contrôleurs, stockage ; redémarrage dans l'ordre inverse.
- Computes : `compute service set --disable`, **live migration** (hôte vivant), cold migration, **evacuate** (hôte mort et fencé) ; capacité = (total − réservé) × ratio dans Placement ; Watcher pour rééquilibrer.

## Sécurité et supervision

- TLS sur API publiques et internes, Galera, RabbitMQ, OVN, libvirt (IdM ou cert-manager).
- Rôle personnalisé : `role create` + règle dans `policy.yaml` ; reader système pour auditer.
- Nœuds : SELinux enforcing (sVirt), **AIDE** avec base de référence gardée à l'extérieur.
- Infrastructure : exporters → Prometheus → Alertmanager/Grafana ; consommation : Ceilometer → Gnocchi/Prometheus → Aodh ; Red Hat : **STF**.
- Logs centralisés, recherche par **request-id**.

## Déboguer

1. `server show` (status, fault) → 2. request-id (`server event list`, `--debug`) → 3. logs des services sur le parcours → 4. état réel (virsh, OVN, Ceph) → 5. corriger la cause, l'état en dernier.

| Symptôme | Piste |
| --- | --- |
| 401 / 403 | authentification / politique |
| No valid host | capacité ou filtres : logs nova-scheduler |
| binding_failed | ovn-controller, hostname, bridge mappings |
| pas de clé SSH | métadonnées (agent ovn-metadata) |
| tout lent, BUILD sans fin | RabbitMQ ou Galera |
| volume bloqué | Cinder, Nova et stockage ensemble |

## Automatiser

- **Terraform** : provider `terraform-provider-openstack/openstack`, `cloud = "prod"`, état dans un backend partagé.
- **Ansible** : collection `openstack.cloud`, inventaire dynamique ; déploie aussi le cloud (Kolla, OSA, EDPM).
- **Kubernetes** : cloud-provider-openstack (Octavia pour les Services LoadBalancer, Cinder CSI, Manila CSI), Cluster API (CAPO).
