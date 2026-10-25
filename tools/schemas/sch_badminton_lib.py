from svg import D
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


