---
title: Résoudre un challenge Root Me par catégorie
chapter: 12
order: 1
duration: 14
level: intermédiaire
tags:
- Root Me
- CTF
- web
- crypto
- stéganographie
- reverse
- forensic
cards:
- q: Comment est organisé Root Me ?
  a: 'Par **catégories** : Web-Client, Web-Serveur, Cryptanalyse, Stéganographie, Programmation, Réseau, Cracking (rétro-ingénierie), App-Script, App-Système, Forensic, Réaliste… Chaque catégorie a sa logique propre, mais le [fil conducteur](../10-methodologie-le-fil-conducteur/) reste le même : observer, énumérer, raisonner, essayer, noter.'
- q: Par où aborder un challenge Web-Serveur ?
  a: 'Par l''**observation** : code source de la page, requêtes envoyées (via les outils de développement du navigateur ou un proxy comme Burp Suite), paramètres, cookies, en-têtes. On cherche ensuite quelle **famille d''injection ou de défaut de logique** le challenge illustre (le titre et la difficulté sont souvent des indices).'
- q: Comment reconnaître un challenge de cryptanalyse ?
  a: 'Par la **forme** du texte : longueur, alphabet, présence de `=` final (base64), de chiffres hexadécimaux, de motifs répétés. On identifie d''abord l''**encodage ou le chiffrement** (un outil comme CyberChef ou dcode.fr aide), puis on applique la technique correspondante. Encoder n''est pas chiffrer : base64 ou ROT13 se « décodent », ils ne protègent rien.'
- q: Quelle est la démarche en stéganographie ?
  a: Chercher ce qui est **caché dans un fichier** (image, son). On regarde d'abord les **métadonnées** (`exiftool`), puis la structure du fichier (`binwalk` pour détecter des fichiers imbriqués, `strings` pour le texte lisible), puis les techniques spécifiques (bits de poids faible d'une image, spectrogramme d'un son). Toujours du plus simple au plus sophistiqué.
- q: Qu'attend un challenge de rétro-ingénierie (cracking) ?
  a: Comprendre ce que fait un **programme** sans son code source, pour retrouver un mot de passe ou une logique. On commence par l'analyse **statique** (`strings`, un décompilateur comme Ghidra), puis **dynamique** (observer l'exécution avec un débogueur). Souvent, le secret est visible en clair ou dans une comparaison simple.
- q: Comment aborder un challenge de programmation ?
  a: 'Ils imposent une **réponse rapide** (quelques secondes), impossible à la main : il faut **scripter**. On automatise la récupération de l''énoncé, le calcul et l''envoi de la réponse, en général en Python (avec `requests` ou `pwntools`). L''enjeu est la **vitesse d''automatisation**, pas l''algorithme lui-même.'
- q: Quelle catégorie choisir pour commencer ?
  a: 'Celle qu''on veut **travailler**, en difficulté croissante. Pour un profil DevOps/cloud, **Web-Serveur**, **Réseau** et **App-Système** sont les plus proches du métier. On fait les challenges d''une catégorie dans l''ordre : chacun introduit une notion réutilisée dans le suivant.'
quiz:
- q: Un challenge te donne la chaîne `aGVsbG8=`. Quel est le réflexe ?
  options:
  - La soumettre telle quelle
  - Reconnaître du base64 (le `=` final) et la décoder
  - La chiffrer à nouveau
  - Chercher un exploit web
  answer: 1
  explain: 'Le `=` de padding et l''alphabet trahissent le base64. C''est un encodage, pas un chiffrement : il se décode directement (ici « hello »).'
- q: Sur un challenge Web-Serveur, tu regardes la page et tu ne vois rien d'évident. Que fais-tu d'abord ?
  options:
  - Tu abandonnes
  - Tu lis le code source, tu inspectes les requêtes et les paramètres avec les outils du navigateur ou Burp
  - Tu scannes les ports de root-me.org
  - Tu forces le mot de passe admin
  answer: 1
  explain: 'Tout challenge web se résout d''abord par l''observation du client : source, requêtes, paramètres, cookies. (Scanner l''infrastructure de Root Me elle-même serait hors sujet et interdit.)'
- q: On te donne une image PNG et le flag est « caché dedans ». Premier geste ?
  options:
  - Ouvrir l'image et regarder fixement
  - Lancer exiftool, strings et binwalk pour voir métadonnées, texte et fichiers imbriqués
  - La convertir en PDF
  - La supprimer
  answer: 1
  explain: 'On part toujours du plus simple : métadonnées, texte lisible, fichiers cachés, avant les techniques fines comme les bits de poids faible.'
- q: Un challenge de programmation exige une réponse en 2 secondes. Comment faire ?
  options:
  - Répondre très vite à la main
  - Écrire un script qui récupère l'énoncé, calcule et renvoie la réponse automatiquement
  - Demander un délai
  - C'est impossible
  answer: 1
  explain: Ces challenges testent ta capacité à automatiser un échange, en général en Python. La main est trop lente par conception.
---

Root Me range ses épreuves par **catégorie**, chacune avec ses codes. Le [fil conducteur](../10-methodologie-le-fil-conducteur/) ne change pas — observer, énumérer, raisonner, essayer, noter — mais les **premiers gestes** diffèrent. Cette fiche donne, pour chaque grande catégorie, la bonne porte d'entrée. Tout se fait sur la plateforme, qui est **prévue pour ça** : on n'attaque jamais l'infrastructure de Root Me elle-même.

