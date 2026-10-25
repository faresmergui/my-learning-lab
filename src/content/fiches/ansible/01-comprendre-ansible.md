---
title: Ce qu'est Ansible, et ce qu'il n'est pas
chapter: 1
order: 1
duration: 10
level: intermédiaire
tags:
- Ansible
- gestion de configuration
- idempotence
cards:
- q: À quoi sert Ansible ?
  a: 'À **automatiser la configuration** de machines existantes : installer des paquets, déposer des fichiers, gérer des services et des utilisateurs, sur un serveur ou sur mille, à partir d''une description écrite une fois.'
- q: Pourquoi dit-on qu'Ansible est « sans agent » ?
  a: Il n'installe rien de permanent sur les machines gérées. Il s'y connecte en **SSH** (ou WinRM pour Windows), y copie un petit programme Python, l'exécute puis le supprime. Il faut seulement SSH et Python côté cible.
- q: Qu'est-ce que le nœud de contrôle ?
  a: 'La machine d''où l''on lance Ansible : ton poste, un bastion ou un runner de CI. C''est la seule où Ansible est installé.'
- q: Que veut dire « idempotent » pour une tâche Ansible ?
  a: La relancer ne change rien si l'état voulu est déjà atteint. Une tâche « le paquet nginx est installé » ne fait rien la deuxième fois et répond `ok` au lieu de `changed`.
- q: Quelle différence de rôle entre Terraform et Ansible ?
  a: 'Terraform **crée** l''infrastructure (réseaux, VM, bases) et garde un state. Ansible **configure** ce qui tourne dessus (paquets, fichiers, services), sans state : il vérifie l''état réel à chaque passage.'
- q: 'Push ou pull : comment fonctionne Ansible par défaut ?'
  a: 'En **push** : le nœud de contrôle se connecte aux machines et leur applique la configuration. Puppet ou Chef fonctionnent plutôt en pull, avec un agent qui vient chercher sa configuration.'
quiz:
- q: Tu relances un playbook déjà appliqué, sans rien changer. Que doit afficher un bon playbook ?
  options:
  - Uniquement des tâches `changed`
  - Uniquement des tâches `ok`
  - Des erreurs
  - Rien du tout
  answer: 1
  explain: 'Un code idempotent ne modifie rien quand l''état voulu est déjà là : tout est `ok`.'
- q: Que faut-il au minimum sur un serveur Linux pour qu'Ansible le gère ?
  options:
  - Un agent Ansible
  - SSH et Python
  - Docker
  - Une base de données
  answer: 1
  explain: Ansible se connecte en SSH et exécute ses modules avec le Python de la machine cible.
- q: Tu dois créer 3 VM sur OpenStack puis y installer nginx. Quel partage est le plus courant ?
  options:
  - Tout avec Ansible
  - Tout avec Terraform
  - Terraform crée les VM, Ansible les configure
  - Ansible crée les VM, Terraform les configure
  answer: 2
  explain: 'Chaque outil fait ce pour quoi il est fait : Terraform pour l''infrastructure et son state, Ansible pour la configuration.'
---

**Ansible** est un outil de **gestion de configuration** et d'automatisation, open source, maintenu par Red Hat. Tu décris dans des fichiers YAML l'état que doivent avoir tes serveurs (tel paquet installé, tel fichier présent, tel service démarré), et Ansible se connecte à chaque machine pour l'amener dans cet état. Il est écrit en Python et s'installe uniquement sur la machine d'où tu le lances.

> **Les outils cités dans cette fiche.**
> - **Ansible** : l'outil d'automatisation open source de Red Hat, écrit en Python, qui configure des machines à partir de fichiers YAML.
> - **YAML** : un format de fichier texte lisible, basé sur l'indentation, utilisé pour les playbooks et les inventaires.
> - **SSH** : le protocole de connexion à distance sécurisée qu'Ansible utilise pour parler aux serveurs Linux.
> - **Terraform** : l'outil de HashiCorp qui crée l'infrastructure (réseaux, VM, DNS) et garde la trace de ce qu'il a créé dans un **state** ; **HCL** est son langage.
> - **OpenStack** : une plateforme de cloud privé qui fournit VM, réseaux et stockage par API.
> - **Kubernetes** : l'orchestrateur qui fait tourner et surveille des conteneurs sur un ensemble de machines.
> - **démon** (daemon) : un programme qui tourne en permanence en arrière-plan sur une machine.

## Le problème qu'il résout

Configurer un serveur à la main, c'est une suite de commandes tapées en SSH. Ça marche pour un serveur. Pour vingt, on oublie une étape sur l'un d'eux, les serveurs finissent tous un peu différents (on parle de **dérive de configuration**), et personne ne sait plus reconstruire une machine à l'identique.

Un script Bash règle une partie du problème, mais il décrit des **actions** (« ajoute cette ligne »). Relancé deux fois, il ajoute la ligne deux fois. Ansible décrit des **états** (« cette ligne est présente ») : relancé dix fois, le résultat est le même. C'est l'**idempotence**, et c'est toute la différence.

## Comment il fonctionne

| Élément | Rôle |
| --- | --- |
| **Nœud de contrôle** | la machine où Ansible est installé (ton poste, un bastion, une CI) |
| **Nœuds gérés** | les serveurs à configurer ; ils n'ont besoin que de SSH et de Python |
| **Inventaire** | la liste des nœuds gérés, rangés en groupes |
| **Module** | une unité de travail : installer un paquet, copier un fichier, gérer un service |
| **Playbook** | un fichier YAML qui dit quels modules appliquer à quels groupes |

