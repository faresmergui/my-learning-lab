---
title: Les composants du cluster
chapter: 1
order: 1
duration: 9
level: intermédiaire
tags:
- CKA
cards:
- q: Quel est le seul composant qui lit et écrit directement dans etcd ?
  a: Le **kube-apiserver**. Le scheduler, le controller-manager et les kubelets passent tous par l'API.
- q: Que fait le `kube-scheduler`, et que ne fait-il pas ?
  a: Il choisit un nœud pour chaque pod sans nœud et écrit ce choix (`spec.nodeName`) via l'API. Il ne démarre **pas** le conteneur, c'est le kubelet du nœud qui le fait.
- q: Combien de membres etcd peuvent tomber dans un cluster de 5 sans perdre le quorum ?
  a: '**2**. Le quorum est de (n/2)+1 = 3. C''est pour ça qu''on choisit un nombre impair : 4 membres ne tolèrent pas plus de pannes que 3.'
- q: Où sont les manifestes des composants du control plane sur un cluster kubeadm ?
  a: Dans `/etc/kubernetes/manifests/`. Ce sont des **static pods** que le kubelet lance directement, sans passer par le scheduler.
quiz:
- q: Le kubelet d'un nœud ne répond plus. Que voit-on en premier ?
  options:
  - Les pods du nœud sont supprimés immédiatement
  - Le nœud passe en `NotReady`, puis ses pods sont évincés après un délai
  - etcd perd le quorum
  - Le scheduler s'arrête
  answer: 1
  explain: Le node controller marque le nœud `NotReady` quand les heartbeats s'arrêtent. Par défaut, les pods tolèrent `node.kubernetes.io/unreachable` pendant 300 s avant d'être évincés.
- q: Quel composant traduit les Services en règles réseau sur chaque nœud ?
  options:
  - kube-proxy
  - kubelet
  - CoreDNS
  - kube-controller-manager
  answer: 0
  explain: '`kube-proxy` programme iptables, IPVS ou nftables. Certains CNI comme Cilium peuvent le remplacer complètement avec eBPF.'
---

Un cluster se divise en deux : le **control plane**, qui décide, et les **nœuds**, qui exécutent.
Tout le monde communique via une seule porte d'entrée : l'API.

