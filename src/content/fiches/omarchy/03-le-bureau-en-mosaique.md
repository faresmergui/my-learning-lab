---
title: Le bureau en mosaïque au quotidien
chapter: 3
order: 1
duration: 12
level: Débutant
tags:
- Hyprland
- raccourcis
- espaces de travail
- presse-papiers
- captures
cards:
- q: Quelle est la logique générale des raccourcis Omarchy ?
  a: '**Super** (touche Windows) pour agir sur les fenêtres et lancer ; **Super+Shift** pour la variante « déplacer » ou une autre appli ; **Super+Ctrl** pour les panneaux et réglages ; **Super+Alt** pour les variantes secondaires. Super+K affiche la liste complète.'
- q: Comment changer d'espace de travail et y envoyer une fenêtre ?
  a: '**Super+2** va sur l''espace 2 de l''écran courant. **Super+Shift+2** y envoie la fenêtre active (et t''y emmène). **Super+Shift+Alt+2** l''y envoie **sans** changer d''espace. **Super+Tab** fait défiler les espaces de l''écran.'
- q: Comment se déplacer entre les fenêtres au clavier ?
  a: '**Super+flèches** déplace le focus vers la fenêtre dans cette direction. **Super+Shift+flèches** échange la fenêtre active avec sa voisine. La souris marche aussi : le focus suit le clic.'
- q: Pourquoi Super+C et Super+V plutôt que Ctrl+C et Ctrl+V ?
  a: Dans un terminal, **Ctrl+C** interrompt le programme en cours. Omarchy fournit **Super+C / Super+X / Super+V**, qui marchent pareil **partout**, terminal compris. **Super+Ctrl+V** ouvre l'historique du presse-papiers.
- q: Comment faire une capture d'écran ?
  a: '**Impr écran** pour une capture (zone ou fenêtre), **Super+Ctrl+C** pour le menu de capture, **Alt+Impr écran** pour enregistrer une vidéo, **Super+Impr écran** pour la pipette à couleurs. Les fichiers vont dans `~/Pictures/Screenshots`.'
- q: Comment verrouiller, éteindre ou redémarrer ?
  a: '**Super+Ctrl+L** verrouille. **Super+Échap** ouvre le menu Système (verrouiller, veille, redémarrer, éteindre). C''est la bonne façon d''éteindre, surtout avec un système sur disque externe.'
- q: Comment gérer les notifications ?
  a: '**Super+,** ferme la dernière, **Super+Shift+,** les ferme toutes, **Super+Ctrl+,** active le mode silencieux, **Super+Shift+Alt+,** ouvre l''historique.'
quiz:
- q: Tu veux copier une commande affichée dans le terminal et la coller dans le navigateur. Quel raccourci est sûr dans les deux ?
  options:
  - Ctrl+C puis Ctrl+V
  - Super+C puis Super+V
  - Alt+C puis Alt+V
  - Clic molette uniquement
  answer: 1
  explain: Ctrl+C interrompt le programme dans un terminal. Super+C / Super+V fonctionnent de la même manière dans toutes les applications.
- q: Tu travailles sur l'espace 1 et veux ranger le navigateur sur l'espace 3 sans quitter ton espace actuel. Raccourci ?
  options:
  - Super+3
  - Super+Shift+3
  - Super+Shift+Alt+3
  - Super+Tab
  answer: 2
  explain: Super+Shift+3 envoie la fenêtre et t'emmène avec elle ; avec Alt en plus, tu restes où tu es.
- q: Tu as oublié le raccourci pour ouvrir le gestionnaire de fichiers. Le plus rapide ?
  options:
  - Chercher sur Internet
  - Super+K, qui affiche tous les raccourcis
  - Redémarrer
  - Ouvrir les fichiers de configuration
  answer: 1
  explain: Super+K liste les raccourcis actifs, y compris ceux que tu as ajoutés. Pour info, c'est Super+Shift+F.
- q: Ton espace 2 contient déjà trois fenêtres et tu ouvres un terminal. Que fait Hyprland par défaut ?
  options:
  - Le terminal s'ouvre par-dessus les autres
  - Il découpe la place de la fenêtre active pour y mettre le terminal, sans chevauchement
  - Il ferme la plus ancienne
  - Il refuse d'en ouvrir une quatrième
  answer: 1
  explain: En disposition dwindle (par défaut), chaque nouvelle fenêtre partage l'espace de la fenêtre active. Toutes restent visibles.
---

Le premier choc en arrivant de Windows, c'est l'absence de barre des tâches et de fenêtres qu'on traîne à la souris. Hyprland range tout seul, et tu pilotes au clavier. Cette fiche donne les gestes de tous les jours, ceux qui doivent devenir des réflexes la première semaine. Tous viennent du manuel Omarchy 4 ; **Super+K** les rappelle à tout moment.

> **Les outils cités dans cette fiche.**
> - **Hyprland** : le compositeur en mosaïque qui place les fenêtres et gère les raccourcis.
> - **touche Super** : la touche Windows du clavier, base de presque tous les raccourcis.
> - **espace de travail** (workspace) : un bureau virtuel numéroté ; chaque écran a les siens.
> - **focus** : la fenêtre active, celle qui reçoit le clavier.
> - **menu Omarchy** : le menu central (Super+Espace) pour installer, régler, mettre à jour.
> - **dock** : une rangée d'icônes d'applis, présente sur les espaces en disposition flottante.

## Comprendre : penser en espaces, pas en fenêtres

Sous Windows, tu ouvres des fenêtres puis tu cherches la bonne dans la barre des tâches. Sous Hyprland, tu **ranges tes activités par espace** et tu sautes directement à l'espace voulu. Une organisation possible :

