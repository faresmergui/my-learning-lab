---
title: Ingress et Gateway API
chapter: 4
order: 2
duration: 7
level: intermédiaire
tags:
- CKA
cards:
- q: Que faut-il, en plus de l'objet Ingress, pour qu'il fonctionne ?
  a: Un **Ingress controller** (Traefik, HAProxy, NGINX…). L'objet Ingress n'est qu'une configuration, c'est le contrôleur qui fait le routage.
- q: Quels sont les trois objets principaux de Gateway API, et qui les gère ?
  a: '`GatewayClass` (le fournisseur d''infra), `Gateway` (l''équipe plateforme : ports, certificats) et `HTTPRoute` (les équipes applicatives : règles de routage).'
- q: Qu'apporte Gateway API par rapport à Ingress ?
  a: Une séparation claire des rôles, des fonctions standard sans annotations propriétaires (répartition pondérée, en-têtes, redirections), et d'autres protocoles que HTTP (gRPC, TCP, TLS).
- q: Comment active-t-on HTTPS sur un Ingress ?
  a: Avec une section `tls` qui référence un Secret de type `kubernetes.io/tls`, souvent créé automatiquement par **cert-manager**.
- q: 'Différence entre `pathType: Prefix` et `pathType: Exact` ?'
  a: '`Prefix` : `/api` correspond aussi à `/api/users`. `Exact` : seulement `/api`.'
quiz:
- q: Tu crées un Ingress, mais il n'a pas d'adresse et rien ne répond. Que vérifier d'abord ?
  options:
  - Qu'un Ingress controller est installé et que `ingressClassName` le désigne
  - Que le Service est de type LoadBalancer
  - Que CoreDNS fonctionne
  - Que les pods ont une liveness probe
  answer: 0
  explain: Sans contrôleur, ou avec une mauvaise classe, aucun composant ne prend en charge l'Ingress.
- q: Tu veux envoyer 10 % du trafic vers la nouvelle version d'une appli. Quelle solution est standard ?
  options:
  - Une annotation propre à ton Ingress controller
  - Des `backendRefs` pondérés dans une HTTPRoute
  - Deux Services avec le même nom
  - Un NodePort
  answer: 1
  explain: 'Gateway API gère nativement les poids (`weight: 90` et `weight: 10`). Avec Ingress, cela dépend des annotations de chaque contrôleur.'
---

Un **Ingress** est un objet Kubernetes qui décrit des règles de routage HTTP : « `shop.fr/api` va vers le Service `api`, le reste vers `front` ». Il ne fait rien tout seul : il faut un **Ingress Controller**, un reverse proxy (nginx, Traefik, HAProxy…) installé dans le cluster, qui lit ces règles et reçoit réellement le trafic. La **Gateway API** est son successeur officiel, plus complet et mieux découpé entre l'équipe plateforme et les équipes applicatives.

Un Service `LoadBalancer` par appli coûte cher et ne sait pas router selon le nom de domaine ou le chemin. Ingress, puis Gateway API, résolvent ce problème avec un point d'entrée HTTP partagé.

