---
title: GitOps avec ArgoCD
chapter: 5
order: 1
duration: 9
level: intermédiaire
tags:
- gitops
- argocd
cards:
- q: Quels sont les principes du GitOps ?
  a: L'état voulu est **déclaratif**, **versionné** dans Git, **tiré** automatiquement par un agent dans le cluster et **réconcilié** en continu.
- q: Pourquoi le modèle « pull » est-il plus sûr que le « push » depuis la CI ?
  a: 'La CI n''a **pas besoin d''accès au cluster** : c''est ArgoCD, dans le cluster, qui lit Git. Moins de secrets à exposer.'
- q: Différence entre statut **Sync** et statut **Health** dans ArgoCD ?
  a: '**Sync** : le cluster correspond-il à Git ? **Health** : les ressources fonctionnent-elles (pods prêts, rollout terminé) ? Une app peut être Synced mais Degraded.'
- q: Que font `prune` et `selfHeal` dans une sync automatique ?
  a: '`prune` **supprime** du cluster ce qui a disparu de Git. `selfHeal` **annule** les modifications manuelles faites dans le cluster.'
- q: À quoi servent les sync waves ?
  a: 'À ordonner l''application des ressources avec l''annotation `argocd.argoproj.io/sync-wave` : les vagues négatives d''abord (CRD, namespaces), puis les suivantes.'
- q: Qu'est-ce qu'un ApplicationSet ?
  a: Un générateur d'Applications ArgoCD à partir d'une liste, des clusters enregistrés ou des dossiers d'un dépôt. Utile pour déployer la même app sur plusieurs environnements.
- q: Comment la CI déclenche-t-elle un déploiement en GitOps ?
  a: Elle construit l'image, puis **met à jour le tag** dans le dépôt de manifests (commit ou MR). ArgoCD voit le changement et synchronise.
- q: 'GitOps : pourquoi le pull est-il plus sûr que le push ?'
  a: 'La CI n''a **plus de droits sur le cluster** : seul l''agent ArgoCD, dans le cluster, applique.'
- q: Une app ArgoCD Synced mais Degraded, ça veut dire ?
  a: Git est bien appliqué, mais les ressources **ne fonctionnent pas** (ex. image qui plante).
- q: 'Que fait `prune: true` ?'
  a: Supprime du cluster les ressources **retirées de Git**.
- q: Comment gérer les secrets en GitOps ?
  a: '**Sealed Secrets**, **External Secrets Operator** ou **SOPS** : jamais de secret en clair dans Git.'
quiz:
- q: Un collègue fait `kubectl scale --replicas=5` sur une app gérée par ArgoCD avec selfHeal. Que se passe-t-il ?
  options:
  - Le changement reste
  - ArgoCD remet le nombre de répliques de Git
  - ArgoCD supprime l'app
  - La sync se bloque
  answer: 1
  explain: Avec selfHeal, toute dérive par rapport à Git est corrigée. Pour changer durablement, on modifie Git.
- q: Ton app est Synced mais Degraded. Où chercher ?
  options:
  - Dans Git, le manifest est faux
  - 'Dans l''état des pods : CrashLoopBackOff, probes, image introuvable'
  - Dans la config d'ArgoCD
  - Dans le pipeline CI
  answer: 1
  explain: 'Synced signifie que le cluster correspond à Git. Degraded signifie que ce qui est déployé ne fonctionne pas : on regarde les ressources Kubernetes.'
---

**GitOps** est une façon de déployer sur Kubernetes : l'état voulu du cluster (tous les manifestes YAML) est rangé dans un dépôt Git, et un programme qui tourne **dans** le cluster s'assure en permanence que le cluster ressemble à ce dépôt. **ArgoCD** est ce programme, le plus répandu (projet open source de la CNCF, la fondation qui héberge Kubernetes). Il s'installe dans le cluster, surveille un ou plusieurs dépôts Git, compare leur contenu avec ce qui tourne réellement, et corrige les différences. Il a une interface web qui montre chaque application, son état (synchronisée ou non) et son historique. Son concurrent principal s'appelle **Flux**.

En GitOps, **Git est la seule source de vérité**. On ne fait plus `kubectl apply` : on commite, et un agent applique.


> **Les termes et outils cités dans cette fiche.**
> - **cluster** : un groupe de machines qui travaillent ensemble comme un seul système.
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…
> - **CNCF** : la fondation qui héberge Kubernetes, Prometheus et de nombreux projets cloud native.
> - **CRD** : une définition de ressource personnalisée, qui ajoute un nouveau type d'objet à Kubernetes.
> - **namespace** : un espace de noms : dans Kubernetes, une partition du cluster ; sous Linux, une isolation du noyau.
> - **pipeline** : une suite d'étapes automatiques (construire, tester, déployer) lancée à chaque modification.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.

## Le flux

