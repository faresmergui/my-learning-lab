from svg import D, figure
from inject import put

M = 'finance'


def axes(d, x0, y0, x1, y1, ymax, ystep, yfmt, xmax, xstep, xlabel):
    """Chart grid and ticks: (x0, y0) top left, (x1, y1) bottom right."""
    for v in range(0, ymax + 1, ystep):
        y = y1 - (y1 - y0) * v / ymax
        d.line(x0, y, x1, y)
        d.text(x0 - 8, y + 4, yfmt(v), 's', anchor='end')
    for v in range(0, xmax + 1, xstep):
        x = x0 + (x1 - x0) * v / xmax
        d.text(x, y1 + 18, str(v), 's')
    d.text((x0 + x1) / 2, y1 + 36, xlabel, 's')


def curve(d, x0, y0, x1, y1, ymax, xmax, f, color, k='thick'):
    pts = [(x0 + (x1 - x0) * t / xmax, y1 - (y1 - y0) * f(t) / ymax) for t in range(xmax + 1)]
    d.arrow(pts, color=color, k=k, end=False, draw=True)
    return pts[-1]


# --- 03: compound interest ------------------------------------------
d = D(680, 320)
X0, Y0, X1, Y1 = 80, 30, 560, 250
axes(d, X0, Y0, X1, Y1, 250000, 50000, lambda v: f'{v // 1000} k€', 30, 5, 'années')
r = 0.07 / 12
total = lambda t: 200 * ((1 + r) ** (12 * t) - 1) / r
e = curve(d, X0, Y0, X1, Y1, 250000, 30, total, 'c')
d.text(e[0] + 8, e[1] + 4, '244 k€', 'ct', anchor='start')
e = curve(d, X0, Y0, X1, Y1, 250000, 30, lambda t: 200 * 12 * t, '', k='dash')
d.text(e[0] + 8, e[1] + 4, '72 k€ versés', 's', anchor='start')
d.text(X0 + 20, Y0 + 14, '200 € par mois à 7 % par an', 'tl', anchor='start')
put(f'{M}/03-interets-composes-et-inflation.md', 'composes', figure(d, 'Les intérêts composés',
    "La courbe pleine est le capital, la droite en tirets ce que tu as versé. Après 30 ans, plus des deux tiers du capital sont des intérêts : l'écart se creuse surtout à la fin."),
    before='### La règle de 72')

# --- 08: the effect of fees ------------------------------------------
d = D(680, 320)
X0, Y0, X1, Y1 = 80, 30, 540, 250
axes(d, X0, Y0, X1, Y1, 80000, 20000, lambda v: f'{v // 1000} k€', 30, 5, 'années')
for fee, color, k, label in [(0.002, 'c', 'thick', '0,2 % : 72 k€'), (0.01, 'ok', 'thick', '1 % : 57 k€'),
                             (0.02, 'a', 'thick', '2 % : 43 k€'), (0.03, '', 'thick', '3 % : 32 k€')]:
    e = curve(d, X0, Y0, X1, Y1, 80000, 30, lambda t, fee=fee: 10000 * (1.07 - fee) ** t, color, k)
    d.text(e[0] + 8, e[1] + 4, label, 's', anchor='start')
d.text(X0 + 20, Y0 + 14, '10 000 € placés à 7 % brut, selon les frais annuels', 'tl', anchor='start')
put(f'{M}/08-les-frais.md', 'frais', figure(d, "L'effet des frais sur 30 ans",
    "Même placement, même marché : seuls les frais changent. Passer de 0,2 % à 2 % de frais par an coûte presque 30 000 € sur 10 000 € investis."),
    before='## Les différents frais')

# --- 18: order of priorities --------------------------------------
d = D(680, 300)
steps = [('Budget', 'dettes chères'), ('Précaution', '3 à 6 mois'), ('Abondement', 'employeur'),
         ('Projets courts', 'placements sûrs'), ('Long terme', 'PEA, AV, PER'), ('Optimiser', 'locatif, transmission')]
w, h = 104, 46
for i, (t, s) in enumerate(steps):
    x = 16 + i * 110
    y = 230 - i * 36
    d.box(x, y, w, h, t, sub=s, k='c' if i < 3 else 'a', d=i)
    if i:
        d.rect(x, y + h, w, 230 + h - y - h, k='fill')
d.text(20, 24, 'Chaque marche repose sur la précédente', 'tl', anchor='start')
put(f'{M}/18-construire-son-plan-financier.md', 'priorites', figure(d, "L'ordre des priorités",
    "Les trois premières marches protègent et rapportent sans risque ; les suivantes font travailler l'argent. Sauter une marche fragilise tout le reste."),
    before='## Fixer des objectifs chiffrés')
