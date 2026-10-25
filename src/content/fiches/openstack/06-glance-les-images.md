---
title: 'Glance : les images'
chapter: 6
order: 1
duration: 11
tags:
- OpenStack
- EX210
- Glance
cards:
- q: Quels formats d'image Glance accepte-t-il le plus souvent ?
  a: '**qcow2** (compact, avec copie sur écriture, le plus courant), **raw** (brut, indispensable avec Ceph pour les clones instantanés), **vmdk** (VMware), **vhd/vhdx** (Hyper-V), **iso** (installation). `qemu-img convert` passe de l''un à l''autre.'
- q: Pourquoi utiliser des images raw quand Glance et Nova sont sur Ceph ?
  a: 'Ceph peut alors **cloner** l''image instantanément (copy-on-write RBD) pour créer le disque de l''instance. Avec du qcow2, Nova doit d''abord télécharger et convertir l''image : démarrages lents et espace gaspillé.'
- q: À quoi servent les propriétés d'une image ?
  a: 'À décrire l''image (`os_distro`, `os_version`) et à guider Nova : `hw_disk_bus=scsi`, `hw_scsi_model=virtio-scsi`, `hw_qemu_guest_agent=yes`, `hw_firmware_type=uefi`, `hw_machine_type=q35`, `os_require_quiesce`, et les traits requis pour le scheduler.'
- q: Comment créer une image personnalisée sans la préparer à la main ?
  a: Partir d'une image cloud officielle et la modifier avec **virt-customize** (installer des paquets, ajouter des fichiers, injecter une clé) ou **diskimage-builder** / **Packer**, puis la téléverser dans Glance. Avec `virt-sysprep`, on retire les éléments propres à une machine (machine-id, clés SSH de l'hôte).
- q: Qu'est-ce qu'un snapshot d'instance ?
  a: Une **nouvelle image Glance** créée depuis le disque d'une instance (`openstack server image create`). Pour une instance démarrée sur volume, c'est un snapshot Cinder référencé par une image. On peut relancer des instances à partir de lui.
- q: Comment vérifier qu'une image n'a pas été altérée ?
  a: Glance calcule une empreinte (`os_hash_algo`, `os_hash_value`, sha512 par défaut) et l'ancien `checksum` md5. On peut aussi **signer** les images (propriétés `img_signature*`, avec Barbican) et demander à Nova de vérifier la signature.
quiz:
- q: Les instances mettent 4 minutes à démarrer et le réseau de stockage sature à chaque création. Glance et Nova utilisent Ceph. Cause probable ?
  options:
  - Trop de vCPU
  - 'Images en qcow2 : chaque démarrage télécharge et convertit au lieu de cloner'
  - Les clés Fernet
  - Un quota trop bas
  answer: 1
  explain: Convertir l'image en raw (`qemu-img convert -O raw`) permet le clone RBD instantané.
- q: Une image Windows doit démarrer en UEFI avec un bus disque SCSI. Où le déclares-tu ?
  options:
  - Dans la flavor uniquement
  - Dans les propriétés de l'image (`hw_firmware_type=uefi`, `hw_disk_bus=scsi`, `hw_scsi_model=virtio-scsi`)
  - Dans Neutron
  - Dans clouds.yaml
  answer: 1
  explain: Les propriétés d'image indiquent à Nova comment construire la machine virtuelle.
level: intermédiaire
---

**Glance** stocke les **images** : les disques modèles à partir desquels Nova crée les instances. Une bonne image (au bon format, avec les bonnes propriétés, préparée pour le cloud) fait la différence entre une instance qui démarre en dix secondes et une qui met des minutes ou ne démarre pas. L'objectif EX210 « Create and customize images » porte précisément là-dessus.

> **Les outils cités dans cette fiche.**
> - **Glance** : le service d'images d'OpenStack ; il garde les métadonnées et délègue le stockage à un **backend** (fichiers, Ceph RBD, Swift, Cinder, S3).
> - **qcow2** et **raw** : deux formats de disque virtuel ; qcow2 est compact, raw est un disque brut.
> - **qemu-img** : l'outil qui inspecte et convertit les disques virtuels.
> - **cloud-init** : le programme, présent dans les images cloud, qui configure l'instance au premier démarrage (clé SSH, nom, user data).
> - **virt-customize** et **virt-sysprep** (paquet libguestfs) : modifient une image disque sans la démarrer.
> - **diskimage-builder** et **Packer** : construisent des images de façon automatisée.
> - **QEMU guest agent** : un agent dans l'instance qui permet à l'hôte de geler les écritures (snapshots cohérents) ou de connaître l'IP.
> - **MAC** : l'adresse matérielle d'une carte réseau, utilisée sur le réseau local.
> - **RHEL** : Red Hat Enterprise Linux, la distribution Linux d'entreprise de Red Hat.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.

