---
title: 'Nova : créer, initialiser et gérer des instances'
chapter: 7
order: 1
duration: 13
tags:
- OpenStack
- EX210
- Nova
- cloud-init
cards:
- q: Comment une instance reçoit-elle sa clé SSH et son script de démarrage ?
  a: Par le **service de métadonnées** (`http://169.254.169.254`, relayé par Neutron/OVN) ou un **config drive** (petit disque attaché). **cloud-init** y lit la clé (`--key-name`), le nom et les **user data** (`--user-data fichier`) et les applique au premier démarrage.
- q: Différence entre disque éphémère et démarrage sur volume ?
  a: '**Éphémère** : le disque racine vient de l''image, vit sur le compute (ou dans Ceph, pool `vms`) et disparaît avec l''instance. **Boot from volume** : la racine est un **volume Cinder**, qui peut survivre à l''instance (`--boot-from-volume 20`, option de suppression réglable).'
- q: Différence entre `reboot`, `reboot --hard`, `rebuild` et `rescue` ?
  a: '`reboot` (soft) demande à l''OS de redémarrer ; `--hard` coupe et relance la VM ; `rebuild` **réinstalle** le disque racine depuis une image (même ID, même IP) ; `rescue` démarre sur une image de secours avec l''ancien disque attaché, pour le réparer.'
- q: À quoi servent `shelve` et `unshelve` ?
  a: '`shelve` arrête l''instance, en fait une image et **libère les ressources** du compute (CPU, RAM ne sont plus réservés). `unshelve` la recrée, peut-être sur un autre hôte. Utile pour les instances rarement utilisées.'
- q: Comment s'assurer que deux instances ne tournent pas sur le même hôte ?
  a: Les créer dans un **server group** avec la politique **anti-affinity** (`openstack server group create --policy anti-affinity web`, puis `--hint group=<id>`). `soft-anti-affinity` le fait si possible, sans échouer.
- q: Que signifient les états `vm_state` et `task_state` ?
  a: '`vm_state` est l''état stable (`active`, `stopped`, `error`, `shelved_offloaded`…), `task_state` l''opération en cours (`spawning`, `rebooting`, `resize_migrating`…). Une instance coincée a souvent un task_state qui ne se termine pas.'
quiz:
- q: Une instance doit, à sa création, installer nginx et écrire une page d'accueil. Que passes-tu à `server create` ?
  options:
  - '`--property`'
  - '`--user-data init.yaml` avec un `#cloud-config` (packages, write_files, runcmd)'
  - '`--hint`'
  - Un security group
  answer: 1
  explain: cloud-init exécute les user data au premier démarrage, s'il est présent dans l'image.
- q: Après un `server resize`, l'instance est en `VERIFY_RESIZE`. Que faut-il faire ?
  options:
  - Rien, c'est une erreur
  - Vérifier puis `openstack server resize confirm` (ou `revert` pour revenir en arrière)
  - La supprimer
  - '`reboot --hard`'
  answer: 1
  explain: Le redimensionnement attend une confirmation ; sans elle, il est confirmé automatiquement après un délai si `resize_confirm_window` est configuré.
- q: SSH ne répond plus et tu soupçonnes un fstab cassé dans l'instance. Que fais-tu d'abord ?
  options:
  - La supprimer
  - '`openstack console log show` puis la console noVNC ; si besoin, `server rescue` pour réparer le disque'
  - '`rebuild` immédiatement'
  - Augmenter la flavor
  answer: 1
  explain: Le journal de console montre le démarrage ; le mode rescue permet de monter le disque et de corriger sans perdre les données.
level: intermédiaire
---

**Nova** crée et gère les instances : le service qu'on utilise le plus et sur lequel on passe le plus de temps à déboguer. Cette fiche couvre le cycle de vie d'une instance, son initialisation par cloud-init (objectif EX210 « Initialize an instance during deployment ») et les actions courantes. La fiche suivante traite du placement sur les hôtes.

> **Les outils cités dans cette fiche.**
> - **instance** (server) : une machine virtuelle gérée par Nova.
> - **flavor** : son gabarit (vCPU, RAM, disque racine, disque éphémère, swap, propriétés).
> - **key pair** : une clé SSH publique enregistrée, injectée dans l'instance.
> - **service de métadonnées** : une adresse (`169.254.169.254`) où l'instance lit sa configuration ; **config drive** : la même information sur un petit disque.
> - **cloud-init** : lit ces informations et configure l'instance au premier démarrage.
> - **server group** : un ensemble d'instances avec une règle de placement (affinity, anti-affinity).
> - **noVNC** : la console graphique dans le navigateur.
> - **OVN** : Open Virtual Network : le moteur qui réalise les réseaux virtuels d'OpenStack (voir la fiche OVN).
> - **latence** : le délai entre une demande et sa réponse.
> - **hyperviseur** : le logiciel qui fait tourner des machines virtuelles sur un serveur physique (KVM, VMware ESXi).

## Créer une instance

