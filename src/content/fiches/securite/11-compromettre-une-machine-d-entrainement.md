---
title: Compromettre une machine d'entraînement
chapter: 11
order: 1
duration: 14
level: intermédiaire
tags:
- CTF
- boot2root
- énumération
- élévation de privilèges
- Hack The Box
- TryHackMe
cards:
- q: Qu'est-ce qu'une machine « boot2root » ?
  a: Une machine virtuelle volontairement vulnérable (sur Hack The Box, TryHackMe, VulnHub) dont le but est d'obtenir d'abord un **accès utilisateur**, puis les droits **root/administrateur**. Deux flags valident ces deux étapes. C'est l'entraînement le plus proche d'un vrai pentest interne.
- q: Par quoi commence toujours une machine ?
  a: 'Par le **scan des ports** : savoir quels services écoutent (web, SSH, SMB, FTP, base de données…) et dans quelles **versions**. On utilise typiquement `nmap`, d''abord pour trouver les ports ouverts, puis pour détecter versions et services sur ces ports.'
- q: Qu'énumère-t-on sur un service web ?
  a: Les **répertoires et fichiers cachés** (avec un outil de *content discovery* comme gobuster, ffuf ou feroxbuster et une liste de mots), le **code source** des pages, les **technologies** utilisées (CMS, framework, versions), les pages de **login**, les **formulaires** et les paramètres. Le web est le vecteur d'accès le plus fréquent.
- q: Qu'appelle-t-on « accès initial » (*foothold*) ?
  a: 'Le **premier pied dans la machine** : obtenir une exécution de commandes ou une session, souvent avec les droits d''un utilisateur de service peu privilégié. On y arrive en exploitant une faiblesse d''un service exposé (web vulnérable, identifiants faibles, service non à jour).'
- q: Qu'est-ce que l'élévation de privilèges, et comment la prépare-t-on ?
  a: 'Passer d''un compte limité à **root/administrateur**. On commence toujours par **ré-énumérer depuis l''intérieur** : droits sudo, binaires SUID, tâches planifiées (cron), services mal configurés, mots de passe en clair, version du noyau. Des scripts comme linPEAS/winPEAS automatisent cette énumération.'
- q: Qu'est-ce que GTFOBins ?
  a: 'Un site de référence qui recense les **binaires Linux légitimes détournables** : si un binaire courant est exécutable avec des droits élevés (sudo, SUID), GTFOBins indique s''il permet, par une fonction détournée, d''obtenir un shell privilégié. L''équivalent Windows s''appelle LOLBAS.'
- q: Pourquoi documenter chaque machine à la fin ?
  a: Pour **ancrer la méthode** et construire sa bibliothèque personnelle. Écrire le chemin complet (recon → foothold → privesc) transforme une réussite ponctuelle en réflexe réutilisable, et t'entraîne à rédiger comme dans un vrai rapport de pentest.
quiz:
- q: Tu viens de te connecter à une nouvelle machine TryHackMe. Quel est ton tout premier geste ?
  options:
  - Chercher directement une faille root
  - Scanner les ports pour savoir quels services tournent
  - Redémarrer la machine
  - Deviner le mot de passe root
  answer: 1
  explain: 'On ne peut rien attaquer qu''on n''a pas d''abord découvert : le scan de ports ouvre tout le reste.'
- q: Un scan montre un seul port web ouvert. La page d'accueil est banale et tu bloques. Que faire ?
  options:
  - Conclure que la machine est impossible
  - Énumérer les répertoires cachés et lire le code source des pages
  - Rescanner les mêmes ports en boucle
  - Passer à une autre machine
  answer: 1
  explain: 'Un site a presque toujours plus que sa page d''accueil : pages d''admin, fichiers oubliés, commentaires dans le HTML. C''est le « enumerate harder » appliqué au web.'
- q: Tu as obtenu un shell utilisateur. Quelle est la bonne étape suivante avant de chercher un exploit ?
  options:
  - Tenter immédiatement des exploits du noyau au hasard
  - 'Ré-énumérer depuis l''intérieur : sudo, SUID, cron, configs, mots de passe'
  - Supprimer des fichiers
  - Te déconnecter
  answer: 1
  explain: 'L''élévation de privilèges commence par l''énumération locale. Les exploits de noyau sont bruyants et risqués : on les garde pour la fin.'
