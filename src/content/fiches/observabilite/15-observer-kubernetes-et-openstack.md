---
title: Observer Kubernetes et OpenStack
chapter: 15
order: 1
duration: 12
tags:
- Observabilité
- Kubernetes
- OpenStack
- Prometheus
cards:
- q: Que contient le chart kube-prometheus-stack ?
  a: Le **Prometheus Operator**, un **Prometheus**, **Alertmanager**, **Grafana**, **node_exporter** (DaemonSet), **kube-state-metrics**, des **ServiceMonitors** pour les composants du cluster (kubelet, cAdvisor, API server, etcd, scheduler…), et un jeu de règles et de tableaux de bord prêts à l'emploi (kubernetes-mixin).
- q: Différence entre kube-state-metrics, cAdvisor et metrics-server ?
  a: '**kube-state-metrics** expose l''**état des objets** Kubernetes (réplicas voulus et disponibles, pods en échec, jobs, limites déclarées). **cAdvisor** (dans le kubelet) expose la **consommation réelle** des conteneurs (CPU, mémoire, réseau). **metrics-server** fournit seulement les valeurs instantanées de CPU et mémoire à `kubectl top` et à l''autoscaler (HPA), sans historique.'
- q: Quelles alertes de base sur un cluster Kubernetes ?
  a: Pods en **CrashLoopBackOff** ou longtemps non prêts, déploiement avec moins de réplicas disponibles que voulus, conteneurs **OOMKilled**, nœuds **NotReady** ou sous pression (mémoire, disque), PVC presque pleins, certificats proches de l'expiration, API server en erreur ou lent, etcd sans leader ou lent, et jobs ou CronJobs en échec.
- q: Comment superviser un cloud OpenStack ?
  a: 'À plusieurs niveaux : **hôtes** (node_exporter, ou Centreon), **services** OpenStack (état des agents et services, temps de réponse des API, via openstack-exporter ou des sondes), **piliers** (mysqld_exporter pour Galera, plugin Prometheus de RabbitMQ, exporters OVN et libvirt), **Ceph** (module prometheus du mgr), **capacité** (Placement, quotas) et **logs** centralisés recherchés par request-id.'
- q: Qu'expose le module prometheus de Ceph ?
  a: 'Le **ceph-mgr** expose sur un port (9283 par défaut) les métriques du cluster : santé (`ceph_health_status`), OSD up/in, PG par état, capacité et utilisation par pool, latences et débits par OSD. Des tableaux de bord et des règles d''alerte officiels existent (ceph-mixin).'
quiz:
- q: Un déploiement est « sain » selon Kubernetes, mais la page renvoie des erreurs 502. Qu'est-ce qui manque dans la supervision ?
  options:
  - Rien
  - 'Des indicateurs côté utilisateur : taux d''erreurs et latence au niveau de l''ingress ou du service, et une sonde boîte noire, en plus de l''état des pods'
  - Plus de métriques kube-state-metrics
  - Un deuxième Prometheus
  answer: 1
  explain: Un pod prêt ne garantit pas que l'application répond correctement ; il faut mesurer ce que voit l'utilisateur.
- q: Sur OpenStack, les API répondent mais les créations d'instances échouent depuis une heure. Quel indicateur aurait alerté le plus tôt ?
  options:
  - Le CPU des contrôleurs
  - Une sonde de bout en bout qui crée et supprime régulièrement une instance (Rally, Tempest ou un script), et la profondeur des files RabbitMQ sans consommateur
  - Le nombre d'utilisateurs Keystone
  - La taille des images Glance
  answer: 1
  explain: Les tests de fumée de bout en bout voient ce que vivent les utilisateurs du cloud.
level: intermédiaire
---

Kubernetes et OpenStack sont deux plateformes que tu exploites au quotidien, et chacune a ses propres couches à observer : l'infrastructure, la plateforme elle-même et les applications qui tournent dessus. Cette fiche donne une architecture de supervision type pour chacune, en réutilisant les outils du module.

