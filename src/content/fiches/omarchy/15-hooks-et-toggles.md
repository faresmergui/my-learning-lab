---
title: 'Automatiser : hooks, bascules, veille et variables'
chapter: 15
order: 1
duration: 13
level: Avancé
tags:
- hooks
- toggles
- veille
- uwsm
- systemd
- scripts
cards:
- q: Qu'est-ce qu'un hook Omarchy ?
  a: 'Un **script lancé automatiquement** quand un événement se produit. Il se place dans `~/.config/omarchy/hooks/<événement>.d/`. Événements : `post-boot`, `post-update`, `theme-set`, `font-set`, `pre-refresh-pacman`, `battery-low`.'
- q: Comment créer un hook ?
  a: Copier un des fichiers `.sample` fournis et le renommer, ou `omarchy hook install <événement> <script>`. Le script doit être **exécutable** (`chmod +x`). Comme le reste de `~/.config`, il t'appartient et survit aux mises à jour.
- q: Qu'est-ce qu'une bascule (toggle) ?
  a: 'Un interrupteur on/off pour une fonction : veilleuse, économiseur d''écran, mise en veille, notifications… **Super+Ctrl+O** (*Trigger > Toggle*) ou `omarchy toggle <nom>`. L''état est un simple fichier drapeau dans `~/.local/state/omarchy/toggles/` (par exemple `screensaver-off`).'
- q: Où régler les délais d'économiseur d'écran et de verrouillage ?
  a: 'Dans le bloc `idle` de `~/.config/omarchy/shell.json`, en secondes : `screensaver` (150 par défaut) et `lock` (300). Le changement s''applique à l''enregistrement. **Super+Ctrl+I** empêche temporairement la mise en veille (pour un film, une longue compilation).'
- q: Comment définir une variable d'environnement pour toute la session ?
  a: 'Dans un fichier de `~/.config/uwsm/env.d/` (uwsm lance la session Hyprland). Exemple du manuel : `OMARCHY_SCREENRECORD_DIR` pour changer le dossier des enregistrements d''écran. Une variable dans `~/.bashrc` ne vaut que pour les terminaux.'
- q: Pourquoi `--json` est-il utile dans un script ?
  a: 'Beaucoup de commandes `omarchy` (et `hyprctl -j`) produisent du **JSON** : ton script lit une valeur précise avec `jq` au lieu de découper du texte, ce qui ne casse pas quand l''affichage change.'
- q: Comment lancer une tâche régulière (sauvegarde des dotfiles chaque soir) ?
  a: 'Avec un **timer systemd utilisateur** : un fichier `.service` (la commande) et un fichier `.timer` (la fréquence) dans `~/.config/systemd/user/`, puis `systemctl --user enable --now mon.timer`. C''est le cron moderne de Linux.'
quiz:
- q: Après chaque mise à jour d'Omarchy, tu veux être sûr que ton dépôt de dotfiles n'a pas de modification non commitée. Outil ?
  options:
  - Un hook post-update qui lance `git -C ~/dotfiles status --short` et t'envoie une notification
  - Un thème
  - Le scratchpad
  - Un plugin de barre obligatoirement
  answer: 0
  explain: 'post-update se déclenche après chaque mise à jour : idéal pour vérifier ou relancer ce qui dépend d''Omarchy.'
- q: Tu regardes un tutoriel vidéo de 40 minutes et l'écran se verrouille au bout de 5 minutes. Solution immédiate ?
  options:
  - Super+Ctrl+I pour rester éveillé
  - Désactiver LUKS
  - Réinstaller Omarchy
  - Débrancher la souris
  answer: 0
  explain: La bascule « rester éveillé » suspend la mise en veille ; pour un réglage durable, modifie le bloc idle de shell.json.
