---
title: Supervision et télémétrie
chapter: 21
order: 1
duration: 12
tags:
- OpenStack
- EX210
- Supervision
- Télémétrie
cards:
- q: Quels sont les services de télémétrie d'OpenStack ?
  a: '**Ceilometer** collecte les mesures (CPU, réseau, disques des instances, événements des services) ; **Gnocchi** les stocke en séries temporelles (ou on les envoie vers Prometheus) ; **Aodh** déclenche des **alarmes** sur ces mesures (par exemple pour l''autoscaling Heat).'
- q: Qu'est-ce que le Service Telemetry Framework (STF) ?
  a: 'La pile de supervision de Red Hat pour OpenStack : des agents (**collectd**, **Ceilometer**, sg-core) sur les nœuds envoient métriques et événements par un bus **AMQ Interconnect** vers OpenShift, où **Prometheus** stocke les métriques, **Alertmanager** alerte et **Grafana** affiche. Dans RHOSO, la télémétrie s''intègre au Cluster Observability Operator d''OpenShift.'
- q: Différence entre surveiller le cloud et surveiller les instances ?
  a: 'Surveiller **le cloud**, c''est l''exploitant qui suit la santé des nœuds, des services, de Galera, RabbitMQ, Ceph et la capacité. Surveiller **les instances**, c''est la consommation par VM ou par projet (facturation, autoscaling) : c''est le rôle de Ceilometer.'
- q: Comment circulent les logs dans un cloud OpenStack bien exploité ?
  a: Chaque service écrit ses logs (fichiers, journald, stdout des conteneurs) ; un agent (**rsyslog**, **Fluent Bit**, Vector, ou ClusterLogForwarder sur OpenShift) les envoie vers un stockage central (**Loki**, **OpenSearch/Elasticsearch**) où on les cherche par service, nœud et **request-id**.
- q: Quelles métriques suivre en priorité sur un cloud ?
  a: Disponibilité des API (temps de réponse, erreurs 5xx), services `down`, files RabbitMQ, état de Galera, santé et remplissage de Ceph, capacité restante (vCPU, RAM, IP flottantes), échecs de création d'instances, et état des agents OVN.
quiz:
- q: Le groupe d'autoscaling Heat n'ajoute jamais de serveur malgré une charge forte. Quel maillon vérifies-tu ?
  options:
  - Glance
  - Que Ceilometer publie bien la mesure, que Gnocchi la stocke, et que l'alarme Aodh passe en `alarm` (`openstack alarm list`, `alarm-history`)
  - Keystone
  - Horizon
  answer: 1
  explain: L'autoscaling dépend de toute la chaîne de télémétrie ; une alarme en `insufficient data` signale qu'aucune mesure n'arrive.
- q: Tu cherches pourquoi une création d'instance a échoué hier. Quel est le moyen le plus rapide ?
  options:
  - Lire tous les fichiers de logs nœud par nœud
  - Chercher le request-id de la requête dans le stockage central des logs, tous services confondus
  - Redémarrer Nova
  - Regarder Grafana
  answer: 1
  explain: Le request-id (`req-…`) suit la requête de service en service ; centralisé, il donne l'histoire complète en une recherche.
level: intermédiaire
---

Un cloud se surveille à deux niveaux : l'**infrastructure** (nœuds, services, bases, stockage, capacité), qui intéresse l'exploitant, et la **consommation** des instances et des projets (facturation, autoscaling), qui passe par la télémétrie d'OpenStack. L'EX210 demande de connaître le Service Telemetry Framework et le cheminement des logs.

> **Les outils cités dans cette fiche.**
> - **Ceilometer** : la collecte des mesures d'usage ; **Gnocchi** : leur stockage en séries temporelles ; **Aodh** : les alarmes.
> - **Prometheus** : la base de métriques par scraping ; **Alertmanager** : l'envoi des alertes ; **Grafana** : les tableaux de bord.
> - **exporter** : un petit programme qui expose les métriques d'un logiciel pour Prometheus (openstack-exporter, ceph-mgr prometheus, mysqld-exporter, rabbitmq_prometheus).
> - **collectd** : un agent qui collecte des métriques système.
> - **STF** (Service Telemetry Framework) : la pile de supervision Red Hat pour OpenStack, sur OpenShift.
> - **Loki** et **OpenSearch** : des stockages de logs ; **Fluent Bit** et **rsyslog** : des agents qui les transportent.
> - **OVS** : Open vSwitch : le commutateur virtuel logiciel installé sur chaque nœud.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **latence** : le délai entre une demande et sa réponse.
> - **OVN** : Open Virtual Network : le moteur qui réalise les réseaux virtuels d'OpenStack (voir la fiche OVN).
> - **RHOSP** : Red Hat OpenStack Platform, l'ancienne version Red Hat d'OpenStack (fondée sur TripleO).
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **CLI** : interface en ligne de commande, qu'on utilise dans un terminal.

