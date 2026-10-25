---
title: CRD et opérateurs
chapter: 10
order: 3
duration: 9
tags:
- CKA
- CRD
- opérateurs
cards:
- q: Qu'est-ce qu'une CRD ?
  a: 'Une **CustomResourceDefinition** : elle ajoute un nouveau type d''objet à l''API Kubernetes (par exemple `Certificate` ou `PostgresCluster`), avec son schéma. Ensuite on crée des objets de ce type comme n''importe quel autre.'
- q: Une CRD seule fait-elle quelque chose ?
  a: '**Non.** Elle ne fait que stocker des objets dans etcd. Il faut un **contrôleur** qui les lit et agit pour qu''il se passe quelque chose.'
- q: Qu'est-ce qu'un opérateur ?
  a: 'Une ou plusieurs CRD **plus** un contrôleur qui contient le savoir-faire d''un humain sur une application : installer, mettre à jour, sauvegarder, basculer en cas de panne.'
- q: Comment lister les CRD d'un cluster et voir les champs d'un type personnalisé ?
  a: '`kubectl get crd` pour la liste, `kubectl api-resources` pour tous les types, et `kubectl explain <type>.spec` pour la documentation des champs.'
- q: Que se passe-t-il si on supprime une CRD ?
  a: '**Tous les objets de ce type sont supprimés** avec elle. C''est une opération dangereuse, à ne faire qu''en sachant ce qu''on fait.'
quiz:
- q: Tu installes la CRD `Certificate` de cert-manager mais pas son contrôleur. Tu crées un objet `Certificate`. Que se passe-t-il ?
  options:
  - Un certificat est créé
  - L'objet est enregistré mais rien ne se passe
  - La création est refusée
  - Le pod cert-manager démarre tout seul
  answer: 1
  explain: L'API accepte l'objet car son type existe, mais personne ne le traite. C'est le contrôleur qui crée le certificat.
- q: Quelle commande montre les champs attendus dans `spec` d'un type `PostgresCluster` ?
  options:
  - '`kubectl describe crd`'
  - '`kubectl explain postgrescluster.spec`'
  - '`kubectl get postgrescluster -o yaml`'
  - '`helm show values`'
  answer: 1
  explain: '`kubectl explain` lit le schéma de la CRD, comme pour les types intégrés.'
level: intermédiaire
---

Kubernetes connaît d'origine des Pods, des Deployments, des Services… Mais on peut lui apprendre de nouveaux types d'objets. C'est ce que font la plupart des outils de l'écosystème : cert-manager ajoute des `Certificate`, Argo CD des `Application`, Prometheus Operator des `ServiceMonitor`. La CKA demande de savoir les reconnaître et les manipuler.

> **Les outils cités dans cette fiche.**
> - **CRD** (CustomResourceDefinition) : la déclaration d'un nouveau type d'objet dans l'API, avec son nom et son schéma.
> - **contrôleur** : un programme qui surveille des objets et agit pour que la réalité corresponde à ce qu'ils décrivent. Le Deployment controller en est un, intégré à Kubernetes.
> - **opérateur** : un contrôleur écrit pour une application précise (une base de données, un outil), qui automatise ce qu'un administrateur ferait à la main.
> - **cert-manager** : un opérateur qui demande et renouvelle des certificats TLS automatiquement.
> - **Argo CD** : un outil GitOps qui synchronise le cluster avec un dépôt Git ; il décrit chaque application dans un objet `Application`.
> - **Prometheus Operator** : un opérateur qui installe et configure Prometheus, l'outil de collecte de métriques.
> - **réplica** : une copie identique d'un pod, d'une base ou d'une donnée.
> - **RBAC** : le contrôle d'accès par rôles : on donne des droits à des rôles, puis des rôles aux personnes ou programmes.

## Comprendre : la boucle de contrôle

Tout Kubernetes repose sur une idée : tu écris l'**état voulu** dans un objet, et un contrôleur compare sans arrêt cet état à la réalité, puis corrige l'écart. Quand tu demandes 3 réplicas, le contrôleur des ReplicaSets crée ou supprime des pods jusqu'à en avoir 3.

Une CRD et un opérateur reprennent exactement ce modèle pour des choses que Kubernetes ne connaît pas :

| Pièce | Rôle | Analogie |
| --- | --- | --- |
| CRD | ajoute le type `PostgresCluster` à l'API | un nouveau formulaire |
| objet personnalisé | « je veux un Postgres à 3 nœuds en version 17 » | le formulaire rempli |
| opérateur | lit l'objet et crée StatefulSet, Services, sauvegardes | l'employé qui traite le formulaire |

Sans opérateur, la CRD est un formulaire que personne ne lit : l'objet est stocké, rien ne se passe.

## À quoi ressemble une CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.shop.fr          # <pluriel>.<groupe>
spec:
  group: shop.fr
  scope: Namespaced
  names: { kind: Backup, plural: backups, singular: backup, shortNames: [bk] }
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                schedule: { type: string }
                retentionDays: { type: integer, minimum: 1 }
```

Puis on crée un objet de ce type :

```yaml
apiVersion: shop.fr/v1
kind: Backup
metadata: { name: nightly, namespace: shop }
spec: { schedule: "0 2 * * *", retentionDays: 14 }
```

## Les commandes utiles

```bash
kubectl get crd                          # les types ajoutés au cluster
kubectl api-resources --api-group=cert-manager.io
kubectl explain certificate.spec         # les champs, comme pour un type intégré
kubectl get certificates -A              # les objets de ce type
kubectl describe certificate api-tls -n shop   # l'état rempli par l'opérateur (status, events)
```

Le champ `status` d'un objet personnalisé est rempli par l'opérateur. C'est là qu'on regarde en premier quand quelque chose ne marche pas, avec les events et les logs du pod de l'opérateur.

## Les précautions

- **Supprimer une CRD supprime tous ses objets.** Désinstaller un chart Helm qui l'avait installée peut donc effacer, par exemple, toutes tes définitions de certificats.
- Les CRD sont des objets **du cluster** (non rattachés à un namespace) : il faut des droits élevés pour les créer. On les installe en général une fois, avec l'opérateur.
- Un opérateur a souvent des droits RBAC larges. Le choisir, c'est lui faire confiance comme à un administrateur.

> **À retenir.** Une CRD ajoute un type à l'API, un opérateur le fait vivre. On les explore avec `kubectl get crd`, `kubectl explain` et le `status` des objets. Supprimer une CRD efface tous les objets de ce type.
