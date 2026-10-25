---
title: Services et découverte
chapter: 4
order: 1
duration: 9
level: intermédiaire
tags:
- CKA
cards:
- q: Quels sont les types de Service, du plus interne au plus exposé ?
  a: '`ClusterIP` (défaut, interne au cluster), `NodePort` (un port sur chaque nœud, 30000-32767), `LoadBalancer` (un load balancer externe, en général fourni par le cloud). Plus `ExternalName`, un simple alias DNS.'
- q: Différence entre `port`, `targetPort` et `nodePort` ?
  a: '`port` : le port du Service. `targetPort` : le port du conteneur. `nodePort` : le port ouvert sur chaque nœud pour un Service NodePort ou LoadBalancer.'
- q: Comment un Service sait-il vers quels pods envoyer le trafic ?
  a: Par son **selector** de labels. Le plan de contrôle tient à jour les **EndpointSlices** avec les IP des pods qui correspondent **et** qui sont Ready.
- q: Quel est le nom DNS complet du Service `api` dans le namespace `shop` ?
  a: '`api.shop.svc.cluster.local`. Depuis le même namespace, `api` suffit. Depuis un autre, `api.shop`.'
- q: Qu'est-ce qu'un Service headless ?
  a: 'Un Service avec `clusterIP: None`. Pas d''IP virtuelle : le DNS renvoie directement les IP des pods. Utilisé par les StatefulSets.'
- q: 'À quoi sert `externalTrafficPolicy: Local` ?'
  a: À garder l'**IP source du client** et à éviter un saut réseau en plus. En contrepartie, seuls les nœuds qui hébergent un pod reçoivent le trafic.
quiz:
- q: Ton Service n'a aucun endpoint. Quelle est la cause la plus probable ?
  options:
  - kube-proxy est arrêté
  - Le selector ne correspond pas aux labels des pods, ou les pods ne sont pas Ready
  - CoreDNS est en panne
  - Le Service est de type ClusterIP
  answer: 1
  explain: Compare `kubectl get svc api -o yaml` (selector) avec `kubectl get pods --show-labels`, puis vérifie les readiness probes. `kubectl get endpointslices -l kubernetes.io/service-name=api` montre ce qui est retenu.
- q: Un pod du namespace `front` doit appeler le Service `api` du namespace `back`. Quel nom utiliser ?
  options:
  - api
  - api.back
  - back.api
  - api.cluster
  answer: 1
  explain: Le nom court ne résout que dans le namespace du pod. `api.back` (ou le nom complet `api.back.svc.cluster.local`) fonctionne partout.
- q: Quel type de Service ne crée aucune règle de load balancing ?
  options:
  - ClusterIP
  - NodePort
  - ExternalName
  - LoadBalancer
  answer: 2
  explain: '`ExternalName` renvoie seulement un enregistrement DNS CNAME vers un nom externe.'
---

Les pods sont éphémères et changent d'IP. Un Service leur donne une adresse stable et répartit le trafic entre eux.


> **Les termes et outils cités dans cette fiche.**
> - **proxy** : un intermédiaire qui reçoit les requêtes et les transmet à leur place.
> - **CNI** : le standard des plugins réseau de Kubernetes (Calico, Cilium…), qui donnent une adresse IP à chaque pod.
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **NAT** : la traduction d'adresses : plusieurs machines privées sortent sur Internet avec une seule adresse publique.
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.

## Le principe

