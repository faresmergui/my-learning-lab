---
title: Déboguer OpenStack
chapter: 22
order: 1
duration: 15
tags:
- OpenStack
- EX210
- Debug
cards:
- q: Quelle est la méthode générale pour déboguer une opération OpenStack qui échoue ?
  a: 1) Lire le **message d'erreur** et le `fault` de la ressource (`server show`). 2) Récupérer le **request-id** (`--debug`, ou `openstack server event list` / `event show`). 3) Suivre ce request-id dans les logs des services, de l'API vers le scheduler, le conductor puis le compute ou l'agent. 4) Vérifier l'état réel (libvirt, OVN, Ceph). 5) Corriger la cause, puis seulement l'état.
- q: Que signifie `No valid host was found` ?
  a: 'Le **scheduler** n''a trouvé aucun compute acceptable. Causes : capacité insuffisante dans Placement, filtres (AZ, agrégats, propriétés de flavor ou d''image, affinité de server group), computes désactivés ou `down`, ou ressources spéciales manquantes (GPU, hugepages). Les logs de nova-scheduler disent quel filtre a tout éliminé.'
- q: Que signifie un port en `binding_failed` ?
  a: 'Neutron n''a pas pu **lier le port** au compute : aucun mécanisme (OVN) ne sait le brancher sur cet hôte. Causes : `ovn-controller` arrêté ou absent sur le compute, hostname différent entre Nova et OVN (`ovs-vsctl get open . external_ids:hostname`), réseau physique (provider) non mappé sur cet hôte (`ovn-bridge-mappings`).'
- q: Une instance démarre mais n'a ni clé SSH ni configuration. Quelle piste ?
  a: 'Le **service de métadonnées** est injoignable : cloud-init n''atteint pas 169.254.169.254. Vérifier l''agent **ovn-metadata** sur le compute (`openstack network agent list`), le namespace `ovnmeta-<réseau>` et le proxy HAProxy qu''il contient, et dans la VM `curl http://169.254.169.254/openstack/latest/meta_data.json`. Le config drive est une solution de contournement.'
- q: Comment voir l'historique des actions sur une instance ?
  a: '`openstack server event list <vm>` liste les actions (create, migrate, reboot…) avec leur request-id ; `openstack server event show <vm> <req-id>` donne les étapes et l''éventuelle trace d''erreur (pour un admin).'
- q: Comment remettre une instance bloquée dans un état stable ?
  a: 'Après avoir compris et corrigé la cause : `openstack server set --state active <vm>` (ou `--state error`) en admin, puis `openstack server reboot --hard`. Pour une VM en `ERROR` après un échec de build, la supprimer et la recréer est souvent le plus propre.'
quiz:
- q: La CLI répond `HTTP 401 The request you have made requires authentication` sur toutes les commandes. Premier réflexe ?
  options:
  - Redémarrer Nova
  - 'Vérifier l''authentification : variables OS_* ou clouds.yaml, mot de passe, domaine, projet, puis `openstack token issue`'
  - Vider Ceph
  - Augmenter les quotas
  answer: 1
  explain: 401 vient de Keystone ou du middleware keystonemiddleware ; 403 serait un refus de politique (authentifié mais pas autorisé).
- q: Une instance reste en `BUILD/scheduling` puis passe en ERROR avec `No valid host`. Le cloud a de la place. Que vérifies-tu ?
  options:
  - Le DNS
  - Les propriétés de la flavor et de l'image (agrégats, traits, AZ demandée) et la règle du server group (anti-affinity sur trop peu d'hôtes)
  - Le TLS
  - Swift
  answer: 1
  explain: Une contrainte de placement trop stricte élimine tous les hôtes même avec de la capacité ; les logs du scheduler indiquent le filtre qui a rendu 0 hôte.
level: intermédiaire
---

Déboguer OpenStack paraît intimidant parce qu'une seule commande traverse une dizaine de services. La bonne nouvelle : la méthode est toujours la même, et la plupart des pannes appartiennent à une poignée de familles connues. L'EX210 demande de diagnostiquer des problèmes courants des services du cœur et de suivre les événements d'une stack Heat ; au quotidien, c'est ce qui fait gagner le plus de temps.

> **Les outils cités dans cette fiche.**
> - **request-id** : l'identifiant (`req-…`) qui suit une requête dans tous les services.
> - **ovn-controller**, **ovn-metadata-agent** : les agents OVN du compute (voir la fiche OVN) ; **ovn-trace** : simule le parcours d'un paquet.
> - **virsh** : la commande de libvirt pour voir les VM sur un hôte.
> - **cloud-init** : configure l'instance au démarrage à partir des métadonnées.
> - **config drive** : un petit disque attaché à la VM qui contient les métadonnées, sans passer par le réseau.
> - **jeton** : une chaîne secrète qui prouve qu'on est authentifié, à durée limitée.
> - **AZ** : une zone de disponibilité : un ou plusieurs datacenters indépendants dans une région.
> - **scheduler** : le composant qui décide où placer une charge de travail (sur quel nœud ou quel hôte).
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.
> - **namespace** : un espace de noms : dans Kubernetes, une partition du cluster ; sous Linux, une isolation du noyau.
> - **NTP** : le protocole qui synchronise l'horloge des machines.

