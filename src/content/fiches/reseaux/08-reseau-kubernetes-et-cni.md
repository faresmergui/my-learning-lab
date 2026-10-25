---
title: Le réseau Kubernetes et les CNI
chapter: 8
order: 1
duration: 10
level: intermédiaire
tags:
- CKA
cards:
- q: Quelles sont les règles du modèle réseau Kubernetes ?
  a: Chaque pod a sa **propre IP**. Tous les pods peuvent se joindre **sans NAT**, quel que soit leur nœud. Les nœuds joignent aussi tous les pods.
- q: Quel est le rôle d'un plugin CNI ?
  a: 'Donner une IP à chaque pod, brancher son interface, et rendre les pods **joignables entre nœuds**. Selon le CNI : NetworkPolicies, chiffrement, observabilité.'
- q: Différence entre un réseau overlay et un réseau routé ?
  a: '**Overlay** (VXLAN, Geneve) : le trafic entre pods est encapsulé dans des paquets entre nœuds, ce qui marche partout mais réduit le MTU. **Routé** (BGP, routes du cloud) : pas d''encapsulation, mais le réseau sous-jacent doit connaître les routes des pods.'
- q: Qu'apporte Cilium par rapport à un CNI classique ?
  a: 'Il s''appuie sur **eBPF** : il peut remplacer kube-proxy, appliquer des NetworkPolicies jusqu''en L7, et offre une observabilité fine des flux avec **Hubble**.'
- q: Quels sont les modes de kube-proxy ?
  a: '**iptables** (le classique), **IPVS** (plus efficace avec beaucoup de Services) et **nftables** (le plus récent). Certains CNI comme Cilium le remplacent entièrement.'
- q: Pourquoi le CIDR des pods ne doit-il pas chevaucher celui du VPC ou du réseau d'entreprise ?
  a: 'Sinon, certaines destinations deviennent **ambiguës** : un pod qui veut joindre `10.0.5.4` ne sait plus s''il s''agit d''un autre pod ou d''une machine du réseau.'
- q: Pourquoi les conteneurs d'un même pod se parlent-ils en `localhost` ?
  a: 'Ils partagent le même namespace réseau : même IP, mêmes interfaces, même `lo`.'
- q: Qu'est-ce qu'une ClusterIP, techniquement ?
  a: Une IP virtuelle qui n'appartient à aucune machine. kube-proxy (ou le CNI) installe sur chaque nœud des règles de DNAT qui la réécrivent vers l'IP d'un pod Ready.
- q: Pourquoi `ping` vers une ClusterIP ne répond-il pas ?
  a: Les règles n'existent que pour les ports TCP/UDP déclarés par le Service. Teste avec `curl` ou `nc` sur le port du Service.
- q: Que se passe-t-il si tu crées une NetworkPolicy avec un CNI qui ne les gère pas ?
  a: 'L''API l''accepte, mais elle n''a **aucun effet** : c''est le CNI qui applique les policies.'
- q: Cause la plus fréquente d'un Service qui ne répond pas ?
  a: 'Il n''a **aucun endpoint** : le `selector` ne correspond aux labels d''aucun pod, ou les pods ne sont pas Ready. `kubectl get endpointslices` le montre.'
quiz:
- q: Dans un cluster avec un CNI en VXLAN, les petites requêtes passent entre pods de nœuds différents, mais pas les grosses. Que soupçonner ?
  options:
  - Un problème de DNS
  - Un MTU des pods mal réglé par rapport à l'encapsulation
  - Une NetworkPolicy
  - kube-proxy en mode IPVS
  answer: 1
  explain: VXLAN ajoute 50 octets d'en-tête. Avec un MTU de 1500 sous-jacent, celui des pods doit être de 1450 au plus.
- q: Quel CNI de base n'applique pas les NetworkPolicies ?
  options:
  - Calico
  - Cilium
  - Flannel
  - Antrea
  answer: 2
  explain: Flannel fournit seulement la connectivité. On le combine parfois avec Calico pour les policies (installation « Canal »).
- q: '`curl api.shop` depuis un pod donne « connection refused » ; `kubectl get endpointslices` pour `api` ne montre aucune adresse. Que vérifier ?'
  options:
  - Le CNI
  - Que le selector du Service correspond aux labels des pods, et que ceux-ci sont Ready
  - CoreDNS
  - La NetworkPolicy
  answer: 1
  explain: Sans endpoints, la ClusterIP ne mène nulle part. Le DNS fonctionne (le nom a été résolu) et le réseau aussi.
