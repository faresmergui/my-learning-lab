---
title: Arch Linux, pacman et l'AUR
chapter: 6
order: 1
duration: 14
level: Intermédiaire
tags:
- Arch Linux
- pacman
- AUR
- yay
- rolling release
- paquets
cards:
- q: Qu'est-ce qu'une distribution en « rolling release » ?
  a: 'Une distribution **sans versions majeures** : les logiciels sont mis à jour en continu, dès que leurs nouvelles versions sont prêtes. Pas de « grosse mise à niveau » tous les deux ans comme Ubuntu ou Windows, mais des mises à jour régulières, à faire **souvent** et **en entier**.'
- q: Quels dépôts utilise Omarchy ?
  a: 'Les dépôts officiels d''Arch : **core** (le système de base), **extra** (tout le reste), **multilib** (bibliothèques 32 bits, utiles pour Steam), plus le dépôt **omarchy** (pkgs.omarchy.org) qui fournit Omarchy lui-même. L''**AUR** ne sert qu''en option.'
- q: Pourquoi `sudo pacman -Syu` est-il bloqué sous Omarchy ?
  a: Une **garde ALPM** (un crochet de pacman) l'intercepte et renvoie vers **`omarchy update`**, qui prend un **snapshot** avant, suit le canal choisi et lance les étapes de migration d'Omarchy. Une mise à jour faite « à côté » sauterait ces protections.
- q: Qu'est-ce que l'AUR, et quel est son risque ?
  a: 'L''**Arch User Repository** : des recettes de construction (**PKGBUILD**) écrites par des utilisateurs, **non vérifiées** par Arch. Le manuel Omarchy le compare à npm : immense et pratique, mais n''importe qui peut publier. Lis le PKGBUILD et vérifie la popularité et la date avant d''installer.'
- q: Pourquoi ne jamais faire `pacman -Sy paquet` ?
  a: 'C''est une **mise à jour partielle** : tu rafraîchis la liste des paquets sans mettre à jour le système, puis tu installes un paquet compilé pour des bibliothèques plus récentes que les tiennes. Résultat possible : des programmes qui ne démarrent plus. Sous Arch, on met tout à jour d''un bloc, ou rien.'
- q: Comment installer et supprimer proprement un logiciel dans Omarchy ?
  a: '**`omarchy pkg add <paquet>`** (ou *Install > Package* dans le menu) et **`omarchy pkg drop <paquet>`** (ou *Remove > Package*). Pour une appli préinstallée, *Remove > Preinstalls* retire aussi les raccourcis associés.'
- q: Quelles commandes pacman servent à enquêter ?
  a: '`pacman -Ss mot` cherche dans les dépôts, `pacman -Qi paquet` décrit un paquet installé, `pacman -Ql paquet` liste ses fichiers, `pacman -Qo /chemin/fichier` dit quel paquet possède un fichier, `pacman -Qe` liste ce que tu as installé explicitement, `pacman -Qdtq` les dépendances orphelines.'
quiz:
- q: Tu veux installer htop. Quelle méthode est la plus « Omarchy » ?
  options:
  - Télécharger un .exe
  - '`omarchy pkg add htop` (ou Install > Package)'
  - Compiler depuis les sources
  - '`sudo pacman -Sy htop`'
  answer: 1
  explain: La commande omarchy passe par pacman avec les bonnes options. `pacman -Sy paquet` est une mise à jour partielle à éviter.
- q: Un logiciel n'existe que dans l'AUR, avec 3 votes et une dernière mise à jour il y a quatre ans. Que fais-tu ?
  options:
  - Tu l'installes sans regarder
  - Tu lis le PKGBUILD, tu cherches une alternative dans les dépôts officiels ou en Flatpak, et tu installes en connaissance de cause
  - Tu désactives le pare-feu
  - Tu réinstalles Omarchy
  answer: 1
  explain: Un paquet AUR peu suivi peut être cassé, obsolète ou malveillant. Le PKGBUILD montre exactement ce qui sera téléchargé et exécuté.
