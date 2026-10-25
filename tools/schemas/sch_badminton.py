from svg import D, figure
from inject import put

M = 'badminton'
L, W = 13.4, 6.1
NET = L / 2
SSL = 1.98      # short service line, from the net
LSD = 0.76      # doubles long service line, from the back
SIDE = 0.46     # side alley


def court(d, x0, y0, s, labels=False):
    """Court seen from above, net vertical in the middle."""
    X = lambda m: round(x0 + m * s, 1)
    Y = lambda m: round(y0 + m * s, 1)
    d.rect(X(0), Y(0), L * s, W * s, k='floor', rx=2)
    d.raw(f'<rect x="{X(0)}" y="{Y(0)}" width="{L * s}" height="{W * s}" class="dg-court"/>')
    for y in (SIDE, W - SIDE):
        d.line(X(0), Y(y), X(L), Y(y), k='court')
    for x in (NET - SSL, NET + SSL, LSD, L - LSD):
        d.line(X(x), Y(0), X(x), Y(W), k='court')
    d.line(X(0), Y(W / 2), X(NET - SSL), Y(W / 2), k='court')
    d.line(X(NET + SSL), Y(W / 2), X(L), Y(W / 2), k='court')
    d.line(X(NET), Y(-0.25), X(NET), Y(W + 0.25), k='net')
    return X, Y


# --- 1. The court and its lines --------------------------------------
d = D(680, 330)
X, Y = court(d, 40, 40, 40)
d.text(X(NET), Y(0) - 14, 'filet · 1,55 m', 's')
d.arrow([(X(0), Y(W) + 26), (X(L), Y(W) + 26)], start=True)
d.text(X(L / 2), Y(W) + 44, '13,40 m', 's')
d.arrow([(X(L) + 22, Y(0)), (X(L) + 22, Y(W))], start=True)
d.text(X(L) + 30, Y(W / 2) - 6, '6,10 m', 's', anchor='start')
d.text(X(L) + 30, Y(W / 2) + 10, 'en double', 's', anchor='start')
# numbered markers
marks = [
    (NET - SSL, 1.4, '1'), (LSD, 1.4, '2'), (4.0, SIDE / 2, '3'), (2.2, W / 2, '4'),
]
for i, (mx, my, n) in enumerate(marks):
    d.circle(X(mx), Y(my), 10, k='c', d=i)
    d.text(X(mx), Y(my) + 4, n, 'w', d=i)
legend = ['1  ligne de service court, à 1,98 m du filet',
          '2  ligne de service long en double, à 76 cm du fond',
          '3  couloir latéral : hors jeu en simple, en jeu en double',
          '4  ligne médiane : sépare zone droite et zone gauche']
for i, l in enumerate(legend):
    d.text(X(NET) + 24 if i > 1 else X(0) + 4, Y(W) + 66 + (i % 2) * 18, l, 's', anchor='start')
d.h = 390
put(f'{M}/01-regles-et-score.md', 'terrain', figure(d, 'Le terrain de badminton vu de dessus', 'Le terrain vu de dessus. Une ligne touchée par le volant fait partie du terrain.'), before='## Le service')

# --- 2. Singles / doubles service areas ------------------------------
d = D(680, 230)
for i, (title, x0, single) in enumerate([('simple : long et étroit', 20, True), ('double : court et large', 360, False)]):
    s = 22.5
    X, Y = court(d, x0, 40, s)
    # receiving area (diagonal from the server, placed bottom left)
    rx0, rx1 = NET + SSL, (L if single else L - LSD)
    ry0, ry1 = (SIDE if single else 0), W / 2
    d.raw(f'<rect x="{X(rx0)}" y="{Y(ry0)}" width="{round((rx1 - rx0) * s, 1)}" height="{round((ry1 - ry0) * s, 1)}" class="dg-fillA"/>')
    d.circle(X(2.5), Y(W * 0.72), 7, k='c', d=i)
    d.arrow(f'M{X(2.7)} {Y(W * 0.70)} Q {X(7)} {Y(W * 0.2)} {X((rx0 + rx1) / 2)} {Y((ry0 + ry1) / 2)}', color='a', draw=True, d=i + 1)
    d.text(X(L / 2), 24, title, 't')
    d.text(X(L / 2), Y(W) + 22, 'serveur (point pair) → zone de réception en rouge', 's')
