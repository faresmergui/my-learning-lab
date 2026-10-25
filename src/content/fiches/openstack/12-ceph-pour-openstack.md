---
title: Ceph pour OpenStack
chapter: 12
order: 1
duration: 14
tags:
- OpenStack
- EX210
- Ceph
cards:
- q: Quels sont les démons principaux de Ceph ?
  a: '**MON** (moniteurs : la carte du cluster, en nombre impair pour le quorum), **MGR** (gestionnaire : métriques, tableau de bord, orchestrateur cephadm), **OSD** (un par disque : stocke les données, réplique, se répare), **RGW** (passerelle objet S3/Swift) et **MDS** (métadonnées de CephFS).'
- q: Que sont un pool, un placement group et CRUSH ?
  a: Un **pool** est un espace logique avec sa règle de protection (réplication ×3 ou erasure coding). Il est découpé en **placement groups (PG)**. L'algorithme **CRUSH** calcule, sans table centrale, sur quels OSD vit chaque PG, en respectant les domaines de panne (hôte, baie, salle).
- q: Quels pools Ceph utilise un OpenStack classique ?
  a: '`images` (Glance), `volumes` (Cinder), `vms` (disques éphémères de Nova), `backups` (cinder-backup), plus les pools de RGW si Swift/S3 passe par Ceph. Chaque service a un utilisateur cephx limité à ses pools.'
- q: Pourquoi lancer une instance depuis une image est quasi instantané avec Ceph ?
  a: 'Parce que Glance stocke l''image en RBD (format **raw**) et que Nova ou Cinder créent le disque comme un **clone copy-on-write** de son snapshot protégé : rien n''est copié, seuls les blocs modifiés s''écrivent ensuite.'
- q: Que signifient HEALTH_OK, HEALTH_WARN et HEALTH_ERR ?
  a: '`HEALTH_OK` : tout va bien. `HEALTH_WARN` : dégradé mais les données sont servies (OSD down, PG en reconstruction, cluster presque plein…). `HEALTH_ERR` : problème grave (PG inactifs ou incomplets, OSD pleins) qui peut bloquer des écritures. `ceph health detail` dit lequel.'
- q: Qu'est-ce qu'un déploiement hyperconvergé (HCI) ?
  a: Les **mêmes nœuds** sont à la fois computes Nova et serveurs OSD Ceph. On économise du matériel, mais il faut **réserver** CPU et mémoire aux OSD (`reserved_host_memory_mb`, `cpu_allocation_ratio` adaptés) pour que les VM ne les étouffent pas.
- q: Que faire avant d'arrêter un nœud OSD pour maintenance ?
  a: '`ceph osd set noout` pour que Ceph ne lance pas une reconstruction massive pendant l''arrêt, faire la maintenance, redémarrer, attendre que les PG soient `active+clean`, puis `ceph osd unset noout`.'
quiz:
- q: Avec une réplication ×3 et `min_size 2`, deux OSD de deux hôtes différents tombent. Que se passe-t-il pour un PG qui avait ses copies sur ces deux OSD ?
  options:
  - Les données sont perdues
  - 'Le PG n''a plus qu''une copie : il passe sous min_size et bloque les écritures jusqu''à la reconstruction'
  - Rien du tout
  - Le cluster s'arrête entièrement
  answer: 1
  explain: Une copie reste, donc rien n'est perdu, mais sous `min_size` Ceph refuse les écritures sur ce PG pour ne pas risquer la cohérence. Il reconstruit les copies manquantes sur d'autres OSD.
- q: Le cluster affiche `nearfull` à 85 %. Quel est le vrai risque ?
  options:
  - Aucun, c'est informatif
  - Atteindre `full` (95 % par défaut) bloque toutes les écritures, et une panne d'OSD ferait monter le remplissage des autres
  - Ceph supprime les vieux snapshots
  - Les performances doublent
  answer: 1
  explain: 'Il faut toujours garder de la place pour absorber la perte d''un hôte : ajouter des disques ou faire du ménage avant d''atteindre full.'
level: intermédiaire
---

**Ceph** est le stockage le plus utilisé sous OpenStack : un seul cluster distribué fournit à la fois le bloc (RBD) pour Glance, Cinder et Nova, l'objet (RGW) à la place de Swift, et un système de fichiers partagé (CephFS) pour Manila. L'EX210 demande de savoir gérer un stockage Ceph, intégré ou dédié. Au quotidien, c'est souvent là que se cachent les causes des lenteurs et des volumes bloqués.

