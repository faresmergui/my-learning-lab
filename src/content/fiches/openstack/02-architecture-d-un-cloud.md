---
title: L'architecture d'un cloud OpenStack
chapter: 2
order: 1
duration: 13
tags:
- OpenStack
- EX210
- architecture
cards:
- q: Quels types de nœuds trouve-t-on dans un cloud OpenStack ?
  a: Les **contrôleurs** (API, bases, RabbitMQ, schedulers ; souvent 3 pour la haute disponibilité), les **compute** (hyperviseur KVM, nova-compute, agent réseau), parfois des **nœuds réseau** (passerelles vers l'extérieur), et les **nœuds de stockage** (Ceph, Swift). En **hyperconvergé** (HCI), compute et Ceph partagent les mêmes serveurs.
- q: Quels services d'infrastructure le control plane utilise-t-il ?
  a: '**MariaDB/Galera** (une base par service), **RabbitMQ** (messages internes), **memcached** (cache des jetons Keystone), **HAProxy** + **keepalived** (une IP virtuelle et la répartition vers les API) ; avec OVN, les bases **OVN Northbound/Southbound**.'
- q: Quel est le chemin d'une requête `openstack server create` ?
  a: CLI → **Keystone** (jeton et catalogue) → **nova-api** → base Nova → **nova-conductor** → **nova-scheduler** (qui interroge **Placement**) → **nova-compute** du nœud choisi (via RabbitMQ) → appels à **Glance** (image), **Neutron** (port), **Cinder** (volume si besoin) → **libvirt/KVM** démarre la VM.
- q: Pourquoi un nombre impair de contrôleurs ?
  a: Galera et RabbitMQ (et les bases OVN, etcd sous OpenShift) ont besoin d'une **majorité** (quorum) pour fonctionner. Avec 3 nœuds, on survit à la perte d'un ; avec 2, une coupure entre eux bloque tout (split brain).
- q: Quels sont les réseaux physiques typiques d'un déploiement ?
  a: Un réseau de **gestion/API interne**, un réseau d'**API publique**, un réseau **tenant** (tunnels Geneve/VXLAN entre computes), un réseau **externe** (IP flottantes, provider), un réseau **stockage** (accès Ceph) et souvent **stockage-gestion** (réplication Ceph) et **IPMI/BMC** (gestion matérielle).
- q: Qu'est-ce que le catalogue de services ?
  a: La liste, tenue par **Keystone**, des services et de leurs **endpoints** (URL `public`, `internal`, `admin`) par région. Le client la reçoit avec son jeton et y trouve l'adresse de Nova, Neutron, etc.
quiz:
- q: Un des trois contrôleurs tombe. Que se passe-t-il pour les utilisateurs ?
  options:
  - Le cloud est arrêté
  - 'Rien de visible : HAProxy envoie vers les deux autres, Galera et RabbitMQ gardent leur quorum'
  - Les instances s'arrêtent
  - Il faut redémarrer tous les computes
  answer: 1
  explain: La haute disponibilité du control plane repose sur la majorité. Les instances, elles, tournent sur les computes et ne dépendent pas du control plane pour continuer à fonctionner.
- q: Le control plane entier est inaccessible pendant une heure. Les instances déjà lancées continuent-elles de tourner ?
  options:
  - Non, elles s'arrêtent
  - 'Oui : elles tournent sur les computes ; on ne peut juste plus rien créer ni modifier par API'
  - Seulement celles avec un volume
  - Seulement celles avec une IP flottante
  answer: 1
  explain: Le data plane (KVM, OVS/OVN sur les computes) continue. Selon la conception réseau, certaines fonctions (DHCP, métadonnées) peuvent être perturbées au renouvellement.
level: intermédiaire
---

Quand on utilise OpenStack, on ne voit qu'une API. Quand on l'**exploite**, il faut savoir où tourne chaque morceau, qui parle à qui et ce qui casse si une machine tombe. Cette fiche donne la carte qui servira dans toutes les suivantes.

> **Les outils cités dans cette fiche.**
> - **control plane** : tout ce qui pilote le cloud (API, schedulers, bases, files de messages). **data plane** : ce qui fait tourner les instances et transporte leur trafic.
> - **MariaDB Galera** : un cluster de bases MariaDB où chaque nœud peut écrire, répliqué de façon synchrone.
> - **RabbitMQ** : la file de messages qui relie les composants d'un même service.
> - **memcached** : un cache en mémoire, utilisé notamment pour les jetons Keystone.
> - **HAProxy** et **keepalived** : répartiteur de charge et gestion d'une **IP virtuelle** (VIP) qui passe d'un contrôleur à l'autre.
> - **libvirt**, **QEMU**, **KVM** : la pile qui crée et fait tourner les machines virtuelles sur un compute.
> - **OVS** (Open vSwitch) et **OVN** (Open Virtual Network) : le commutateur virtuel et le système de réseau virtuel utilisés par Neutron.
> - **IPMI** / **BMC** : l'interface de gestion matérielle d'un serveur (allumer, éteindre, console à distance).
> - **OSD** : le démon Ceph qui gère un disque et ses données.
> - **HCI** : hyperconvergé : les mêmes serveurs font calcul (VM) et stockage (Ceph).
> - **RHEL** : Red Hat Enterprise Linux, la distribution Linux d'entreprise de Red Hat.
> - **VXLAN** : une technique qui transporte des réseaux virtuels à l'intérieur de paquets UDP, pour relier des machines sur plusieurs serveurs.
> - **scheduler** : le composant qui décide où placer une charge de travail (sur quel nœud ou quel hôte).

## Comprendre : les rôles des machines

<!-- schema:archi -->
<figure class="diagram"><svg viewBox="0 0 680 340" role="img" aria-label="Les rôles des machines d&#x27;un cloud OpenStack" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="92" width="96" height="44" rx="9"/></g><text x="62.0" y="119.0" class="dg-t" text-anchor="middle" style="--d:0">utilisateurs</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="134" y="92" width="112" height="44" rx="9"/></g><text x="190.0" y="119.0" class="dg-t" text-anchor="middle" style="--d:1">VIP HAProxy</text><path d="M110 114 L132 114" class="dg-l" marker-end="url(#g1-n)"/><rect x="270" y="14" width="396" height="172" rx="12" class="dg-zone dg-zc"/><text x="282" y="32" class="dg-zl" text-anchor="start">contrôleurs ×3</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="286" y="40" width="364" height="56" rx="9"/></g><text x="468.0" y="58.0" class="dg-t" text-anchor="middle" style="--d:2">API</text><text x="468.0" y="76.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="468.0" dy="0">keystone, nova-api, neutron-server, glance,</tspan><tspan x="468.0" dy="14">cinder, placement, heat, octavia…</tspan></text><g class="dg-box dg-pop" style="--d:3"><rect x="286" y="110" width="172" height="62" rx="9"/></g><text x="372.0" y="131.0" class="dg-t" text-anchor="middle" style="--d:3">planification</text><text x="372.0" y="149.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="372.0" dy="0">nova-scheduler</tspan><tspan x="372.0" dy="14">nova-conductor</tspan></text><g class="dg-box dg-pop" style="--d:4"><rect x="472" y="110" width="178" height="62" rx="9"/></g><text x="561.0" y="131.0" class="dg-t" text-anchor="middle" style="--d:4">état partagé</text><text x="561.0" y="149.0" class="dg-s" text-anchor="middle" style="--d:4"><tspan x="561.0" dy="0">Galera · RabbitMQ</tspan><tspan x="561.0" dy="14">memcached · OVN</tspan></text><path d="M246 114 L262 114 L262 68 L284 68" class="dg-l a" marker-end="url(#g1-a)"/><rect x="14" y="222" width="310" height="106" rx="12" class="dg-zone "/><text x="26" y="240" class="dg-zl" text-anchor="start">computes ×N</text><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="30" y="248" width="278" height="64" rx="9"/></g><text x="169.0" y="270.0" class="dg-t" text-anchor="middle" style="--d:5">nova-compute · libvirt/KVM</text><text x="169.0" y="288.0" class="dg-s" text-anchor="middle" style="--d:5"><tspan x="169.0" dy="0">ovn-controller · OVS</tspan><tspan x="169.0" dy="14">agent metadata</tspan></text><rect x="376" y="222" width="290" height="106" rx="12" class="dg-zone "/><text x="388" y="240" class="dg-zl" text-anchor="start">stockage Ceph</text><g class="dg-box dg-pop" style="--d:6"><rect x="392" y="248" width="258" height="64" rx="9"/></g><text x="521.0" y="270.0" class="dg-t" text-anchor="middle" style="--d:6">MON · OSD · MGR</text><text x="521.0" y="288.0" class="dg-s" text-anchor="middle" style="--d:6"><tspan x="521.0" dy="0">ou hyperconvergé</tspan><tspan x="521.0" dy="14">sur les computes</tspan></text><path d="M372 186 L372 204 L169 204 L169 246" class="dg-l c" marker-end="url(#g1-c)"/><text x="270.5" y="198.0" class="dg-s" text-anchor="middle">ordres via RabbitMQ</text><path d="M560 186 L560 246" class="dg-l" marker-end="url(#g1-n)" style="--d:6"/><text x="568" y="218" class="dg-s" text-anchor="start">API</text><path d="M310 290 L390 290" class="dg-l c" marker-end="url(#g1-c)" marker-start="url(#g1-c)"/><text x="350.0" y="282.0" class="dg-s" text-anchor="middle">RBD</text></svg><figcaption>Les contrôleurs décident, les computes font tourner les VM, Ceph garde les disques.</figcaption></figure>
<!-- /schema:archi -->

| Rôle | Contient | Combien |
| --- | --- | --- |
| contrôleur | API, schedulers, bases, RabbitMQ, OVN central | 3 (quorum) |
| compute | nova-compute, libvirt/KVM, ovn-controller/OVS | de quelques-uns à des milliers |
| réseau (selon l'architecture) | passerelles vers l'extérieur, routeurs | 0 avec OVN distribué, ou 2-3 « gateway chassis » |
| stockage | Ceph (MON, OSD, MGR), Swift | 3 et plus |
| hyperconvergé (HCI) | compute + OSD Ceph sur les mêmes serveurs | réduit le nombre de machines |

Sous **RHOSO**, les services du control plane tournent en **pods OpenShift** (gérés par des opérateurs) ; les computes restent des serveurs RHEL configurés par Ansible.

## Comprendre : un service, plusieurs processus

Chaque service est découpé en morceaux qui se parlent par **RabbitMQ** et partagent **une base** :

| Service | Processus principaux |
| --- | --- |
| Nova | `nova-api`, `nova-scheduler`, `nova-conductor`, `nova-compute` (sur chaque compute), `nova-novncproxy` (console) |
| Neutron | `neutron-server` (API), plugin **ML2/OVN**, `ovn-metadata-agent` sur les computes |
| Cinder | `cinder-api`, `cinder-scheduler`, `cinder-volume` (pilote du stockage), `cinder-backup` |
| Glance | `glance-api` |
| Keystone | l'API dans Apache/httpd |

Entre services différents, on passe toujours par les **API REST**, avec un jeton Keystone. Nova demande un port à Neutron par son API, jamais par sa base.

## Le trajet d'une création d'instance

<!-- schema:trajet -->
<figure class="diagram"><svg viewBox="0 0 680 350" role="img" aria-label="Le trajet d&#x27;une création d&#x27;instance" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="30" width="118" height="62" rx="9"/></g><text x="73.0" y="58.0" class="dg-t" text-anchor="middle" style="--d:0"><tspan x="73.0" dy="0">openstack</tspan><tspan x="73.0" dy="16">server create</tspan></text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="148" y="30" width="118" height="62" rx="9"/></g><text x="207.0" y="51.0" class="dg-t" text-anchor="middle" style="--d:1">nova-api</text><text x="207.0" y="69.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="207.0" dy="0">jeton, quotas,</tspan><tspan x="207.0" dy="14">BUILD en base</tspan></text><path d="M132 61 L146 61" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="282" y="30" width="118" height="62" rx="9"/></g><text x="341.0" y="58.0" class="dg-t" text-anchor="middle" style="--d:2">nova-conductor</text><text x="341.0" y="76.0" class="dg-s" text-anchor="middle" style="--d:2">orchestre</text><path d="M266 61 L280 61" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="416" y="30" width="118" height="62" rx="9"/></g><text x="475.0" y="58.0" class="dg-t" text-anchor="middle" style="--d:3">nova-scheduler</text><text x="475.0" y="76.0" class="dg-s" text-anchor="middle" style="--d:3">choisit l&#x27;hôte</text><path d="M400 61 L414 61" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="550" y="30" width="118" height="62" rx="9"/></g><text x="609.0" y="58.0" class="dg-t" text-anchor="middle" style="--d:4">nova-compute</text><text x="609.0" y="76.0" class="dg-s" text-anchor="middle" style="--d:4">sur l&#x27;hôte choisi</text><path d="M534 61 L548 61" class="dg-l c" marker-end="url(#g2-c)"/><text x="484" y="24" class="dg-s" text-anchor="middle">via RabbitMQ</text><g class="dg-box dg-pop" style="--d:1"><rect x="14" y="132" width="118" height="48" rx="9"/></g><text x="73.0" y="153.0" class="dg-t" text-anchor="middle" style="--d:1">Keystone</text><text x="73.0" y="171.0" class="dg-s" text-anchor="middle" style="--d:1">jeton + catalogue</text><path d="M73 92 L73 130" class="dg-l" marker-end="url(#g2-n)" marker-start="url(#g2-n)"/><g class="dg-box dg-pop" style="--d:4"><rect x="416" y="132" width="118" height="48" rx="9"/></g><text x="475.0" y="153.0" class="dg-t" text-anchor="middle" style="--d:4">Placement</text><text x="475.0" y="171.0" class="dg-s" text-anchor="middle" style="--d:4">qui a la place ?</text><path d="M475 92 L475 130" class="dg-l" marker-end="url(#g2-n)" marker-start="url(#g2-n)"/><path d="M615 92 L615 210" class="dg-l a"/><path d="M90 210 L615 210" class="dg-l a"/><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="30" y="236" width="140" height="56" rx="9"/></g><text x="100.0" y="261.0" class="dg-t" text-anchor="middle" style="--d:5">Glance</text><text x="100.0" y="279.0" class="dg-s" text-anchor="middle" style="--d:5">image (ou clone RBD)</text><path d="M100 210 L100 234" class="dg-l a" marker-end="url(#g2-a)"/><g class="dg-box dg-c dg-pop" style="--d:6"><rect x="192" y="236" width="140" height="56" rx="9"/></g><text x="262.0" y="261.0" class="dg-t" text-anchor="middle" style="--d:6">Neutron</text><text x="262.0" y="279.0" class="dg-s" text-anchor="middle" style="--d:6">port + réseau OVN</text><path d="M262 210 L262 234" class="dg-l a" marker-end="url(#g2-a)"/><g class="dg-box dg-c dg-pop" style="--d:7"><rect x="354" y="236" width="140" height="56" rx="9"/></g><text x="424.0" y="254.0" class="dg-t" text-anchor="middle" style="--d:7">Cinder</text><text x="424.0" y="272.0" class="dg-s" text-anchor="middle" style="--d:7"><tspan x="424.0" dy="0">volume si boot</tspan><tspan x="424.0" dy="14">sur volume</tspan></text><path d="M424 210 L424 234" class="dg-l a" marker-end="url(#g2-a)"/><g class="dg-box dg-c dg-pop" style="--d:8"><rect x="516" y="236" width="140" height="56" rx="9"/></g><text x="586.0" y="261.0" class="dg-t" text-anchor="middle" style="--d:8">libvirt</text><text x="586.0" y="279.0" class="dg-s" text-anchor="middle" style="--d:8">démarre la VM KVM</text><path d="M586 210 L586 234" class="dg-l a" marker-end="url(#g2-a)"/><text x="340" y="322" class="dg-ct" text-anchor="middle" style="--d:9">statut ACTIVE, puis cloud-init lit les métadonnées (clé SSH, user data)</text></svg><figcaption>Quand une création échoue, ce trajet dit dans quels logs chercher : nova-api, puis scheduler, puis compute.</figcaption></figure>
<!-- /schema:trajet -->

C'est ce trajet qu'on remonte quand une instance part en `ERROR` : à quelle étape, dans quel log (fiche « Déboguer OpenStack »).

## Les réseaux physiques

| Réseau | Transporte |
| --- | --- |
| gestion / API interne | échanges entre services, RabbitMQ, bases |
| API publique | accès des utilisateurs aux API et à Horizon |
| tenant | trafic entre instances, encapsulé (Geneve avec OVN, VXLAN avec OVS) |
| externe / provider | IP flottantes, réseaux reliés au physique (VLAN) |
| stockage | accès des computes et contrôleurs à Ceph |
| stockage-gestion | réplication interne de Ceph |
| IPMI / BMC | gestion matérielle, provisionnement |

On les sépare par **VLAN** sur des interfaces souvent agrégées (**bonding**) pour la redondance. Le **MTU** compte : l'encapsulation Geneve ou VXLAN prend environ 50 octets, d'où des MTU de 1442 ou 1450 dans les instances si le réseau physique reste à 1500, ou des **jumbo frames** (9000) sur le réseau tenant.

## La haute disponibilité

- **API** : sans état, derrière HAProxy et une VIP keepalived (ou un Service OpenShift).
- **Galera** et **RabbitMQ** : en cluster, avec **quorum** : 3 nœuds pour tolérer une panne.
- **Instances** : elles tournent sur les computes ; si le control plane tombe, elles **continuent**, on ne peut simplement plus rien changer.
- **Compute en panne** : ses instances s'arrêtent ; on les **évacue** vers d'autres hôtes (fiche « Exploiter les nœuds compute »), plus facilement si leurs disques sont dans Ceph.

> **À retenir.** Contrôleurs (API, schedulers, Galera, RabbitMQ, memcached, OVN central) par trois pour le quorum, computes (nova-compute, libvirt/KVM, OVN/OVS), stockage (souvent Ceph, parfois hyperconvergé). Les services se parlent par API, leurs processus internes par RabbitMQ. Le trajet d'un `server create` passe par Keystone, nova-api, conductor, scheduler et Placement, puis nova-compute qui appelle Glance, Neutron et Cinder. Les instances survivent à une panne du control plane.
