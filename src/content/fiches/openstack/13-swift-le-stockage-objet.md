---
title: 'Swift : le stockage objet'
chapter: 13
order: 1
duration: 11
tags:
- OpenStack
- EX210
- Swift
cards:
- q: Comment Swift organise-t-il les données ?
  a: 'En trois niveaux : **compte** (un par projet, `AUTH_<id-projet>`), **conteneur** (comme un bucket S3) et **objet** (le fichier et ses métadonnées). L''URL est `/v1/AUTH_<projet>/<conteneur>/<objet>`.'
- q: Quels sont les services d'un cluster Swift ?
  a: Le **proxy** (reçoit les requêtes, vérifie le jeton Keystone, choisit les nœuds), et sur les nœuds de stockage les serveurs **account**, **container** et **object**, plus les **replicators**, **auditors** et **updaters** qui maintiennent la cohérence en tâche de fond.
- q: Qu'est-ce qu'un ring Swift ?
  a: La table qui associe chaque **partition** à des disques, en respectant les zones et régions. Il y a un ring par type (account, container, object, et un par politique de stockage). On le construit avec `swift-ring-builder` et on le distribue à tous les nœuds.
- q: Swift est-il fortement cohérent ?
  a: 'Non, il est **éventuellement cohérent** : une écriture est validée dès qu''une majorité de copies est écrite, et les réplicateurs réparent le reste. Un listing de conteneur peut avoir un léger retard après une écriture.'
- q: Comment exposer Swift en API S3 ?
  a: Avec le middleware **s3api** dans le pipeline du proxy, et des **identifiants EC2** Keystone (`openstack ec2 credentials create`) qui donnent une clé d'accès et un secret compatibles S3.
- q: Qu'est-ce qu'une URL temporaire Swift ?
  a: 'Un lien signé (clé `Temp-URL-Key` posée sur le compte ou le conteneur) qui autorise un GET ou un PUT sur un objet jusqu''à une date, sans jeton Keystone : pratique pour partager un fichier ou laisser un client téléverser.'
quiz:
- q: Tu dois stocker un fichier de 20 Go dans Swift. Comment ?
  options:
  - Directement, il n'y a pas de limite
  - En le découpant en segments avec un manifeste (SLO ou DLO), ce que `openstack object create` ou `swift upload --segment-size` font
  - Impossible
  - En le mettant dans Cinder
  answer: 1
  explain: Un objet simple est limité à 5 Go par défaut ; au-delà on utilise un objet segmenté (Static ou Dynamic Large Object).
- q: Le cloud utilise déjà Ceph. Comment offrir l'API Swift sans déployer Swift ?
  options:
  - Impossible
  - Avec RGW, qui expose l'API Swift et S3 et s'authentifie auprès de Keystone
  - Avec Cinder
  - Avec Manila
  answer: 1
  explain: Beaucoup de clouds (dont Red Hat avec Ceph) utilisent RGW comme point d'accès object-store dans le catalogue Keystone.
level: intermédiaire
---

**Swift** est le service de **stockage objet** d'OpenStack : on y range des fichiers (sauvegardes, images, logs, contenus web) accessibles par HTTP, sans système de fichiers ni disque à attacher. C'est l'équivalent de S3. L'EX210 demande de gérer un stockage objet Swift ; dans beaucoup de clouds réels, l'API Swift est en fait servie par **RGW** de Ceph.

> **Les outils cités dans cette fiche.**
> - **Swift** : le service de stockage objet d'OpenStack.
> - **proxy-server** : le point d'entrée HTTP de Swift.
> - **ring** : la table de placement des données de Swift.
> - **s3api** : le module qui rend Swift compatible avec l'API S3 d'AWS.
> - **SLO / DLO** (Static / Dynamic Large Object) : la façon de stocker un gros fichier en plusieurs segments.
> - **RGW** : la passerelle objet de Ceph, qui parle aussi l'API Swift.
> - **ACL** : une liste de contrôle d'accès : qui a le droit de faire quoi sur une ressource.
> - **EC2** : le service de machines virtuelles d'AWS.

