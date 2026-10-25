---
title: NetworkPolicies
chapter: 8
order: 3
duration: 9
level: intermédiaire
tags:
- CKA
- CKS
cards:
- q: Sans aucune NetworkPolicy, que peut joindre un pod ?
  a: '**Tout** : tous les pods de tous les namespaces, et l''extérieur. Le réseau Kubernetes est ouvert par défaut.'
- q: Que se passe-t-il dès qu'une NetworkPolicy sélectionne un pod en `Ingress` ?
  a: Tout le trafic entrant vers ce pod est **refusé**, sauf ce qu'autorise une des policies qui le sélectionnent. Les policies s'additionnent.
- q: Que faut-il côté cluster pour que les NetworkPolicies fonctionnent ?
  a: 'Un **CNI qui les applique** : Calico, Cilium, Antrea… Avec Flannel seul, elles sont acceptées par l''API mais **ignorées**.'
- q: 'Quelle est la différence entre ces deux écritures : un seul élément `from` avec `namespaceSelector` **et** `podSelector`, ou deux éléments séparés ?'
  a: 'Dans le **même** élément : ET (les pods correspondants **dans** les namespaces correspondants). En **deux** éléments : OU (tous les pods de ces namespaces, ou ces pods dans le namespace local).'
- q: Après une policy « deny all » en egress, qu'oublie-t-on presque toujours d'autoriser ?
  a: 'Le **DNS** : le port 53 en UDP et TCP vers CoreDNS dans `kube-system`. Sans lui, plus aucun nom ne résout.'
quiz:
- q: Tu appliques une policy « deny all egress » et ton appli ne joint plus son API, même avec une règle qui l'autorise par son IP. Cause probable ?
  options:
  - Le DNS est bloqué
  - Le Service est de type ClusterIP
  - La readiness probe échoue
  - Le RBAC bloque la connexion
  answer: 0
  explain: L'appli doit d'abord résoudre le nom. Ajoute une règle egress vers `kube-system` sur le port 53, en UDP et en TCP.
- q: Tu crées une NetworkPolicy, mais tout passe encore. Que vérifier en premier ?
  options:
  - Que le CNI du cluster applique les NetworkPolicies
  - Que les pods ont une liveness probe
  - Que le namespace a une ResourceQuota
  - Que kube-proxy est en mode IPVS
  answer: 0
  explain: L'API accepte l'objet même si personne ne l'applique. Ensuite, vérifie que le `podSelector` sélectionne bien les pods visés.
---

Par défaut, n'importe quel pod peut parler à n'importe quel autre. Les NetworkPolicies sont le pare-feu du cluster, à l'échelle des pods.


> **Les termes et outils cités dans cette fiche.**
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **RBAC** : le contrôle d'accès par rôles : on donne des droits à des rôles, puis des rôles aux personnes ou programmes.
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **CNI** : le standard des plugins réseau de Kubernetes (Calico, Cilium…), qui donnent une adresse IP à chaque pod.

## Commencer par tout fermer

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: shop }
spec:
  podSelector: {}              # tous les pods du namespace
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns, namespace: shop }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
          podSelector: { matchLabels: { k8s-app: kube-dns } }
      ports:
        - { protocol: UDP, port: 53 }
        - { protocol: TCP, port: 53 }