```bash
openstack keypair create --public-key ~/.ssh/id_ed25519.pub fares
openstack server create \
  --flavor m1.small --image rocky-9 \
  --network app-net --security-group web \
  --key-name fares \
  --user-data init.yaml \
  --property role=web \
  --wait web1
openstack floating ip create public
openstack server add floating ip web1 203.0.113.25
ssh rocky@203.0.113.25            # l'utilisateur dépend de l'image : rocky, ubuntu, cloud-user…
```

Variantes : `--boot-from-volume 20` (racine sur un volume Cinder de 20 Go), `--port <id>` (un port préparé avec une IP fixe), `--config-drive true`, `--min 3 --max 3` (plusieurs instances), `--hint group=<server-group-id>`.

## Initialiser avec cloud-init

```yaml
#cloud-config
hostname: web1
timezone: Europe/Paris
users:
  - default
  - name: ops
    groups: wheel
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys: ["ssh-ed25519 AAAA… ops@shop"]
packages: [nginx]
write_files:
  - path: /usr/share/nginx/html/index.html
    content: "<h1>web1</h1>"
runcmd:
  - systemctl enable --now nginx
```

```
Instance ─► 169.254.169.254 ─► (OVN metadata agent sur le compute) ─► Nova metadata API
           ou config drive (disque /dev/sr0 « config-2 »)
cloud-init : lit meta-data (nom, clé, propriétés) + user-data, et l'applique au 1er démarrage
```

Diagnostiquer : `openstack console log show web1` (sortie de cloud-init visible au démarrage) puis, dans l'instance, `/var/log/cloud-init.log`, `/var/log/cloud-init-output.log` et `cloud-init status --long`. Si les métadonnées sont injoignables, la clé SSH n'est pas installée : c'est un problème réseau (fiche « Neutron : OVN sous le capot »).

## Les disques d'une instance

| Disque | Origine | Survit à la suppression ? |
| --- | --- | --- |
| racine éphémère | image, taille de la flavor | non |
| racine sur volume | volume Cinder créé depuis l'image | oui si `delete_on_termination=false` |
| éphémère supplémentaire, swap | flavor | non |
| volumes attachés | Cinder | oui |

Avec Ceph, les disques éphémères sont dans un pool (`vms`) : l'instance peut être **évacuée** vers un autre hôte même si son compute est mort.

## Le cycle de vie

| Action | Effet |
| --- | --- |
| `server stop` / `start` | arrêt et démarrage (ressources gardées sur l'hôte) |
| `server reboot` / `--hard` | redémarrage propre / coupure et relance |
| `server pause` / `suspend` | RAM gardée en mémoire / sur disque |
| `server shelve` / `unshelve` | image + libération des ressources de l'hôte / recréation |
| `server resize --flavor` puis `resize confirm` | changement de gabarit (ou `resize revert`) |
| `server rebuild --image` | réinstallation du disque racine, même ID et IP |
| `server rescue` / `unrescue` | démarrage sur une image de secours, disque d'origine attaché |
| `server lock` / `unlock` | empêcher les actions (sauf admin) |
| `server migrate` / `--live-migration` | changer d'hôte (fiche « Exploiter les nœuds compute ») |

```bash
openstack server show web1 -c status -c OS-EXT-STS:vm_state -c OS-EXT-STS:task_state \
  -c OS-EXT-SRV-ATTR:host -c OS-EXT-SRV-ATTR:instance_name
openstack server event list web1            # historique des actions, avec request-id
openstack server event show web1 req-…      # détail d'une action en échec
openstack console url show --novnc web1
```

## Placer les instances entre elles

```bash
openstack server group create --policy anti-affinity web
openstack server create … --hint group=$(openstack server group show web -f value -c id) web2
```

| Politique | Effet |
| --- | --- |
| `affinity` | toutes sur le même hôte (latence) |
| `anti-affinity` | toutes sur des hôtes différents (résilience) ; échec si impossible |
| `soft-affinity` / `soft-anti-affinity` | si possible |

## Côté hyperviseur

Sur le compute, l'instance est un **domaine libvirt** nommé `instance-0000xxxx` :

```bash
virsh list --all                            # (dans le conteneur nova_libvirt selon le déploiement)
virsh dumpxml instance-000003e8 | less      # disques, interfaces, CPU
ls /var/lib/nova/instances/<uuid>/          # console.log, disques locaux
```

On n'agit **pas** directement avec virsh sur une instance gérée par Nova (sauf diagnostic) : Nova ne serait plus d'accord avec la réalité.

> **À retenir.** `server create` avec flavor, image, réseau, security group, key pair et `--user-data` ; cloud-init lit les métadonnées (169.254.169.254 ou config drive). Racine éphémère ou sur volume Cinder. stop, reboot, shelve, resize + confirm, rebuild, rescue ; `server event list` pour l'historique. Server groups pour l'affinité et l'anti-affinité. Sur le compute, l'instance est un domaine libvirt `instance-…`.
