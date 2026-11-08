from svg import D, figure
from inject import put

M = 'yugioh'

# --- 23: the three card families around the Normal monster ---------
d = D(680, 330)
d.box(250, 96, 180, 86, 'Dragon Blanc', 'monstre Normal\nNiv. 8, 3000 ATK', k='c', d=0)
d.zone(14, 40, 200, 196, 'lanceurs', k='a')
for i, (t, s) in enumerate([('Sage', 'cherche un Syntoniseur'), ('Maiden of White', 'pose True Light'), ('Kaibaman', 'invoque un Dragon Blanc')]):
    d.box(28, 66 + i * 56, 172, 46, t, s, k='a', d=1 + i)
d.zone(466, 40, 200, 196, 'payoffs (Extra Deck)', k='ok')
for i, (t, s) in enumerate([('Spirit Dragon', 'Synchro Niv. 9'), ('Ultimate Spirit', 'négation sur le terrain'), ('Magia', 'Fusion, 3 négations')]):
    d.box(480, 66 + i * 56, 172, 46, t, s, k='ok', d=4 + i)
d.box(150, 262, 380, 54, 'soutien qui mentionne le Dragon Blanc', 'Vœux, True Light, Roar, Ultimate Fusion, Majesty', d=7)
d.arrow([(214, 139), (248, 139)], color='a')
d.arrow([(430, 139), (464, 139)], color='c')
d.arrow([(340, 260), (340, 184)])
d.text(340, 26, 'tout le deck sert à poser, recycler ou transformer un monstre sans effet', 's')
put(f'{M}/24-l-identite-blue-eyes.md', 'be-familles', figure(d, 'Les trois familles de cartes Blue-Eyes',
    'Les lanceurs amènent le Dragon Blanc, le soutien le pose et le recycle, l\'Extra Deck le transforme en terrain final.'))

# --- 24: roles along a game ----------------------------------------
d = D(680, 300)
steps = [
    ('starter', 'Vœux, Maiden, Sage', 'a'),
    ('Dragon Blanc', 'Kaibaman, True Light, Roar', 'c'),
    ('fin de combo', 'Spirit Dragon, Magia', 'ok'),
]
for i, (t, s, k) in enumerate(steps):
    d.box(14 + i * 226, 40, 200, 60, t, s, k=k, d=i)
    if i:
        d.arrow([(14 + i * 226 - 24, 70), (14 + i * 226 - 2, 70)])
d.text(14, 26, 'en premier : une ligne', 's', anchor='start')
d.zone(14, 130, 318, 156, 'en second : nettoyer', k='c')
d.box(30, 160, 286, 40, 'Ultimate Fusion', 'détruit selon les matériels du terrain', k='c', d=3)
d.box(30, 210, 286, 40, 'Majesty', 'jusqu\'à 3 cartes détruites', k='c', d=4)
d.text(173, 274, 'puis 3000 ATK et plus pour finir', 's')
d.zone(348, 130, 318, 156, 'ce qui te coupe', k='a')
d.box(364, 160, 286, 40, 'Ash Blossom, Veiler', 'sur les recherches et les invocations', k='a', d=5)
d.box(364, 210, 286, 40, 'Ghost Belle, D.D. Crow', 'sur le cimetière', k='a', d=6)
d.text(507, 274, 'garde toujours une seconde source', 's')
put(f'{M}/25-les-cartes-blue-eyes.md', 'be-roles', figure(d, 'Le rôle des cartes Blue-Eyes',
    'Chaque carte a une place dans la partie : lancer, poser le Dragon Blanc, finir, ou nettoyer en second.'))

# --- 26: the ten-step base line ------------------------------------
d = D(680, 360)
line = [
    ('1 Maiden', 'pose True Light'), ('2 True Light', 'pose Vœux'), ('3 Vœux', 'Kaibaman + Roar'),
    ('4 Kaibaman', 'Dragon Blanc du deck'), ('5 Maiden', 'revient du cimetière'),
    ('10 Synchro', '2e Spirit Dragon'), ('9 Kaibaman', 'cherche un Blue-Eyes'), ('8 Roar', 'Dragon Blanc\ndu cimetière'),
    ('7 Synchro', 'Spirit Dragon'), ('6 Vœux', 'équipe Ultimate\nDragon'),
]
W, G = 120, 14
for i, (t, s) in enumerate(line):
    row, col = divmod(i, 5)
    x = 14 + col * (W + G)
    y = 40 + row * 110
    k = 'ok' if t.endswith('Synchro') or 'Synchro' in t else ('a' if row == 0 else 'c')
    d.box(x, y, W, 58, t, s, k=k, d=i if row == 0 else 14 - i)
for col in range(4):
    x = 14 + col * (W + G) + W
    d.arrow([(x + 1, 69), (x + G - 1, 69)])
    d.arrow([(x + G - 1, 179), (x + 1, 179)])
