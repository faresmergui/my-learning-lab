"""Small SVG diagram generator for the notes.

Colors are not hard-coded: each element gets a class (dg-box, dg-c, dg-l...)
styled in global.css with the theme variables, so the same diagram looks right
in Tech (dark) and Perso (paper). --c is the module color, set on the note.
"""
from html import escape

_n = [0]


class D:
    def __init__(self, w, h):
        _n[0] += 1
        self.id = f'g{_n[0]}'
        self.w, self.h = w, h
        self.els = []

    # --- text ----------------------------------------------------------
    def text(self, x, y, t, k='t', anchor='middle', d=None):
        lines = t.split('\n')
        attrs = f'x="{x}" y="{y}" class="dg-{k}" text-anchor="{anchor}"'
        if d is not None:
            attrs += f' style="--d:{d}"'
        if len(lines) == 1:
            self.els.append(f'<text {attrs}>{escape(t)}</text>')
        else:
            lh = 14 if k in ('s', 'zl') else 16
            sp = ''.join(f'<tspan x="{x}" dy="{0 if i == 0 else lh}">{escape(l)}</tspan>' for i, l in enumerate(lines))
            self.els.append(f'<text {attrs}>{sp}</text>')
        return self

    # --- shapes --------------------------------------------------------
    def box(self, x, y, w, h, t='', sub=None, k='', rx=9, d=None, tk='t'):
        cls = f'dg-box {"dg-" + k if k else ""}'.strip()
        st = f' style="--d:{d}"' if d is not None else ''
        self.els.append(f'<g class="{cls} dg-pop"{st}><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></g>')
        cx = x + w / 2
        if t and sub:
            nt = t.count('\n') + 1
            ns = sub.count('\n') + 1
            total = nt * 16 + ns * 14
            top = y + (h - total) / 2 + 12
            self.text(cx, top, t, tk, d=d)
            self.text(cx, top + nt * 16 + 2, sub, 's', d=d)
        elif t:
            nt = t.count('\n') + 1
            self.text(cx, y + h / 2 + 5 - (nt - 1) * 8, t, tk, d=d)
        return self

    def zone(self, x, y, w, h, label='', k='', rx=12):
        self.els.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="dg-zone {"dg-z" + k if k else ""}"/>')
        if label:
            self.text(x + 12, y + 18, label, 'zl', anchor='start')
        return self

    def circle(self, x, y, r, k='', t=None, tk='t', d=None):
        st = f' style="--d:{d}"' if d is not None else ''
        self.els.append(f'<circle cx="{x}" cy="{y}" r="{r}" class="dg-dot {"dg-" + k if k else ""} dg-pop"{st}/>')
        if t:
            self.text(x, y + 4, t, tk, d=d)
        return self

    def line(self, x1, y1, x2, y2, k='grid'):
        self.els.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="dg-{k}"/>')
        return self

    def rect(self, x, y, w, h, k='fill', rx=0):
        self.els.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="dg-{k}"/>')
        return self

    # --- arrows --------------------------------------------------------
    def _marker(self, k):
        return f'url(#{self.id}-{k or "n"})'

    def arrow(self, pts, color='', k='', label=None, at=0.5, dy=-7, end=True, start=False, draw=False, d=None, lk='s'):
        """pts: list of points (polyline) or an SVG path string.
        color: '' (neutral), 'c' (module), 'a' (accent), 'ok' (green).
        k: extra classes, e.g. 'flow' (animated dashes) or 'dash'."""
        path = pts if isinstance(pts, str) else 'M' + ' L'.join(f'{x} {y}' for x, y in pts)
        cls = ' '.join(c for c in ('dg-l', color, k, 'draw' if draw else '') if c)
        attrs = f'd="{path}" class="{cls}"'
        if end:
            attrs += f' marker-end="{self._marker(color)}"'
        if start:
            attrs += f' marker-start="{self._marker(color)}"'
        if draw:
            attrs += ' pathLength="1"'
        if d is not None:
            attrs += f' style="--d:{d}"'
        self.els.append(f'<path {attrs}/>')
        if label and not isinstance(pts, str):
            (x1, y1), (x2, y2) = pts[0], pts[-1]
            if len(pts) > 2:
                i = len(pts) // 2
                (x1, y1), (x2, y2) = pts[i - 1], pts[i]
            self.text(x1 + (x2 - x1) * at, y1 + (y2 - y1) * at + dy, label, lk, d=d)
        return self

    def raw(self, s):
        self.els.append(s)
        return self

    # --- output --------------------------------------------------------
    def svg(self, title):
        m = ''.join(
            f'<marker id="{self.id}-{k}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 1 L9 5 L0 9 z" class="dg-head {k}"/></marker>'
            for k in ('n', 'c', 'a', 'ok'))
        body = ''.join(self.els)
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(title)}" '
                f'style="--minw:{min(self.w, 560)}px"><defs>{m}</defs>{body}</svg>')


def figure(d, title, caption=None):
    cap = f'<figcaption>{escape(caption)}</figcaption>' if caption else ''
    return f'<figure class="diagram">{d.svg(title)}{cap}</figure>'