- q: Tu ajoutes `export OMARCHY_SCREENRECORD_DIR=~/Videos/Captures` dans ~/.bashrc, mais les enregistrements lancés par raccourci n'en tiennent pas compte. Pourquoi ?
  options:
  - Le dossier n'existe pas
  - ~/.bashrc ne s'applique qu'aux terminaux ; la variable doit aller dans ~/.config/uwsm/env.d/
  - Il faut redémarrer le routeur
  - La variable est mal orthographiée dans le manuel
  answer: 1
  explain: Les raccourcis sont lancés par la session, pas par bash. uwsm charge env.d au démarrage de la session.
- q: Tu veux que k9s recharge ses couleurs à chaque changement de thème. Quel événement ?
  options:
  - post-boot
  - theme-set
  - battery-low
  - pre-refresh-pacman
  answer: 1
  explain: theme-set se déclenche après un changement de thème, en complément d'un modèle .tpl (fiche 13).
---

Une fois le poste réglé, l'étape suivante consiste à le faire **réagir tout seul** : lancer un script après une mise à jour, adapter une appli quand le thème change, couper la veille pendant un film. Omarchy fournit pour ça des **hooks**, des **bascules** et des commandes scriptables. Les éléments propres à Omarchy viennent du manuel Omarchy 4 ; les timers systemd sont du Linux général.

> **Les outils cités dans cette fiche.**
> - **hook** : un script exécuté automatiquement lors d'un événement (après une mise à jour, un changement de thème…).
> - **toggle** (bascule) : un interrupteur on/off pour une fonction du système.
> - **fichier drapeau** : un fichier vide dont la simple présence signifie « activé ».
> - **uwsm** : le gestionnaire qui lance la session Wayland (Hyprland) avec ses variables d'environnement.
> - **variable d'environnement** : une valeur nommée transmise aux programmes (`PATH`, `EDITOR`…).
> - **jq** : un outil en ligne de commande pour lire et transformer du JSON.
> - **notify-send** : la commande qui affiche une notification de bureau.
> - **timer systemd** : l'équivalent moderne de cron ; il lance un service à intervalles ou à heure fixe.
> - **hyprsunset** : l'outil de veilleuse (filtre de lumière bleue) utilisé par Omarchy.

## Comprendre : événement, réaction

L'automatisation sous Omarchy suit toujours la même logique : **un déclencheur** (un événement, une touche, une heure) et **une réaction** (un script). Les hooks couvrent les événements d'Omarchy, les raccourcis couvrent tes gestes (fiche 12), les timers systemd couvrent le temps.

| Déclencheur | Outil |
| --- | --- |
| un événement d'Omarchy | hook dans `~/.config/omarchy/hooks/` |
| une touche | `o.bind` dans `bindings.lua` |
| l'ouverture de session | `autostart.lua` |
| une heure, un intervalle | timer systemd utilisateur |

## Les hooks

| Événement | Se déclenche | Idée d'usage |
| --- | --- | --- |
| `post-boot` | après le démarrage de la session | monter un partage réseau, lancer une synchro |
| `post-update` | après `omarchy update` | vérifier tes dotfiles, chercher les `.bak` |
| `theme-set` | après un changement de thème | recharger une appli non gérée |
| `font-set` | après un changement de police | idem pour la police |
| `pre-refresh-pacman` | avant le rafraîchissement des dépôts | rarement utile, réservé aux usages avancés |
| `battery-low` | batterie faible | sans objet sur un PC fixe |

Chaque événement a son dossier, `~/.config/omarchy/hooks/<événement>.d/`, qui contient des exemples `.sample`. Pour créer un hook, copie un exemple sans l'extension `.sample`, ou :

```bash
omarchy hook install post-update ~/bin/check-dotfiles.sh
```

Un exemple de hook `post-update` :

```bash
#!/usr/bin/env bash
# ~/.config/omarchy/hooks/post-update.d/10-dotfiles
changes=$(git -C ~/dotfiles status --short)
baks=$(fd '\.bak$' ~/.config)
if [ -n "$changes$baks" ]; then
  notify-send "Dotfiles" "Modifications non commitées ou fichiers .bak à vérifier"
fi
```