- q: Tu ajoutes une NetworkPolicy qui n'autorise que `app=front` à joindre `app=api`. Un pod `app=batch` joint toujours `api`. Le cluster utilise Flannel seul. Pourquoi ?
  options:
  - La policy est mal écrite
  - Flannel n'applique pas les NetworkPolicies
  - Il faut redémarrer les pods
  - batch est dans le même namespace
  answer: 1
  explain: Il faut un CNI qui applique les policies, comme Calico ou Cilium (ou Canal, Flannel + Calico).
- q: Ton entreprise utilise 10.96.0.0/16 pour un datacenter joint par VPN. Le cluster utilise 10.96.0.0/12 pour les Services. Que risques-tu ?
  options:
  - Rien, ce sont des réseaux différents
  - 'Les pods ne pourront pas joindre ce datacenter : les paquets seront traités comme du trafic de Service'
  - Les Services ne recevront plus d'IP
  - Le VPN tombera
  answer: 1
  explain: Les plages qui se chevauchent rendent une partie des destinations injoignables. On les choisit avant de créer le cluster.
---

Dans un cluster Kubernetes, les pods naissent, meurent et changent de nœud en permanence, chacun avec sa propre IP. Pourtant n'importe quel pod peut en joindre n'importe quel autre, sur n'importe quel nœud. Cette fiche explique qui rend ça possible : le **CNI** pour relier les pods, et les **Services** pour leur donner une adresse stable.

> **Les outils et sigles cités dans cette fiche.**
> - **CNI** (Container Network Interface) : le standard de plugin qui donne une IP aux pods et les relie entre eux. **Calico**, **Cilium** et **Flannel** sont les plus courants ; **AWS VPC CNI** et **Azure CNI** sont ceux des clouds.
> - **kubelet** : l'agent Kubernetes présent sur chaque nœud, qui lance les pods. **kube-proxy** : l'agent qui traduit les Services en règles réseau sur chaque nœud.
> - **veth** : une paire d'interfaces virtuelles reliées comme un câble, un bout dans le pod, l'autre sur le nœud.
> - **VXLAN** et **Geneve** : protocoles d'encapsulation, qui emballent un paquet dans un autre pour le transporter entre nœuds (overlay).
> - **BGP** : le protocole qu'utilisent les routeurs pour s'annoncer quels réseaux sont derrière eux. Calico s'en sert pour annoncer les plages de pods.
> - **VPC** (Virtual Private Cloud) : ton réseau privé chez un fournisseur cloud.
> - **eBPF** : une technologie qui permet d'exécuter de petits programmes vérifiés dans le noyau Linux. Cilium s'en sert pour router, filtrer et observer le trafic sans iptables ; **Hubble** est son outil d'observation.
> - **CoreDNS** : le serveur DNS interne du cluster, qui répond aux noms comme `api.shop.svc.cluster.local`.
> - **netshoot** : une image de conteneur remplie d'outils réseau (`dig`, `curl`, `tcpdump`…), à lancer temporairement pour diagnostiquer depuis l'intérieur du cluster.
> - **MTU** : taille maximale d'un paquet. L'encapsulation ajoute des octets, donc l'overlay réduit la place disponible.
> - **NAT** : la traduction d'adresses : plusieurs machines privées sortent sur Internet avec une seule adresse publique.
> - **UDP** : le protocole de transport sans connexion, rapide mais sans garantie de livraison (DNS, vidéo, VXLAN).
> - **TLS** : le protocole qui chiffre une connexion et prouve l'identité du serveur par un certificat.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **load balancer** : un répartiteur de charge qui distribue les requêtes entre plusieurs serveurs.
> - **TCP** : le protocole de transport fiable : connexion établie, données remises dans l'ordre et sans perte.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.

## Le contrat réseau de Kubernetes

Kubernetes ne fournit pas de réseau lui-même. Il impose seulement trois règles :

1. chaque pod a **sa propre IP** ;
2. tout pod peut joindre tout autre pod **directement**, sans NAT, même sur un autre nœud ;
3. les agents d'un nœud (kubelet) peuvent joindre les pods de ce nœud.

Comment ces règles sont tenues, c'est le travail d'un **plugin CNI** (Container Network Interface) que tu installes : Calico, Cilium, Flannel, le CNI de ton cloud…

## Sur un nœud : comme Docker

À l'intérieur d'un nœud, on retrouve les briques de la fiche précédente. Chaque pod a son **namespace réseau** (partagé par tous les conteneurs du pod, d'où le fait qu'ils se parlent en `localhost`). Le CNI crée une **paire veth** pour chaque pod et lui attribue une IP dans la plage du nœud (par exemple `10.244.1.0/24` pour le nœud 1).

