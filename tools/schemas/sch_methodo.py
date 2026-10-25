from svg import D, figure
from inject import put

M = 'securite'

# --- fiche 10 : la boucle des phases ---------------------------------
d = D(680, 230)
phases = [('1 · Recon', 'cadrer'), ('2 · Énumérer', 'tout lister'),
          ('3 · Vecteurs', 'quelle faille'), ('4 · Exploiter', "l'accès"),
          ('5 · Privesc', 'aller + loin'), ('6 · Doc', 'write-up')]
x0, w, step, y = 8, 98, 112, 50
for i, (t, s) in enumerate(phases):
    x = x0 + i * step
    k = 'c' if i in (1,) else ('a' if i == 4 else '')
    d.box(x, y, w, 56, t, s, k=k, tk='s', d=i)
    if i:
        d.arrow([(x - 14, y + 28), (x - 2, y + 28)], color='c')
# boucle de retour : de privesc (5) vers énumération (2)
d.arrow([(x0 + 4*step + w/2, y + 58), (x0 + 4*step + w/2, 150),
         (x0 + step + w/2, 150), (x0 + step + w/2, y + 58)], color='a', k='dash')
d.text(680/2, 170, "une découverte tardive → on revient énumérer", 's')
put(f'{M}/10-methodologie-le-fil-conducteur.md', 'phases',
    figure(d, 'Les six phases, et la boucle du retour',
    "On avance de la reconnaissance à la documentation, mais chaque nouvelle information renvoie à l'énumération : le trajet n'est jamais une ligne droite."),
    before='| Phase | Question')

# --- fiche 11 : le trajet type d'une machine -------------------------
d = D(680, 250)
steps = [('Scan', 'ports ouverts'), ('Énumérer', 'chaque service'),
         ('Accès initial', 'un pied dedans'), ('Stabiliser', 's\'orienter'),
         ('Privesc', 'devenir root')]
x0, w, step, y = 10, 118, 132, 60
for i, (t, s) in enumerate(steps):
    x = x0 + i * step
    k = 'c' if i < 2 else ('a' if i == 4 else '')
    d.box(x, y, w, 58, t, s, k=k, tk='s', d=i)
    if i:
        d.arrow([(x - 16, y + 29), (x - 2, y + 29)], color='c')
# flags
d.box(x0 + 2*step, y + 86, w, 34, 'flag user', k='ghost', tk='s', rx=7, d=5)
d.arrow([(x0 + 2*step + w/2, y + 58), (x0 + 2*step + w/2, y + 86)], color='', k='dash')
d.box(x0 + 4*step, y + 86, w, 34, 'flag root', k='ghost', tk='s', rx=7, d=6)
d.arrow([(x0 + 4*step + w/2, y + 58), (x0 + 4*step + w/2, y + 86)], color='', k='dash')
d.text(680/2, 210, "à chaque étape, on ré-énumère avant de forcer", 's')
put(f'{M}/11-compromettre-une-machine-d-entrainement.md', 'killchain',
    figure(d, "Le trajet type d'une machine",
    "Scanner, énumérer chaque service, obtenir un premier accès (flag utilisateur), puis élever ses privilèges jusqu'à root (flag root)."),
    before='Le trajet type est toujours')