<!-- schema:service -->
<figure class="diagram"><svg viewBox="0 0 680 236" role="img" aria-label="Un Service devant ses pods" style="--minw:560px"><defs><marker id="g6-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g6-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g6-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g6-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="16" y="92" width="110" height="52" rx="9"/></g><text x="71.0" y="115.0" class="dg-t" text-anchor="middle" style="--d:0">client</text><text x="71.0" y="133.0" class="dg-s" text-anchor="middle" style="--d:0">autre pod</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="176" y="84" width="180" height="68" rx="9"/></g><text x="266.0" y="108.0" class="dg-t" text-anchor="middle" style="--d:1">Service api</text><text x="266.0" y="126.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="266.0" dy="0">IP virtuelle stable</tspan><tspan x="266.0" dy="14">selector app=api</tspan></text><path d="M126 118 L174 118" class="dg-l c flow" marker-end="url(#g6-c)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="436" y="30" width="200" height="46" rx="9"/></g><text x="536.0" y="50.0" class="dg-t" text-anchor="middle" style="--d:2">pod 10.244.1.12</text><text x="536.0" y="68.0" class="dg-s" text-anchor="middle" style="--d:2">Ready</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="436" y="96" width="200" height="46" rx="9"/></g><text x="536.0" y="116.0" class="dg-t" text-anchor="middle" style="--d:3">pod 10.244.2.8</text><text x="536.0" y="134.0" class="dg-s" text-anchor="middle" style="--d:3">Ready</text><g class="dg-box dg-off dg-pop" style="--d:4"><rect x="436" y="162" width="200" height="46" rx="9"/></g><text x="536.0" y="182.0" class="dg-t" text-anchor="middle" style="--d:4">pod 10.244.3.4</text><text x="536.0" y="200.0" class="dg-s" text-anchor="middle" style="--d:4">pas Ready</text><path d="M356 108 L396 108 L396 53 L434 53" class="dg-l c flow" marker-end="url(#g6-c)"/><path d="M356 118 L434 118" class="dg-l c flow" marker-end="url(#g6-c)"/><path d="M356 128 L396 128 L396 185 L420 185" class="dg-l a dash"/><text x="426" y="190" class="dg-at" text-anchor="middle">✗</text><text x="266" y="182" class="dg-s" text-anchor="middle">la liste des pods prêts</text><text x="266" y="196" class="dg-s" text-anchor="middle">est dans les EndpointSlices</text></svg><figcaption>Seuls les pods qui portent le bon label ET qui sont Ready reçoivent du trafic.</figcaption></figure>
<!-- /schema:service -->

Le Service sélectionne les pods par leurs labels. Seuls les pods **Ready** reçoivent du trafic. kube-proxy (ou le CNI) programme les règles sur chaque nœud.

## Les types

| Type | Accessible depuis | Usage |
| --- | --- | --- |
| `ClusterIP` | l'intérieur du cluster | communication entre services |
| `NodePort` | `<IP du nœud>:30000-32767` | tests, environnements simples |
| `LoadBalancer` | Internet ou le réseau du cloud | exposer un service en production |
| `ExternalName` | alias DNS | pointer vers un service externe |

```yaml
apiVersion: v1
kind: Service
metadata: { name: api, namespace: shop }
spec:
  selector: { app: api }
  ports:
    - port: 80          # port du Service
      targetPort: 8080  # port du conteneur
```

## Comprendre le trajet d'un paquet vers un Service

1. L'appli appelle `http://api.shop`. **CoreDNS** répond avec la ClusterIP du Service, par exemple `10.96.12.5`.
2. L'appli ouvre une connexion vers `10.96.12.5:80`.
3. Sur le **nœud de l'appli**, des règles installées par kube-proxy (ou le CNI) interceptent ce paquet et réécrivent sa destination vers l'**IP d'un pod** Ready, sur le `targetPort` : `10.244.2.7:8080`. C'est du NAT de destination (fiche « Pare-feu et NAT » du module Réseaux).
4. Le CNI achemine le paquet jusqu'au pod, éventuellement sur un autre nœud.

La ClusterIP n'appartient à **aucune** machine : rien n'« écoute » dessus. C'est pourquoi un `ping` vers elle ne répond pas, alors que `curl` sur son port fonctionne.

## Les trois ports, sans confusion

| Champ | Où | Exemple |
| --- | --- | --- |
| `port` | le port du **Service**, celui qu'appellent les clients | 80 |
| `targetPort` | le port du **conteneur**, sur lequel l'appli écoute | 8080 |
| `nodePort` | avec `NodePort`/`LoadBalancer`, le port ouvert sur **chaque nœud** | 31080 |

Une erreur fréquente : un `targetPort` qui ne correspond pas au port réel de l'appli. Le Service a des endpoints, le DNS répond, mais toutes les connexions sont refusées.

## Les endpoints, la vraie liste

Le Service lui-même ne contient pas de pods. Un contrôleur maintient des **EndpointSlices** : la liste à jour des IP des pods qui correspondent au `selector` **et** sont Ready. C'est cette liste que kube-proxy programme. Un pod qui échoue sa readiness disparaît de la liste en quelques secondes ; c'est ce qui rend les rolling updates sans coupure.

Un Service **headless** (`clusterIP: None`) n'a pas d'IP virtuelle : le DNS renvoie directement les IP des pods. C'est ce qu'utilisent les StatefulSets pour donner un nom à chaque pod (`db-0.db`).

## Le DNS

CoreDNS crée un nom pour chaque Service : `<service>.<namespace>.svc.cluster.local`. Les pods ont des domaines de recherche, donc `api` suffit dans le même namespace et `api.shop` depuis un autre.

> **Piège classique.** Un Service sans endpoint ne renvoie pas d'erreur DNS : le nom résout, mais les connexions échouent. Vérifie toujours les EndpointSlices.

```bash
kubectl get endpointslices -l kubernetes.io/service-name=api -n shop
kubectl run tmp --rm -it --image=busybox:1.36 -- wget -qO- http://api.shop
```

> **À retenir.** Un Service donne un nom DNS et une IP virtuelle stables devant des pods qui changent. Il envoie le trafic aux seuls pods **Ready** qui correspondent à son `selector` (les EndpointSlices). Si ça ne répond pas, vérifie dans l'ordre : endpoints, `targetPort`, puis l'appli.
