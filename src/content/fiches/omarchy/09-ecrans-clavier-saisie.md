---
title: Écrans, clavier AZERTY et saisie du japonais
chapter: 9
order: 1
duration: 13
level: Intermédiaire
tags:
- monitors.lua
- mise à l'échelle
- input.lua
- AZERTY
- touche compose
- Mozc
cards:
- q: Quelles valeurs d'échelle pour un écran 1080p ou 1440p ?
  a: 'Dans `~/.config/hypr/monitors.lua` : `omarchy_gdk_scale = 1` et `omarchy_monitor_scale = 1`. Omarchy part d''un écran haute densité (2x) : sur un écran de PC fixe classique, ces deux lignes évitent des applis énormes.'
- q: Et pour un écran 4K de 27 ou 32 pouces ?
  a: 'Le manuel recommande `omarchy_gdk_scale = 2` et `omarchy_monitor_scale = 1.6` (mise à l''échelle fractionnaire). Pour grossir seulement le texte : `omarchy display text size 14` (de 9 à 20).'
- q: Que règlent les deux variables d'échelle ?
  a: '`omarchy_monitor_scale` : l''échelle de l''écran dans Hyprland (taille de tout ce qui s''affiche). `omarchy_gdk_scale` : l''échelle des applis **GTK/XWayland** qui gèrent mal l''échelle fractionnaire. Les deux doivent être cohérentes avec la densité de l''écran.'
- q: Comment passer le clavier en AZERTY ?
  a: 'Dans `~/.config/hypr/input.lua` (*Setup > Input*), mets `kb_layout = "fr"` dans le bloc `input`. Pour deux dispositions : `kb_layout = "fr,us"` avec `grp:alts_toggle` dans `kb_options` (les deux Alt ensemble basculent). La barre affiche la disposition active.'
- q: Qu'est-ce que la touche compose, et laquelle est-ce dans Omarchy ?
  a: 'Une touche qui combine les suivantes pour taper un caractère spécial : compose, `''`, `e` donne é. Dans Omarchy, c''est **Shift+Verr. Maj** (`omarchy:shift_caps_compose`). Les combinaisons perso vont dans `~/.XCompose`, rechargé avec `omarchy-restart-xcompose`.'
- q: Comment écrire en japonais sous Omarchy ?
  a: '`omarchy setup input mozc` (ou *Setup > Typing > Input Methods*) installe **Mozc** via **fcitx5**. On bascule entre saisie latine et japonaise avec le raccourci de fcitx5 ; `omarchy font cjk jp` règle les polices pour que les kanji s''affichent dans leur forme japonaise.'
- q: Comment connaître le nom de ses écrans ?
  a: '`hyprctl monitors` liste les sorties (`DP-1`, `HDMI-A-1`…), leur résolution, fréquence et échelle. Ces noms servent dans `monitors.lua`. **Hyprmon**, un outil en terminal, permet aussi de placer les écrans visuellement.'
quiz:
- q: Sur ton écran 1440p de 27 pouces, toutes les applis paraissent deux fois trop grandes. Que changes-tu ?
  options:
  - Tu achètes un écran 4K
  - Tu mets `omarchy_gdk_scale = 1` et `omarchy_monitor_scale = 1` dans monitors.lua
  - Tu réinstalles Omarchy
  - Tu baisses la résolution
  answer: 1
  explain: Les réglages par défaut visent un écran 2x. À 1440p sur 27 pouces, l'échelle 1 est la bonne.
- q: Tu veux taper en AZERTY au quotidien mais garder le QWERTY pour certains raccourcis de code. Que mets-tu dans input.lua ?
  options:
  - '`kb_layout = "fr"`'
  - '`kb_layout = "fr,us"` et `grp:alts_toggle` dans kb_options'
  - Rien, c'est impossible
  - '`kb_layout = "jp"`'
  answer: 1
  explain: Deux dispositions séparées par une virgule, et une option de bascule (ici les deux Alt). La barre affiche celle qui est active.
- q: Tu révises tes kanji et veux taper 勉強 dans le navigateur. Que fais-tu ?
  options:
  - Copier-coller depuis Google
  - '`omarchy setup input mozc`, puis basculer en saisie japonaise avec fcitx5'
  - Installer Windows
  - Changer kb_layout en "jp"
  answer: 1
  explain: kb_layout change la disposition physique ; la conversion kana vers kanji demande un moteur de saisie comme Mozc.
