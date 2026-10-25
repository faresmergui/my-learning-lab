---
title: 'Neutron : OVN sous le capot'
chapter: 10
order: 1
duration: 15
tags:
- OpenStack
- EX210
- OVN
- OVS
cards:
- q: Quel est le chemin d'une configuration de Neutron jusqu'au compute avec OVN ?
  a: '`neutron-server` (pilote ML2/OVN) écrit dans la base **OVN Northbound** (switchs et routeurs logiques) → **ovn-northd** traduit en **flux logiques** dans la base **Southbound** → **ovn-controller** sur chaque hôte (chassis) les transforme en règles **OpenFlow** dans le pont OVS `br-int`.'
- q: À quoi correspondent les objets Neutron dans OVN ?
  a: Réseau → **logical switch** (`neutron-<id>`), port → **logical switch port** (nommé par l'ID du port), routeur → **logical router**, security group → **ACL** sur un **port group**, IP flottante → règle **NAT** `dnat_and_snat` du routeur logique.
- q: Qu'est-ce qu'un gateway chassis ?
  a: 'Un hôte (contrôleur, nœud réseau ou compute choisi) qui porte le **port externe** d''un routeur logique : c''est par lui que passe le SNAT des instances sans IP flottante. Plusieurs gateway chassis avec des priorités assurent la bascule (via BFD).'
- q: Comment OVN fournit-il DHCP et métadonnées ?
  a: 'Le **DHCP** est natif : ovn-controller répond lui-même aux requêtes DHCP, sans agent. Les **métadonnées** passent par l''**ovn-metadata-agent** de chaque compute, qui écoute dans un namespace `ovnmeta-<réseau>` sur 169.254.169.254 et relaie vers l''API metadata de Nova.'
- q: Quels outils pour suivre un paquet dans OVN ?
  a: '`ovn-nbctl show` et `ovn-sbctl show` (topologie logique et chassis), **`ovn-trace`** (simule le trajet logique d''un paquet), `ovs-vsctl show` et `ovs-ofctl dump-flows br-int` (règles réelles), `ovs-appctl ofproto/trace` (trajet réel dans OVS), `tcpdump` sur l''interface physique ou `genev_sys_6081`.'
- q: Que se passait-il avant OVN, avec ML2/OVS ?
  a: 'Des **agents** Neutron sur les hôtes : `neutron-openvswitch-agent` (règles OVS), `neutron-l3-agent` (routeurs dans des namespaces `qrouter-…`), `neutron-dhcp-agent` (dnsmasq dans `qdhcp-…`), `neutron-metadata-agent`, avec **VXLAN** et souvent des nœuds réseau centraux. Beaucoup de clouds existants l''utilisent encore.'
quiz:
- q: Une instance n'obtient pas d'IP par DHCP sur un cloud OVN. Où regardes-tu ?
  options:
  - Les logs du dhcp-agent
  - L'état du port (`binding_host_id`, `status`), puis `ovn-sbctl show` (le port est-il lié au chassis ?) et les logs d'ovn-controller sur le compute
  - Glance
  - Keystone
  answer: 1
  explain: 'Avec OVN, pas d''agent DHCP : c''est ovn-controller du compute qui répond. Si le port n''est pas lié (binding) au chassis, rien ne répond.'
- q: Les instances sans IP flottante ne sortent plus sur Internet, celles avec IP flottante si. Piste ?
  options:
  - Les security groups
  - Le gateway chassis du routeur (SNAT centralisé) est tombé ou injoignable
  - Le DHCP
  - Le MTU
  answer: 1
  explain: Avec le routage distribué, les IP flottantes sortent depuis le compute ; le SNAT des autres passe par le gateway chassis. `ovn-nbctl lrp-get-gateway-chassis` montre lequel est actif.
- q: Comment vérifier sans envoyer de trafic qu'une ACL laisse passer TCP 443 vers une instance ?
  options:
  - Désactiver le security group
  - '`ovn-trace` avec un paquet décrit (inport, eth, ip, tcp.dst=443)'
  - '`ping`'
  - Redémarrer ovn-northd
  answer: 1
  explain: ovn-trace parcourt les flux logiques et dit quelle règle autorise ou rejette le paquet.
level: intermédiaire
---

La fiche précédente décrivait **ce que** l'utilisateur crée. Celle-ci montre **comment** c'est réalisé sur les machines, avec **OVN**, le moteur par défaut de Neutron aujourd'hui (RHOSO, Kolla, OpenStack-Ansible). C'est la fiche à relire quand une instance n'a pas d'IP, ne joint pas les métadonnées ou ne sort pas sur Internet. L'objectif EX210 « Configure Open Virtual Networking (OVN) services » s'appuie dessus.

> **Les outils cités dans cette fiche.**
> - **OVS** (Open vSwitch) : un commutateur virtuel programmable, présent sur chaque hôte ; il applique des règles **OpenFlow**.
> - **OVN** (Open Virtual Network) : un système qui construit des réseaux virtuels (switchs, routeurs, ACL, NAT) au-dessus d'OVS.
> - **ML2/OVN** : le pilote de Neutron qui traduit les objets Neutron en objets OVN.
> - **base Northbound (NB)** : la description logique voulue ; **ovn-northd** : la traduit ; **base Southbound (SB)** : les flux logiques et l'état des hôtes.
> - **ovn-controller** : le démon de chaque hôte (**chassis**) qui programme OVS localement.
> - **Geneve** : le protocole de tunnel entre hôtes (UDP 6081), qui transporte aussi des métadonnées OVN.
> - **br-int** (pont d'intégration où se branchent les instances) et **br-ex** (pont vers le réseau physique externe).
> - **BFD** : un protocole de détection rapide de panne, utilisé entre gateway chassis.
> - **RHOSO** : Red Hat OpenStack Services on OpenShift, la version actuelle d'OpenStack chez Red Hat.
> - **SNAT** : NAT sur l'adresse source (la sortie vers l'extérieur).
> - **load balancer** : un répartiteur de charge qui distribue les requêtes entre plusieurs serveurs.
> - **namespace** : un espace de noms : dans Kubernetes, une partition du cluster ; sous Linux, une isolation du noyau.
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).
> - **RHOSP** : Red Hat OpenStack Platform, l'ancienne version Red Hat d'OpenStack (fondée sur TripleO).
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.

