import math
from svg import D, figure
from inject import put

M = 'piano'
WHITE = ['do', 'ré', 'mi', 'fa', 'sol', 'la', 'si']
BLACK_AFTER = {0: 'do♯', 1: 'ré♯', 3: 'fa♯', 4: 'sol♯', 5: 'la♯'}


def keyboard(d, x, y, n, ww=40, wh=150, on=(), on_black=(), names=True, blabels=None, start=0):
    """Clavier de n touches blanches à partir de do (start : décalage, 6 = partir du si). on : indices des blanches
    surlignées ; on_black : indices (de la blanche de gauche) des noires surlignées."""
    bw, bh = ww * 0.6, wh * 0.62
    for i in range(n):
        cls = 'dg-kw on' if i in on else 'dg-kw'
        d.raw(f'<rect x="{x + i * ww}" y="{y}" width="{ww}" height="{wh}" rx="3" class="{cls}"/>')
        if names:
            d.text(x + i * ww + ww / 2, y + wh - 12, WHITE[(i + start) % 7], 'ct' if i in on else 's')
    for i in range(n - 1):
        if (i + start) % 7 in BLACK_AFTER:
            cls = 'dg-kb on' if i in on_black else 'dg-kb'
            bx = x + (i + 1) * ww - bw / 2
            d.raw(f'<rect x="{bx}" y="{y}" width="{bw}" height="{bh}" rx="2" class="{cls}"/>')
            if blabels and i in blabels:
                d.text(bx + bw / 2, y + bh - 10, blabels[i], 'kbt')
    return d


# --- 01 : le clavier ----------------------------------------------------
d = D(680, 280)
keyboard(d, 60, 40, 14, on=(0, 7, 3, 10), blabels={0: 'do♯', 1: 'ré♯', 3: 'fa♯', 4: 'sol♯', 5: 'la♯'})
d.text(60 + 1.5 * 40, 28, 'groupe de 2', 's')
d.text(60 + 5 * 40, 28, 'groupe de 3', 's')
d.arrow([(60 + 2.5 * 40, 206), (60 + 3.5 * 40, 206)], color='a', start=True, label='½ ton', dy=16)
d.arrow([(60 + 6.5 * 40, 206), (60 + 7.5 * 40, 206)], color='a', start=True, label='½ ton', dy=16)
d.arrow([(60 + 0.5 * 40, 244), (60 + 7.5 * 40, 244)], color='c', start=True)
d.text(60 + 4 * 40, 266, 'une octave = 12 demi-tons', 'ct')
put(f'{M}/01-le-clavier-et-les-notes.md', 'clavier', figure(d, 'Le clavier',
    "Do est à gauche du groupe de deux noires, fa à gauche du groupe de trois. Mi-fa et si-do ne sont séparés que d'un demi-ton."), before="## L'octave")

# --- 05 : la gamme majeure ---------------------------------------------
d = D(680, 230)
x0 = 130
keyboard(d, x0, 60, 8, ww=52, wh=150, on=range(8))
steps = ['T', 'T', '½', 'T', 'T', 'T', '½']
for i, s in enumerate(steps):
    cx = x0 + (i + 1) * 52
    d.text(cx, 46, s, 'at' if s == '½' else 'ct')
d.text(340, 22, 'do majeur : T – T – ½ – T – T – T – ½', 'tl')
put(f'{M}/07-intervalles-et-gamme-majeure.md', 'gamme', figure(d, 'La gamme de do majeur',
    "Les deux demi-tons tombent naturellement sur mi-fa et si-do : do majeur n'a besoin d'aucune touche noire."), before='## Les degrés')

# --- 06 : le cycle des quintes -----------------------------------------
d = D(680, 380)
cx, cy = 340, 190
majors = ['do', 'sol', 'ré', 'la', 'mi', 'si', 'fa♯\nsol♭', 'ré♭', 'la♭', 'mi♭', 'si♭', 'fa']
minors = ['la m', 'mi m', 'si m', 'fa♯ m', 'do♯ m', 'sol♯ m', 'ré♯ m', 'si♭ m', 'fa m', 'do m', 'sol m', 'ré m']
alts = ['0', '1♯', '2♯', '3♯', '4♯', '5♯', '6♯/6♭', '5♭', '4♭', '3♭', '2♭', '1♭']
d.raw(f'<circle cx="{cx}" cy="{cy}" r="150" class="dg-grid" fill="none"/>')
d.raw(f'<circle cx="{cx}" cy="{cy}" r="95" class="dg-grid" fill="none"/>')
for i in range(12):
    a = math.radians(i * 30 - 90)
    xo, yo = cx + 150 * math.cos(a), cy + 150 * math.sin(a)
    xi, yi = cx + 95 * math.cos(a), cy + 95 * math.sin(a)
    d.circle(xo, yo, 27, k='c' if i == 0 else '', d=i * 0.3)
    d.text(xo, yo + (4 if '\n' not in majors[i] else -3), majors[i], 't' if '\n' not in majors[i] else 's', d=i * 0.3)
    d.text(xi, yi + 4, minors[i], 's', d=i * 0.3)
    xa, ya = cx + 55 * math.cos(a), cy + 55 * math.sin(a)
    d.text(xa, ya + 4, alts[i], 'zl', d=i * 0.3)
