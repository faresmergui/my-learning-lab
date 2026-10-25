---
title: Les autres services
chapter: 16
order: 1
duration: 12
tags:
- OpenStack
- Designate
- Barbican
- Manila
- Ironic
cards:
- q: À quoi sert Designate ?
  a: 'Au **DNS as a Service** : des zones et enregistrements gérés par l''API OpenStack, poussés vers de vrais serveurs DNS (BIND, PowerDNS). Il peut créer automatiquement un enregistrement pour chaque IP flottante ou port (`dns_name`) grâce à l''intégration Neutron.'
- q: À quoi sert Barbican ?
  a: 'Au **stockage de secrets** : clés de chiffrement des volumes Cinder (LUKS), certificats TLS d''Octavia, clés de signature d''images Glance, mots de passe applicatifs. Il garde les secrets chiffrés, éventuellement dans un HSM, et contrôle l''accès par ACL.'
- q: À quoi sert Manila ?
  a: 'Aux **systèmes de fichiers partagés** (NFS, CephFS, CIFS) : on crée un *share*, on donne l''accès à des adresses IP ou des identités (`share access create`), et plusieurs instances le montent en même temps. C''est l''équivalent d''EFS.'
- q: À quoi sert Ironic ?
  a: 'Au **bare metal** : il déploie des serveurs physiques comme des instances Nova (même API, même image Glance), en les pilotant par leur BMC (IPMI, Redfish) et le boot PXE. Il sert aussi à installer OpenStack lui-même (TripleO, Metal3).'
- q: À quoi servent Magnum et Zun ?
  a: '**Magnum** crée des clusters Kubernetes à partir de modèles (cluster templates), en lançant des instances. **Zun** lance des conteneurs isolés directement par l''API OpenStack. En pratique, beaucoup de clouds préfèrent installer Kubernetes eux-mêmes avec Cluster API ou Terraform.'
- q: À quoi sert Placement, et pourquoi est-il à part ?
  a: Placement tient l'inventaire des ressources (vCPU, RAM, disque, GPU, bande passante) et leurs consommations. Sorti de Nova, il est utilisé aussi par Neutron (bande passante garantie) et Cyborg (accélérateurs).
quiz:
- q: Trois instances doivent écrire dans le même répertoire partagé. Quel service ?
  options:
  - Cinder multi-attach
  - Manila (un share NFS ou CephFS)
  - Swift
  - Glance
  answer: 1
  explain: Un volume multi-attach exige un système de fichiers en cluster ; Manila fournit directement un partage NFS ou CephFS prêt à monter.
- q: Le service Masakari est installé. À quoi sert-il ?
  options:
  - À la facturation
  - À relancer automatiquement les instances d'un compute tombé (haute disponibilité des instances)
  - Au DNS
  - Aux sauvegardes
  answer: 1
  explain: Masakari surveille hôtes, processus et instances, et évacue les VM d'un hôte en panne.
level: intermédiaire
---

Au-delà du cœur (Keystone, Glance, Nova, Neutron, Cinder, Swift, Heat, Octavia), OpenStack compte une trentaine de services. Tous ne sont pas déployés partout : cette fiche présente ceux que l'on croise le plus souvent dans un cloud d'entreprise, pour savoir à quoi ils servent, comment les reconnaître dans le catalogue et quand les proposer.

> **Les outils cités dans cette fiche.**
> - **catalogue de services** : la liste des services et de leurs URL tenue par Keystone (`openstack catalog list`).
> - **HSM** (Hardware Security Module) : un boîtier matériel qui garde des clés sans jamais les laisser sortir.
> - **BMC** (Baseboard Management Controller) : la carte de gestion d'un serveur (iDRAC, iLO), pilotée par **IPMI** ou **Redfish**.
> - **PXE** : le démarrage d'un serveur par le réseau.
> - **NFS** et **CIFS/SMB** : des protocoles de partage de fichiers en réseau.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **KMS** : le service de gestion des clés de chiffrement.
> - **EFS** : le système de fichiers partagé (NFS) d'AWS.
> - **EKS** : le service Kubernetes managé d'AWS.
> - **EC2** : le service de machines virtuelles d'AWS.
> - **GPU** : le processeur graphique, qui fait énormément de calculs en parallèle (IA, rendu).