> **Les outils cités dans cette fiche.**
> - **kube-prometheus-stack** : le chart Helm qui installe une stack Prometheus complète pour Kubernetes.
> - **kube-state-metrics** : l'exporter de l'état des objets Kubernetes ; **cAdvisor** : la mesure de la consommation des conteneurs, intégrée au kubelet.
> - **metrics-server** : la source des métriques de `kubectl top` et de l'autoscaling.
> - **mixin** : un ensemble partagé de règles d'alerte et de tableaux de bord pour un logiciel (kubernetes-mixin, ceph-mixin).
> - **openstack-exporter** : l'exporter Prometheus qui interroge les API OpenStack.
> - **Rally** et **Tempest** : les outils de tests de charge et de tests fonctionnels d'OpenStack.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **chart Helm** | un paquet d'installation pour Kubernetes (voir la fiche Helm du module Kubernetes) |
| **kubelet** | l'agent Kubernetes sur chaque nœud, qui lance les conteneurs et expose leurs métriques |
| **plan de contrôle** | les composants qui pilotent le cluster : API server, etcd, scheduler, controller-manager |
| **etcd** | la base clé-valeur où Kubernetes garde tout son état |
| **CrashLoopBackOff** | l'état d'un pod qui plante et que Kubernetes relance en boucle, avec une attente croissante |
| **OOMKilled** | un conteneur tué parce qu'il a dépassé sa limite de mémoire (OOM = out of memory) |
| **PVC** | une demande de volume persistant par un pod (voir la fiche stockage) |
| **ingress** | le point d'entrée HTTP du cluster, qui voit toutes les requêtes des utilisateurs |
| **IPMI / Redfish** | les interfaces de gestion matérielle des serveurs (températures, alimentations, ventilateurs) |
| **test de fumée** | un test simple de bout en bout qui vérifie que les fonctions essentielles marchent |
| **dead man's switch** | une alerte toujours active ; si elle cesse d'arriver chez un service externe, c'est que la supervision elle-même est en panne |

## Comment ça marche : qui regarde quoi dans un cluster

1. **node_exporter** tourne sur chaque nœud (DaemonSet) et lit les fichiers système de Linux (`/proc`, `/sys`) : CPU, mémoire, disques, réseau du nœud.
2. Le **kubelet** de chaque nœud intègre **cAdvisor**, qui lit les cgroups pour savoir ce que consomme chaque conteneur.
3. **kube-state-metrics** interroge l'API server et transforme l'état des objets en métriques : « ce déploiement veut 3 réplicas et en a 2 disponibles ».
4. Les composants du plan de contrôle (API server, etcd, scheduler) exposent leurs propres métriques.
5. **Prometheus**, configuré par l'opérateur à partir des ServiceMonitors, collecte tout cela, évalue les règles du **kubernetes-mixin** et envoie les alertes à Alertmanager.
6. **Grafana** affiche les tableaux de bord fournis (par cluster, par namespace, par pod, par nœud).

Les trois sources se complètent : node_exporter dit si le **nœud** souffre, cAdvisor si un **conteneur** consomme trop, kube-state-metrics si Kubernetes n'arrive pas à obtenir **l'état voulu**.

## Comprendre : trois couches à observer

```
        Kubernetes                               OpenStack
applications   RED, SLO, traces, logs           instances des projets (Ceilometer, côté projet)
plateforme     API server, etcd, scheduler,      API Nova/Neutron/Cinder…, agents, RabbitMQ,
               kubelet, CoreDNS, ingress         Galera, OVN, Ceph, Placement (capacité)
infrastructure nœuds : CPU, mémoire, disques,    hôtes contrôleurs et computes, réseau physique,
               réseau (node_exporter)            matériel (IPMI, Redfish), stockage
```

## Kubernetes