<!-- schema:flux -->
<figure class="diagram"><svg viewBox="0 0 680 260" role="img" aria-label="Le flux GitOps" style="--minw:560px"><defs><marker id="g21-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g21-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g21-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g21-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="20" width="150" height="52" rx="9"/></g><text x="89.0" y="43.0" class="dg-t" text-anchor="middle" style="--d:0">dépôt app</text><text x="89.0" y="61.0" class="dg-s" text-anchor="middle" style="--d:0">code source</text><g class="dg-box dg-pop" style="--d:1"><rect x="214" y="20" width="160" height="52" rx="9"/></g><text x="294.0" y="43.0" class="dg-t" text-anchor="middle" style="--d:1">CI</text><text x="294.0" y="61.0" class="dg-s" text-anchor="middle" style="--d:1">build + push</text><g class="dg-box dg-pop" style="--d:2"><rect x="424" y="20" width="242" height="52" rx="9"/></g><text x="545.0" y="43.0" class="dg-t" text-anchor="middle" style="--d:2">registre</text><text x="545.0" y="61.0" class="dg-s" text-anchor="middle" style="--d:2">api:3f2a9c1</text><path d="M164 46 L212 46" class="dg-l" marker-end="url(#g21-n)"/><path d="M374 46 L422 46" class="dg-l" marker-end="url(#g21-n)"/><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="214" y="120" width="160" height="56" rx="9"/></g><text x="294.0" y="145.0" class="dg-t" text-anchor="middle" style="--d:3">dépôt manifests</text><text x="294.0" y="163.0" class="dg-s" text-anchor="middle" style="--d:3">image: api:3f2a9c1</text><path d="M294 72 L294 118" class="dg-l c" marker-end="url(#g21-c)"/><text x="294.0" y="99.0" class="dg-s" text-anchor="middle">commit du tag</text><rect x="424" y="104" width="242" height="140" rx="12" class="dg-zone dg-zc"/><text x="436" y="122" class="dg-zl" text-anchor="start">cluster</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="440" y="130" width="210" height="52" rx="9"/></g><text x="545.0" y="153.0" class="dg-t" text-anchor="middle" style="--d:4">ArgoCD</text><text x="545.0" y="171.0" class="dg-s" text-anchor="middle" style="--d:4">compare Git et cluster</text><g class="dg-box dg-pop" style="--d:5"><rect x="440" y="194" width="210" height="38" rx="9"/></g><text x="545.0" y="218.0" class="dg-s" text-anchor="middle" style="--d:5">Deployment api</text><path d="M438 148 L374 148" class="dg-l c flow" marker-end="url(#g21-c)"/><text x="406.0" y="142.0" class="dg-s" text-anchor="middle">pull</text><path d="M545 182 L545 192" class="dg-l c" marker-end="url(#g21-c)"/><text x="110" y="210" class="dg-s" text-anchor="middle">la CI n&#x27;a aucun accès</text><text x="110" y="224" class="dg-s" text-anchor="middle">au cluster</text></svg><figcaption>ArgoCD tire l&#x27;état voulu depuis Git et corrige toute différence dans le cluster.</figcaption></figure>
<!-- /schema:flux -->

## Une Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: api
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://gitlab.com/fares/manifests.git
    targetRevision: main
    path: apps/api/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: api
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions: [CreateNamespace=true]
```

## Organiser plusieurs apps

- **App of apps** : une Application qui pointe vers un dossier d'Applications.
- **ApplicationSet** : génère les Applications (une par cluster, par environnement, par dossier).
- **Sync waves** : CRD et namespaces en vague `-1`, l'app en `0`, les jobs de vérification en `1`.

## Pull plutôt que push

Dans un pipeline classique, la CI **pousse** vers le cluster avec `kubectl` ou `helm` : elle doit détenir des identifiants d'administration du cluster. En GitOps, un agent **dans** le cluster **tire** l'état depuis Git.

| Push (CI déploie) | Pull (GitOps) |
| --- | --- |
| La CI a des droits sur le cluster | Seul l'agent a des droits, la CI ne touche qu'à Git |
| Un changement manuel dans le cluster reste invisible | La dérive est détectée et corrigée |
| Retour arrière : relancer un ancien pipeline | Retour arrière : `git revert` |
| Audit dans les logs de CI | Audit dans l'historique Git |

## Les états d'une Application

- **Synced / OutOfSync** : le cluster correspond-il à Git ?
- **Healthy / Progressing / Degraded** : les ressources fonctionnent-elles (pods prêts, rollout terminé) ?

Une app peut être **Synced mais Degraded** : Git a bien été appliqué, mais l'image plante. Les deux indicateurs se lisent séparément.

## `prune` et `selfHeal`

- `selfHeal: true` : un changement fait à la main dans le cluster est **annulé** pour revenir à Git.
- `prune: true` : une ressource retirée de Git est **supprimée** du cluster. Sans `prune`, elle reste orpheline.

## Séparer code et manifests

On garde en général un dépôt de **code** (qui construit l'image) et un dépôt de **manifests** (que lit ArgoCD). La CI du code construit l'image, puis met à jour le tag dans le dépôt de manifests via une MR. Cela évite qu'un commit applicatif déclenche une boucle de déploiements, et sépare les droits.

## Les secrets

Git ne doit pas contenir de secrets en clair. Les options courantes : **Sealed Secrets** (chiffrés dans Git, déchiffrés dans le cluster), **External Secrets Operator** (référence vers Vault ou un Secrets Manager), ou **SOPS**.

> **À retenir.** Si ce n'est pas dans Git, ça n'existe pas. Un changement fait à la main dans le cluster sera effacé.
