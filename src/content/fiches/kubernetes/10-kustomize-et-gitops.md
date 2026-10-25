---
title: Kustomize et GitOps avec ArgoCD
chapter: 10
order: 2
duration: 8
level: intermédiaire
tags:
- GitOps
cards:
- q: Quel est le principe de Kustomize ?
  a: 'Une **base** de manifestes YAML purs, et des **overlays** par environnement qui la modifient par patchs. Pas de templates : le YAML reste valide.'
- q: Pourquoi `configMapGenerator` ajoute-t-il un suffixe au nom du ConfigMap ?
  a: Le suffixe est un **hash du contenu**. Quand la config change, le nom change, donc le template du pod change et un rolling update est déclenché.
- q: Quels sont les quatre principes du GitOps ?
  a: L'état voulu est **déclaratif**, **versionné** dans Git, **tiré** automatiquement par un agent dans le cluster, et **réconcilié** en continu.
- q: Que font `prune` et `selfHeal` dans la `syncPolicy` d'ArgoCD ?
  a: '`prune` supprime du cluster ce qui a disparu de Git. `selfHeal` annule les modifications faites à la main dans le cluster.'
- q: À quoi sert un ApplicationSet ?
  a: 'À générer plusieurs Applications ArgoCD à partir d''un modèle : une par cluster, par dossier du dépôt, ou par environnement.'
- q: Quel avantage du modèle *pull* d'ArgoCD par rapport à un `kubectl apply` en CI ?
  a: La CI n'a **pas besoin d'accès** au cluster, et les écarts entre Git et le cluster sont détectés et corrigés en continu.
quiz:
- q: 'Quelqu''un modifie un Deployment à la main avec `kubectl edit`, et l''Application a `selfHeal: true`. Que se passe-t-il ?'
  options:
  - La modification reste
  - ArgoCD remet l'état décrit dans Git
  - ArgoCD supprime le Deployment
  - ArgoCD met à jour Git avec la modification
  answer: 1
  explain: Git est la source de vérité. Pour un changement durable, il faut passer par une merge request.
- q: Ton overlay de prod doit passer à 5 réplicas et changer le tag de l'image. Comment l'écrire avec Kustomize ?
  options:
  - Copier tous les manifestes dans le dossier prod
  - Utiliser `replicas` et `images` dans le `kustomization.yaml` de l'overlay
  - Utiliser des templates Go
  - Modifier la base
  answer: 1
  explain: Kustomize a des champs dédiés pour les cas fréquents. Les patchs servent pour le reste.
---

**Kustomize** est un outil intégré à `kubectl` (`kubectl apply -k`) qui part d'un jeu de manifestes YAML de base et lui applique des modifications par environnement, sans templates. **ArgoCD** est un programme qui tourne dans le cluster et le synchronise en permanence avec un dépôt Git : on ne déploie plus avec `kubectl apply`, on fait un commit (la fiche DevOps « GitOps et ArgoCD » le détaille).

Helm génère des manifestes à partir de templates. Kustomize part d'un autre principe : du YAML pur, ajusté par environnement. Et ArgoCD fait en sorte que le cluster reflète toujours Git.


> **Les termes et outils cités dans cette fiche.**
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…
> - **commit** : un instantané enregistré des modifications dans Git, avec un message et un auteur.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **rollback** : le retour à la version précédente après un déploiement raté.

## Kustomize : base et overlays

```
k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── staging/kustomization.yaml
    └── prod/kustomization.yaml
```

```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: shop-prod
resources: [../../base]
replicas:
  - { name: api, count: 5 }
images:
  - { name: registry.local/api, newTag: "2.1.0" }
configMapGenerator:
  - name: api-config
    literals: [LOG_LEVEL=warn]
patches:
  - path: resources-prod.yaml
```

```bash
kubectl kustomize overlays/prod      # voir le résultat
kubectl apply -k overlays/prod
```

<!-- schema:overlays -->
<figure class="diagram"><svg viewBox="0 0 680 230" role="img" aria-label="Kustomize : une base, des overlays" style="--minw:560px"><defs><marker id="g16-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g16-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g16-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g16-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="14" y="86" width="150" height="60" rx="9"/></g><text x="89.0" y="106.0" class="dg-t" text-anchor="middle" style="--d:0">base/</text><text x="89.0" y="124.0" class="dg-s" text-anchor="middle" style="--d:0"><tspan x="89.0" dy="0">deployment, service</tspan><tspan x="89.0" dy="14">communs</tspan></text><g class="dg-box dg-pop" style="--d:1"><rect x="236" y="24" width="170" height="60" rx="9"/></g><text x="321.0" y="51.0" class="dg-t" text-anchor="middle" style="--d:1">overlays/staging</text><text x="321.0" y="69.0" class="dg-s" text-anchor="middle" style="--d:1">replicas: 2</text><g class="dg-box dg-pop" style="--d:1"><rect x="236" y="148" width="170" height="60" rx="9"/></g><text x="321.0" y="168.0" class="dg-t" text-anchor="middle" style="--d:1">overlays/prod</text><text x="321.0" y="186.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="321.0" dy="0">replicas: 6</tspan><tspan x="321.0" dy="14">image: api:1.8.2</tspan></text><path d="M164 106 L200 106 L200 54 L234 54" class="dg-l c" marker-end="url(#g16-c)"/><path d="M164 126 L200 126 L200 178 L234 178" class="dg-l c" marker-end="url(#g16-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="476" y="24" width="188" height="60" rx="9"/></g><text x="570.0" y="51.0" class="dg-t" text-anchor="middle" style="--d:2">manifests staging</text><text x="570.0" y="69.0" class="dg-s" text-anchor="middle" style="--d:2">kubectl kustomize</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="476" y="148" width="188" height="60" rx="9"/></g><text x="570.0" y="175.0" class="dg-t" text-anchor="middle" style="--d:2">manifests prod</text><text x="570.0" y="193.0" class="dg-s" text-anchor="middle" style="--d:2">ce que lit ArgoCD</text><path d="M406 54 L474 54" class="dg-l flow" marker-end="url(#g16-n)"/><path d="M406 178 L474 178" class="dg-l c flow" marker-end="url(#g16-c)"/><text x="440" y="120" class="dg-s" text-anchor="middle">patchs appliqués sur la base</text></svg><figcaption>La base ne change pas. Chaque overlay ne contient que les différences de son environnement.</figcaption></figure>
<!-- /schema:overlays -->

## GitOps avec ArgoCD

```
dev ──merge──► Git (manifestes) ◄──pull── ArgoCD (dans le cluster) ──applique──► cluster
                                             └─ compare en continu, signale les écarts
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: shop-prod, namespace: argocd }
spec:
  project: default
  source:
    repoURL: https://gitlab.com/fares/shop-deploy.git
    targetRevision: main
    path: k8s/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: shop-prod
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true]
```

> **À retenir.** Sépare le dépôt de code et le dépôt de déploiement. La CI construit l'image, puis met à jour le tag dans le dépôt de déploiement. ArgoCD fait le reste.

## Helm ou Kustomize ?

| | Helm | Kustomize |
| --- | --- | --- |
| Principe | templates + valeurs | YAML pur + patchs |
| Idéal pour | distribuer une appli à d'autres (charts publics) | tes propres applis, par environnement |
| Historique et rollback | oui (releases) | non, c'est Git qui fait foi |

Les deux se combinent très bien : ArgoCD sait déployer un chart Helm, un dossier Kustomize, ou un chart Helm ajusté par Kustomize.
