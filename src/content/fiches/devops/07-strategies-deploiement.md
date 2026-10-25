---
title: Stratégies de déploiement
chapter: 7
order: 1
duration: 8
level: intermédiaire
tags:
- déploiement
- kubernetes
cards:
- q: Comment fonctionne un rolling update ?
  a: Les anciens pods sont remplacés **progressivement** par les nouveaux, réglés par `maxSurge` (pods en plus) et `maxUnavailable` (pods en moins tolérés).
- q: Qu'est-ce qu'un déploiement blue/green ?
  a: 'Deux environnements complets : **blue** (actuel) et **green** (nouveau). On bascule tout le trafic d''un coup quand green est validé, et le retour arrière est immédiat.'
- q: Qu'est-ce qu'un déploiement canary ?
  a: On envoie une **petite part du trafic** (par exemple 5 %) à la nouvelle version, on observe les métriques, puis on augmente par paliers.
- q: Quelle différence entre déployer et livrer une fonctionnalité avec un feature flag ?
  a: Le code est **déployé** mais désactivé. On **active** la fonctionnalité plus tard, pour certains utilisateurs, sans redéployer.
- q: Comment revenir en arrière sur un Deployment Kubernetes ?
  a: '`kubectl rollout undo deployment/api` (ou `--to-revision=N`). En GitOps, on fait un **revert du commit** dans Git.'
- q: Quel outil permet des canary automatiques sur Kubernetes ?
  a: '**Argo Rollouts** (ou Flagger) : il remplace le Deployment, gère les paliers et peut annuler tout seul si une analyse de métriques échoue.'
quiz:
- q: Ta nouvelle version a un bug sur une migration de base de données. Quelle stratégie limite le plus l'impact ?
  options:
  - Recreate
  - Canary avec analyse des métriques
  - 'Rolling update avec maxUnavailable: 100%'
  - Déployer le vendredi soir
  answer: 1
  explain: 'Le canary n''expose qu''une petite partie des utilisateurs. Attention quand même : les migrations doivent rester compatibles avec l''ancienne version.'
- q: Pourquoi les migrations de schéma doivent-elles être rétrocompatibles en rolling update ?
  options:
  - Pour aller plus vite
  - Parce que l'ancienne et la nouvelle version tournent en même temps sur la même base
  - Parce que Kubernetes l'exige
  - Ce n'est pas nécessaire
  answer: 1
  explain: 'Pendant le rolling update, les deux versions servent du trafic. On procède en plusieurs étapes : ajouter la colonne, migrer, puis supprimer l''ancienne plus tard.'
---

Déployer souvent n'est possible que si chaque déploiement est **sans risque et réversible**.


> **Les termes et outils cités dans cette fiche.**
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **load balancer** : un répartiteur de charge qui distribue les requêtes entre plusieurs serveurs.
> - **latence** : le délai entre une demande et sa réponse.
> - **rollback** : le retour à la version précédente après un déploiement raté.

## Les stratégies

| Stratégie | Principe | Retour arrière | Coût |
| --- | --- | --- | --- |
| Recreate | tout couper, tout relancer | lent | coupure |
| Rolling | remplacement progressif | moyen | faible |
| Blue/green | deux environnements, bascule | immédiat | double infra |
| Canary | quelques % puis plus | immédiat | outillage |

