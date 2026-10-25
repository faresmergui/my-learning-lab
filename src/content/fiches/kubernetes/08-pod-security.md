---
title: securityContext et Pod Security
chapter: 8
order: 2
duration: 7
level: intermédiaire
tags:
- CKS
cards:
- q: Quels réglages de `securityContext` forment la base d'un conteneur durci ?
  a: '`runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, `capabilities: { drop: [ALL] }` et `seccompProfile: { type: RuntimeDefault }`.'
- q: Quels sont les trois niveaux de Pod Security Standards ?
  a: '**privileged** (aucune restriction), **baseline** (bloque les escalades connues : privileged, hostPath, hostNetwork…) et **restricted** (bonnes pratiques de durcissement).'
- q: Comment applique-t-on Pod Security à un namespace ?
  a: 'Avec des labels : `pod-security.kubernetes.io/enforce: restricted`. Les modes `warn` et `audit` permettent de tester sans bloquer.'
- q: Qu'est-ce qui a remplacé les PodSecurityPolicy ?
  a: '**Pod Security Admission**, intégré à l''API server. Les PSP ont été supprimées en Kubernetes 1.25. Pour des règles plus fines : Kyverno ou OPA Gatekeeper.'
- q: 'Pourquoi `readOnlyRootFilesystem: true` gêne-t-il certaines applis, et comment faire ?'
  a: Elles écrivent dans `/tmp` ou un cache. On leur monte un `emptyDir` à ces endroits précis, le reste du système de fichiers reste en lecture seule.
quiz:
- q: Tu veux passer un namespace en `restricted` sans risquer de casser la prod. Comment procéder ?
  options:
  - 'Appliquer `enforce: restricted` directement'
  - 'Mettre `warn: restricted` et `audit: restricted`, corriger, puis passer en `enforce`'
  - Supprimer les pods existants
  - Utiliser une PodSecurityPolicy
  answer: 1
  explain: Les modes `warn` et `audit` signalent les violations sans bloquer. Note que `enforce` ne bloque que les nouveaux pods, pas ceux qui tournent déjà.
- q: 'Un pod a `privileged: true`. Que peut-il faire ?'
  options:
  - Seulement lire les Secrets
  - 'Presque tout sur le nœud : accès aux périphériques, toutes les capabilities, sortie possible du conteneur'
  - Rien de plus qu'un autre pod
  - Seulement modifier son propre réseau
  answer: 1
  explain: Un conteneur privilégié a pratiquement les droits de root sur le nœud. À réserver aux agents système qui en ont vraiment besoin.
---

Par défaut, un conteneur tourne souvent en root avec plus de droits que nécessaire. Le `securityContext` les réduit, et Pod Security Admission impose un niveau minimum par namespace.

> **Les termes cités dans cette fiche.**
> - **securityContext** : la partie du manifeste qui règle les droits d'un pod ou d'un conteneur (utilisateur, privilèges, système de fichiers).
> - **root** : l'administrateur d'un système Linux, qui a tous les droits. **setuid** : un drapeau sur un programme qui le fait tourner avec les droits de son propriétaire (souvent root), une voie classique pour gagner des privilèges.
> - **capabilities** : les pouvoirs de root découpés en petits morceaux (ouvrir un port bas, manipuler le réseau, monter un disque…). Un conteneur peut en garder certains sans être root ; `drop: [ALL]` les retire tous.
> - **seccomp** : un filtre du noyau qui limite les appels système qu'un programme a le droit de faire. `RuntimeDefault` applique le profil prudent fourni par le runtime.
> - **Pod Security Admission** : le contrôle intégré à Kubernetes qui vérifie, à la création, qu'un pod respecte un des trois niveaux de sécurité (`privileged`, `baseline`, `restricted`).
> - **CNI** : le standard des plugins réseau de Kubernetes (Calico, Cilium…), qui donnent une adresse IP à chaque pod.
> - **CSI** : le standard des pilotes de stockage de Kubernetes.

## Un conteneur durci

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    fsGroup: 10001
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: api
      image: registry.local/api:2.1
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities: { drop: [ALL] }
      volumeMounts: [{ name: tmp, mountPath: /tmp }]
  volumes:
    - name: tmp
      emptyDir: {}
```

| Réglage | Ce qu'il empêche |
| --- | --- |
| `runAsNonRoot` | de tourner en root |
| `allowPrivilegeEscalation: false` | de gagner des droits (setuid, sudo) |
| `readOnlyRootFilesystem` | de modifier les binaires ou d'y déposer un outil |
| `capabilities: drop ALL` | les privilèges noyau (réseau brut, montage…) |
| `seccomp RuntimeDefault` | les appels système rares et dangereux |

## Pod Security Admission

```bash
kubectl label namespace app \
  pod-security.kubernetes.io/enforce=baseline \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/audit=restricted
```

| Niveau | Pour qui |
| --- | --- |
| `privileged` | agents système (CNI, CSI, monitoring des nœuds) |
| `baseline` | toutes les applis, au minimum |
| `restricted` | l'objectif pour tes applis |

> **À retenir.** Commence par `warn` et `audit` en `restricted`, corrige ce qui remonte, puis passe en `enforce`. Les pods déjà lancés ne sont pas touchés, seulement les nouveaux.
