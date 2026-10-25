---
title: 'RBAC : rôles et ServiceAccounts'
chapter: 8
order: 1
duration: 9
level: intermédiaire
tags:
- CKA
- CKS
cards:
- q: Différence entre Role et ClusterRole ?
  a: Un **Role** donne des droits dans **un namespace**. Un **ClusterRole** est défini pour tout le cluster et sert pour les ressources globales (nœuds, PV) ou pour être réutilisé dans plusieurs namespaces.
- q: Que se passe-t-il si une RoleBinding référence un ClusterRole ?
  a: Les droits du ClusterRole sont donnés **uniquement dans le namespace** de la RoleBinding. C'est la façon classique de réutiliser `edit` ou `view`.
- q: Peut-on interdire une action avec RBAC ?
  a: 'Non. RBAC est **uniquement additif** : il n''existe pas de règle de refus. Tout ce qui n''est pas autorisé est refusé.'
- q: Comment vérifier ce qu'une ServiceAccount a le droit de faire ?
  a: '`kubectl auth can-i --list --as=system:serviceaccount:<ns>:<sa> -n <ns>`, ou une action précise : `kubectl auth can-i delete pods --as=…`.'
- q: Les utilisateurs humains sont-ils des objets Kubernetes ?
  a: 'Non. Kubernetes ne stocke pas d''utilisateurs : il fait confiance à un certificat, un token OIDC ou un autre authentificateur. Seules les **ServiceAccounts** sont des objets.'
- q: Quels verbes RBAC sont particulièrement dangereux ?
  a: '`escalate` et `bind` (se donner plus de droits), `impersonate` (agir au nom d''un autre), et `create` sur les pods (monter n''importe quel Secret ou ServiceAccount du namespace).'
quiz:
- q: Tu veux que la ServiceAccount `ci` puisse déployer dans `staging` uniquement. Quelle combinaison ?
  options:
  - ClusterRole `edit` + ClusterRoleBinding
  - ClusterRole `edit` + RoleBinding dans `staging`
  - Role `edit` dans `kube-system`
  - Ajouter `ci` au groupe `system:masters`
  answer: 1
  explain: La RoleBinding limite les droits du ClusterRole au namespace `staging`. Une ClusterRoleBinding les donnerait partout.
- q: 'Un pod reçoit `forbidden: User "system:serviceaccount:app:default" cannot list pods`. Que faire ?'
  options:
  - Donner `cluster-admin` à la ServiceAccount default
  - Créer une ServiceAccount dédiée, un Role avec `list` sur `pods`, et une RoleBinding
  - Désactiver RBAC
  - Redémarrer l'API server
  answer: 1
  explain: 'Ne jamais élargir la ServiceAccount `default` : tous les pods du namespace en héritent. Une ServiceAccount par appli, avec le strict nécessaire.'
---

RBAC répond à une question : **qui** peut faire **quoi** sur **quelles ressources**, et **où**.


> **Les termes et outils cités dans cette fiche.**
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **jeton** : une chaîne secrète qui prouve qu'on est authentifié, à durée limitée.
> - **OIDC** : OpenID Connect, le standard de connexion par un fournisseur d'identité, qui délivre des jetons signés.

## Les quatre objets