<!-- schema:architecture -->
<figure class="diagram"><svg viewBox="0 0 680 330" role="img" aria-label="Architecture d&#x27;un cluster Kubernetes" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="140" width="92" height="48" rx="9"/></g><text x="60.0" y="161.0" class="dg-t" text-anchor="middle" style="--d:0">kubectl</text><text x="60.0" y="179.0" class="dg-s" text-anchor="middle" style="--d:0">toi</text><rect x="124" y="14" width="268" height="302" rx="12" class="dg-zone dg-zc"/><text x="136" y="32" class="dg-zl" text-anchor="start">control plane</text><g class="dg-box dg-pop" style="--d:1"><rect x="142" y="44" width="112" height="58" rx="9"/></g><text x="198.0" y="70.0" class="dg-t" text-anchor="middle" style="--d:1">scheduler</text><text x="198.0" y="88.0" class="dg-s" text-anchor="middle" style="--d:1">place les pods</text><g class="dg-box dg-pop" style="--d:1"><rect x="264" y="44" width="112" height="58" rx="9"/></g><text x="320.0" y="62.0" class="dg-t" text-anchor="middle" style="--d:1"><tspan x="320.0" dy="0">controller-</tspan><tspan x="320.0" dy="16">manager</tspan></text><text x="320.0" y="96.0" class="dg-s" text-anchor="middle" style="--d:1">boucles</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="142" y="136" width="234" height="56" rx="9"/></g><text x="259.0" y="161.0" class="dg-t" text-anchor="middle" style="--d:2">kube-apiserver</text><text x="259.0" y="179.0" class="dg-s" text-anchor="middle" style="--d:2">point d&#x27;entrée unique</text><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="142" y="238" width="112" height="58" rx="9"/></g><text x="198.0" y="264.0" class="dg-t" text-anchor="middle" style="--d:3">etcd</text><text x="198.0" y="282.0" class="dg-s" text-anchor="middle" style="--d:3">état du cluster</text><g class="dg-box dg-ghost dg-pop" style="--d:3"><rect x="264" y="238" width="112" height="58" rx="9"/></g><text x="320.0" y="256.0" class="dg-t" text-anchor="middle" style="--d:3"><tspan x="320.0" dy="0">cloud-</tspan><tspan x="320.0" dy="16">controller</tspan></text><text x="320.0" y="290.0" class="dg-s" text-anchor="middle" style="--d:3">optionnel</text><path d="M106 164 L140 164" class="dg-l c flow" marker-end="url(#g1-c)"/><path d="M198 104 L198 134" class="dg-l" marker-end="url(#g1-n)" marker-start="url(#g1-n)"/><path d="M320 104 L320 134" class="dg-l" marker-end="url(#g1-n)" marker-start="url(#g1-n)"/><path d="M198 194 L198 236" class="dg-l a" marker-end="url(#g1-a)" marker-start="url(#g1-a)"/><path d="M320 194 L320 236" class="dg-l dash" marker-end="url(#g1-n)" marker-start="url(#g1-n)"/><rect x="410" y="14" width="256" height="302" rx="12" class="dg-zone "/><text x="422" y="32" class="dg-zl" text-anchor="start">nœuds (workers)</text><rect x="424" y="40" width="228" height="124" rx="12" class="dg-zone "/><text x="436" y="58" class="dg-zl" text-anchor="start">nœud 1</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="436" y="70" width="96" height="36" rx="9"/></g><text x="484.0" y="93.0" class="dg-t" text-anchor="middle" style="--d:4">kubelet</text><g class="dg-box dg-pop" style="--d:4"><rect x="542" y="70" width="98" height="36" rx="9"/></g><text x="591.0" y="93.0" class="dg-t" text-anchor="middle" style="--d:4">kube-proxy</text><g class="dg-box dg-pop" style="--d:4"><rect x="436" y="116" width="96" height="36" rx="9"/></g><text x="484.0" y="139.0" class="dg-t" text-anchor="middle" style="--d:4">containerd</text><circle cx="566" cy="134" r="9" class="dg-dot dg-c dg-pop" style="--d:5"/><circle cx="592" cy="134" r="9" class="dg-dot dg-c dg-pop" style="--d:5"/><circle cx="618" cy="134" r="9" class="dg-dot dg-c dg-pop" style="--d:5"/><text x="592" y="160" class="dg-s" text-anchor="middle">pods</text><rect x="424" y="178" width="228" height="124" rx="12" class="dg-zone "/><text x="436" y="196" class="dg-zl" text-anchor="start">nœud 2</text><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="436" y="208" width="96" height="36" rx="9"/></g><text x="484.0" y="231.0" class="dg-t" text-anchor="middle" style="--d:5">kubelet</text><g class="dg-box dg-pop" style="--d:5"><rect x="542" y="208" width="98" height="36" rx="9"/></g><text x="591.0" y="231.0" class="dg-t" text-anchor="middle" style="--d:5">kube-proxy</text><g class="dg-box dg-pop" style="--d:5"><rect x="436" y="254" width="96" height="36" rx="9"/></g><text x="484.0" y="277.0" class="dg-t" text-anchor="middle" style="--d:5">containerd</text><circle cx="566" cy="272" r="9" class="dg-dot dg-c dg-pop" style="--d:6"/><circle cx="592" cy="272" r="9" class="dg-dot dg-c dg-pop" style="--d:6"/><circle cx="618" cy="272" r="9" class="dg-dot dg-c dg-pop" style="--d:6"/><text x="592" y="298" class="dg-s" text-anchor="middle">pods</text><path d="M436 88 L398 88 L398 156 L378 156" class="dg-l c" marker-end="url(#g1-c)"/><path d="M436 226 L404 226 L404 172 L378 172" class="dg-l c" marker-end="url(#g1-c)"/></svg><figcaption>Tout passe par l&#x27;API server : aucun composant ne parle directement à un autre, ni à etcd.</figcaption></figure>
<!-- /schema:architecture -->