- q: Tu tapes `sudo pacman -Syu` par habitude et un message te renvoie ailleurs. Pourquoi ?
  options:
  - pacman est cassé
  - La garde d'Omarchy impose `omarchy update`, qui prend un snapshot et applique les migrations
  - Il manque les droits root
  - Le dépôt est hors ligne
  answer: 1
  explain: 'C''est voulu : la mise à jour officielle protège le système (snapshot, canal, migrations).'
- q: Une commande `foo` est présente mais tu ne sais pas d'où elle vient. Comment le savoir ?
  options:
  - '`pacman -Qo $(which foo)`'
  - '`pacman -Ss foo`'
  - '`omarchy update`'
  - '`rm $(which foo)`'
  answer: 0
  explain: '`pacman -Qo` indique le paquet propriétaire d''un fichier ; `which` donne le chemin de la commande.'
---

Tu n'avais jamais utilisé Arch : cette fiche explique ce qui le rend différent d'Ubuntu ou de Windows, comment fonctionne son gestionnaire de paquets **pacman**, ce qu'est l'**AUR**, et ce qu'Omarchy change à ces habitudes. C'est la base pour installer des logiciels sans abîmer le système.

> **Les outils cités dans cette fiche.**
> - **Arch Linux** : la distribution sous Omarchy, minimaliste et en mise à jour continue.
> - **paquet** : une archive qui contient un logiciel, ses fichiers et la liste de ses dépendances.
> - **dépôt** : un serveur qui héberge des paquets vérifiés, signés par leurs mainteneurs.
> - **pacman** : le gestionnaire de paquets d'Arch ; il installe, met à jour et supprime en gérant les dépendances.
> - **ALPM** : la bibliothèque sur laquelle repose pacman ; ses *hooks* (crochets) exécutent des actions avant ou après une opération.
> - **AUR** (Arch User Repository) : un catalogue communautaire de recettes de construction, non vérifié par Arch.
> - **PKGBUILD** : le script qui décrit comment télécharger, compiler et empaqueter un logiciel de l'AUR.
> - **yay** : un assistant AUR qui télécharge les PKGBUILD, construit les paquets et les installe avec pacman.
> - **Flatpak** : un format d'applications isolées, indépendant de la distribution.
> - **wiki Arch** : la documentation communautaire d'Arch (wiki.archlinux.org), référence pour tout Linux.

## Comprendre : la mise à jour continue

Ubuntu sort une version tous les six mois et fige les logiciels entre deux versions. Windows fait de même avec ses mises à jour de fonctionnalités. **Arch** fonctionne en **rolling release** : dès qu'une nouvelle version d'un logiciel est prête et testée, elle arrive dans les dépôts.

| | Ubuntu, Windows | Arch (et Omarchy) |
| --- | --- | --- |
| Versions | majeures, tous les 6 mois à 2 ans | aucune, flux continu |
| Logiciels | figés, parfois anciens | récents |
| Mises à jour | petites, puis une grosse migration | régulières, jamais de grosse migration |
| Ce qu'on attend de toi | presque rien | mettre à jour **souvent et en entier** |

La contrepartie de logiciels récents : une mise à jour peut parfois casser quelque chose. Omarchy l'encadre avec des canaux et des snapshots (fiche 7).

Une règle s'en déduit, la plus importante d'Arch : **pas de mise à jour partielle**. Tous les paquets sont construits pour fonctionner avec les versions actuelles des autres. Mettre à jour un seul paquet, ou installer un paquet récent sur un système ancien, peut casser des dépendances.

## Les dépôts

| Dépôt | Contenu |
| --- | --- |
| **core** | le strict nécessaire : noyau, outils de base, pacman |
| **extra** | presque tout le reste : bureaux, applications, langages |
| **multilib** | bibliothèques 32 bits (Steam, Wine) |
| **omarchy** | Omarchy lui-même : scripts, shell, thèmes, configurations par défaut |
| **AUR** | communautaire, hors dépôts officiels, en option |

Le manuel d'Omarchy précise que le système n'utilise que les dépôts officiels et le sien ; l'AUR n'intervient que pour des options que tu choisis.

