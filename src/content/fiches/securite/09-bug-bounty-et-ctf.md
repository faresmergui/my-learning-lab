---
title: Bug bounty, CTF et s'entraîner légalement
chapter: 9
order: 1
duration: 8
level: intermédiaire
tags:
- offensif
- entraînement
cards:
- q: Qu'est-ce qu'un programme de bug bounty ?
  a: Une entreprise autorise publiquement des chercheurs à tester certains de ses services, selon des règles écrites, et les **récompense** pour chaque faille valide signalée.
- q: Qu'est-ce que le « scope » d'un bug bounty ?
  a: "La liste de ce qu'on a le droit de tester (domaines, applis) et de ce qui est **hors périmètre** ou interdit (déni de service, ingénierie sociale, accès aux données d'autres utilisateurs). Sortir du scope fait perdre la protection juridique."
- q: Qu'est-ce qu'un CTF ?
  a: "*Capture The Flag* : une compétition ou un exercice où l'on résout des défis de sécurité sur des systèmes **conçus pour être attaqués**, afin de trouver un « drapeau » (une chaîne de texte) qui prouve la réussite."
- q: Différence entre un CTF « jeopardy » et « attaque-défense » ?
  a: "**Jeopardy** : des défis indépendants classés par catégorie (web, crypto, forensic…). **Attaque-défense** : chaque équipe défend ses services tout en attaquant ceux des autres."
- q: Qu'est-ce qu'une politique de divulgation coordonnée (VDP) ?
  a: Une page où une organisation explique comment lui signaler une faille et s'engage à ne pas poursuivre les personnes de bonne foi qui suivent ses règles. Souvent publiée dans un fichier `security.txt`.
- q: Pourquoi un lab local est-il idéal pour débuter ?
  a: "Tu attaques tes **propres** machines volontairement vulnérables (DVWA, Juice Shop…) : aucun risque légal, et tu peux observer en même temps ce que voient les logs côté défense."
quiz:
- q: "Un programme de bug bounty couvre `app.boutique.fr`. Tu trouves `admin.boutique.fr`, absent de la liste. Que fais-tu ?"
  options:
  - Tu le testes aussi, c'est le même domaine
  - Tu ne le testes pas, et tu peux demander au programme s'il est dans le périmètre
  - Tu le testes discrètement sans le signaler
  - Tu lances un scan léger seulement
  answer: 1
  explain: "Seul ce qui est listé est autorisé. Un sous-domaine voisin peut appartenir à un autre prestataire. Demander d'abord est la seule bonne réponse."
- q: Tu veux t'entraîner à l'injection SQL ce soir. Quelle option est légale ?
  options:
  - Le site d'un petit commerce, puisqu'il ne remarquera rien
  - Une appli volontairement vulnérable comme Juice Shop, lancée sur ta machine
  - Un site gouvernemental, pour la bonne cause
  - Le site de ton employeur sans prévenir personne
  answer: 1
  explain: "Seul un système qui t'appartient ou que tu es explicitement autorisé à tester est légal. Les applis volontairement vulnérables sont faites pour ça."
- q: "Dans un bug bounty, tu peux lire les commandes d'un autre client. Que fais-tu ?"
  options:
  - Tu télécharges toute la base pour prouver la gravité
  - Tu t'arrêtes à la preuve minimale (ton propre compte de test, ou un seul enregistrement), tu ne gardes rien et tu signales
  - Tu préviens les clients concernés toi-même
  - Tu publies la faille sur les réseaux sociaux
  answer: 1
  explain: "La règle est de prouver avec le minimum de données, de ne pas les conserver, et de passer par le canal du programme. Collecter des données personnelles sort du cadre et du RGPD."
---

La fiche précédente a posé le cadre : on ne teste que ce qu'on est autorisé à tester. Bonne nouvelle, il existe beaucoup d'endroits **faits exprès** pour s'entraîner, et des programmes où les entreprises **invitent** les chercheurs à chercher leurs failles. Comprendre comment pense un attaquant est le meilleur moyen de mieux défendre ce que tu construis.

> **Les termes cités dans cette fiche.**
> - **Bug bounty** : programme de récompense des failles signalées, souvent hébergé par une plateforme (**YesWeHack**, française, **HackerOne**, **Bugcrowd**, **Intigriti**).
> - **CTF** (*Capture The Flag*) : compétition de sécurité sur des systèmes préparés pour être attaqués.
> - **VDP** (*Vulnerability Disclosure Policy*) : politique de divulgation, qui explique comment signaler une faille sans récompense mais avec protection.
> - **security.txt** : un petit fichier standard, à l'adresse `/.well-known/security.txt` d'un site, qui indique à qui signaler une faille.
> - **OWASP** : une fondation qui publie des ressources libres sur la sécurité des applications, dont le **Top 10** des failles web les plus fréquentes.
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).
> - **cluster** : un groupe de machines qui travaillent ensemble comme un seul système.