## Comprendre : du Neutron à OpenFlow

<!-- schema:ovn -->
<figure class="diagram"><svg viewBox="0 0 680 430" role="img" aria-label="De Neutron à OpenFlow avec OVN" style="--minw:560px"><defs><marker id="g5-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g5-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g5-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g5-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="40" y="14" width="260" height="40" rx="9"/></g><text x="170.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:0">neutron-server (ML2/OVN)</text><g class="dg-box dg-pop" style="--d:1"><rect x="40" y="90" width="260" height="58" rx="9"/></g><text x="170.0" y="109.0" class="dg-t" text-anchor="middle" style="--d:1">OVN Northbound DB</text><text x="170.0" y="127.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="170.0" dy="0">switches et routeurs logiques,</tspan><tspan x="170.0" dy="14">ACL, NAT, load balancers</tspan></text><g class="dg-box dg-pop" style="--d:2"><rect x="40" y="184" width="260" height="52" rx="9"/></g><text x="170.0" y="200.0" class="dg-t" text-anchor="middle" style="--d:2">OVN Southbound DB</text><text x="170.0" y="218.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="170.0" dy="0">flux logiques, chassis,</tspan><tspan x="170.0" dy="14">port bindings</tspan></text><path d="M170 54 L170 88" class="dg-l c" marker-end="url(#g5-c)"/><text x="182" y="76" class="dg-s" text-anchor="start">écrit</text><path d="M170 148 L170 182" class="dg-l c" marker-end="url(#g5-c)"/><text x="182" y="170" class="dg-s" text-anchor="start">ovn-northd traduit</text><text x="340" y="40" class="dg-zl" text-anchor="start">ce que veut l&#x27;utilisateur</text><text x="340" y="124" class="dg-zl" text-anchor="start">le réseau décrit logiquement</text><text x="340" y="214" class="dg-zl" text-anchor="start">le réseau traduit pour les hôtes</text><rect x="14" y="266" width="466" height="152" rx="12" class="dg-zone dg-zc"/><text x="26" y="284" class="dg-zl" text-anchor="start">hôte (chassis)</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="30" y="294" width="150" height="48" rx="9"/></g><text x="105.0" y="323.0" class="dg-t" text-anchor="middle" style="--d:3">ovn-controller</text><path d="M105 236 L105 292" class="dg-l c" marker-end="url(#g5-c)"/><text x="114" y="262" class="dg-s" text-anchor="start">lit</text><g class="dg-box dg-pop" style="--d:4"><rect x="230" y="294" width="150" height="48" rx="9"/></g><text x="305.0" y="315.0" class="dg-t" text-anchor="middle" style="--d:4">OVS br-int</text><text x="305.0" y="333.0" class="dg-s" text-anchor="middle" style="--d:4">règles OpenFlow</text><path d="M180 318 L228 318" class="dg-l c" marker-end="url(#g5-c)"/><g class="dg-box dg-pop" style="--d:5"><rect x="230" y="360" width="150" height="44" rx="9"/></g><text x="305.0" y="379.0" class="dg-t" text-anchor="middle" style="--d:5">br-ex</text><text x="305.0" y="397.0" class="dg-s" text-anchor="middle" style="--d:5">patch port</text><path d="M305 342 L305 358" class="dg-l" marker-end="url(#g5-n)"/><g class="dg-box dg-pop" style="--d:6"><rect x="526" y="294" width="140" height="48" rx="9"/></g><text x="596.0" y="323.0" class="dg-t" text-anchor="middle" style="--d:6">autres hôtes</text><path d="M380 318 L524 318" class="dg-l a flow" marker-end="url(#g5-a)" marker-start="url(#g5-a)"/><text x="452.0" y="310.0" class="dg-s" text-anchor="middle">tunnels Geneve</text><g class="dg-box dg-a dg-pop" style="--d:7"><rect x="526" y="360" width="140" height="44" rx="9"/></g><text x="596.0" y="379.0" class="dg-t" text-anchor="middle" style="--d:7">réseau externe</text><text x="596.0" y="397.0" class="dg-s" text-anchor="middle" style="--d:7">interface physique</text><path d="M380 382 L524 382" class="dg-l a" marker-end="url(#g5-a)"/></svg><figcaption>Une règle qui manque sur un hôte se cherche dans l&#x27;ordre : NB, SB, puis OpenFlow sur br-int.</figcaption></figure>
<!-- /schema:ovn -->

| Neutron | OVN |
| --- | --- |
| réseau | logical switch `neutron-<id réseau>` |
| port | logical switch port (nom = ID du port) |
| routeur | logical router `neutron-<id routeur>` |
| security group | **port group** + **ACL** |
| IP flottante | NAT `dnat_and_snat` sur le routeur logique |
| SNAT du routeur | NAT `snat` sur le port de passerelle |
| Octavia avec le fournisseur `ovn` | load balancer OVN (niveau 4) |

## Où passe le trafic

| Trafic | Chemin avec OVN |
| --- | --- |
| entre deux instances du même réseau, hôtes différents | tunnel Geneve direct d'hôte à hôte |
| entre deux réseaux du même routeur | routage **distribué** sur l'hôte source, puis tunnel |
| instance avec IP flottante vers l'extérieur | NAT et sortie **depuis son compute** (si le routage distribué des FIP est activé et le compute relié au réseau externe) |
| instance sans IP flottante vers l'extérieur | tunnel vers le **gateway chassis** actif, SNAT, puis sortie |
| réseau provider | directement par `br-ex` (ou le pont du physnet) du compute |
| DHCP | répondu **localement** par ovn-controller, sans agent |
| métadonnées | `ovn-metadata-agent` du compute, namespace `ovnmeta-<réseau>` |

## Les outils de diagnostic

Selon le déploiement, les commandes OVN se lancent dans un conteneur (`podman exec ovn_controller …` avec Kolla ou RHOSP 17) ou dans un pod (`oc exec -n openstack ovsdbserver-nb-0 -- ovn-nbctl show` avec RHOSO).

```bash
# Vue logique
ovn-nbctl show                                   # switchs, routeurs, ports
ovn-nbctl lr-nat-list neutron-<id-routeur>       # SNAT et IP flottantes
ovn-nbctl lrp-get-gateway-chassis lrp-<id-port>  # gateway chassis et priorités
ovn-nbctl acl-list pg_<id-sg-avec-underscores>   # règles d'un security group

# Vue des hôtes
ovn-sbctl show                                   # chassis et ports liés à chacun
ovn-sbctl find port_binding logical_port=<id-port>

# Simulation logique
ovn-trace neutron-<id-réseau> 'inport=="<id-port>" && eth.src==fa:16:3e:aa:bb:cc &&
  ip4.src==10.0.1.12 && ip4.dst==10.0.2.20 && ip.ttl==64 && tcp && tcp.dst==5432'

# Sur le compute
ovs-vsctl show                                   # ponts, ports tap des instances, tunnels
ovs-ofctl dump-flows br-int | wc -l
ovs-appctl ofproto/trace br-int in_port=<n>,tcp,nw_dst=10.0.2.20,tp_dst=5432
ip netns                                         # ovnmeta-<id-réseau>
tcpdump -ni genev_sys_6081                       # trafic des tunnels
```

L'interface d'une instance sur l'hôte s'appelle `tap<11 premiers caractères de l'ID du port>` : c'est là qu'on pose un `tcpdump` pour savoir si les paquets sortent bien de la VM.

## Les pannes typiques

| Symptôme | Piste OVN |
| --- | --- |
| pas d'IP par DHCP | port non lié au chassis (`ovn-sbctl show`), ovn-controller arrêté ou déconnecté de la base SB |
| pas de clé SSH (métadonnées) | `ovn-metadata-agent` du compute, namespace `ovnmeta-…`, proxy vers Nova metadata |
| sortie Internet impossible sans IP flottante | gateway chassis actif tombé, `br-ex` mal relié, mapping `ovn-bridge-mappings` faux |
| IP flottante injoignable | NAT absent (`lr-nat-list`), ARP non répondu sur le réseau externe, sécurité du port |
| port en `binding_failed` | chassis non enregistré, `ovn-bridge-mappings` qui ne contient pas le physnet demandé |
| tout casse après une coupure du control plane | bases NB/SB en cluster RAFT sans quorum ; ovn-controller ne reçoit plus de mises à jour |

## Les bases OVN et leur santé

Les bases NB et SB tournent en **cluster RAFT** sur trois nœuds. Comme Galera, il leur faut une **majorité**.

```bash
ovs-appctl -t /var/run/ovn/ovnnb_db.ctl cluster/status OVN_Northbound
ovs-appctl -t /var/run/ovn/ovnsb_db.ctl cluster/status OVN_Southbound
```

Si la base Neutron et la base NB divergent (après une restauration, un incident), l'outil **`neutron-ovn-db-sync-util`** resynchronise OVN à partir de Neutron (en mode `log` d'abord pour voir les écarts, puis `repair`).

