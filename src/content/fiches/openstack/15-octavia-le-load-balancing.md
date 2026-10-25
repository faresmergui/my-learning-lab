---
title: 'Octavia : le load balancing'
chapter: 15
order: 1
duration: 11
tags:
- OpenStack
- EX210
- Octavia
cards:
- q: Quels sont les objets d'un load balancer Octavia ?
  a: Le **load balancer** (une VIP sur un sous-réseau), un ou plusieurs **listeners** (un protocole et un port, ex. HTTPS 443), des **pools** (groupes de serveurs, avec un algorithme), des **membres** (adresse et port de chaque serveur), un **health monitor** par pool, et éventuellement des **L7 policies** (routage selon l'URL ou l'en-tête).
- q: Différence entre les providers amphora et ovn ?
  a: '**amphora** lance une petite VM HAProxy par load balancer (couche 4 et 7 : HTTP, TLS, L7 policies), plus lourd mais complet. **ovn** programme l''équilibrage directement dans OVN (couche 4 seulement : TCP/UDP/SCTP), instantané et sans VM, mais sans HTTP ni TLS.'
- q: Quels sont les composants d'Octavia en mode amphora ?
  a: '**octavia-api**, **octavia-worker** (crée les amphoras via Nova et Neutron), **health-manager** (reçoit les battements de cœur des amphoras et bascule en cas de panne) et **housekeeping** (pool d''amphoras de réserve, rotation des certificats). Ils parlent aux amphoras par le **réseau de gestion** `lb-mgmt-net`.'
- q: Que signifient provisioning_status et operating_status ?
  a: '**provisioning_status** dit où en est la configuration (`ACTIVE`, `PENDING_CREATE`, `PENDING_UPDATE`, `ERROR`). **operating_status** dit si le trafic passe (`ONLINE`, `DEGRADED` si des membres sont en panne, `ERROR`, `OFFLINE`).'
- q: Comment terminer le TLS sur Octavia ?
  a: Mettre le certificat et la clé (en PKCS12) dans **Barbican**, puis créer un listener `TERMINATED_HTTPS` avec `--default-tls-container-ref` pointant vers ce secret. L'amphora déchiffre et parle en HTTP aux membres.
quiz:
- q: Le load balancer est `ACTIVE` mais `DEGRADED`. Que vérifies-tu en premier ?
  options:
  - La VIP
  - 'Le statut des membres et du health monitor : au moins un membre échoue au contrôle de santé (service arrêté, groupe de sécurité qui bloque l''amphora)'
  - Le quota
  - Keystone
  answer: 1
  explain: '`openstack loadbalancer status show <lb>` montre l''arbre complet et le statut de chaque membre.'
- q: Tu as besoin de router `/api` vers un pool et le reste vers un autre. Quel provider ?
  options:
  - ovn
  - amphora, qui gère la couche 7 et les L7 policies
  - les deux
  - aucun
  answer: 1
  explain: Le provider ovn ne fait que de la couche 4.
level: intermédiaire
---

**Octavia** fournit des **load balancers** à la demande : une adresse virtuelle (VIP) qui répartit le trafic entre plusieurs instances et écarte celles qui ne répondent plus. C'est l'équivalent d'ELB. Il sert pour les applications des utilisateurs, pour les `Service` de type LoadBalancer de Kubernetes, et pour la stack équilibrée demandée à l'EX210.

> **Les outils cités dans cette fiche.**
> - **Octavia** : le service de load balancing d'OpenStack.
> - **amphora** : la petite VM qui fait tourner le load balancer (HAProxy) dans le provider par défaut.
> - **HAProxy** : un load balancer logiciel très répandu ; **keepalived** : l'outil qui fait basculer une VIP entre deux machines (protocole VRRP).
> - **VIP** (Virtual IP) : l'adresse publique du load balancer.
> - **Barbican** : le coffre à secrets d'OpenStack, qui garde ici les certificats TLS.
> - **ELB** : Elastic Load Balancing, la famille des load balancers d'AWS.
> - **OVN** : Open Virtual Network : le moteur qui réalise les réseaux virtuels d'OpenStack (voir la fiche OVN).
> - **TCP** : le protocole de transport fiable : connexion établie, données remises dans l'ordre et sans perte.
> - **UDP** : le protocole de transport sans connexion, rapide mais sans garantie de livraison (DNS, vidéo, VXLAN).
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **HTTPS** : HTTP chiffré par TLS.

