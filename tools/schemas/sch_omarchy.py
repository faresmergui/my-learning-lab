from svg import D, figure
from inject import put

M = 'omarchy'

# --- 01: the layers ------------------------------------------------
d = D(680, 352)
layers = [
    ('tes applications', 'foot, Neovim, Chromium, btop…', 'ok'),
    ('thèmes', 'une palette appliquée partout', ''),
    ('shell Quickshell', 'barre, lanceur, menus, notifications, verrouillage', 'c'),
    ('Hyprland', 'compositeur en mosaïque : place et dessine les fenêtres', 'c'),
    ('Wayland (+ XWayland)', "protocole d'affichage", ''),
    ('Arch Linux', 'pacman, systemd, dépôts', 'a'),
    ('noyau linux-omarchy', 'pilotes, mémoire, processus', 'ghost'),
]
for i, (t, s, k) in enumerate(layers):
    w = 440 + i * 30
    x = 340 - w / 2
    d.box(x, 14 + i * 44, w, 38, t, s, k=k, rx=8, d=6 - i)
d.text(14, 342, 'chaque couche ne parle qu\'à ses voisines : une panne appartient à une couche', 's', anchor='start')
put(f'{M}/01-comprendre-omarchy.md', 'couches', figure(d, "Les couches d'Omarchy",
    "Omarchy, c'est Arch Linux plus des choix tout faits pour chaque couche au-dessus."), before='| Couche |')

# --- 02: booting from the external SSD ----------------------------
d = D(680, 330)
d.box(220, 14, 240, 50, 'UEFI', 'ordre de démarrage ou F8 / F11 / F12', k='c', d=0)
d.zone(14, 100, 300, 210, 'disque interne', k='')
d.zone(366, 100, 300, 210, 'Samsung T7 (USB 3.2)', k='c')
d.box(34, 132, 260, 44, 'ESP Windows', 'Windows Boot Manager', d=1)
d.box(34, 200, 260, 44, 'Windows', 'BitLocker, Vanguard, Secure Boot', d=2)
d.box(386, 132, 260, 44, 'ESP Omarchy', 'Limine (menu des snapshots)', k='c', d=1)
d.box(386, 200, 260, 44, 'partition LUKS', 'mot de passe au démarrage', k='a', d=2)
d.box(386, 258, 260, 40, 'Omarchy (Btrfs)', k='ok', tk='s', d=3)
d.arrow([(220, 39), (164, 39), (164, 130)])
d.arrow([(460, 39), (516, 39), (516, 130)], color='c')
d.text(176, 84, 'T7 débranché', 's', anchor='start')
d.text(504, 84, 'T7 branché, en premier', 's', anchor='end')
d.arrow([(164, 176), (164, 198)])
d.arrow([(516, 176), (516, 198)], color='c')
d.arrow([(516, 244), (516, 256)], color='c')
put(f'{M}/02-omarchy-sur-ssd-externe.md', 'demarrage', figure(d, 'Deux disques, deux chargeurs',
    "Chaque disque a sa propre partition de démarrage : Omarchy n'écrit rien sur le disque Windows."), before='- le disque interne')

# --- 04: the three layouts ----------------------------------------
d = D(680, 250)
titles = [('dwindle', 'tout reste visible'), ('scrolling', 'un ruban qui déborde'), ('floating', 'fenêtres libres')]
for i, (t, s) in enumerate(titles):
    x = 14 + i * 224
    d.zone(x, 14, 204, 170, t, k='c' if i == 0 else '')
    d.text(x + 102, 206, s, 's')
x = 24
d.box(x, 40, 90, 134, '1', k='c', d=0)
d.box(x + 96, 40, 88, 64, '2', d=1)
d.box(x + 96, 110, 42, 64, '3', d=2)
d.box(x + 144, 110, 40, 64, '4', d=3)
x = 248
for i in range(3):
    d.box(x + i * 64, 40, 58, 134, str(i + 1), k='c' if i == 1 else '', d=i)