d.text(560, 60, '→ +1 dièse', 'ct', anchor='start')
d.text(120, 60, '+1 bémol ←', 'at', anchor='end')
put(f'{M}/08-gammes-mineures-et-tonalites.md', 'cycle', figure(d, 'Le cycle des quintes',
    "Extérieur : tonalités majeures. Intérieur : leurs relatifs mineurs. Au centre : le nombre d'altérations de l'armure."), before='Ce cycle sert à tout')

# --- 07 : majeur et mineur ---------------------------------------------
d = D(680, 230)
keyboard(d, 30, 40, 7, ww=40, wh=140, on=(0, 2, 4))
d.text(30 + 140, 24, 'C : do – mi – sol', 'ct')
d.text(30 + 140, 205, 'tierce majeure (4) + tierce mineure (3)', 's')
keyboard(d, 370, 40, 7, ww=40, wh=140, on=(0, 4), on_black=(1,))
d.text(370 + 140, 24, 'Cm : do – mi♭ – sol', 'at')
d.text(370 + 140, 205, 'tierce mineure (3) + tierce majeure (4)', 's')
put(f'{M}/09-les-accords-et-les-renversements.md', 'triades', figure(d, 'Accord majeur et accord mineur',
    "Seule la note du milieu change : en la descendant d'un demi-ton, l'accord majeur devient mineur."), before='## La gamme harmonisée')

# --- 12 : la pentatonique ----------------------------------------------
d = D(680, 210)
keyboard(d, 60, 40, 14, ww=40, wh=140, on=(0, 1, 2, 4, 5, 7, 8, 9, 11, 12))
d.text(340, 24, 'pentatonique de do majeur : do, ré, mi, sol, la (sans fa ni si)', 'ct')
put(f'{M}/14-improviser-et-jouer-d-oreille.md', 'penta', figure(d, 'La gamme pentatonique de do majeur',
    "Sans fa ni si, il n'y a plus de demi-ton : presque toutes les combinaisons sonnent bien sur une grille en do."), before='## Premiers pas')
print('ok')


# --- 14 : ii-V-I sans fondamentale ---------------------------------------
d = D(680, 230)
chords = [('Dm9', 'position A', (3, 5, 7, 9)), ('G13', 'position B', (3, 5, 6, 9)), ('Cmaj9', 'position A', (2, 4, 6, 8))]
for i, (name, pos, on) in enumerate(chords):
    x = 25 + i * 220
    keyboard(d, x, 50, 10, ww=20, wh=110, on=on, names=False)
    d.text(x + 100, 30, name, 'tl')
    d.text(x + 100, 186, pos, 's')
    if i:
        d.arrow([(x - 18, 105), (x - 4, 105)], color='c')
d.text(340, 216, 'une seule voix bouge entre Dm9 et G13 (do → si)', 'ct')
put(f'{M}/16-voicings-et-ii-v-i.md', 'rootless', figure(d, 'Le ii-V-I sans fondamentale en do',
    "Dm9 (fa-la-do-mi), G13 (fa-la-si-mi), Cmaj9 (mi-sol-si-ré) : la main reste au même endroit et les voix glissent d'un demi-ton ou d'un ton."),
    before='## Le ii-V-i mineur')

# --- 13 : du plus clair au plus sombre ----------------------------------
d = D(680, 250)
modes = [('lydien', 'fa♯'), ('ionien', ''), ('mixolydien', 'si♭'), ('dorien', 'mi♭'),
         ('éolien', 'la♭'), ('phrygien', 'ré♭'), ('locrien', 'sol♭')]
for i, (m, n) in enumerate(modes):
    x = 20 + i * 93
    d.box(x, 70, 84, 56, m, k='c' if i < 3 else 'a', d=i)
    if n:
        d.text(x + 42, 150, ('+ ' if i == 0 else '− ') + n, 'ct' if i == 0 else 'at')
d.arrow([(30, 190), (650, 190)], color='', k='')
d.text(30, 214, 'plus clair', 's', anchor='start')
d.text(650, 214, 'plus sombre', 's', anchor='end')
d.text(340, 40, 'Les sept modes sur do : chaque pas abaisse une seule note', 'tl')
put(f'{M}/15-les-modes-et-l-harmonie-modale.md', 'modes', figure(d, 'Les modes, du plus clair au plus sombre',
    "Le lydien monte le fa ; à partir de l'ionien, chaque mode abaisse une note de plus : si, mi, la, ré, puis sol."),
    before='## La note caractéristique')


# --- 02 : les quatre accords en renversements ----------------------------
d = D(680, 250)
voicings = [('C', (0, 2, 4)), ('G', (-1, 1, 4)), ('Am', (0, 2, 5)), ('F', (0, 3, 5))]
for i, (name, on) in enumerate(voicings):
    x = 20 + i * 165
    # 7 blanches à partir du si grave : k = 0 pour do, -1 pour le si.
    keyboard(d, x, 50, 7, ww=20, wh=110, on=[k + 1 for k in on], names=False, start=6)
    d.text(x + 70, 32, name, 'tl')
    if i:
        d.arrow([(x - 22, 105), (x - 6, 105)], color='c')
d.text(340, 196, 'do-mi-sol → si-ré-sol → do-mi-la → do-fa-la', 'ct')
d.text(340, 222, 'la main reste en place : chaque note bouge au plus d’une touche blanche', 's')
put(f'{M}/02-jouer-avec-des-grilles-d-accords.md', 'quatre', figure(d, 'C – G – Am – F sans sauter',
    "Les quatre accords les plus utilisés de la pop, joués en renversements : les notes communes restent, les autres glissent vers la touche blanche voisine."),
    before='## Méthode')