> **Les outils cités dans cette fiche.**
> - **Ceph** : un système de stockage distribué, libre, qui se réplique et se répare seul.
> - **RBD** (RADOS Block Device) : des disques virtuels stockés dans Ceph ; **RADOS** est la couche objet de base de Ceph.
> - **RGW** (RADOS Gateway) : la passerelle qui expose Ceph en S3 et en Swift.
> - **CephFS** : le système de fichiers partagé de Ceph.
> - **cephadm** : l'outil qui déploie et gère Ceph dans des conteneurs ; **cephx** : son système d'authentification par clés.
> - **OSD** (Object Storage Daemon) : le démon qui gère un disque ; **MON** et **MGR** : moniteurs et gestionnaire du cluster.
> - **erasure coding** : une protection par calcul de parité (comme un RAID 5/6 distribué), moins gourmande en place que la réplication.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.
> - **latence** : le délai entre une demande et sa réponse.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **quorum** : la majorité de membres nécessaire pour qu'un cluster prenne des décisions (2 sur 3).

## Comprendre : comment Ceph place les données

<!-- schema:crush -->
<figure class="diagram"><svg viewBox="0 0 680 290" role="img" aria-label="Comment Ceph place un objet" style="--minw:560px"><defs><marker id="g6-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g6-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g6-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g6-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="40" y="24" width="190" height="54" rx="9"/></g><text x="135.0" y="48.0" class="dg-t" text-anchor="middle" style="--d:0">objet</text><text x="135.0" y="66.0" class="dg-s" text-anchor="middle" style="--d:0">4 Mo d&#x27;un disque RBD</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="300" y="24" width="190" height="54" rx="9"/></g><text x="395.0" y="48.0" class="dg-t" text-anchor="middle" style="--d:1">placement group</text><text x="395.0" y="66.0" class="dg-s" text-anchor="middle" style="--d:1">du pool « volumes »</text><path d="M230 51 L298 51" class="dg-l c" marker-end="url(#g6-c)"/><text x="264.0" y="43.0" class="dg-s" text-anchor="middle">hachage</text><text x="506" y="46" class="dg-s" text-anchor="start">CRUSH : 3 copies,</text><text x="506" y="60" class="dg-s" text-anchor="start">une par hôte</text><rect x="14" y="136" width="208" height="96" rx="12" class="dg-zone "/><text x="26" y="154" class="dg-zl" text-anchor="start">hôte A</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="38" y="164" width="160" height="48" rx="9"/></g><text x="118.0" y="185.0" class="dg-t" text-anchor="middle" style="--d:2">OSD.4</text><text x="118.0" y="203.0" class="dg-s" text-anchor="middle" style="--d:2">une copie</text><path d="M395 78 L395 110 L118 110 L118 162" class="dg-l c" marker-end="url(#g6-c)"/><rect x="236" y="136" width="208" height="96" rx="12" class="dg-zone "/><text x="248" y="154" class="dg-zl" text-anchor="start">hôte B</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="260" y="164" width="160" height="48" rx="9"/></g><text x="340.0" y="185.0" class="dg-t" text-anchor="middle" style="--d:3">OSD.11</text><text x="340.0" y="203.0" class="dg-s" text-anchor="middle" style="--d:3">une copie</text><path d="M395 78 L395 110 L340 110 L340 162" class="dg-l c" marker-end="url(#g6-c)"/><rect x="458" y="136" width="208" height="96" rx="12" class="dg-zone "/><text x="470" y="154" class="dg-zl" text-anchor="start">hôte C</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="482" y="164" width="160" height="48" rx="9"/></g><text x="562.0" y="185.0" class="dg-t" text-anchor="middle" style="--d:4">OSD.19</text><text x="562.0" y="203.0" class="dg-s" text-anchor="middle" style="--d:4">une copie</text><path d="M395 78 L395 110 L562 110 L562 162" class="dg-l c" marker-end="url(#g6-c)"/><text x="340" y="266" class="dg-s" text-anchor="middle" style="--d:5">perdre un hôte ne perd aucune donnée : Ceph recrée la copie manquante ailleurs</text></svg><figcaption>Personne ne garde de table « objet → disque » : CRUSH recalcule la position à chaque accès.</figcaption></figure>
<!-- /schema:crush -->

Il n'y a pas de serveur central qui sait « où est quoi » : chaque client calcule la position avec la carte du cluster que lui donnent les **MON**. Quand un OSD tombe, les PG concernés passent en `degraded`, puis Ceph recrée les copies ailleurs (`recovering`, `backfilling`) jusqu'à revenir en `active+clean`.

| Protection | Place utilisée | Usage |
| --- | --- | --- |
| réplication ×3 (`size 3`, `min_size 2`) | 300 % | volumes et VM (latence faible) |
| erasure coding 4+2 | 150 % | objet RGW, sauvegardes, archives |

## Ceph et OpenStack : qui utilise quoi

| Service | Pool | Utilisateur cephx | Ce qu'il fait |
| --- | --- | --- | --- |
| Glance | `images` | `client.glance` | stocke les images en RBD (format **raw** pour le clonage) |
| Cinder | `volumes` | `client.cinder` (ou `openstack`) | crée, clone, étend les volumes |
| Nova | `vms` | même clé que Cinder | disques éphémères des instances |
| cinder-backup | `backups` | `client.cinder-backup` | sauvegardes |
| RGW | `default.rgw.*` | — | API S3 et Swift, authentifiée par Keystone |

Le compute ne passe par aucun serveur intermédiaire : **libvirt** parle directement aux OSD avec la clé cephx, déclarée comme secret libvirt (`virsh secret-list`). C'est pour cela que la **migration à chaud** est simple avec Ceph : le disque est déjà partagé.

## Les commandes de santé

```bash
ceph -s                      # vue d'ensemble : santé, MON, OSD, PG, I/O
ceph health detail           # le détail de chaque alerte
ceph osd tree                # OSD par hôte, up/down, in/out
ceph df                      # remplissage global et par pool
ceph osd df tree             # remplissage par OSD (déséquilibres)
ceph pg stat                 # PG active+clean ou non
ceph orch ps                 # (cephadm) démons et leur état
rbd -p volumes ls            # images RBD du pool volumes
rbd info volumes/volume-<id> # détail d'un volume Cinder
rbd status volumes/volume-<id>   # qui l'a ouvert (watchers) : utile pour un volume « bloqué »
```

| Alerte fréquente | Sens | Réaction |
| --- | --- | --- |
| `OSD_DOWN` | un disque ou un hôte ne répond plus | vérifier le démon, le disque (`journalctl`, `smartctl`) |
| `PG_DEGRADED` | des copies manquent | attendre la reconstruction, surveiller |
| `OSD_NEARFULL` / `POOL_NEARFULL` | 85 % atteint | ajouter de la capacité, nettoyer |
| `SLOW_OPS` | requêtes lentes sur un OSD | disque malade, réseau saturé |
| `MON_DOWN` | un moniteur perdu | le quorum tient tant qu'une majorité reste |
| `PG_AVAILABILITY` | PG inactifs | grave : écritures bloquées sur ces données |

## Dédié ou hyperconvergé

- **Ceph dédié** : des serveurs de stockage à part. Plus simple à dimensionner, une panne de stockage n'emporte pas des VM. C'est le choix des grands clouds.
- **Hyperconvergé (HCI)** : OSD et Nova sur les mêmes nœuds. Moins de serveurs, mais il faut réserver des ressources aux OSD (environ 1 cœur et 5 Go de mémoire par OSD) dans `nova.conf` (`reserved_host_memory_mb`) et éviter de surcharger les computes.
- **Ceph externe** : un cluster existant, géré par une autre équipe ; OpenStack reçoit seulement `ceph.conf` et les clés.

## Maintenance sans drame

```bash
ceph osd set noout           # avant d'arrêter un hôte : pas de reconstruction inutile
# … maintenance, redémarrage …
ceph -s                      # attendre active+clean
ceph osd unset noout
ceph orch host maintenance enter stor3   # (cephadm) même idée, gérée par l'orchestrateur
ceph osd out 17              # vider un disque avant de le retirer (les données migrent)
```

> **À retenir.** Ceph place les données par CRUSH dans des PG sur des OSD, sans serveur central ; MON pour la carte, MGR pour la gestion. OpenStack utilise un pool par service (images, volumes, vms, backups) et une clé cephx par service. Images en raw pour les clones copy-on-write, disque partagé pour la migration à chaud. `ceph -s`, `ceph health detail`, `ceph osd tree`, `ceph df` sont les premiers réflexes. Garder de la marge avant `nearfull`, poser `noout` avant une maintenance, réserver des ressources aux OSD en hyperconvergé.
