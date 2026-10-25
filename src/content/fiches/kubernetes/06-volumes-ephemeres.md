---
title: Volumes éphémères et projetés
chapter: 6
order: 2
duration: 5
level: intermédiaire
tags:
- CKA
- CKAD
cards:
- q: Combien de temps vit un volume `emptyDir` ?
  a: Autant que le **pod**. Il survit au redémarrage d'un conteneur, mais il est effacé quand le pod est supprimé.
- q: Comment créer un `emptyDir` en mémoire ?
  a: '`emptyDir: { medium: Memory, sizeLimit: 256Mi }`. C''est un tmpfs, et son contenu compte dans la limite mémoire du conteneur.'
- q: Pourquoi `hostPath` est-il dangereux ?
  a: Il donne accès au système de fichiers du **nœud**. Monter `/` ou `/var/run/containerd` revient presque à donner un accès root au nœud. Pod Security le refuse au niveau `baseline`.
- q: À quoi sert la Downward API ?
  a: 'À donner au conteneur des infos sur **son propre pod** : nom, namespace, labels, IP, requests et limits, en variables ou en fichiers.'
- q: Qu'est-ce qu'un volume `projected` ?
  a: 'Un volume qui regroupe plusieurs sources dans un même dossier : ConfigMap, Secret, Downward API et token de ServiceAccount.'
quiz:
- q: Ton appli écrit un cache de 2 Gio dans un `emptyDir` sans `sizeLimit`. Quel risque ?
  options:
  - Aucun
  - Remplir le disque du nœud et provoquer l'éviction de pods
  - Le cache est perdu à chaque requête
  - Le pod ne peut pas démarrer
  answer: 1
  explain: Un `emptyDir` sur disque utilise le stockage éphémère du nœud. Avec `sizeLimit` ou une limite `ephemeral-storage`, seul ton pod est évincé s'il dépasse.
- q: Comment donner au conteneur le nom du nœud sur lequel il tourne ?
  options:
  - 'Une variable avec `fieldRef: { fieldPath: spec.nodeName }`'
  - Un ConfigMap
  - '`hostPath: /etc/hostname`'
  - C'est impossible
  answer: 0
  explain: C'est la Downward API. Utile pour des logs ou des métriques qui doivent savoir où ils tournent.
---

Tous les volumes ne servent pas à garder des données. Certains servent à partager des fichiers dans un pod, ou à lui donner des informations.

> **Les termes cités dans cette fiche.**
> - **Volume éphémère** : un volume qui disparaît avec le pod (ou qui reflète un objet), par opposition aux volumes persistants (PV/PVC) de la fiche précédente.
> - **tmpfs** : un système de fichiers en mémoire vive. Très rapide, mais il compte dans la limite mémoire du conteneur et s'efface au redémarrage.
> - **Downward API** : le moyen de donner à un conteneur des informations sur son propre pod (nom, nœud, limites) sans qu'il interroge l'API.
> - **ServiceAccount token** : un jeton qui prouve l'identité du pod. Projeté avec une durée de vie et une **audience** (le service à qui il est destiné, ici **Vault**, un coffre-fort à secrets), il expire et se renouvelle tout seul.
> - **hostPath** : monte un dossier du nœud dans le pod. Le pod peut alors lire ou modifier le système du nœud, d'où le danger.
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **CNI** : le standard des plugins réseau de Kubernetes (Calico, Cilium…), qui donnent une adresse IP à chaque pod.
> - **CSI** : le standard des pilotes de stockage de Kubernetes.

| Volume | Durée de vie | Usage |
| --- | --- | --- |
| `emptyDir` | celle du pod | cache, échange de fichiers entre conteneurs |
| `configMap`, `secret` | celle de l'objet | fichiers de config, certificats |
| `downwardAPI` | celle du pod | infos sur le pod lui-même |
| `projected` | celle des sources | plusieurs sources dans un seul dossier |
| `hostPath` | celle du nœud | agents système uniquement, à éviter |

## emptyDir

```yaml
volumes:
  - name: cache
    emptyDir: { sizeLimit: 1Gi }
  - name: scratch
    emptyDir: { medium: Memory, sizeLimit: 256Mi }   # tmpfs
```

## Downward API

```yaml
env:
  - name: POD_NAME
    valueFrom: { fieldRef: { fieldPath: metadata.name } }
  - name: NODE_NAME
    valueFrom: { fieldRef: { fieldPath: spec.nodeName } }
  - name: MEM_LIMIT
    valueFrom: { resourceFieldRef: { resource: limits.memory } }
```

## Volume projeté

```yaml
volumes:
  - name: app-files
    projected:
      sources:
        - configMap: { name: app-config }
        - secret: { name: app-tls }
        - serviceAccountToken: { path: token, expirationSeconds: 3600, audience: vault }
```

> **À retenir.** Un `hostPath` dans un manifeste applicatif est presque toujours un mauvais signe. Seuls les agents système (CNI, CSI, collecteurs de logs) en ont vraiment besoin.
