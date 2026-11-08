---
title: 'Les dotfiles : ce qui est à toi, ce qui est à Omarchy'
chapter: 8
order: 1
duration: 13
level: Intermédiaire
tags:
- dotfiles
- ~/.config
- Lua
- GNU Stow
- git
- surcharges
cards:
- q: Qu'est-ce qu'un dotfile ?
  a: 'Un fichier de configuration personnel, souvent caché car son nom commence par un **point** (`.bashrc`, `.config/`). Par extension, l''ensemble de tes réglages : on parle de « ses dotfiles » qu''on sauvegarde et qu''on partage.'
- q: Quelle est la règle de propriété des fichiers dans Omarchy ?
  a: '**À toi** : `~/.config`, `~/.XCompose`, `~/.bashrc`, jamais écrasés par une mise à jour. **À Omarchy** : `/usr/share/omarchy`, **remplacé à chaque mise à jour**. On ne modifie jamais les fichiers d''Omarchy : on les **surcharge** depuis ses propres fichiers.'
- q: Comment Hyprland combine-t-il les réglages d'Omarchy et les tiens ?
  a: '`~/.config/hypr/hyprland.lua` charge d''abord les **défauts d''Omarchy**, puis **tes fichiers** (`bindings.lua`, `monitors.lua`, `input.lua`, `looknfeel.lua`, `autostart.lua`). Ce qui est chargé en dernier gagne : tes valeurs remplacent les défauts.'
- q: Quel fichier pour quel réglage ?
  a: '`bindings.lua` raccourcis, `monitors.lua` écrans et échelle, `input.lua` clavier, souris, gestes, `looknfeel.lua` apparence (bordures, marges, disposition), `autostart.lua` programmes au démarrage, `~/.config/omarchy/shell.json` barre et délais de veille, `~/.config/foot/foot.ini` terminal.'
- q: Comment remettre une configuration par défaut ?
  a: '*Update > Config* dans le menu, ou `omarchy reinstall configs` pour toutes. Après une mise à jour qui a dû remplacer un de tes fichiers, ta version est gardée en **`.bak`** à côté.'
- q: Pourquoi versionner ses dotfiles avec git ?
  a: Les snapshots ne couvrent pas `~/.config`. Avec git, chaque modification est **datée et réversible** (`git diff`, `git checkout`), tu peux tester sans peur et réinstaller sur une autre machine en quelques minutes.
- q: À quoi sert GNU Stow ?
  a: Il crée des **liens symboliques** depuis un dossier (par exemple `~/dotfiles/hypr/.config/hypr/`) vers leur emplacement attendu (`~/.config/hypr/`). Tes fichiers vivent dans un dépôt git, et les applications les trouvent à leur place habituelle. Le manuel Omarchy le recommande.
quiz:
- q: Tu veux changer la couleur des bordures et tu trouves le réglage dans /usr/share/omarchy. Que fais-tu ?
  options:
  - Tu modifies le fichier dans /usr/share/omarchy
  - Tu recopies le réglage dans ~/.config/hypr/looknfeel.lua et tu l'y modifies
  - Tu supprimes /usr/share/omarchy
  - Tu passes en canal dev
  answer: 1
  explain: '/usr/share/omarchy est remplacé à chaque mise à jour : ta modification disparaîtrait. Tes fichiers, chargés après, surchargent les défauts.'
- q: Après une grosse mise à jour, un de tes réglages a disparu. Où chercher ?
  options:
  - Nulle part, il est perdu
  - Un fichier .bak à côté du fichier concerné, à comparer avec la nouvelle version
  - Dans la corbeille
  - Dans le snapshot
  answer: 1
  explain: Omarchy garde ta version en .bak quand il doit remettre un défaut. `fd '\.bak$' ~/.config` les liste.
- q: Tu as testé plusieurs réglages et plus rien ne marche dans les raccourcis. Ton dépôt git de dotfiles est à jour. Solution la plus rapide ?
  options:
  - Réinstaller Omarchy
  - '`git diff` pour voir ce qui a changé, puis `git checkout` du fichier'
  - Restaurer un snapshot
  - Formater le T7
  answer: 1
  explain: git montre exactement ce que tu as modifié et permet d'annuler fichier par fichier.
- q: Tu ajoutes un widget dans shell.json mais une nouvelle version d'Omarchy ajoute un widget par défaut que tu ne vois pas. Pourquoi ?
  options:
  - Un bug
  - 'Ton shell.json fait foi tel quel : il n''est pas fusionné avec les défauts, les nouveaux widgets n''arrivent pas seuls'
  - Il faut redémarrer deux fois
  - Le thème le cache
  answer: 1
  explain: 'Le manuel le précise : pas de fusion profonde. Compare avec `omarchy bar defaults` pour récupérer les nouveautés.'
---

Personnaliser Omarchy sans le casser repose sur une seule règle : savoir **à qui appartient chaque fichier**. Les fichiers d'Omarchy sont remplacés à chaque mise à jour ; les tiens jamais. Tu ne modifies donc pas les premiers, tu les **surcharges** avec les seconds. Cette fiche donne la carte des fichiers et une méthode pour les sauvegarder. D'après le manuel Omarchy 4.

