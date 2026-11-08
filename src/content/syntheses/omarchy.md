---
title: Synthèse Omarchy
description: "Couches, démarrage sur SSD externe, raccourcis, dispositions, paquets, mises à jour et snapshots, dotfiles, écrans et clavier, réseau, dépannage, personnalisation."
---

## Le modèle

- **Omarchy = Arch Linux + des choix tout faits** : Hyprland (fenêtres en mosaïque), shell **Quickshell** (barre, menus, notifications, verrouillage), thèmes, commande `omarchy`.
- Couches : noyau `linux-omarchy` → Arch (pacman, systemd) → Wayland → Hyprland → shell → thèmes → applis. Une panne appartient à une couche.
- **v4 « Quattro »** (août 2026) : config Hyprland en **Lua** (`~/.config/hypr/*.lua`), Waybar/Walker/Mako/hyprlock remplacés par le shell, **foot** par défaut, Omarchy en paquets. Méfiance envers les tutos plus anciens.

## Le T7 et Windows

- Chaque disque a son ESP : Windows Boot Manager en interne, **Limine** sur le T7. Choix au démarrage : F8 / F11 / F12 ou ordre de démarrage dans l'UEFI.
- Horloge décalée sous Windows : `RealTimeIsUniversal = 1` dans le registre.
- **Secure Boot** coupé pour Omarchy, à rallumer pour Valorant (VAN 9003). Démarrage rapide de Windows désactivé.
- Port **USB 3.2 Gen 2 arrière** : `lsusb -t` → `Driver=uas`, `10000M` ; `omarchy disk speedtest`. Ne jamais débrancher en marche.

## Raccourcis essentiels

