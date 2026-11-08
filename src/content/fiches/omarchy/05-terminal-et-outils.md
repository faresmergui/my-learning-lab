---
title: Le terminal, tmux et les outils en ligne de commande
chapter: 5
order: 1
duration: 13
level: Débutant
tags:
- foot
- tmux
- bash
- fzf
- zoxide
- Neovim
- omarchy CLI
cards:
- q: Pourquoi foot n'a-t-il ni onglets ni écrans partagés ?
  a: 'C''est un choix : foot reste **léger et rapide**, et les onglets et découpages sont confiés à **tmux** (ou à Hyprland lui-même, qui range les fenêtres). **Super+Alt+Entrée** ouvre directement un terminal dans une session tmux.'
- q: Quel est le préfixe tmux dans Omarchy, et que fait `s` ?
  a: 'Le préfixe est **Ctrl+Espace** (au lieu de Ctrl+B par défaut) : on l''appuie, on relâche, puis on tape la commande. **Préfixe puis s** liste les sessions. **Super+Alt+K** affiche les raccourcis tmux.'
- q: Que remplace zoxide ?
  a: 'La commande **cd** : il mémorise les dossiers où tu vas et te laisse y sauter avec un bout de nom (`cd learning` peut t''emmener dans `~/Documents/Projects/my-learning-hub`). Le chemin complet marche toujours.'
- q: À quoi sert fzf dans Omarchy ?
  a: 'C''est un **filtre interactif** : tu tapes quelques lettres et il trie une liste en direct. **Ctrl+R** cherche dans l''historique des commandes, `ff` cherche un fichier avec aperçu.'
- q: Quels remplaçants modernes de commandes classiques sont livrés ?
  a: '**eza** pour `ls` (alias `ls`, `lt` en arbre, `lsa`, `lta`), **ripgrep** (`rg`) pour `grep`, **fd** pour `find`, **bat** pour `cat` avec coloration, **tldr** pour des exemples à la place des longues pages `man`.'
- q: Comment explorer la commande `omarchy` ?
  a: '`omarchy` seul affiche le centre de commandes et ses groupes (`audio`, `bar`, `theme`, `pkg`, `network`, `update`…). Ajoute `--help` à n''importe quel niveau : `omarchy bar --help`. Beaucoup de commandes acceptent `--json` pour être utilisées dans un script.'
- q: Pourquoi éditer `~/.bashrc` plutôt que les fichiers d'Omarchy pour ses alias ?
  a: '`~/.bashrc` t''appartient et n''est **jamais écrasé** par les mises à jour, alors que les fichiers sous `/usr/share/omarchy` sont remplacés à chaque mise à jour. Tes alias et variables y sont en sécurité.'
quiz:
- q: Tu veux deux terminaux côte à côte dans foot, comme les onglets de Windows Terminal. Que fais-tu ?
  options:
  - Tu cherches l'option dans les menus de foot
  - Tu ouvres deux fenêtres (Hyprland les range) ou tu utilises tmux
  - Tu installes Windows Terminal
  - C'est impossible sous Linux
  answer: 1
  explain: 'foot délègue volontairement onglets et découpages : Hyprland pour les fenêtres, tmux pour les sessions qu''on peut détacher et retrouver.'
