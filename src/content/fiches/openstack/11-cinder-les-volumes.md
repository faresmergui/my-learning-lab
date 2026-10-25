---
title: 'Cinder : les volumes'
chapter: 11
order: 1
duration: 13
tags:
- OpenStack
- EX210
- Cinder
cards:
- q: Quels sont les composants de Cinder ?
  a: '**cinder-api** (requêtes), **cinder-scheduler** (choisit le backend selon le type et la capacité), **cinder-volume** (parle au stockage par un **pilote** : Ceph RBD, NetApp, Pure, PowerMax, LVM…) et **cinder-backup** (sauvegardes vers Ceph, Swift, S3, NFS).'
- q: À quoi sert un type de volume ?
  a: 'À offrir des **classes de stockage** aux utilisateurs (`ssd`, `standard`, `chiffré`) : il pointe vers un backend (`volume_backend_name`) et peut porter des QoS, du chiffrement, la réplication, le multi-attach.'
- q: Différence entre snapshot et backup Cinder ?
  a: Un **snapshot** est une copie instantanée **dans le même backend** (rapide, mais perdue si le backend l'est). Un **backup** est une copie **vers un autre stockage** (Swift, Ceph d'un autre cluster, S3), incrémentale, qui survit à la perte du backend principal.
- q: Comment se passe l'attachement d'un volume à une instance ?
  a: Nova demande à Cinder une **attachment** ; cinder-volume prépare l'accès (export iSCSI/FC, ou simple autorisation RBD) et renvoie les informations de connexion ; **os-brick** sur le compute branche le disque ; libvirt l'ajoute à la VM. Le volume passe de `available` à `attaching` puis `in-use`.
- q: Différence entre `retype` et `migrate` ?
  a: '`retype` change le **type** d''un volume (avec `--migration-policy on-demand` s''il faut changer de backend). `migrate` déplace le volume vers **un autre backend ou hôte** sans changer son type (opération d''admin).'
- q: Comment débloquer un volume coincé en `attaching` ou `deleting` ?
  a: 'D''abord comprendre (logs de cinder-volume, nova-compute, os-brick). Ensuite, en admin : `openstack volume set --state available <vol>` (ou `cinder reset-state`), et nettoyer les attachments orphelins (`cinder attachment-delete`). C''est un geste de dernier recours, après avoir vérifié l''état réel côté stockage et hyperviseur.'
quiz:
- q: Un volume de 100 Go doit passer à 200 Go alors qu'il est attaché. Que fais-tu ?
  options:
  - Le détacher obligatoirement
  - '`openstack volume set --size 200` (extension à chaud si le pilote et Nova le permettent), puis agrandir le système de fichiers dans l''instance'
  - Créer un nouveau volume et copier
  - Impossible
  answer: 1
  explain: Cinder étend le volume ; dans l'instance, `growpart` et `resize2fs` ou `xfs_growfs` agrandissent la partition et le système de fichiers.
- q: Le cluster Ceph principal est perdu. Quelles copies d'un volume restent utilisables ?
  options:
  - Les snapshots
  - Les backups envoyés vers un autre stockage
  - Les deux
  - Aucune
  answer: 1
  explain: Un snapshot vit dans le même backend que le volume ; seul un backup sur un autre stockage protège d'une perte du backend.
level: intermédiaire
---

**Cinder** fournit des **volumes** : des disques persistants qu'on crée, attache, détache, étend, copie et sauvegarde, indépendamment de la vie des instances. C'est l'équivalent d'EBS. L'objectif EX210 « Implement storage choices » consiste en bonne partie à choisir et configurer les bons types de volumes.

> **Les outils cités dans cette fiche.**
> - **Cinder** : le service de stockage bloc d'OpenStack.
> - **backend** : un stockage réel derrière Cinder (Ceph RBD, une baie NetApp ou Pure, LVM local…), piloté par un **pilote** (driver).
> - **type de volume** : une classe de stockage proposée aux utilisateurs, liée à un ou plusieurs backends.
> - **iSCSI** et **Fibre Channel** : des protocoles d'accès au stockage bloc ; **RBD** : le protocole bloc de Ceph.
> - **os-brick** : la bibliothèque qui branche le disque sur le compute (iSCSI, FC, NVMe-oF, RBD).
> - **multipath** : plusieurs chemins vers le même disque pour la redondance (baies iSCSI/FC).
> - **EBS** : les disques réseau attachés aux instances EC2.
> - **hyperviseur** : le logiciel qui fait tourner des machines virtuelles sur un serveur physique (KVM, VMware ESXi).
> - **IOPS** : le nombre d'opérations de lecture ou d'écriture qu'un disque fait par seconde.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **LUKS** : le chiffrement de disque standard de Linux.
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **NFS** : un protocole de partage de fichiers en réseau, monté comme un dossier local.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.

## Comprendre : où vivent les données

```
Instance ── disque virtio ── libvirt (compute) ── os-brick ──► backend
                                                     iSCSI / FC / NVMe-oF : baie
                                                     RBD : directement le cluster Ceph
cinder-api ─► cinder-scheduler ─► cinder-volume (pilote du backend) ─► API de la baie / Ceph
```

