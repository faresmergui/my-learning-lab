---
title: Automatiser avec Terraform, Ansible et Kubernetes
chapter: 23
order: 1
duration: 14
tags:
- OpenStack
- Terraform
- Ansible
- Kubernetes
cards:
- q: Quel provider Terraform utiliser pour OpenStack ?
  a: '`terraform-provider-openstack/openstack`. Il lit l''authentification dans **clouds.yaml** (`cloud = "prod"`) ou les variables `OS_*`, et propose des ressources comme `openstack_compute_instance_v2`, `openstack_networking_network_v2`, `openstack_blockstorage_volume_v3` et `openstack_lb_loadbalancer_v2`.'
- q: Où stocker l'état Terraform d'un projet OpenStack ?
  a: 'Dans un backend partagé avec verrouillage : le backend **s3** pointé vers RGW ou Swift s3api (le backend `swift` historique a été retiré de Terraform 1.3), ou HCP Terraform. Jamais seulement sur un poste.'
- q: Quelle collection Ansible pour piloter OpenStack ?
  a: '**openstack.cloud** : des modules comme `openstack.cloud.server`, `network`, `subnet`, `router`, `security_group_rule`, `volume`, `project`, `role_assignment`, qui utilisent clouds.yaml. Et un **inventaire dynamique** (`openstack.cloud.openstack`) qui liste les instances comme hôtes Ansible.'
- q: Terraform ou Heat ?
  a: '**Heat** est intégré au cloud (pas d''outil à installer, autoscaling avec Aodh, état gardé par le cloud). **Terraform** est multi-cloud, avec un écosystème de modules, un `plan` lisible et un état sous ton contrôle. Beaucoup d''équipes utilisent Terraform pour l''infrastructure et Ansible pour configurer les machines.'
- q: Que fournit cloud-provider-openstack à Kubernetes ?
  a: L'**OpenStack Cloud Controller Manager** (nœuds, Services `LoadBalancer` via **Octavia**), le pilote **Cinder CSI** (PersistentVolumes sur des volumes Cinder), **Manila CSI** (volumes partagés), et un webhook d'authentification Keystone. Il s'authentifie avec un identifiant d'application.
- q: Qu'est-ce que Cluster API Provider OpenStack (CAPO) ?
  a: 'Le fournisseur OpenStack de **Cluster API** : on décrit un cluster Kubernetes en ressources Kubernetes (Cluster, OpenStackCluster, MachineDeployment), et des contrôleurs créent réseaux, load balancer et instances pour lui, puis gèrent mises à jour et remplacements de nœuds.'
quiz:
- q: Tu veux que les PersistentVolumeClaims d'un cluster Kubernetes sur OpenStack créent des volumes Cinder. Qu'installes-tu ?
  options:
  - Le provider Terraform
  - Le pilote Cinder CSI de cloud-provider-openstack, avec une StorageClass `cinder.csi.openstack.org`
  - Swift
  - Manila seulement
  answer: 1
  explain: 'La StorageClass peut préciser le type de volume Cinder (`type: ssd`) et l''AZ.'
- q: Pourquoi utiliser un identifiant d'application plutôt qu'un compte utilisateur pour Terraform en CI ?
  options:
  - C'est plus rapide
  - Il est lié à un seul projet, avec des rôles limités, révocable sans toucher au compte humain, et ne dépend pas de son mot de passe ni de son MFA
  - C'est obligatoire
  - Il évite les quotas
  answer: 1
  explain: 'Dans clouds.yaml : `auth_type: v3applicationcredential` avec son id et son secret, gardés dans le coffre de la CI.'
level: intermédiaire
---

Cliquer dans Horizon ou taper des commandes une à une ne tient pas à l'échelle d'une équipe. On décrit donc l'infrastructure en code (**Terraform**), on configure les machines et on automatise l'exploitation (**Ansible**), et on fait souvent tourner les applications dans **Kubernetes** installé sur OpenStack. L'EX210 parle d'automatiser avec Ansible et de déploiements de masse ; cette fiche va au-delà avec Terraform et Kubernetes, très présents en entreprise.

> **Les outils cités dans cette fiche.**
> - **Terraform** : l'outil d'infrastructure en code (voir le module Terraform) ; **provider** : son plugin pour une plateforme.
> - **Ansible** : l'outil d'automatisation par playbooks YAML ; **collection** : un paquet de modules Ansible.
> - **clouds.yaml** : le fichier d'authentification commun à la CLI, Terraform et Ansible (voir la fiche CLI).
> - **identifiant d'application** (application credential) : un accès Keystone limité, fait pour les robots.
> - **CSI** (Container Storage Interface) : le standard des pilotes de stockage Kubernetes.
> - **Cluster API** : un projet Kubernetes qui crée et gère des clusters Kubernetes de façon déclarative.
> - **AZ** : une zone de disponibilité : un ou plusieurs datacenters indépendants dans une région.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.
> - **EDPM** : la partie de RHOSO qui configure les nœuds RHEL du data plane par Ansible.
> - **RHOSO** : Red Hat OpenStack Services on OpenShift, la version actuelle d'OpenStack chez Red Hat.