<!-- schema:rbac -->
<figure class="diagram"><svg viewBox="0 0 680 270" role="img" aria-label="Les quatre objets RBAC" style="--minw:560px"><defs><marker id="g12-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g12-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g12-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g12-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="22" width="140" height="52" rx="9"/></g><text x="84.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:0">User</text><text x="84.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:0">fares@…</text><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="102" width="140" height="52" rx="9"/></g><text x="84.0" y="125.0" class="dg-t" text-anchor="middle" style="--d:0">Group</text><text x="84.0" y="143.0" class="dg-s" text-anchor="middle" style="--d:0">devops</text><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="182" width="140" height="52" rx="9"/></g><text x="84.0" y="205.0" class="dg-t" text-anchor="middle" style="--d:0">ServiceAccount</text><text x="84.0" y="223.0" class="dg-s" text-anchor="middle" style="--d:0">ns/argocd</text><text x="84" y="264" class="dg-zl" text-anchor="middle">qui</text><rect x="214" y="10" width="450" height="118" rx="12" class="dg-zone dg-zc"/><text x="226" y="28" class="dg-zl" text-anchor="start">namespace shop</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="232" y="44" width="160" height="56" rx="9"/></g><text x="312.0" y="69.0" class="dg-t" text-anchor="middle" style="--d:1">RoleBinding</text><text x="312.0" y="87.0" class="dg-s" text-anchor="middle" style="--d:1">relie sujets et rôle</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="484" y="44" width="160" height="56" rx="9"/></g><text x="564.0" y="69.0" class="dg-t" text-anchor="middle" style="--d:2">Role</text><text x="564.0" y="87.0" class="dg-s" text-anchor="middle" style="--d:2">get, list pods</text><path d="M392 72 L482 72" class="dg-l c" marker-end="url(#g12-c)"/><rect x="214" y="148" width="450" height="114" rx="12" class="dg-zone "/><text x="226" y="166" class="dg-zl" text-anchor="start">tout le cluster</text><g class="dg-box dg-pop" style="--d:3"><rect x="232" y="180" width="160" height="56" rx="9"/></g><text x="312.0" y="205.0" class="dg-t" text-anchor="middle" style="--d:3">ClusterRoleBinding</text><text x="312.0" y="223.0" class="dg-s" text-anchor="middle" style="--d:3">droits partout</text><g class="dg-box dg-pop" style="--d:4"><rect x="484" y="180" width="160" height="56" rx="9"/></g><text x="564.0" y="205.0" class="dg-t" text-anchor="middle" style="--d:4">ClusterRole</text><text x="564.0" y="223.0" class="dg-s" text-anchor="middle" style="--d:4">view, edit, admin…</text><path d="M392 208 L482 208" class="dg-l" marker-end="url(#g12-n)"/><path d="M392 92 C 440 120, 470 150, 520 178" class="dg-l c dash" marker-end="url(#g12-c)"/><text x="560" y="152" class="dg-s" text-anchor="middle">droits limités au ns</text><path d="M154 48 L230 66" class="dg-l c" marker-end="url(#g12-c)"/><path d="M154 128 L230 82" class="dg-l c" marker-end="url(#g12-c)"/><path d="M154 208 L230 208" class="dg-l" marker-end="url(#g12-n)"/><text x="440" y="264" class="dg-zl" text-anchor="middle">quoi</text></svg><figcaption>Un Role définit des droits, un Binding les donne à des sujets. Un RoleBinding peut réutiliser un ClusterRole, limité à son namespace.</figcaption></figure>
<!-- /schema:rbac -->

Les **sujets** sont des `User`, des `Group` ou des `ServiceAccount`.

## Les droits et leur attribution

RBAC sépare **ce qu'on a le droit de faire** de **qui en a le droit** :

| | Dans un namespace | Dans tout le cluster |
| --- | --- | --- |
| **les droits** (une liste de règles) | `Role` | `ClusterRole` |
| **l'attribution** (qui reçoit ces droits) | `RoleBinding` | `ClusterRoleBinding` |

Une **règle** se lit comme une phrase : « sur les ressources `pods` et `pods/log` du groupe d'API `""` (le groupe de base), autoriser les verbes `get`, `list`, `watch` ». Les verbes correspondent aux opérations de l'API : `get` (un objet), `list` (tous), `watch` (suivre les changements), `create`, `update`, `patch`, `delete`.

Le groupe d'API est indiqué par l'`apiVersion` de la ressource : `apps/v1` → groupe `apps` (Deployments), `v1` → groupe `""` (pods, services, secrets), `networking.k8s.io/v1` → groupe `networking.k8s.io`.

## Deux règles qui évitent les erreurs

- **RBAC n'a que des autorisations**, jamais d'interdictions. Tout est refusé par défaut, et chaque binding **ajoute** des droits. Pour retirer un droit, il faut trouver et retirer le binding qui le donne.
- **Un `RoleBinding` peut référencer un `ClusterRole`** : les droits du ClusterRole s'appliquent alors **seulement dans le namespace** du binding. C'est ainsi qu'on donne le rôle fourni `edit` à une équipe sur son seul namespace, sans réécrire de Role.

## Qui sont les sujets

- Les **User** et **Group** ne sont pas des objets Kubernetes : ils viennent de l'**authentification** (le nom dans un certificat client, ou dans le jeton OIDC de ton fournisseur d'identité). Kubernetes leur fait confiance tels quels.
- Les **ServiceAccount** sont des objets du namespace, pour les **programmes** qui tournent dans des pods. Leur nom complet dans RBAC est `system:serviceaccount:<namespace>:<nom>`.

## Une ServiceAccount pour une appli

```yaml
apiVersion: v1
kind: ServiceAccount
metadata: { name: reporter, namespace: app }
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: pod-reader, namespace: app }
rules:
  - apiGroups: [""]
    resources: [pods, pods/log]
    verbs: [get, list, watch]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: reporter-pod-reader, namespace: app }
subjects:
  - { kind: ServiceAccount, name: reporter, namespace: app }
roleRef:
  { kind: Role, name: pod-reader, apiGroup: rbac.authorization.k8s.io }
```

```bash
kubectl create role pod-reader --verb=get,list,watch --resource=pods -n app
kubectl create rolebinding reporter-pod-reader --role=pod-reader --serviceaccount=app:reporter -n app
kubectl auth can-i list pods -n app --as=system:serviceaccount:app:reporter
```

> **Piège classique.** Donner `create` sur les pods paraît anodin. Mais un pod peut monter n'importe quel Secret et utiliser n'importe quelle ServiceAccount de son namespace : c'est donc accéder à tout ce qu'ils protègent.

## Les rôles fournis

| ClusterRole | Droits |
| --- | --- |
| `view` | lecture, sans les Secrets |
| `edit` | lecture et écriture des ressources applicatives, sans le RBAC |
| `admin` | `edit` + gestion du RBAC dans le namespace |
| `cluster-admin` | tout, partout |

> **À retenir.** Un Role (ou ClusterRole) liste des droits, un RoleBinding (ou ClusterRoleBinding) les donne à un sujet. Tout est refusé par défaut et les bindings ne font qu'ajouter. Teste toujours avec `kubectl auth can-i … --as=…`, et méfie-toi des droits qui en ouvrent d'autres (`create pods`, lecture des Secrets).
