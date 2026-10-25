---
title: 'Heat : l''orchestration'
chapter: 14
order: 1
duration: 14
tags:
- OpenStack
- EX210
- Heat
cards:
- q: Qu'est-ce qu'une stack Heat ?
  a: 'L''ensemble des ressources (réseaux, instances, volumes, load balancers…) créées à partir d''un **template HOT** et gérées comme un tout : on la crée, la met à jour, la supprime d''une seule commande, et Heat calcule l''ordre des opérations.'
- q: Quelles sont les sections d'un template HOT ?
  a: '`heat_template_version` (obligatoire, ex. `2021-04-16` ou `wallaby`), `description`, `parameters` (entrées), `parameter_groups`, `resources` (ce qu''on crée), `outputs` (ce qu''on renvoie) et `conditions`.'
- q: À quoi servent `get_param`, `get_resource` et `get_attr` ?
  a: '`get_param` lit un paramètre ; `get_resource` renvoie l''**identifiant** d''une ressource de la stack (et crée une dépendance) ; `get_attr` lit un **attribut** d''une ressource une fois créée (par exemple `first_address` d''un serveur).'
- q: Qu'est-ce qu'une stack imbriquée (nested stack) ?
  a: 'Un template utilisé comme **type de ressource** dans un autre (`type: serveur-web.yaml`, ou via `resource_registry` dans un fichier d''environnement). Elle permet de réutiliser un bloc et sert aussi de modèle de membre dans un `OS::Heat::ResourceGroup` ou un `AutoScalingGroup`.'
- q: Que fait un fichier d'environnement Heat ?
  a: Il fournit les **valeurs des paramètres** (`parameters:`, `parameter_defaults:`) et peut **remplacer des types** de ressources (`resource_registry:`) sans toucher au template. On le passe avec `-e env.yaml`.
- q: Comment comprendre l'échec d'une stack ?
  a: '`openstack stack event list <stack>` (avec `--nested-depth 5` pour les stacks imbriquées) donne la chronologie et la raison de l''échec ; `openstack stack resource list -n 5 <stack> --filter status=CREATE_FAILED` isole la ressource ; `openstack stack failures list <stack>` résume ; ensuite les logs du service concerné (Nova, Neutron…) avec le request-id.'
- q: Que se passe-t-il lors d'un `stack update` ?
  a: 'Heat compare l''ancien et le nouveau template et ne touche qu''aux ressources modifiées : certaines propriétés se mettent à jour **en place**, d''autres imposent un **remplacement** (la ressource est recréée). `openstack stack update --dry-run` montre lesquelles avant d''agir.'
quiz:
- q: 'La ressource `port_web` utilise `{ get_resource: reseau_prive }`. Dans quel ordre Heat crée-t-il les deux ressources ?'
  options:
  - Au hasard
  - 'D''abord le réseau, puis le port : get_resource crée une dépendance implicite'
  - D'abord le port
  - En même temps, toujours
  answer: 1
  explain: Heat construit un graphe de dépendances à partir de get_resource, get_attr et depends_on, et crée en parallèle tout ce qui ne dépend de rien.
- q: Une stack est en `CREATE_FAILED` à cause d'un quota dépassé. Une fois le quota augmenté, que fais-tu ?
  options:
  - Supprimer et tout recréer obligatoirement
  - '`openstack stack update --existing <stack>` (ou un `stack check` puis update) pour que Heat reprenne les ressources manquantes'
  - Modifier la base de Heat
  - Attendre qu'elle se répare
  answer: 1
  explain: Une mise à jour sur une stack en échec relance la création de ce qui manque ; la supprimer reste possible si elle est petite ou si l'état est trop incohérent.
level: intermédiaire
---

**Heat** est le service d'**orchestration** d'OpenStack : on décrit dans un fichier YAML (un *template* HOT) l'ensemble d'une application, et Heat crée, met à jour et supprime toutes ses ressources dans le bon ordre. C'est l'équivalent de CloudFormation. L'EX210 demande d'écrire des templates, de déployer une stack avec load balancer et de diagnostiquer une stack en échec à partir de ses **événements**. Red Hat s'en sert aussi pour décrire le cloud lui-même (TripleO historiquement).

> **Les outils cités dans cette fiche.**
> - **Heat** : le service d'orchestration d'OpenStack.
> - **HOT** (Heat Orchestration Template) : le format YAML des templates Heat.
> - **stack** : une application déployée à partir d'un template.
> - **cloud-init** : l'outil qui configure l'instance au premier démarrage (voir la fiche Nova).
> - **Aodh** : le service d'alarmes qui peut déclencher l'autoscaling (voir la fiche supervision).
> - **load balancer** : un répartiteur de charge qui distribue les requêtes entre plusieurs serveurs.

## Comprendre : un template minimal

