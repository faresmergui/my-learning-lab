---
title: Ce qu'est Omarchy, couche par couche
chapter: 1
order: 1
duration: 12
level: Débutant
tags:
- Omarchy
- Arch Linux
- Wayland
- Hyprland
- Quickshell
cards:
- q: Qu'est-ce qu'Omarchy, en une phrase ?
  a: 'Une **configuration complète et opinionnée** posée sur **Arch Linux**, créée par DHH : Hyprland comme gestionnaire de fenêtres, un shell graphique maison, des thèmes, des raccourcis et des outils déjà réglés. Ce n''est pas un nouveau noyau ni un nouveau système : c''est Arch, très bien préparé.'
- q: Quelles sont les couches d'Omarchy, de bas en haut ?
  a: Le **noyau Linux** (linux-omarchy), **Arch Linux** (paquets, pacman, systemd), **Wayland** (le protocole d'affichage), **Hyprland** (le compositeur qui place et dessine les fenêtres), le **shell Quickshell** (barre, lanceur, menus, notifications, verrouillage), puis **tes applications** et tes réglages.
- q: Quelle différence entre un environnement de bureau et un gestionnaire de fenêtres en mosaïque ?
  a: Un **environnement de bureau** (GNOME, KDE, Windows) fournit tout, avec des fenêtres flottantes qu'on déplace à la souris. Un **gestionnaire en mosaïque** comme Hyprland **range automatiquement** les fenêtres côte à côte sans chevauchement, et tout se pilote au clavier. Omarchy ajoute autour le reste du bureau.
- q: Qu'a changé Omarchy 4 « Quattro » (août 2026) ?
  a: Un **shell unique en Quickshell** remplace Waybar, Walker, Mako, SwayOSD, hyprlock et hypridle ; la configuration de Hyprland passe en **Lua** (`~/.config/hypr/*.lua`) ; **foot** devient le terminal par défaut ; Omarchy est distribué sous forme de **paquets Arch**.
- q: Pourquoi dit-on qu'Omarchy est « opinionné » ?
  a: 'Les choix sont faits pour toi (terminal, éditeur, navigateur, thèmes, raccourcis). L''idée : un poste prêt à travailler dès l''installation, que tu modifies ensuite. Tu peux tout changer, mais il vaut mieux comprendre les choix avant de les défaire.'
- q: Qu'est-ce que Wayland, et qu'est-ce qu'il remplace ?
  a: 'Le **protocole d''affichage moderne** de Linux : il définit comment les applications envoient leurs images au compositeur. Il remplace **X11** (Xorg), vieux de près de 40 ans. Les applications X11 tournent encore grâce à **XWayland**, une couche de compatibilité.'
- q: Où trouver de l'aide intégrée dans Omarchy ?
  a: '**Super+K** affiche tous les raccourcis, **Super+Espace** ouvre le menu Omarchy, la commande **`omarchy`** sans argument liste les commandes (et `--help` partout), et le manuel officiel est sur **omarchy.org/manual**.'
quiz:
- q: 'Un collègue te dit : « Omarchy, c''est une distribution à part, donc les tutos Arch ne marchent pas ». Qu''en penses-tu ?'
  options:
  - Il a raison, Omarchy a ses propres paquets incompatibles
  - 'C''est faux : Omarchy est Arch ; le wiki Arch s''applique, en passant par les commandes Omarchy pour les mises à jour'
  - Il faut utiliser les tutos Ubuntu
  - Seuls les tutos Fedora fonctionnent
  answer: 1
  explain: Omarchy ajoute un dépôt de paquets et une configuration au-dessus d'Arch. Le wiki Arch reste la référence pour le système, avec quelques règles Omarchy (mises à jour via `omarchy update`).
- q: Une ancienne appli ne connaît que X11. Va-t-elle s'afficher sous Omarchy ?
  options:
  - Non, Wayland refuse les applis X11
  - Oui, via XWayland, une couche de compatibilité
  - Seulement en mode console
  - Il faut réinstaller Omarchy en X11
  answer: 1
  explain: XWayland fait tourner les applications X11 dans une session Wayland. Quelques cas (partage d'écran, mise à l'échelle) peuvent être moins nets.
- q: Tu lis un tuto de 2025 qui modifie `~/.config/hypr/hyprland.conf` et Waybar. Que faut-il en conclure ?
  options:
  - Il s'applique tel quel
  - 'Il date d''avant Omarchy 4 : la config Hyprland est maintenant en Lua et Waybar a été remplacé par le shell Quickshell'
  - Il faut réinstaller Waybar
  - Il concerne macOS
  answer: 1
  explain: Depuis la version 4, les fichiers sont `~/.config/hypr/*.lua` et la barre se règle dans `~/.config/omarchy/shell.json`. Vérifie toujours la date d'un tuto Omarchy.
- q: Quel composant décide où se place une nouvelle fenêtre ?
  options:
  - Le noyau Linux
  - pacman
  - Hyprland, le compositeur
  - Le navigateur
  answer: 2
  explain: Sous Wayland, le compositeur (ici Hyprland) reçoit les images des applications, les place, les dessine et gère clavier et souris.
---

**Omarchy** est une configuration de poste de travail Linux créée par **DHH** (David Heinemeier Hansson, le créateur de Ruby on Rails et cofondateur de 37signals). Elle part d'**Arch Linux** et y ajoute un bureau en mosaïque piloté au clavier, des thèmes, des raccourcis et une sélection d'outils, le tout réglé pour être utilisable dès l'installation. Cette fiche donne le modèle mental : quelles couches empilent Omarchy, et à quoi sert chacune. Elle s'appuie sur le manuel officiel (omarchy.org/manual) à jour en octobre 2026, version 4.0.6.

> **Les outils cités dans cette fiche.**
> - **Arch Linux** : une distribution Linux minimaliste en *rolling release* (mise à jour en continu, sans versions majeures), connue pour son wiki très complet.
> - **noyau Linux** (kernel) : le cœur du système, qui parle au matériel (processeur, mémoire, disques, carte graphique).
> - **pacman** : le gestionnaire de paquets d'Arch, qui installe, met à jour et supprime les logiciels.
> - **systemd** : le programme qui démarre le système et gère les services en arrière-plan (réseau, son, Bluetooth).
> - **Wayland** : le protocole d'affichage moderne de Linux, successeur de **X11** (Xorg).
> - **XWayland** : une couche de compatibilité qui fait tourner les anciennes applications X11 sous Wayland.
> - **compositeur** : sous Wayland, le programme qui reçoit l'image de chaque application, les assemble à l'écran et distribue clavier et souris.
> - **Hyprland** : le compositeur en mosaïque (tiling) utilisé par Omarchy, connu pour ses animations et sa configurabilité.
> - **Quickshell** : une boîte à outils pour écrire des barres, menus et panneaux en **QML** (le langage d'interface de Qt) ; Omarchy 4 construit tout son shell avec.
> - **Lua** : un petit langage de script, simple à lire, dans lequel s'écrit la configuration de Hyprland depuis Omarchy 4.
> - **foot** : un terminal léger pour Wayland, terminal par défaut d'Omarchy 4.
> - **Neovim** : un éditeur de texte au clavier, livré dans Omarchy avec la configuration **LazyVim**.

## Comprendre : un bureau en couches

Sous Windows, le bureau, le système et les pilotes forment un bloc. Sous Linux, ce sont des pièces séparées qu'on assemble. Omarchy est précisément cet assemblage, fait pour toi.

<!-- schema:couches -->
<figure class="diagram"><svg viewBox="0 0 680 352" role="img" aria-label="Les couches d&#x27;Omarchy" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-ok dg-pop" style="--d:6"><rect x="120.0" y="14" width="440" height="38" rx="8"/></g><text x="340.0" y="30.0" class="dg-t" text-anchor="middle" style="--d:6">tes applications</text><text x="340.0" y="48.0" class="dg-s" text-anchor="middle" style="--d:6">foot, Neovim, Chromium, btop…</text><g class="dg-box dg-pop" style="--d:5"><rect x="105.0" y="58" width="470" height="38" rx="8"/></g><text x="340.0" y="74.0" class="dg-t" text-anchor="middle" style="--d:5">thèmes</text><text x="340.0" y="92.0" class="dg-s" text-anchor="middle" style="--d:5">une palette appliquée partout</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="90.0" y="102" width="500" height="38" rx="8"/></g><text x="340.0" y="118.0" class="dg-t" text-anchor="middle" style="--d:4">shell Quickshell</text><text x="340.0" y="136.0" class="dg-s" text-anchor="middle" style="--d:4">barre, lanceur, menus, notifications, verrouillage</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="75.0" y="146" width="530" height="38" rx="8"/></g><text x="340.0" y="162.0" class="dg-t" text-anchor="middle" style="--d:3">Hyprland</text><text x="340.0" y="180.0" class="dg-s" text-anchor="middle" style="--d:3">compositeur en mosaïque : place et dessine les fenêtres</text><g class="dg-box dg-pop" style="--d:2"><rect x="60.0" y="190" width="560" height="38" rx="8"/></g><text x="340.0" y="206.0" class="dg-t" text-anchor="middle" style="--d:2">Wayland (+ XWayland)</text><text x="340.0" y="224.0" class="dg-s" text-anchor="middle" style="--d:2">protocole d&#x27;affichage</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="45.0" y="234" width="590" height="38" rx="8"/></g><text x="340.0" y="250.0" class="dg-t" text-anchor="middle" style="--d:1">Arch Linux</text><text x="340.0" y="268.0" class="dg-s" text-anchor="middle" style="--d:1">pacman, systemd, dépôts</text><g class="dg-box dg-ghost dg-pop" style="--d:0"><rect x="30.0" y="278" width="620" height="38" rx="8"/></g><text x="340.0" y="294.0" class="dg-t" text-anchor="middle" style="--d:0">noyau linux-omarchy</text><text x="340.0" y="312.0" class="dg-s" text-anchor="middle" style="--d:0">pilotes, mémoire, processus</text><text x="14" y="342" class="dg-s" text-anchor="start">chaque couche ne parle qu&#x27;à ses voisines : une panne appartient à une couche</text></svg><figcaption>Omarchy, c&#x27;est Arch Linux plus des choix tout faits pour chaque couche au-dessus.</figcaption></figure>
<!-- /schema:couches -->

| Couche | Composant dans Omarchy | Ce qu'elle fait | Quand tu y touches |
| --- | --- | --- | --- |
| Noyau | `linux-omarchy` | pilotes, mémoire, processus | rarement (choix du noyau, fiche 7) |
| Système | Arch Linux, pacman, systemd | paquets, services, démarrage | installer des logiciels (fiche 6) |
| Affichage | Wayland (+ XWayland) | le protocole entre applis et écran | jamais directement |
| Fenêtres | Hyprland | place, dessine, anime les fenêtres ; raccourcis | souvent (fiches 3, 4, 12) |
| Shell | Quickshell (QML) | barre, lanceur, menus, notifications, verrouillage | pour personnaliser (fiche 14) |
| Style | thèmes Omarchy | couleurs, polices, fonds d'écran partout | pour personnaliser (fiche 13) |
| Applis | foot, Neovim, Chromium, etc. | ton travail | tous les jours |

Le point important : quand quelque chose ne va pas, demande-toi **à quelle couche** appartient le problème. Un raccourci qui ne marche pas, c'est Hyprland. Un widget de barre absent, c'est le shell. Un logiciel introuvable, c'est pacman. Le Wi-Fi qui tombe, c'est le système ou le noyau.

## Mosaïque contre fenêtres flottantes

Sous Windows, chaque fenêtre flotte : tu la déplaces et la redimensionnes à la souris, et elles se chevauchent. Hyprland fait l'inverse : chaque nouvelle fenêtre **prend une place** dans une grille, les autres se poussent pour lui faire de la place, et rien ne se chevauche. Tu passes de l'une à l'autre au clavier.

Les avantages se voient vite : pas de temps perdu à arranger les fenêtres, tout l'écran utilisé, et des **espaces de travail** (bureaux virtuels) numérotés où tu ranges tes activités (navigateur sur le 1, terminal sur le 2, etc.). Le prix à payer, c'est l'apprentissage des raccourcis, d'où **Super+K** qui les affiche à tout moment. La touche **Super** est la touche Windows de ton clavier.

## Ce qu'Omarchy ajoute à Arch

Installer Arch « nu » donne un terminal noir et rien d'autre : tout est à choisir et configurer. Omarchy fait ces choix :

- **le bureau** : Hyprland, plus le shell Quickshell (barre en haut, menu, notifications, écran de verrouillage) ;
- **les applications** : foot (terminal), Neovim avec LazyVim, Chromium, un gestionnaire de fichiers, un moniteur d'activité (btop), etc. ;
- **les thèmes** : une palette appliquée d'un coup au terminal, à l'éditeur, à la barre, au navigateur ;
- **les outils** : la commande `omarchy`, des mises à jour avec **snapshots** (photos du système pour revenir en arrière), un pare-feu, le chiffrement du disque ;
- **les raccourcis** : une logique cohérente autour de Super.

Depuis la version 4, tout cela arrive sous forme de **paquets Arch** depuis un dépôt Omarchy. Conséquence pratique : Omarchy se met à jour comme le reste du système, avec sa propre commande (fiche 7).

## Omarchy 4 : ce qui a changé

Si tu lis des tutoriels ou des vidéos, regarde leur date. La version 4.0 « Quattro » (août 2026) a beaucoup changé :

| Avant (v3) | Depuis la v4 |
| --- | --- |
| Waybar (barre), Walker (lanceur), Mako (notifications), hyprlock, hypridle | un seul **shell Quickshell** qui fait tout |
| `~/.config/hypr/hyprland.conf` et ses `.conf` | `~/.config/hypr/*.lua` (`bindings.lua`, `monitors.lua`, `input.lua`, `looknfeel.lua`, `autostart.lua`) |
| Alacritty par défaut | **foot** par défaut (Alacritty, Ghostty, Kitty restent possibles) |
| Omarchy cloné avec git | Omarchy installé en **paquets** |

Un tuto qui parle de `waybar/config` ou de `hyprland.conf` décrit l'ancienne version : l'idée est souvent juste, mais les fichiers ne sont plus les mêmes.

## Se repérer dès le premier jour

| Besoin | Raccourci ou commande |
| --- | --- |
| Voir tous les raccourcis | **Super+K** |
| Menu Omarchy (installer, réglages, mises à jour) | **Super+Espace** |
| Ouvrir un terminal | **Super+Entrée** |
| Ouvrir le navigateur | **Super+Shift+Entrée** |
| Fermer une fenêtre | **Super+W** |
| Toutes les commandes en ligne | `omarchy`, puis `omarchy <groupe> --help` |

Le menu **Super+Espace** est ton point d'entrée pour presque tout : *Install* (logiciels, polices, thèmes), *Setup* (écrans, clavier, réseau), *Update* (mises à jour, matériel), *Remove*, *Appearance*. Les fiches suivantes y font souvent référence.

> **À retenir.** Omarchy, c'est Arch Linux plus des choix tout faits : Hyprland range les fenêtres en mosaïque, le shell Quickshell fournit barre et menus, et la commande `omarchy` gère le reste. Pense en couches pour savoir où chercher, retiens Super+K et Super+Espace, et méfie-toi des tutos d'avant la version 4.
