---
title: 'Ansible en équipe : CI/CD, AWX et les autres outils'
chapter: 12
order: 1
duration: 13
level: intermédiaire
tags:
- awx
- ci/cd
- execution environment
- terraform
- kubernetes
cards:
- q: Qu'est-ce qu'AWX ?
  a: 'L''interface web et l''API open source pour lancer Ansible en équipe : projets reliés à Git, inventaires, identifiants stockés chiffrés, droits par équipe, historique de chaque exécution, planification. C''est le projet amont de Red Hat Ansible Automation Platform.'
- q: Qu'est-ce qu'un job template dans AWX ?
  a: 'Un lancement préparé : tel playbook, de tel projet Git, sur tel inventaire, avec tels identifiants et telles variables. On le lance en un clic, par API ou selon un planning, avec des droits précis.'
- q: Qu'est-ce qu'un execution environment ?
  a: Une **image de conteneur** qui contient ansible-core, les collections et les bibliothèques Python nécessaires. Tout le monde (poste, CI, AWX) exécute le playbook dans le même environnement. On la construit avec ansible-builder.
- q: Comment Terraform et Ansible se passent-ils les machines créées ?
  a: Soit Ansible lit les machines par un **inventaire dynamique** (OpenStack, AWS) en filtrant sur des tags posés par Terraform, soit Terraform écrit un fichier d'inventaire à partir de ses outputs. L'inventaire dynamique évite un fichier de plus à synchroniser.
- q: Que fait Ansible dans un monde Kubernetes ?
  a: Il prépare les nœuds (système, runtime, durcissement), installe ou met à jour le cluster (Kubespray est écrit en Ansible) et peut appliquer des manifestes ou des charts Helm avec `kubernetes.core`. Les applications elles-mêmes sont mieux gérées par GitOps (ArgoCD).
- q: Pourquoi faire tourner Ansible depuis une CI plutôt que depuis son poste ?
  a: Pour que chaque changement passe par une merge request relue, soit testé, et soit appliqué toujours de la même façon, avec une trace de qui a lancé quoi. Le poste personnel reste pour le développement et les tests.
quiz:
- q: Un collègue a ansible-core 2.15, toi 2.18, et le même playbook ne se comporte pas pareil. Quelle solution durable ?
  options:
  - Réinstaller Ansible chaque semaine
  - Interdire les collections
  - Se mettre d'accord par message
  - Un execution environment commun, image versionnée avec les mêmes versions pour tous
  answer: 3
  explain: 'Comme un Dockerfile pour une appli : l''environnement d''exécution devient lui aussi du code versionné.'
- q: L'équipe support doit pouvoir redémarrer une application en prod, mais pas modifier le playbook ni voir les mots de passe. Qu'utilises-tu ?
  options:
  - Un job template AWX avec droit d'exécution seulement
  - Un script Bash partagé
  - Leur donner le mot de passe Vault
  - Un accès SSH root
  answer: 0
  explain: AWX sépare qui peut lancer, qui peut modifier, et garde les identifiants hors de portée des utilisateurs.
- q: Terraform vient de créer 6 VM OpenStack avec la métadonnée `role=web`. Comment Ansible les cible-t-il sans fichier à maintenir ?
  options:
  - En lisant le state Terraform directement dans le playbook
  - Avec le plugin d'inventaire `openstack.cloud.openstack` et des groupes construits sur la métadonnée
  - Avec `ansible-pull`
  - En copiant les IP à la main
  answer: 1
  explain: 'L''option `keyed_groups` du plugin crée des groupes à partir des métadonnées : les VM tombent dans le bon groupe dès leur création.'
- q: Dans une chaîne de déploiement d'une nouvelle application sur Kubernetes, quel est le meilleur partage des rôles ?
  options:
  - Ansible applique les manifestes de l'appli à chaque commit
  - ArgoCD crée les VM
  - Terraform crée les VM, Ansible prépare les nœuds et installe le cluster, ArgoCD déploie les applications
  - Ansible fait tout
  answer: 2
  explain: 'Chacun fait ce qu''il fait le mieux : créer l''infra, configurer les machines, synchroniser en continu l''état du cluster avec Git.'
---