```

<!-- schema:policies -->
<figure class="diagram"><svg viewBox="0 0 680 262" role="img" aria-label="Une politique réseau en refus par défaut" style="--minw:560px"><defs><marker id="g11-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g11-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g11-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g11-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="16" y="14" width="470" height="234" rx="12" class="dg-zone dg-zc"/><text x="28" y="32" class="dg-zl" text-anchor="start">namespace shop</text><g class="dg-box dg-pop" style="--d:0"><rect x="40" y="52" width="120" height="50" rx="9"/></g><text x="100.0" y="82.0" class="dg-t" text-anchor="middle" style="--d:0">frontend</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="200" y="52" width="120" height="50" rx="9"/></g><text x="260.0" y="74.0" class="dg-t" text-anchor="middle" style="--d:1">api</text><text x="260.0" y="92.0" class="dg-s" text-anchor="middle" style="--d:1">port 8080</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="360" y="52" width="110" height="50" rx="9"/></g><text x="415.0" y="74.0" class="dg-t" text-anchor="middle" style="--d:2">postgres</text><text x="415.0" y="92.0" class="dg-s" text-anchor="middle" style="--d:2">port 5432</text><path d="M160 77 L198 77" class="dg-l ok thick" marker-end="url(#g11-ok)"/><path d="M320 77 L358 77" class="dg-l ok thick" marker-end="url(#g11-ok)"/><path d="M100 104 C 100 170, 410 170, 412 106" class="dg-l a dash"/><text x="256" y="160" class="dg-at" text-anchor="middle">✗ frontend → postgres refusé</text><g class="dg-box dg-off dg-pop" style="--d:3"><rect x="40" y="186" width="430" height="44" rx="9"/></g><text x="255.0" y="213.0" class="dg-t" text-anchor="middle" style="--d:3">default-deny : tout est fermé, sauf ce qu&#x27;une policy autorise</text><rect x="510" y="14" width="154" height="108" rx="12" class="dg-zone "/><text x="522" y="32" class="dg-zl" text-anchor="start">autre namespace</text><g class="dg-box dg-pop" style="--d:4"><rect x="530" y="48" width="114" height="46" rx="9"/></g><text x="587.0" y="76.0" class="dg-t" text-anchor="middle" style="--d:4">pod x</text><path d="M530 70 C 480 70, 300 20, 262 50" class="dg-l a dash"/><text x="420" y="34" class="dg-at" text-anchor="middle">✗</text><rect x="510" y="140" width="154" height="108" rx="12" class="dg-zone "/><text x="522" y="158" class="dg-zl" text-anchor="start">kube-system</text><g class="dg-box dg-pop" style="--d:4"><rect x="530" y="174" width="114" height="46" rx="9"/></g><text x="587.0" y="194.0" class="dg-t" text-anchor="middle" style="--d:4">CoreDNS</text><text x="587.0" y="212.0" class="dg-s" text-anchor="middle" style="--d:4">UDP 53</text><path d="M260 104 C 260 130, 480 210, 528 197" class="dg-l ok dash" marker-end="url(#g11-ok)"/><text x="395" y="128" class="dg-s" text-anchor="middle">egress DNS à ouvrir</text></svg><figcaption>On ferme tout, puis on ouvre seulement les flux attendus, sans oublier le DNS.</figcaption></figure>
<!-- /schema:policies -->

## Puis ouvrir le nécessaire

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: api-from-front, namespace: shop }
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector: { matchLabels: { app: front } }
      ports: [{ protocol: TCP, port: 8080 }]
```

## Comprendre le modèle

Trois idées suffisent à raisonner juste :

1. **Sans aucune policy, tout est ouvert.** Un pod non sélectionné par une policy accepte tout et peut tout joindre.
2. **Dès qu'une policy sélectionne un pod** (`podSelector`) pour un sens (`Ingress` ou `Egress`), ce sens devient **fermé par défaut** pour ce pod : seul ce qu'une policy autorise passe.
3. **Les policies s'additionnent.** Comme RBAC, il n'y a que des autorisations. Plusieurs policies qui sélectionnent le même pod cumulent leurs autorisations ; aucune ne peut en retirer une autre.

C'est pour ça qu'on commence par un `default-deny` (qui sélectionne tous les pods sans rien autoriser), puis qu'on ajoute des policies d'ouverture, chacune lisible isolément.

Une policy sur un pod **qui reçoit** ne suffit pas toujours : si le pod **qui appelle** est lui aussi sous `default-deny` en `Egress`, il faut aussi autoriser sa sortie. Un flux traverse deux contrôles, comme un pare-feu à chaque extrémité.

## Pourquoi autoriser le DNS en premier

Avec un `default-deny` en sortie, les pods ne peuvent même plus joindre **CoreDNS** : tous les noms échouent, et on croit à une panne générale. La policy `allow-dns` rouvre le port 53 vers les pods `kube-dns` de `kube-system`. C'est le premier réflexe à avoir après un `default-deny` en `Egress`.

Les NetworkPolicies travaillent par **labels** et par **ports** (L3/L4). Elles ne savent pas filtrer par chemin HTTP ni par nom de domaine externe : pour ça, il faut les extensions de ton CNI (CiliumNetworkPolicy) ou un service mesh. Et rappel : elles n'ont d'effet que si le CNI les applique.

## ET ou OU

```yaml
# Un seul élément : les pods etl DE l'équipe data (ET)
from:
  - namespaceSelector: { matchLabels: { team: data } }
    podSelector: { matchLabels: { app: etl } }
```

```yaml
# Deux éléments : toute l'équipe data OU les pods etl du namespace local (OU)
from:
  - namespaceSelector: { matchLabels: { team: data } }
  - podSelector: { matchLabels: { app: etl } }
```

> **Piège classique.** Un tiret de trop, ou de moins, transforme un ET en OU. C'est l'erreur la plus fréquente avec les NetworkPolicies, relis toujours l'indentation.

> **À retenir.** Sans policy, tout est ouvert ; dès qu'une policy sélectionne un pod, le sens concerné est fermé sauf ce qui est autorisé, et les autorisations s'additionnent. Commence par un `default-deny`, rouvre le DNS, puis ouvre flux par flux. Et vérifie que ton CNI applique bien les policies.
