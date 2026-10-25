---
title: Disques, montages et LVM
chapter: 6
order: 1
duration: 10
level: intermédiaire
tags:
- LFCS
cards:
- q: Comment voir les disques, leurs partitions et où ils sont montés ?
  a: '`lsblk -f` : arbre des disques avec système de fichiers, UUID et point de montage.'
- q: Pourquoi utiliser l'UUID plutôt que `/dev/sdb1` dans `/etc/fstab` ?
  a: Les noms `/dev/sdX` peuvent **changer** d'un démarrage à l'autre. L'UUID est lié au système de fichiers lui-même.
- q: À quoi sert l'option `nofail` dans fstab ?
  a: À ne pas bloquer le démarrage si ce disque est absent. Sans elle, un disque de données manquant peut laisser le serveur en mode urgence.
- q: Quelles sont les trois couches de LVM ?
  a: '**PV** (volume physique, un disque ou une partition), **VG** (groupe de volumes, qui réunit des PV), **LV** (volume logique, découpé dans le VG et formaté).'
- q: Comment agrandir un LV et son système de fichiers en une commande ?
  a: '`lvextend -r -L +10G /dev/vg_data/lv_app`. Le `-r` redimensionne aussi le système de fichiers (ext4 ou XFS).'
- q: Pourquoi `df` et `du` donnent-ils parfois des chiffres différents ?
  a: '`df` voit l''espace occupé sur le système de fichiers, y compris par des fichiers **supprimés mais encore ouverts**. `du` ne compte que les fichiers visibles. `lsof +L1` trouve la différence.'
- q: 'Disque plein mais `du` ne trouve rien : cause probable ?'
  a: Un **fichier supprimé encore ouvert** par un processus. `lsof +L1` le montre, redémarrer le service libère l'espace.
- q: '`df -h` montre de la place mais impossible de créer un fichier ?'
  a: 'Plus d''**inodes** libres : `df -i`. Souvent des millions de petits fichiers (cache, sessions).'
- q: Peut-on réduire un système de fichiers xfs ?
  a: '**Non**, xfs ne peut qu''être agrandi. ext4 peut être réduit hors ligne.'
- q: Pourquoi utiliser l'UUID dans /etc/fstab ?
  a: Les noms `/dev/sdX` peuvent **changer d'ordre** au démarrage. L'UUID identifie le système de fichiers lui-même.
quiz:
- q: Tu ajoutes une ligne dans fstab. Comment la tester sans redémarrer ?
  options:
  - '`mount -a` (et `findmnt --verify`)'
  - '`systemctl restart fstab`'
  - '`fsck -A`'
  - Il faut redémarrer
  answer: 0
  explain: '`mount -a` monte tout ce qui ne l''est pas encore : une erreur apparaît tout de suite, au lieu de bloquer le prochain démarrage.'
- q: Peut-on réduire un système de fichiers XFS ?
  options:
  - Oui, avec xfs_growfs -D
  - Non, XFS ne peut qu'être agrandi
  - Oui, avec lvreduce -r
  - Seulement s'il est démonté
  answer: 1
  explain: ext4 peut être réduit (démonté), XFS non. Pour récupérer de la place, il faut sauvegarder, recréer et restaurer.
---