<!-- schema:push -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="Ansible pousse ses tâches en SSH" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="252" height="200" rx="12" class="dg-zone dg-zc"/><text x="26" y="32" class="dg-zl" text-anchor="start">nœud de contrôle</text><g class="dg-box dg-pop" style="--d:0"><rect x="30" y="44" width="106" height="52" rx="9"/></g><text x="83.0" y="67.0" class="dg-t" text-anchor="middle" style="--d:0">inventaire</text><text x="83.0" y="85.0" class="dg-s" text-anchor="middle" style="--d:0">qui</text><g class="dg-box dg-pop" style="--d:0"><rect x="146" y="44" width="106" height="52" rx="9"/></g><text x="199.0" y="67.0" class="dg-t" text-anchor="middle" style="--d:0">playbook</text><text x="199.0" y="85.0" class="dg-s" text-anchor="middle" style="--d:0">quoi</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="30" y="130" width="222" height="56" rx="9"/></g><text x="141.0" y="155.0" class="dg-t" text-anchor="middle" style="--d:1">ansible-playbook</text><text x="141.0" y="173.0" class="dg-s" text-anchor="middle" style="--d:1">ton poste, un bastion, la CI</text><path d="M83 96 L83 128" class="dg-l c" marker-end="url(#g1-c)"/><path d="M199 96 L199 128" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="470" y="24" width="196" height="50" rx="9"/></g><text x="568.0" y="46.0" class="dg-t" text-anchor="middle" style="--d:2">web1</text><text x="568.0" y="64.0" class="dg-s" text-anchor="middle" style="--d:2">SSH + Python, rien d&#x27;autre</text><path d="M252 158 L380 158 L380 49 L468 49" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:3"><rect x="470" y="94" width="196" height="50" rx="9"/></g><text x="568.0" y="116.0" class="dg-t" text-anchor="middle" style="--d:3">web2</text><text x="568.0" y="134.0" class="dg-s" text-anchor="middle" style="--d:3">SSH + Python, rien d&#x27;autre</text><path d="M252 158 L380 158 L380 119 L468 119" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:4"><rect x="470" y="164" width="196" height="50" rx="9"/></g><text x="568.0" y="186.0" class="dg-t" text-anchor="middle" style="--d:4">db1</text><text x="568.0" y="204.0" class="dg-s" text-anchor="middle" style="--d:4">SSH + Python, rien d&#x27;autre</text><path d="M252 158 L380 158 L380 189 L468 189" class="dg-l c" marker-end="url(#g1-c)"/><text x="316" y="150" class="dg-s" text-anchor="middle">SSH</text><g class="dg-box dg-ghost dg-pop" style="--d:5"><rect x="14" y="244" width="154" height="40" rx="9"/></g><text x="91.0" y="269.0" class="dg-s" text-anchor="middle" style="--d:5">1. copie le module</text><g class="dg-box dg-ghost dg-pop" style="--d:6"><rect x="180" y="244" width="154" height="40" rx="9"/></g><text x="257.0" y="269.0" class="dg-s" text-anchor="middle" style="--d:6">2. l&#x27;exécute (Python)</text><g class="dg-box dg-ghost dg-pop" style="--d:7"><rect x="346" y="244" width="154" height="40" rx="9"/></g><text x="423.0" y="269.0" class="dg-s" text-anchor="middle" style="--d:7">3. renvoie du JSON</text><g class="dg-box dg-ghost dg-pop" style="--d:8"><rect x="512" y="244" width="154" height="40" rx="9"/></g><text x="589.0" y="269.0" class="dg-s" text-anchor="middle" style="--d:8">4. nettoie</text><text x="14" y="236" class="dg-zl" text-anchor="start">à chaque tâche, sur chaque machine</text></svg><figcaption>Aucun agent ne tourne sur les serveurs : ils ont seulement besoin de SSH et de Python.</figcaption></figure>
<!-- /schema:push -->

À chaque tâche, Ansible se connecte en SSH, envoie le code du module, l'exécute avec le Python de la machine, récupère le résultat en JSON et nettoie derrière lui. C'est pour ça qu'on dit qu'il est **sans agent** : rien ne tourne en permanence sur les serveurs, et il n'y a pas de démon à mettre à jour ni à sécuriser.

Chaque tâche renvoie un statut :

- **ok** : l'état était déjà le bon, rien n'a été fait ;
- **changed** : Ansible a modifié quelque chose ;
- **failed** : la tâche a échoué ;
- **skipped** : la tâche a été sautée (une condition n'était pas remplie).

## Ansible et Terraform

On les compare souvent, mais ils se complètent :

| | Terraform | Ansible |
| --- | --- | --- |
| Sert à | créer l'infrastructure | configurer les machines |
| Exemples | réseau, VM, base managée, DNS | paquets, fichiers, services, utilisateurs |
| Mémoire | un **state** qui note ce qui a été créé | aucune : vérifie l'état réel à chaque fois |
| Langage | HCL | YAML |

Un enchaînement classique : Terraform crée trois VM sur OpenStack et sort leurs adresses IP, Ansible s'y connecte et installe l'application.

## Ce qu'Ansible n'est pas

- **Pas un outil de déploiement d'infrastructure cloud** en premier lieu : il sait créer des VM via des modules, mais sans state, il gère mal leur suppression et leur évolution.
- **Pas un orchestrateur de conteneurs** : pour faire tourner des conteneurs en continu, c'est Kubernetes. Ansible peut en revanche installer un cluster ou y déposer des manifestes.
- **Pas un outil de supervision** : il applique un état au moment où on le lance, il ne surveille rien entre deux passages.

> **À retenir.** Ansible décrit un état voulu en YAML et l'applique en SSH, sans agent. Le cœur de l'outil, c'est l'idempotence : un playbook se relance sans danger, et un deuxième passage sans changement ne doit afficher que des `ok`.