put(f'{M}/01-regles-et-score.md', 'zones-service', figure(d, 'Zones de service en simple et en double', 'Le service part en diagonale. En double, le fond de court est interdit, les couloirs latéraux sont autorisés.'), before='> **À retenir.**')

# --- Side view: trajectories ---------------------------------------
def side(d, x0, ground, sx, sy, xmin=0.0, xmax=L, hmax=8):
    X = lambda m: round(x0 + (m - xmin) * sx, 1)
    Yh = lambda h: round(ground - h * sy, 1)
    d.rect(X(xmin), ground, (xmax - xmin) * sx, 5, k='floor')
    d.line(X(xmin), ground, X(xmax), ground, k='court')
    if xmin <= NET <= xmax:
        d.line(X(NET), ground, X(NET), Yh(1.55), k='net')
        d.circle(X(NET), Yh(1.55), 3, k='')
    return X, Yh


d = D(680, 280)
X, Yh = side(d, 30, 230, 46, 24)
for xm, lab in ((NET - SSL, 'service court'), (NET + SSL, 'service court')):
    d.line(X(xm), 230, X(xm), 238, k='court')
d.text(X(1.2), 254, 'toi, au fond du court', 's')
d.text(X(11.5), 254, 'adversaire', 's')
paths = [
    ('dégagement défensif', 'c', f'M{X(1.2)} {Yh(2.7)} C {X(4)} {Yh(10)}, {X(10.5)} {Yh(8.5)}, {X(12.9)} {Yh(0)}', (5.2, 7.75)),
    ("dégagement d'attaque", 'c', f'M{X(1.2)} {Yh(2.7)} C {X(4)} {Yh(5.2)}, {X(9.5)} {Yh(5)}, {X(12.6)} {Yh(0)}', (5.2, 4.95)),
    ('smash', 'a', f'M{X(1.2)} {Yh(2.7)} Q {X(6)} {Yh(2.75)} {X(10.6)} {Yh(0)}', (9.0, 1.45)),
    ('amorti', 'ok', f'M{X(1.2)} {Yh(2.7)} C {X(4)} {Yh(3.4)}, {X(6.3)} {Yh(2.6)}, {X(7.6)} {Yh(0)}', (7.7, 2.3)),
]
for i, (lab, col, p, (lx, ly)) in enumerate(paths):
    d.arrow(p, color=col, k='thick', draw=True, d=i * 2)
    d.text(X(lx), Yh(ly), lab, {'c': 'ct', 'a': 'at', 'ok': 'okt'}[col], anchor='middle' if col == 'c' else 'start', d=i * 2 + 1)
d.circle(X(1.2), Yh(2.7), 5, k='c')
put(f'{M}/04-degagement-et-smash.md', 'trajectoires', figure(d, 'Trajectoires des coups de fond de court, vue de côté', 'Même préparation, quatre trajectoires. L\'adversaire ne doit pas savoir laquelle arrive.'), before='## Le smash, en trois points')

# --- Slow / fast drop shot ---------------------------------------------
d = D(680, 230)
X, Yh = side(d, 30, 190, 46, 26)
d.line(X(NET + SSL), 190, X(NET + SSL), 198, k='court')
d.text(X(NET + SSL), 214, 'ligne de service court', 's')
d.raw(f'<rect x="{X(NET)}" y="186" width="{round(SSL * 46, 1)}" height="4" class="dg-fillOk"/>')
d.arrow(f'M{X(1.2)} {Yh(2.7)} C {X(4)} {Yh(3.6)}, {X(6.2)} {Yh(2.7)}, {X(7.3)} {Yh(0)}', color='ok', k='thick', draw=True, d=0)
d.text(X(4.2), Yh(3.55), 'amorti lent : tombe près du filet', 'okt', d=1)
d.arrow(f'M{X(1.2)} {Yh(2.7)} Q {X(6)} {Yh(2.2)} {X(8.3)} {Yh(0)}', color='a', k='thick', draw=True, d=2)
d.text(X(8.6), Yh(1.2), 'amorti rapide : tendu, arrive vite', 'at', anchor='start', d=3)
d.circle(X(1.2), Yh(2.7), 5, k='c')
put(f'{M}/04-amorti.md', 'amortis', figure(d, 'Amorti lent et amorti rapide, vue de côté', 'Les deux doivent tomber avant la ligne de service court (zone verte).'), before='## Les clés techniques')

