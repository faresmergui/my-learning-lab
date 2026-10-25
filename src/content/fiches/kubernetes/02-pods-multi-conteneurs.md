---
title: 'Pods multi-conteneurs : init et sidecars'
chapter: 2
order: 1
duration: 6
level: intermédiaire
tags:
- CKA
- CKAD
cards:
- q: Que partagent les conteneurs d'un même pod ?
  a: Le **réseau** (même IP, ils se parlent en `localhost`) et les **volumes** déclarés dans le pod. Ils ne partagent pas leur système de fichiers par défaut.
- q: Comment s'exécutent plusieurs init containers ?
  a: '**Un par un**, dans l''ordre. Chacun doit se terminer avec succès avant le suivant, et les conteneurs principaux ne démarrent qu''après le dernier.'
- q: Comment déclare-t-on un sidecar natif ?
  a: 'Dans `initContainers`, avec `restartPolicy: Always`. Il démarre avant les conteneurs principaux, tourne pendant toute la vie du pod et s''arrête après eux.'
- q: Pourquoi un sidecar natif est-il mieux qu'un sidecar classique pour un Job ?
  a: Un sidecar classique ne s'arrête jamais, donc le Job ne se termine jamais. Le sidecar natif est arrêté automatiquement quand le conteneur principal a fini.
- q: Un init container échoue en boucle. Dans quel état est le pod ?
  a: '`Init:CrashLoopBackOff` (ou `Init:Error`). Pour voir ses logs : `kubectl logs <pod> -c <nom-init>`.'
quiz:
- q: Tu veux attendre que la base de données réponde avant de démarrer ton appli. Que choisis-tu ?
  options:
  - Un sidecar natif
  - Un init container qui boucle jusqu'à joindre la base
  - Une liveness probe
  - Un second Deployment
  answer: 1
  explain: L'init container bloque le démarrage tant qu'il ne s'est pas terminé avec succès. C'est exactement le comportement voulu.
- q: Deux conteneurs du même pod doivent échanger des fichiers. Quelle est la solution la plus simple ?
  options:
  - Un volume `emptyDir` monté dans les deux
  - Un PersistentVolume
  - Un ConfigMap
  - Ils voient déjà les fichiers de l'autre
  answer: 0
  explain: '`emptyDir` vit aussi longtemps que le pod et peut être monté dans plusieurs de ses conteneurs.'
---

Un pod n'est pas forcément un seul conteneur. On y ajoute des conteneurs qui **préparent** le terrain ou qui **accompagnent** l'application.

<!-- schema:pod -->
<figure class="diagram"><svg viewBox="0 0 680 262" role="img" aria-label="Ce que contient et partage un pod" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="16" y="12" width="648" height="238" rx="12" class="dg-zone dg-zc"/><text x="28" y="30" class="dg-zl" text-anchor="start">pod</text><g class="dg-box dg-pop" style="--d:0"><rect x="36" y="56" width="104" height="50" rx="9"/></g><text x="88.0" y="78.0" class="dg-t" text-anchor="middle" style="--d:0">init 1</text><text x="88.0" y="96.0" class="dg-s" text-anchor="middle" style="--d:0">attendre la DB</text><g class="dg-box dg-pop" style="--d:1"><rect x="160" y="56" width="104" height="50" rx="9"/></g><text x="212.0" y="78.0" class="dg-t" text-anchor="middle" style="--d:1">init 2</text><text x="212.0" y="96.0" class="dg-s" text-anchor="middle" style="--d:1">migrations</text><path d="M140 81 L158 81" class="dg-l" marker-end="url(#g3-n)"/><text x="150" y="128" class="dg-s" text-anchor="middle">un par un, chacun doit finir avant le suivant</text><path d="M264 81 L300 81 L300 72 L320 72" class="dg-l c" marker-end="url(#g3-c)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="322" y="46" width="150" height="50" rx="9"/></g><text x="397.0" y="68.0" class="dg-t" text-anchor="middle" style="--d:2">app</text><text x="397.0" y="86.0" class="dg-s" text-anchor="middle" style="--d:2">le conteneur principal</text><g class="dg-box dg-pop" style="--d:3"><rect x="322" y="112" width="150" height="50" rx="9"/></g><text x="397.0" y="134.0" class="dg-t" text-anchor="middle" style="--d:3">sidecar</text><text x="397.0" y="152.0" class="dg-s" text-anchor="middle" style="--d:3">logs, proxy…</text><g class="dg-box dg-ghost dg-pop" style="--d:4"><rect x="504" y="46" width="140" height="116" rx="9"/></g><text x="574.0" y="93.0" class="dg-t" text-anchor="middle" style="--d:4"><tspan x="574.0" dy="0">volume</tspan><tspan x="574.0" dy="16">partagé</tspan></text><text x="574.0" y="127.0" class="dg-s" text-anchor="middle" style="--d:4">emptyDir</text><path d="M472 71 L502 71" class="dg-l dash" marker-end="url(#g3-n)" marker-start="url(#g3-n)"/><path d="M472 137 L502 137" class="dg-l dash" marker-end="url(#g3-n)" marker-start="url(#g3-n)"/><g class="dg-box dg-off dg-pop" style="--d:5"><rect x="36" y="186" width="608" height="44" rx="9"/></g><text x="340.0" y="213.0" class="dg-t" text-anchor="middle" style="--d:5">réseau partagé : une seule IP, les conteneurs se parlent en localhost</text></svg><figcaption>Les init containers préparent, puis l&#x27;app et ses sidecars tournent ensemble avec le même réseau et les mêmes volumes.</figcaption></figure>
<!-- /schema:pod -->


> **Les termes et outils cités dans cette fiche.**
> - **proxy** : un intermédiaire qui reçoit les requêtes et les transmet à leur place.

## Ce que partage un pod

- **Le réseau** : une seule IP, les conteneurs se joignent en `localhost`.
- **Les volumes** déclarés dans `spec.volumes`.
- **Le cycle de vie** : ils sont planifiés ensemble, sur le même nœud.

## Init containers : préparer avant de démarrer

Ils tournent **un par un, jusqu'au bout**, avant les conteneurs principaux. Cas typiques : attendre une dépendance, lancer une migration, générer une config.

```yaml
initContainers:
  - name: wait-db
    image: busybox:1.36
    command: ["sh", "-c", "until nc -z postgres 5432; do sleep 2; done"]
```

## Sidecars natifs : accompagner l'appli

Un sidecar natif est un init container avec `restartPolicy: Always`. Il démarre avant l'appli, reste actif et s'arrête après elle. Idéal pour un agent de logs ou un proxy.

```yaml
initContainers:
  - name: log-shipper
    image: fluent/fluent-bit:3.2
    restartPolicy: Always
    volumeMounts: [{ name: logs, mountPath: /var/log/app }]
containers:
  - name: app
    image: registry.local/app:1.4
    volumeMounts: [{ name: logs, mountPath: /var/log/app }]
volumes:
  - name: logs
    emptyDir: {}
```

> **Piège classique.** Avec un sidecar déclaré dans `containers`, un Job ne se termine jamais, car le sidecar continue de tourner. Le sidecar natif règle ce problème.

> **À retenir.** Les conteneurs d'un pod partagent le réseau et les volumes. Un **init container** prépare et se termine avant l'appli ; un **sidecar natif** (init container avec `restartPolicy: Always`) l'accompagne pendant toute sa vie et s'arrête après elle.
