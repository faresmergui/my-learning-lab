---
title: 'Les thèmes : changer, installer, créer le tien'
chapter: 13
order: 1
duration: 13
level: Avancé
tags:
- thèmes
- colors.toml
- templates
- Aether
- polices
- icônes
cards:
- q: Qu'est-ce qu'un thème Omarchy ?
  a: 'Un dossier qui décrit une **palette de couleurs** (`colors.toml`) et quelques fichiers d''accompagnement (fonds d''écran, jeu d''icônes, image de déverrouillage). En le choisissant, Omarchy **génère** les configurations de couleurs du terminal, de la barre, de Neovim, de btop, de Chromium, de Hyprland, etc. : tout change d''un coup.'
- q: Où sont les thèmes ?
  a: Les thèmes **intégrés** dans `/usr/share/omarchy/themes/` (à ne pas modifier) ; **les tiens** dans `~/.config/omarchy/themes/`. Tout dossier placé là apparaît dans le menu de sélection des thèmes.
- q: Comment créer son thème le plus simplement ?
  a: '**Copier** un thème intégré proche de ce que tu veux depuis `/usr/share/omarchy/themes/` vers `~/.config/omarchy/themes/mon-theme/`, puis modifier son `colors.toml` et ses fonds d''écran. L''appli graphique **Aether** permet aussi de composer une palette visuellement.'