## L'ancien modèle : ML2/OVS avec agents

Beaucoup de clouds en production l'utilisent encore :

| Fonction | ML2/OVS | ML2/OVN |
| --- | --- | --- |
| règles des ports | `neutron-openvswitch-agent` | ovn-controller |
| routeurs | `neutron-l3-agent`, namespaces `qrouter-…` (DVR en option) | routeurs logiques distribués |
| DHCP | `neutron-dhcp-agent` (dnsmasq, `qdhcp-…`) | natif |
| métadonnées | `neutron-metadata-agent` | `ovn-metadata-agent` |
| tunnels | VXLAN | Geneve |

Avec ML2/OVS, `openstack network agent list` est la première commande de diagnostic ; avec OVN, elle montre les « OVN Controller agent » et « OVN Metadata agent » de chaque hôte, utiles aussi.

> **À retenir.** Neutron écrit dans la base OVN Northbound, ovn-northd produit les flux logiques de la Southbound, ovn-controller de chaque hôte programme OVS. DHCP natif, métadonnées par ovn-metadata-agent, routage distribué, SNAT par le gateway chassis. Diagnostiquer avec `ovn-nbctl show`, `ovn-sbctl show`, `ovn-trace`, `ovs-vsctl show`, `tcpdump` sur le tap. Les bases NB/SB ont besoin du quorum.