> **Les termes cités dans cette fiche.**
> - **Encodage** : une transformation réversible sans secret (base64, hexadécimal, URL). Ça se **décode**.
> - **Chiffrement** : une transformation qui dépend d'une **clé**. Sans la clé (ou une faiblesse), ça ne se lit pas.
> - **Métadonnées** : des informations attachées à un fichier (auteur, date, appareil) sans être son contenu visible.
> - **Analyse statique / dynamique** : étudier un programme sans l'exécuter / en l'exécutant.
> - **Burp Suite** : un proxy qui intercepte et modifie les requêtes entre le navigateur et un site.
> - **CyberChef** : un outil web « couteau suisse » pour encoder, décoder, déchiffrer.

## Le réflexe commun

Quelle que soit la catégorie : **lire l'énoncé en entier** (il dit souvent ce qu'on cherche), repérer la **difficulté** (un indice sur la technique), **observer** avant d'agir, et **noter**. Le titre d'un challenge est fréquemment un indice déguisé.

## Web-Client et Web-Serveur

Le plus gros morceau, et le plus proche du métier.

- **Observer d'abord** : code source de la page (`Ctrl+U`), outils de développement du navigateur (onglets *Réseau* et *Éléments*), cookies, en-têtes, paramètres d'URL.
- **Intercepter** les requêtes avec **Burp Suite** ou l'outil intégré du navigateur pour les lire et les modifier.
- **Web-Client** : la faiblesse est côté navigateur (JavaScript lisible, contrôle contournable, données cachées dans la page). On lit le code livré au client.
- **Web-Serveur** : la faiblesse est côté serveur. Les grandes familles à connaître (détaillées dans la fiche [Panorama des outils](../13-panorama-des-outils/) et dans PortSwigger Academy) : **injection** (SQL, commandes), **inclusion de fichiers**, **upload** non filtré, **défaut de logique** ou d'authentification, **contrôle d'accès** manquant.

Pour apprendre ces failles proprement, **PortSwigger Web Security Academy** est la meilleure ressource gratuite, avec théorie et labs.

## Cryptanalyse

On identifie **avant** d'attaquer :

1. **encodage ?** `=` final et alphabet lettres/chiffres → base64 ; que des chiffres `0-9a-f` → hexadécimal ; `%xx` → URL. Ça se **décode** (CyberChef).
2. **chiffrement classique ?** décalage de lettres (César/ROT), substitution (analyse de fréquences), Vigenère.
3. **chiffrement moderne ?** on cherche une **faiblesse d'implémentation** (clé réutilisée, paramètres faibles), pas à « casser » l'algorithme.

Règle d'or : **encoder n'est pas chiffrer**. Beaucoup de challenges « faciles » ne sont qu'une pile d'encodages.

## Stéganographie et Forensic

On fouille un **fichier** (image, son, capture réseau, image disque), du plus simple au plus fin :

| Étape | Outils |
| --- | --- |
| métadonnées | `exiftool` |
| texte lisible | `strings` |
| fichiers imbriqués | `binwalk`, `foremost` |
| image : bits de poids faible, canaux | `zsteg`, `stegsolve` |
| son : spectrogramme | Audacity, Sonic Visualiser |
| capture réseau (`.pcap`) | Wireshark, suivre les flux |

En **forensic**, on reconstitue ce qui s'est passé à partir de traces (logs, mémoire, disque). La patience prime : le flag est rarement là où on regarde en premier.

## Cracking (rétro-ingénierie)

Comprendre un **programme** sans son code :

1. **statique** : `strings` (le secret est parfois en clair), puis un décompilateur comme **Ghidra** pour lire la logique ;
2. **dynamique** : exécuter sous un **débogueur** (gdb, et pour les challenges web/binaires `pwntools`) pour observer les comparaisons.

Beaucoup de challenges d'introduction se résolvent par un simple `strings` ou en repérant la comparaison du mot de passe.

## Programmation

Ils imposent une **réponse automatisée** en quelques secondes : impossible à la main. On **script** (Python, avec `requests` pour le web ou `pwntools` pour une socket) : récupérer l'énoncé, calculer, renvoyer. L'enjeu est la **boucle d'automatisation**, pas l'algorithme.

## Réseau et App-Système

- **Réseau** : analyse de captures (`.pcap`) dans Wireshark, compréhension des protocoles. Proche des fiches du module Réseaux.
- **App-Système** : interaction avec un système Linux, permissions, binaires — la logique de l'[élévation de privilèges](../11-compromettre-une-machine-d-entrainement/) sur machine.

Ce sont les catégories les plus utiles pour un profil **DevOps / cloud**.

## Un parcours conseillé

1. **Web-Serveur** en difficulté croissante, en parallèle de PortSwigger Academy ;
2. **Cryptanalyse** pour les réflexes encodage/chiffrement ;
3. **App-Système** et **Réseau**, proches du métier ;
4. **Stéganographie / Forensic** pour varier ;
5. **Cracking** quand on veut aller vers le bas niveau.

Fais les challenges d'une catégorie **dans l'ordre** : chacun réutilise le précédent. Et pour chaque réussite, note la **technique** dans ton fichier maître.

> **À retenir.** Sur Root Me, la catégorie dicte les premiers gestes, mais la démarche reste la même. Web : observer source, requêtes et paramètres (Burp). Crypto : identifier encodage vs chiffrement avant d'attaquer (encoder n'est pas chiffrer). Stégano/forensic : métadonnées → strings → binwalk → techniques fines. Cracking : statique (strings, Ghidra) puis dynamique. Programmation : scripter. Avance catégorie par catégorie, dans l'ordre, et note chaque technique.