> **Les outils cités dans cette fiche.**
> - **dotfiles** : les fichiers de configuration personnels, souvent cachés (nom commençant par un point).
> - **`~`** : raccourci pour ton dossier personnel, `/home/<ton nom>`.
> - **surcharge** (override) : redéfinir une valeur dans un fichier chargé après le fichier par défaut, pour qu'elle le remplace.
> - **Lua** : le langage de la configuration de Hyprland depuis Omarchy 4.
> - **JSON** / **JSONC** : des formats de données texte ; JSONC accepte en plus les commentaires.
> - **git** : le système de gestion de versions, que tu connais du travail.
> - **GNU Stow** : un petit outil qui crée des liens symboliques depuis un dossier de dotfiles vers leur emplacement.
> - **lien symbolique** : un raccourci au niveau du système de fichiers, qui pointe vers un autre fichier.

## Comprendre : deux étages

<!-- schema:dotfiles -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="Deux étages de configuration" style="--minw:560px"><defs><marker id="g5-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g5-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g5-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g5-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="300" height="220" rx="12" class="dg-zone "/><text x="26" y="32" class="dg-zl" text-anchor="start">à Omarchy · remplacé à chaque mise à jour</text><rect x="366" y="14" width="300" height="220" rx="12" class="dg-zone dg-zc"/><text x="378" y="32" class="dg-zl" text-anchor="start">à toi · jamais écrasé</text><g class="dg-box dg-ghost dg-pop" style="--d:0"><rect x="34" y="44" width="260" height="48" rx="9"/></g><text x="164.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:0">/usr/share/omarchy</text><text x="164.0" y="83.0" class="dg-s" text-anchor="middle" style="--d:0">défauts, scripts</text><g class="dg-box dg-ghost dg-pop" style="--d:1"><rect x="34" y="106" width="260" height="48" rx="9"/></g><text x="164.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:1">thèmes intégrés</text><text x="164.0" y="145.0" class="dg-s" text-anchor="middle" style="--d:1">à copier, pas à modifier</text><g class="dg-box dg-ghost dg-pop" style="--d:2"><rect x="34" y="168" width="260" height="48" rx="9"/></g><text x="164.0" y="189.0" class="dg-t" text-anchor="middle" style="--d:2">plugins omarchy.*</text><text x="164.0" y="207.0" class="dg-s" text-anchor="middle" style="--d:2">widgets du shell</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="386" y="44" width="260" height="48" rx="9"/></g><text x="516.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:3">~/.config/hypr/*.lua</text><text x="516.0" y="83.0" class="dg-s" text-anchor="middle" style="--d:3">raccourcis, écrans, clavier, look</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="386" y="106" width="260" height="48" rx="9"/></g><text x="516.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:4">~/.config/omarchy/</text><text x="516.0" y="145.0" class="dg-s" text-anchor="middle" style="--d:4">shell.json, thèmes, hooks, menu</text><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="386" y="168" width="260" height="48" rx="9"/></g><text x="516.0" y="189.0" class="dg-t" text-anchor="middle" style="--d:5">~/.bashrc, ~/.XCompose</text><text x="516.0" y="207.0" class="dg-s" text-anchor="middle" style="--d:5">shell, touche compose</text><g class="dg-box dg-ok dg-pop" style="--d:6"><rect x="190" y="252" width="300" height="40" rx="9"/></g><text x="340.0" y="277.0" class="dg-s" text-anchor="middle" style="--d:6">hyprland.lua : défauts, puis tes fichiers</text><path d="M164 234 L164 272 L188 272" class="dg-l" marker-end="url(#g5-n)"/><path d="M516 234 L516 272 L492 272" class="dg-l c" marker-end="url(#g5-c)"/></svg><figcaption>Tes fichiers sont chargés après ceux d&#x27;Omarchy : tu écris seulement ce que tu changes.</figcaption></figure>
<!-- /schema:dotfiles -->

| | À Omarchy | À toi |
| --- | --- | --- |
| Où | `/usr/share/omarchy` (et `~/.local/share/omarchy`, un lien géré par pacman) | `~/.config`, `~/.bashrc`, `~/.XCompose` |
| Contenu | défauts, scripts, thèmes intégrés, shell | tes surcharges et tes réglages |
| Mise à jour | **remplacé** à chaque `omarchy update` | **jamais écrasé** (sauf `.bak` dans de rares cas) |
| Tu peux… | lire, copier des exemples | modifier librement |

C'est le même principe qu'en DevOps avec des valeurs par défaut et des surcharges (un `values.yaml` de chart Helm et ton propre fichier de valeurs, ou les `defaults/` et les `vars/` d'un rôle Ansible) : tu ne modifies pas le paquet, tu fournis tes valeurs, et elles gagnent.

## La carte des fichiers

| Fichier | Rôle | Accès rapide |
| --- | --- | --- |
| `~/.config/hypr/hyprland.lua` | point d'entrée : charge les défauts puis tes fichiers | — |
| `~/.config/hypr/bindings.lua` | raccourcis clavier (fiche 12) | *Setup* |
| `~/.config/hypr/monitors.lua` | écrans, résolution, échelle (fiche 9) | *Setup > Monitors* |
| `~/.config/hypr/input.lua` | clavier, souris, gestes (fiche 9) | *Setup > Input* |
| `~/.config/hypr/looknfeel.lua` | bordures, marges, arrondis, disposition | — |
| `~/.config/hypr/autostart.lua` | programmes lancés à la connexion | — |
| `~/.config/omarchy/shell.json` | barre, widgets, délais de veille et de verrouillage (fiche 14) | — |
| `~/.config/omarchy/themes/` | tes thèmes (fiche 13) | — |
| `~/.config/omarchy/themed/` | tes modèles de fichiers à colorer selon le thème | — |
| `~/.config/omarchy/extensions/omarchy-menu.jsonc` | tes entrées du menu Omarchy (fiche 12) | — |
| `~/.config/omarchy/hooks/` | scripts lancés sur des événements (fiche 15) | — |
| `~/.config/foot/foot.ini` | le terminal | — |
| `~/.bashrc` | alias, variables, fonctions du shell | — |
| `~/.XCompose` | combinaisons de la touche compose (fiche 9) | — |

Les entrées du menu *Setup* ouvrent le bon fichier dans l'éditeur ; le changement s'applique quand tu fermes l'éditeur. Pour les autres, Hyprland recharge sa configuration automatiquement à l'enregistrement.

## Comment se fait la surcharge

`hyprland.lua` charge les fichiers dans cet ordre : **défauts d'Omarchy d'abord, tes fichiers ensuite**. Une valeur définie deux fois prend la dernière. Un exemple dans `looknfeel.lua` :

```lua
hl.config({
  decoration = {
    rounding = 8,       -- coins arrondis
  },
  general = {
    gaps_in = 0,        -- pas d'espace entre les fenêtres
    gaps_out = 0,       -- ni autour
    border_size = 0,    -- pas de bordure
  },
})
```

Tu n'écris que **ce que tu changes** : tout le reste vient des défauts. Pour trouver un nom de réglage, lis les défauts dans `/usr/share/omarchy` (sans les modifier) ou la documentation de Hyprland.

## Remettre à zéro

| Besoin | Moyen |
| --- | --- |
| Remettre une configuration par défaut | *Update > Config* |
| Remettre toutes les configurations | `omarchy reinstall configs` |
| Retrouver ta version après une mise à jour | le fichier `.bak` à côté |

Avant une remise à zéro, sauvegarde : elle écrase tes modifications.

## Sauvegarder ses dotfiles avec git et Stow

Les snapshots ne couvrent pas `~/.config`, et ton système vit sur un disque externe qui peut tomber ou se perdre. Mets tes réglages dans un dépôt git. Le manuel recommande **GNU Stow** pour garder les fichiers dans un dossier unique tout en les laissant à leur place :

```bash
omarchy pkg add stow
mkdir -p ~/dotfiles/hypr/.config
mv ~/.config/hypr ~/dotfiles/hypr/.config/
cd ~/dotfiles && stow hypr      # recrée ~/.config/hypr comme lien vers ~/dotfiles/hypr/.config/hypr
git init && git add . && git commit -m "Hyprland : réglages de départ"
```

Fais de même pour `omarchy` (le dossier `~/.config/omarchy`), `foot`, et un dossier `bash` pour `.bashrc`. Pousse le dépôt sur GitHub (en **privé** si tes fichiers contiennent des informations personnelles, et sans aucun secret).

Le bénéfice au quotidien :

- `git diff` montre ce que tu as changé depuis le dernier état qui marchait ;
- `git checkout -- fichier` annule une expérience ratée ;
- une réinstallation d'Omarchy se termine par `git clone` et `stow` : tu retrouves ton poste en deux minutes.

## Les bonnes habitudes

1. **Un changement à la fois**, puis test, puis commit. Si quelque chose casse, tu sais quoi annuler.
2. **Commente** tes surcharges en une ligne : dans six mois, tu sauras pourquoi elles existent.
3. Après une **version majeure** d'Omarchy, cherche les `.bak` et relis les notes de version : un réglage a pu changer de nom.
4. Garde une **console de secours** en tête : si Hyprland ne démarre plus, **Ctrl+Alt+F2** ouvre une console texte d'où tu peux corriger un fichier (fiche 11).

> **À retenir.** `/usr/share/omarchy` appartient à Omarchy et change à chaque mise à jour ; `~/.config`, `~/.bashrc` et `~/.XCompose` sont à toi. On n'édite jamais les défauts : on écrit seulement ce qu'on change dans ses propres fichiers, chargés après. Versionne `~/.config` avec git (et Stow), car aucun snapshot ne le protège.