# --- Net play: three heights ------------------------------------
d = D(680, 290)
X, Yh = side(d, 20, 250, 92, 62, xmin=3.4, xmax=10.5, hmax=3.4)
d.text(X(9.3), 272, 'toi, au filet', 's')
d.text(X(4.4), 272, 'adversaire', 's')
d.raw(f'<rect x="{X(6.85)}" y="{Yh(3.3)}" width="{round(3.5 * 92, 1)}" height="{round((3.3 - 1.75) * 62, 1)}" class="dg-fillA" rx="6"/>')
d.raw(f'<rect x="{X(6.85)}" y="{Yh(1.75)}" width="{round(3.5 * 92, 1)}" height="{round(0.35 * 62, 1)}" class="dg-fill" rx="4"/>')
d.raw(f'<rect x="{X(6.85)}" y="{Yh(1.4)}" width="{round(3.5 * 92, 1)}" height="{round(1.3 * 62, 1)}" class="dg-fillOk" rx="6"/>')
d.text(X(10.4), Yh(3.05), 'au-dessus de la bande', 's', anchor='end')
d.text(X(10.4), Yh(1.5), 'au niveau de la bande', 's', anchor='end')
d.text(X(10.4), Yh(0.35), 'sous la bande', 's', anchor='end')
d.arrow(f'M{X(7.2)} {Yh(2.6)} L {X(5.6)} {Yh(0)}', color='a', k='thick', draw=True, d=0)
d.text(X(5.75), Yh(1.55), 'kill', 'at', anchor='end', d=1)
d.arrow(f'M{X(7.2)} {Yh(1.55)} Q {X(6.75)} {Yh(2.9)} {X(6.3)} {Yh(0)}', color='c', k='thick', draw=True, d=2)
d.text(X(6.1), Yh(0.6), 'filet serré', 'ct', anchor='end', d=3)
d.arrow(f'M{X(7.3)} {Yh(0.7)} C {X(6.6)} {Yh(4)}, {X(5)} {Yh(4.4)}, {X(3.45)} {Yh(3.6)}', color='ok', k='thick', draw=True, d=4)
d.text(X(3.6), Yh(3.15), 'lift, vers le fond', 'okt', anchor='start', d=5)
put(f'{M}/05-jeu-au-filet.md', 'hauteurs', figure(d, 'Les trois options au filet selon la hauteur du volant', 'Plus tu prends le volant haut, plus tu as d\'options.'), before='## Les clés techniques')

# --- Footwork: the star ------------------------------------------
d = D(680, 300)
s = 40
X, Y = court(d, 70, 30, s)
cx, cy = 3.6, W / 2
corners = [(5.9, 0.6, 'avant gauche'), (5.9, W - 0.6, 'avant droit'), (3.6, 0.55, 'côté gauche'),
           (3.6, W - 0.55, 'côté droit'), (0.9, 0.7, 'fond gauche'), (0.9, W - 0.7, 'fond droit')]
for i, (x, y, lab) in enumerate(corners):
    d.arrow([(X(cx), Y(cy)), (X(x), Y(y))], color='c', k='thick', draw=True, d=i)
    d.circle(X(x), Y(y), 5, k='c', d=i)
d.circle(X(cx), Y(cy), 11, k='a', d=0)
d.text(X(cx), Y(cy) + 30, 'base', 'at')
d.text(X(NET + 3.3), Y(1.2), '1. split step quand', 's')
d.text(X(NET + 3.3), Y(1.2) + 15, "l'adversaire frappe", 's')
d.text(X(NET + 3.3), Y(2.6), '2. départ vers le coin', 's')
d.text(X(NET + 3.3), Y(3.6), '3. frappe en équilibre', 's')
d.text(X(NET + 3.3), Y(4.6), '4. retour à la base', 's')
put(f'{M}/06-deplacements.md', 'etoile', figure(d, 'Les six directions de déplacement depuis la base', 'Le shadow en étoile : chaque coin, puis retour à la base, à chaque fois.'), before="## Les appuis clés")