- q: Tu veux taper « œ » ou « É » facilement sur un clavier AZERTY. Outil prévu ?
  options:
  - 'La touche compose : Shift+Verr. Maj puis la combinaison'
  - Une table de caractères Windows
  - Un script Python
  - Le scratchpad
  answer: 0
  explain: La touche compose enchaîne des touches (compose, o, e donne œ). `~/.XCompose` accepte tes propres combinaisons.
---

Omarchy est pensé au départ pour l'écran haute densité d'un portable et pour un clavier américain. Sur un **PC fixe** avec un écran classique et un clavier **AZERTY**, deux fichiers sont à régler dès le premier jour : `monitors.lua` et `input.lua`. Et puisque tu apprends le japonais, Omarchy sait aussi le taper. D'après le manuel Omarchy 4.

> **Les outils cités dans cette fiche.**
> - **monitors.lua** / **input.lua** : tes fichiers de réglages Hyprland pour les écrans et pour clavier et souris, dans `~/.config/hypr/`.
> - **PPI** (pixels par pouce) : la densité d'un écran ; plus elle est forte, plus il faut agrandir l'affichage.
> - **mise à l'échelle fractionnaire** : agrandir l'affichage d'un facteur non entier (1,25 ; 1,6), utile pour les écrans 4K de bureau.
> - **GTK** : une bibliothèque d'interfaces graphiques utilisée par de nombreuses applis Linux.
> - **hyprctl** : l'outil en ligne de commande pour interroger et piloter Hyprland.
> - **Hyprmon** : un outil en terminal pour disposer et régler les écrans.
> - **XKB** : le système de dispositions de clavier de Linux (`kb_layout`, `kb_options`).
> - **touche compose** : une touche qui combine les suivantes pour produire un caractère spécial.
> - **fcitx5** : un cadre de méthodes de saisie pour les langues qui ne s'écrivent pas lettre par lettre.
> - **Mozc** : le moteur de saisie japonais (dérivé de Google Japanese Input) qui convertit les kana en kanji.
> - **DDC/CI** : un protocole qui permet de régler la luminosité d'un écran externe depuis l'ordinateur.

## Comprendre : densité et échelle

Un écran 1080p de 24 pouces affiche environ 90 pixels par pouce ; un 4K de 27 pouces, environ 160 ; l'écran d'un MacBook ou d'un Framework, plus de 200. Plus la densité est forte, plus il faut agrandir l'affichage pour que le texte reste lisible. Omarchy règle par défaut une **échelle 2** (écrans très denses, autour de 218 PPI). Sur un écran de bureau classique, c'est beaucoup trop : tout paraît énorme.

## Régler ses écrans

Ouvre `~/.config/hypr/monitors.lua` (ou *Setup > Monitors*) et ajuste les deux variables en haut du fichier :

| Écran | `omarchy_gdk_scale` | `omarchy_monitor_scale` |
| --- | --- | --- |
| 1080p ou 1440p (24 à 27 pouces) | `1` | `1` |
| 4K en 27 ou 32 pouces | `2` | `1.6` |
| écran très dense (portable 2x) | `2` | `2` (défaut) |

```lua
-- ~/.config/hypr/monitors.lua, écran 1440p de bureau
local omarchy_gdk_scale = 1
local omarchy_monitor_scale = 1
```

- `omarchy_monitor_scale` fixe la taille de tout l'affichage dans Hyprland.
- `omarchy_gdk_scale` corrige les applis GTK et XWayland, qui gèrent mal l'échelle fractionnaire et sinon s'afficheraient floues ou trop petites.