## Comprendre : ce qu'est une image cloud

Une image cloud n'est pas un système installé à la main. Elle est **générique** et se personnalise au démarrage :

- **cloud-init** installé : il lit le service de métadonnées ou le config drive (clé SSH, nom, user data) ;
- **aucun mot de passe** par défaut, connexion par clé ;
- pilotes **virtio** (disque et réseau) pour les performances ;
- système de fichiers qui **s'agrandit** à la taille du disque de la flavor ;
- aucun élément propre à une machine (machine-id, clés SSH de l'hôte, adresse MAC figée).

Les distributions publient ces images : Rocky Linux, AlmaLinux, RHEL (KVM Guest Image), Ubuntu Cloud Images, Debian « genericcloud ».

## Téléverser une image

```bash
qemu-img info rocky-9.qcow2                       # format, taille virtuelle
qemu-img convert -f qcow2 -O raw rocky-9.qcow2 rocky-9.raw    # pour un backend Ceph

openstack image create --disk-format raw --container-format bare \
  --file rocky-9.raw --public \
  --property os_distro=rocky --property os_version=9 \
  --property hw_qemu_guest_agent=yes \
  --min-disk 10 --min-ram 1024 \
  rocky-9

openstack image list
openstack image show rocky-9 -c status -c size -c properties
```

Pour de très grosses images, l'**import interopérable** (`openstack image create --import` avec la méthode `web-download` ou `glance-direct`) laisse Glance télécharger ou traiter l'image lui-même, et peut **convertir** automatiquement le format à l'import.

## Le bon format

| Backend | Format conseillé | Pourquoi |
| --- | --- | --- |
| Ceph RBD (Glance + Nova/Cinder sur Ceph) | **raw** | clone instantané, aucun téléchargement |
| fichiers locaux | qcow2 | compact, copie sur écriture locale |
| import depuis VMware | vmdk → convertir | `qemu-img convert -f vmdk -O raw` |

## Les propriétés utiles

| Propriété | Effet |
| --- | --- |
| `os_distro`, `os_version` | description, parfois utilisées par d'autres outils |
| `hw_disk_bus` / `hw_scsi_model` | `virtio` (défaut), ou `scsi` + `virtio-scsi` (plus de disques, TRIM) |
| `hw_vif_model` | modèle de carte réseau (`virtio`, `e1000` pour de vieux systèmes) |
| `hw_firmware_type=uefi` / `hw_machine_type=q35` | démarrage UEFI, machine moderne (Windows récents, Secure Boot) |
| `hw_qemu_guest_agent=yes` | active le canal de l'agent invité |
| `os_require_quiesce=yes` | exige l'agent pour geler les écritures lors d'un snapshot |
| `hw_rng_model=virtio` | source d'aléa pour l'instance |
| `trait:CUSTOM_…=required` | n'utiliser que des hôtes qui ont ce trait |
| `min_disk`, `min_ram` | refuser une flavor trop petite |

## Personnaliser une image

```bash
virt-customize -a rocky-9.qcow2 \
  --install qemu-guest-agent,chrony,vim-enhanced \
  --run-command 'systemctl enable qemu-guest-agent' \
  --copy-in ./ca-entreprise.crt:/etc/pki/ca-trust/source/anchors/ \
  --run-command 'update-ca-trust' \
  --selinux-relabel
virt-sysprep -a rocky-9.qcow2 --operations machine-id,ssh-hostkeys,logfiles
```

Pour une chaîne industrielle (une image durcie reconstruite chaque mois), on automatise avec **diskimage-builder** ou **Packer** (qui démarre une instance temporaire, la configure avec Ansible, puis la capture), et on publie l'image avec une date dans son nom.

## Snapshots et cycle de vie

```bash
openstack server image create --name web1-avant-maj web1    # snapshot de l'instance
openstack image set --deactivate rocky-9-2026-08            # empêcher les téléchargements
openstack image set --property hw_firmware_type=uefi rocky-9
openstack image set --protected rocky-9                     # interdire la suppression
openstack image delete rocky-9-2026-06
```

Un snapshot d'instance n'est cohérent que si les écritures sont gelées : avec l'agent invité, Nova le demande automatiquement (`fsfreeze`). Une bonne pratique : garder des images **nommées par date**, marquer la courante (`--tag current` ou une propriété), et désactiver puis supprimer les anciennes une fois inutilisées.

> **À retenir.** Une image cloud est générique et se configure au démarrage avec cloud-init. raw avec Ceph pour le clone instantané, qcow2 sinon ; `qemu-img` pour inspecter et convertir. Les propriétés (`hw_*`, `os_*`, `min_*`) disent à Nova comment construire la VM. virt-customize et virt-sysprep pour personnaliser, diskimage-builder ou Packer pour industrialiser. Snapshot = nouvelle image, cohérente avec l'agent invité.
