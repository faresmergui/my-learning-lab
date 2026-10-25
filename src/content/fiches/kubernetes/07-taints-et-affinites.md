---
title: Taints, tolerations et affinités
chapter: 7
order: 1
duration: 6
level: intermédiaire
tags:
- CKA
cards:
- q: Quelle est la différence entre un taint et une affinité de nœud ?
  a: Le **taint** est posé sur le nœud et repousse les pods qui ne le tolèrent pas. L'**affinité** est déclarée dans le pod et l'attire vers des nœuds portant certains labels.
- q: Une toleration suffit-elle à envoyer un pod sur un nœud ?
  a: Non. Elle l'**autorise** seulement à y aller. Pour réserver des nœuds, on combine taint + affinité (ou `nodeSelector`).
- q: Quels sont les trois effets possibles d'un taint ?
  a: '`NoSchedule` (pas de nouveaux pods), `PreferNoSchedule` (à éviter si possible) et `NoExecute` (évince aussi les pods déjà présents qui ne le tolèrent pas).'
- q: Comment retirer le taint `gpu=true:NoSchedule` du nœud `gpu-01` ?
  a: '`kubectl taint nodes gpu-01 gpu=true:NoSchedule-` : le `-` final supprime le taint.'
- q: Que signifie `IgnoredDuringExecution` dans `requiredDuringSchedulingIgnoredDuringExecution` ?
  a: La règle n'est vérifiée qu'au placement. Si les labels du nœud changent ensuite, le pod déjà lancé **reste** en place.
quiz:
- q: Un pod porte une toleration pour `gpu=true:NoSchedule` mais aucun nodeSelector. Où peut-il être planifié ?
  options:
  - Uniquement sur les nœuds GPU
  - Sur les nœuds GPU et sur tous les nœuds sans taint
  - Nulle part, il manque une affinité
  - Uniquement sur le control plane
  answer: 1
  explain: La toleration lève l'interdiction mais n'attire pas le pod. Il peut atterrir sur n'importe quel nœud compatible, GPU ou non.
- q: Tu ajoutes un taint `NoExecute` sur un nœud. Qu'arrive-t-il aux pods déjà présents qui ne le tolèrent pas ?
  options:
  - Rien, le taint ne s'applique qu'aux nouveaux pods
  - Ils sont évincés
  - Ils passent en Pending
  - Ils sont redémarrés sur place
  answer: 1
  explain: '`NoExecute` évince les pods sans toleration. Avec `tolerationSeconds`, un pod peut rester un temps donné avant d''être évincé.'
- q: Pourquoi tes pods applicatifs ne tournent-ils pas sur le control plane d'un cluster kubeadm ?
  options:
  - Le kubelet n'y tourne pas
  - Le nœud porte le taint `node-role.kubernetes.io/control-plane:NoSchedule`
  - Le scheduler ignore ce nœud par construction
  - Il n'a pas de runtime de conteneurs
  answer: 1
  explain: Il suffit de tolérer ce taint (ou de le retirer) pour pouvoir y planifier des pods, ce qu'on fait parfois sur un cluster de test à un seul nœud.
---

Deux mécanismes complémentaires pour contrôler **où** les pods atterrissent. Ils se ressemblent, mais ne regardent pas dans le même sens.

<div class="compare">
  <div><b>Taint → repousse</b><span>Posé sur le <em>nœud</em>. Aucun pod n'y est planifié sauf s'il porte la toleration correspondante.</span></div>
  <div><b>Affinity → attire</b><span>Déclarée dans le <em>pod</em>. Le scheduler préfère ou exige des nœuds portant certains labels.</span></div>
</div>


> **Les termes et outils cités dans cette fiche.**
> - **scheduler** : le composant qui décide où placer une charge de travail (sur quel nœud ou quel hôte).
> - **GPU** : le processeur graphique, qui fait énormément de calculs en parallèle (IA, rendu).

## Dédier des nœuds GPU

