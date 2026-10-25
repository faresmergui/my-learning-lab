---
title: Ce qu'est OpenStack
chapter: 1
order: 1
duration: 11
tags:
- OpenStack
- EX210
- fondations
cards:
- q: Qu'est-ce qu'OpenStack ?
  a: 'Un ensemble de logiciels open source qui transforme des serveurs, du stockage et du réseau en **cloud IaaS** : on crée des machines virtuelles, des réseaux, des volumes par API, en libre-service, avec des quotas par projet. C''est l''équivalent privé d''EC2, VPC et EBS.'
- q: Quels sont les services cœur et leur rôle ?
  a: '**Keystone** (identité et catalogue), **Glance** (images), **Nova** (instances), **Placement** (inventaire des ressources), **Neutron** (réseau), **Cinder** (volumes), **Horizon** (interface web). Souvent aussi **Swift** (objet), **Heat** (orchestration), **Octavia** (load balancer).'
- q: Comment sont nommées les versions d'OpenStack ?
  a: Deux versions par an, au printemps et à l'automne, nommées `année.1` et `année.2` (2025.1 « Epoxy », 2025.2 « Flamingo »…) avec un nom de code alphabétique. Les versions **SLURP** (une sur deux, les `.1`) permettent de sauter une version lors d'une mise à jour.
- q: Quelles sont les principales distributions ou outils de déploiement ?
  a: '**Red Hat OpenStack Services on OpenShift** (RHOSO, le control plane tourne sur OpenShift), **Kolla-Ansible** (conteneurs Docker ou Podman), **OpenStack-Ansible** (conteneurs LXC ou sans), **Canonical** (Sunbeam, Charms), **Kayobe**, et **DevStack** pour le développement seulement.'
- q: Que veut dire « IaaS » ?
  a: '**Infrastructure as a Service** : le fournisseur donne des briques d''infrastructure (calcul, réseau, stockage) que l''utilisateur assemble ; il gère lui-même les systèmes et applications dessus. Par opposition au PaaS (plateforme) et au SaaS (logiciel).'
- q: Comment les services OpenStack communiquent-ils entre eux ?
  a: Par leurs **API REST** (un service appelle l'API d'un autre, avec un jeton Keystone) et, **à l'intérieur** d'un service, par une file de messages **RabbitMQ** (par exemple nova-api vers nova-conductor vers nova-compute). Chacun a sa propre base de données.
quiz:
- q: Quel service OpenStack équivaut à EBS sur AWS ?
  options:
  - Swift
  - Cinder
  - Glance
  - Manila
  answer: 1
  explain: Cinder fournit des volumes bloc attachables. Swift équivaut à S3, Manila à EFS, Glance au registre d'AMI.
