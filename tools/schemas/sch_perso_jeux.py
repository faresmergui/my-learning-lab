from svg import D, figure
from inject import put

# ============================== YU-GI-OH! ==============================
M = 'yugioh'

# --- 01 : les zones du terrain ----------------------------------------
d = D(680, 300)
X = lambda c: 20 + c * 92
W = 74
d.box(X(2) - 46, 14, W, 66, 'Extra\nMonstre', k='a', tk='s', d=0)
d.box(X(4) - 46, 14, W, 66, 'Extra\nMonstre', k='a', tk='s', d=0)
d.text(X(3) - 9, 52, 'une par joueur', 's')
for c in range(1, 6):
    d.box(X(c), 96, W, 84, f'M{c}', 'monstre', k='c', d=1)
    d.box(X(c), 192, W, 84, f'S{c}', 'Pendule' if c in (1, 5) else 'magie/piège', d=2)
d.box(X(0), 96, W, 84, 'Terrain', tk='s', d=3)
d.box(X(0), 192, W, 84, 'Extra\nDeck', tk='s', d=3)
d.box(X(6), 14, W, 66, 'Bannies', tk='s', k='ghost', d=3)
d.box(X(6), 96, W, 84, 'Cime-\ntière', tk='s', d=3)
d.box(X(6), 192, W, 84, 'Deck', tk='s', d=3)
put(f'{M}/01-le-deroule-d-un-duel.md', 'zones', figure(d, 'Les zones du terrain', "Les monstres de l'Extra Deck vont dans une zone Monstre Extra, ou dans une zone pointée par un monstre Lien."), fence='[Extra Monstre]')

# --- 03 : construire puis résoudre une chaîne -------------------------
d = D(680, 230)
d.text(70, 24, 'on empile', 'zl')
d.arrow([(70, 190), (70, 40)], color='c')
d.box(130, 40, 300, 60, 'maillon 2 · toi', 'Ash Blossom : nie l\'effet', k='c', d=1)
d.box(130, 120, 300, 60, 'maillon 1 · adversaire', 'effet qui recherche une carte', d=0)
d.text(470, 24, 'on résout', 'zl')
d.arrow([(470, 40), (470, 190)], color='a')
d.box(500, 40, 166, 60, '1er à se résoudre', "l'effet du maillon 1\nest nié", k='a', d=2)
d.box(500, 120, 166, 60, '2e à se résoudre', 'ne fait rien', d=3)
d.text(340, 212, 'le dernier maillon ajouté se résout en premier', 'ct', d=4)
put(f'{M}/03-la-chaine-et-les-vitesses.md', 'chaine', figure(d, 'Une chaîne se résout à l\'envers', "C'est pour cela qu'une réponse peut nier un effet activé avant elle."), before='## Les vitesses de sort')

# --- 04 : la régularité ----------------------------------------------
d = D(680, 230)
d.text(14, 20, 'mains de départ (5 cartes, deck de 40) avec au moins un starter', 'zl', anchor='start')
for i, (n, p) in enumerate([(8, 70), (10, 78), (12, 85), (15, 92)]):
    y = 40 + i * 44
    d.text(120, y + 20, f'{n} starters', 't', anchor='end', d=i)
    d.box(140, y, p * 5, 30, '', k='c' if p < 85 else 'ok', rx=6, d=i)
    d.text(150 + p * 5, y + 20, f'≈ {p} %', 'ct', anchor='start', d=i)
put(f'{M}/04-construire-un-deck.md', 'regularite', figure(d, 'Plus de starters, des mains plus régulières', 'Passer de 8 à 12 starters fait gagner environ une main sur sept.'), before='Si le chiffre est trop bas')

# =============================== VALORANT ==============================
M = 'valorant'

# --- 01 : le rythme d'une manche --------------------------------------
d = D(680, 190)
d.text(74, 46, '30 s', 's'); d.text(299, 46, '1 min 40', 's'); d.text(564, 46, '45 s', 's')
d.box(14, 56, 120, 42, "phase d'achat", tk='s', d=0)
d.box(134, 56, 330, 42, "phase d'action", k='c', d=1)
d.box(464, 56, 200, 42, 'spike posé', k='a', d=2)
d.circle(464, 77, 9, k='a', d=2)
d.text(464, 30, 'pose (4 s)', 'at', d=2)
d.text(299, 124, 'sans pose, le temps joue pour la défense', 'ct', d=1)
d.text(564, 144, "le temps joue pour l'attaque", 'at', d=2)
d.text(564, 162, 'désamorçage : 7 s (palier à 3,5 s)', 's', d=3)
put(f'{M}/01-le-deroule-d-une-partie.md', 'rythme', figure(d, "Le rythme d'une manche", "La pose du spike inverse le chronomètre : c'est alors à la défense de se dépêcher."), before='Le chronomètre change donc de sens')

