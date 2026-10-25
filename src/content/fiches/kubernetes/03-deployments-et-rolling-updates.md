---
title: Deployments et rolling updates
chapter: 3
order: 1
duration: 8
level: intermédiaire
tags:
- CKA
- CKAD
cards:
- q: Quelle est la chaîne d'objets derrière un Deployment ?
  a: Deployment → **ReplicaSet** → Pods. À chaque changement du template de pod, le Deployment crée un nouveau ReplicaSet.
- q: Que règlent `maxSurge` et `maxUnavailable` ?
  a: '`maxSurge` : combien de pods **en plus** du nombre voulu pendant la mise à jour. `maxUnavailable` : combien peuvent manquer. Les deux valent **25 %** par défaut.'
- q: Comment revenir à la version précédente d'un Deployment ?
  a: '`kubectl rollout undo deployment/api`, ou `--to-revision=N` pour une révision précise (voir `kubectl rollout history`).'
- q: Un `kubectl scale` crée-t-il une nouvelle révision ?
  a: Non. Seul un changement du **template de pod** (`spec.template`) crée un nouveau ReplicaSet et donc une révision.
- q: Comment redémarrer tous les pods d'un Deployment sans changer l'image ?
  a: '`kubectl rollout restart deployment/api` : il modifie une annotation du template, ce qui déclenche un rolling update.'
- q: Quand utiliser la stratégie `Recreate` ?
  a: Quand deux versions ne peuvent pas tourner en même temps (migration de schéma incompatible, volume en `ReadWriteOnce`). Elle supprime tout avant de recréer, donc avec une coupure.
quiz:
- q: Pendant un rolling update, les nouveaux pods ne deviennent jamais Ready. Que se passe-t-il ?
  options:
  - Les anciens pods sont supprimés quand même
  - Le rollout se bloque, les anciens pods continuent de servir
  - Le Deployment revient automatiquement en arrière
  - Le cluster redémarre
  answer: 1
  explain: Le rollout n'avance que si les nouveaux pods sont prêts. Après `progressDeadlineSeconds` (600 s par défaut), il est marqué en échec, mais il n'y a **pas** de retour arrière automatique.
- q: 'Avec 4 réplicas, `maxSurge: 1` et `maxUnavailable: 0`, combien de pods au maximum pendant la mise à jour ?'
  options:
  - '4'
  - '5'
  - '6'
  - '8'
  answer: 1
  explain: '4 voulus + 1 en surplus = 5. Avec `maxUnavailable: 0`, on ne descend jamais sous 4 pods prêts.'
- q: Quelle commande met à jour l'image du conteneur `api` ?
  options:
  - kubectl set image deployment/api api=registry.local/api:2.1
  - kubectl rollout image api:2.1
  - kubectl edit pod api
  - kubectl replace --image api:2.1
  answer: 0
  explain: '`kubectl set image` modifie le template, ce qui crée une nouvelle révision. Ajoute une annotation `kubernetes.io/change-cause` pour garder une trace dans l''historique.'
---

Le Deployment est l'objet de base pour une appli sans état. Il garantit le nombre de réplicas et orchestre les mises à jour sans coupure.


> **Les termes et outils cités dans cette fiche.**
> - **réplica** : une copie identique d'un pod, d'une base ou d'une donnée.

## La chaîne des objets