Seul, on lance `ansible-playbook` depuis son terminal. En équipe, il faut répondre à d'autres questions : qui a le droit de lancer quoi en prod, avec quelles versions d'Ansible, où sont les mots de passe, qui a lancé le playbook qui a cassé le service hier soir. Ce dernier chapitre montre comment industrialiser Ansible, et comment il s'articule avec Terraform et Kubernetes.

> **Les outils cités dans cette fiche.**
> - **CI/CD** : intégration et déploiement continus, des pipelines qui testent et appliquent automatiquement le code à chaque changement (par exemple **GitLab CI**).
> - **AWX** : l'interface web et l'API open source pour exécuter Ansible en équipe.
> - **Red Hat Ansible Automation Platform** (AAP) : la version commerciale et supportée, construite à partir d'AWX (son interface s'appelait **Ansible Tower**).
> - **execution environment** (EE) : une image de conteneur avec tout ce qu'il faut pour exécuter un playbook.
> - **ansible-builder** : l'outil qui construit un execution environment à partir d'un fichier de description.
> - **ansible-navigator** : un outil en ligne de commande qui lance les playbooks dans un execution environment, comme AWX le fait.
> - **Kubespray** : un ensemble de playbooks Ansible qui installe un cluster Kubernetes de production.
> - **ArgoCD** : un outil GitOps qui synchronise en continu un cluster Kubernetes avec le contenu d'un dépôt Git.
> - **Event-Driven Ansible** (EDA) : la brique qui lance un playbook automatiquement en réaction à un événement (une alerte, un webhook).

## Organiser le dépôt

Un dépôt d'équipe typique :

```
infra-ansible/
├── ansible.cfg
├── collections/requirements.yml
├── execution-environment.yml
├── inventaires/
│   ├── staging/ (hosts.yml, group_vars/, host_vars/)
│   └── prod/
├── playbooks/
│   ├── site.yml
│   ├── web.yml
│   └── maintenance/redemarrer-app.yml
├── roles/            # rôles maison, chacun avec ses tests Molecule
├── .ansible-lint
└── .gitlab-ci.yml
```

Les règles qui évitent la plupart des problèmes :

- **un seul chemin vers la prod** : merge request, relecture, CI ; personne n'applique un playbook en prod depuis son poste sauf urgence notée ;
- **staging d'abord** : la même branche s'applique à staging, puis à prod ;
- **des versions figées** : ansible-core, collections, rôles, image d'exécution ;
- **des playbooks courts et nommés pour ce qu'ils font** : `redemarrer-app.yml` se lance sans lire le code.

## Le même environnement pour tous

« Ça marche chez moi » existe aussi en Ansible : version d'ansible-core, collections, bibliothèques Python (`openstacksdk`, `boto3`…). Un **execution environment** règle le problème en empaquetant tout dans une image :

```yaml
# execution-environment.yml
version: 3
images:
  base_image:
    name: quay.io/fedora/fedora:40
dependencies:
  python_interpreter:
    package_system: python3
    python_path: /usr/bin/python3
  ansible_core:
    package_pip: ansible-core==2.18.*
  ansible_runner:
    package_pip: ansible-runner
  galaxy: collections/requirements.yml
  python:
    - openstacksdk>=3.0
```

```bash
ansible-builder build -t registry.exemple.fr/ansible-ee:1.4
ansible-navigator run playbooks/site.yml -i inventaires/staging \
  --eei registry.exemple.fr/ansible-ee:1.4
```

La même image sert sur ton Mac, dans la CI et dans AWX.

## Ansible dans la CI

```yaml
# .gitlab-ci.yml
stages: [test, staging, prod]

lint:
  stage: test
  image: registry.exemple.fr/ansible-ee:1.4
  script:
    - ansible-lint

apercu-prod:
  stage: test
  image: registry.exemple.fr/ansible-ee:1.4
  script:
    - ansible-playbook -i inventaires/prod playbooks/site.yml --check --diff

staging:
  stage: staging
  image: registry.exemple.fr/ansible-ee:1.4
  script:
    - ansible-playbook -i inventaires/staging playbooks/site.yml
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

prod:
  stage: prod
  image: registry.exemple.fr/ansible-ee:1.4
  script:
    - ansible-playbook -i inventaires/prod playbooks/site.yml
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual          # un humain valide le passage en prod
```