## Comprendre : compte, conteneur, objet

```
https://swift.example.com/v1/AUTH_8f3a…/sauvegardes/2026-10-23/db.sql.gz
                              └ compte ─┘ └ conteneur ┘ └──── objet ────┘
```

Le « / » dans un nom d'objet n'est pas un dossier : c'est un caractère comme un autre, que les outils affichent comme une arborescence (option `--prefix`). Chaque conteneur peut porter des métadonnées, des ACL (lecture publique, accès d'un autre projet), un quota et une politique de stockage.

## Utiliser Swift

```bash
openstack container create sauvegardes
openstack object create sauvegardes db.sql.gz           # téléverser
openstack object list sauvegardes --prefix 2026-10/
openstack object save sauvegardes db.sql.gz             # télécharger
openstack object show sauvegardes db.sql.gz
openstack container show sauvegardes                    # nombre d'objets, octets
openstack container set --property Read-ACL=".r:*,.rlistings" public   # conteneur public

swift upload --segment-size 1G sauvegardes gros.tar     # gros fichier en segments (SLO)
swift post -m "Temp-URL-Key:secret" && swift tempurl GET 3600 /v1/AUTH_…/sauvegardes/db.sql.gz secret
```

Pour les outils S3 (rclone, aws cli, restic) :

```bash
openstack ec2 credentials create      # donne access et secret
aws --endpoint-url https://swift.example.com s3 ls
```

## L'architecture d'un cluster

```
clients ──► load balancer ──► proxy-server (authtoken Keystone, s3api, tempurl, ratelimit)
                                  │ ring
                 ┌────────────────┼────────────────┐
              nœud zone 1      nœud zone 2      nœud zone 3
          account / container / object servers + replicator, auditor, updater
```

- **Les rings** découpent l'espace en 2^n **partitions** réparties sur les disques selon leur poids. Trois copies par défaut, chacune dans une **zone** différente (baie, salle), voire une **région** différente.
- **Les politiques de stockage** permettent plusieurs rings objet : réplication ×3 pour l'usage courant, **erasure coding** pour l'archive.
- **Les processus de fond** : le *replicator* recopie ce qui manque, l'*auditor* relit les données pour détecter la corruption (bit rot), l'*updater* rattrape les mises à jour de listing différées.

```bash
swift-ring-builder object.builder create 10 3 1          # 2^10 partitions, 3 copies, 1 h entre déplacements
swift-ring-builder object.builder add r1z1-10.0.0.11:6200/sdb 100
swift-ring-builder object.builder rebalance
swift-recon --replication --disk                          # état de réplication et remplissage
```

Les fichiers `*.ring.gz` doivent être **identiques** sur tous les proxies et nœuds : une différence crée des objets « introuvables ».

## Swift ou RGW

| | Swift | Ceph RGW |
| --- | --- | --- |
| stockage | ses propres disques et rings | le cluster Ceph |
| cohérence | éventuelle | forte (RADOS) |
| API | Swift native, S3 par s3api | S3 native, Swift compatible |
| intérêt | très grande échelle, multi-région | un seul stockage à opérer quand on a déjà Ceph |

Dans les deux cas, Keystone fournit l'authentification et le catalogue annonce un endpoint `object-store`.

> **À retenir.** Swift stocke des objets par HTTP : compte (projet), conteneur, objet. Le proxy authentifie et route grâce aux rings ; les serveurs account, container et object stockent ; replicator et auditor maintiennent la cohérence, qui est éventuelle. Gros fichiers en segments (SLO), partage par ACL ou URL temporaire, compatibilité S3 par s3api et identifiants EC2. Avec Ceph, RGW sert souvent l'API Swift à sa place.
