---
title: Passer l'EX210
chapter: 24
order: 1
duration: 10
tags:
- OpenStack
- EX210
- Certification
cards:
- q: Quel est le format de l'EX210 ?
  a: 'Un examen **pratique** de 4 heures sur un vrai environnement Red Hat OpenStack Services on OpenShift : on réalise des tâches (créer, configurer, réparer), sans QCM. Il mène au titre **Red Hat Certified Specialist in Cloud Infrastructure** et compte pour le RHCA.'
- q: Quelle règle d'or pour les tâches de l'EX210 ?
  a: Tout ce qu'on configure doit **survivre à un redémarrage** et être fait **de façon durable** (dans la CR, le fichier d'environnement ou la configuration gérée par l'outil), pas seulement en mémoire ou dans un fichier généré qui sera écrasé.
- q: Quels sont les grands domaines de l'EX210 ?
  a: Control plane (services, sauvegarde et restauration, arrêt et redémarrage), sécurité de l'infrastructure (TLS, AIDE), sécurité des utilisateurs (IdM, portées, domaines, rôles personnalisés, clés de jetons), ressources applicatives (images, flavors, initialisation), stockage (Ceph, Swift), réseau (OVN, réseaux partagés), compute (nœuds, capacité, HCI, rééquilibrage), supervision (STF, logs), automatisation (Heat, Ansible, stack équilibrée) et dépannage.
- q: Quelles formations préparent à l'EX210 ?
  a: '**CL110** (Red Hat OpenStack Administration I : utilisation par un projet) puis **CL210** (Administration II : exploitation du cloud). Le prérequis conseillé est le **RHCSA** ou un niveau équivalent en administration RHEL.'
quiz:
- q: Pendant l'examen, une stack Heat demandée échoue. Quelle est la démarche la plus efficace ?
  options:
  - La supprimer et tout recommencer
  - '`stack failures list` et `stack event list --nested-depth`, corriger la cause dans le template ou l''environnement, puis `stack update`'
  - Passer à la tâche suivante sans revenir
  - Modifier la base de Heat
  answer: 1
  explain: Les événements donnent la raison exacte ; on corrige la source et on relance.