La clé SSH de déploiement et le mot de passe Vault sont des **variables protégées et masquées** du projet GitLab, disponibles seulement sur la branche principale. Le job `apercu-prod` affiche dans la merge request ce que le changement modifierait en prod.

## AWX et Automation Platform

La CI suffit pour appliquer du code. AWX ajoute ce qui manque quand beaucoup de gens lancent beaucoup de playbooks :

| Notion AWX | Ce que c'est |
| --- | --- |
| **Projet** | un dépôt Git, synchronisé à chaque lancement |
| **Inventaire** | statique ou dynamique (source OpenStack, AWS, VMware…), mis à jour automatiquement |
| **Identifiant** (credential) | clé SSH, mot de passe Vault, compte cloud ; stocké chiffré, utilisable sans être visible |
| **Job template** | playbook + inventaire + identifiants + variables, prêt à lancer |
| **Workflow** | un enchaînement de job templates, avec des branches en cas de succès ou d'échec |
| **Survey** | un petit formulaire qui demande des variables au lancement (version, environnement) |
| **Planning** | un lancement régulier (correctifs chaque nuit, contrôle de conformité chaque semaine) |
| **Équipes et rôles** | qui peut voir, lancer ou modifier chaque élément |

Chaque exécution reste dans l'historique avec sa sortie complète, l'auteur et la version Git utilisée. Pour un support ou une astreinte, un job template « redémarrer l'application » avec seulement le droit de lancer est beaucoup plus sûr qu'un accès SSH. AWX s'installe sur Kubernetes avec l'**AWX Operator** ; Automation Platform ajoute le support Red Hat, un Automation Hub privé et Event-Driven Ansible.

## Avec Terraform

Terraform crée, Ansible configure. Le point de contact, c'est la **liste des machines** :

```hcl
# Terraform : poser des métadonnées utilisables par Ansible
resource "openstack_compute_instance_v2" "web" {
  count = 3
  name  = "web-${count.index}"
  metadata = {
    role = "web"
    env  = "prod"
  }
}
```

```yaml
# inventaires/prod/openstack.yml
plugin: openstack.cloud.openstack
keyed_groups:
  - key: openstack.metadata.role
    prefix: role       # crée le groupe role_web
  - key: openstack.metadata.env
    prefix: env
```

Les VM créées par Terraform tombent seules dans les bons groupes. L'enchaînement se fait dans la CI (un job Terraform, puis un job Ansible) ou dans un workflow AWX. Évite d'appeler Ansible depuis Terraform (`local-exec`) : un échec de configuration ferait échouer, ou pire marquer comme abîmée, une ressource Terraform pourtant bien créée.

## Avec Kubernetes

| Besoin | Outil adapté |
| --- | --- |
| créer les VM ou le cluster managé | Terraform |
| préparer les nœuds (paquets, noyau, durcissement CIS) | Ansible |
| installer un cluster sur ses propres machines | Ansible via Kubespray, ou kubeadm piloté par Ansible |
| amorcer le cluster (installer ArgoCD, les CRD de base) | Ansible avec `kubernetes.core.helm` |
| déployer et faire évoluer les applications | GitOps avec ArgoCD |

Ansible applique un état **au moment où on le lance** ; ArgoCD, lui, surveille en permanence et corrige toute dérive dans le cluster. Pour les applications, c'est ce comportement continu qu'on veut.

## Aller plus loin : réagir aux événements

**Event-Driven Ansible** écoute des sources (alertes Prometheus, webhooks, files de messages) et lance un playbook selon des règles : une alerte « disque plein » déclenche un nettoyage, un nouveau serveur déclaré dans un outil d'inventaire déclenche sa configuration. C'est utile pour les remédiations simples et bien comprises ; garde un humain dans la boucle pour tout ce qui est risqué.

> **À retenir.** En équipe, la prod se change par merge request, testée et appliquée par la CI ou AWX, jamais depuis un poste. Un execution environment donne à tous les mêmes versions. AWX ajoute les droits, les identifiants cachés, l'historique et les plannings. Terraform crée et pose des métadonnées, Ansible lit l'inventaire dynamique et configure, ArgoCD déploie les applications sur Kubernetes.
