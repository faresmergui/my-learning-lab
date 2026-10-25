---
title: EBS, EFS et FSx
chapter: 7
order: 1
duration: 10
tags:
- AWS SAA
- EBS
- EFS
- stockage
cards:
- q: Différence entre les volumes EBS gp3 et io2 ?
  a: '**gp3** : SSD général, 3 000 IOPS et 125 Mo/s inclus, réglables indépendamment de la taille ; le choix par défaut. **io2 Block Express** : IOPS provisionnées très élevées (jusqu''à 256 000), latence stable, durabilité 99,999 %, pour les bases critiques.'
- q: Comment déplacer un volume EBS vers une autre AZ ou région ?
  a: Faire un **snapshot** (stocké dans S3, régional), le **copier** dans l'autre région si besoin, puis créer un nouveau volume à partir du snapshot dans l'AZ voulue.
- q: Qu'est-ce qu'EFS ?
  a: '**Elastic File System** : un système de fichiers **NFS** managé, monté en même temps par de nombreuses instances, conteneurs ou Lambda, sur plusieurs AZ, qui grandit et rétrécit tout seul. Linux uniquement.'
- q: Quand choisir FSx ?
  a: 'Quand il faut un système de fichiers précis : **FSx for Windows File Server** (SMB, Active Directory), **FSx for Lustre** (calcul haute performance, lié à S3), **FSx for NetApp ONTAP** (NFS, SMB, iSCSI, migration de NetApp), **FSx for OpenZFS**.'
- q: Qu'est-ce qu'EBS Multi-Attach ?
  a: La possibilité d'attacher **un volume io1/io2** à plusieurs instances de la même AZ. L'application doit gérer elle-même les écritures concurrentes (système de fichiers de cluster).
- q: À quoi sert AWS Backup ?
  a: À centraliser les **plans de sauvegarde** (fréquence, rétention, copie vers une autre région ou un autre compte) pour EBS, EC2, RDS, DynamoDB, EFS, FSx, S3… avec des coffres verrouillables (Vault Lock).
quiz:
- q: Des dizaines d'instances Linux dans plusieurs AZ doivent lire et écrire les mêmes fichiers. Quel service ?
  options:
  - Un volume EBS partagé
  - EFS
  - Instance store
  - S3 Glacier
  answer: 1
  explain: EFS est fait pour un accès partagé, multi-AZ, en NFS. EBS Multi-Attach reste limité à une AZ et demande un système de fichiers de cluster.
- q: Des serveurs Windows ont besoin d'un partage SMB intégré à Active Directory. Quel service ?
  options:
  - EFS
  - FSx for Windows File Server
  - S3
  - FSx for Lustre
  answer: 1
  explain: EFS ne parle que NFS et ne fonctionne pas avec Windows.
- q: Un volume gp2 de 100 Go manque d'IOPS. Solution simple et économique ?
  options:
  - Passer en io2
  - Passer en gp3 et augmenter les IOPS sans agrandir le volume
  - Créer un RAID 0 d'instance store
  - Doubler la taille
  answer: 1
  explain: En gp2, les IOPS dépendaient de la taille ; gp3 les découple, et coûte environ 20 % moins cher. Le changement se fait à chaud.
level: intermédiaire
---

S3 stocke des objets. Mais un système d'exploitation, une base de données ou une application qui écrit des fichiers ont besoin d'un **disque** (stockage bloc) ou d'un **système de fichiers partagé**. AWS propose EBS pour le premier, EFS et FSx pour le second.

> **Les outils cités dans cette fiche.**
> - **EBS** (Elastic Block Store) : un disque réseau attaché à une instance, dans une AZ.
> - **snapshot** : une copie incrémentale d'un volume EBS, stockée par AWS de façon régionale.
> - **IOPS** : le nombre d'opérations de lecture ou d'écriture par seconde qu'un disque accepte. **débit** : le volume de données par seconde (Mo/s).
> - **EFS** (Elastic File System) : un partage de fichiers NFS managé, multi-AZ, pour Linux.
> - **FSx** : une famille de systèmes de fichiers managés spécialisés (Windows, Lustre, NetApp ONTAP, OpenZFS).
> - **SMB** : le protocole de partage de fichiers de Windows ; **NFS** : celui du monde Linux.
> - **AWS Backup** : le service qui centralise les sauvegardes de nombreux services.
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **latence** : le délai entre une demande et sa réponse.
> - **KMS** : le service de gestion des clés de chiffrement.
> - **EC2** : le service de machines virtuelles d'AWS.
> - **ECS** : le service d'exécution de conteneurs d'AWS.
> - **EKS** : le service Kubernetes managé d'AWS.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).