Avec **Ceph**, il n'y a pas d'export : le compute parle directement au cluster avec une clé (cephx), et cinder-volume ne fait que créer, cloner et supprimer des images RBD. C'est pour cela que Ceph est si répandu sous OpenStack.

## Les gestes courants

```bash
openstack volume create --size 50 --type ssd data-web1
openstack server add volume web1 data-web1          # apparaît en /dev/vdb (ou /dev/sdb)
openstack volume list --long
openstack server remove volume web1 data-web1
openstack volume set --size 100 data-web1           # extension (à chaud selon le pilote)
openstack volume create --image rocky-9 --size 20 --bootable rocky-boot   # volume amorçable
openstack volume create --source data-web1 data-web1-clone                # clone
openstack volume transfer request create data-web1                        # céder à un autre projet
```

Dans l'instance, après une extension : `growpart /dev/vdb 1` puis `resize2fs` ou `xfs_growfs`.

## Types de volumes et backends

```ini
# cinder.conf (extrait)
[DEFAULT]
enabled_backends = ceph-ssd,ceph-hdd

[ceph-ssd]
volume_driver = cinder.volume.drivers.rbd.RBDDriver
volume_backend_name = ceph-ssd
rbd_pool = volumes-ssd
rbd_user = openstack
rbd_secret_uuid = …

[ceph-hdd]
volume_driver = cinder.volume.drivers.rbd.RBDDriver
volume_backend_name = ceph-hdd
rbd_pool = volumes-hdd
…
```

```bash
openstack volume type create --property volume_backend_name=ceph-ssd ssd
openstack volume type create --property volume_backend_name=ceph-hdd --public standard
openstack volume qos create --consumer front-end \
  --property total_iops_sec=3000 --property total_bytes_sec=209715200 qos-ssd
openstack volume qos associate qos-ssd ssd
openstack volume type set --property multiattach="<is> True" shared-disk
openstack volume backend pool list --long       # (admin) capacité vue par le scheduler
openstack volume service list                   # cinder-volume par backend : up/down
```

| Propriété du type | Effet |
| --- | --- |
| `volume_backend_name` | backend utilisé |
| QoS associée (`front-end` : appliquée par l'hyperviseur, `back-end` : par la baie) | limites d'IOPS et de débit |
| `multiattach="<is> True"` | attachable à plusieurs instances (le système de fichiers doit le gérer) |
| chiffrement (`volume type create --encryption-provider luks …`) | volume chiffré par LUKS, clé dans Barbican |
| `replication_enabled="<is> True"` | réplication par le backend (selon le pilote) |

## Snapshots et backups

```bash
openstack volume snapshot create --volume data-web1 data-web1-snap
openstack volume create --snapshot data-web1-snap data-web1-restaure

openstack volume backup create --name data-web1-bkp data-web1           # complet
openstack volume backup create --incremental --name data-web1-inc data-web1
openstack volume backup restore data-web1-bkp data-web1-restaure2
openstack volume backup list
```

| | Snapshot | Backup |
| --- | --- | --- |
| où | même backend | autre stockage (Swift, Ceph secondaire, S3, NFS) |
| vitesse | instantané (Ceph) | copie des données (incrémentale ensuite) |
| survit à la perte du backend | non | **oui** |
| usage | point de retour avant une opération | protection réelle des données |

Un volume `in-use` peut être sauvegardé avec `--force` (en passant par un snapshot), mais la cohérence applicative (base de données) demande de geler ou d'arrêter l'application.

## Déplacer et changer de classe

```bash
openstack volume set --type ssd --retype-policy on-demand data-web1   # changer de type, migrer si besoin
openstack volume migrate --host cinder@ceph-hdd#ceph-hdd data-web1   # (admin) autre backend
```

## Les états et les blocages

| État | Sens |
| --- | --- |
| `creating` → `available` | créé, libre |
| `attaching` → `in-use` | attaché |
| `detaching` → `available` | détaché |
| `extending`, `backing-up`, `restoring-backup`, `retyping`, `deleting` | opérations en cours |
| `error`, `error_deleting`, `error_extending` | échec |

Un volume bloqué vient presque toujours d'un désaccord entre Cinder, Nova (libvirt) et le stockage. Méthode : request-id dans les logs de cinder-volume et nova-compute, état réel sur la baie ou dans Ceph (`rbd ls volumes-ssd`, `rbd status`), état réel dans la VM (`virsh domblklist`). Seulement ensuite, en admin, `openstack volume set --state available` et nettoyage des attachments.

> **À retenir.** cinder-api, scheduler, volume (pilote du backend), backup. Les types de volumes offrent des classes (backend, QoS, chiffrement, multi-attach). Snapshot = même backend, backup = autre stockage, seul le second protège vraiment. Extension avec `volume set --size` puis agrandissement dans l'instance. Un volume bloqué se diagnostique sur les trois côtés (Cinder, Nova, stockage) avant tout `set --state`.