- q: Pourquoi une entreprise choisit-elle OpenStack plutôt qu'un cloud public ?
  options:
  - C'est toujours moins cher
  - Pour garder la maîtrise des données et du matériel (souveraineté, coûts à grande échelle, réseau d'opérateur, besoins spécifiques)
  - Parce qu'il n'y a rien à exploiter
  - Pour avoir plus de services managés
  answer: 1
  explain: OpenStack demande une vraie équipe d'exploitation ; en échange, on contrôle tout, sur son propre matériel.
level: intermédiaire
---

**OpenStack** est le logiciel de cloud privé le plus répandu : opérateurs télécoms, banques, administrations, hébergeurs, laboratoires. Il fait sur tes propres serveurs ce qu'AWS fait sur les siens : des machines virtuelles, des réseaux et des volumes créés à la demande par API. Ce module part des fondations et va jusqu'à l'exploitation et au débogage d'un cloud en production.

> **Les outils cités dans cette fiche.**
> - **IaaS** (Infrastructure as a Service) : un cloud qui fournit des machines, des réseaux et du stockage, sur lesquels l'utilisateur installe ce qu'il veut.
> - **hyperviseur** : le logiciel qui fait tourner les machines virtuelles ; dans OpenStack, presque toujours **KVM** piloté par **libvirt** et **QEMU**.
> - **API REST** : une interface HTTP ; chaque service OpenStack en expose une.
> - **RabbitMQ** : un courtier de messages, utilisé par les composants d'un même service pour se parler.
> - **MariaDB** (souvent en cluster **Galera**) : la base de données où chaque service garde son état.
> - **Ceph** : un système de stockage distribué très souvent utilisé sous OpenStack (fiche dédiée).
> - **OpenShift** : la plateforme Kubernetes de Red Hat, sur laquelle tourne le control plane de RHOSO.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **jeton** : une chaîne secrète qui prouve qu'on est authentifié, à durée limitée.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).
> - **EC2** : le service de machines virtuelles d'AWS.
> - **AMI** : l'image de disque à partir de laquelle on démarre une instance EC2.
> - **VPC** : un réseau privé virtuel dans le cloud, isolé des autres clients.

## Comprendre : un cloud, c'est quoi de plus que la virtualisation ?

Un cluster de virtualisation classique (VMware, Proxmox) permet à un **administrateur** de créer des VM. Un cloud ajoute :

| Propriété | Ce que ça veut dire dans OpenStack |
| --- | --- |
| **libre-service** | chaque équipe crée ses instances, réseaux, volumes, sans ticket |
| **API d'abord** | tout est faisable par API, donc par Terraform, Ansible, la CI |
| **multi-tenant** | chaque projet est isolé (réseaux, quotas, droits) |
| **élasticité** | on crée et détruit en minutes ; les instances sont jetables |
| **mesure** | quotas, consommation par projet, facturation interne |

Conséquence importante : une instance OpenStack se traite comme du **bétail**, pas comme un animal de compagnie. On la recrée à partir d'une image et d'une configuration plutôt que de la réparer à la main.

## Les services et leurs équivalents

| Service | Rôle | Équivalent AWS |
| --- | --- | --- |
| **Keystone** | identité, jetons, catalogue des services | IAM |
| **Nova** | instances (machines virtuelles) | EC2 |
| **Placement** | inventaire et réservation des ressources (CPU, RAM, disque) | — |
| **Glance** | images de systèmes | AMI |
| **Neutron** | réseaux, routeurs, IP flottantes, security groups | VPC |
| **Cinder** | volumes bloc | EBS |
| **Swift** | stockage objet | S3 |
| **Manila** | partages de fichiers (NFS, CephFS) | EFS |
| **Heat** | orchestration par modèles | CloudFormation |
| **Octavia** | load balancer | ELB |
| **Designate** | DNS | Route 53 |
| **Barbican** | secrets et clés | KMS, Secrets Manager |
| **Ironic** | serveurs physiques en libre-service | instances bare metal |
| **Magnum** | clusters Kubernetes | EKS |
| **Horizon** | interface web | console |
| **Ceilometer**, **Gnocchi**, **Aodh** | télémétrie, métriques, alarmes | CloudWatch |

## Le rythme des versions

OpenStack sort **deux versions par an**. Depuis 2023, elles sont numérotées `2025.1`, `2025.2`… avec un nom de code (Antelope, Bobcat, Caracal, Dalmatian, Epoxy, Flamingo…). Une version sur deux, la `.1`, est dite **SLURP** (Skip Level Upgrade Release Process) : on peut passer directement de l'une à la suivante en sautant la `.2` intermédiaire.

Les distributions commerciales figent une version et la maintiennent plus longtemps. Côté Red Hat :

| Produit | Base | Déploiement |
| --- | --- | --- |
| RHOSP 16 et 17 | OpenStack Train, Wallaby | **TripleO** : un « undercloud » déploie l'« overcloud » |
| **RHOSO 18** | Antelope | le **control plane** tourne en pods sur **OpenShift** (opérateurs), les nœuds compute sont gérés par Ansible (« data plane ») |

Les termes **undercloud / overcloud** restent très présents dans la documentation et l'examen : l'overcloud est le cloud des utilisateurs, l'undercloud l'outil qui le déploie.

## Les manières de déployer

| Outil | Principe |
| --- | --- |
| **Kolla-Ansible** | services en conteneurs Docker ou Podman, déployés par Ansible ; très répandu |
| **OpenStack-Ansible** | rôles Ansible, services dans des conteneurs LXC ou directement sur l'hôte |
| **RHOSO** | opérateurs Kubernetes sur OpenShift + Ansible pour les nœuds |
| **Canonical** (Sunbeam, Charms) | snaps et Juju |
| **Kayobe** | Kolla-Ansible plus le provisionnement des serveurs physiques |
| **DevStack** | une machine de développement ou d'essai, **jamais en production** |

Le chapitre « Déployer OpenStack » compare ces outils.

## Les mots à connaître dès maintenant

- **projet** (anciennement *tenant*) : l'unité d'isolation et de quotas ;
- **instance** : une machine virtuelle ; **flavor** : son gabarit (vCPU, RAM, disque) ;
- **image** : le disque modèle ; **volume** : un disque persistant ;
- **réseau self-service** : un réseau privé créé par un projet ; **réseau provider** : un réseau relié au réseau physique ;
- **IP flottante** : une adresse publique attachée à une instance ;
- **control plane** : les API, bases, files de messages ; **nœuds compute** : les serveurs qui font tourner les instances.

> **À retenir.** OpenStack transforme des serveurs en cloud IaaS en libre-service, par API, multi-projet. Keystone, Nova, Placement, Glance, Neutron, Cinder et Horizon forment le cœur ; Swift, Heat, Octavia, Designate, Barbican et Manila complètent. Deux versions par an (`2025.1`, `2025.2`), la `.1` permet de sauter une version. Red Hat est passé de TripleO (undercloud/overcloud) à RHOSO, avec le control plane sur OpenShift.
