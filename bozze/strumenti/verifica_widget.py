"""Confronta la funzione risolvi() del widget (JS) con sympy su una griglia di casi.
Uso: python3 verifica_widget.py   (da qualunque cartella)"""
import json, subprocess, sys, pathlib
import sympy as sp

QUI = pathlib.Path(__file__).resolve().parent
JS = QUI.parents[1] / "assets" / "js" / "equazione2.js"
x = sp.symbols("x", real=True)

casi = []
for a2 in range(-6, 7):          # a da -3 a 3 con passo 0,5
    for b in range(-8, 9):
        for c in range(-8, 9):
            casi.append((sp.Rational(a2, 2), sp.Integer(b), sp.Integer(c)))

attesi = []
for a, b, c in casi:
    if a == 0:
        sol = sp.solve(b * x + c, x) if b != 0 else []
        attesi.append({"tipo": "retta", "x": [float(s) for s in sol]})
        continue
    sol = sorted(sp.solve(a * x**2 + b * x + c, x), key=lambda s: float(s))
    d = b**2 - 4 * a * c
    tipo = "due" if d > 0 else ("una" if d == 0 else "nessuna")
    xv = -b / (2 * a)
    attesi.append({"tipo": tipo, "delta": float(d), "x": [float(s) for s in sol],
                   "vertice": [float(xv), float(a * xv**2 + b * xv + c)]})

js = f"""
const {{ risolvi }} = require({json.dumps(str(JS))});
const casi = {json.dumps([[float(a), float(b), float(c)] for a, b, c in casi])};
console.log(JSON.stringify(casi.map(([a,b,c]) => risolvi(a,b,c))));
"""
res = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)

errori = 0
for (a, b, c), att, got in zip(casi, attesi, res):
    ok = got["tipo"] == att["tipo"]
    if ok and att["tipo"] != "retta":
        ok = abs(got["delta"] - att["delta"]) < 1e-9
        got_x = [v for v in (got["x1"], got["x2"]) if v is not None]
        ok = ok and len(got_x) == len(att["x"]) and all(abs(g - e) < 1e-9 for g, e in zip(got_x, att["x"]))
        ok = ok and all(abs(g - e) < 1e-9 for g, e in zip(got["vertice"], att["vertice"]))
    if att["tipo"] == "retta":
        got_x = [got["x1"]] if got["x1"] is not None else []
        ok = ok and len(got_x) == len(att["x"]) and all(abs(g - e) < 1e-9 for g, e in zip(got_x, att["x"]))
    if not ok:
        errori += 1
        print("DIVERSO", a, b, c, got, att)
print(f"{len(casi)} casi confrontati con sympy, differenze: {errori}")
sys.exit(1 if errori else 0)
