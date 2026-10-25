---
title: 'Nova : placement, scheduling et capacité'
chapter: 8
order: 1
duration: 14
tags:
- OpenStack
- EX210
- Nova
- Placement
cards:
- q: Quel est le rôle du service Placement ?
  a: 'Il tient l''**inventaire** de chaque fournisseur de ressources (un compute : VCPU, MEMORY_MB, DISK_GB ; aussi des GPU, de la bande passante), les **allocations** consommées par chaque instance et les **traits** (capacités). Le scheduler lui demande d''abord quels hôtes peuvent accueillir la demande.'
- q: Que sont les ratios d'allocation ?
  a: 'Le **surbooking** autorisé : `cpu_allocation_ratio` (vCPU vendus par cœur physique), `ram_allocation_ratio`, `disk_allocation_ratio`. Exemple : 48 cœurs × ratio 4 = 192 vCPU allouables. On les règle dans nova.conf ou directement dans Placement.'
- q: Comment le scheduler choisit-il un hôte ?
  a: 1) **Placement** renvoie les candidats qui ont les ressources et traits requis ; 2) les **filtres** éliminent ceux qui ne conviennent pas (zone, agrégat, anti-affinité, NUMA, PCI…) ; 3) les **weighers** classent les restants (RAM libre, CPU, métriques) ; il prend le meilleur.
- q: Différence entre un agrégat d'hôtes et une zone de disponibilité ?
  a: Un **agrégat** est un groupe d'hôtes avec des métadonnées, **invisible** pour les utilisateurs, utilisé par l'admin pour diriger des flavors (GPU, SSD, licence). Une **zone de disponibilité** est un agrégat avec un nom **exposé**, que l'utilisateur choisit (`--availability-zone`), en général pour des pannes indépendantes.
- q: Que veut dire « No valid host was found » ?
  a: 'Le scheduler n''a trouvé **aucun hôte** qui satisfasse la demande : plus assez de ressources (ou ratios atteints), filtre éliminatoire (zone, agrégat, anti-affinité, NUMA, image), hôtes désactivés. Les logs de nova-scheduler et nova-conductor disent quel filtre a tout éliminé.'
- q: À quoi servent `hw:cpu_policy=dedicated`, `hw:numa_nodes` et `hw:mem_page_size` ?
  a: 'Pour les charges sensibles (télécom, NFV, bases) : **CPU dédiés** (pinning, pas de partage de cœur), alignement **NUMA** (CPU et mémoire du même socket) et **huge pages** (pages mémoire de 2 Mo ou 1 Go). Les hôtes doivent être préparés (`cpu_dedicated_set`, huge pages réservées au démarrage).'
- q: Pourquoi réserver de la mémoire sur un nœud hyperconvergé ?
  a: Les OSD Ceph du nœud consomment de la RAM (plusieurs Go chacun) et du CPU. Si Nova ne les réserve pas (`reserved_host_memory_mb`, `cpu_shared_set`/`reserved_host_cpus`), il vend cette mémoire aux instances et l'OOM killer frappe Ceph ou les VM.
quiz:
- q: Le cloud affiche 40 % de RAM libre au total, mais les grosses instances échouent avec No valid host. Explication probable ?
  options:
  - Un bug de Glance
  - 'La RAM libre est éparpillée : aucun hôte n''a seul assez de RAM libre pour une grosse flavor'
  - Le quota du projet
  - Les clés Fernet
  answer: 1
  explain: Il faut regarder la capacité par hôte (`openstack resource provider inventory list`, `usage show`) ; rééquilibrer par migrations ou réserver des hôtes aux grosses flavors.
- q: Les instances GPU doivent aller seulement sur les 4 hôtes équipés, et aucune autre instance ne doit les occuper. Que fais-tu ?
  options:
  - Une zone de disponibilité pour tout le monde
  - Un agrégat GPU + propriété sur la flavor GPU (ou trait requis), et isoler l'agrégat aux seules flavors qui le demandent (filtre d'isolation ou trait interdit pour les autres)
  - Désactiver le scheduler
  - Réduire le ratio CPU
  answer: 1
  explain: 'Diriger les flavors GPU ne suffit pas : il faut aussi empêcher les autres d''y aller.'
- q: Pourquoi baisser `cpu_allocation_ratio` de 16 à 4 sur un cloud de production ?
  options:
  - Pour avoir plus d'instances
  - 'Pour limiter la contention : avec 16, une forte charge simultanée rend toutes les instances lentes (steal time)'
  - Pour réduire la RAM utilisée
  - Parce que Placement l'exige
  answer: 1
  explain: Le surbooking est un compromis densité / performance ; on le règle selon le profil réel de charge.
level: intermédiaire
---

