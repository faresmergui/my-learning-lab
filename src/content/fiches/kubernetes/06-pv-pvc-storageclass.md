---
title: PV, PVC et StorageClass
chapter: 6
order: 1
duration: 9
level: intermédiaire
tags:
- CKA
cards:
- q: 'Quel est le rôle de chacun : PV, PVC, StorageClass ?'
  a: Le **PV** est un volume réel. Le **PVC** est une demande de stockage faite par une appli. La **StorageClass** décrit comment créer des PV à la demande (provisionnement dynamique).
- q: Que signifient RWO, ROX, RWX et RWOP ?
  a: '`ReadWriteOnce` : en écriture par **un nœud**. `ReadOnlyMany` : en lecture par plusieurs nœuds. `ReadWriteMany` : en écriture par plusieurs nœuds. `ReadWriteOncePod` : en écriture par **un seul pod**.'
- q: 'Différence entre `reclaimPolicy: Delete` et `Retain` ?'
  a: À la suppression du PVC, `Delete` supprime aussi le volume et ses données. `Retain` garde le PV et ses données, qu'il faudra récupérer à la main.
- q: 'Pourquoi utiliser `volumeBindingMode: WaitForFirstConsumer` ?'
  a: Pour créer le volume **après** le choix du nœud. Sinon, le disque peut être créé dans une zone où le pod ne pourra pas être planifié.
- q: Comment agrandir un PVC ?
  a: 'Si la StorageClass a `allowVolumeExpansion: true`, on augmente `spec.resources.requests.storage` du PVC. On ne peut pas réduire un volume.'
quiz:
- q: Ton PVC reste en `Pending`. Quelle cause n'est pas plausible ?
  options:
  - Aucune StorageClass par défaut et aucune n'est précisée
  - Le mode `WaitForFirstConsumer` attend qu'un pod l'utilise
  - Aucun PV statique ne correspond à la taille ou au mode d'accès
  - Le pod a une readiness probe qui échoue
  answer: 3
  explain: La readiness probe n'a rien à voir avec le stockage. `kubectl describe pvc` donne la raison exacte dans les événements.
- q: Un Deployment de 3 réplicas sur 3 nœuds doit partager le même volume en écriture. Quel mode d'accès faut-il ?
  options:
  - ReadWriteOnce
  - ReadWriteMany
  - ReadOnlyMany
  - ReadWriteOncePod
  answer: 1
  explain: Seul RWX permet l'écriture depuis plusieurs nœuds. Il faut un stockage qui le supporte (NFS, CephFS, EFS…). Un disque bloc type EBS ne le permet pas.
- q: Tu supprimes par erreur le PVC d'une base de prod, avec une StorageClass en `Delete`. Que deviennent les données ?
  options:
  - Elles sont conservées dans le PV
  - Elles sont supprimées avec le volume
  - Elles sont déplacées dans un snapshot
  - Elles restent jusqu'au redémarrage du nœud
  answer: 1
  explain: C'est pour ça qu'on utilise `Retain` sur les données critiques, en plus de vraies sauvegardes (Velero, snapshots CSI).
---

Le stockage persistant sépare **ce dont l'appli a besoin** (le PVC) de **ce que fournit l'infrastructure** (le PV), avec la StorageClass pour automatiser.


> **Les termes et outils cités dans cette fiche.**
> - **EBS** : les disques réseau attachés aux instances EC2.
> - **NFS** : un protocole de partage de fichiers en réseau, monté comme un dossier local.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **EFS** : le système de fichiers partagé (NFS) d'AWS.

## Le provisionnement dynamique

