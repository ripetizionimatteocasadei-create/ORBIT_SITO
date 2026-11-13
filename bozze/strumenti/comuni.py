"""Funzioni comuni per i post: numeri calcolati con sympy, formattazione italiana, figura iniziale del grafico a parabola.
Ogni post ha una cartella bozze/<nome>/ con meta.json, sorgente.html e calcoli.py (che importa da qui)."""
import sympy as sp
from sympy import Rational as R

MINUS = "\u2212"


def tex(v):
    return sp.latex(v).replace(".", "{,}")


def txt(v):
    """Numero in italiano per il testo normale: -1/2 -> −0,5."""
    v = sp.nsimplify(v)
    s = f"{float(v):.4f}".rstrip("0").rstrip(".").replace(".", ",")
    return s.replace("-", MINUS)


class Dati:
    """Dizionario dei valori usati dai segnaposto <<CHIAVE>> del sorgente (in formula: tex; nel testo: txt)."""
    def __init__(self):
        self.D = {}

    def put(self, k, v, plain=None):
        self.D[k] = {"tex": tex(v), "txt": plain if plain is not None else txt(v)}

    def raw(self, k, t, p):
        self.D[k] = {"tex": t, "txt": p}

    def dec(self, k, v, cifre=2):
        s = f"{float(v):.{cifre}f}"
        self.D[k] = {"tex": s.replace(".", "{,}"), "txt": s.replace(".", ",").replace("-", MINUS)}


def solve(a, b, c):
    x = sp.symbols("x", real=True)
    d = b * b - 4 * a * c
    sols = sorted(sp.solve(a * x**2 + b * x + c, x), key=lambda s: float(s))
    if d > 0:
        f = sorted([(-b - sp.sqrt(d)) / (2 * a), (-b + sp.sqrt(d)) / (2 * a)], key=float)
        assert [sp.simplify(p - q) for p, q in zip(f, sols)] == [0, 0]
    return d, sols


# ------------------------------------------------------------------ grafico a parabola (stessa geometria di equazione2.js)
W, H, XMIN, XMAX, YMIN, YMAX = 640, 400, -6, 6, -10, 10
sx = lambda x: (x - XMIN) / (XMAX - XMIN) * W
sy = lambda y: H - (y - YMIN) / (YMAX - YMIN) * H


def num_it(n):
    s = f"{round(float(n) * 1000) / 1000:g}".replace(".", ",")
    return s.replace("-", MINUS)


def equazione_it(a, b, c):
    def term(co, pot, primo):
        if co == 0:
            return ""
        sg = MINUS if co < 0 else ("" if primo else "+")
        ab = abs(co)
        cifra = "" if (ab == 1 and pot) else num_it(ab)
        return (sg if primo else f" {sg} ") + cifra + pot
    s = term(a, "x\u00b2", True)
    t = term(b, "x", s == "")
    u = term(c, "", s == "" and t == "")
    return ((s + t + u) or "0") + " = 0"


def lettura_it(a, b, c):
    d = b * b - 4 * a * c
    if a == 0:
        return "Con a = 0 non c\u2019\u00e8 pi\u00f9 il termine x\u00b2: non \u00e8 un\u2019equazione di secondo grado, ma una retta."
    if d > 0:
        r1, r2 = sorted([(-b - d**0.5) / (2 * a), (-b + d**0.5) / (2 * a)])
        return f"\u0394 = {num_it(d)} > 0: due soluzioni, x\u2081 = {num_it(r1)} e x\u2082 = {num_it(r2)}. La parabola taglia l\u2019asse x in due punti."
    if d == 0:
        return f"\u0394 = 0: una sola soluzione (doppia), x = {num_it(-b / (2 * a))}. La parabola tocca l\u2019asse x in un punto."
    return f"\u0394 = {num_it(d)} < 0: nessuna soluzione reale. La parabola non incontra l\u2019asse x."


