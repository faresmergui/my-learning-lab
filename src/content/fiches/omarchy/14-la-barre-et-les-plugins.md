---
title: La barre, le shell Quickshell et les plugins
chapter: 14
order: 1
duration: 14
level: Avancé
tags:
- Quickshell
- barre
- shell.json
- widgets
- plugins
- QML
cards:
- q: Qu'est-ce que le shell d'Omarchy 4 ?
  a: Un **seul programme Quickshell** (écrit en QML) qui fournit la barre, le lanceur, les menus, les notifications, les indicateurs de volume et de luminosité, les panneaux, l'écran de verrouillage et l'agent d'autorisation. Il remplace Waybar, Walker, Mako, SwayOSD, hyprlock et hypridle.
- q: Où se règle la barre ?
  a: Dans **`~/.config/omarchy/shell.json`** (position, fond, disposition des widgets, réglages de chaque widget, délais de veille), ou avec la commande **`omarchy bar`**. On peut aussi faire glisser les widgets à la souris et double-cliquer sur le fond pour changer son style.
- q: Quelles sont les zones de la barre ?
  a: '**left**, **centerBegin**, **center**, **centerEnd**, **right**. Par défaut : à gauche le menu et les espaces ; au centre les indicateurs, l''horloge, la météo, le badge de mise à jour ; à droite la zone de notification, la disposition clavier, les agents, Bluetooth, réseau, audio, écran, alimentation.'
- q: Pourquoi les nouveaux widgets d'une mise à jour n'apparaissent-ils pas toujours ?
  a: 'Ton `shell.json` **fait foi tel quel** : il n''est pas fusionné en profondeur avec les défauts. Si tu as personnalisé la disposition, un widget ajouté par Omarchy n''y entre pas tout seul. `omarchy bar defaults` montre la configuration par défaut pour comparer.'
- q: Quelles commandes `omarchy bar` faut-il connaître ?
  a: '`omarchy bar position bottom` (haut, bas, gauche, droite), `omarchy bar background glassy` (clear, glassy, opaque), `omarchy bar move <id> --section <zone> --index <n>`, `omarchy bar set <id> <clé> <valeur>` (ex. format de l''horloge), `omarchy bar defaults`.'
- q: Qu'est-ce qu'un plugin du shell ?
  a: 'Un dossier avec un **`manifest.json`** (identifiant, nom, version, types : widget de barre, panneau, superposition, menu, service) et des fichiers **QML**. Les intégrés ont l''espace de noms réservé `omarchy.` ; les tiens vont dans `~/.config/omarchy/plugins/` et sont rechargés à chaud.'
- q: Quel est le risque des plugins tiers ?
  a: 'Ils **ne sont pas isolés** : un plugin s''exécute avec tes droits, comme n''importe quel programme. Un plugin tiers n''est activé que s''il est listé dans `shell.json`, mais installe uniquement ce que tu as lu ou ce qui vient d''une source fiable (plugins.omarchy.org).'
quiz:
- q: Tu préfères la barre en bas de l'écran, avec un fond transparent. Commandes ?
  options:
  - Modifier /usr/share/omarchy/shell
  - '`omarchy bar position bottom` puis `omarchy bar background clear`'
  - Réinstaller Waybar
  - '`hyprctl bar bottom`'
  answer: 1
  explain: La commande omarchy bar modifie ton shell.json ; Waybar n'existe plus depuis la version 4.
- q: Tu veux l'horloge au format 24 h avec les secondes. Que fais-tu ?
  options:
  - '`omarchy bar set omarchy.clock format HH:mm:ss`'
  - Changer le fuseau horaire
  - Écrire un plugin
  - Modifier le noyau
  answer: 0
  explain: Chaque widget a ses réglages ; `omarchy bar set <id> <clé> <valeur>` les change, et le manuel cite justement le format de l'horloge.