## Terraform

```hcl
terraform {
  required_providers {
    openstack = { source = "terraform-provider-openstack/openstack", version = "~> 3.0" }
  }
}
provider "openstack" { cloud = "prod" }            # entrée de clouds.yaml

resource "openstack_networking_network_v2" "app" { name = "app" }
resource "openstack_networking_subnet_v2" "app" {
  network_id = openstack_networking_network_v2.app.id
  cidr       = "10.30.0.0/24"
}
resource "openstack_networking_router_interface_v2" "app" {
  router_id = data.openstack_networking_router_v2.principal.id
  subnet_id = openstack_networking_subnet_v2.app.id
}
data "openstack_networking_router_v2" "principal" { name = "routeur-principal" }

resource "openstack_compute_instance_v2" "web" {
  count       = 3
  name        = "web-${count.index}"
  image_name  = "rocky-9"
  flavor_name = "m1.small"
  key_pair    = "ma-cle"
  security_groups = ["web"]
  user_data   = file("cloud-init.yaml")
  network { uuid = openstack_networking_network_v2.app.id }
}
```

Ressources utiles : `openstack_networking_secgroup_rule_v2`, `openstack_networking_floatingip_associate_v2`, `openstack_blockstorage_volume_v3` et `openstack_compute_volume_attach_v2`, `openstack_lb_loadbalancer_v2` et `openstack_lb_members_v2`, `openstack_identity_project_v3` pour les équipes plateforme. Les identifiants viennent de `clouds.yaml` (ou de `secure.yaml` séparé), jamais du code.

## Ansible

```yaml
- name: Créer une petite ferme web
  hosts: localhost
  tasks:
    - openstack.cloud.network: { cloud: prod, name: app }
    - openstack.cloud.subnet:  { cloud: prod, network_name: app, name: app-sn, cidr: 10.30.0.0/24 }
    - openstack.cloud.server:
        cloud: prod
        name: "web-{{ item }}"
        image: rocky-9
        flavor: m1.small
        key_name: ma-cle
        network: app
        security_groups: [web]
        auto_ip: false
        wait: true
      loop: [1, 2, 3]
```

```yaml
# inventaire dynamique : openstack.yml
plugin: openstack.cloud.openstack
clouds: [prod]
expand_hostvars: true
```

`ansible-inventory -i openstack.yml --graph` montre les instances groupées par projet, AZ, flavor ou métadonnée : on configure ensuite les VM avec des rôles Ansible classiques. C'est aussi Ansible qui déploie le cloud lui-même (Kolla-Ansible, OpenStack-Ansible, EDPM dans RHOSO) et automatise l'exploitation (créer des projets et quotas pour une nouvelle équipe, vider un compute).

## Choisir son outil

| Besoin | Outil |
| --- | --- |
| infrastructure d'une application, plan lisible, multi-cloud | Terraform |
| tout rester dans le cloud, autoscaling natif | Heat |
| configurer les VM, tâches d'exploitation, déploiement du cloud | Ansible |
| clusters Kubernetes gérés de façon déclarative | Cluster API (CAPO) ou Magnum |

## Kubernetes sur OpenStack

```
cluster Kubernetes (instances Nova)
 ├─ openstack-cloud-controller-manager  → Services LoadBalancer = load balancers Octavia
 │                                       → adresses et état des nœuds via Nova
 ├─ cinder-csi-plugin                   → PersistentVolumes = volumes Cinder (attachés au nœud)
 ├─ manila-csi-plugin                   → volumes partagés ReadWriteMany (CephFS, NFS)
 └─ k8s-keystone-auth (option)          → connexion à kubectl avec Keystone
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: cinder-ssd }
provisioner: cinder.csi.openstack.org
parameters: { type: ssd }
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

Points d'attention : le nombre de volumes attachables par instance (limite de virtio), l'AZ du volume qui doit correspondre à celle du nœud, les quotas Octavia et IP flottantes du projet, et un **identifiant d'application** dédié au cluster dans le secret `cloud-config`.

> **À retenir.** Terraform (provider openstack, authentification par clouds.yaml, état dans un backend partagé) décrit l'infrastructure ; Ansible (collection openstack.cloud, inventaire dynamique) configure les VM, automatise l'exploitation et déploie le cloud lui-même ; Heat reste l'outil natif. Kubernetes sur OpenStack s'appuie sur cloud-provider-openstack : Octavia pour les Services LoadBalancer, Cinder CSI et Manila CSI pour le stockage ; Cluster API gère les clusters. Les robots utilisent des identifiants d'application.
