from svg import D, figure
from inject import put
from sch_badminton_lib import court, side, NET, SSL, LSD, L, W

B = 'badminton'

# --- FFBaD ranking ladder -----------------------------------
d = D(680, 250)
fam = [('NC', ['NC'], 'départ'), ('Promotion', ['P12', 'P11', 'P10'], ''), ('Départemental', ['D9', 'D8', 'D7'], ''),
       ('Régional', ['R6', 'R5', 'R4'], ''), ('National', ['N3', 'N2', 'N1'], '')]
x, step, bw = 24, 44, 38
i = 0
for f, (name, ranks, _) in enumerate(fam):
    x0 = x
    for r in ranks:
        h = 40 + i * 10
        k = 'c' if f % 2 else ''
        d.box(x, 190 - h, bw, h, r, k=k, rx=6, d=i)
        x += step
        i += 1
    d.text((x0 + x - step + bw) / 2, 214, name, 's')
    x += 8
d.arrow([(30, 26), (660, 26)], color='a', k='thick', draw=True, d=0)
d.text(345, 18, 'niveau croissant', 'at')
d.text(345, 240, 'un classement par discipline : simple, double, mixte', 's')
put(f'{B}/01-classement-ffbad.md', 'echelle-ffbad',
    figure(d, 'Échelle des classements FFBaD', 'Treize marches, de NC à N1. Ce module suit les mêmes paliers.'))

# --- Serves, side view ---------------------------------------
d = D(680, 260)
X, Yh = side(d, 30, 210, 46, 24)
for xm in (NET - SSL, NET + SSL, L - LSD):
    d.line(X(xm), 210, X(xm), 218, k='court')
d.text(X(NET + SSL), 234, 'service court', 's')
d.text(X(L - LSD), 234, 'service long double', 's')
d.text(X(4.2), 234, 'serveur', 's')
o = (X(4.6), Yh(1.0))
d.arrow(f'M{o[0]} {o[1]} Q {X(6.6)} {Yh(2.1)} {X(8.9)} {Yh(0)}', color='ok', k='thick', draw=True, d=0)
d.text(X(9.1), Yh(0.9), 'court : rase la bande', 'okt', anchor='start', d=1)
d.arrow(f'M{o[0]} {o[1]} C {X(6.5)} {Yh(9.5)}, {X(11.5)} {Yh(9.5)}, {X(13.2)} {Yh(0)}', color='c', k='thick', draw=True, d=2)
d.text(X(9.3), Yh(7.6), 'long et haut (simple)', 'ct', d=3)
d.arrow(f'M{o[0]} {o[1]} C {X(6.4)} {Yh(3.6)}, {X(10.5)} {Yh(4.4)}, {X(12.6)} {Yh(0)}', color='a', k='thick', draw=True, d=4)
d.text(X(8.0), Yh(3.75), 'flick : surprend, juste hors de portée', 'at', d=5)
d.circle(o[0], o[1], 5, k='c')
put(f'{B}/03-le-service.md', 'services',
    figure(d, 'Trois services vus de côté', 'Même départ, trois trajectoires : le court rase la bande, le flick surprend, le long monte au fond.'))

# --- Doubles defense -----------------------------------------------
d = D(680, 300)
s = 40
X, Y = court(d, 70, 30, s)
d.circle(X(11.6), Y(1.4), 9, k='a')
d.text(X(11.6), Y(1.4) - 16, 'smasheur', 'at')
d.circle(X(3.2), Y(1.5), 9, k='c', d=0)
d.text(X(3.2), Y(1.5) - 16, 'en ligne : protège la ligne', 'ct', d=0)
d.circle(X(2.4), Y(W - 1.5), 9, k='c', d=1)
d.text(X(2.4), Y(W - 1.5) + 28, 'en croisé : couvre le milieu', 'ct', d=1)
d.arrow([(X(11.3), Y(1.5)), (X(3.6), Y(1.5))], color='a', k='thick', draw=True, d=2)
d.arrow([(X(11.3), Y(1.6)), (X(2.8), Y(W - 1.6))], color='a', k='dash', draw=True, d=3)
d.line(X(0.2), Y(W / 2), X(NET - 0.2), Y(W / 2), k='grid')
put(f'{B}/11-defense.md', 'defense-double',
    figure(d, 'Placement de la défense côte à côte en double', 'Chaque défenseur couvre sa moitié : la ligne pour l\'un, le milieu et le croisé pour l\'autre.'))

# --- Japanese: giving and receiving -----------------------------------
d = D(680, 240)
d.box(250, 90, 180, 60, 'moi', 'et mon cercle proche', k='c')
d.box(20, 90, 150, 60, 'les autres', None)
d.box(510, 90, 150, 60, 'les autres', None)
d.arrow([(250, 108), (172, 108)], color='c', k='thick', draw=True, label='あげる', d=0, lk='ct')
d.text(210, 140, 'je donne', 's', d=0)
d.arrow([(508, 108), (432, 108)], color='ok', k='thick', draw=True, label='くれる', d=1, lk='okt')
d.text(470, 140, 'on me donne', 's', d=1)
d.arrow('M 585 88 C 585 20, 340 20, 340 86', color='a', k='thick', draw=True, d=2)
d.text(462, 30, 'もらう : je reçois (de quelqu\'un に)', 'at', d=2)
d.text(340, 200, 'くれる et もらう décrivent le même don, vu sous deux angles', 's')
put('japonais/14-donner-et-recevoir.md', 'donner-recevoir',
    figure(d, 'Les verbes de don selon la direction', 'La flèche décide du verbe : depuis moi あげる, vers moi くれる, et もらう quand je suis le sujet qui reçoit.'),
    before='## Avec des actions')
print('niveaux ok')