- q: Tu as modifié `nova.conf` directement dans un conteneur pour une tâche. Quel est le risque ?
  options:
  - Aucun
  - 'Le réglage disparaît au prochain redéploiement ou redémarrage du pod : la tâche sera notée comme échouée'
  - Le conteneur plante
  - Nova refuse de démarrer
  answer: 1
  explain: Il faut passer par la source de configuration (customServiceConfig dans la CR, ou l'outil de déploiement).
level: intermédiaire
---

L'**EX210** valide la capacité à **exploiter** un cloud Red Hat OpenStack, pas seulement à l'utiliser. C'est un examen pratique : on a un environnement, une liste de tâches, et un correcteur automatique vérifie le résultat final. Cette fiche relie chaque domaine de l'examen aux fiches du module et donne une stratégie pour le jour J.

> **Les outils cités dans cette fiche.**
> - **EX210** : l'examen Red Hat Certified Specialist in Cloud Infrastructure.
> - **RHOSO** : Red Hat OpenStack Services on OpenShift, la version sur laquelle porte l'examen.
> - **CL110** et **CL210** : les formations Red Hat qui préparent à l'examen ; **RHCSA** : la certification d'administration RHEL de base ; **RHCA** : le titre d'architecte qui cumule plusieurs spécialités.
> - **TLS** : le protocole qui chiffre une connexion et prouve l'identité du serveur par un certificat.
> - **jeton** : une chaîne secrète qui prouve qu'on est authentifié, à durée limitée.
> - **OVN** : Open Virtual Network : le moteur qui réalise les réseaux virtuels d'OpenStack (voir la fiche OVN).
> - **HCI** : hyperconvergé : les mêmes serveurs font calcul (VM) et stockage (Ceph).
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.

## Comprendre : ce qui est évalué

L'examen ne vérifie pas que tu connais la commande, il vérifie **l'état final** du cloud : le projet existe avec les bons quotas, l'utilisateur a le bon rôle dans la bonne portée, la stack est en `CREATE_COMPLETE` et répond, le service est configuré et le reste après redémarrage. Deux conséquences :

- un réglage fait « à la main » dans un fichier généré, ou non persistant, compte comme raté ;
- une tâche à moitié faite ne rapporte rien : mieux vaut finir proprement que commencer partout.

## Les domaines et les fiches

| Domaine | Fiches du module |
| --- | --- |
| gérer le control plane, sauvegarde et restauration, arrêt et redémarrage | Exploiter le control plane, Déployer OpenStack |
| sécurité de l'infrastructure (TLS de bout en bout, AIDE) | Sécuriser un cloud |
| sécurité des utilisateurs (IdM, portées, domaines, rôles, clés de jetons) | Keystone, Projets et quotas, Sécuriser un cloud |
| ressources applicatives (images, flavors, initialisation) | Glance, Nova : les instances |
| stockage (Ceph, choix de stockage, Swift) | Cinder, Ceph pour OpenStack, Swift |
| réseau (OVN, réseaux partagés) | Neutron : les concepts, OVN sous le capot, Projets et partage |
| compute (nœuds, capacité, HCI, rééquilibrage) | Nova : placement, Exploiter les nœuds compute |
| supervision (STF, flux des logs) | Supervision et télémétrie |
| automatisation (Heat, Ansible, stack équilibrée) | Heat, Octavia, Automatiser |
| dépannage (services du cœur, événements Heat) | Déboguer OpenStack |

## Se préparer

1. Lire le module dans l'ordre, puis la synthèse OpenStack.
2. Réviser les cartes de la certification (page Certifications) jusqu'à les maîtriser.
3. Pratiquer sur un vrai cloud : ton environnement de travail pour les tâches de projet (images, réseaux, stacks), et un laboratoire (DevStack, Kolla-Ansible tout-en-un, ou le lab de la formation CL210) pour les tâches d'administrateur (rôles personnalisés, sauvegardes, computes, Galera).
4. Refaire chaque geste **sans documentation externe** : seules les pages de manuel, `--help` et la documentation fournie sont disponibles le jour J.
5. Chronométrer une série de tâches : quatre heures passent vite.

## Les gestes à avoir dans les doigts

```bash
openstack --os-cloud admin project create --domain client-acme web
openstack quota set --instances 20 --cores 40 --ram 81920 web
openstack role create redemarreur && openstack role add --project web --user alice redemarreur
openstack network create --share --provider-network-type flat --provider-physical-network datacentre public
openstack image create --disk-format qcow2 --file rocky.qcow2 --property hw_qemu_guest_agent=yes rocky-9
openstack flavor create --vcpus 2 --ram 4096 --disk 20 --property hw:cpu_policy=dedicated m1.dedie
openstack stack create -t lb.yaml -e env.yaml --wait app && openstack stack output show app url
openstack compute service set --disable cmp2 nova-compute && openstack server migrate --live-migration --wait vm1
openstack volume type create --property volume_backend_name=ceph ssd
ceph -s && ceph df
oc get pods -n openstack && oc edit openstackcontrolplane
```

## Stratégie le jour J

1. **Lire toutes les tâches** au début : certaines dépendent d'autres (un projet avant ses utilisateurs, un réseau avant la stack).
2. Commencer par ce que tu maîtrises pour sécuriser des points, marquer le reste.
3. **Vérifier chaque tâche** après l'avoir faite (`show`, `list`, un test de connexion à l'instance), comme le ferait le correcteur.
4. Pour tout ce qui touche la configuration d'un service, passer par la source durable, puis confirmer après redémarrage du service ou du pod.
5. Garder un œil sur l'heure : 15 minutes avant la fin, relire la liste et vérifier les tâches à moitié faites.

> **À retenir.** L'EX210 est pratique, sur RHOSO, et note l'état final : tout doit être correct, durable et survivre à un redémarrage. Chaque domaine correspond à une ou plusieurs fiches du module. Se préparer en pratiquant les gestes de projet sur un vrai cloud et ceux d'administrateur dans un laboratoire, sans documentation externe. Le jour J : tout lire, commencer par le sûr, vérifier chaque tâche, passer par la configuration durable.
