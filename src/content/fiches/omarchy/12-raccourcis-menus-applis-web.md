---
title: Tes raccourcis, ton menu, tes applis web
chapter: 12
order: 1
duration: 13
level: Avancé
tags:
- bindings.lua
- raccourcis
- applis web
- menu Omarchy
- autostart
- règles de fenêtres
cards:
- q: Comment remplacer l'appli lancée par un raccourci existant ?
  a: 'Dans `~/.config/hypr/bindings.lua`, avec **`o.rebind`** : `o.rebind("SUPER + SHIFT + O", "Joplin", "joplin-desktop")` remplace Obsidian par Joplin sur Super+Shift+O. Les trois arguments : la combinaison, la description affichée dans Super+K, la commande.'
- q: Quelle différence entre `o.bind`, `o.rebind` et `hl.unbind` ?
  a: '**`o.bind`** ajoute un raccourci sur une combinaison libre, **`o.rebind`** remplace ce que fait une combinaison déjà utilisée par Omarchy, **`hl.unbind`** supprime un raccourci. Vérifie avec Super+K qu''une combinaison est libre avant `o.bind`.'
- q: Qu'est-ce qu'une appli web dans Omarchy ?
  a: 'Un site ouvert dans sa **propre fenêtre**, sans barre d''adresse, avec son icône et éventuellement un raccourci : il se comporte comme une appli. *Install > Web App* (nom, adresse, icône) l''ajoute ; *Remove > Web App* la retire.'
- q: Comment ajouter une entrée à ton menu Omarchy ?
  a: 'Dans `~/.config/omarchy/extensions/omarchy-menu.jsonc`, avec des identifiants à points : `"personal"` crée une entrée à la racine, `"personal.notes"` une sous-entrée, avec `icon`, `label` et `action` (la commande lancée).'
- q: Comment lancer un programme à chaque ouverture de session ?
  a: 'Dans `~/.config/hypr/autostart.lua` : `o.launch_on_start("mon-programme")`. Exemple du manuel : `o.launch_on_start("hyprsunset")` pour le filtre de lumière bleue.'
- q: Qu'est-ce qu'une règle de fenêtre ?
  a: Un réglage appliqué automatiquement aux fenêtres dont le nom correspond à un motif. Le manuel donne `o.window("(Alacritty|kitty|foot)", { scroll_touchpad = 1.5 })` pour défiler plus vite dans les terminaux. On s'en sert aussi pour forcer une appli en flottant ou sur un espace précis.
- q: Comment trouver le nom (classe) d'une fenêtre pour une règle ?
  a: '`hyprctl clients` liste les fenêtres ouvertes avec leur **class** et leur **title**. C''est la classe qu''on met dans le motif d''une règle.'
quiz:
- q: Tu utilises Notion à la place d'Obsidian et veux le garder sur Super+Shift+O. Que fais-tu ?
  options:
  - Tu modifies le fichier de raccourcis dans /usr/share/omarchy
  - Tu installes Notion en appli web puis `o.rebind` sur SUPER + SHIFT + O dans ton bindings.lua
  - Tu supprimes Obsidian et rien d'autre
  - Ce n'est pas possible
  answer: 1
  explain: o.rebind remplace l'action d'une combinaison existante dans ton propre fichier, qui survit aux mises à jour.
- q: Tu ajoutes `o.bind` sur Super+Shift+A et rien ne se passe comme prévu. Pourquoi, probablement ?
  options:
  - 'La combinaison est déjà prise (ChatGPT par défaut) : il fallait o.rebind, ou une combinaison libre'
  - Lua est mal installé
  - Il faut redémarrer le PC
  - Le thème bloque le raccourci
  answer: 0
  explain: Super+Shift+A ouvre ChatGPT par défaut. Super+K montre les combinaisons utilisées.
- q: Tu veux que ta messagerie Discord s'ouvre comme une appli, avec son icône, sans onglets de navigateur. Le plus simple ?
  options:
  - Install > Web App
  - Compiler Discord depuis les sources
  - Un paquet AUR non maintenu
  - Un raccourci vers le navigateur
  answer: 0
  explain: Discord fait partie des applis web proposées ; une appli web a sa fenêtre, son icône et peut recevoir un raccourci.
- q: Tu veux qu'une calculatrice s'ouvre toujours en flottant. Par où commences-tu ?
  options:
  - '`hyprctl clients` pour lire sa classe, puis une règle `o.window` sur cette classe'
  - Changer la disposition de tous les espaces
  - Modifier le code de la calculatrice
  - Super+T à chaque fois, pas d'autre choix
  answer: 0
  explain: Une règle de fenêtre s'applique automatiquement à chaque ouverture ; il faut seulement connaître la classe de la fenêtre.
---

Les raccourcis d'Omarchy sont un point de départ. L'objectif de cette étape : un poste où **tes** applications sont à une touche, où le menu contient **tes** actions, et où les programmes dont tu as besoin se lancent seuls. Tout se fait dans tes fichiers, jamais dans ceux d'Omarchy. Les exemples marqués « manuel » sont repris du manuel Omarchy 4 ; vérifie toujours la forme exacte dans les exemples commentés de tes propres fichiers, car la configuration Lua est récente et peut évoluer.

> **Les outils cités dans cette fiche.**
> - **bindings.lua** : ton fichier de raccourcis clavier, dans `~/.config/hypr/`.
> - **`o.`** et **`hl.`** : les deux familles de fonctions de la configuration Lua ; `o.` pour les aides d'Omarchy, `hl.` pour les fonctions de Hyprland.
> - **appli web** : un site ouvert dans sa propre fenêtre, sans barre d'adresse, avec son icône.
> - **favicon** : la petite icône d'un site web.
> - **JSONC** : du JSON avec commentaires, format du fichier d'extensions du menu.
> - **classe de fenêtre** (class) : l'identifiant qu'une application donne à ses fenêtres, utilisé par les règles.
> - **hyprsunset** : un petit outil qui réchauffe les couleurs de l'écran le soir (filtre de lumière bleue).

