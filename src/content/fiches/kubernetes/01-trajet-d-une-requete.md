---
title: Le trajet d'un kubectl apply
chapter: 1
order: 2
duration: 7
level: intermédiaire
tags:
- CKA
cards:
- q: Dans quel ordre l'API server traite-t-il une requête ?
  a: '**Authentification** (qui es-tu ?), **autorisation** (as-tu le droit ?, souvent RBAC), **admission** (mutation puis validation), puis écriture dans etcd.'
- q: Quelle est la différence entre un admission controller *mutating* et *validating* ?
  a: Le **mutating** peut modifier l'objet (ajouter un sidecar, des valeurs par défaut). Le **validating** ne peut qu'accepter ou refuser. Les mutations passent toujours en premier.
- q: Après un `kubectl apply` d'un Deployment, qui crée réellement les pods ?
  a: Le contrôleur Deployment crée un **ReplicaSet**, et c'est le contrôleur ReplicaSet qui crée les **pods**. Le scheduler leur choisit ensuite un nœud.
- q: Quelles interfaces le kubelet utilise-t-il pour démarrer un pod ?
  a: '**CRI** pour le runtime de conteneurs, **CNI** pour le réseau du pod, **CSI** pour les volumes.'
- q: Comment tester un manifeste contre les règles d'admission du cluster sans rien créer ?
  a: '`kubectl apply --dry-run=server -f app.yaml` : la requête passe par toute la chaîne, admission comprise, mais n''est pas enregistrée.'
quiz:
- q: Un `kubectl apply` échoue avec `Forbidden`. À quelle étape la requête a-t-elle été refusée ?
  options:
  - Authentification
  - Autorisation
  - Écriture dans etcd
  - Planification
  answer: 1
  explain: '`Forbidden` (403) signifie que tu es bien identifié mais que tu n''as pas le droit. Une erreur d''authentification donne `Unauthorized` (401). Vérifie avec `kubectl auth can-i`.'
- q: Ton pod est créé mais reste sans nœud. Quel composant faut-il regarder en premier ?
  options:
  - Le kubelet
  - Le kube-scheduler
  - kube-proxy
  - Le contrôleur ReplicaSet
  answer: 1
  explain: Un pod sans `nodeName` attend le scheduler. `kubectl describe pod` montre ses événements, par exemple `FailedScheduling` avec la raison.
- q: Quel mécanisme permet à un outil comme Istio d'injecter un sidecar dans tes pods ?
  options:
  - Un mutating admission webhook
  - Un DaemonSet
  - Une NetworkPolicy
  - Un init container ajouté par le kubelet
  answer: 0
  explain: Le webhook reçoit l'objet Pod avant son enregistrement et renvoie un patch qui ajoute le conteneur.
---

Suivre une requête de bout en bout est le meilleur moyen de comprendre qui fait quoi dans un cluster, et donc où chercher quand ça casse.

> **Les outils et sigles cités dans cette fiche.**
> - **API server** : le point d'entrée unique du cluster ; tout le monde (toi, les contrôleurs, les nœuds) passe par lui. **etcd** : la base de données clé-valeur où il range l'état du cluster.
> - **OIDC** (OpenID Connect) : un standard de connexion qui permet de s'authentifier au cluster avec le compte de l'entreprise (Google, Azure AD, Keycloak…). **ServiceAccount** : l'identité d'un pod auprès de l'API.
> - **RBAC** (Role-Based Access Control) : les règles qui disent qui a le droit de faire quoi sur quelles ressources.
> - **Admission** : l'étape où des contrôleurs modifient ou refusent un objet avant son enregistrement. **Kyverno** et **OPA Gatekeeper** sont des moteurs de règles qu'on y branche (« refuser les images sans version », etc.).
> - **Scheduler** : choisit le nœud de chaque pod. **kubelet** : l'agent de chaque nœud qui lance réellement les pods.
> - **CSI**, **CNI**, **CRI** : trois interfaces standard par lesquelles le kubelet délègue le stockage (Container Storage Interface), le réseau (Container Network Interface) et l'exécution des conteneurs (Container Runtime Interface). **containerd** et **CRI-O** sont les deux runtimes courants.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **webhook** : un appel HTTP automatique envoyé par un outil quand un événement se produit.