- q: La météo dans la barre ne t'intéresse pas. Le plus propre ?
  options:
  - '`omarchy plugin disable omarchy.weather`'
  - Supprimer des fichiers dans /usr/share/omarchy
  - Couper Internet
  - Changer de thème
  answer: 0
  explain: Les widgets intégrés sont des plugins qu'on active ou désactive ; rien n'est supprimé, c'est réversible.
- q: Tu veux écrire un widget qui affiche le contexte Kubernetes courant. Point de départ conseillé ?
  options:
  - '`omarchy plugin clone <id>` d''un widget proche, puis l''adapter dans ~/.config/omarchy/plugins/'
  - Modifier un plugin intégré en place
  - Réinstaller Omarchy en mode dev
  - Un thème
  answer: 0
  explain: 'Cloner copie un plugin dans ton dossier, avec rechargement à chaud : tu modifies sans toucher aux fichiers d''Omarchy.'
---

Depuis la version 4, tout ce qui entoure les fenêtres (barre, lanceur, menus, notifications, écran de verrouillage) est un seul programme écrit avec **Quickshell**. Cette fiche explique comment régler la barre, comment fonctionnent les widgets et comment aller jusqu'à écrire tes propres plugins. D'après le manuel Omarchy 4.

> **Les outils cités dans cette fiche.**
> - **Quickshell** : une boîte à outils pour construire barres, menus et panneaux de bureau en QML ; Omarchy 4 l'utilise pour tout son shell.
> - **QML** : le langage déclaratif d'interfaces de **Qt**, qui décrit des éléments visuels et leur comportement, avec un peu de JavaScript.
> - **widget** : un élément de la barre (horloge, volume, réseau…).
> - **plugin** : un module qui ajoute au shell un widget, un panneau, un menu ou un service.
> - **manifest.json** : le fichier d'identité d'un plugin (nom, version, types, points d'entrée).
> - **shell.json** : ton fichier de réglages du shell, dans `~/.config/omarchy/`.
> - **polkit** : le système d'autorisations de Linux ; son « agent » affiche la demande de mot de passe quand une appli a besoin de droits.
> - **OSD** (on-screen display) : les petits indicateurs qui s'affichent quand tu changes le volume ou la luminosité.

## Comprendre : un shell, des plugins

<!-- schema:shell -->
<figure class="diagram"><svg viewBox="0 0 680 280" role="img" aria-label="Un shell, des plugins" style="--minw:560px"><defs><marker id="g9-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g9-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g9-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g9-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="652" height="70" rx="12" class="dg-zone "/><text x="26" y="32" class="dg-zl" text-anchor="start">avant la v4 : six outils, six configurations</text><g class="dg-box dg-ghost dg-pop" style="--d:0"><rect x="26" y="40" width="96" height="34" rx="9"/></g><text x="74.0" y="62.0" class="dg-s" text-anchor="middle" style="--d:0">Waybar</text><g class="dg-box dg-ghost dg-pop" style="--d:0"><rect x="132" y="40" width="96" height="34" rx="9"/></g><text x="180.0" y="62.0" class="dg-s" text-anchor="middle" style="--d:0">Walker</text><g class="dg-box dg-ghost dg-pop" style="--d:0"><rect x="238" y="40" width="96" height="34" rx="9"/></g><text x="286.0" y="62.0" class="dg-s" text-anchor="middle" style="--d:0">Mako</text><g class="dg-box dg-ghost dg-pop" style="--d:0"><rect x="344" y="40" width="96" height="34" rx="9"/></g><text x="392.0" y="62.0" class="dg-s" text-anchor="middle" style="--d:0">SwayOSD</text><g class="dg-box dg-ghost dg-pop" style="--d:0"><rect x="450" y="40" width="96" height="34" rx="9"/></g><text x="498.0" y="62.0" class="dg-s" text-anchor="middle" style="--d:0">hyprlock</text><g class="dg-box dg-ghost dg-pop" style="--d:0"><rect x="556" y="40" width="96" height="34" rx="9"/></g><text x="604.0" y="62.0" class="dg-s" text-anchor="middle" style="--d:0">hypridle</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="200" y="116" width="280" height="56" rx="9"/></g><text x="340.0" y="141.0" class="dg-t" text-anchor="middle" style="--d:1">shell Quickshell</text><text x="340.0" y="159.0" class="dg-s" text-anchor="middle" style="--d:1">un processus, un fichier : shell.json</text><path d="M340 84 L340 114" class="dg-l c" marker-end="url(#g9-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="14" y="210" width="204" height="54" rx="9"/></g><text x="116.0" y="234.0" class="dg-t" text-anchor="middle" style="--d:2">omarchy.*</text><text x="116.0" y="252.0" class="dg-s" text-anchor="middle" style="--d:2">plugins intégrés</text><path d="M340 172 L340 190 L116 190 L116 208" class="dg-l c" marker-end="url(#g9-c)"/><g class="dg-box dg-ok dg-pop" style="--d:3"><rect x="238" y="210" width="204" height="54" rx="9"/></g><text x="340.0" y="234.0" class="dg-t" text-anchor="middle" style="--d:3">~/.config/omarchy/plugins</text><text x="340.0" y="252.0" class="dg-s" text-anchor="middle" style="--d:3">tes plugins (QML)</text><path d="M340 172 L340 190 L340 190 L340 208" class="dg-l c" marker-end="url(#g9-c)"/><g class="dg-box dg-pop" style="--d:4"><rect x="462" y="210" width="204" height="54" rx="9"/></g><text x="564.0" y="234.0" class="dg-t" text-anchor="middle" style="--d:4">omarchy bar …</text><text x="564.0" y="252.0" class="dg-s" text-anchor="middle" style="--d:4">réglages en ligne de commande</text><path d="M340 172 L340 190 L564 190 L564 208" class="dg-l c" marker-end="url(#g9-c)"/></svg><figcaption>Barre, lanceur, notifications et verrouillage sont désormais des plugins d&#x27;un seul programme.</figcaption></figure>
<!-- /schema:shell -->

Avant la version 4, Omarchy assemblait six outils séparés (Waybar pour la barre, Walker pour le lanceur, Mako pour les notifications, etc.), chacun avec son format de configuration. Le shell Quickshell les remplace par **un seul processus**, configuré par **un seul fichier** (`shell.json`), et dont chaque élément est un **plugin**. Même les widgets d'Omarchy sont des plugins, avec l'identifiant réservé `omarchy.` (`omarchy.clock`, `omarchy.weather`, `omarchy.media`…).

## La barre par défaut

| Zone | Contenu |
| --- | --- |
| **left** | menu Omarchy, espaces de travail |
| **center** | indicateurs, horloge, Elsewhen (autres fuseaux), météo, badge de mise à jour |
| **right** | zone de notification, disposition du clavier, agents IA, Bluetooth, réseau, audio, écran, alimentation |

Les zones `centerBegin` et `centerEnd` encadrent le centre. Les widgets réagissent à la souris : sur l'horloge, clic gauche pour le calendrier, clic droit pour le format, clic milieu pour le fuseau ; sur le volume, la molette règle le niveau. Les icônes de la zone de notification se gèrent d'un clic droit sur la flèche.

Les panneaux complets s'ouvrent au clavier : **Super+Ctrl+A** (audio), **Super+Ctrl+N** (réseau), **Super+Ctrl+B** (Bluetooth), **Super+Ctrl+Alt+D** (calendrier). **Super+Shift+Espace** masque ou affiche la barre.

## Régler la barre

À la souris : fais **glisser** un widget pour le déplacer, **double-clique** sur le fond de la barre pour passer de transparent à vitré à opaque.

En ligne de commande :

```bash
omarchy bar position bottom                       # top, bottom, left, right
omarchy bar background glassy                     # clear, glassy, opaque
omarchy bar move omarchy.clock --section right --index 0
omarchy bar set omarchy.clock format "HH:mm:ss"
omarchy bar defaults                              # la configuration par défaut, pour comparer
omarchy plugin list                               # widgets disponibles et état
omarchy plugin enable omarchy.media --section centerEnd
omarchy plugin disable omarchy.weather
```

## Le fichier shell.json

Toutes ces commandes écrivent dans `~/.config/omarchy/shell.json`. Sa structure, simplifiée (les identifiants de widgets sont indicatifs) :

```json
{
  "bar": {
    "position": "top",
    "background": "glassy",
    "layout": {
      "left": ["omarchy.menu", "omarchy.workspaces"],
      "center": ["omarchy.clock"],
      "right": ["omarchy.network", "omarchy.audio"]
    }
  },
  "widgets": {
    "omarchy.clock": { "format": "HH:mm" }
  },
  "idle": { "screensaver": 150, "lock": 300 }
}
```

Les identifiants exacts des widgets se lisent avec `omarchy plugin list`, et la structure complète avec `omarchy bar defaults`. Le bloc `idle` règle en secondes le délai avant l'économiseur d'écran et avant le verrouillage (fiche 15).

**Point important** : ton `shell.json` n'est **pas fusionné** avec les défauts. Dès que tu le personnalises, il fait foi tel quel, et un widget ajouté par une future version d'Omarchy n'y apparaîtra pas seul. Après une version majeure, compare avec `omarchy bar defaults`.

## Les plugins

Un plugin est un dossier :

```
mon-widget/
├── manifest.json      identité et points d'entrée
└── Widget.qml         l'interface en QML
```

Le `manifest.json` déclare un `schemaVersion`, un `id` (pas de `omarchy.`, réservé), un `name`, une `version`, des **types** (`bar-widget`, `panel`, `overlay`, `menu`, `service`) et les **points d'entrée** QML.

| Commande | Effet |
| --- | --- |
| `omarchy plugin clone <id>` | copie un plugin (intégré ou non) dans `~/.config/omarchy/plugins/` pour le modifier ; `--edit` ouvre l'éditeur |
| `omarchy plugin add <url-git>` | installe un plugin depuis un dépôt |
| `omarchy plugin validate` | vérifie le manifeste |
| `omarchy plugin update` / `remove` | met à jour, supprime |

Les plugins de `~/.config/omarchy/plugins/` sont **rechargés à chaud** : tu enregistres, la barre se met à jour. Un plugin tiers n'est actif que s'il figure dans `shell.json` ; `disabledPlugins` désactive un plugin sans le supprimer. Le catalogue communautaire est sur **plugins.omarchy.org**.

### Écrire ton premier widget

La méthode la plus sûre : **cloner** un widget intégré qui ressemble à ton idée, puis l'adapter.

1. `omarchy plugin clone omarchy.clock --edit` ;
2. change l'`id` et le `name` dans le manifeste ;
3. modifie le QML : un widget de barre est un petit composant visuel qui affiche un texte ou une icône, mis à jour par un minuteur ou par la sortie d'une commande ;
4. ajoute-le à une zone avec `omarchy bar move` ou dans `shell.json`.

Idées pour un DevOps : le contexte `kubectl` courant (pour ne jamais se tromper de cluster), l'état d'un pipeline, la connexion VPN.

### Prudence

Les plugins **ne sont pas isolés** : un plugin s'exécute avec tes droits et peut lancer des commandes. Applique la même prudence qu'avec l'AUR : lis le code (le QML est court et lisible) avant d'installer un plugin d'une source inconnue.

> **À retenir.** Le shell Quickshell fait tout ce qui entoure les fenêtres, configuré par `~/.config/omarchy/shell.json` et la commande `omarchy bar`. Tout widget est un plugin : on les active, désactive, clone et modifie sans toucher aux fichiers d'Omarchy. Ton `shell.json` n'est pas fusionné avec les défauts : compare avec `omarchy bar defaults` après une mise à jour, et lis un plugin tiers avant de l'installer.