# --- Grips: base position ----------------------------------------
d = D(680, 300)
s = 40
X, Y = court(d, 70, 30, s)
d.raw(f'<ellipse cx="{X(3.9)}" cy="{Y(W / 2)}" rx="{1.3 * s}" ry="{1.1 * s}" class="dg-fill"/>')
d.circle(X(3.9), Y(W / 2), 10, k='c', d=0)
d.text(X(3.9), Y(W / 2) + 34, 'position d\'attente', 'ct', d=1)
d.text(X(3.9), Y(W / 2) + 49, 'un peu en arrière du milieu', 's', d=1)
d.text(X(NET + 3.35), Y(W / 2) - 6, 'distances à peu près égales', 's')
d.text(X(NET + 3.35), Y(W / 2) + 10, 'vers le filet et vers le fond', 's')
for i, (x, y) in enumerate([(6.3, 0.5), (6.3, W - 0.5), (0.4, 0.5), (0.4, W - 0.5)]):
    d.arrow([(X(3.9), Y(W / 2)), (X(x), Y(y))], k='dash', d=i + 1)
put(f'{M}/02-prises-et-placement.md', 'base', figure(d, 'Position d\'attente en simple', 'Depuis la base, les quatre coins sont à distance comparable.'), before='## Exercice')

# --- Singles tactics: the four corners -------------------------------
d = D(680, 330)
s = 40
X, Y = court(d, 70, 40, s)
for (x0, x1, y0, y1, lab, ly) in [(NET, NET + SSL + 0.6, 0, W / 2, 'avant droit', 0.45), (NET, NET + SSL + 0.6, W / 2, W, 'avant gauche', W - 0.3),
                                  (L - 2.4, L, 0, W / 2, 'fond droit', 0.45), (L - 2.4, L, W / 2, W, 'fond gauche', W - 0.3)]:
    d.raw(f'<rect x="{X(x0)}" y="{Y(y0)}" width="{round((x1 - x0) * s, 1)}" height="{round((y1 - y0) * s, 1)}" class="dg-fill"/>')
    d.text(X((x0 + x1) / 2), Y(ly) + 4, lab, 's')
d.text(X(NET + (L - NET) / 2), Y(0) - 10, 'côtés vus par l\'adversaire', 's')
d.circle(X(2.4), Y(W * 0.7), 8, k='a')
d.text(X(2.4), Y(W * 0.7) + 26, 'toi', 'at')
d.arrow(f'M{X(2.6)} {Y(W * 0.68)} Q {X(7.5)} {Y(W * 0.6)} {X(L - 1.1)} {Y(1.4)}', color='c', k='thick', draw=True, d=0)
d.text(X(4.3), Y(2.5), '1. dégagement croisé', 'ct', d=1)
d.arrow(f'M{X(L - 1.2)} {Y(1.5)} Q {X(9)} {Y(2.0)} {X(3.2)} {Y(W * 0.62)}', k='dash', d=2)
d.arrow(f'M{X(3.0)} {Y(W * 0.66)} Q {X(6.2)} {Y(W * 0.85)} {X(NET + 1.2)} {Y(W - 0.9)}', color='a', k='thick', draw=True, d=4)
d.text(X(NET + 1.4), Y(W) + 20, '2. amorti en ligne, dans le coin opposé', 'at', d=5)
put(f'{M}/09-tactique-simple.md', 'coins', figure(d, 'Les quatre coins et un enchaînement type', 'Fond croisé, puis avant opposé : l\'adversaire traverse tout le terrain.'), before="## Lire l'adversaire")

# --- Doubles tactics: formations -------------------------------------
d = D(680, 240)
for i, (title, x0, pos, note) in enumerate([
        ('attaque : avant-arrière', 20, [(NET - 1.4, W / 2), (2.0, W / 2)], 'ton équipe frappe vers le bas'),
        ('défense : côte à côte', 360, [(3.6, 1.6), (3.6, W - 1.6)], 'ton équipe a levé le volant')]):
    s = 22.5
    X, Y = court(d, x0, 40, s)
    for j, (x, y) in enumerate(pos):
        d.circle(X(x), Y(y), 8, k='c', d=i * 2 + j)
    d.text(X(L / 2), 26, title, 't')
    d.text(X(L / 2), Y(W) + 22, note, 's')
    if i == 0:
        d.arrow(f'M{X(2.2)} {Y(W / 2) - 4} L {X(9.8)} {Y(1.8)}', color='a', k='thick', draw=True, d=3)
    else:
        d.arrow(f'M{X(11.5)} {Y(1.2)} L {X(4)} {Y(1.75)}', color='a', k='thick', draw=True, d=3)
put(f'{M}/10-tactique-double.md', 'formations', figure(d, 'Les deux formations en double', 'On change de formation selon le dernier coup de son équipe.'), before='## Le service et le retour')
print('badminton ok')
