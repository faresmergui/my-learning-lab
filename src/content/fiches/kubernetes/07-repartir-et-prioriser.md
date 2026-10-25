---
title: Répartir et prioriser les pods
chapter: 7
order: 3
duration: 7
level: intermédiaire
tags:
- CKA
cards:
- q: Comment empêcher deux réplicas d'une appli de tourner sur le même nœud ?
  a: 'Avec une `podAntiAffinity` sur les labels de l''appli et `topologyKey: kubernetes.io/hostname`.'
- q: Que règle `maxSkew` dans `topologySpreadConstraints` ?
  a: 'L''écart maximal de nombre de pods entre deux domaines (zones, nœuds). Avec `maxSkew: 1` sur 3 zones, on ne peut pas avoir 3 pods dans une zone et 1 dans une autre.'
- q: 'Différence entre `whenUnsatisfiable: DoNotSchedule` et `ScheduleAnyway` ?'
  a: '`DoNotSchedule` laisse le pod en Pending si la règle ne peut pas être respectée. `ScheduleAnyway` en fait une simple préférence.'
- q: À quoi sert une PriorityClass ?
  a: À donner une priorité aux pods. Si un pod prioritaire ne trouve pas de place, le scheduler peut **évincer** des pods moins prioritaires (préemption).
- q: À quoi sert un PodDisruptionBudget ?
  a: 'À garantir un minimum de pods disponibles pendant les interruptions **volontaires** : `kubectl drain`, mise à jour des nœuds, autoscaler. Il ne protège pas contre une panne.'
quiz:
- q: Tu lances `kubectl drain node-2` et la commande reste bloquée. Quelle est la cause la plus probable ?
  options:
  - Un PodDisruptionBudget interdit d'évincer un pod de plus
  - Le nœud n'a pas de taint
  - kube-proxy est arrêté
  - Le scheduler est en panne
  answer: 0
  explain: 'Le drain respecte les PDB. Avec un PDB `minAvailable: 2` et seulement 2 pods prêts, aucun ne peut partir. Ajoute des réplicas ou vérifie que les pods sont bien Ready.'
- q: Tu veux répartir 6 pods équitablement sur 3 zones, sans jamais bloquer le déploiement. Quelle règle ?
  options:
  - podAntiAffinity requise par zone
  - topologySpreadConstraints avec topologyKey zone et ScheduleAnyway
  - Un nodeSelector par zone
  - Trois Deployments
  answer: 1
  explain: L'anti-affinité requise par zone n'autoriserait qu'un pod par zone. Le spread avec `ScheduleAnyway` équilibre sans risquer de pods en Pending.
---

Placer les pods au bon endroit, c'est ce qui permet à une appli de survivre à la perte d'un nœud ou d'une zone.


> **Les termes et outils cités dans cette fiche.**
> - **réplica** : une copie identique d'un pod, d'une base ou d'une donnée.
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.
> - **scheduler** : le composant qui décide où placer une charge de travail (sur quel nœud ou quel hôte).

## Répartir les réplicas

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: ScheduleAnyway
      labelSelector: { matchLabels: { app: api } }
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - topologyKey: kubernetes.io/hostname
          labelSelector: { matchLabels: { app: api } }
```

- **topologySpreadConstraints** : équilibre les pods entre zones ou nœuds.
- **podAntiAffinity** : interdit (ou évite) deux pods identiques au même endroit.
- **podAffinity** : l'inverse, rapproche des pods (par exemple une appli et son cache).

<!-- schema:spread -->
<figure class="diagram"><svg viewBox="0 0 680 210" role="img" aria-label="Six réplicas répartis sur trois zones" style="--minw:560px"><defs><marker id="g18-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g18-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g18-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g18-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="16" y="14" width="208" height="150" rx="12" class="dg-zone dg-zc"/><text x="28" y="32" class="dg-zl" text-anchor="start">zone a</text><g class="dg-box dg-pop" style="--d:0"><rect x="30" y="44" width="86" height="104" rx="8"/></g><text x="73" y="70" class="dg-t" text-anchor="middle" style="--d:0">nœud 1</text><g class="dg-box dg-pop" style="--d:0"><rect x="128" y="44" width="86" height="104" rx="8"/></g><text x="171" y="70" class="dg-t" text-anchor="middle" style="--d:0">nœud 2</text><circle cx="73" cy="112" r="11" class="dg-dot dg-c dg-pop" style="--d:1"/><circle cx="171" cy="112" r="11" class="dg-dot dg-c dg-pop" style="--d:2"/><rect x="236" y="14" width="208" height="150" rx="12" class="dg-zone dg-zc"/><text x="248" y="32" class="dg-zl" text-anchor="start">zone b</text><g class="dg-box dg-pop" style="--d:1"><rect x="250" y="44" width="86" height="104" rx="8"/></g><text x="293" y="70" class="dg-t" text-anchor="middle" style="--d:1">nœud 3</text><g class="dg-box dg-pop" style="--d:1"><rect x="348" y="44" width="86" height="104" rx="8"/></g><text x="391" y="70" class="dg-t" text-anchor="middle" style="--d:1">nœud 4</text><circle cx="293" cy="112" r="11" class="dg-dot dg-c dg-pop" style="--d:2"/><circle cx="391" cy="112" r="11" class="dg-dot dg-c dg-pop" style="--d:3"/><rect x="456" y="14" width="208" height="150" rx="12" class="dg-zone dg-zc"/><text x="468" y="32" class="dg-zl" text-anchor="start">zone c</text><g class="dg-box dg-pop" style="--d:2"><rect x="470" y="44" width="86" height="104" rx="8"/></g><text x="513" y="70" class="dg-t" text-anchor="middle" style="--d:2">nœud 5</text><g class="dg-box dg-pop" style="--d:2"><rect x="568" y="44" width="86" height="104" rx="8"/></g><text x="611" y="70" class="dg-t" text-anchor="middle" style="--d:2">nœud 6</text><circle cx="513" cy="112" r="11" class="dg-dot dg-c dg-pop" style="--d:3"/><circle cx="611" cy="112" r="11" class="dg-dot dg-c dg-pop" style="--d:4"/><text x="340" y="188" class="dg-s" text-anchor="middle">topologySpreadConstraints · maxSkew: 1 · topologyKey: zone</text><text x="340" y="204" class="dg-ct" text-anchor="middle">la perte d&#x27;une zone ne coupe qu&#x27;un tiers des réplicas</text></svg><figcaption>Sans contrainte, le scheduler peut tout mettre sur les mêmes nœuds.</figcaption></figure>
<!-- /schema:spread -->

## Prioriser

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: { name: critical-app }
value: 100000
description: Services critiques, peuvent préempter les autres
---
spec:
  priorityClassName: critical-app
```

## Protéger pendant la maintenance

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api }
spec:
  minAvailable: 2
  selector: { matchLabels: { app: api } }
```

> **À retenir.** Sans PDB, un `kubectl drain` peut évincer tous les réplicas d'une appli en même temps si elles sont sur le même nœud. Répartition + PDB, c'est le duo de base de la haute disponibilité.

```bash
kubectl drain node-2 --ignore-daemonsets --delete-emptydir-data
kubectl uncordon node-2
```