```yaml
heat_template_version: 2021-04-16
description: Un serveur web sur son propre réseau

parameters:
  image:   { type: string, default: rocky-9 }
  flavor:  { type: string, default: m1.small, constraints: [ { custom_constraint: nova.flavor } ] }
  key:     { type: string }
  reseau_public: { type: string, default: public }

resources:
  reseau:
    type: OS::Neutron::Net
  sous_reseau:
    type: OS::Neutron::Subnet
    properties: { network: { get_resource: reseau }, cidr: 10.20.0.0/24, dns_nameservers: [9.9.9.9] }
  routeur:
    type: OS::Neutron::Router
    properties: { external_gateway_info: { network: { get_param: reseau_public } } }
  interface:
    type: OS::Neutron::RouterInterface
    properties: { router: { get_resource: routeur }, subnet: { get_resource: sous_reseau } }
  groupe_web:
    type: OS::Neutron::SecurityGroup
    properties:
      rules: [ { protocol: tcp, port_range_min: 80, port_range_max: 80 } ]
  port:
    type: OS::Neutron::Port
    properties:
      network: { get_resource: reseau }
      fixed_ips: [ { subnet: { get_resource: sous_reseau } } ]
      security_groups: [ { get_resource: groupe_web } ]
  serveur:
    type: OS::Nova::Server
    properties:
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key }
      networks: [ { port: { get_resource: port } } ]
      user_data_format: RAW
      user_data: |
        #cloud-config
        packages: [nginx]
        runcmd: [ [systemctl, enable, --now, nginx] ]
  ip_flottante:
    type: OS::Neutron::FloatingIP
    depends_on: interface
    properties:
      floating_network: { get_param: reseau_public }
      port_id: { get_resource: port }

outputs:
  url:
    value: { list_join: ['', ['http://', { get_attr: [ip_flottante, floating_ip_address] }]] }
```

Heat lit les `get_resource`, `get_attr` et `depends_on` pour construire un **graphe de dépendances** ; tout ce qui est indépendant est créé en parallèle.

## Les commandes

```bash
openstack orchestration template validate -t web.yaml
openstack stack create -t web.yaml -e env.yaml --parameter key=ma-cle --wait web
openstack stack list
openstack stack output show web url
openstack stack resource list web
openstack stack update -t web.yaml -e env.yaml --dry-run web    # voir ce qui sera remplacé
openstack stack update -t web.yaml -e env.yaml --wait web
openstack stack delete --yes --wait web
openstack orchestration resource type list | grep Octavia        # types disponibles
```

## Réutiliser : environnements, imbrication, groupes

```yaml
# env.yaml
parameters:
  flavor: m1.medium
resource_registry:
  My::Serveur::Web: serveur-web.yaml      # un template devient un type
```

```yaml
  ferme:
    type: OS::Heat::ResourceGroup
    properties:
      count: 3
      resource_def:
        type: My::Serveur::Web
        properties: { index: "%index%", pool: { get_resource: pool_lb } }
```

Pour une stack **équilibrée en charge** (objectif EX210), on combine les ressources Octavia (`OS::Octavia::LoadBalancer`, `Listener`, `Pool`, `HealthMonitor`) et, dans le template du membre, un `OS::Octavia::PoolMember` qui inscrit chaque serveur dans le pool (voir la fiche Octavia).

## L'autoscaling

`OS::Heat::AutoScalingGroup` maintient entre `min_size` et `max_size` copies d'une ressource ; des `OS::Heat::ScalingPolicy` ajoutent ou retirent des membres, déclenchées par une alarme **Aodh** (CPU moyen au-dessus d'un seuil) ou par un appel à leur URL signée. Sans télémétrie, on peut aussi ajuster `count` d'un ResourceGroup par un `stack update`.

## Diagnostiquer une stack en échec

```bash
openstack stack list --nested                       # stacks et sous-stacks
openstack stack failures list web                   # résumé des ressources en échec
openstack stack event list --nested-depth 5 web     # chronologie détaillée
openstack stack resource list -n 5 --filter status=CREATE_FAILED web
openstack stack resource show web serveur           # resource_status_reason
journalctl -u heat-engine / logs du conteneur heat_engine    # côté cloud
```

| Raison fréquente | Cause |
| --- | --- |
| `Quota exceeded` | quota du projet (instances, ports, IP flottantes) |
| `No valid host was found` | Nova ne trouve pas de compute (voir placement) |
| `Resource CREATE failed: … timed out` | ressource trop lente, ou `WaitCondition` jamais signalée |
| `The Resource Type is not available` | service absent (Octavia non déployé) ou faute de frappe |
| `Property error` | mauvaise valeur dans le template (`template validate` l'aurait vu) |

Une fois la cause corrigée, un `stack update` reprend ce qui manque ; une stack bloquée en `*_IN_PROGRESS` après un redémarrage de heat-engine peut se débloquer avec `openstack stack cancel` puis update ou delete.

> **À retenir.** Un template HOT décrit paramètres, ressources et sorties ; Heat en déduit l'ordre grâce à get_resource, get_attr et depends_on. Fichiers d'environnement pour les valeurs et le `resource_registry`, stacks imbriquées et ResourceGroup pour réutiliser, AutoScalingGroup avec Aodh pour l'élasticité. `stack update --dry-run` avant de changer. En cas d'échec : `stack failures list` et `stack event list --nested-depth`, puis les logs du service fautif.