<!-- schema:strategies -->
<figure class="diagram"><svg viewBox="0 0 680 280" role="img" aria-label="Trois façons de déployer" style="--minw:560px"><defs><marker id="g23-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g23-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g23-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g23-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="110" y="22" class="dg-t" text-anchor="middle">rolling update</text><g class="dg-box dg-off dg-pop" style="--d:0"><rect x="30" y="40" width="48" height="40" rx="9"/></g><text x="54.0" y="65.0" class="dg-s" text-anchor="middle" style="--d:0">v1</text><g class="dg-box dg-off dg-pop" style="--d:0"><rect x="86" y="40" width="48" height="40" rx="9"/></g><text x="110.0" y="65.0" class="dg-s" text-anchor="middle" style="--d:0">v1</text><g class="dg-box dg-off dg-pop" style="--d:0"><rect x="142" y="40" width="48" height="40" rx="9"/></g><text x="166.0" y="65.0" class="dg-s" text-anchor="middle" style="--d:0">v1</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="30" y="92" width="48" height="40" rx="9"/></g><text x="54.0" y="117.0" class="dg-s" text-anchor="middle" style="--d:1">v2</text><g class="dg-box dg-off dg-pop" style="--d:1"><rect x="86" y="92" width="48" height="40" rx="9"/></g><text x="110.0" y="117.0" class="dg-s" text-anchor="middle" style="--d:1">v1</text><g class="dg-box dg-off dg-pop" style="--d:1"><rect x="142" y="92" width="48" height="40" rx="9"/></g><text x="166.0" y="117.0" class="dg-s" text-anchor="middle" style="--d:1">v1</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="30" y="144" width="48" height="40" rx="9"/></g><text x="54.0" y="169.0" class="dg-s" text-anchor="middle" style="--d:2">v2</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="86" y="144" width="48" height="40" rx="9"/></g><text x="110.0" y="169.0" class="dg-s" text-anchor="middle" style="--d:2">v2</text><g class="dg-box dg-off dg-pop" style="--d:2"><rect x="142" y="144" width="48" height="40" rx="9"/></g><text x="166.0" y="169.0" class="dg-s" text-anchor="middle" style="--d:2">v1</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="30" y="196" width="48" height="40" rx="9"/></g><text x="54.0" y="221.0" class="dg-s" text-anchor="middle" style="--d:3">v2</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="86" y="196" width="48" height="40" rx="9"/></g><text x="110.0" y="221.0" class="dg-s" text-anchor="middle" style="--d:3">v2</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="142" y="196" width="48" height="40" rx="9"/></g><text x="166.0" y="221.0" class="dg-s" text-anchor="middle" style="--d:3">v2</text><text x="110" y="262" class="dg-s" text-anchor="middle">un pod à la fois</text><line x1="226" y1="30" x2="226" y2="250" class="dg-grid"/><text x="340" y="22" class="dg-t" text-anchor="middle">blue / green</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="280" y="50" width="120" height="44" rx="9"/></g><text x="340.0" y="77.0" class="dg-t" text-anchor="middle" style="--d:0">routeur</text><g class="dg-box dg-off dg-pop" style="--d:1"><rect x="250" y="150" width="80" height="50" rx="9"/></g><text x="290.0" y="172.0" class="dg-t" text-anchor="middle" style="--d:1">blue</text><text x="290.0" y="190.0" class="dg-s" text-anchor="middle" style="--d:1">v1</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="350" y="150" width="80" height="50" rx="9"/></g><text x="390.0" y="172.0" class="dg-t" text-anchor="middle" style="--d:2">green</text><text x="390.0" y="190.0" class="dg-s" text-anchor="middle" style="--d:2">v2</text><path d="M320 94 L290 148" class="dg-l dash"/><path d="M360 94 L390 148" class="dg-l c thick" marker-end="url(#g23-c)"/><text x="340" y="236" class="dg-s" text-anchor="middle">bascule d&#x27;un coup,</text><text x="340" y="250" class="dg-s" text-anchor="middle">retour immédiat</text><line x1="456" y1="30" x2="456" y2="250" class="dg-grid"/><text x="570" y="22" class="dg-t" text-anchor="middle">canary</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="510" y="50" width="120" height="44" rx="9"/></g><text x="570.0" y="77.0" class="dg-t" text-anchor="middle" style="--d:0">routeur</text><g class="dg-box dg-off dg-pop" style="--d:1"><rect x="480" y="150" width="90" height="50" rx="9"/></g><text x="525.0" y="172.0" class="dg-t" text-anchor="middle" style="--d:1">v1</text><text x="525.0" y="190.0" class="dg-s" text-anchor="middle" style="--d:1">95 %</text><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="590" y="150" width="76" height="50" rx="9"/></g><text x="628.0" y="172.0" class="dg-t" text-anchor="middle" style="--d:2">v2</text><text x="628.0" y="190.0" class="dg-s" text-anchor="middle" style="--d:2">5 %</text><path d="M550 94 L525 148" class="dg-l thick" marker-end="url(#g23-n)"/><path d="M600 94 L628 148" class="dg-l a" marker-end="url(#g23-a)"/><text x="570" y="236" class="dg-s" text-anchor="middle">on observe, puis</text><text x="570" y="250" class="dg-s" text-anchor="middle">25 %, 50 %, 100 %</text></svg><figcaption>Le rolling update est le défaut de Kubernetes. Blue/green et canary demandent un routage plus fin.</figcaption></figure>
<!-- /schema:strategies -->

## Rolling update bien réglé

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0     # ne jamais descendre sous la capacité
  minReadySeconds: 10
```

Sans **readinessProbe** correcte, un rolling update envoie du trafic à des pods pas encore prêts.

## Canary avec Argo Rollouts

```yaml
strategy:
  canary:
    steps:
      - setWeight: 10
      - pause: { duration: 5m }
      - setWeight: 50
      - pause: { duration: 10m }
```

## Comprendre chaque stratégie

**Recreate** : on arrête toute l'ancienne version, puis on démarre la nouvelle. Simple, mais il y a une **coupure**. Utile quand deux versions ne peuvent pas tourner en même temps (une migration de base incompatible, une appli qui prend un verrou exclusif).

**Rolling update** : on remplace les instances **petit à petit**. Pendant quelques minutes, ancienne et nouvelle version servent du trafic **en même temps**. C'est le défaut de Kubernetes. Dans l'exemple, `maxSurge: 25%` autorise 25 % de pods en plus pendant la mise à jour, et `maxUnavailable: 0` interdit de descendre sous le nombre voulu : on crée un nouveau pod, on attend qu'il soit Ready, puis on retire un ancien. `minReadySeconds: 10` impose qu'un pod reste prêt 10 s avant d'être compté comme disponible, pour écarter ceux qui crashent juste après le démarrage.

**Blue/green** : la nouvelle version (green) est déployée **à côté** de l'ancienne (blue), entièrement, et testée. Puis on bascule tout le trafic d'un coup (DNS, load balancer, sélecteur de Service). Le retour arrière est une simple re-bascule, tant que blue est gardé. Le coût : deux fois l'infra pendant la bascule.

**Canary** : on envoie un **petit pourcentage** du trafic réel (10 %) vers la nouvelle version, on compare ses **métriques** (erreurs, latence) à celles de l'ancienne, et on augmente par paliers. Si les chiffres se dégradent, on annule : seuls 10 % des utilisateurs ont été touchés, pendant quelques minutes. Argo Rollouts ou Flagger automatisent l'analyse : ils interrogent Prometheus à chaque palier et annulent tout seuls.

## La contrainte qu'on oublie : deux versions en même temps

Rolling, blue/green et canary font cohabiter deux versions. Elles doivent donc être **compatibles** : même schéma de base de données, mêmes formats de messages. Une migration qui renomme une colonne casse l'ancienne version encore en service. La technique classique, *expand and contract*, procède en trois déploiements : ajouter la nouvelle colonne (les deux versions marchent), basculer le code, puis supprimer l'ancienne colonne.

## Séparer déployer et activer

Les **feature flags** permettent de déployer du code désactivé, puis de l'activer pour certains utilisateurs, sans redéployer. Le retour arrière devient un interrupteur, et on peut faire un canary par utilisateur plutôt que par instance.

> **À retenir.** Une stratégie de déploiement ne vaut que par la vitesse du retour arrière. Teste le rollback avant d'en avoir besoin.