Choisir **où** placer une instance est le cœur du travail d'un cloud. Nova s'appuie sur **Placement** pour savoir ce qui est disponible, puis sur ses **filtres** et **poids** pour choisir. Comprendre cette mécanique est indispensable pour résoudre le fameux « No valid host was found », gérer la capacité et répartir la charge (objectifs EX210 « Manage compute resource capacity » et « Re-balance compute node workloads »).

> **Les outils cités dans cette fiche.**
> - **Placement** : le service qui tient l'inventaire des ressources de chaque hôte et les allocations des instances.
> - **resource provider** : un fournisseur de ressources dans Placement (un compute, un GPU, un pool de stockage partagé).
> - **trait** : une capacité d'un fournisseur (`HW_CPU_X86_AVX512F`, `COMPUTE_STATUS_DISABLED`, ou un trait maison `CUSTOM_SSD`).
> - **nova-scheduler** : le composant qui filtre et classe les hôtes candidats.
> - **agrégat d'hôtes** et **zone de disponibilité** : des groupes d'hôtes, l'un pour l'admin, l'autre visible des utilisateurs.
> - **NUMA** : l'organisation mémoire des serveurs à plusieurs sockets ; chaque socket a sa mémoire « proche ».
> - **huge pages** : de grandes pages mémoire (2 Mo, 1 Go) qui réduisent le coût de traduction des adresses.
> - **osc-placement** : le module de la CLI pour interroger Placement (`openstack resource provider …`).
> - **HCI** : hyperconvergé : les mêmes serveurs font calcul (VM) et stockage (Ceph).
> - **swap** : un espace disque utilisé comme mémoire de secours quand la RAM est pleine.
> - **OOM** : out of memory : la mémoire est épuisée, le noyau tue un processus pour en libérer.
> - **hyperviseur** : le logiciel qui fait tourner des machines virtuelles sur un serveur physique (KVM, VMware ESXi).
> - **PCI** : le bus qui relie les cartes (réseau, GPU) à la carte mère.
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **OSD** : le démon Ceph qui gère un disque et ses données.

## Comprendre : trois étapes