| Espace | Activité |
| --- | --- |
| 1 | navigateur |
| 2 | terminal et éditeur |
| 3 | documentation, notes |
| 4 | messagerie, musique |

Au bout de quelques jours, **Super+1**, **Super+2** deviennent aussi naturels qu'Alt+Tab, et beaucoup plus rapides : tu sais où est chaque chose, sans chercher. Les espaces sont **par écran** : avec deux écrans, chacun a ses espaces 1 à 10.

## Lancer et fermer

| Action | Raccourci |
| --- | --- |
| Menu Omarchy (tout faire) | **Super+Espace** |
| Grille des applications | **Super+Alt+Espace** (ou *Apps* dans le menu) |
| Terminal | **Super+Entrée** |
| Navigateur | **Super+Shift+Entrée** |
| Gestionnaire de fichiers | **Super+Shift+F** |
| Moniteur d'activité (btop) | **Super+Shift+T** |
| Fermer la fenêtre | **Super+W** (ou Super+Q) |
| Fermer toutes les fenêtres | **Ctrl+Alt+Suppr** |

Attention au dernier : sous Windows, Ctrl+Alt+Suppr ouvre un écran de sécurité ; sous Omarchy, il ferme tout.

## Naviguer entre les fenêtres

| Action | Raccourci |
| --- | --- |
| Focus vers la gauche, droite, haut, bas | **Super+flèches** |
| Échanger avec la fenêtre voisine | **Super+Shift+flèches** |
| Plein écran | **Super+F** |
| Pleine largeur (la barre reste visible) | **Super+Alt+F** |
| Passer une fenêtre en flottant / la remettre | **Super+T** |
| Déplacer à la souris | **Super + clic gauche** et glisser |
| Redimensionner à la souris | **Super + clic droit** et glisser |

## Les espaces de travail

| Action | Raccourci |
| --- | --- |
| Aller à l'espace 1 à 10 | **Super+1** … **Super+0** |
| Y envoyer la fenêtre (et suivre) | **Super+Shift+chiffre** |
| Y envoyer la fenêtre (sans suivre) | **Super+Shift+Alt+chiffre** |
| Faire défiler les espaces de l'écran | **Super+Tab** |

Clavier AZERTY : les chiffres demandent Shift (la touche « 1 » donne « & »). Omarchy lie ces raccourcis à la **position physique** des touches, donc Super + la touche « & / 1 » va bien sur l'espace 1, sans Shift. Si ce n'était pas le cas chez toi, la fiche 9 explique comment régler la disposition du clavier.

## Le presse-papiers

Dans un terminal, **Ctrl+C** n'a jamais voulu dire « copier » : il **interrompt** le programme en cours. Omarchy contourne le problème avec des raccourcis universels :

| Action | Raccourci |
| --- | --- |
| Copier | **Super+C** |
| Couper (hors terminal) | **Super+X** |
| Coller | **Super+V** |
| Historique du presse-papiers | **Super+Ctrl+V** |

Prends l'habitude de Super+C / Super+V partout : un seul geste, quelle que soit l'appli.

## Captures, couleurs et texte

| Action | Raccourci |
| --- | --- |
| Capture d'écran (zone, fenêtre, écran) | **Impr écran** |
| Menu de capture | **Super+Ctrl+C** |
| Enregistrement vidéo | **Alt+Impr écran** |
| Pipette à couleurs | **Super+Impr écran** |
| Extraire le texte d'une zone (OCR) | **Super+Ctrl+Impr écran** |
| Émojis | **Super+Ctrl+E** |

Les captures arrivent dans `~/Pictures/Screenshots`. L'extraction de texte est précieuse : une erreur affichée dans une image ou une vidéo devient du texte collable.

## Notifications, verrouillage, extinction

| Action | Raccourci |
| --- | --- |
| Fermer la dernière notification | **Super+,** |
| Les fermer toutes | **Super+Shift+,** |
| Mode silencieux | **Super+Ctrl+,** |
| Historique | **Super+Shift+Alt+,** |
| Verrouiller | **Super+Ctrl+L** |
| Menu Système (veille, redémarrer, éteindre) | **Super+Échap** |

## Le menu Omarchy

**Super+Espace** ouvre un menu qui se parcourt au clavier (flèches, Entrée, Échap) :

| Entrée | Contenu |
| --- | --- |
| **Apps** | la grille des applications |
| **Install** | paquets, AUR, applis web, polices, thèmes, services, jeux, IA |
| **Remove** | désinstaller paquets, applis web, applis préinstallées |
| **Setup** | écrans, clavier, réseau, sécurité, applis par défaut |
| **Appearance** | thème, police, fond d'écran |
| **Update** | mises à jour, matériel, configuration, mot de passe |
| **Trigger** | captures, bascules (toggles), tests de vitesse |

Tout ce que fait le menu existe aussi en ligne de commande (`omarchy …`, fiche 5) : le menu pour découvrir, la commande pour aller vite ou automatiser.

## Une méthode pour apprendre vite

1. La première semaine, n'apprends que **six raccourcis** : Super+Entrée, Super+Shift+Entrée, Super+W, Super+chiffre, Super+Shift+chiffre, Super+Espace.
2. Garde **Super+K** comme filet de sécurité, sans culpabiliser.
3. Chaque fois que tu prends la souris pour une action répétée, cherche son raccourci dans Super+K.
4. Au bout de deux semaines, ajoute les flèches, les captures et le presse-papiers.

> **À retenir.** Range tes activités par espace (Super+chiffre), lance au clavier (Super+Entrée, Super+Shift+Entrée), ferme avec Super+W, copie avec Super+C / Super+V pour que ça marche aussi dans le terminal. Super+Espace ouvre le menu de tout, Super+K rappelle tous les raccourcis, Super+Échap pour éteindre proprement.