d.text(x + 186, 112, '→', 'ct')
x = 472
d.box(x, 46, 110, 76, '1', d=0)
d.box(x + 60, 84, 110, 76, '2', k='c', d=1)
d.box(x + 20, 128, 70, 42, '3', d=2)
d.text(340, 238, 'Super+L change la disposition de l\'espace courant (mémorisée par espace)', 's')
put(f'{M}/04-fenetres-espaces-dispositions.md', 'dispositions', figure(d, 'Dwindle, scrolling, floating',
    "Chaque espace de travail garde sa propre disposition, même après un redémarrage."), before='| Disposition |')

# --- 07: update and rollback ---------------------------------------
d = D(680, 300)
steps = [('snapshot', 'photo de /'), ('Omarchy', 'dépôt Omarchy'), ('migrations', 'configs adaptées'), ('paquets Arch', 'miroir stable (≈ 1 mois)')]
for i, (t, s) in enumerate(steps):
    x = 14 + i * 168
    d.box(x, 40, 150, 56, t, s, k='c' if i == 0 else '', d=i)
    if i:
        d.arrow([(x - 16, 68), (x - 2, 68)], color='c')
d.text(14, 26, 'omarchy update', 'zl', anchor='start')
d.box(14, 150, 300, 56, 'tout va bien', 'tu continues, le snapshot reste disponible', k='ok', d=4)
d.box(366, 150, 300, 56, 'quelque chose casse', 'redémarrer, menu Limine, snapshot d\'avant', k='a', d=4)
d.arrow([(588, 96), (588, 116), (164, 116), (164, 148)], color='ok')
d.arrow([(588, 116), (516, 116), (516, 148)], color='a')
d.box(366, 236, 300, 50, 'omarchy-snapshot restore', 'rendre le retour définitif', k='ghost', d=5)
d.arrow([(516, 206), (516, 234)], color='a')
d.text(14, 250, 'les snapshots ne couvrent ni /home', 's', anchor='start')
d.text(14, 268, 'ni ~/.config : tes réglages se protègent avec git', 's', anchor='start')
put(f'{M}/07-mettre-a-jour-sans-casser.md', 'miseajour', figure(d, 'Une mise à jour avec filet',
    "Le snapshot pris avant la mise à jour est ton bouton « annuler »."), before='À chaque `omarchy update`')

# --- 08: who owns what ------------------------------------------------
d = D(680, 300)
d.zone(14, 14, 300, 220, 'à Omarchy · remplacé à chaque mise à jour', k='')
d.zone(366, 14, 300, 220, 'à toi · jamais écrasé', k='c')
for i, (t, s) in enumerate([('/usr/share/omarchy', 'défauts, scripts'), ('thèmes intégrés', 'à copier, pas à modifier'), ('plugins omarchy.*', 'widgets du shell')]):
    d.box(34, 44 + i * 62, 260, 48, t, s, k='ghost', d=i)
for i, (t, s) in enumerate([('~/.config/hypr/*.lua', 'raccourcis, écrans, clavier, look'), ('~/.config/omarchy/', 'shell.json, thèmes, hooks, menu'), ('~/.bashrc, ~/.XCompose', 'shell, touche compose')]):
    d.box(386, 44 + i * 62, 260, 48, t, s, k='c', d=3 + i)
d.box(190, 252, 300, 40, 'hyprland.lua : défauts, puis tes fichiers', k='ok', tk='s', d=6)
d.arrow([(164, 234), (164, 272), (188, 272)])
d.arrow([(516, 234), (516, 272), (492, 272)], color='c')
put(f'{M}/08-les-dotfiles.md', 'dotfiles', figure(d, 'Deux étages de configuration',
    "Tes fichiers sont chargés après ceux d'Omarchy : tu écris seulement ce que tu changes."), before='| | À Omarchy | À toi |')

# --- 10: the firewall --------------------------------------------------
d = D(680, 260)
d.box(250, 90, 180, 80, 'ton PC Omarchy', 'pare-feu UFW', k='c', d=0)
d.box(14, 20, 180, 50, 'Internet', d=1)
d.box(14, 190, 180, 50, 'réseau local', 'téléphone, autre PC', d=1)
d.box(486, 20, 180, 50, 'sortant', 'web, mises à jour, jeux', k='ok', d=2)
d.box(486, 190, 180, 50, 'Tailscale', 'réseau privé, aucun port ouvert', k='ghost', d=3)
d.arrow([(194, 45), (248, 110)], color='a')
d.arrow([(194, 215), (248, 150)], color='ok')
d.text(206, 104, 'entrant : bloqué', 'at', anchor='end')
d.text(206, 166, '53317 : LocalSend', 'okt', anchor='end')
d.arrow([(432, 110), (484, 45)], color='ok')
d.arrow([(432, 150), (484, 215)], color='c', start=True)
put(f'{M}/10-reseau-securite-services.md', 'parefeu', figure(d, 'Ce qui entre, ce qui sort',
    "Tout l'entrant est bloqué sauf LocalSend ; le sortant est libre ; SSH reste éteint tant que tu ne l'actives pas."), before='Un poste de travail **sort**')