## EBS : le disque des instances

Un volume EBS vit dans **une AZ** et s'attache à une instance de cette AZ. Il est répliqué dans l'AZ, mais une panne de l'AZ le rend indisponible : la résilience vient des snapshots et des architectures multi-AZ.

| Type | Nature | Performance | Usage |
| --- | --- | --- | --- |
| **gp3** | SSD | 3 000 IOPS et 125 Mo/s inclus, plus si on les provisionne | défaut : systèmes, la plupart des bases |
| gp2 | SSD (ancien) | IOPS liés à la taille | à migrer vers gp3 |
| **io2 Block Express** | SSD à IOPS provisionnées | jusqu'à 256 000 IOPS | bases critiques, latence stable, Multi-Attach |
| **st1** | disque dur, débit | jusqu'à 500 Mo/s | big data, logs, lectures séquentielles |
| **sc1** | disque dur froid | le moins cher | données rarement lues |

Les disques durs (st1, sc1) ne peuvent pas servir de volume de démarrage.

Opérations courantes :

- agrandir un volume ou changer son type **à chaud** (Elastic Volumes), puis étendre le système de fichiers (`growpart`, `resize2fs` ou `xfs_growfs`) ;
- **snapshot** incrémental : seuls les blocs modifiés sont stockés ; on crée un volume à partir d'un snapshot dans n'importe quelle AZ de la région, ou on le copie dans une autre région ;
- **chiffrement** avec KMS : un volume créé depuis un snapshot chiffré est chiffré ; pour chiffrer un volume existant, on passe par un snapshot copié avec chiffrement. On peut activer le **chiffrement par défaut** pour tout le compte ;
- **Data Lifecycle Manager** ou **AWS Backup** pour automatiser les snapshots.

## EFS : un partage NFS élastique

```bash
sudo mount -t efs -o tls fs-0abc1234:/ /mnt/partage    # avec l'utilitaire amazon-efs-utils
```

- monté par des milliers de clients à la fois (EC2, ECS, EKS, Lambda), sur toutes les AZ de la région ;
- pas de taille à prévoir : on paie ce qui est stocké ;
- classes **Standard**, **Infrequent Access** et **Archive** avec cycle de vie, comme S3 ;
- modes de débit **elastic** (recommandé, suit la demande), **bursting** ou **provisioned** ;
- variante **One Zone** moins chère, sur une seule AZ ;
- accès contrôlés par security groups (port NFS 2049), IAM et **access points** (un dossier et un utilisateur imposés par application).

EFS est plus cher au Go que S3 ou EBS : on le réserve aux données qui doivent vraiment être **partagées en fichiers**.

## FSx : quand il faut un système de fichiers précis

| Variante | Protocole | Pour |
| --- | --- | --- |
| FSx for Windows File Server | SMB, Active Directory | partages Windows, DFS |
| FSx for Lustre | Lustre (client Linux) | calcul haute performance, ML ; se relie à un bucket S3 |
| FSx for NetApp ONTAP | NFS, SMB, iSCSI | migrer depuis NetApp, multi-protocole, snapshots, clones |
| FSx for OpenZFS | NFS | migrer depuis ZFS, snapshots et clones rapides |

## Choisir

```
Disque d'une instance, une base sur EC2 ............ EBS (gp3, io2 si critique)
Fichiers partagés Linux, multi-AZ .................. EFS
Partages Windows ................................... FSx for Windows
Calcul haute performance sur des données S3 ........ FSx for Lustre
Objets, sauvegardes, données d'analyse ............. S3
Cache temporaire très rapide ....................... instance store
```

## Sauvegarder

**AWS Backup** applique des **plans de sauvegarde** (toutes les 4 heures, rétention 35 jours, copie mensuelle dans une autre région) à des ressources choisies par tag. Les sauvegardes vont dans des **coffres** ; avec **Vault Lock**, même un administrateur ne peut pas les supprimer avant la fin de la rétention, ce qui protège contre les rançongiciels.

> **À retenir.** EBS est le disque d'une instance, lié à une AZ ; gp3 par défaut, io2 pour la performance garantie, et les snapshots pour changer d'AZ ou de région. EFS est un partage NFS multi-AZ pour Linux ; FSx couvre Windows, Lustre, NetApp et ZFS. AWS Backup centralise les sauvegardes, avec copie dans une autre région et coffres verrouillés.