> **Les termes et outils cités dans cette fiche.**
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **load balancer** : un répartiteur de charge qui distribue les requêtes entre plusieurs serveurs.
> - **réplica** : une copie identique d'un pod, d'une base ou d'une donnée.
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…
> - **EKS** : le service Kubernetes managé d'AWS.
> - **GKE** : le service Kubernetes managé de Google Cloud.
> - **AKS** : le service Kubernetes managé d'Azure.
> - **scheduler** : le composant qui décide où placer une charge de travail (sur quel nœud ou quel hôte).

## Le control plane

| Composant | Rôle |
| --- | --- |
| `kube-apiserver` | Point d'entrée unique. Authentifie, valide, puis lit et écrit dans etcd. |
| `etcd` | Base clé-valeur qui contient tout l'état du cluster. |
| `kube-scheduler` | Choisit un nœud pour chaque nouveau pod. |
| `kube-controller-manager` | Boucles de contrôle qui ramènent l'état réel vers l'état désiré (ReplicaSet, Node, Job…). |
| `cloud-controller-manager` | Fait le lien avec le cloud (load balancers, volumes, nœuds). |

## Sur chaque nœud

- **kubelet** : reçoit les pods qui lui sont assignés et les fait tourner via le runtime.
- **runtime de conteneurs** : containerd ou CRI-O, piloté par l'interface CRI.
- **kube-proxy** : traduit les Services en règles réseau.

## Comprendre : on décrit, Kubernetes réalise

Avec un script, tu dis **quoi faire** : « lance 3 conteneurs ». Avec Kubernetes, tu décris **l'état voulu** : « il doit y avoir 3 réplicas de cette image ». Tu l'écris dans un objet (un manifeste YAML), l'API le range dans etcd, et c'est tout.

Ensuite, des **contrôleurs** tournent en boucle, en permanence :

1. **observer** l'état réel (combien de pods tournent vraiment ?) ;
2. **comparer** à l'état voulu (il en faut 3) ;
3. **agir** pour réduire l'écart (en créer un, en supprimer un).

C'est la **boucle de réconciliation**. Elle explique le comportement qui surprend au début : si tu supprimes un pod d'un Deployment à la main, il revient aussitôt, car le contrôleur voit 2 pods au lieu de 3. Pour changer quelque chose durablement, on modifie l'**état voulu** (le manifeste), jamais le résultat.

Chaque objet porte d'ailleurs deux parties : `spec` (ce que tu veux, écrit par toi) et `status` (ce qui est, écrit par les contrôleurs).

## Les labels, la colle du système

Les objets ne se référencent presque jamais par leur nom, mais par leurs **labels** : des étiquettes `clé: valeur` (`app: api`, `env: prod`). Un **sélecteur** dit « tous les objets qui portent ces labels ». Un ReplicaSet compte les pods qui ont `app: api` ; un Service envoie le trafic aux pods qui ont `app: api`.

C'est souple, mais une faute de frappe dans un label suffit à « débrancher » silencieusement un Service de ses pods.

## Le cas des clusters managés

Sur EKS, GKE ou AKS, le control plane est **géré par le cloud** : tu ne vois ni etcd ni le scheduler, seulement l'API. Tu ne gères que les nœuds (et encore, pas toujours). Comprendre les composants reste utile pour lire les erreurs : un pod `Pending`, c'est le scheduler qui n'a pas trouvé de place ; un pod qui ne démarre pas sur son nœud, c'est le kubelet.

> **À retenir.** Aucun composant ne parle à un autre directement : ils observent l'API (*watch*) et y écrivent. C'est ce qui rend Kubernetes si résilient, et si facile à étendre avec des contrôleurs maison.

## Vérifier l'état du control plane

```bash
kubectl get nodes -o wide
kubectl -n kube-system get pods
kubectl get --raw='/readyz?verbose'
```