xr = 14 + 4 * (W + G) + W / 2
d.arrow([(xr, 99), (xr, 149)])
d.text(14, 26, 'chaque effet une fois, dans l\'ordre qui en déclenche le plus', 's', anchor='start')
d.box(140, 262, 400, 70, 'terrain final', '2 Spirit Dragon + True Light\nen main : la carte cherchée par Kaibaman', k='ok', d=12)
d.arrow([(74, 209), (74, 297), (138, 297)], color='ok')
put(f'{M}/28-les-lignes-de-jeu-blue-eyes.md', 'be-ligne', figure(d, 'La ligne de base Maiden of White + 1 carte',
    'Les étapes du tableau ci-dessous, dans l\'ordre. Les points de rupture principaux sont les étapes 3, 4 et 5.'))

# --- 23: Millennium Ankh engine ------------------------------------
d = D(680, 336)
d.box(14, 40, 200, 70, '5 pièces montrées', 'main, deck ou terrain\njamais au cimetière', d=0)
d.box(250, 40, 180, 70, 'Ânkh Millénaire', 'invoque l\'Incarné\npuis retourne au deck', k='a', d=1)
d.box(466, 40, 200, 70, "L'Incarné", 'nie 1 Magie ou Piège par tour\nATK = tes LP en combat', k='c', d=2)
d.arrow([(214, 75), (248, 75)])
d.arrow([(430, 75), (464, 75)], color='c')
d.zone(14, 146, 416, 150, 'zone Magie et Piège (Magies Continues)', k='a')
for i, (t, s) in enumerate([('Bouclier', 'cherche l\'Ânkh'), ('Sengenjin', 'cherche un Millénaire'), ('Golem', 'Ânkh non niable')]):
    d.box(28 + i * 136, 178, 124, 50, t, s, k='a', d=3 + i)
d.text(222, 256, "invocation : payer 2000 LP ou révéler l'Ânkh", 's')
d.text(222, 276, 'Temple Wedju en place deux d\'un coup', 's')
d.arrow([(90, 176), (90, 140), (300, 140), (300, 112)], color='a', label='cherche', at=0.6)
d.box(466, 178, 200, 70, 'End Phase', 'pose Feux de la Rage Exxod :\ntoutes les cartes adverses', k='ok', d=6)
d.arrow([(566, 110), (566, 176)], color='ok')
d.text(340, 324, "l'Ânkh en dernier : après lui, plus aucune invocation ce tour", 's')
put(f'{M}/23-exodia-millenaire.md', 'exodia-ankh', figure(d, "Le moteur d'Exodia Millénaire",
    "Les monstres Millénaire sortent de la zone Magie et Piège et cherchent l'Ânkh, qui montre les pièces restées dans le deck."),
    before='## Les cartes et leurs rôles')

# --- 26: how Primite feeds Blue-Eyes -------------------------------
d = D(680, 330)
d.box(14, 40, 200, 56, 'Béryl Éthérique', 'invoqué : pose Filon Noble', k='a', d=0)
d.box(240, 40, 200, 56, 'Filon Noble', 'cherche Rayon de Forage', k='a', d=1)
d.box(466, 40, 200, 56, 'Rayon de Forage', 'nie et bannit', k='ok', d=2)
d.box(14, 160, 200, 56, 'Esprit avec des\nYeux de Bleu', 'Lien 1', d=3)
d.box(240, 160, 200, 56, 'Dragon Blanc', 'monstre Normal', k='c', d=4)
d.box(466, 160, 200, 56, 'Maiden revient', 'Kaibaman cherche', k='c', d=5)
d.box(14, 260, 200, 56, 'Mausolée Blanc', '2e invocation normale', d=6)
d.arrow([(214, 68), (238, 68)])
d.arrow([(440, 68), (464, 68)])
d.arrow([(114, 96), (114, 158)], label='Lien', dy=4)
d.arrow([(300, 96), (300, 158)], color='c', label='invoque, en dernier', dy=4)
d.arrow([(440, 188), (464, 188)], color='c')
d.arrow([(400, 158), (400, 128), (600, 128), (600, 98)], color='ok', label='gratuit s\'il est en jeu', at=0.5)
d.arrow([(114, 216), (114, 258)], label='cherche', dy=4)
d.text(450, 270, 'verrou de Filon Noble : plus d\'effets de monstres', 's')
d.text(450, 288, 'invoqués spécialement ce tour, donc en dernier', 's')
put(f'{M}/26-blue-eyes-primite.md', 'primite', figure(d, 'Ce que Primite apporte à Blue-Eyes',
    'Le moteur invoque le Dragon Blanc, qui déclenche Maiden et Kaibaman et rend Rayon de Forage gratuit.'),
    before='## Le prix : deux verrous')