## Savoir ce qui est déployé

```bash
openstack catalog list            # services et endpoints visibles par toi
openstack service list            # (admin) tous les services enregistrés
openstack versions show           # versions d'API de chaque service
```

## Les services qu'on rencontre souvent

| Service | Nom (type) | Rôle | Équivalent AWS |
| --- | --- | --- | --- |
| **Designate** | `dns` | zones et enregistrements DNS, enregistrement automatique des IP | Route 53 |
| **Barbican** | `key-manager` | secrets, clés, certificats | KMS, Secrets Manager |
| **Manila** | `sharev2` | partages NFS, CephFS, CIFS | EFS, FSx |
| **Ironic** | `baremetal` | serveurs physiques à la demande | instances metal |
| **Magnum** | `container-infra` | clusters Kubernetes | EKS |
| **Placement** | `placement` | inventaire des ressources | — |
| **Ceilometer, Gnocchi, Aodh** | `metric`, `alarming` | métriques et alarmes | CloudWatch |
| **Masakari** | `instance-ha` | relance des instances d'un hôte en panne | auto-recovery EC2 |
| **Watcher** | `infra-optim` | rééquilibrage et consolidation des computes | — |
| **Cyborg** | `accelerator` | GPU, FPGA et autres accélérateurs | — |
| **Trove** | `database` | bases de données managées (peu répandu) | RDS |
| **Skyline** | — | interface web moderne, alternative à Horizon | console |

## Designate en pratique

```bash
openstack zone create --email dns@example.com projet.example.com.
openstack recordset create --type A --record 203.0.113.12 projet.example.com. www
openstack recordset list projet.example.com.
# intégration Neutron : le réseau porte un dns_domain, le port un dns_name
openstack network set --dns-domain projet.example.com. reseau-web
openstack floating ip create --dns-domain projet.example.com. --dns-name api public
```

Designate ne répond pas lui-même aux requêtes DNS : **designate-worker** pousse les zones vers des serveurs BIND ou PowerDNS, et **mDNS** leur sert les transferts de zone.

## Barbican en pratique

```bash
openstack secret store --name mdp-db --payload 'S3cr3t!'
openstack secret list
openstack secret get --payload <secret-href>
openstack acl user add --user robot-ci <secret-href>        # partager un secret
```

Barbican est la pièce qui rend possibles les **volumes chiffrés** de Cinder, la **terminaison TLS** d'Octavia et la **signature d'images** Glance. Ses secrets sont chiffrés par une clé maître (simple_crypto dans un fichier, ou un HSM PKCS#11) : c'est elle qu'il faut sauvegarder et protéger.

## Manila en pratique

```bash
openstack share type list
openstack share create --name partage-web --share-type cephfs CephFS 100
openstack share access create partage-web cephx client-web       # CephFS natif
openstack share access create partage-nfs ip 10.20.0.0/24        # NFS
openstack share export location list partage-web                 # chemin à monter
```

## Ironic en pratique

```bash
openstack baremetal node list                          # (admin) état : enroll, manageable, available, active
openstack baremetal node manage <node> && openstack baremetal node provide <node>
openstack server create --flavor baremetal-gpu --image rocky-9 --network prov serveur-physique
```

Un nœud Ironic passe par `enroll` → `manageable` (inspection du matériel) → `available` (nettoyé, prêt) → `active` (déployé). Les flavors bare metal utilisent une **resource class** (`resources:CUSTOM_BAREMETAL_GPU=1`) plutôt que des vCPU.

> **À retenir.** `openstack catalog list` dit ce qui est déployé. Designate pour le DNS (enregistrements automatiques des IP), Barbican pour les secrets (volumes chiffrés, TLS d'Octavia), Manila pour les partages NFS/CephFS, Ironic pour le bare metal piloté par BMC, Magnum pour Kubernetes, Masakari et Watcher pour la haute disponibilité et le rééquilibrage des instances. Chacun s'appuie sur Keystone pour l'identité et sur les services du cœur.