## Le bug bounty

Une entreprise publie un programme : « vous pouvez tester ces applications, selon ces règles, et nous vous payons selon la gravité de ce que vous trouvez ». C'est un pentest **permanent**, fait par des centaines de personnes, payé au résultat.

Ce qui compte dans un programme :

- **Le périmètre** : les domaines et applis autorisés, et les exclusions explicites.
- **Les interdits** : presque toujours le déni de service, l'ingénierie sociale (piéger les employés), l'accès aux données d'autres utilisateurs, les scans massifs.
- **La « safe harbor »** : l'engagement de ne pas poursuivre les personnes qui respectent les règles. C'est elle qui te protège juridiquement.
- **La divulgation** : on ne publie rien avant que l'entreprise ait corrigé, et seulement si elle l'accepte.

En pratique, les débutants y gagnent peu au début : les failles faciles sont trouvées très vite. C'est surtout une excellente école une fois les bases acquises.

**Côté DevOps**, l'inverse t'intéresse aussi : publier un `security.txt` et une VDP sur tes propres services permet à quelqu'un qui tombe sur une faille de te prévenir au lieu de l'exploiter ou de la vendre.

## Les CTF

Un CTF est un jeu : chaque défi cache un **drapeau** (du texte comme `FLAG{...}`) qu'on ne peut récupérer qu'en résolvant le problème. Les catégories classiques :

| Catégorie | Ce qu'on y apprend |
| --- | --- |
| **Web** | les failles des applis web (injections, contrôle d'accès, sessions) |
| **Crypto** | pourquoi un chiffrement mal utilisé se casse |
| **Forensic** | analyser des traces après coup : captures réseau, images disque, logs |
| **Reverse** | comprendre ce que fait un programme compilé |
| **Pwn** | exploiter des bugs mémoire dans des programmes |
| **Misc / OSINT** | logique, recherche d'informations publiques |

Pour un profil DevOps, **web**, **forensic** et les défis **Linux/réseau** sont les plus utiles : ils recoupent ton travail quotidien (lire des logs, comprendre un flux réseau, repérer une mauvaise configuration).

## Où s'entraîner légalement

| Plateforme | Pour qui | Points forts |
| --- | --- | --- |
| **TryHackMe** | débutant | parcours guidés, explications pas à pas, salles « défense » aussi |
| **Root-Me** | tous niveaux | française, gratuite, des centaines de défis par catégorie |
| **Hack The Box** | intermédiaire à avancé | machines réalistes, parcours « Academy » très complets |
| **PortSwigger Web Security Academy** | web, tous niveaux | gratuite, la meilleure référence sur les failles web, avec labs |
| **OverTheWire** (Bandit) | débutant Linux | apprendre la ligne de commande sous forme de jeu |
| **picoCTF** | débutant | CTF éducatif permanent |

Et en local, sur ta propre machine (dans des conteneurs, jamais exposés sur Internet) :

- **OWASP Juice Shop** : une boutique en ligne pleine de failles, avec un tableau de score.
- **DVWA** (*Damn Vulnerable Web Application*) : les failles web classiques, avec plusieurs niveaux de difficulté.
- **Kubernetes Goat** : un cluster volontairement mal configuré, idéal pour comprendre les risques que les fiches Kubernetes de ce module décrivent.

L'avantage du lab local : tu vois les **deux côtés**. Tu peux regarder les logs du serveur pendant l'attaque et te demander « est-ce que j'aurais détecté ça ? ».

## Un parcours raisonnable pour toi

1. **OverTheWire Bandit** pour la ligne de commande sous un angle sécurité.
2. **TryHackMe**, parcours débutant, puis les salles sur Linux, le réseau et le web.
3. **PortSwigger Academy** pour les failles web, en lisant d'abord la théorie de chaque thème.
4. **Kubernetes Goat** pour relier tout ça à ton métier.
5. Un CTF en équipe (il y en a régulièrement en ligne, listés sur **CTFtime**) quand tu te sens à l'aise.

> **À retenir.** Un bug bounty est un terrain autorisé, mais seulement dans son périmètre et selon ses règles. Les CTF et les labs sont faits pour être attaqués : c'est là qu'on apprend, sans risque. Et pour tes propres services, un `security.txt` et une politique de divulgation invitent les gens honnêtes à te prévenir.
