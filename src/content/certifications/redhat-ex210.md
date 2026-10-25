---
title: EX210
name: Red Hat Certified Specialist in Cloud Infrastructure
org: Red Hat
order: 6
color: "#e0457b"
description: Exploiter un cloud Red Hat OpenStack Services on OpenShift, du control plane au dépannage.
officialUrl: https://www.redhat.com/en/services/training/ex210-red-hat-certified-system-administrator-red-hat-openstack-exam
checked: 23 octobre 2026
format:
  - { label: Type, value: "Examen pratique sur un vrai environnement RHOSO, tâches notées sur l'état final" }
  - { label: Durée, value: "4 heures" }
  - { label: Version, value: "Red Hat OpenStack Services on OpenShift (RHOSO 18)" }
  - { label: Formations conseillées, value: "CL110 puis CL210" }
  - { label: Prérequis conseillé, value: "RHCSA ou niveau équivalent en administration RHEL" }
  - { label: Règle clé, value: "Les configurations doivent être durables et survivre à un redémarrage" }
domains:
  - name: Gérer le control plane (services, sauvegarde et restauration, arrêt et redémarrage)
    fiches: [openstack/02-architecture-d-un-cloud, openstack/17-deployer-openstack, openstack/18-exploiter-le-control-plane]
  - name: Sécuriser l'infrastructure (services chiffrés de bout en bout, AIDE)
    fiches: [openstack/20-securiser-un-cloud, securite/07-tls-et-pki]
  - name: Sécuriser les utilisateurs (IdM, accès par portée, projets, domaines, clés de jetons, rôles personnalisés)
    fiches: [openstack/04-keystone-l-identite, openstack/05-projets-quotas-et-partage, openstack/20-securiser-un-cloud]
  - name: Ressources applicatives (images, flavors, personnalisation, initialisation des instances)
    fiches: [openstack/06-glance-les-images, openstack/07-nova-les-instances, openstack/03-cli-clouds-yaml-et-horizon]
  - name: Stockage (Ceph dédié et intégré, choix de stockage, Swift)
    fiches: [openstack/11-cinder-les-volumes, openstack/12-ceph-pour-openstack, openstack/13-swift-le-stockage-objet]
  - name: Réseau (OVN, réseaux partagés)
    fiches: [openstack/09-neutron-les-concepts, openstack/10-neutron-ovn-sous-le-capot, openstack/05-projets-quotas-et-partage]
  - name: Compute (nœuds, capacité, hyperconvergence, rééquilibrage)
    fiches: [openstack/08-nova-placement-et-scheduling, openstack/19-exploiter-les-noeuds-compute, openstack/12-ceph-pour-openstack]
  - name: Supervision (Service Telemetry Framework, flux des logs)
    fiches: [openstack/21-supervision-et-telemetrie]
  - name: Automatisation (déploiement à grande échelle, Heat, Ansible, stack équilibrée)
    fiches: [openstack/14-heat-l-orchestration, openstack/15-octavia-le-load-balancing, openstack/23-automatiser-terraform-ansible-kubernetes]
  - name: Dépannage (services du cœur, événements des stacks Heat)
    fiches: [openstack/22-deboguer-openstack, openstack/14-heat-l-orchestration]
---

## Ce que l'examen vérifie vraiment

L'EX210 ne pose aucune question : il donne un cloud et une liste de tâches, puis un correcteur vérifie **l'état final**. Un projet mal nommé, un rôle donné dans la mauvaise portée, un réglage perdu au redémarrage du pod : la tâche est ratée. Red Hat ne publie pas de poids par domaine.

La dernière fiche du module OpenStack (« Passer l'EX210 ») relie chaque domaine aux fiches et liste les gestes à avoir dans les doigts.

## Les pièges

- **La configuration non durable.** Modifier un fichier dans un conteneur ou un pod ne tient pas : passer par la CR `OpenStackControlPlane` (`customServiceConfig`) ou la source de l'outil, puis vérifier après redémarrage.
- **La portée des rôles.** `--project`, `--domain` ou `--system` : le même rôle n'a pas le même effet.
- **Les dépendances entre tâches.** Un utilisateur dans un domaine qui n'existe pas encore, une stack sur un réseau pas encore partagé : lire toutes les tâches avant de commencer.
- **Changer un état sans corriger la cause.** Un `set --state` masque le problème, le correcteur vérifie que la ressource fonctionne.

## À connaître par cœur

| Besoin | Réponse type |
| --- | --- |
| voir les services du cloud | `compute service list`, `network agent list`, `volume service list`, `oc get pods -n openstack` |
| rôle personnalisé | `role create` puis règle dans le `policy.yaml` du service |
| réseau partagé à un seul projet | `network rbac create --target-project … --action access_as_shared` |
| vider un compute | `compute service set --disable` puis `server migrate --live-migration` |
| stack en échec | `stack failures list`, `stack event list --nested-depth 5` |
| santé du stockage | `ceph -s`, `ceph health detail`, `ceph df` |
| détecter une modification de fichier | `aide --init`, `aide --check` |

## Se préparer

- Lire tout le module OpenStack, puis sa synthèse.
- Réviser les cartes de cette certification (bouton en haut de la page).
- Pratiquer les tâches de projet sur un vrai cloud, et les tâches d'administrateur dans un laboratoire (Kolla-Ansible tout-en-un, DevStack, ou le lab CL210).
- S'entraîner sans documentation externe : `--help`, les pages de manuel et la documentation fournie suffisent.

## Stratégie le jour J

1. Lire toutes les tâches et repérer leurs dépendances.
2. Faire d'abord ce que tu maîtrises, marquer le reste.
3. Vérifier chaque tâche comme le correcteur (`show`, `list`, test de connexion), puis après redémarrage quand c'est une configuration de service.
4. Garder 15 minutes à la fin pour relire la liste.