- q: Comment faire un thème clair ?
  a: Mettre `mode = "light"` en haut de `colors.toml` (l'ancienne méthode, un fichier vide `light.mode` à la racine du thème, marche encore).
- q: À quoi servent les modèles `.tpl` ?
  a: À colorer **une appli qu'Omarchy ne gère pas**. Tu places dans `~/.config/omarchy/themed/` un fichier nommé comme la config générée plus `.tpl` (ex. `alacritty.toml.tpl`) avec des variables `{{ background }}`, `{{ foreground }}`, `{{ accent }}`, `{{ color0 }}` à `{{ color15 }}`. Il est régénéré à **chaque changement de thème**.
- q: Comment installer ou partager un thème ?
  a: 'Installer : *Install > Style > Theme* avec l''adresse du dépôt, ou `omarchy theme install <url>`. Partager : publier un dépôt git public nommé **`omarchy-<nom>-theme`**. À l''installation, les fichiers `.lua` et les configs de terminal sont ignorés, pour la sécurité et la cohérence.'
- q: Comment changer de police ?
  a: '*Appearance > Font* pour choisir parmi les polices installées (JetBrainsMono Nerd Font par défaut) ; *Install > Style > Font* pour en ajouter (Cascadia, Meslo, Fira Code, Victor Mono, Iosevka…). Une **Nerd Font** est nécessaire pour les icônes de la barre et du terminal.'
quiz:
- q: Tu veux reprendre Tokyo Night en changeant seulement l'accent et le fond d'écran. Méthode ?
  options:
  - Modifier /usr/share/omarchy/themes/tokyo-night
  - Copier le dossier dans ~/.config/omarchy/themes/ sous un autre nom et modifier la copie
  - Écrire un plugin QML
  - Changer les couleurs appli par appli
  answer: 1
  explain: Les thèmes intégrés sont remplacés à chaque mise à jour ; ta copie dans ~/.config/omarchy/themes/ est à toi et apparaît dans le menu.
- q: Tu utilises k9s, qu'Omarchy ne colore pas, et tu veux qu'il suive le thème. Outil prévu ?
  options:
  - Un modèle .tpl dans ~/.config/omarchy/themed/
  - Un hook theme-set uniquement
  - Modifier k9s à chaque changement de thème
  - Ce n'est pas possible
  answer: 0
  explain: Un modèle avec les variables de la palette est régénéré à chaque changement de thème. (Un hook theme-set peut compléter, pour recharger l'appli.)
- q: Tu installes un thème trouvé sur GitHub, qui contenait un fichier `hyprland.lua`. Que devient-il ?
  options:
  - Il est appliqué tel quel
  - 'Il est ignoré : l''installation retire les .lua et les configs de terminal'
  - Il remplace ton bindings.lua
  - Il bloque l'installation
  answer: 1
  explain: 'Un thème ne doit changer que l''apparence : Omarchy écarte le code Lua et les configs de terminal d''un thème installé.'
- q: Les icônes de ta barre deviennent des carrés après un changement de police. Pourquoi ?
  options:
  - Le thème est cassé
  - La police choisie n'est pas une Nerd Font, qui contient les glyphes d'icônes
  - Le noyau est trop ancien
  - Il manque l'AUR
  answer: 1
  explain: Les icônes de la barre et du terminal sont des caractères spéciaux présents uniquement dans les Nerd Fonts.
---

Les thèmes sont la partie la plus visible d'Omarchy : un seul choix change les couleurs du terminal, de l'éditeur, de la barre, du navigateur, des bordures de fenêtres et le fond d'écran, de façon cohérente. Cette fiche explique comment ça marche, pour aller au-delà des thèmes fournis et créer le tien. D'après le manuel Omarchy 4.

> **Les outils cités dans cette fiche.**
> - **palette** : l'ensemble des couleurs d'un thème (fond, texte, accent, et 16 couleurs de terminal).
> - **colors.toml** : le fichier qui décrit la palette d'un thème ; **TOML** est un format de configuration simple (`clé = valeur`).
> - **modèle** (template, `.tpl`) : un fichier avec des variables `{{ … }}` remplacées par les couleurs du thème.
> - **Aether** : une application graphique pour créer et ajuster des thèmes Omarchy.
> - **Nerd Font** : une police enrichie de milliers d'icônes, nécessaire pour la barre et le terminal.
> - **Yaru** : la famille de jeux d'icônes utilisée par Omarchy, en plusieurs teintes.
> - **Plymouth** : l'écran graphique affiché au démarrage, notamment pour la saisie du mot de passe de chiffrement.

## Comprendre : une palette, des fichiers générés

<!-- schema:themes -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="Une palette, toutes les applis" style="--minw:560px"><defs><marker id="g8-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g8-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g8-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g8-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="14" y="110" width="170" height="70" rx="9"/></g><text x="99.0" y="142.0" class="dg-t" text-anchor="middle" style="--d:0">colors.toml</text><text x="99.0" y="160.0" class="dg-s" text-anchor="middle" style="--d:0">la palette</text><g class="dg-box dg-ghost dg-pop" style="--d:1"><rect x="14" y="200" width="170" height="50" rx="9"/></g><text x="99.0" y="222.0" class="dg-t" text-anchor="middle" style="--d:1">modèles .tpl</text><text x="99.0" y="240.0" class="dg-s" text-anchor="middle" style="--d:1">~/.config/omarchy/themed</text><g class="dg-box dg-ok dg-pop" style="--d:2"><rect x="250" y="120" width="160" height="60" rx="9"/></g><text x="330.0" y="147.0" class="dg-t" text-anchor="middle" style="--d:2">changement de thème</text><text x="330.0" y="165.0" class="dg-s" text-anchor="middle" style="--d:2">génération</text><path d="M184 145 L248 150" class="dg-l c" marker-end="url(#g8-c)"/><path d="M184 225 L250 225 L330 182" class="dg-l" marker-end="url(#g8-n)"/><g class="dg-box dg-pop" style="--d:3"><rect x="486" y="14" width="180" height="44" rx="9"/></g><text x="576.0" y="41.0" class="dg-s" text-anchor="middle" style="--d:3">foot, Alacritty, Ghostty</text><path d="M410 150 L450 150 L450 36 L484 36" class="dg-l ok" marker-end="url(#g8-ok)"/><g class="dg-box dg-pop" style="--d:4"><rect x="486" y="70" width="180" height="44" rx="9"/></g><text x="576.0" y="97.0" class="dg-s" text-anchor="middle" style="--d:4">Hyprland (bordures)</text><path d="M410 150 L450 150 L450 92 L484 92" class="dg-l ok" marker-end="url(#g8-ok)"/><g class="dg-box dg-pop" style="--d:5"><rect x="486" y="126" width="180" height="44" rx="9"/></g><text x="576.0" y="153.0" class="dg-s" text-anchor="middle" style="--d:5">shell (barre, menus)</text><path d="M410 150 L450 150 L450 148 L484 148" class="dg-l ok" marker-end="url(#g8-ok)"/><g class="dg-box dg-pop" style="--d:6"><rect x="486" y="182" width="180" height="44" rx="9"/></g><text x="576.0" y="209.0" class="dg-s" text-anchor="middle" style="--d:6">Neovim, Helix, VS Code</text><path d="M410 150 L450 150 L450 204 L484 204" class="dg-l ok" marker-end="url(#g8-ok)"/><g class="dg-box dg-pop" style="--d:7"><rect x="486" y="238" width="180" height="44" rx="9"/></g><text x="576.0" y="265.0" class="dg-s" text-anchor="middle" style="--d:7">btop, Chromium, Obsidian</text><path d="M410 150 L450 150 L450 260 L484 260" class="dg-l ok" marker-end="url(#g8-ok)"/></svg><figcaption>Le thème décrit les couleurs une seule fois ; Omarchy génère la configuration de chaque appli.</figcaption></figure>
<!-- /schema:themes -->

Au lieu de régler chaque appli séparément, un thème Omarchy décrit **une seule palette** dans `colors.toml`. Quand tu changes de thème, Omarchy **génère** à partir de cette palette les fichiers de couleurs de chaque appli prise en charge : foot, Alacritty, Ghostty, Kitty, btop, Chromium, Hyprland, Neovim, Helix, VS Code, Obsidian et le shell Omarchy. Le résultat est rangé dans `~/.local/state/omarchy/current`.

L'idée est la même qu'un template Helm ou Jinja2 : des modèles d'un côté, des valeurs de l'autre, et un rendu à chaque changement de valeurs.

## Changer de thème

- *Appearance > Theme* dans le menu Super+Espace, avec aperçu ;
- les thèmes de la communauté : *Install > Style > Theme* puis l'adresse du dépôt, ou `omarchy theme install <url>` ;
- `omarchy theme --help` pour le reste des commandes.

## Ce que contient un thème

| Fichier | Rôle |
| --- | --- |
| `colors.toml` | la palette, source de toutes les couleurs générées ; `mode = "light"` en tête pour un thème clair |
| `backgrounds/` | les fonds d'écran du thème |
| `icons.theme` | le nom d'un jeu d'icônes (`Yaru-blue`, `Yaru-red`, `Yaru-sage`…) |
| `unlock.png`, `preview-unlock.png` | l'image de l'écran de déverrouillage du disque (PNG transparent de préférence) ; l'aperçu se génère avec `omarchy plymouth preview` |
| `btop.theme`, `chromium.theme`, `helix.toml`, `shell.toml` | réglages propres à certaines applis |

## Créer ton thème

1. **Pars d'un thème proche** :

   ```bash
   cp -r /usr/share/omarchy/themes/tokyo-night ~/.config/omarchy/themes/mon-theme
   ```

2. **Modifie la palette** dans `~/.config/omarchy/themes/mon-theme/colors.toml` : fond, texte, accent, puis les 16 couleurs de terminal. Garde un **contraste** suffisant entre texte et fond (au moins 4,5 pour 1, la norme d'accessibilité WCAG), sinon la lecture fatigue vite.
3. **Remplace les fonds d'écran** dans `backgrounds/`.
4. **Choisis-le** dans *Appearance > Theme* : il apparaît automatiquement.
5. **Versionne-le** avec tes dotfiles.

Si tu préfères composer visuellement, **Aether** propose une interface graphique pour créer une palette à partir d'une image ou de couleurs choisies, puis l'exporter en thème Omarchy.

## Colorer les applis non prises en charge : les modèles

Pour qu'une appli supplémentaire suive le thème (k9s, lazygit, ton prompt…), crée un **modèle** dans `~/.config/omarchy/themed/`. Il porte le nom du fichier de configuration à générer, suivi de `.tpl`, et contient des variables :

| Variable | Valeur |
| --- | --- |
| `{{ background }}`, `{{ foreground }}` | fond et texte |
| `{{ accent }}` | couleur d'accent |
| `{{ red }}` et autres couleurs nommées | couleurs de la palette |
| `{{ color0 }}` à `{{ color15 }}` | les 16 couleurs de terminal |
| suffixe `_strip` | la couleur sans le `#` |
| suffixe `_rgb` | la couleur en RGB décimal |

Le dossier contient un exemple entièrement commenté, `alacritty.toml.tpl.sample` : c'est la référence pour l'écriture exacte des suffixes. Les modèles sont régénérés **à chaque changement de thème** et remplacent les modèles intégrés pour la même appli. Pour qu'une appli relise sa configuration aussitôt, ajoute un **hook** `theme-set` (fiche 15).

## Partager un thème

1. Publie le dossier dans un dépôt git **public**.
2. Nomme-le **`omarchy-<nom>-theme`** (minuscules, sans espace) : il apparaîtra sous le nom `<nom>`.
3. Les autres l'installent avec *Install > Style > Theme* et l'adresse du dépôt.

À l'installation d'un thème, Omarchy **retire** les fichiers `.lua`, `alacritty.toml`, `foot.ini`, `ghostty.conf`, `kitty.conf` et `vscode.json` : un thème change l'apparence, pas le comportement, et ne peut pas glisser de code dans ta configuration. Ne compte donc pas sur ces fichiers dans un thème partagé.

## Polices et icônes

| Besoin | Moyen |
| --- | --- |
| Changer de police | *Appearance > Font* |
| Installer une police | *Install > Style > Font* (Cascadia, Meslo, Fira Code, Victor Mono, Iosevka…) |
| Polices japonaises par défaut | `omarchy font cjk jp` |
| Changer d'icônes | `icons.theme` dans ton thème |

Choisis une **Nerd Font** pour le terminal et la barre : sans elle, les icônes deviennent des carrés vides.

> **À retenir.** Un thème, c'est une palette (`colors.toml`) dont Omarchy génère les couleurs de toutes les applis. Tes thèmes vivent dans `~/.config/omarchy/themes/` : copie un thème intégré, modifie la palette et les fonds, il apparaît dans le menu. Les modèles `.tpl` de `~/.config/omarchy/themed/` étendent le thème à n'importe quelle appli, et un dépôt `omarchy-<nom>-theme` le partage.