```bash
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

| Source | Ce qu'elle dit |
| --- | --- |
| node_exporter | santé des nœuds (CPU, mémoire, disques, réseau) |
| cAdvisor (kubelet) | consommation de chaque conteneur |
| kube-state-metrics | état voulu et réel des objets (réplicas, pods en échec, jobs, PVC) |
| API server, etcd, scheduler, CoreDNS | santé du plan de contrôle |
| contrôleur d'ingress (NGINX, Traefik, Envoy) | trafic, erreurs et latence vus de l'extérieur |
| applications (ServiceMonitor) | RED, métriques métier |

```promql
# pods qui redémarrent en boucle
increase(kube_pod_container_status_restarts_total[30m]) > 3
# déploiements sans assez de réplicas disponibles
kube_deployment_status_replicas_available < kube_deployment_spec_replicas
# conteneurs proches de leur limite mémoire
container_memory_working_set_bytes{container!=""} / on (namespace, pod, container)
  kube_pod_container_resource_limits{resource="memory"} > 0.9
# PVC presque pleins
kubelet_volume_stats_available_bytes / kubelet_volume_stats_capacity_bytes < 0.1
```

Les **logs** suivent le même chemin (Fluent Bit ou Alloy en DaemonSet vers Loki ou Elasticsearch), avec les **événements Kubernetes** (`kubectl get events`) collectés aussi : ils expliquent souvent un incident (scheduling impossible, image introuvable, OOMKilled). Les **traces** passent par l'OpenTelemetry Operator.

## OpenStack

| Couche | Outil | À surveiller |
| --- | --- | --- |
| hôtes | node_exporter ou Centreon | CPU, mémoire, disques, réseau, NTP, matériel (IPMI) |
| services | openstack-exporter, sondes HTTP | services et agents `down`, temps de réponse et erreurs des API |
| Galera | mysqld_exporter | `wsrep_cluster_size`, état `Primary`, réplication |
| RabbitMQ | plugin rabbitmq_prometheus | messages en attente, files sans consommateur, alarmes mémoire/disque |
| OVN / OVS | ovn-exporter, ovs-exporter | état des bases NB/SB, chassis, ports |
| libvirt | libvirt-exporter | VM par hôte, CPU, disques, réseau |
| Ceph | mgr prometheus | `ceph_health_status`, OSD down, PG non actifs, remplissage |
| capacité | openstack-exporter, Placement | vCPU, RAM, IP flottantes, quotas |
| bout en bout | Rally, Tempest, script | créer une VM, un volume, un load balancer, puis supprimer |

Les **logs** de tous les services se centralisent (Loki ou Elasticsearch) et se cherchent par **request-id** ; c'est le plus gros gain pour le débogage OpenStack. Red Hat propose sa propre pile (Service Telemetry Framework, et l'intégration à l'observabilité d'OpenShift dans RHOSO) ; voir la fiche supervision du module OpenStack.

## Les alertes à ne pas oublier

- **Kubernetes** : nœuds NotReady, CrashLoopBackOff, réplicas manquants, OOMKilled, PVC pleins, certificats, etcd, API server.
- **OpenStack** : service ou agent `down`, Galera non `Primary` ou incomplet, files RabbitMQ qui gonflent, Ceph `HEALTH_ERR`, capacité sous 20 %, test de fumée en échec.
- **Les deux** : la **supervision de la supervision** (Prometheus qui ne scrape plus, Alertmanager injoignable) avec une alerte « toujours active » (Watchdog/dead man's switch) relayée par un service externe.

> **À retenir.** Observer trois couches : infrastructure, plateforme, applications. Sur Kubernetes, kube-prometheus-stack apporte l'opérateur, node_exporter, kube-state-metrics, cAdvisor et les règles du kubernetes-mixin ; ajouter les métriques d'ingress et des applications, les logs et les événements. Sur OpenStack, superviser hôtes, services et agents, Galera, RabbitMQ, OVN, libvirt, Ceph et capacité, avec un test de fumée de bout en bout et des logs centralisés par request-id. Et surveiller la supervision elle-même avec un dead man's switch.