- q: '`sudo -l` montre que tu peux lancer un binaire courant en root. Quel réflexe ?'
  options:
  - Abandonner, ce n'est pas un exploit
  - Vérifier sur GTFOBins si ce binaire permet d'obtenir un shell root
  - Réinstaller le binaire
  - Changer le mot de passe root
  answer: 1
  explain: 'GTFOBins recense précisément ces détournements : un binaire autorisé en sudo est souvent le chemin direct vers root.'
---

Une **machine d'entraînement** (Hack The Box, TryHackMe, VulnHub) se joue comme un petit pentest interne : on part de rien, on cherche un premier accès, puis on monte en privilèges jusqu'à root. C'est l'exercice qui ressemble le plus au métier. Cette fiche applique le [fil conducteur](../10-methodologie-le-fil-conducteur/) à ce format ; elle décrit la **démarche**, pas des recettes d'attaque clés en main.

> **Les termes cités dans cette fiche.**
> - **Boot2root** : une machine vulnérable dont l'objectif est d'obtenir les droits root/administrateur.
> - **Foothold** (accès initial) : le premier accès obtenu sur la machine.
> - **Content discovery** : la recherche de répertoires et fichiers non listés sur un serveur web.
> - **Shell** : un accès en ligne de commande sur la machine cible.
> - **SUID** : un bit sur un fichier Linux qui le fait s'exécuter avec les droits de son propriétaire (souvent root).
> - **Reverse shell** : une connexion que la cible ouvre vers toi, te donnant une ligne de commande à distance.
> - **linPEAS / winPEAS** : des scripts qui énumèrent automatiquement les pistes d'élévation de privilèges.

## Vue d'ensemble

<!-- schema:killchain -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Le trajet type d&#x27;une machine" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="10" y="60" width="118" height="58" rx="9"/></g><text x="69.0" y="86.0" class="dg-s" text-anchor="middle" style="--d:0">Scan</text><text x="69.0" y="104.0" class="dg-s" text-anchor="middle" style="--d:0">ports ouverts</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="142" y="60" width="118" height="58" rx="9"/></g><text x="201.0" y="86.0" class="dg-s" text-anchor="middle" style="--d:1">Énumérer</text><text x="201.0" y="104.0" class="dg-s" text-anchor="middle" style="--d:1">chaque service</text><path d="M126 89 L140 89" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="274" y="60" width="118" height="58" rx="9"/></g><text x="333.0" y="86.0" class="dg-s" text-anchor="middle" style="--d:2">Accès initial</text><text x="333.0" y="104.0" class="dg-s" text-anchor="middle" style="--d:2">un pied dedans</text><path d="M258 89 L272 89" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-pop" style="--d:3"><rect x="406" y="60" width="118" height="58" rx="9"/></g><text x="465.0" y="86.0" class="dg-s" text-anchor="middle" style="--d:3">Stabiliser</text><text x="465.0" y="104.0" class="dg-s" text-anchor="middle" style="--d:3">s&#x27;orienter</text><path d="M390 89 L404 89" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="538" y="60" width="118" height="58" rx="9"/></g><text x="597.0" y="86.0" class="dg-s" text-anchor="middle" style="--d:4">Privesc</text><text x="597.0" y="104.0" class="dg-s" text-anchor="middle" style="--d:4">devenir root</text><path d="M522 89 L536 89" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-ghost dg-pop" style="--d:5"><rect x="274" y="146" width="118" height="34" rx="7"/></g><text x="333.0" y="168.0" class="dg-s" text-anchor="middle" style="--d:5">flag user</text><path d="M333.0 118 L333.0 146" class="dg-l dash" marker-end="url(#g2-n)"/><g class="dg-box dg-ghost dg-pop" style="--d:6"><rect x="538" y="146" width="118" height="34" rx="7"/></g><text x="597.0" y="168.0" class="dg-s" text-anchor="middle" style="--d:6">flag root</text><path d="M597.0 118 L597.0 146" class="dg-l dash" marker-end="url(#g2-n)"/><text x="340.0" y="210" class="dg-s" text-anchor="middle">à chaque étape, on ré-énumère avant de forcer</text></svg><figcaption>Scanner, énumérer chaque service, obtenir un premier accès (flag utilisateur), puis élever ses privilèges jusqu&#x27;à root (flag root).</figcaption></figure>
<!-- /schema:killchain -->

Le trajet type est toujours le même : **scanner**, **énumérer** chaque service, trouver un **accès initial**, puis **élever ses privilèges**. On revient en arrière à chaque nouvelle information.

## 1. Reconnaissance : le scan de ports

On commence par savoir **ce qui écoute**. Avec `nmap` :