Rends-le exécutable (`chmod +x`). Garde les hooks **courts et rapides** : un hook qui bloque retarde l'événement qui l'a déclenché.

## Les bascules

**Super+Ctrl+O** ouvre le menu des bascules (*Trigger > Toggle*) ; en ligne de commande, `omarchy toggle <nom>`. Les plus utiles :

| Bascule | Raccourci ou commande |
| --- | --- |
| Rester éveillé (pas de veille ni de verrouillage) | **Super+Ctrl+I** |
| Mode silencieux des notifications | **Super+Ctrl+,** |
| Veilleuse (hyprsunset, 4000 K) | menu des bascules |
| Mise en veille autorisée ou non | `omarchy toggle suspend` |
| Barre affichée ou masquée | **Super+Shift+Espace** |
| Marges et bordures | **Super+Shift+Retour arrière** |

L'état de chaque bascule est un **fichier drapeau** dans `~/.local/state/omarchy/toggles/` : `screensaver-off` existe, l'économiseur est coupé. Un script peut donc tester une bascule avec un simple `[ -e … ]`.

Pour que la veilleuse s'allume à chaque session, ajoute `o.launch_on_start("hyprsunset")` dans `autostart.lua` ; sa température se règle dans `~/.config/hypr/hyprsunset.conf`.

## Veille, verrouillage, économiseur

Les délais sont dans le bloc `idle` de `~/.config/omarchy/shell.json`, en secondes, appliqués dès l'enregistrement :

```json
"idle": { "screensaver": 600, "lock": 900 }
```

L'économiseur d'écran se personnalise dans *Appearance > Branding > Screensaver*. **Super+Ctrl+L** verrouille à la main, **Super+Échap** ouvre le menu Système. Sur un PC fixe, la mise en veille profonde et l'hibernation sont traitées dans la fiche 16, avec les précautions propres au disque externe.

## Les variables de session

Une variable définie dans `~/.bashrc` n'existe que dans les terminaux. Pour qu'elle s'applique aussi aux applis lancées par raccourci, place-la dans un fichier de **`~/.config/uwsm/env.d/`**, lu au démarrage de la session :

```bash
# ~/.config/uwsm/env.d/perso
export OMARCHY_SCREENRECORD_DIR="$HOME/Videos/Captures"
export EDITOR=nvim
```

Déconnecte-toi et reconnecte-toi pour l'appliquer.

## Des scripts robustes

- Préfère les sorties **JSON** : `hyprctl -j clients | jq -r '.[].class'` plutôt que de découper du texte. Beaucoup de commandes `omarchy` acceptent aussi `--json`.
- Range tes scripts dans `~/bin` (ou `~/.local/bin`), versionnés avec tes dotfiles, et appelle-les depuis un hook, un raccourci ou le menu.
- Teste un script à la main avant de le brancher sur un événement.

## Les tâches planifiées : timers systemd

Pour une action régulière (pousser tes dotfiles chaque soir), un **timer systemd utilisateur** :

```ini
# ~/.config/systemd/user/dotfiles-push.service
[Service]
Type=oneshot
ExecStart=/usr/bin/git -C %h/dotfiles push

# ~/.config/systemd/user/dotfiles-push.timer
[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl --user enable --now dotfiles-push.timer
systemctl --user list-timers
```

`Persistent=true` rattrape une exécution manquée : précieux pour un système que tu ne démarres que de temps en temps depuis le T7.

> **À retenir.** Les hooks (`~/.config/omarchy/hooks/<événement>.d/`) réagissent aux événements d'Omarchy, surtout `post-update` et `theme-set`. Les bascules (Super+Ctrl+O, `omarchy toggle`) sont de simples fichiers drapeaux, les délais de veille vivent dans le bloc `idle` de `shell.json`, les variables de session dans `~/.config/uwsm/env.d/`, et les tâches régulières dans des timers systemd avec `Persistent=true`.