- q: Tu as tapé une longue commande `docker run …` il y a deux jours. Le plus rapide pour la retrouver ?
  options:
  - Flèche haut 200 fois
  - Ctrl+R et quelques lettres (recherche fzf dans l'historique)
  - Relire tout ~/.bash_history à la main
  - La retaper
  answer: 1
  explain: 'Ctrl+R ouvre une recherche floue dans l''historique : `dock run` suffit à la retrouver.'
- q: Tu veux ajouter l'alias `gs='git status'` durablement. Où l'écrire ?
  options:
  - Dans /usr/share/omarchy
  - Dans ~/.bashrc
  - Dans le menu Super+Espace
  - Dans monitors.lua
  answer: 1
  explain: ~/.bashrc est à toi et survit aux mises à jour ; /usr/share/omarchy est remplacé à chaque mise à jour.
- q: Tu veux savoir quelles sous-commandes existent pour gérer le thème. Réflexe ?
  options:
  - Chercher sur Reddit
  - '`omarchy theme --help`'
  - Réinstaller Omarchy
  - Lire le code source
  answer: 1
  explain: Chaque groupe de la commande omarchy documente ses sous-commandes avec --help.
---

Omarchy est conçu pour le clavier, et le terminal en est le centre. Même si tu viens du monde DevOps et connais déjà bash, Omarchy livre un ensemble d'outils modernes et de réglages qui méritent d'être connus, ainsi que la commande `omarchy` qui pilote tout le système. Les faits viennent du manuel Omarchy 4.

> **Les outils cités dans cette fiche.**
> - **foot** : le terminal par défaut d'Omarchy 4, léger et natif Wayland ; Alacritty, Ghostty et Kitty sont aussi proposés.
> - **bash** : le shell (l'interpréteur de commandes) par défaut ; sa configuration personnelle est dans `~/.bashrc`.
> - **tmux** : un multiplexeur de terminal ; il découpe un terminal en volets et garde des sessions vivantes qu'on peut quitter et retrouver.
> - **fzf** : un filtre interactif qui trie une liste en direct pendant que tu tapes.
> - **zoxide** : un `cd` intelligent qui retient tes dossiers favoris.
> - **eza** : un `ls` moderne avec couleurs, icônes et vue en arbre.
> - **ripgrep** (`rg`) : une recherche de texte dans les fichiers, beaucoup plus rapide que `grep`.
> - **fd** : un `find` simplifié et rapide.
> - **bat** : un `cat` avec coloration syntaxique et numéros de ligne.
> - **tldr** : des exemples courts pour une commande, en complément des pages `man`.
> - **Neovim** / **LazyVim** : l'éditeur de texte au clavier et la configuration prête à l'emploi livrée par Omarchy.
> - **btop** : un moniteur de ressources (processeur, mémoire, disques, processus) dans le terminal.

## Comprendre : le terminal comme poste de pilotage

Omarchy suit une idée simple : ce que tu fais souvent doit se faire au clavier, et ce qui se fait au clavier peut s'automatiser. Le menu Super+Espace sert à découvrir ; le terminal sert à aller vite. Presque chaque entrée du menu correspond à une commande `omarchy …` que tu peux taper, mettre dans un script ou lier à un raccourci.

## foot et le choix du terminal

**foot** n'a **ni onglets ni découpages**, volontairement : il démarre instantanément et consomme très peu. Pour plusieurs terminaux, deux solutions :

- **plusieurs fenêtres**, que Hyprland range en mosaïque (Super+Entrée plusieurs fois) ;
- **tmux**, pour des volets et des sessions qui survivent à la fermeture de la fenêtre.

Pour changer de terminal : *Install > Terminal* puis *Setup > Defaults > Terminal* dans le menu. La configuration de foot est dans `~/.config/foot/foot.ini` ; les couleurs viennent du thème (fiche 13).

## tmux en dix secondes

| Action | Comment |
| --- | --- |
| Terminal directement dans tmux | **Super+Alt+Entrée** |
| Préfixe (avant chaque commande tmux) | **Ctrl+Espace**, puis relâcher |
| Lister et changer de session | préfixe puis **s** |
| Aide des raccourcis tmux | **Super+Alt+K** |

L'intérêt principal : une session tmux continue de tourner si tu fermes la fenêtre. Tu lances une longue commande, tu fermes, tu reviens plus tard avec préfixe puis **s**. C'est le même principe que sur un serveur en SSH.

## Les outils du quotidien

| Besoin | Outil | Exemple |
| --- | --- | --- |
| Changer de dossier vite | **zoxide** (remplace `cd`) | `cd hub` pour un dossier déjà visité |
| Retrouver une commande | **fzf** | **Ctrl+R** puis quelques lettres |
| Trouver un fichier | **fzf** | `ff` (avec aperçu) |
| Lister | **eza** | `ls`, `lt` (arbre), `lsa` (avec fichiers cachés) |
| Chercher du texte | **ripgrep** | `rg "TODO" src/` |
| Chercher des fichiers | **fd** | `fd '\.lua$' ~/.config` |
| Lire un fichier | **bat** | `bat ~/.config/hypr/bindings.lua` |
| Exemples d'une commande | **tldr** | `tldr tar` |
| Surveiller le système | **btop** | **Super+Shift+T** |

Un détail utile : `try` crée un dossier d'essai daté dans `~/Work/tries` pour tester une idée sans encombrer tes projets.

## Neovim et LazyVim

L'éditeur par défaut est **Neovim** avec **LazyVim**, une configuration complète (explorateur de fichiers, recherche, coloration, complétion). Si tu ne connais pas Vim, rien ne t'oblige à l'adopter : *Setup > Defaults* permet de choisir un autre éditeur. Mais si tu veux t'y mettre, Omarchy est l'environnement idéal, car tout le reste du bureau suit la même logique clavier. Le minimum vital : `i` pour écrire, `Échap` pour revenir en mode commande, `:w` pour enregistrer, `:q` pour quitter.

## La commande omarchy

```bash
omarchy                    # le centre de commandes : tous les groupes
omarchy theme --help       # les sous-commandes d'un groupe
omarchy update             # mettre à jour tout le système (fiche 7)
omarchy pkg add btop       # installer un paquet (fiche 6)
omarchy bar position bottom
```

Quelques options reviennent partout :

| Option | Effet |
| --- | --- |
| `--help` | aide du groupe ou de la sous-commande |
| `--json` | sortie lisible par un script |
| `--all` | appliquer à tous les éléments |
| `--check` | vérifier sans modifier |

Le réflexe à prendre : avant de chercher sur Internet, tape `omarchy`, repère le groupe qui correspond, puis `--help`.

## Tes réglages de shell

Tes alias, fonctions et variables vont dans **`~/.bashrc`**, qui t'appartient et n'est jamais écrasé par une mise à jour. Un exemple pour un DevOps :

```bash
# ~/.bashrc
alias k='kubectl'
alias tf='terraform'
alias gs='git status'
export EDITOR=nvim
```

Recharge avec `source ~/.bashrc` ou ouvre un nouveau terminal. Les dossiers `bin/` de tes projets ne sont pas dans le `PATH` : lance leurs scripts avec `./bin/script` ou ajoute-les toi-même.

> **À retenir.** foot reste minimal ; tmux (préfixe Ctrl+Espace) gère volets et sessions. Ctrl+R pour l'historique, `cd` boosté par zoxide, `rg`, `fd`, `bat` et `eza` à la place des commandes classiques. La commande `omarchy` et son `--help` remplacent souvent une recherche sur Internet, et tes réglages vont dans `~/.bashrc`, que les mises à jour ne touchent pas.
