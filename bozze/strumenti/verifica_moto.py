"""Verifica calcola() di moto.js con aritmetica esatta (Fraction) e con la derivata di sympy."""
import json, subprocess, sys, pathlib
from fractions import Fraction as F
import sympy as sp

JS = pathlib.Path(__file__).resolve().parents[2] / "assets" / "js" / "moto.js"
casi = [(a, v0, t0 / 2, dt / 10) for a in range(-4, 9) for v0 in range(0, 9) for t0 in range(0, 9) for dt in range(1, 21)]
js = f"""
const {{ calcola }} = require({json.dumps(str(JS))});
const casi = JSON.parse(require('fs').readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(casi.map(c => {{ const r = calcola(c[0],c[1],c[2],c[3]); return [r.s0,r.s1,r.ds,r.vm,r.vi]; }})));
"""
res = json.loads(subprocess.run(["node", "-e", js], input=json.dumps(casi), capture_output=True, text=True, check=True).stdout)
t, a, v0 = sp.symbols("t a v0")
s = v0 * t + a * t**2 / 2
vi_formula = sp.diff(s, t)
assert sp.simplify(vi_formula - (v0 + a * t)) == 0           # v_ist = v0 + a t
err = 0
for (a_, v_, t0, dt), r in zip(casi, res):
    A, V, T0, DT = F(a_), F(v_), F(t0).limit_denominator(100), F(dt).limit_denominator(100)
    S = lambda x: V * x + A * x * x / 2
    esatto = [S(T0), S(T0 + DT), S(T0 + DT) - S(T0), (S(T0 + DT) - S(T0)) / DT, V + A * T0]
    if any(abs(float(e) - g) > 1e-9 for e, g in zip(esatto, r)):
        err += 1
        if err < 5: print("DIVERSO", a_, v_, t0, dt, r, [float(e) for e in esatto])
print(f"{len(casi)} casi confrontati con il calcolo esatto: differenze = {err}")
sys.exit(1 if err else 0)