La vraie question est **entre** les nœuds : comment un paquet pour `10.244.2.7` sait-il qu'il doit aller sur le nœud 2 ?

## Entre les nœuds : overlay ou routé

<!-- schema:cni -->
<figure class="diagram"><svg viewBox="0 0 680 260" role="img" aria-label="Le modèle réseau de Kubernetes" style="--minw:560px"><defs><marker id="g16-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g16-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g16-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g16-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="292" height="232" rx="12" class="dg-zone dg-zc"/><text x="26" y="32" class="dg-zl" text-anchor="start">nœud 1 · 10.10.16.11</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="34" y="46" width="170" height="44" rx="9"/></g><text x="119.0" y="73.0" class="dg-s" text-anchor="middle" style="--d:0">pod A 10.244.1.5</text><path d="M204 68 L244 68 L244 160" class="dg-l" marker-end="url(#g16-n)"/><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="34" y="104" width="170" height="44" rx="9"/></g><text x="119.0" y="131.0" class="dg-s" text-anchor="middle" style="--d:1">pod B 10.244.1.6</text><path d="M204 126 L244 126 L244 160" class="dg-l" marker-end="url(#g16-n)"/><g class="dg-box dg-pop" style="--d:2"><rect x="164" y="160" width="120" height="40" rx="9"/></g><text x="224.0" y="185.0" class="dg-s" text-anchor="middle" style="--d:2">cni0 / eBPF</text><rect x="374" y="14" width="292" height="232" rx="12" class="dg-zone dg-zc"/><text x="386" y="32" class="dg-zl" text-anchor="start">nœud 2 · 10.10.16.12</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="394" y="46" width="170" height="44" rx="9"/></g><text x="479.0" y="73.0" class="dg-s" text-anchor="middle" style="--d:1">pod C 10.244.2.7</text><path d="M564 68 L604 68 L604 160" class="dg-l" marker-end="url(#g16-n)"/><g class="dg-box dg-pop" style="--d:2"><rect x="524" y="160" width="120" height="40" rx="9"/></g><text x="584.0" y="185.0" class="dg-s" text-anchor="middle" style="--d:2">cni0 / eBPF</text><path d="M284 190 L522 190" class="dg-l c flow thick" marker-end="url(#g16-c)" marker-start="url(#g16-c)"/><text x="400" y="180" class="dg-s" text-anchor="middle">overlay (VXLAN)</text><text x="400" y="214" class="dg-s" text-anchor="middle">ou routage direct</text><text x="340" y="244" class="dg-ct" text-anchor="middle">règle : chaque pod joint chaque pod, sans NAT</text></svg><figcaption>Le CNI (Calico, Cilium, Flannel…) donne une IP à chaque pod et fait le lien entre les nœuds.</figcaption></figure>
<!-- /schema:cni -->

**Overlay (encapsulation).** Le CNI emballe le paquet du pod dans un autre paquet, adressé de l'IP du nœud 1 à l'IP du nœud 2 (VXLAN ou Geneve, sur UDP). Le réseau physique ne voit que du trafic entre nœuds ; le nœud 2 déballe et livre au pod. Avantage : ça marche sur **n'importe quel** réseau, sans toucher aux routeurs. Inconvénient : l'en-tête ajouté (environ 50 octets) réduit la taille utile des paquets (MTU) et coûte un peu de CPU.

**Routé (natif).** Pas d'emballage : on apprend aux routeurs que `10.244.2.0/24` se trouve derrière le nœud 2. Soit par **BGP** (Calico annonce les routes), soit parce que le cloud les gère (routes VPC). Plus performant, plus lisible avec `tcpdump`, mais il faut que le réseau sous-jacent coopère.

**IP du VPC.** Certains CNI de cloud (AWS VPC CNI, Azure CNI) donnent aux pods de **vraies IP du VPC**. Les pods sont joignables directement depuis le reste du réseau, mais ils consomment beaucoup d'adresses : il faut des sous-réseaux larges.

Le symptôme typique d'un problème de MTU en overlay : les petites requêtes passent (ping, health checks), les grosses restent bloquées (téléchargements, réponses volumineuses, poignées de main TLS avec de gros certificats).

## Les Services : une adresse qui ne bouge pas

Les IP de pods changent à chaque redémarrage. Les clients ne peuvent pas les suivre. Un **Service** donne une **IP virtuelle stable** (ClusterIP, dans une plage dédiée comme `10.96.0.0/12`) et un nom DNS (`api.shop.svc.cluster.local`).

Cette IP n'appartient à aucune machine. C'est un **DNAT** distribué : sur chaque nœud, **kube-proxy** (ou le CNI, avec Cilium) installe des règles qui disent « un paquet vers `10.96.12.5:80` → réécris la destination vers l'IP d'un des pods Ready, sur le port 8080 ». La liste des pods vient des **EndpointSlices**, mises à jour en permanence selon les readiness probes.

| Mode de kube-proxy | Fonctionnement |
| --- | --- |
| iptables | une chaîne de règles par Service ; simple, lent avec des milliers de Services |
| IPVS | un vrai load balancer L4 du noyau ; plus efficace à grande échelle |
| nftables | successeur moderne d'iptables |
| (sans kube-proxy) | Cilium fait le même travail en **eBPF** |

Conséquence : `ping` vers une ClusterIP ne répond généralement **pas**, puisque seules les règles pour le port TCP/UDP du Service existent. Pour tester un Service, utilise `curl` ou `nc` sur son port.

## Les types de Service, vus du réseau

| Type | Ce qui se passe |
| --- | --- |
| `ClusterIP` | IP virtuelle joignable depuis l'intérieur du cluster seulement |
| `NodePort` | en plus, un port (30000-32767) ouvert sur **chaque** nœud, en DNAT vers les pods |
| `LoadBalancer` | en plus, le cloud crée un load balancer externe qui envoie vers les nœuds (ou directement les pods) |
| Ingress / Gateway API | un reverse proxy L7 (nginx, Envoy…) qui route par nom et chemin vers des Services ClusterIP |

## Les NetworkPolicies

Par défaut, tout pod peut parler à tout pod : le réseau d'un cluster est **plat**. Une **NetworkPolicy** est un pare-feu par pod : « seuls les pods `app=front` peuvent joindre `app=api` sur 8080 ». Dès qu'une policy sélectionne un pod, tout ce qui n'est pas explicitement autorisé (dans le sens concerné) est refusé.

Point important : c'est le **CNI** qui applique les policies. Avec un CNI qui ne les gère pas (Flannel seul), tu peux créer des NetworkPolicies, l'API les accepte… et elles n'ont **aucun effet**.

## Les CNI les plus courants

| CNI | Mode | Points forts |
| --- | --- | --- |
| Flannel | overlay VXLAN | simple, pas de NetworkPolicies |
| Calico | routé (BGP) ou overlay | NetworkPolicies avancées, très répandu |
| Cilium | eBPF, overlay ou routé | remplace kube-proxy, policies L7, observabilité avec Hubble |
| AWS VPC CNI | IP du VPC | pods joignables directement depuis le VPC |

## Diagnostiquer

On procède par couches, du plus bas au plus haut :

```bash
kubectl get pods -A -o wide                    # IP et nœud de chaque pod
kubectl get endpointslices -n shop -l kubernetes.io/service-name=api   # le Service a-t-il des pods derrière ?
kubectl -n kube-system get pods -l k8s-app=cilium   # le CNI tourne-t-il partout ?
kubectl run tmp --rm -it --image=nicolaka/netshoot -- bash
#   ping 10.244.2.7        → pod à pod (le CNI)
#   dig api.shop           → le DNS (CoreDNS)
#   curl api.shop          → le Service (kube-proxy)
cilium status ; hubble observe --namespace shop   # avec Cilium : voir les paquets refusés
```

Un Service sans endpoints est la cause la plus fréquente : le `selector` ne correspond aux labels d'aucun pod, ou les pods ne sont pas Ready.

## Les plages à prévoir

| Plage | Exemple | Taille à prévoir |
| --- | --- | --- |
| Nœuds | sous-réseaux du VPC | selon le nombre de nœuds |
| Pods (`--cluster-cidr`) | `10.244.0.0/16` | souvent un /24 par nœud (110 pods max par défaut) |
| Services (`--service-cluster-ip-range`) | `10.96.0.0/12` | une IP par Service |

Ces plages ne doivent chevaucher **ni** le VPC, **ni** le réseau de l'entreprise, **ni** les VPN : sinon certains paquets partent dans le cluster au lieu d'aller vers leur vraie destination.

> **À retenir.** Le CNI relie les pods (overlay qui emballe, ou routé qui annonce des routes) et applique les NetworkPolicies. Les Services sont un DNAT distribué par kube-proxy vers les pods Ready. Pour diagnostiquer, teste dans l'ordre pod à pod, DNS, puis Service. Le CNI se choisit au début et se change difficilement.