<!-- schema:entonnoir -->
<figure class="diagram"><svg viewBox="0 0 680 340" role="img" aria-label="Le choix d&#x27;un hôte en trois étapes" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="40.0" y="14" width="600" height="50" rx="9"/></g><text x="340.0" y="36.0" class="dg-t" text-anchor="middle" style="--d:0">demande</text><text x="340.0" y="54.0" class="dg-s" text-anchor="middle" style="--d:0">flavor m1.large (4 vCPU, 8 Go, 40 Go) + image + zone</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="90.0" y="90" width="500" height="50" rx="9"/></g><text x="340.0" y="112.0" class="dg-t" text-anchor="middle" style="--d:1">1. Placement</text><text x="340.0" y="130.0" class="dg-s" text-anchor="middle" style="--d:1">qui a assez de ressources libres ? → 37 hôtes</text><path d="M340 72 L340 88" class="dg-l c" marker-end="url(#g3-c)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="150.0" y="166" width="380" height="50" rx="9"/></g><text x="340.0" y="188.0" class="dg-t" text-anchor="middle" style="--d:2">2. Filtres</text><text x="340.0" y="206.0" class="dg-s" text-anchor="middle" style="--d:2">zone, agrégat, affinité, NUMA… → 12 hôtes</text><path d="M340 148 L340 164" class="dg-l c" marker-end="url(#g3-c)"/><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="230.0" y="242" width="220" height="50" rx="9"/></g><text x="340.0" y="264.0" class="dg-t" text-anchor="middle" style="--d:3">3. Poids</text><text x="340.0" y="282.0" class="dg-s" text-anchor="middle" style="--d:3">→ compute-07</text><path d="M340 224 L340 240" class="dg-l c" marker-end="url(#g3-c)"/><text x="340" y="326" class="dg-s" text-anchor="middle" style="--d:4">allocation enregistrée dans Placement, puis nova-compute crée l&#x27;instance</text></svg><figcaption>Placement élimine sur les ressources, les filtres sur les règles, les poids classent ceux qui restent.</figcaption></figure>
<!-- /schema:entonnoir -->

## Placement et les ratios

Chaque compute déclare ses inventaires. Ce qui est allouable :

```
capacité = (total − réservé) × ratio d'allocation
```

```bash
openstack resource provider list
openstack resource provider inventory list <uuid-compute-07>
openstack resource provider usage show <uuid-compute-07>
openstack allocation candidate list --resource VCPU=4 --resource MEMORY_MB=8192 --resource DISK_GB=40
openstack resource provider trait list <uuid>
```

| Réglage (nova.conf du compute) | Effet | Valeur courante |
| --- | --- | --- |
| `cpu_allocation_ratio` | vCPU vendus par cœur | 4.0 (la valeur initiale historique de 16 est souvent trop haute) |
| `ram_allocation_ratio` | surbooking mémoire | 1.0 (pas de surbooking) à 1.5 |
| `disk_allocation_ratio` | surbooking disque local | 1.0 |
| `reserved_host_memory_mb` | RAM gardée pour l'hôte | 4096 et plus ; beaucoup plus en HCI |
| `cpu_shared_set`, `cpu_dedicated_set` | cœurs pour les vCPU partagés / épinglés | selon le matériel |

Un ratio CPU trop haut provoque du **steal time** (les vCPU attendent un cœur) ; un ratio mémoire au-dessus de 1 provoque du swap ou des OOM sur l'hôte.

## Les filtres et les poids

Les filtres actifs sont dans `[filter_scheduler] enabled_filters`. Les plus utiles :

| Filtre | Élimine les hôtes… |
| --- | --- |
| `ComputeFilter` | désactivés ou hors service |
| `AvailabilityZoneFilter` | hors de la zone demandée |
| `ComputeCapabilitiesFilter` | qui ne correspondent pas aux propriétés de la flavor |
| `ImagePropertiesFilter` | incompatibles avec l'image (architecture, hyperviseur) |
| `ServerGroupAntiAffinityFilter` / `AffinityFilter` | qui violent la politique du server group |
| `AggregateInstanceExtraSpecsFilter` | dont l'agrégat ne correspond pas aux propriétés de la flavor |
| `NUMATopologyFilter` | qui ne peuvent pas satisfaire la topologie NUMA, le pinning, les huge pages |
| `PciPassthroughFilter` | sans le périphérique PCI demandé (GPU, carte réseau SR-IOV) |

Les **weighers** classent : par défaut, l'hôte qui a le plus de RAM libre gagne (étalement). Un multiplicateur négatif inverse le comportement (remplissage, pour garder des hôtes vides).

## Agrégats et zones

```bash
# Un agrégat pour les hôtes SSD, utilisé par une flavor
openstack aggregate create --property ssd=true agg-ssd
openstack aggregate add host agg-ssd compute-10
openstack flavor set --property aggregate_instance_extra_specs:ssd=true m1.large.ssd

# Une zone de disponibilité visible des utilisateurs
openstack aggregate create --zone az-salle-b agg-salle-b
openstack aggregate add host agg-salle-b compute-20
openstack availability zone list --compute
openstack server create … --availability-zone az-salle-b …
```

Un hôte peut être dans plusieurs agrégats, mais dans **une seule** zone de disponibilité. Méthode moderne pour diriger : les **traits** (`openstack resource provider trait set --trait CUSTOM_GPU <uuid>`, et `trait:CUSTOM_GPU=required` sur la flavor). Pour **réserver** des hôtes à certaines flavors, on interdit le trait aux autres (`trait:CUSTOM_GPU=forbidden`) ou on utilise l'isolation d'agrégat de Placement.

## Les charges sensibles

```bash
openstack flavor set nfv.large \
  --property hw:cpu_policy=dedicated \
  --property hw:cpu_thread_policy=prefer \
  --property hw:numa_nodes=1 \
  --property hw:mem_page_size=1GB
```

Les hôtes doivent être préparés : `cpu_dedicated_set` dans nova.conf, cœurs isolés du système, huge pages réservées par le noyau au démarrage. Ces instances ne se mélangent pas avec les instances partagées : on les place dans un agrégat dédié.

## Gérer la capacité

```bash
openstack hypervisor list --long
openstack hypervisor stats show                         # (anciennes versions) total du cloud
openstack resource provider usage show <uuid>           # par hôte : ce qui compte vraiment
openstack compute service list --service nova-compute   # hôtes up/down, enabled/disabled
```

- Raisonner **par hôte** : 40 % de RAM libre éparpillée ne loge pas une grosse instance.
- **Rééquilibrer** : migrer à chaud des instances depuis les hôtes pleins (fiche « Exploiter les nœuds compute ») ; Watcher automatise ces optimisations.
- **Hyperconvergé** : réserver la RAM et les cœurs des OSD Ceph (`reserved_host_memory_mb`, `cpu_shared_set` qui exclut les cœurs de Ceph), sinon Nova les vend aux instances.
- **Cells v2** : au-delà de quelques centaines d'hôtes, Nova se découpe en cellules (bases et RabbitMQ séparés) ; `cell0` contient les instances qui n'ont jamais été placées (celles en ERROR « No valid host »).

> **À retenir.** Placement d'abord (ressources et traits), filtres ensuite (zone, agrégat, affinité, NUMA, PCI), poids enfin. Capacité = (total − réservé) × ratio ; ratio CPU raisonnable, RAM à 1, réservations plus fortes en HCI. Agrégats pour l'admin, zones pour les utilisateurs, traits pour diriger. « No valid host » : lire nova-scheduler et nova-conductor, et raisonner par hôte.