<!-- schema:chaine -->
<figure class="diagram"><svg viewBox="0 0 680 236" role="img" aria-label="Deployment, ReplicaSets et Pods" style="--minw:560px"><defs><marker id="g5-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g5-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g5-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g5-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="16" y="92" width="150" height="56" rx="9"/></g><text x="91.0" y="117.0" class="dg-t" text-anchor="middle" style="--d:0">Deployment api</text><text x="91.0" y="135.0" class="dg-s" text-anchor="middle" style="--d:0">ce que tu écris</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="226" y="30" width="180" height="54" rx="9"/></g><text x="316.0" y="54.0" class="dg-t" text-anchor="middle" style="--d:1">ReplicaSet api-7d9f</text><text x="316.0" y="72.0" class="dg-s" text-anchor="middle" style="--d:1">révision 2 · 3 réplicas</text><g class="dg-box dg-off dg-pop" style="--d:1"><rect x="226" y="152" width="180" height="54" rx="9"/></g><text x="316.0" y="176.0" class="dg-t" text-anchor="middle" style="--d:1">ReplicaSet api-5c8b</text><text x="316.0" y="194.0" class="dg-s" text-anchor="middle" style="--d:1">révision 1 · 0 réplica</text><path d="M166 112 L196 112 L196 57 L224 57" class="dg-l c" marker-end="url(#g5-c)"/><path d="M166 128 L196 128 L196 179 L224 179" class="dg-l dash" marker-end="url(#g5-n)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="446" y="36" width="66" height="42" rx="9"/></g><text x="479.0" y="54.0" class="dg-t" text-anchor="middle" style="--d:2">pod</text><text x="479.0" y="72.0" class="dg-s" text-anchor="middle" style="--d:2">v2</text><g class="dg-box dg-off dg-pop" style="--d:2"><rect x="446" y="158" width="66" height="42" rx="9"/></g><text x="479.0" y="176.0" class="dg-t" text-anchor="middle" style="--d:2">pod</text><text x="479.0" y="194.0" class="dg-s" text-anchor="middle" style="--d:2">v1</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="522" y="36" width="66" height="42" rx="9"/></g><text x="555.0" y="54.0" class="dg-t" text-anchor="middle" style="--d:3">pod</text><text x="555.0" y="72.0" class="dg-s" text-anchor="middle" style="--d:3">v2</text><g class="dg-box dg-off dg-pop" style="--d:3"><rect x="522" y="158" width="66" height="42" rx="9"/></g><text x="555.0" y="176.0" class="dg-t" text-anchor="middle" style="--d:3">pod</text><text x="555.0" y="194.0" class="dg-s" text-anchor="middle" style="--d:3">v1</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="598" y="36" width="66" height="42" rx="9"/></g><text x="631.0" y="54.0" class="dg-t" text-anchor="middle" style="--d:4">pod</text><text x="631.0" y="72.0" class="dg-s" text-anchor="middle" style="--d:4">v2</text><g class="dg-box dg-off dg-pop" style="--d:4"><rect x="598" y="158" width="66" height="42" rx="9"/></g><text x="631.0" y="176.0" class="dg-t" text-anchor="middle" style="--d:4">pod</text><text x="631.0" y="194.0" class="dg-s" text-anchor="middle" style="--d:4">v1</text><path d="M406 57 L444 57" class="dg-l c" marker-end="url(#g5-c)"/><path d="M406 179 L444 179" class="dg-l dash" marker-end="url(#g5-n)"/><text x="560" y="128" class="dg-s" text-anchor="middle">gardé pour le rollback</text></svg><figcaption>Chaque changement du template crée un ReplicaSet. L&#x27;ancien reste à 0 réplica pour pouvoir revenir en arrière.</figcaption></figure>
<!-- /schema:chaine -->

Changer l'image crée un **nouveau ReplicaSet**. Le Deployment fait monter le nouveau et descendre l'ancien, petit à petit. Les anciens ReplicaSets sont gardés à zéro réplica pour pouvoir revenir en arrière (`revisionHistoryLimit`, 10 par défaut).

## Régler le rolling update

```yaml
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # au plus 5 pods pendant la mise à jour
      maxUnavailable: 0  # jamais moins de 4 pods prêts
```

> **À retenir.** Sans readiness probe, Kubernetes considère un pod prêt dès qu'il démarre. Le rolling update peut alors envoyer du trafic vers une appli qui n'est pas encore prête.

## Comprendre la chaîne Deployment → ReplicaSet → Pods

Pourquoi deux niveaux ? Chacun a un seul travail :

- le **ReplicaSet** garantit qu'il y a **N pods identiques** (même template). Il ne sait faire que ça : il ne connaît pas les versions ;
- le **Deployment** gère les **versions** : à chaque changement du template de pod (image, variable, ressources), il crée un nouveau ReplicaSet et fait glisser les réplicas de l'ancien vers le nouveau.

Seul un changement dans `spec.template` déclenche un rollout. Modifier `replicas` ne fait qu'ajuster le ReplicaSet actuel. Et un ConfigMap modifié ne change pas le template : aucun rollout (d'où `kubectl rollout restart`, qui ajoute une annotation datée au template pour forcer un nouveau ReplicaSet).

Le **rollback** est simple grâce à ce modèle : les anciens ReplicaSets existent toujours, à zéro réplica. `rollout undo` fait remonter l'un d'eux.

## Les étapes d'un rolling update avec `maxSurge: 1`, `maxUnavailable: 0`

Avec 4 réplicas en version 1 :

1. création d'un pod v2 (5 pods au total, c'est le `maxSurge`) ;
2. attente que le pod v2 soit **Ready** ;
3. suppression d'un pod v1 (retour à 4) ;
4. on recommence jusqu'à 4 pods v2.

Si le nouveau pod ne devient jamais Ready (image cassée, probe qui échoue), le rollout **reste bloqué** à l'étape 2 : les 4 pods v1 continuent de servir. C'est le filet de sécurité. `progressDeadlineSeconds` (600 s par défaut) marque ensuite le rollout en échec, que `kubectl rollout status` signale.

## Les commandes du quotidien

```bash
kubectl set image deployment/api api=registry.local/api:2.1
kubectl rollout status deployment/api
kubectl rollout history deployment/api
kubectl rollout undo deployment/api --to-revision=3
kubectl rollout restart deployment/api
kubectl rollout pause deployment/api   # pour enchaîner plusieurs changements
```
