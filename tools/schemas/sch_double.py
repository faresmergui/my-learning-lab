from svg import D, figure
from inject import put
from sch_badminton_lib import court, NET, SSL, LSD, L, W

B = 'badminton/'

# --- Anatomy: the first four shots --------------------------------
d = D(680, 330)
X, Y = court(d, 70, 40, 40)
S, P = (NET - SSL - 0.25, W * 0.72), (2.4, W / 2 + 0.6)       # server (right), partner
R, RP = (NET + SSL + 0.35, W * 0.28), (L - 2.4, W / 2 - 0.4)  # receiver, diagonally
for (x, y), lab, k in [(S, 'serveur', 'c'), (P, 'partenaire', 'c'), (R, 'receveur', 'a'), (RP, 'partenaire', 'a')]:
    d.circle(X(x), Y(y), 9, k=k)
    d.text(X(x), Y(y) + 24, lab, 'ct' if k == 'c' else 'at')
d.arrow(f'M{X(S[0]) + 8} {Y(S[1]) - 6} Q {X(NET)} {Y(W / 2) - 30} {X(NET + SSL + 0.15)} {Y(W / 2) - 4}', color='ok', k='thick', draw=True, d=0)
d.text(X(NET) + 8, Y(W * 0.62) + 4, '1. service court au T', 'okt', anchor='start', d=0)
d.raw(f'<ellipse cx="{X(3.9)}" cy="{Y(W / 2 + 0.2)}" rx="44" ry="34" class="dg-fillA"/>')
d.arrow(f'M{X(R[0]) - 8} {Y(R[1]) + 4} Q {X(NET)} {Y(W * 0.38)} {X(4.1)} {Y(W / 2 + 0.1)}', color='a', k='thick', draw=True, d=1)
d.text(X(3.9), Y(W / 2) - 52, '2. retour poussé dans le trou', 'at', d=1)
d.text(X(L / 2), Y(W) + 22, '3. le troisième coup doit rester à plat ou bas, sinon l\'équipe au service passe en défense', 's', d=2)
d.h = 360
put(B + '10-anatomie-d-un-point.md', 'anatomie', figure(d, 'Les premiers coups d\'un point en double',
    'Le retour vise la zone entre le serveur et son partenaire. Qui doit lever au troisième coup perd l\'initiative.'))

# --- Rotation: attack -> defense after a lift --------------------------
d = D(680, 260)
for i, (title, x0, pos, arrows, note) in enumerate([
        ('avant : ton équipe attaque', 20, [(NET - 1.2, W * 0.75), (1.8, W / 2)], [], 'le joueur avant (droite) doit lever'),
        ('après le lift droit', 360, [(3.4, W * 0.75), (3.4, W * 0.25)], [((NET - 1.2, W * 0.75), (3.6, W * 0.75)), ((1.8, W / 2), (3.2, W * 0.27))], 'il recule sur son côté, le partenaire prend l\'autre')]):
    s = 22.5
    X, Y = court(d, x0, 46, s)
    for j, (x, y) in enumerate(pos):
        d.circle(X(x), Y(y), 8, k='c', d=i * 2 + j)
    for j, ((x1, y1), (x2, y2)) in enumerate(arrows):
        d.arrow([(X(x1), Y(y1)), (X(x2), Y(y2))], k='dash', d=3 + j)
    if i == 0:
        d.arrow(f'M{X(NET - 1.1)} {Y(W * 0.75) - 6} C {X(8)} {Y(W * 0.9)}, {X(11)} {Y(W * 0.85)}, {X(12.5)} {Y(W * 0.8)}', color='ok', k='thick', draw=True, d=1)
    else:
        d.arrow([(X(12.3), Y(W * 0.8)), (X(3.7), Y(W * 0.78))], color='a', k='thick', draw=True, d=5)
    if i == 1:
        d.text(X(3.4), Y(W * 0.75) + 22, 'lifteur', 'ct')
    d.text(X(L / 2), 30, title, 't')
    d.text(X(L / 2), Y(W) + 22, note, 's')