## Comprendre : la méthode

```
1. Symptôme       openstack server show web1 -c status -c fault
2. Request-id     openstack server event list web1   /   openstack --debug …
3. Le parcours    nova-api → nova-conductor → nova-scheduler (Placement) → nova-compute → libvirt
                  └─► neutron-server → OVN NB → ovn-controller      └─► cinder-volume → Ceph
4. L'état réel    virsh, ovn-nbctl / ovs-vsctl, rbd, ceph -s
5. Corriger       la cause, puis seulement l'état (reset-state en dernier recours)
```

```bash
openstack --debug server create … 2>&1 | grep -iE 'req-|HTTP/1.1 [45]'
grep req-4f2c… /var/log/kolla/nova/*.log           # ou la recherche dans le stockage central
```

Un **401** est un problème d'authentification (identifiants, domaine, jeton expiré) ; un **403** est un refus de **politique** (authentifié mais pas autorisé) ; un **409** un conflit d'état ; un **413** ou « Quota exceeded » un quota ; un **500** une erreur interne à lire dans les logs du service ; un **503** un service ou un backend indisponible.

## Les pannes classiques

| Symptôme | Cause habituelle | Où regarder |
| --- | --- | --- |
| `No valid host was found` | capacité, filtres (AZ, agrégats, traits, affinité), computes down | logs nova-scheduler (« Filter X returned 0 hosts »), `allocation candidate list` |
| `Quota exceeded for instances/cores/ram` | quota du projet | `openstack quota show`, `limits show --absolute` |
| port `binding_failed`, VM en ERROR à la création | ovn-controller absent, hostname différent, provider non mappé | `network agent list`, `ovs-vsctl get open . external_ids` |
| VM sans clé SSH ni user data | métadonnées injoignables | agent ovn-metadata, namespace `ovnmeta-*`, `curl 169.254.169.254` dans la VM |
| VM injoignable depuis l'extérieur | groupe de sécurité, IP flottante non associée, routeur sans passerelle, gateway OVN | `server show`, `port show`, `ovn-trace` |
| volume bloqué en `attaching`/`deleting` | désaccord Cinder, Nova, stockage | logs cinder-volume et nova-compute, `rbd status`, `virsh domblklist` |
| image en `queued` ou téléversement interrompu | backend Glance plein ou injoignable | logs glance-api, `ceph df` |
| tout est lent, BUILD sans fin | RabbitMQ ou Galera malade | `rabbitmqctl list_queues`, `wsrep_cluster_status` |
| service `down` mais processus vivant | battement de cœur perdu (base, bus, NTP) | logs du service, `chronyc tracking` |
| 401 partout | Keystone, memcached, clés Fernet différentes entre contrôleurs | logs keystone, `token issue` |

## Quelques diagnostics réseau

```bash
openstack port list --server web1 --long            # état, binding:host_id, IP
openstack port show <port> -c binding_vif_type -c status   # binding_failed ?
ovn-nbctl show                                       # vue logique : switchs, routeurs, ports
ovn-sbctl show                                       # chassis (computes) et ports liés
ovn-trace --summary <switch> 'inport=="<port>" && eth.src==<mac> && ip4.src==10.0.0.5 && ip4.dst==8.8.8.8 && ip.ttl==64'
ip netns exec ovnmeta-<id-réseau> curl -s http://169.254.169.254   # métadonnées côté compute
```

## Les stacks Heat en échec

```bash
openstack stack failures list web
openstack stack event list --nested-depth 5 web | grep -i failed
openstack stack resource show web serveur -c resource_status_reason
```

La raison d'échec d'une ressource Heat est presque toujours **le message d'erreur du service sous-jacent** : on repart donc de la ligne du tableau ci-dessus qui lui correspond.

## Remettre en état, mais en dernier

```bash
openstack server set --state active web1      # (admin) après correction de la cause
openstack server reboot --hard web1
openstack volume set --state available vol1   # (admin) si le volume n'est réellement attaché nulle part
openstack server event show web1 <req-id>     # vérifier ce qui s'est vraiment passé
```

Changer un état sans avoir vérifié la réalité (VM toujours présente dans libvirt, volume toujours mappé) crée des incohérences encore plus difficiles à démêler.

> **À retenir.** Toujours la même méthode : symptôme et `fault`, request-id, parcours dans les logs des services, état réel (virsh, OVN, Ceph), correction de la cause, état en dernier. 401 = authentification, 403 = politique, quota exceeded = quota. `No valid host` : capacité ou filtres, lire nova-scheduler. `binding_failed` : ovn-controller et hostname. Pas de clé SSH : métadonnées. Lent partout : RabbitMQ ou Galera. Une stack Heat échoue toujours à cause d'un service du dessous.