<!-- schema:provisioning -->
<figure class="diagram"><svg viewBox="0 0 680 230" role="img" aria-label="Le provisionnement dynamique d&#x27;un volume" style="--minw:560px"><defs><marker id="g8-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g8-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g8-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g8-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="16" y="140" width="100" height="52" rx="9"/></g><text x="66.0" y="163.0" class="dg-t" text-anchor="middle" style="--d:0">Pod</text><text x="66.0" y="181.0" class="dg-s" text-anchor="middle" style="--d:0">monte data</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="156" y="140" width="130" height="52" rx="9"/></g><text x="221.0" y="163.0" class="dg-t" text-anchor="middle" style="--d:1">PVC data</text><text x="221.0" y="181.0" class="dg-s" text-anchor="middle" style="--d:1">20Gi · RWO · gp3</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="326" y="140" width="130" height="52" rx="9"/></g><text x="391.0" y="163.0" class="dg-t" text-anchor="middle" style="--d:4">PV pvc-3f2a</text><text x="391.0" y="181.0" class="dg-s" text-anchor="middle" style="--d:4">le volume réel</text><g class="dg-box dg-pop" style="--d:5"><rect x="496" y="140" width="168" height="52" rx="9"/></g><text x="580.0" y="163.0" class="dg-t" text-anchor="middle" style="--d:5">disque EBS</text><text x="580.0" y="181.0" class="dg-s" text-anchor="middle" style="--d:5">chez le cloud</text><path d="M116 166 L154 166" class="dg-l" marker-end="url(#g8-n)"/><path d="M286 166 L324 166" class="dg-l c" marker-end="url(#g8-c)" marker-start="url(#g8-c)"/><text x="305.0" y="158.0" class="dg-s" text-anchor="middle">lié</text><path d="M456 166 L494 166" class="dg-l" marker-end="url(#g8-n)"/><g class="dg-box dg-pop" style="--d:2"><rect x="156" y="24" width="130" height="52" rx="9"/></g><text x="221.0" y="47.0" class="dg-t" text-anchor="middle" style="--d:2">StorageClass</text><text x="221.0" y="65.0" class="dg-s" text-anchor="middle" style="--d:2">gp3</text><g class="dg-box dg-pop" style="--d:3"><rect x="326" y="24" width="130" height="52" rx="9"/></g><text x="391.0" y="47.0" class="dg-t" text-anchor="middle" style="--d:3">driver CSI</text><text x="391.0" y="65.0" class="dg-s" text-anchor="middle" style="--d:3">ebs.csi.aws.com</text><path d="M221 138 L221 78" class="dg-l dash" marker-end="url(#g8-n)"/><text x="221.0" y="112.0" class="dg-s" text-anchor="middle">demande</text><path d="M286 50 L324 50" class="dg-l" marker-end="url(#g8-n)"/><path d="M391 78 L391 138" class="dg-l c" marker-end="url(#g8-c)" style="--d:4"/><path d="M456 50 L580 50 L580 138" class="dg-l dash" marker-end="url(#g8-n)"/><text x="518" y="40" class="dg-s" text-anchor="middle">crée le disque</text><text x="398" y="112" class="dg-s" text-anchor="start">crée le PV</text></svg><figcaption>Tu écris seulement le PVC. La StorageClass et le driver CSI créent le disque et le PV.</figcaption></figure>
<!-- /schema:provisioning -->

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: gp3 }
provisioner: ebs.csi.aws.com
parameters: { type: gp3 }
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: data }
spec:
  storageClassName: gp3
  accessModes: [ReadWriteOnce]
  resources: { requests: { storage: 20Gi } }
```

## Comprendre avec une analogie

Pense à une location de place de parking :

- le **PVC** (*PersistentVolumeClaim*) est ta **demande** : « il me faut 20 Go, en écriture, de type rapide ». Il est écrit par l'équipe appli, dans son namespace ;
- le **PV** (*PersistentVolume*) est la **place réelle** : un disque EBS précis, un partage NFS. C'est un objet du cluster, pas d'un namespace ;
- la **StorageClass** est le **gestionnaire** qui crée des places à la demande. Sans elle, un administrateur devrait créer chaque PV à la main.

Le **binding** associe un PVC à un PV, de façon exclusive : un PV ne sert qu'un PVC. Le pod, lui, ne référence que le PVC : il ne sait rien du disque derrière, et le même manifeste fonctionne sur AWS ou sur un cluster local.

## Les options de la StorageClass, expliquées

- **`provisioner`** : le pilote **CSI** qui sait créer le disque (`ebs.csi.aws.com`). C'est un composant installé dans le cluster.
- **`volumeBindingMode: WaitForFirstConsumer`** : attendre qu'un pod utilise le PVC avant de créer le disque. Indispensable avec des disques **zonaux** comme EBS : sans ça, le disque peut être créé en zone `a` alors que le pod est placé en zone `b`, où il ne pourra jamais le monter (pod `Pending` pour toujours).
- **`reclaimPolicy`** : que faire du disque quand le PVC est supprimé. `Delete` (le défaut le plus courant) le **détruit avec les données** ; `Retain` le garde, à nettoyer à la main. Pour des données précieuses, `Retain`.
- **`allowVolumeExpansion`** : autoriser l'agrandissement en modifiant la taille demandée dans le PVC.

Un PVC `Pending` vient presque toujours de l'un de ces points : pas de StorageClass par défaut, pilote CSI absent, ou disque dans une autre zone que le pod. `kubectl describe pvc` le dit dans ses événements.

## Les modes d'accès

| Mode | Écriture | Exemple de stockage |
| --- | --- | --- |
| `ReadWriteOnce` | un nœud | EBS, disque Ceph RBD |
| `ReadOnlyMany` | aucune, lecture multi-nœuds | NFS |
| `ReadWriteMany` | plusieurs nœuds | NFS, CephFS, EFS |
| `ReadWriteOncePod` | un seul pod | disques CSI récents |

> **Piège classique.** `ReadWriteOnce` limite à un **nœud**, pas à un pod. Deux pods sur le même nœud peuvent écrire ensemble sur le même volume. Pour un seul pod, utilise `ReadWriteOncePod`.

## Diagnostiquer

```bash
kubectl get pvc,pv
kubectl describe pvc data
kubectl get storageclass   # la classe par défaut est marquée (default)
```

> **À retenir.** Le pod référence un PVC (la demande), la StorageClass crée le PV (le disque réel) à la volée. Avec des disques zonaux, `WaitForFirstConsumer` est indispensable, et `reclaimPolicy: Retain` protège les données précieuses d'une suppression du PVC.