## Comprendre : l'arbre d'un load balancer

<!-- schema:arbre -->
<figure class="diagram"><svg viewBox="0 0 680 340" role="img" aria-label="L&#x27;arbre d&#x27;un load balancer Octavia" style="--minw:560px"><defs><marker id="g7-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g7-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g7-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g7-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="20" width="110" height="44" rx="9"/></g><text x="69.0" y="47.0" class="dg-t" text-anchor="middle" style="--d:0">clients</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="180" y="14" width="300" height="56" rx="9"/></g><text x="330.0" y="32.0" class="dg-t" text-anchor="middle" style="--d:1">load balancer « web-lb »</text><text x="330.0" y="50.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="330.0" dy="0">VIP 10.20.0.50</tspan><tspan x="330.0" dy="14">IP flottante 203.0.113.12</tspan></text><path d="M124 42 L178 42" class="dg-l a" marker-end="url(#g7-a)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="180" y="98" width="300" height="50" rx="9"/></g><text x="330.0" y="120.0" class="dg-t" text-anchor="middle" style="--d:2">listener HTTP :80</text><text x="330.0" y="138.0" class="dg-s" text-anchor="middle" style="--d:2">ou HTTPS :443 + certificat Barbican</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="180" y="176" width="300" height="50" rx="9"/></g><text x="330.0" y="198.0" class="dg-t" text-anchor="middle" style="--d:3">pool « web »</text><text x="330.0" y="216.0" class="dg-s" text-anchor="middle" style="--d:3">ROUND_ROBIN, LEAST_CONNECTIONS…</text><path d="M330 70 L330 96" class="dg-l c" marker-end="url(#g7-c)"/><path d="M330 148 L330 174" class="dg-l c" marker-end="url(#g7-c)"/><g class="dg-box dg-pop" style="--d:4"><rect x="506" y="176" width="160" height="50" rx="9"/></g><text x="586.0" y="198.0" class="dg-t" text-anchor="middle" style="--d:4">health monitor</text><text x="586.0" y="216.0" class="dg-s" text-anchor="middle" style="--d:4">GET /health, 5 s</text><line x1="480" y1="201" x2="506" y2="201" class="dg-grid"/><path d="M330 226 L330 248" class="dg-l c"/><path d="M110 248 L550 248" class="dg-l c"/><g class="dg-box dg-pop" style="--d:5"><rect x="40" y="272" width="140" height="48" rx="9"/></g><text x="110.0" y="293.0" class="dg-t" text-anchor="middle" style="--d:5">membre</text><text x="110.0" y="311.0" class="dg-s" text-anchor="middle" style="--d:5">10.20.0.11:80</text><path d="M110 248 L110 270" class="dg-l c" marker-end="url(#g7-c)"/><g class="dg-box dg-pop" style="--d:6"><rect x="260" y="272" width="140" height="48" rx="9"/></g><text x="330.0" y="293.0" class="dg-t" text-anchor="middle" style="--d:6">membre</text><text x="330.0" y="311.0" class="dg-s" text-anchor="middle" style="--d:6">10.20.0.12:80</text><path d="M330 248 L330 270" class="dg-l c" marker-end="url(#g7-c)"/><g class="dg-box dg-pop" style="--d:7"><rect x="480" y="272" width="140" height="48" rx="9"/></g><text x="550.0" y="293.0" class="dg-t" text-anchor="middle" style="--d:7">membre</text><text x="550.0" y="311.0" class="dg-s" text-anchor="middle" style="--d:7">10.20.0.13:80</text><path d="M550 248 L550 270" class="dg-l c" marker-end="url(#g7-c)"/><path d="M640 226 L640 296 L622 296" class="dg-l dash" marker-end="url(#g7-n)"/></svg><figcaption>Le health monitor retire du pool un membre qui ne répond plus, sans intervention.</figcaption></figure>
<!-- /schema:arbre -->

## Créer un load balancer

```bash
openstack loadbalancer create --name web-lb --vip-subnet-id sous-reseau-web --wait
openstack loadbalancer listener create --name http --protocol HTTP --protocol-port 80 --wait web-lb
openstack loadbalancer pool create --name web --lb-algorithm ROUND_ROBIN \
  --listener http --protocol HTTP --wait
openstack loadbalancer healthmonitor create --type HTTP --url-path /health \
  --delay 5 --timeout 3 --max-retries 3 --wait web
for ip in 10.20.0.11 10.20.0.12 10.20.0.13; do
  openstack loadbalancer member create --subnet-id sous-reseau-web \
    --address $ip --protocol-port 80 --wait web
done
openstack floating ip create --port $(openstack loadbalancer show web-lb -f value -c vip_port_id) public
openstack loadbalancer status show web-lb        # tout l'arbre et les statuts
```

Les groupes de sécurité des membres doivent laisser entrer le trafic **venant du load balancer** (le port de l'amphora sur le sous-réseau des membres), sinon les health checks échouent.

## Amphora ou OVN

| | amphora | ovn |
| --- | --- | --- |
| comment | une VM HAProxy (ou deux en ACTIVE_STANDBY avec keepalived) | règles dans OVN, distribuées sur les computes |
| protocoles | TCP, UDP, HTTP, HTTPS, TERMINATED_HTTPS, SCTP | TCP, UDP, SCTP |
| L7 (URL, en-têtes), TLS, cookies | oui | non |
| création | une à deux minutes (démarrage d'une VM) | instantanée |
| coût | une VM par load balancer | aucun |

```bash
openstack loadbalancer provider list
openstack loadbalancer create --provider ovn --name dns-lb --vip-subnet-id sous-reseau …
openstack loadbalancer flavor list       # profils d'amphora (single, active-standby, taille)
```

## Ce qu'il y a derrière (côté exploitant)

```
octavia-api ─► octavia-worker ─► Nova (crée l'amphora depuis l'image amphora-x64-haproxy)
                               └► Neutron (port VIP, ports membres)
amphoras ─(lb-mgmt-net, mTLS)─► health-manager (battements toutes les 10 s → bascule si silence)
housekeeping : amphoras de réserve, rotation des certificats
```

```bash
openstack loadbalancer amphora list                 # (admin) amphoras, rôle MASTER/BACKUP
openstack loadbalancer amphora failover <id>       # recréer une amphora
openstack loadbalancer failover web-lb             # reconstruire le load balancer
```

| Problème | Piste |
| --- | --- |
| reste en `PENDING_CREATE` puis `ERROR` | logs de octavia-worker ; Nova ne peut pas lancer l'amphora (image, flavor, quota du projet service) |
| `DEGRADED` | membres en échec : service, health monitor mal réglé, groupe de sécurité |
| bloqué en `PENDING_UPDATE` | worker redémarré au mauvais moment ; attendre l'expiration puis `failover` |
| amphoras injoignables | `lb-mgmt-net` mal routé depuis les nœuds contrôleurs |

## Avec Heat et Kubernetes

Dans Heat, les ressources `OS::Octavia::LoadBalancer`, `Listener`, `Pool`, `HealthMonitor` et `PoolMember` décrivent le même arbre. Dans Kubernetes, **cloud-provider-openstack** crée un load balancer Octavia pour chaque `Service` `type: LoadBalancer` (voir la fiche automatisation).

> **À retenir.** Load balancer (VIP) → listeners → pools → membres, avec un health monitor par pool. Provider amphora pour la couche 7 et le TLS (certificat dans Barbican), provider ovn pour du TCP/UDP instantané. `loadbalancer status show` donne l'arbre et les statuts ; provisioning dit où en est la configuration, operating si le trafic passe. Les groupes de sécurité des membres doivent accepter le load balancer.