def svg_parabola(a, b, c, alt):
    f = lambda x: a * x * x + b * x + c
    pts, x = [], XMIN
    while x <= XMAX + 1e-9:
        pts.append(("M" if not pts else "L") + f"{sx(x):.1f} {sy(f(x)):.1f}")
        x = round(x + 0.05, 10)
    grid = "".join(f'<line class="g-grid" x1="{sx(i):.1f}" y1="0" x2="{sx(i):.1f}" y2="{H}"/>' for i in range(XMIN, XMAX + 1))
    grid += "".join(f'<line class="g-grid" x1="0" y1="{sy(j):.1f}" x2="{W}" y2="{sy(j):.1f}"/>' for j in range(YMIN, YMAX + 1, 2))
    ticks = "".join(f'<text x="{sx(i):.1f}" y="{sy(0) + 16:.1f}" font-size="12" text-anchor="middle">{num_it(i)}</text>' for i in range(-4, 5, 2) if i != 0)
    ticks += "".join(f'<text x="{sx(0) - 8:.1f}" y="{sy(j) + 4:.1f}" font-size="12" text-anchor="end">{num_it(j)}</text>' for j in (-5, 5))
    d = b * b - 4 * a * c
    xv = -b / (2 * a)
    yv = f(xv)
    marks = ""
    if d > 0:
        r1_, r2_ = sorted([(-b - d**0.5) / (2 * a), (-b + d**0.5) / (2 * a)])
        ldy = 26 if a > 0 else -16
        for rr, lab, ldx in ((r1_, "x\u2081", -16), (r2_, "x\u2082", 16)):
            if XMIN <= rr <= XMAX:
                marks += (f'<circle class="eq-radice" cx="{sx(rr):.1f}" cy="{sy(0):.1f}" r="7"></circle>'
                          f'<text class="g-lab-radice" x="{sx(rr) + ldx:.1f}" y="{sy(0) + ldy:.1f}" text-anchor="middle" font-size="15">{lab}</text>')
    elif d == 0 and XMIN <= xv <= XMAX:
        ldy = 26 if a > 0 else -16
        marks += (f'<circle class="eq-radice" cx="{sx(xv):.1f}" cy="{sy(0):.1f}" r="7"></circle>'
                  f'<text class="g-lab-radice" x="{sx(xv):.1f}" y="{sy(0) + ldy:.1f}" text-anchor="middle" font-size="15">x</text>')
    vdy = 24 if a > 0 else -14
    if XMIN <= xv <= XMAX and YMIN <= yv <= YMAX:
        marks += (f'<circle class="eq-vertice" cx="{sx(xv):.1f}" cy="{sy(yv):.1f}" r="6"></circle>'
                  f'<text class="g-lab-vertice" x="{sx(xv):.1f}" y="{sy(yv) + vdy:.1f}" text-anchor="middle" font-size="15">V</text>')
    import html as _h
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{_h.escape(alt)}" width="{W}" height="{H}">'
            f'<defs><clipPath id="eq-clip"><rect width="{W}" height="{H}"/></clipPath></defs>'
            f'<g>{grid}</g>'
            f'<line class="g-axis" x1="0" y1="{sy(0):.1f}" x2="{W}" y2="{sy(0):.1f}"/><line class="g-axis" x1="{sx(0):.1f}" y1="0" x2="{sx(0):.1f}" y2="{H}"/>'
            f'<g>{ticks}</g>'
            f'<path class="g-curva" data-eq="curva" clip-path="url(#eq-clip)" d="{"".join(pts)}"/>'
            f'<g data-eq="punti">{marks}</g></svg>')


def widget_parabola(dati, a, b, c, alt):
    """Imposta W_EQ, W_SVG, W_LETTURA per il widget della parabola (markup nel sorgente)."""
    dati.raw("W_EQ", "", equazione_it(a, b, c))
    dati.raw("W_SVG", "", svg_parabola(a, b, c, alt))
    dati.raw("W_LETTURA", "", lettura_it(a, b, c))


# ------------------------------------------------------------------ disequazioni di secondo grado
def intervalli(a, b, c, op):
    """Insieme delle soluzioni di a x^2 + b x + c  op  0 come lista di (lo, hi, incLo, incHi) (sympy)."""
    x = sp.symbols("x", real=True)
    e = sp.nsimplify(a) * x**2 + b * x + c
    rel = {">": e > 0, "<": e < 0, ">=": e >= 0, "<=": e <= 0}[op]
    S = sp.solve_univariate_inequality(rel, x, relational=False)
    out = []
    for t in (S.args if isinstance(S, sp.Union) else [S]):
        if t == sp.S.EmptySet:
            continue
        if isinstance(t, sp.FiniteSet):
            for v in t:
                out.append((v, v, True, True))
        else:
            out.append((t.start, t.end, not bool(t.left_open), not bool(t.right_open)))
    # unisce (-oo,r) e (r,oo) quando restano separati solo dal punto r: lasciati distinti (come in JS)
    return sorted(out, key=lambda z: float(z[0]))