put(B + '10-rotations.md', 'rotation', figure(d, 'Rotation de l\'attaque vers la défense après un lift',
    'Celui qui lève défend la ligne de son côté ; le partenaire glisse sur l\'autre moitié.'))

# --- Positioning errors: front player glued to the net --------------------
d = D(680, 260)
for i, (title, x0, front, ok) in enumerate([('joueur avant collé au filet', 20, NET - 0.35, False),
                                              ('joueur avant bien placé', 360, NET - SSL + 0.2, True)]):
    s = 22.5
    X, Y = court(d, x0, 46, s)
    d.circle(X(front), Y(W / 2), 8, k='c', d=i)
    d.circle(X(1.6), Y(W / 2), 8, k='c', d=i)
    if not ok:
        d.raw(f'<ellipse cx="{X(3.9)}" cy="{Y(W / 2)}" rx="34" ry="30" class="dg-fillA"/>')
        d.arrow(f'M{X(NET + 2.2)} {Y(W * 0.3)} Q {X(NET)} {Y(W * 0.38)} {X(4.0)} {Y(W / 2) - 6}', color='a', k='thick', draw=True, d=2)
        d.text(X(L / 2), Y(W) + 22, 'la poussée au milieu passe derrière lui', 'at')
    else:
        d.arrow(f'M{X(NET + 2.2)} {Y(W * 0.3)} Q {X(NET + 0.6)} {Y(W * 0.38)} {X(front) + 10} {Y(W / 2) - 10}', color='ok', k='thick', draw=True, d=2)
        d.text(X(L / 2), Y(W) + 22, 'il intercepte la poussée, raquette haute', 'okt')
    d.text(X(L / 2), 30, title, 't')
put(B + '10-erreurs-de-placement.md', 'erreurs', figure(d, 'Joueur avant trop collé au filet ou bien placé',
    'Collé au filet, le joueur avant laisse un trou au milieu. Vers la ligne de service court, il couvre la poussée.'))

# --- Serve and return: positions -----------------------------------------
d = D(680, 300)
X, Y = court(d, 70, 30, 40)
S, P = (NET - SSL - 0.25, W * 0.72), (2.6, W * 0.62)
R, RP = (NET + SSL + 0.4, W * 0.28), (L - 2.3, W * 0.62)
for (x, y), lab, k, dl in [(S, 'serveur', 'c', 26), (P, 'partenaire : couvre fond et milieu', 'c', -16),
                           (R, 'receveur : raquette haute', 'a', -16), (RP, 'partenaire : prêt pour le flick', 'a', 26)]:
    d.circle(X(x), Y(y), 9, k=k)
    d.text(X(x), Y(y) + dl, lab, 'ct' if k == 'c' else 'at')
d.arrow(f'M{X(S[0]) + 8} {Y(S[1]) - 6} Q {X(NET)} {Y(W / 2) - 26} {X(NET + SSL + 0.15)} {Y(W / 2) - 4}', color='ok', k='thick', draw=True, d=0)
d.arrow(f'M{X(S[0]) + 8} {Y(S[1]) - 8} C {X(8)} {Y(0.2)}, {X(11)} {Y(0.1)}, {X(L - LSD - 0.2)} {Y(0.6)}', color='a', k='dash', draw=True, d=1)
d.text(X(L - LSD - 0.6), Y(0.6) + 18, 'flick', 'at', anchor='end', d=1)
d.text(X(NET + SSL + 0.4), Y(W / 2) + 18, 'court au T', 'okt', anchor='start', d=0)
put(B + '03-service-et-retour-en-double.md', 'service-double', figure(d, 'Positions au service et au retour en double',
    'Le serveur sert court au T ; le flick reste une menace pour garder le receveur honnête.'))
print('double schemas ok')