<!-- schema:hub -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="Le trajet d&#x27;un kubectl apply" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="250" y="122" width="180" height="56" rx="9"/></g><text x="340.0" y="147.0" class="dg-t" text-anchor="middle" style="--d:0">kube-apiserver</text><text x="340.0" y="165.0" class="dg-s" text-anchor="middle" style="--d:0">stocke et notifie</text><g class="dg-box dg-pop" style="--d:0"><rect x="20" y="124" width="120" height="52" rx="9"/></g><text x="80.0" y="147.0" class="dg-t" text-anchor="middle" style="--d:0">kubectl apply</text><text x="80.0" y="165.0" class="dg-s" text-anchor="middle" style="--d:0">Deployment</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="280" y="236" width="120" height="50" rx="9"/></g><text x="340.0" y="266.0" class="dg-t" text-anchor="middle" style="--d:1">etcd</text><g class="dg-box dg-pop" style="--d:2"><rect x="40" y="18" width="170" height="52" rx="9"/></g><text x="125.0" y="41.0" class="dg-t" text-anchor="middle" style="--d:2">controller-manager</text><text x="125.0" y="59.0" class="dg-s" text-anchor="middle" style="--d:2">crée ReplicaSet et Pods</text><g class="dg-box dg-pop" style="--d:3"><rect x="470" y="18" width="170" height="52" rx="9"/></g><text x="555.0" y="41.0" class="dg-t" text-anchor="middle" style="--d:3">scheduler</text><text x="555.0" y="59.0" class="dg-s" text-anchor="middle" style="--d:3">choisit un nœud</text><g class="dg-box dg-pop" style="--d:4"><rect x="530" y="124" width="130" height="52" rx="9"/></g><text x="595.0" y="147.0" class="dg-t" text-anchor="middle" style="--d:4">kubelet</text><text x="595.0" y="165.0" class="dg-s" text-anchor="middle" style="--d:4">sur le nœud choisi</text><g class="dg-box dg-pop" style="--d:5"><rect x="530" y="236" width="130" height="50" rx="9"/></g><text x="595.0" y="258.0" class="dg-t" text-anchor="middle" style="--d:5">containerd</text><text x="595.0" y="276.0" class="dg-s" text-anchor="middle" style="--d:5">lance les conteneurs</text><path d="M140 150 L248 150" class="dg-l c" marker-end="url(#g2-c)" style="--d:0"/><circle cx="194" cy="150" r="10" class="dg-dot dg-c dg-pop" style="--d:0"/><text x="194" y="154" class="dg-w" text-anchor="middle" style="--d:0">1</text><path d="M340 180 L340 234" class="dg-l c" marker-end="url(#g2-c)" style="--d:1"/><circle cx="340" cy="207" r="10" class="dg-dot dg-c dg-pop" style="--d:1"/><text x="340" y="211" class="dg-w" text-anchor="middle" style="--d:1">2</text><path d="M210 60 L290 120" class="dg-l c" marker-end="url(#g2-c)" marker-start="url(#g2-c)" style="--d:2"/><circle cx="250" cy="90" r="10" class="dg-dot dg-c dg-pop" style="--d:2"/><text x="250" y="94" class="dg-w" text-anchor="middle" style="--d:2">3</text><path d="M470 60 L392 120" class="dg-l c" marker-end="url(#g2-c)" marker-start="url(#g2-c)" style="--d:3"/><circle cx="431" cy="90" r="10" class="dg-dot dg-c dg-pop" style="--d:3"/><text x="431" y="94" class="dg-w" text-anchor="middle" style="--d:3">4</text><path d="M432 150 L528 150" class="dg-l c" marker-end="url(#g2-c)" marker-start="url(#g2-c)" style="--d:4"/><circle cx="480" cy="150" r="10" class="dg-dot dg-c dg-pop" style="--d:4"/><text x="480" y="154" class="dg-w" text-anchor="middle" style="--d:4">5</text><path d="M595 178 L595 234" class="dg-l c" marker-end="url(#g2-c)" style="--d:5"/><circle cx="595" cy="206" r="10" class="dg-dot dg-c dg-pop" style="--d:5"/><text x="595" y="210" class="dg-w" text-anchor="middle" style="--d:5">6</text><text x="250" y="112" class="dg-s" text-anchor="end">watch</text><text x="440" y="112" class="dg-s" text-anchor="start">watch</text></svg><figcaption>1 la requête arrive, 2 elle est enregistrée, 3 les contrôleurs créent les Pods, 4 le scheduler leur donne un nœud, 5 le kubelet le voit, 6 il lance les conteneurs.</figcaption></figure>
<!-- /schema:hub -->

## 1. L'API server reçoit la requête

```
kubectl apply ──► authentification ──► autorisation ──► admission ──► etcd
                   certificat, token     RBAC            mutating
                   OIDC…                                 puis validating
```

- **Authentification** : certificat client, token de ServiceAccount, OIDC… Échec : `401 Unauthorized`.
- **Autorisation** : en général RBAC. Échec : `403 Forbidden`.
- **Admission** : les contrôleurs *mutating* modifient l'objet, puis les *validating* l'acceptent ou le refusent. C'est ici qu'agissent `LimitRanger`, `ResourceQuota`, Pod Security Admission, et les webhooks (Kyverno, OPA Gatekeeper, Istio…).

## 2. Les contrôleurs réagissent

Le Deployment est enregistré. Le contrôleur Deployment le voit et crée un ReplicaSet. Le contrôleur ReplicaSet crée les pods. Personne ne s'appelle directement : chacun **observe** l'API et y écrit.

## 3. Le scheduler place les pods

Il filtre les nœuds possibles (ressources, taints, affinités), leur donne un score, puis écrit le nœud choisi dans `spec.nodeName`.

## 4. Le kubelet démarre le pod

Sur le nœud choisi, le kubelet voit le pod qui lui est assigné et :

1. prépare les volumes (via **CSI**),
2. crée le réseau du pod (via **CNI**),
3. lance les conteneurs (via **CRI**, avec containerd ou CRI-O),
4. remonte le statut à l'API.

> **À retenir.** Quand quelque chose bloque, demande-toi à quelle étape. `kubectl describe` et `kubectl get events` donnent presque toujours la réponse.

```bash
kubectl get events -A --sort-by=.lastTimestamp | tail -20
kubectl apply --dry-run=server -f app.yaml
```