1. un premier scan pour trouver les **ports ouverts** ;
2. un second, sur ces ports, pour détecter **services et versions** (`-sV`) et lancer les scripts par défaut (`-sC`).

On note chaque port, chaque service, chaque version. Une version précise est une piste en or : elle peut correspondre à une vulnérabilité connue (CVE).

## 2. Énumération, service par service

Chaque service ouvert se creuse avec ses propres outils. Objectif : dresser l'inventaire **complet** avant d'attaquer quoi que ce soit.

| Service | Ce qu'on cherche | Outils types |
| --- | --- | --- |
| **Web (80/443/8080…)** | répertoires cachés, code source, versions de CMS/framework, logins, paramètres | navigateur, gobuster/ffuf, whatweb, nikto, Burp Suite |
| **SMB (445)** | partages accessibles, fichiers, utilisateurs | smbclient, enum4linux, crackmapexec |
| **FTP (21)** | connexion anonyme, fichiers déposés | client ftp |
| **SSH (22)** | version, méthodes d'authentification | le client ssh, la bannière |
| **Bases de données** | accès par défaut, données exposées | le client correspondant |

Le **web** est le vecteur le plus fréquent : on y regarde toujours le **code source** des pages, les **commentaires**, les fichiers oubliés (`robots.txt`, sauvegardes), et on fait du **content discovery** avec une bonne liste de mots (SecLists).

## 3. Trouver l'accès initial

À partir de l'inventaire, on cherche **une** faiblesse qui donne une exécution de commandes ou une session. Les grandes familles (détaillées dans la fiche [Résoudre un challenge Root Me](../12-resoudre-un-challenge-root-me/) pour le web) :

- un **service connu vulnérable** (une version avec une CVE documentée) ;
- une **application web vulnérable** (injection, upload de fichier, etc.) ;
- des **identifiants faibles ou par défaut**, ou trouvés pendant l'énumération ;
- un **fichier ou une donnée exposés** contenant un secret.

Le but de cette phase est modeste : obtenir un **premier pied**, même avec peu de droits. Souvent, cela passe par un **reverse shell** (la cible se connecte à ta machine d'attaque, qui écoute).

## 4. Stabiliser et s'orienter

Une fois dedans :

- **stabiliser** le shell (le rendre interactif) ;
- repérer **qui on est** (`whoami`, `id`) et **où on est** ;
- lire le **répertoire personnel**, l'historique, les fichiers de configuration ;
- récupérer le **flag utilisateur** s'il est accessible.

## 5. Élévation de privilèges

C'est souvent l'étape la plus formatrice. Règle : **on ré-énumère depuis l'intérieur avant d'exploiter**. Les pistes classiques, du plus simple au plus risqué :

| Piste | Ce qu'on regarde |
| --- | --- |
| **Droits sudo** | `sudo -l` : quels programmes on peut lancer en root (→ GTFOBins) |
| **Binaires SUID** | fichiers exécutés avec les droits du propriétaire (→ GTFOBins) |
| **Tâches cron** | scripts planifiés modifiables ou lancés en root |
| **Services mal configurés** | permissions trop larges, chemins modifiables |
| **Secrets** | mots de passe en clair dans des fichiers, historiques, bases |
| **Noyau / logiciels obsolètes** | exploits connus — bruyants, à garder pour la fin |

Des scripts comme **linPEAS** (Linux) ou **winPEAS** (Windows) énumèrent automatiquement toutes ces pistes et les surlignent. On lit leur sortie **en entier**, calmement.

## 6. Documenter

À la fin, on écrit le **chemin complet** : ports → service exploité → accès initial → piste de privesc → root. C'est le réflexe du write-up : il ancre la méthode, nourrit tes notes maîtres, et t'entraîne à rédiger comme dans un vrai rapport.

## Ordre d'attaque conseillé

Quand plusieurs services sont ouverts, on priorise en général : **web** d'abord (le plus riche), puis les **partages de fichiers** (SMB/FTP), puis le reste. On garde SSH pour s'y **connecter** une fois des identifiants trouvés, rarement comme point d'entrée direct.

> **À retenir.** Une machine se joue en appliquant le fil conducteur : scanner les ports, énumérer **chaque** service à fond (surtout le web), trouver un accès initial via une seule faiblesse, se stabiliser, puis élever ses privilèges en **ré-énumérant depuis l'intérieur** (sudo, SUID, cron, secrets, puis noyau en dernier). GTFOBins et linPEAS sont tes meilleurs alliés pour la privesc. Documente le chemin complet à la fin.