def testo_sol(iv):
    oo = sp.oo
    if not iv:
        return "nessuna soluzione"
    if len(iv) == 1 and iv[0][0] == -oo and iv[0][1] == oo:
        return "tutti i numeri reali"
    if len(iv) == 2 and iv[0][1] == iv[1][0] and iv[0][0] == -oo and iv[1][1] == oo and not iv[0][3] and not iv[1][2]:
        return f"x ≠ {num_it(iv[0][1])}"
    parti = []
    for lo, hi, il, ih in iv:
        if lo == hi:
            parti.append(f"x = {num_it(lo)}")
        elif lo == -oo:
            parti.append(f"x {'≤' if ih else '<'} {num_it(hi)}")
        elif hi == oo:
            parti.append(f"x {'≥' if il else '>'} {num_it(lo)}")
        else:
            parti.append(f"{num_it(lo)} {'≤' if il else '<'} x {'≤' if ih else '<'} {num_it(hi)}")
    return " oppure ".join(parti)


def svg_disequazione(a, b, c, op, alt):
    f = lambda x: a * x * x + b * x + c
    pts, x = [], XMIN
    while x <= XMAX + 1e-9:
        pts.append(("M" if not pts else "L") + f"{sx(x):.1f} {sy(f(x)):.1f}")
        x = round(x + 0.05, 10)
    grid = "".join(f'<line class="g-grid" x1="{sx(i):.1f}" y1="0" x2="{sx(i):.1f}" y2="{H}"/>' for i in range(XMIN, XMAX + 1))
    grid += "".join(f'<line class="g-grid" x1="0" y1="{sy(j):.1f}" x2="{W}" y2="{sy(j):.1f}"/>' for j in range(YMIN, YMAX + 1, 2))
    ticks = "".join(f'<text x="{sx(i):.1f}" y="{sy(0) + 16:.1f}" font-size="12" text-anchor="middle">{num_it(i)}</text>' for i in range(-4, 5, 2) if i != 0)
    ticks += "".join(f'<text x="{sx(0) - 8:.1f}" y="{sy(j) + 4:.1f}" font-size="12" text-anchor="end">{num_it(j)}</text>' for j in (-5, 5))
    iv = intervalli(a, b, c, op)
    g = ""
    for lo, hi, il, ih in iv:
        l, h = max(float(lo), XMIN), min(float(hi), XMAX)
        if l < h:
            g += f'<line class="q-sol" x1="{sx(l):.1f}" y1="{sy(0):.1f}" x2="{sx(h):.1f}" y2="{sy(0):.1f}"></line>'
    for lo, hi, il, ih in iv:
        for v, inc in ((lo, il), (hi, ih)):
            if v not in (sp.oo, -sp.oo) and XMIN <= float(v) <= XMAX:
                g += f'<circle class="{"q-pieno" if inc else "q-vuoto"}" cx="{sx(float(v)):.1f}" cy="{sy(0):.1f}" r="7"></circle>'
    import html as _h
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{_h.escape(alt)}" width="{W}" height="{H}">'
            f'<defs><clipPath id="q-clip"><rect width="{W}" height="{H}"/></clipPath></defs>'
            f'<g>{grid}</g>'
            f'<line class="g-axis" x1="0" y1="{sy(0):.1f}" x2="{W}" y2="{sy(0):.1f}"/><line class="g-axis" x1="{sx(0):.1f}" y1="0" x2="{sx(0):.1f}" y2="{H}"/>'
            f'<g>{ticks}</g>'
            f'<path class="g-curva" data-q="curva" clip-path="url(#q-clip)" d="{"".join(pts)}"/>'
            f'<g data-q="soluzione">{g}</g></svg>')


def widget_disequazione(dati, a, b, c, op, alt):
    sim = {">": ">", "<": "<", ">=": "≥", "<=": "≤"}[op]
    dati.raw("Q_TIT", "", equazione_it(a, b, c).replace(" = 0", f" {sim} 0"))
    dati.raw("Q_SVG", "", svg_disequazione(a, b, c, op, alt))
    dati.raw("Q_LETTURA", "", f"Soluzione: {testo_sol(intervalli(a, b, c, op))}.")