```bash
# 1. On repousse tout le monde du nœud
kubectl taint nodes gpu-01 gpu=true:NoSchedule
kubectl label nodes gpu-01 accelerator=nvidia
```

```yaml
# 2. Le pod tolère le taint… et cible le nœud
spec:
  tolerations:
    - key: "gpu"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
  nodeSelector:
    accelerator: nvidia
```

> **Piège classique.** Une toleration *autorise* un pod à aller sur le nœud, elle ne l'y *envoie* pas. Pour réserver vraiment des nœuds, il faut combiner taint + affinité (ou nodeSelector).

<!-- schema:taints -->
<figure class="diagram"><svg viewBox="0 0 680 236" role="img" aria-label="Un taint repousse, une tolération laisse passer" style="--minw:560px"><defs><marker id="g10-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g10-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g10-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g10-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="16" y="30" width="160" height="56" rx="9"/></g><text x="96.0" y="55.0" class="dg-t" text-anchor="middle" style="--d:0">pod ia</text><text x="96.0" y="73.0" class="dg-s" text-anchor="middle" style="--d:0">tolère gpu=true</text><g class="dg-box dg-pop" style="--d:0"><rect x="16" y="150" width="160" height="56" rx="9"/></g><text x="96.0" y="175.0" class="dg-t" text-anchor="middle" style="--d:0">pod web</text><text x="96.0" y="193.0" class="dg-s" text-anchor="middle" style="--d:0">aucune tolération</text><rect x="300" y="14" width="200" height="92" rx="12" class="dg-zone dg-za"/><text x="312" y="32" class="dg-zl" text-anchor="start">nœud gpu-1</text><text x="400" y="58" class="dg-at" text-anchor="middle">taint</text><text x="400" y="76" class="dg-s" text-anchor="middle">gpu=true:NoSchedule</text><rect x="300" y="132" width="200" height="92" rx="12" class="dg-zone "/><text x="312" y="150" class="dg-zl" text-anchor="start">nœud std-1</text><text x="400" y="184" class="dg-s" text-anchor="middle">pas de taint</text><path d="M176 58 L296 58" class="dg-l ok thick draw" marker-end="url(#g10-ok)" pathLength="1" style="--d:1"/><path d="M176 168 C 230 168, 250 110, 290 92" class="dg-l a dash" style="--d:2"/><text x="296" y="98" class="dg-at" text-anchor="middle">✗</text><path d="M176 186 L296 186" class="dg-l c thick draw" marker-end="url(#g10-c)" pathLength="1" style="--d:3"/><g class="dg-box dg-ghost dg-pop" style="--d:4"><rect x="530" y="30" width="134" height="56" rx="9"/></g><text x="597.0" y="48.0" class="dg-t" text-anchor="middle" style="--d:4">tolérer ≠ attirer</text><text x="597.0" y="66.0" class="dg-s" text-anchor="middle" style="--d:4"><tspan x="597.0" dy="0">il faut aussi une</tspan><tspan x="597.0" dy="14">affinité</tspan></text></svg><figcaption>Le pod ia PEUT aller sur gpu-1. Pour qu&#x27;il y aille vraiment, ajoute une affinité de nœud.</figcaption></figure>
<!-- /schema:taints -->

## Les effets d'un taint

- `NoSchedule` : aucun nouveau pod sans toleration.
- `PreferNoSchedule` : le scheduler évite le nœud, sans garantie.
- `NoExecute` : évince aussi les pods déjà présents, éventuellement après `tolerationSeconds`.

## Affinité : obligatoire ou préférée

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: topology.kubernetes.io/zone
              operator: In
              values: [eu-west-3a, eu-west-3b]
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 50
        preference:
          matchExpressions:
            - key: node.kubernetes.io/instance-type
              operator: In
              values: [m6i.large]
```

> **À retenir.** Le taint est posé sur le nœud et **repousse** les pods ; la toleration permet à un pod de passer outre ; l'affinité (ou `nodeSelector`) **attire** le pod vers certains nœuds. Pour réserver des nœuds à une appli, il faut les deux : taint + affinité.
