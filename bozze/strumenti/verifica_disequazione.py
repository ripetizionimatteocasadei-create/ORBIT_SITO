"""Verifica risolvi()/contiene() di disequazione2.js: (1) membership esatta con Fraction su una griglia di punti,
(2) confronto con sympy.solve_univariate_inequality su un campione. Uso: python3 verifica_disequazione.py"""
import json, subprocess, sys, pathlib, itertools, random
from fractions import Fraction as F
import sympy as sp

QUI = pathlib.Path(__file__).resolve().parent
JS = QUI.parents[1] / "assets" / "js" / "disequazione2.js"
OPS = [">", "<", ">=", "<="]
AA = [-3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3]
casi = [(a, b, c, o) for a in AA for b in range(-8, 9) for c in range(-8, 9) for o in OPS]
# punti campione: griglia razionale fitta + radici razionali esatte
xs = [F(k, 4) for k in range(-60, 61)]

js = f"""
const {{ risolvi, contiene }} = require({json.dumps(str(JS))});
const dati = JSON.parse(require('fs').readFileSync(0, 'utf8')); const casi = dati.casi, xs = dati.xs;
const out = casi.map(([a,b,c,o]) => {{ const r = risolvi(a,b,c,o); return {{ m: xs.map(x => contiene(r,x) ? 1 : 0), iv: r.intervalli.map(t=>[t.lo,t.hi,t.incLo,t.incHi]), rad: r.radici }}; }});
process.stdout.write(JSON.stringify(out, (k,v)=> v===Infinity?"inf": v===-Infinity?"-inf": v));
"""
res = json.loads(subprocess.run(["node", "-e", js], input=json.dumps({"casi": casi, "xs": [float(x) for x in xs]}), capture_output=True, text=True, check=True).stdout)

def vero(a, b, c, o, x):
    v = F(a).limit_denominator(10) * x * x + b * x + c
    return {">": v > 0, "<": v < 0, ">=": v >= 0, "<=": v <= 0}[o]

err = 0
for (a, b, c, o), r in zip(casi, res):
    for x, m in zip(xs, r["m"]):
        if bool(m) != vero(a, b, c, o, x):
            err += 1
            if err < 6: print("DIVERSO", a, b, c, o, x, m)
print(f"{len(casi)} disequazioni × {len(xs)} punti: differenze con il calcolo esatto = {err}")

# sympy su un campione
x = sp.symbols("x", real=True)
rnd = random.Random(1)
camp = rnd.sample(list(zip(casi, res)), 400)
err2 = 0
def num(v): return float("inf") if v == "inf" else float("-inf") if v == "-inf" else v
for (a, b, c, o), r in camp:
    e = sp.Rational(a).limit_denominator(10) * x**2 + b * x + c
    rel = {">": e > 0, "<": e < 0, ">=": e >= 0, "<=": e <= 0}[o]
    S = sp.solve_univariate_inequality(rel, x, relational=False)
    ivs = [(sp.S.NegativeInfinity if t[0] == "-inf" else t[0], sp.S.Infinity if t[1] == "inf" else t[1]) for t in [[num(u[0]), num(u[1]), u[2], u[3]] for u in r["iv"]]]
    # ricostruisce l'insieme dai dati JS e lo confronta
    parti = []
    for (lo, hi), u in zip(ivs, r["iv"]):
        if lo == hi: parti.append(sp.FiniteSet(sp.nsimplify(lo)))
        else: parti.append(sp.Interval(sp.nsimplify(lo) if lo not in (sp.S.NegativeInfinity,) else lo, sp.nsimplify(hi) if hi != sp.S.Infinity else hi, u[2], u[3]))
    T = sp.Union(*parti) if parti else sp.S.EmptySet
    # confronto numerico (le radici irrazionali sono approssimate): verifica che la differenza simmetrica abbia misura ~0
    diff = sp.Union(S - T, T - S)
    if diff != sp.S.EmptySet:
        mis = sum(float(i.measure) for i in (diff.args if isinstance(diff, sp.Union) else [diff]) if hasattr(i, "measure") and i.measure != sp.oo)
        inf = any(getattr(i, "measure", 0) == sp.oo for i in (diff.args if isinstance(diff, sp.Union) else [diff]))
        if inf or mis > 1e-9:
            err2 += 1
            if err2 < 6: print("SYMPY DIVERSO", a, b, c, o, S, T)
print(f"{len(camp)} casi confrontati con sympy: differenze = {err2}")
sys.exit(1 if (err or err2) else 0)