## Comprendre : deux chaînes distinctes

```
Infrastructure (exploitant)
  nœuds, Galera, RabbitMQ, Ceph, OVN, API ─► exporters ─► Prometheus ─► Alertmanager ─► astreinte
                                                                    └► Grafana

Consommation (projets, facturation, autoscaling)
  instances, volumes, IP ─► Ceilometer (polling + notifications) ─► Gnocchi / Prometheus
                                                                 └► Aodh ─► alarmes ─► Heat (scaling)

Logs
  services (fichiers, journald, stdout) ─► rsyslog / Fluent Bit ─► Loki / OpenSearch ─► recherche par request-id
```

## La télémétrie OpenStack

```bash
openstack metric resource list --type instance         # Gnocchi : ressources suivies
openstack metric measures show --resource-id <vm> cpu  # mesures CPU d'une instance
openstack alarm create --name cpu-haut --type gnocchi_aggregation_by_resources_threshold \
  --metric cpu --aggregation-method rate:mean --threshold 8e9 --comparison-operator gt \
  --granularity 300 --resource-type instance --query '{"=": {"server_group": "web"}}'
openstack alarm list
openstack alarm-history show <alarme>
```

Une alarme Aodh a trois états : `ok`, `alarm` et `insufficient data` (aucune mesure reçue, souvent un problème de collecte). Les versions récentes peuvent remplacer Gnocchi par **Prometheus** comme stockage, avec Aodh qui l'interroge.

## Le Service Telemetry Framework (Red Hat)

- Sur les nœuds OpenStack : **collectd** (métriques système, libvirt, OVS), **Ceilometer** et **sg-core** envoient les données.
- Transport : **AMQ Interconnect** (QDR), un routeur de messages léger.
- Sur OpenShift : **Prometheus** (métriques), **Alertmanager**, **Grafana**, et une base d'événements.
- Dans **RHOSO**, la télémétrie (Ceilometer, node_exporter sur le data plane) s'intègre directement à la pile d'observabilité d'OpenShift (Cluster Observability Operator) : métriques des VM et des nœuds dans le même Prometheus que le reste.

## Ce qu'il faut surveiller

| Domaine | Indicateurs | Seuil d'alerte typique |
| --- | --- | --- |
| API | latence, taux de 5xx, disponibilité du endpoint | 5xx > 1 %, endpoint injoignable |
| services | `compute service list`, agents OVN `down` | tout service `down` > 2 min |
| RabbitMQ | messages en attente, consommateurs, partitions | file qui grossit sans consommateur |
| Galera | taille du cluster, état `Primary`, réplication | `cluster_size` < 3 |
| Ceph | `ceph health`, remplissage, OSD down, slow ops | `HEALTH_WARN`, > 75 % de remplissage |
| capacité | vCPU, RAM, IP flottantes, quotas | < 20 % de marge |
| expérience utilisateur | taux d'échec de création d'instance, temps de démarrage | test de fumée qui échoue |

Un **test de fumée** régulier (créer une VM, un volume, un load balancer, puis tout supprimer) avec **Rally** ou **Tempest** attrape ce que les métriques ne voient pas.

## Le cheminement des logs

| Déploiement | Où sont les logs |
| --- | --- |
| Kolla | `/var/log/kolla/<service>/` sur chaque nœud (et `docker logs`) |
| RHOSP 17 | `/var/log/containers/<service>/` |
| RHOSO | `oc logs` des pods pour le control plane ; journald et `/var/log/containers/` sur le data plane |
| tous | centralisés par rsyslog, Fluent Bit ou ClusterLogForwarder vers Loki ou OpenSearch |

Chaque requête porte un **request-id** (`req-…`) que tous les services réutilisent dans leurs lignes de log, et que la CLI renvoie en cas d'erreur (`--debug` l'affiche). Une recherche sur cet identifiant dans le stockage central raconte toute l'histoire, de l'API au compute.

> **À retenir.** Deux chaînes : l'infrastructure suivie par des exporters, Prometheus, Alertmanager et Grafana ; la consommation suivie par Ceilometer, stockée dans Gnocchi ou Prometheus, avec des alarmes Aodh qui pilotent l'autoscaling. STF est la version Red Hat (collectd, AMQ Interconnect, Prometheus sur OpenShift). Surveiller API, services, RabbitMQ, Galera, Ceph et capacité, plus un test de fumée. Centraliser les logs et chercher par request-id.