# --- 03 : les trois premières manches ---------------------------------
d = D(680, 250)
for c, t in enumerate(['manche 1', 'manche 2', 'manche 3']):
    d.text(220 + c * 160, 24, t, 'zl')
rows = [("perd la manche\npistolet", [('800', 'pistolet, armure légère', ''), ('≈ 2 000', 'éco : on sauve', 'ghost'), ('≈ 4 400', 'achat complet', 'ok')]),
        ("gagne la manche\npistolet", [('800', 'pistolet, armure légère', ''), ('≈ 3 000 à 3 800', 'SMG + armure', 'c'), ('garde ses armes', 'si elle gagne encore', 'c')])]
for r, (lab, cells) in enumerate(rows):
    y = 44 + r * 100
    d.text(70, y + 30, lab, 't', d=r)
    for c, (t, s, k) in enumerate(cells):
        x = 150 + c * 160
        d.box(x, y, 140, 64, t, s, k=k, d=r * 3 + c)
        if c:
            d.arrow([(x - 18, y + 32), (x - 2, y + 32)], color='c')
d.text(380, 240, 'bonus de défaite : 1 900, puis 2 400 · victoire : 3 000', 's', d=6)
put(f'{M}/03-l-economie.md', 'debut', figure(d, 'Les trois premières manches', "L'équipe qui perd la manche pistolet sauve en manche 2 pour tout acheter en manche 3."), before="À l'inverse, l'équipe qui gagne")

# --- 08 : la défense en 2-1-2 -----------------------------------------
d = D(680, 330)
d.box(270, 14, 140, 34, 'spawn défense', tk='s', d=0)
d.zone(24, 80, 230, 150, 'site A')
d.zone(426, 80, 230, 150, 'site B')
d.zone(290, 104, 100, 100, 'mid', k='c')
d.box(270, 282, 140, 34, 'spawn attaque', k='ghost', tk='s', d=0)
for (x1, y1), (x2, y2) in [((300, 282), (140, 232)), ((340, 282), (340, 206)), ((380, 282), (540, 232))]:
    d.arrow([(x1, y1), (x2, y2)], k='dash')
d.text(196, 262, 'main A', 's'); d.text(484, 262, 'main B', 's')
for i, (x, y, t) in enumerate([(90, 160, 'anchor'), (190, 130, ''), (340, 160, ''), (490, 130, ''), (590, 160, 'anchor')]):
    d.circle(x, y, 11, k='c', d=1 + i)
    if t:
        d.text(x, y + 30, t, 's', d=1 + i)
d.arrow('M196 146 C 250 240, 430 240, 484 146', color='a', k='dash', start=True)
d.text(340, 244, 'rotation', 'at')
put(f'{M}/08-defendre-et-reprendre-un-site.md', 'repartition', figure(d, 'La défense en 2-1-2', "Chaque site garde un anchor ; les autres tournent quand l'information est sûre."), before='Deux types de défenseurs')

# --- 07 : l'après-pose en tir croisé ----------------------------------
d = D(680, 300)
d.zone(110, 20, 460, 250, 'site après la pose')
d.raw('<path d="M340 128 L354 142 L340 156 L326 142 Z" class="dg-dot dg-a dg-pop" style="--d:0"/>')
d.text(340, 178, 'spike', 'at')
d.box(176, 78, 64, 30, 'caisse', tk='s', d=1)
d.box(500, 220, 64, 30, 'caisse', tk='s', d=1)
d.circle(208, 126, 11, k='c', d=2)
d.circle(480, 222, 11, k='c', d=2)
d.line(208, 126, 336, 140, k='l c dash')
d.line(480, 222, 344, 146, k='l c dash')
d.text(208, 156, 'attaquant 1', 's')
d.text(470, 252, 'attaquant 2', 's', anchor='end')
d.circle(610, 60, 11, k='a', d=3)
d.arrow([(598, 68), (362, 136)], color='a', d=3)
d.text(620, 40, 'défenseur', 'at', anchor='end')
d.text(340, 286, 'deux angles sur le spike : le défenseur ne peut pas surveiller les deux', 's', d=4)
put(f'{M}/07-attaquer-un-site.md', 'apres-pose', figure(d, "L'après-pose en tir croisé", "Les attaquants ne restent pas sur le spike : ils le surveillent de deux angles, à couvert."), before='> **À retenir.**')
print('ok')
