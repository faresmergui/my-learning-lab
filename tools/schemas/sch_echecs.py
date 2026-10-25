from svg import D, figure
from inject import put

M = 'echecs'
# Solid glyphs for both sides (color comes from the CSS); \ufe0e forces text rather than emoji rendering.
GLYPH = {'R': '♚', 'D': '♛', 'T': '♜', 'F': '♝', 'C': '♞', 'P': '♟'}
S = 34


def sq(x0, y0, square):
    """Top-left corner of a square, board seen from White's side."""
    f, r = ord(square[0]) - 97, int(square[1])
    return x0 + f * S, y0 + (8 - r) * S


def center(x0, y0, square):
    x, y = sq(x0, y0, square)
    return x + S / 2, y + S / 2


def board(d, x0, y0, white=(), black=(), hl=()):
    """white / black: lists like "Re1", "Pe4" (French piece letters); hl: highlighted squares."""
    for f in range(8):
        for r in range(8):
            k = 'sqd' if (f + r) % 2 == 0 else 'sql'
            d.rect(x0 + f * S, y0 + (7 - r) * S, S, S, k=k)
    for s in hl:
        x, y = sq(x0, y0, s)
        d.rect(x, y, S, S, k='sqh')
    d.rect(x0, y0, 8 * S, 8 * S, k='board')
    for i in range(8):
        d.text(x0 + i * S + S / 2, y0 + 8 * S + 14, 'abcdefgh'[i], 'coord')
        d.text(x0 - 10, y0 + (7 - i) * S + S / 2 + 4, str(i + 1), 'coord')
    for side, k in ((white, 'pw'), (black, 'pb')):
        for p in side:
            cx, cy = center(x0, y0, p[1:])
            d.text(cx, cy + 11, GLYPH[p[0]] + '︎', k)
    return d


def arrow(d, x0, y0, a, b, color='a', k=''):
    d.arrow([center(x0, y0, a), center(x0, y0, b)], color=color, k=k)


X0, Y0 = 60, 20

# --- 04: the knight fork --------------------------------------
d = D(680, 320)
board(d, X0, Y0, white=['Re1', 'Cd5'], black=['Re8', 'Ta8', 'Pb7', 'Pf7'], hl=['c7'])
arrow(d, X0, Y0, 'd5', 'c7')
arrow(d, X0, Y0, 'c7', 'e8', k='dash')
arrow(d, X0, Y0, 'c7', 'a8', k='dash')
d.text(380, 110, 'Cc7+ attaque le roi e8', 'tl', anchor='start')
d.text(380, 132, 'et la tour a8 en même temps.', 'tl', anchor='start')
d.text(380, 170, 'Le roi doit bouger :', 's', anchor='start')
d.text(380, 188, 'Cxa8 gagne la qualité.', 's', anchor='start')
put(f'{M}/04-les-motifs-tactiques.md', 'fourchette', figure(d, 'La fourchette royale',
    "Le cavalier arrive en c7 avec échec et attaque aussi la tour : une seule des deux menaces peut être parée."),
    before='## Le clouage')

# --- 06: smothered mate -------------------------------------------------
d = D(680, 320)
board(d, X0, Y0, white=['Rg1', 'Cf7', 'Ph2', 'Pg2'], black=['Rh8', 'Tg8', 'Pg7', 'Ph7'], hl=['h8'])
arrow(d, X0, Y0, 'f7', 'h8', k='dash')
d.text(380, 110, 'Cf7# : le roi h8 est enfermé', 'tl', anchor='start')
d.text(380, 132, 'par ses propres pièces.', 'tl', anchor='start')
d.text(380, 170, 'Souvent après Dg8+ !! Txg8 :', 's', anchor='start')
d.text(380, 188, 'la tour vient boucher g8.', 's', anchor='start')
put(f'{M}/06-attaquer-le-roi.md', 'etouffe', figure(d, 'Le mat étouffé',
    "g8, g7 et h7 sont occupées par des pièces noires : l'échec du cavalier ne peut être ni intercepté ni fui."),
    before='## Le sacrifice grec')

# --- 15: opposition and key squares ----------------------------
d = D(680, 320)
board(d, X0, Y0, white=['Re5', 'Pe4'], black=['Re7'], hl=['d6', 'e6', 'f6'])
d.text(380, 100, 'Les rois sont face à face :', 'tl', anchor='start')
d.text(380, 122, 'le camp au trait doit céder.', 'tl', anchor='start')
d.text(380, 160, 'Cases critiques du pion e4 :', 's', anchor='start')
d.text(380, 178, 'd6, e6, f6. Si le roi blanc', 's', anchor='start')
d.text(380, 196, "en atteint une, c'est gagné.", 's', anchor='start')
d.text(380, 230, 'Noirs au trait : gain blanc.', 'ct', anchor='start')
d.text(380, 250, 'Blancs au trait : nulle.', 's', anchor='start')
put(f'{M}/15-les-finales-de-pions.md', 'opposition', figure(d, "L'opposition",
    "Celui qui n'a pas le trait « a l'opposition ». Ici, les Noirs au trait doivent s'écarter et le roi blanc entre en d6 ou f6."),
    before='## Roi et pion contre roi')

# --- 16 : Lucena -----------------------------------------------------------
d = D(680, 320)
board(d, X0, Y0, white=['Re8', 'Pe7', 'Tf1'], black=['Rg7', 'Td2'], hl=['g4', 'e4'])
d.arrow([center(X0, Y0, 'f1'), center(X0, Y0, 'g1'), center(X0, Y0, 'g4')], color='a')
d.text(380, 90, '1. Tg1+ coupe le roi noir', 'tl', anchor='start')
d.text(380, 112, '2. Tg4 ! prépare le pont', 'tl', anchor='start')
d.text(380, 150, 'Le roi blanc sort par f7,', 's', anchor='start')
d.text(380, 168, 'descend vers sa tour, et la tour', 's', anchor='start')
d.text(380, 186, "s'interpose en e4 contre les échecs.", 's', anchor='start')
put(f'{M}/16-les-finales-de-tours.md', 'lucena', figure(d, 'La position de Lucena',
    "Pion en 7ᵉ, roi devant lui, roi adverse coupé : la tour en 4ᵉ rangée servira d'abri contre les échecs latéraux."),
    before='## La position de Philidor (nulle)')

# --- 16 : Philidor ---------------------------------------------------------
d = D(680, 320)
board(d, X0, Y0, white=['Rd5', 'Pe5', 'Ta7'], black=['Re8', 'Tb6'], hl=['a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6'])
d.text(380, 90, 'La tour noire tient la 6ᵉ rangée :', 'tl', anchor='start')
d.text(380, 112, 'le roi blanc ne peut pas avancer.', 'tl', anchor='start')
d.text(380, 150, 'Si e6, la tour passe en b1', 's', anchor='start')
d.text(380, 168, 'et donne des échecs par derrière :', 's', anchor='start')
d.text(380, 186, 'le roi blanc n\'a plus d\'abri.', 's', anchor='start')
d.text(380, 220, 'Nulle.', 'ct', anchor='start')
put(f'{M}/16-les-finales-de-tours.md', 'philidor', figure(d, 'La position de Philidor',
    "Le roi défenseur devant le pion et la tour sur la 6ᵉ rangée : c'est la défense de référence des finales de tours."),
    before='## Couper le roi')