## Installer et supprimer avec Omarchy

| Action | Menu | Commande |
| --- | --- | --- |
| Installer un paquet officiel | *Install > Package* | `omarchy pkg add <paquet>` |
| Installer depuis l'AUR | *Install > AUR* | via yay |
| Supprimer un paquet | *Remove > Package* | `omarchy pkg drop <paquet>` |
| Retirer une appli préinstallée | *Remove > Preinstalls* | — |

Les entrées *Install* du menu proposent une recherche avec aperçu : pratique pour découvrir ce qui existe. *Remove > Preinstalls* retire aussi les raccourcis liés à l'appli.

## pacman pour enquêter

Même si Omarchy installe pour toi, pacman reste l'outil pour comprendre ce qu'il y a sur le système :

| Question | Commande |
| --- | --- |
| Ce paquet existe-t-il ? | `pacman -Ss docker` |
| Que contient ce paquet installé ? | `pacman -Qi docker` (description, version, dépendances, taille) |
| Quels fichiers a-t-il posés ? | `pacman -Ql docker` |
| À quel paquet appartient ce fichier ? | `pacman -Qo /usr/bin/docker` |
| Qu'ai-je installé moi-même ? | `pacman -Qe` |
| Quelles dépendances ne servent plus ? | `pacman -Qdtq` |
| Supprimer un paquet et ses dépendances inutiles | `sudo pacman -Rns paquet` |

Les lettres se lisent ainsi : **S** = *sync* (les dépôts), **Q** = *query* (le système local), **R** = *remove*. Puis `s` = chercher, `i` = infos, `l` = liste des fichiers, `o` = propriétaire.

## Pourquoi `pacman -Syu` est bloqué

Sur Arch « nu », on met à jour avec `sudo pacman -Syu`. Sous Omarchy, cette commande (et `yay -Syu`) est **interceptée** par une garde ALPM qui te renvoie vers **`omarchy update`**. Ce n'est pas une contrainte gratuite : la mise à jour d'Omarchy

1. prend un **snapshot** du système avant de toucher à quoi que ce soit ;
2. respecte le **canal** que tu as choisi (stable, rc, edge, dev) ;
3. applique les **migrations** d'Omarchy (changements de configuration entre versions).

Tout est détaillé dans la fiche suivante.

## L'AUR sans se brûler

L'AUR contient des dizaines de milliers de recettes : pilotes rares, logiciels propriétaires, outils de niche. Mais **personne ne les vérifie** : un PKGBUILD peut télécharger n'importe quoi et l'exécuter pendant la construction. Le manuel Omarchy fait la comparaison avec npm.

Avant d'installer un paquet AUR :

1. **cherche d'abord** dans les dépôts officiels (`pacman -Ss`), puis en Flatpak ;
2. regarde sur aur.archlinux.org les **votes**, la **popularité**, la **date** de dernière mise à jour et les **commentaires** ;
3. **lis le PKGBUILD** : d'où vient la source (le site officiel du projet ?), quelles commandes sont exécutées ;
4. préfère les variantes `-bin` officielles (binaire publié par l'éditeur) à une recompilation longue, quand l'éditeur est fiable.

## Le wiki Arch, ton meilleur ami

Le **wiki Arch** est la meilleure documentation Linux qui existe, et elle s'applique à Omarchy pour tout ce qui touche au système : pilotes, services, matériel, réseau. Deux nuances seulement : la mise à jour passe par `omarchy update`, et la configuration de Hyprland suit la structure d'Omarchy (fiche 8).

> **À retenir.** Arch se met à jour en continu : souvent et en entier, jamais de mise à jour partielle (`pacman -Sy paquet` interdit). Sous Omarchy, installe avec `omarchy pkg add`, supprime avec `omarchy pkg drop`, mets à jour avec `omarchy update`. pacman reste l'outil d'enquête (`-Ss`, `-Qi`, `-Ql`, `-Qo`), et l'AUR un dernier recours, PKGBUILD lu.