## Comprendre : trois verbes pour les raccourcis

| Fonction | Rôle | Quand |
| --- | --- | --- |
| **`o.bind`** | ajouter un raccourci | la combinaison est libre |
| **`o.rebind`** | remplacer l'action d'une combinaison d'Omarchy | tu veux une autre appli sur une touche existante |
| **`hl.unbind`** | supprimer un raccourci | une combinaison te gêne (jeu, appli qui l'utilise) |

Avant d'ajouter, ouvre **Super+K** : la liste montre les combinaisons prises, et tes propres raccourcis y apparaissent avec la description que tu leur donnes.

## Remplacer et ajouter

Exemple du manuel : remplacer Obsidian par Joplin sur Super+Shift+O (après `omarchy pkg add joplin-bin`) :

```lua
-- ~/.config/hypr/bindings.lua
o.rebind("SUPER + SHIFT + O", "Joplin", "joplin-desktop")
```

Les trois arguments : la **combinaison**, la **description** (affichée dans Super+K), la **commande** à lancer. `o.bind` prend la même forme pour une combinaison libre :

```lua
o.bind("SUPER + CTRL + ALT + J", "Journal", "foot -e nvim ~/notes/journal.md")
```

Quelques idées pour un DevOps : un terminal directement sur un serveur (`foot -e ssh bastion`), k9s (le tableau de bord Kubernetes en terminal), ou ton dossier de notes dans Neovim.

## Les applis web

Omarchy installe certains services comme des **applis web** : un site dans sa propre fenêtre Chromium, sans barre d'adresse, avec son icône. Elles se lancent et se rangent comme des applis normales, et peuvent avoir un raccourci.

| Action | Moyen |
| --- | --- |
| Ajouter | *Install > Web App* : nom, adresse, et une icône si le favicon du site ne convient pas (dashboardicons.com en propose beaucoup) |
| Retirer | *Remove > Web App* (retire aussi son raccourci) |
| Copier l'adresse de la page affichée | **Shift+Alt+L** dans l'appli web |

Raccourcis par défaut (manuel) :

| Raccourci | Appli web |
| --- | --- |
| **Super+Shift+A** | ChatGPT |
| **Super+Shift+Alt+A** | Grok |
| **Super+Shift+Y** | YouTube |
| **Super+Shift+X** | X |
| **Super+Shift+Alt+G** | WhatsApp |
| **Super+Shift+P** | Google Photos |
| **Super+Shift+S** | Google Maps |
| **Super+Shift+E** / **Super+Shift+C** | HEY (mail / agenda) |

Ceux qui ne te servent pas sont autant de combinaisons à récupérer avec `o.rebind`. Par exemple, Super+Shift+A peut ouvrir Claude au lieu de ChatGPT.

## Ton propre menu

Le menu Super+Espace accepte tes entrées, dans `~/.config/omarchy/extensions/omarchy-menu.jsonc`. Les identifiants à **points** dessinent l'arborescence (manuel) :

```jsonc
"personal": {"icon":"","label":"Personal"},
"personal.notes": {"icon":"󰎞","label":"Notes","action":"omarchy-launch-editor ~/notes"},
```

`personal` apparaît à la racine du menu, `personal.notes` dedans. Les icônes sont des glyphes de la police Nerd Font. Tu peux ainsi regrouper tes actions : ouvrir un projet, te connecter à un serveur, lancer un script de sauvegarde des dotfiles.

## Lancer au démarrage

`~/.config/hypr/autostart.lua` lance des programmes à chaque ouverture de session (manuel) :

```lua
o.launch_on_start("hyprsunset")    -- filtre de lumière bleue le soir
```

Idées : un client de synchronisation, un gestionnaire de mots de passe, Tailscale en interface. N'en mets pas trop : chaque programme ajoute du temps à l'ouverture de session.

## Les règles de fenêtres

Une **règle** applique un réglage aux fenêtres dont la classe correspond à un motif. L'exemple du manuel accélère le défilement dans les terminaux :

```lua
o.window("(Alacritty|kitty|foot)", { scroll_touchpad = 1.5 })
```

Le motif est une **expression régulière** sur la classe de la fenêtre. Pour connaître cette classe :

```bash
hyprctl clients | rg -i "class|title"
```

Usages courants : forcer en flottant une petite appli (calculatrice, sélecteur de couleur), envoyer toujours Discord sur l'espace 4, rendre une fenêtre légèrement transparente. Les propriétés disponibles sont celles des règles de fenêtres de Hyprland : regarde les exemples des défauts d'Omarchy dans `/usr/share/omarchy` (sans les modifier) et recopie la forme dans tes fichiers.

## Les jeux et les raccourcis

Certains jeux utilisent la touche Super ou des combinaisons qu'Omarchy capture. Deux solutions : passer le jeu en plein écran (**Super+F**) sur un espace dédié, ou libérer la combinaison avec `hl.unbind` sur la touche concernée.

> **À retenir.** `o.rebind` remplace l'action d'une touche d'Omarchy, `o.bind` en ajoute une libre, `hl.unbind` en supprime une ; Super+K montre ce qui est pris. Les applis web (Install > Web App) transforment un site en appli avec raccourci, ton menu s'étend dans `omarchy-menu.jsonc`, `autostart.lua` lance tes programmes, et `o.window` applique des règles aux fenêtres repérées avec `hyprctl clients`.