Pour ajuster à chaud : **Super+/** et **Super+Alt+/** changent l'échelle ; `omarchy display text size 14` (de 9 à 20) ne grossit que le texte.

### Plusieurs écrans, fréquence, position

```bash
hyprctl monitors       # nom des sorties (DP-1, HDMI-A-1), résolution, fréquence, échelle
```

Le fichier `monitors.lua` contient des exemples commentés pour fixer, par sortie, la résolution, la **fréquence** (vérifie qu'un écran 144 Hz tourne bien à 144 Hz et pas à 60) et la position relative des écrans. **Hyprmon** fait la même chose visuellement dans le terminal. Rappels utiles :

- chaque écran a **ses espaces 1 à 10** ; le second écran reçoit en interne les numéros 11 à 20 (correspondance dans `~/.local/state/omarchy/monitor-workspaces`) ;
- **Ctrl+Alt+Tab** passe à l'écran suivant ;
- la luminosité d'un écran externe se règle par **DDC/CI** si l'écran le permet (option à activer dans son menu).

## Le clavier AZERTY

Ouvre `~/.config/hypr/input.lua` (*Setup > Input*). Le manuel donne cet exemple, ici adapté au français :

```lua
hl.config({
  input = {
    kb_layout = "fr,us",
    kb_options = "omarchy:shift_caps_compose,grp:alts_toggle",
    repeat_rate = 40,
    repeat_delay = 600,
    sensitivity = 0.35,
  },
})
```

| Réglage | Effet |
| --- | --- |
| `kb_layout = "fr,us"` | AZERTY par défaut, QWERTY en second |
| `grp:alts_toggle` | les **deux Alt** ensemble basculent de disposition |
| `omarchy:shift_caps_compose` | **Shift+Verr. Maj** devient la touche compose |
| `repeat_rate`, `repeat_delay` | vitesse et délai de répétition d'une touche maintenue |
| `sensitivity` | vitesse de la souris (de -1 à 1) |

Si tu n'as besoin que de l'AZERTY, `kb_layout = "fr"` suffit. Pour la variante française qui facilite les majuscules accentuées, il existe `kb_variant = "oss"` (la disposition « fr oss » de XKB). La barre affiche la disposition active.

D'autres options du manuel :

- **utiliser Alt comme Super** : ajouter `altwin:swap_alt_win` dans `kb_options` ;
- **déplacer la touche compose** sur Alt droite : `compose:ralt` à la place de `omarchy:shift_caps_compose`.

## La touche compose

Elle sert à taper ce que le clavier n'a pas. On l'appuie, on relâche, puis on tape une séquence :

| Séquence | Résultat |
| --- | --- |
| compose, `o`, `e` | œ |
| compose, `'`, `E` | É |
| compose, `<`, `<` | « |
| compose, `-`, `-`, `-` | — |

Tes propres séquences vont dans `~/.XCompose` (par exemple ton adresse e-mail sur compose, `m`, `m`), puis `omarchy-restart-xcompose` pour les activer. Omarchy en définit aussi pour les émojis rapides (compose, `m`, puis une lettre).

## Écrire en japonais

Une disposition de clavier ne suffit pas pour le japonais : il faut un **moteur de saisie** qui convertit la lecture en kana puis en kanji. Omarchy l'installe en une commande :

```bash
omarchy setup input mozc     # ou Setup > Typing > Input Methods
omarchy font cjk jp          # polices CJK par défaut en japonais
```

- **Mozc** s'appuie sur **fcitx5**. Tu tapes `benkyou` en romaji, Mozc propose べんきょう puis 勉強 avec Espace, et Entrée valide.
- On bascule entre saisie latine et japonaise avec le raccourci de fcitx5 (souvent Ctrl+Espace ; attention, c'est aussi le préfixe tmux d'Omarchy, donc change l'un des deux si tu utilises les deux).
- `fcitx5-configtool` (à installer avec `omarchy pkg add fcitx5-configtool`) règle les détails.
- `omarchy font cjk jp` évite un piège classique : sans lui, certains kanji peuvent s'afficher dans leur forme chinoise, légèrement différente.

## Souris et gestes

Les réglages de souris sont dans le même bloc `input` (`sensitivity`). Sur un PC fixe, les gestes de pavé tactile ne servent pas, sauf avec un pavé externe : `hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })` fait changer d'espace en glissant trois doigts.

> **À retenir.** Sur un écran de bureau 1080p ou 1440p, mets les deux échelles à 1 dans `monitors.lua` ; en 4K 27 pouces, 2 et 1,6. Passe le clavier en AZERTY dans `input.lua` (`kb_layout = "fr"` ou `"fr,us"` avec bascule par les deux Alt). Shift+Verr. Maj est la touche compose, et `omarchy setup input mozc` suivi de `omarchy font cjk jp` te permet d'écrire en japonais.