# --- 11: the rollback ladder ------------------------------------------
d = D(680, 300)
rungs = [('1 · annuler ton changement', 'git checkout, fichier .bak', 'ok'), ('2 · snapshot d\'avant', 'menu Limine', 'c'),
         ('3 · omarchy reinstall configs', 'configurations par défaut', ''), ('4 · omarchy reinstall', 'paquets + configs, canal stable', 'a'),
         ('5 · réinstaller', 'efface tes données', 'a')]
for i, (t, s, k) in enumerate(rungs):
    w = 300 + i * 70
    d.box(14, 14 + i * 56, w, 46, t, s, k=k, d=i)
d.text(666, 40, 'léger', 's', anchor='end')
d.arrow([(660, 52), (660, 250)], color='a')
d.text(666, 280, 'lourd', 'at', anchor='end')
put(f'{M}/11-depanner.md', 'depannage', figure(d, 'Du retour en arrière le plus léger au plus lourd',
    "Monte d'un barreau seulement si le précédent n'a pas suffi."), before="## L'échelle des retours en arrière")

# --- 13: theme generation ----------------------------------------------
d = D(680, 300)
d.box(14, 110, 170, 70, 'colors.toml', 'la palette', k='c', d=0)
d.box(14, 200, 170, 50, 'modèles .tpl', '~/.config/omarchy/themed', k='ghost', d=1)
d.box(250, 120, 160, 60, 'changement de thème', 'génération', k='ok', d=2)
d.arrow([(184, 145), (248, 150)], color='c')
d.arrow([(184, 225), (250, 225), (330, 182)])
apps = ['foot, Alacritty, Ghostty', 'Hyprland (bordures)', 'shell (barre, menus)', 'Neovim, Helix, VS Code', 'btop, Chromium, Obsidian']
for i, t in enumerate(apps):
    y = 14 + i * 56
    d.box(486, y, 180, 44, t, k='', tk='s', d=3 + i)
    d.arrow([(410, 150), (450, 150), (450, y + 22), (484, y + 22)], color='ok')
put(f'{M}/13-les-themes.md', 'themes', figure(d, 'Une palette, toutes les applis',
    "Le thème décrit les couleurs une seule fois ; Omarchy génère la configuration de chaque appli."), before='Au lieu de régler')

# --- 14: the shell -------------------------------------------------------
d = D(680, 280)
d.zone(14, 14, 652, 70, 'avant la v4 : six outils, six configurations', k='')
for i, t in enumerate(['Waybar', 'Walker', 'Mako', 'SwayOSD', 'hyprlock', 'hypridle']):
    d.box(26 + i * 106, 40, 96, 34, t, k='ghost', tk='s', d=0)
d.box(200, 116, 280, 56, 'shell Quickshell', 'un processus, un fichier : shell.json', k='c', d=1)
d.arrow([(340, 84), (340, 114)], color='c')
parts = [('omarchy.*', 'plugins intégrés'), ('~/.config/omarchy/plugins', 'tes plugins (QML)'), ('omarchy bar …', 'réglages en ligne de commande')]
for i, (t, s) in enumerate(parts):
    x = 14 + i * 224
    d.box(x, 210, 204, 54, t, s, k='ok' if i == 1 else '', d=2 + i)
    d.arrow([(340, 172), (340, 190), (x + 102, 190), (x + 102, 208)], color='c')
put(f'{M}/14-la-barre-et-les-plugins.md', 'shell', figure(d, 'Un shell, des plugins',
    "Barre, lanceur, notifications et verrouillage sont désormais des plugins d'un seul programme."), before='Avant la version 4')
