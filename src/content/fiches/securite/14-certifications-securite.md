---
title: Certifications sécurité pour un DevOps
chapter: 14
order: 1
duration: 6
level: intermédiaire
tags:
- carrière
- certifications
cards:
- q: Quelle certification sécurité est la plus directement liée au travail d'un DevOps sur Kubernetes ?
  a: "La **CKS** (Certified Kubernetes Security Specialist) de la CNCF : un examen pratique sur la sécurisation d'un cluster. Il faut avoir la **CKA** valide pour la passer."
- q: Quelle certification sert de socle généraliste en sécurité ?
  a: "**CompTIA Security+** : vocabulaire, menaces, cryptographie, gestion des identités, réponse aux incidents. Un QCM reconnu, sans prérequis."
- q: Quelle est la différence entre une certification « QCM » et une certification « pratique » ?
  a: "Le **QCM** vérifie des connaissances. La **pratique** (CKS, OSCP, eJPT) te met devant de vraies machines à configurer ou à tester dans un temps limité : elle prouve un savoir-faire, et elle est plus appréciée en entretien technique."
- q: Que vaut la CISSP pour un DevOps intermédiaire ?
  a: "Elle est prestigieuse mais orientée **management** et exige **5 ans d'expérience** en sécurité pour être pleinement délivrée. Ce n'est pas une priorité à ce stade."
- q: Existe-t-il une formation sécurité gratuite et officielle en France ?
  a: "Oui, **SecNumacadémie**, le MOOC de l'ANSSI : une bonne introduction, avec une attestation de suivi."
quiz:
- q: Tu as la CKA et tu gères des clusters en production. Quelle certification sécurité choisir en premier ?
  options:
  - OSCP
  - CKS
  - CISSP
  - CEH
  answer: 1
  explain: "La CKS prolonge directement la CKA et ton travail quotidien : RBAC, NetworkPolicies, Pod Security, scan d'images, détection avec Falco."
- q: "Tu veux comprendre comment pensent les attaquants, sans viser un métier de pentesteur. Quel choix est le plus adapté ?"
  options:
  - L'OSCP immédiatement
  - Une certification d'entrée pratique comme l'eJPT, après les parcours TryHackMe
  - La CISSP
  - Aucune, ça ne sert à rien pour un DevOps
  answer: 1
  explain: "L'eJPT est accessible et pratique ; l'OSCP est longue et exigeante, pensée pour les futurs pentesteurs."
---

Une certification n'apprend rien en elle-même : c'est le **travail de préparation** qui fait progresser. Mais elle donne un objectif, un programme structuré et une preuve lisible sur un CV. Pour un DevOps, l'idée n'est pas de devenir pentesteur, mais de **sécuriser ce qu'on construit** et de **parler le même langage** que l'équipe sécurité. Cette fiche trie les certifications selon ce qu'elles t'apporteraient.

> **Les sigles cités dans cette fiche.**
> - **CNCF** : la fondation qui gère Kubernetes et ses certifications (CKA, CKAD, CKS).
> - **CompTIA**, **ISC2**, **OffSec**, **INE**, **EC-Council** : des organismes qui délivrent des certifications de sécurité.
> - **Examen pratique** : on travaille sur un vrai environnement (terminal, cluster, machines à tester), par opposition au **QCM**.


> **Les termes et outils cités dans cette fiche.**
> - **cluster** : un groupe de machines qui travaillent ensemble comme un seul système.
> - **RBAC** : le contrôle d'accès par rôles : on donne des droits à des rôles, puis des rôles aux personnes ou programmes.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **GCP** : Google Cloud Platform, le cloud public de Google.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **CTF** : Capture The Flag : un concours de sécurité où l'on résout des défis.
> - **ANSSI** : l'agence nationale de la sécurité des systèmes d'information, en France.

## Les certifications, par objectif

| Objectif | Certification | Format | Pour toi |
| --- | --- | --- | --- |
| Sécuriser Kubernetes | **CKS** (CNCF) | pratique, 2 h | ★★★ la suite logique de la CKA |
| Sécuriser le cloud | **AWS Security Specialty**, **AZ-500** (Azure), Google Professional Cloud Security Engineer | QCM | ★★★ si tu travailles sur ce cloud |
| Socle généraliste | **Security+** (CompTIA), **ISC2 CC** | QCM | ★★ pour combler les bases sécurité et réseau |
| Comprendre l'attaque | **eJPT** (INE), certifications Hack The Box ou TryHackMe | pratique | ★★ une bonne découverte du pentest |
| Devenir pentesteur | **OSCP** (OffSec), **HTB CPTS** | pratique, longue | ★ seulement si tu changes d'orientation |
| Management de la sécurité | **CISSP** (ISC2) | QCM, 5 ans d'expérience requis | plus tard, pour un rôle de responsable |

## Les plus utiles pour toi

**CKS (Certified Kubernetes Security Specialist).** Un examen pratique de 2 heures sur des clusters réels : durcir le cluster, RBAC, NetworkPolicies, Pod Security, secrets, scan d'images, analyse des appels système, détection avec Falco. Elle reprend presque tout le module Sécurité de ce site appliqué à Kubernetes. Il faut avoir une **CKA valide** pour s'y inscrire.

**La certification sécurité de ton cloud.** Si tu travailles surtout sur AWS (ou Azure, ou GCP), sa certification sécurité couvre l'IAM, le chiffrement, la journalisation et la réponse aux incidents dans ce cloud, ce qui est directement utile au quotidien. Elle suppose en général une certification de niveau associé ou une bonne pratique de la plateforme.

**Security+ (ou ISC2 CC).** Si les notions de la fiche « Principes et modèle de menace » te semblent encore floues, c'est le bon socle. Elle couvre aussi beaucoup de réseau, ton point plus faible. **ISC2 CC** (*Certified in Cybersecurity*) est une alternative d'entrée plus légère.

## Comprendre l'attaque, sans changer de métier

L'**eJPT** (*eLearnSecurity Junior Penetration Tester*) est un examen pratique accessible : un petit réseau à analyser en autonomie. C'est une bonne façon de valider ce que tu auras appris sur TryHackMe ou Hack The Box (fiche « Bug bounty, CTF »).

L'**OSCP** est la référence des pentesteurs, mais elle demande des centaines d'heures de préparation. Le **CEH** (EC-Council) est connu des recruteurs non techniques, mais souvent jugé trop théorique par les praticiens.

## Commencer gratuitement

- **SecNumacadémie** : le MOOC gratuit de l'ANSSI, en français, pour les bases de la sécurité.
- Les **parcours gratuits** de TryHackMe et de la **PortSwigger Web Security Academy**.
- La documentation officielle de Kubernetes sur la sécurité, qui est la base du programme de la CKS.

## Un ordre raisonnable

1. **SecNumacadémie** ou les bases de ce module, pour le vocabulaire.
2. **CKA** si ce n'est pas déjà fait (fiche « Passer l'examen CKA » du module Kubernetes).
3. **CKS**, la plus rentable pour ton métier.
4. La **certification sécurité de ton cloud** principal.
5. Si l'attaque te plaît : **eJPT**, puis plus loin si tu le souhaites.

Les programmes, formats et prix changent régulièrement : vérifie toujours la page officielle de l'examen avant de t'inscrire.

> **À retenir.** Pour un DevOps, les certifications les plus rentables sont celles qui recoupent ton travail : la CKS pour Kubernetes et la certification sécurité de ton cloud. Security+ comble les bases, l'eJPT fait découvrir l'attaque. Garde l'OSCP et la CISSP pour un changement d'orientation ou de niveau de responsabilité.