<!-- schema:ingress -->
<figure class="diagram"><svg viewBox="0 0 680 246" role="img" aria-label="Le chemin d&#x27;une requête HTTP jusqu&#x27;aux pods" style="--minw:560px"><defs><marker id="g7-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g7-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g7-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g7-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="10" y="96" width="92" height="52" rx="9"/></g><text x="56.0" y="119.0" class="dg-t" text-anchor="middle" style="--d:0">client</text><text x="56.0" y="137.0" class="dg-s" text-anchor="middle" style="--d:0">HTTPS</text><g class="dg-box dg-pop" style="--d:1"><rect x="130" y="96" width="110" height="52" rx="9"/></g><text x="185.0" y="119.0" class="dg-t" text-anchor="middle" style="--d:1">load balancer</text><text x="185.0" y="137.0" class="dg-s" text-anchor="middle" style="--d:1">du cloud</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="268" y="86" width="150" height="72" rx="9"/></g><text x="343.0" y="112.0" class="dg-t" text-anchor="middle" style="--d:2">ingress controller</text><text x="343.0" y="130.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="343.0" dy="0">nginx, traefik…</tspan><tspan x="343.0" dy="14">lit les règles</tspan></text><path d="M102 122 L128 122" class="dg-l c flow" marker-end="url(#g7-c)"/><path d="M240 122 L266 122" class="dg-l c flow" marker-end="url(#g7-c)"/><g class="dg-box dg-pop" style="--d:3"><rect x="462" y="30" width="120" height="48" rx="9"/></g><text x="522.0" y="59.0" class="dg-t" text-anchor="middle" style="--d:3">Service web</text><g class="dg-box dg-pop" style="--d:3"><rect x="462" y="166" width="120" height="48" rx="9"/></g><text x="522.0" y="195.0" class="dg-t" text-anchor="middle" style="--d:3">Service api</text><path d="M418 108 L440 108 L440 54 L460 54" class="dg-l c" marker-end="url(#g7-c)"/><text x="440.0" y="73.0" class="dg-s" text-anchor="middle">shop.fr /</text><path d="M418 136 L440 136 L440 190 L460 190" class="dg-l c" marker-end="url(#g7-c)"/><text x="440.0" y="181.0" class="dg-s" text-anchor="middle">shop.fr /api</text><circle cx="610" cy="54" r="8" class="dg-dot dg-c dg-pop" style="--d:4"/><circle cx="634" cy="54" r="8" class="dg-dot dg-c dg-pop" style="--d:4"/><path d="M582 54 L598 54" class="dg-l" marker-end="url(#g7-n)"/><circle cx="610" cy="190" r="8" class="dg-dot dg-c dg-pop" style="--d:4"/><circle cx="634" cy="190" r="8" class="dg-dot dg-c dg-pop" style="--d:4"/><path d="M582 190 L598 190" class="dg-l" marker-end="url(#g7-n)"/><text x="343" y="182" class="dg-s" text-anchor="middle">TLS terminé ici</text></svg><figcaption>L&#x27;Ingress ne fait que décrire des règles. C&#x27;est le controller qui reçoit le trafic et l&#x27;applique.</figcaption></figure>
<!-- /schema:ingress -->


> **Les termes et outils cités dans cette fiche.**
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **proxy** : un intermédiaire qui reçoit les requêtes et les transmet à leur place.

## Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  ingressClassName: traefik
  tls:
    - hosts: [shop.example.com]
      secretName: shop-tls
  rules:
    - host: shop.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend: { service: { name: api, port: { number: 80 } } }
          - path: /
            pathType: Prefix
            backend: { service: { name: front, port: { number: 80 } } }
```

Ingress est simple mais limité : tout ce qui sort du routage de base passe par des **annotations propres à chaque contrôleur**.

## Gateway API, le successeur

Gateway API découpe la configuration selon qui la gère.

```
GatewayClass   ← le fournisseur (Cilium, Envoy Gateway, Traefik, Istio…)
  └─ Gateway   ← l'équipe plateforme : ports, certificats, domaines autorisés
       └─ HTTPRoute ← chaque équipe appli : chemins, en-têtes, poids
```

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: api }
spec:
  parentRefs: [{ name: public-gw }]
  hostnames: [shop.example.com]
  rules:
    - matches: [{ path: { type: PathPrefix, value: /api } }]
      backendRefs:
        - { name: api-v1, port: 80, weight: 90 }
        - { name: api-v2, port: 80, weight: 10 }
```

> **À retenir.** Ingress n'évolue plus. Pour un nouveau cluster, pars sur Gateway API. Le projet ingress-nginx, très répandu, a d'ailleurs été arrêté en 2026.