Un disque ne sert à rien tant qu'il n'est pas **formaté** (un système de fichiers, comme ext4 ou xfs) et **monté** (rattaché à un dossier de l'arborescence). **LVM** (Logical Volume Manager) ajoute une couche souple entre les deux : il regroupe des disques et les redécoupe en volumes qu'on peut agrandir à chaud.


> **Les termes et outils cités dans cette fiche.**
> - **PV** : un volume persistant : un espace de stockage mis à disposition du cluster.
> - **RHEL** : Red Hat Enterprise Linux, la distribution Linux d'entreprise de Red Hat.

## Voir ce qu'on a

```bash
lsblk -f               # disques, partitions, FS, UUID, montages
df -hT                 # espace par système de fichiers
du -xh / --max-depth=1 | sort -h
findmnt                # arbre des montages
```

## Ajouter un disque de données

```bash
mkfs.xfs /dev/sdb
mkdir -p /data
blkid /dev/sdb         # récupérer l'UUID
echo 'UUID=3f2c…  /data  xfs  defaults,nofail  0 2' >> /etc/fstab
mount -a && df -h /data
```

## LVM

<!-- schema:lvm -->
<figure class="diagram"><svg viewBox="0 0 680 280" role="img" aria-label="Les trois couches de LVM" style="--minw:560px"><defs><marker id="g5-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g5-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g5-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g5-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="120" y="14" width="190" height="44" rx="9"/></g><text x="215.0" y="33.0" class="dg-t" text-anchor="middle" style="--d:0">/dev/sdb</text><text x="215.0" y="51.0" class="dg-s" text-anchor="middle" style="--d:0">disque</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="120" y="80" width="190" height="44" rx="9"/></g><text x="215.0" y="99.0" class="dg-t" text-anchor="middle" style="--d:1">PV /dev/sdb</text><text x="215.0" y="117.0" class="dg-s" text-anchor="middle" style="--d:1">pvcreate</text><path d="M215 58 L215 78" class="dg-l" marker-end="url(#g5-n)"/><path d="M215 124 L215 144" class="dg-l c" marker-end="url(#g5-c)"/><g class="dg-box dg-pop" style="--d:0"><rect x="370" y="14" width="190" height="44" rx="9"/></g><text x="465.0" y="33.0" class="dg-t" text-anchor="middle" style="--d:0">/dev/sdc</text><text x="465.0" y="51.0" class="dg-s" text-anchor="middle" style="--d:0">disque</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="370" y="80" width="190" height="44" rx="9"/></g><text x="465.0" y="99.0" class="dg-t" text-anchor="middle" style="--d:1">PV /dev/sdc</text><text x="465.0" y="117.0" class="dg-s" text-anchor="middle" style="--d:1">pvcreate</text><path d="M465 58 L465 78" class="dg-l" marker-end="url(#g5-n)"/><path d="M465 124 L465 144" class="dg-l c" marker-end="url(#g5-c)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="120" y="146" width="440" height="44" rx="9"/></g><text x="340.0" y="165.0" class="dg-t" text-anchor="middle" style="--d:2">VG vg_data</text><text x="340.0" y="183.0" class="dg-s" text-anchor="middle" style="--d:2">vgcreate : un seul « pool » de 2 disques</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="120" y="214" width="260" height="50" rx="9"/></g><text x="250.0" y="236.0" class="dg-t" text-anchor="middle" style="--d:3">LV lv_app → /srv/app</text><text x="250.0" y="254.0" class="dg-s" text-anchor="middle" style="--d:3">lvcreate, mkfs, mount</text><g class="dg-box dg-pop" style="--d:3"><rect x="392" y="214" width="168" height="50" rx="9"/></g><text x="476.0" y="236.0" class="dg-t" text-anchor="middle" style="--d:3">LV lv_logs</text><text x="476.0" y="254.0" class="dg-s" text-anchor="middle" style="--d:3">→ /var/log/app</text><path d="M250 190 L250 212" class="dg-l c" marker-end="url(#g5-c)"/><path d="M476 190 L476 212" class="dg-l c" marker-end="url(#g5-c)"/><text x="20" y="40" class="dg-zl" text-anchor="start">matériel</text><text x="20" y="106" class="dg-zl" text-anchor="start">PV</text><text x="20" y="172" class="dg-zl" text-anchor="start">VG</text><text x="20" y="243" class="dg-zl" text-anchor="start">LV</text><text x="620" y="172" class="dg-s" text-anchor="middle">on peut</text><text x="620" y="186" class="dg-s" text-anchor="middle">agrandir</text><text x="620" y="243" class="dg-ct" text-anchor="middle">lvextend -r</text></svg><figcaption>On agrandit un LV à chaud, en ajoutant un disque au VG si besoin.</figcaption></figure>
<!-- /schema:lvm -->

```bash
pvcreate /dev/sdb /dev/sdc
vgcreate vg_data /dev/sdb /dev/sdc
lvcreate -n lv_app -L 50G vg_data
mkfs.ext4 /dev/vg_data/lv_app

# Plus tard, agrandir à chaud :
lvextend -r -L +20G /dev/vg_data/lv_app
pvs; vgs; lvs
```

## Comprendre la pile

Entre le disque physique et le dossier `/data`, il y a plusieurs couches. Les connaître aide à savoir **où** agir quand il manque de la place :

| Couche | Exemple | Outil |
| --- | --- | --- |
| Disque | `/dev/sdb`, `/dev/nvme0n1` | `lsblk` |
| Partition (optionnelle) | `/dev/sdb1` | `fdisk`, `parted`, `growpart` |
| LVM (optionnel) | PV → VG → LV | `pvs`, `vgs`, `lvs` |
| Système de fichiers | ext4, xfs | `mkfs`, `resize2fs`, `xfs_growfs` |
| Point de montage | `/data` | `mount`, `/etc/fstab` |

Agrandir un disque cloud, c'est agrandir **chaque couche** du bas vers le haut : le volume chez le fournisseur, puis la partition, puis le PV (`pvresize`), le LV, et enfin le système de fichiers. `lvextend -r` fait les deux dernières étapes d'un coup.

## ext4 ou xfs ?

- **ext4** : polyvalent, se réduit hors ligne si besoin.
- **xfs** : excellent sur les gros fichiers et les gros volumes, par défaut sur RHEL. Il **ne se réduit pas** : on ne peut que l'agrandir.

## Disque plein : la méthode

1. `df -h` : quel système de fichiers est plein ?
2. `df -i` : ce n'est peut-être pas l'espace mais les **inodes** (des millions de petits fichiers).
3. `du -xh /var --max-depth=1 | sort -h` : où est l'espace ? `-x` reste sur le même système de fichiers.
4. Toujours plein alors que `du` ne trouve rien ? Un processus garde un **fichier supprimé ouvert** : `lsof +L1`, puis redémarrer le service concerné.

## Pourquoi l'UUID dans fstab

Les noms `/dev/sdb`, `/dev/sdc` peuvent **changer d'ordre** au redémarrage, surtout sur le cloud. L'UUID (ou un label) identifie le système de fichiers lui-même, pas la place du disque. Le chiffre final de la ligne fstab (`0 2`) règle l'ordre de vérification au démarrage.

> **Piège classique.** Une erreur dans `/etc/fstab` peut empêcher le serveur de démarrer. Teste toujours avec `mount -a` avant de redémarrer, et mets `nofail` sur les disques non essentiels.

> **À retenir.** Disque, partition, LVM, système de fichiers, montage : pour agrandir, on agrandit chaque couche de bas en haut. Monte par UUID avec `nofail`, teste `/etc/fstab` avec `mount -a`, et face à un disque plein, pense aux inodes (`df -i`) et aux fichiers supprimés encore ouverts (`lsof +L1`).