| Action | Touche |
| --- | --- |
| Menu Omarchy / aide | **Super+Espace** / **Super+K** |
| Terminal / navigateur / fichiers | **Super+Entrée** / **Super+Shift+Entrée** / **Super+Shift+F** |
| Fermer / plein écran / flottant | **Super+W** / **Super+F** / **Super+T** |
| Focus / échanger | **Super+flèches** / **Super+Shift+flèches** |
| Espace n / y envoyer / sans suivre | **Super+n** / **Super+Shift+n** / **Super+Shift+Alt+n** |
| Copier / coller / historique | **Super+C** / **Super+V** / **Super+Ctrl+V** |
| Capture / menu capture / OCR | **Impr** / **Super+Ctrl+C** / **Super+Ctrl+Impr** |
| Verrouiller / menu Système | **Super+Ctrl+L** / **Super+Échap** |
| Disposition suivante | **Super+L** (dwindle, scrolling, floating ; par espace) |
| Groupe / scratchpad / console quake | **Super+G** / **Super+S** (envoyer : Super+Alt+S) / **Super+`** |
| Fenêtre / espace vers l'autre écran | **Super+Shift+Ctrl+flèche** / **Super+Shift+Alt+flèche** |

## Terminal

- foot sans onglets → tmux (**Super+Alt+Entrée**, préfixe **Ctrl+Espace**, `s` sessions).
- **Ctrl+R** historique (fzf), `cd` = zoxide, `ls`/`lt` = eza, `rg`, `fd`, `bat`, `tldr`.
- `omarchy` puis `omarchy <groupe> --help` ; `--json` pour les scripts. Alias dans `~/.bashrc`.

## Paquets

- Rolling release : mettre à jour **souvent et en entier**, jamais `pacman -Sy paquet`.
- `omarchy pkg add` / `omarchy pkg drop` ; *Remove > Preinstalls*.
- Enquête : `pacman -Ss`, `-Qi`, `-Ql`, `-Qo /chemin`, `-Qe`, `-Qdtq`.
- `pacman -Syu` bloqué → `omarchy update`. AUR = dernier recours, PKGBUILD lu.

## Mises à jour

- `omarchy update` : snapshot → Omarchy → migrations → paquets Arch (miroir stable ≈ 1 mois de retard) → AUR.
- Canaux : **stable** (défaut), rc, edge, dev (`omarchy-channel-set`).
- Snapshot = `/` seulement (pas `/home`, pas `~/.config`) ; démarrable depuis **Limine** ; `omarchy-snapshot create / restore`. Direct Boot cache Limine.
- Noyau : `omarchy-kernel list / set` ; garder `linux-lts` en secours. Firmware : *Update > Firmware*.
- Dernier recours : `omarchy reinstall configs`, puis `omarchy reinstall`.

## Dotfiles

- **À Omarchy** : `/usr/share/omarchy` (écrasé à chaque mise à jour). **À toi** : `~/.config`, `~/.bashrc`, `~/.XCompose`.
- `hyprland.lua` charge les défauts puis `bindings.lua`, `monitors.lua`, `input.lua`, `looknfeel.lua`, `autostart.lua`. N'écrire que ce qui change.
- Shell : `~/.config/omarchy/shell.json` (pas de fusion avec les défauts). Menu : `extensions/omarchy-menu.jsonc`. Hooks : `hooks/<événement>.d/`.
- Fichiers `.bak` après une mise à jour. Tout versionner : **git + GNU Stow**.

## Écrans et clavier

- Écran 1080p/1440p : `omarchy_gdk_scale = 1`, `omarchy_monitor_scale = 1`. 4K 27" : 2 et 1.6. `hyprctl monitors`, Hyprmon.
- `input.lua` : `kb_layout = "fr,us"`, `kb_options = "omarchy:shift_caps_compose,grp:alts_toggle"`.
- Compose = **Shift+Verr. Maj** ; `~/.XCompose` + `omarchy-restart-xcompose`.
- Japonais : `omarchy setup input mozc` + `omarchy font cjk jp` (bascule fcitx5, attention au conflit avec Ctrl+Espace de tmux).

## Réseau et sécurité

- NetworkManager : **Super+Ctrl+N**, `nmtui`, `omarchy network`, `omarchy dns`.
- `ping 1.1.1.1` OK mais pas `ping github.com` → DNS.
- Pare-feu : entrant bloqué sauf **53317** (LocalSend), sortant libre, Docker verrouillé (ufw-docker). SSH éteint (*Setup > Security > SSHD*).
- LUKS + mot de passe session : *Update > Password*. `omarchy-sudo-passwordless 30` (icône rouge), jamais `permanent`.
- `systemctl status`, `systemctl --failed`, `journalctl -u <svc> -b`, `journalctl -b -p err`.

## Dépanner

- Qu'est-ce qui a changé ? Quelle couche ? Quel retour en arrière le plus léger ?
- Échelle : ton changement (git, `.bak`) → snapshot → `reinstall configs` → `reinstall` → réinstallation.
- **Ctrl+Alt+F2** : console texte. `hyprctl configerrors`. *Update > Hardware* (**Super+Ctrl+H**) pour Wi-Fi, Bluetooth, son.
- Compte bloqué : `faillock --reset --user <nom>`. Aide : `omarchy-debug` + Discord #omarchy-help.
- Extrême : clé USB, `cryptsetup open`, montage, `arch-chroot`.

## Personnaliser

- Raccourcis : `o.rebind("SUPER + SHIFT + O", "Joplin", "joplin-desktop")`, `o.bind` (combinaison libre), `hl.unbind`.
- Applis web : *Install > Web App* ; Shift+Alt+L copie l'URL. Autostart : `o.launch_on_start("…")`.
- Règles : `o.window("(foot)", { … })` ; classe via `hyprctl clients`.
- Thèmes : `~/.config/omarchy/themes/` (copier un intégré), `colors.toml` (`mode = "light"`), modèles `.tpl` dans `themed/` (`{{ background }}`, `{{ accent }}`, `{{ color0 }}`…), partage `omarchy-<nom>-theme`.
- Barre : `omarchy bar position / background / move / set / defaults` ; `omarchy plugin list / enable / disable / clone`. Plugins non isolés.
- Hooks : `post-update`, `theme-set`, `post-boot`… Bascules : **Super+Ctrl+O**, **Super+Ctrl+I** (rester éveillé). `idle` dans shell.json. Variables : `~/.config/uwsm/env.d/`. Timers systemd avec `Persistent=true`.

## Optimiser

- `systemd-analyze blame` ; `lspci -k` (éviter `nouveau` sur NVIDIA) ; fréquence de l'écran.
- Sur le T7 : extinction plutôt qu'hibernation (`omarchy hibernation setup` réserve la taille de la RAM).
- Jeux : Steam + Proton, ProtonDB ; pas de Valorant (Vanguard) → redémarrer sur Windows.
- Agents IA : `omarchy default agent`, **Super+Shift+Ctrl+A** ; auto-approbation → commit avant, sudo protégé, tâche précise.
