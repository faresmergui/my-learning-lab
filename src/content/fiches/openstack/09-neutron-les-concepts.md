---
title: 'Neutron : réseaux, routeurs et IP flottantes'
chapter: 9
order: 1
duration: 14
tags:
- OpenStack
- EX210
- Neutron
cards:
- q: Quels sont les objets de base de Neutron ?
  a: Le **réseau** (un domaine de niveau 2), le **sous-réseau** (une plage IP, une passerelle, le DHCP, les DNS), le **port** (une interface virtuelle avec MAC et IP, branchée à une instance, un routeur, un DHCP), le **routeur** (relie des sous-réseaux et fait le NAT vers l'extérieur) et l'**IP flottante** (une IP externe associée à un port).
- q: Différence entre réseau provider et réseau self-service ?
  a: Un réseau **provider** correspond à un réseau **physique** existant (flat ou VLAN), créé par l'admin ; les instances y ont une IP du réseau de l'entreprise. Un réseau **self-service** (tenant) est créé par un projet, **encapsulé** (Geneve, VXLAN) entre les computes, et sort par un routeur.
- q: Comment fonctionne une IP flottante ?
  a: Le routeur du projet fait du **NAT 1 pour 1** (DNAT et SNAT) entre l'IP flottante, prise dans le sous-réseau du réseau externe, et l'IP privée du port de l'instance. L'instance ne voit jamais l'IP flottante dans son système.
- q: Comment fonctionnent les security groups ?
  a: 'Des règles **avec état** appliquées à chaque **port** : par défaut tout est refusé en entrée (sauf depuis le même groupe dans le groupe `default`) et tout est permis en sortie. Une règle peut viser une plage IP ou un autre security group (`--remote-group`).'
- q: Pourquoi l'instance a-t-elle un MTU de 1442 sur un réseau Geneve ?
  a: L'**encapsulation** Geneve ajoute environ 58 octets d'en-têtes. Si le réseau physique est à 1500, le réseau virtuel doit être plus petit pour que les paquets encapsulés passent sans fragmentation. Avec des jumbo frames (9000) sur le réseau tenant, on peut offrir 1500 ou plus aux instances.
- q: Qu'est-ce que la sécurité des ports (port security) ?
  a: Une protection qui n'autorise sur un port que la **MAC et l'IP** qui lui sont attribuées (anti-usurpation) et applique les security groups. Pour une instance qui route ou porte une IP virtuelle (keepalived), on ajoute des **allowed address pairs** plutôt que de désactiver la protection.
quiz:
- q: Une instance sur un réseau self-service doit être joignable depuis Internet. Que faut-il ?
  options:
  - Seulement un security group
  - Un routeur relié au réseau externe et au sous-réseau, une IP flottante associée au port, et une règle de security group qui ouvre le port
  - Un réseau provider
  - Un port supplémentaire
  answer: 1
  explain: 'Il faut les trois : le chemin (routeur), l''adresse (IP flottante) et l''autorisation (security group).'
- q: Deux instances keepalived partagent une IP virtuelle 10.0.0.100, mais le trafic vers cette IP ne passe pas. Correction ?
  options:
  - Désactiver tous les security groups
  - Ajouter 10.0.0.100 en allowed address pair sur les ports des deux instances (et réserver l'IP avec un port sans instance)
  - Créer une IP flottante
  - Changer de sous-réseau
  answer: 1
  explain: La sécurité des ports bloque les IP non attribuées au port ; les allowed address pairs l'autorisent explicitement.
- q: Le transfert de gros fichiers entre instances se bloque alors que le ping marche. Piste la plus probable ?
  options:
  - DNS
  - 'MTU : des paquets trop grands pour le réseau encapsulé, sans fragmentation'
  - Quota
  - Image corrompue
  answer: 1
  explain: Les petits paquets (ping) passent, les gros non. Vérifier le MTU annoncé par DHCP et celui de l'instance.
level: intermédiaire
---

**Neutron** fournit le réseau : chaque projet construit ses propres réseaux, routeurs et règles de filtrage, isolés de ceux des autres, par API. C'est le service le plus riche et le plus souvent en cause dans les incidents. Cette fiche pose les concepts ; la suivante montre comment OVN les réalise. La fiche AWS sur les VPC suit la même logique, et les fiches Réseaux (adressage, routage, NAT) donnent les bases.

> **Les outils cités dans cette fiche.**
> - **Neutron** : le service de réseau d'OpenStack ; il délègue le travail à un **plugin** (ML2 avec OVN aujourd'hui, ML2 avec OVS et agents dans les anciens déploiements).
> - **réseau**, **sous-réseau**, **port**, **routeur**, **IP flottante** : les objets de base (détaillés plus bas).
> - **flat**, **VLAN**, **VXLAN**, **Geneve** : les types de réseaux ; les deux derniers sont des **tunnels** qui transportent les réseaux virtuels entre les computes.
> - **security group** : un pare-feu avec état, appliqué à chaque port.
> - **DHCP** : le protocole qui donne son IP à l'instance au démarrage.
> - **MTU** : la taille maximale d'un paquet sur un réseau.
> - **QoS** : des règles de qualité de service (limite de débit, marquage).
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **VPC** : un réseau privé virtuel dans le cloud, isolé des autres clients.
> - **MAC** : l'adresse matérielle d'une carte réseau, utilisée sur le réseau local.
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.

## Comprendre : un projet type

<!-- schema:projet -->
<figure class="diagram"><svg viewBox="0 0 680 350" role="img" aria-label="Un projet type dans Neutron" style="--minw:560px"><defs><marker id="g4-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g4-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g4-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g4-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-a dg-pop" style="--d:0"><rect x="170" y="14" width="340" height="50" rx="9"/></g><text x="340.0" y="36.0" class="dg-t" text-anchor="middle" style="--d:0">réseau externe « public »</text><text x="340.0" y="54.0" class="dg-s" text-anchor="middle" style="--d:0">provider, VLAN 200 · 203.0.113.0/24</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="270" y="104" width="140" height="50" rx="9"/></g><text x="340.0" y="126.0" class="dg-t" text-anchor="middle" style="--d:1">routeur r1</text><text x="340.0" y="144.0" class="dg-s" text-anchor="middle" style="--d:1">SNAT 203.0.113.10</text><path d="M340 64 L340 102" class="dg-l a" marker-end="url(#g4-a)" marker-start="url(#g4-a)"/><rect x="14" y="196" width="316" height="140" rx="12" class="dg-zone dg-zc"/><text x="26" y="214" class="dg-zl" text-anchor="start">app-net · Geneve · 10.0.1.0/24</text><rect x="350" y="196" width="316" height="140" rx="12" class="dg-zone dg-zc"/><text x="362" y="214" class="dg-zl" text-anchor="start">db-net · Geneve · 10.0.2.0/24</text><path d="M300 154 L300 174 L172 174 L172 194" class="dg-l c" marker-end="url(#g4-c)"/><text x="236.0" y="168.0" class="dg-s" text-anchor="middle">10.0.1.1</text><path d="M380 154 L380 174 L508 174 L508 194" class="dg-l c" marker-end="url(#g4-c)"/><text x="444.0" y="168.0" class="dg-s" text-anchor="middle">10.0.2.1</text><g class="dg-box dg-pop" style="--d:2"><rect x="34" y="240" width="130" height="52" rx="9"/></g><text x="99.0" y="263.0" class="dg-t" text-anchor="middle" style="--d:2">web1</text><text x="99.0" y="281.0" class="dg-s" text-anchor="middle" style="--d:2">10.0.1.12</text><g class="dg-box dg-pop" style="--d:3"><rect x="182" y="240" width="130" height="52" rx="9"/></g><text x="247.0" y="263.0" class="dg-t" text-anchor="middle" style="--d:3">web2</text><text x="247.0" y="281.0" class="dg-s" text-anchor="middle" style="--d:3">10.0.1.13</text><g class="dg-box dg-pop" style="--d:4"><rect x="443" y="240" width="130" height="52" rx="9"/></g><text x="508.0" y="263.0" class="dg-t" text-anchor="middle" style="--d:4">db1</text><text x="508.0" y="281.0" class="dg-s" text-anchor="middle" style="--d:4">10.0.2.20</text><path d="M170 50 C 120 50, 110 150, 100 238" class="dg-l a dash" marker-end="url(#g4-a)"/><text x="140" y="100" class="dg-s" text-anchor="start">IP flottante</text><text x="140" y="114" class="dg-s" text-anchor="start">203.0.113.25</text><text x="140" y="128" class="dg-s" text-anchor="start">→ web1</text></svg><figcaption>Les VM n&#x27;ont que des IP privées ; le routeur fait le SNAT vers l&#x27;extérieur et l&#x27;IP flottante rend web1 joignable.</figcaption></figure>
<!-- /schema:projet -->

| Objet | Rôle |
| --- | --- |
| **réseau** | un segment de niveau 2 isolé (comme un commutateur) |
| **sous-réseau** | plage IP, passerelle, DHCP, serveurs DNS, routes ; plusieurs par réseau possible (IPv4 et IPv6) |
| **port** | une « prise » : MAC, IP fixe, security groups ; une instance, un routeur ou un DHCP s'y branche |
| **routeur** | relie des sous-réseaux, sort vers un réseau externe avec **SNAT**, porte les IP flottantes |
| **IP flottante** | IP externe associée à un port, par **NAT 1 pour 1** |

## Provider ou self-service

| | Provider | Self-service (tenant) |
| --- | --- | --- |
| créé par | l'admin | le projet |
| correspond à | un réseau physique (flat, VLAN) | un réseau virtuel encapsulé (Geneve, VXLAN) |
| IP des instances | du réseau de l'entreprise | privées, sortie par routeur et IP flottantes |
| usage | réseau externe, accès direct au LAN, performances | isolation, libre-service |

```bash
# (admin) Réseau externe sur le VLAN 200 de l'interface physique « datacentre »
openstack network create --external --provider-network-type vlan \
  --provider-physical-network datacentre --provider-segment 200 public
openstack subnet create --network public --subnet-range 203.0.113.0/24 \
  --gateway 203.0.113.1 --allocation-pool start=203.0.113.20,end=203.0.113.250 \
  --no-dhcp public-subnet

# (projet) Réseau privé, routeur, sortie vers l'extérieur
openstack network create app-net
openstack subnet create --network app-net --subnet-range 10.0.1.0/24 \
  --dns-nameserver 10.10.0.53 app-subnet
openstack router create r1
openstack router set --external-gateway public r1
openstack router add subnet r1 app-subnet
```

## Security groups

```bash
openstack security group create web
openstack security group rule create --ingress --protocol tcp --dst-port 443 --remote-ip 0.0.0.0/0 web
openstack security group rule create --ingress --protocol tcp --dst-port 22 --remote-ip 10.10.0.0/16 web
openstack security group rule create --ingress --protocol tcp --dst-port 5432 --remote-group web db
openstack server add security group web1 web
openstack security group rule list web
```

- **avec état** : la réponse d'une connexion autorisée passe d'office ;
- par défaut : entrée refusée (sauf depuis les membres du même groupe pour le groupe `default`), sortie autorisée ;
- `--remote-group` : « la base accepte le port 5432 depuis les instances du groupe web », sans IP ;
- s'applique **par port** : une instance à deux interfaces a des règles par interface.

## Les ports en détail

```bash
openstack port create --network app-net --fixed-ip subnet=app-subnet,ip-address=10.0.1.50 vip-port
openstack port set --allowed-address ip-address=10.0.1.50 <port-web1>
openstack port set --allowed-address ip-address=10.0.1.50 <port-web2>
openstack port show <port> -c binding_host_id -c binding_vif_type -c status
```

La **sécurité des ports** (anti-usurpation de MAC et d'IP) est active par défaut. Pour une IP virtuelle partagée (keepalived), un routeur logiciel ou un pare-feu virtuel, on ajoute des **allowed address pairs** au lieu de la désactiver (`--disable-port-security` retire aussi les security groups).

Le champ **binding** dit sur quel hôte le port est branché et par quel mécanisme ; un `binding_vif_type=binding_failed` explique une instance en erreur (fiche « Déboguer OpenStack »).

## Le MTU

```
Paquet de l'instance (MTU 1442) + en-têtes Geneve/UDP/IP (~58 o) = 1500 o sur le réseau physique
```

Neutron calcule le MTU de chaque réseau à partir de `global_physnet_mtu` et du type de réseau, et l'annonce par DHCP. Des symptômes typiques d'un MTU incohérent : SSH qui se fige après la connexion, `git clone` ou transferts bloqués, alors que le ping fonctionne. La solution durable : des **jumbo frames** sur le réseau tenant physique.

## Les autres fonctions

- **DHCP et DNS** : par sous-réseau ; `dns_domain` et l'extension DNS donnent des noms aux ports, éventuellement publiés dans **Designate**.
- **IPv6** : modes SLAAC ou DHCPv6, préfixes délégués.
- **QoS** : limites de débit par port ou réseau (`openstack network qos policy create`).
- **Trunks** : plusieurs VLAN sur un seul port d'instance.
- **SR-IOV** : une fonction de la carte réseau physique donnée directement à l'instance (performances télécom).
- **Réseaux routés** (segments) et **BGP** : annoncer les IP flottantes ou les réseaux de projet aux routeurs physiques.

> **À retenir.** Réseau (niveau 2), sous-réseau (IP, DHCP, passerelle), port (MAC, IP, security groups), routeur (SNAT, IP flottantes), IP flottante (NAT 1 pour 1). Provider = réseau physique créé par l'admin, self-service = réseau encapsulé du projet. Security groups avec état, par port, avec `--remote-group`. Allowed address pairs pour les IP virtuelles. Un MTU incohérent bloque les gros transferts mais pas le ping.
