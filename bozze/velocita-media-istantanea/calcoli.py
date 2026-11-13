from comuni import *
import json, subprocess, pathlib

DATI = Dati()
P, RAW, DEC = DATI.put, DATI.raw, DATI.dec
JS = pathlib.Path(__file__).resolve().parents[2] / "assets" / "js" / "moto.js"

# aggancio: 90 km in 1,5 h
vm = R(90) / R(3, 2); assert vm == 60
P("A_KM", 90); P("A_VM", vm)
DEC("A_H", R(3, 2), 1)

# media aritmetica sbagliata: 60 km a 30 km/h e 60 km a 60 km/h
t1, t2 = R(60) / 30, R(60) / 60
vtot = R(120) / (t1 + t2); assert (t1, t2, vtot) == (2, 1, 40) and R(30 + 60, 2) == 45
P("B_T1", t1); P("B_T2", t2); P("B_V", vtot); P("B_ERR", R(45))

# unità: 72 km/h = 20 m/s
assert R(72) / R(18, 5) == 20 and R(18) / R(18, 5) == 5 and 72 * R(18, 5) == R(1296, 5)
P("U_72", R(72) / R(18, 5)); P("U_ERR", 72 * R(18, 5)); DEC("U_ERRD", 72 * R(18, 5), 1)

# esempio 1: s(t) = 2 t^2
t = sp.symbols("t", real=True); s = 2 * t**2
s1, s3 = s.subs(t, 1), s.subs(t, 3); assert (s1, s3) == (2, 18)
P("E_S1", s1); P("E_S3", s3); P("E_DS", s3 - s1); P("E_VM", (s3 - s1) / 2)
vi = sp.diff(s, t); assert vi.subs(t, 1) == 4 and vi.subs(t, 3) == 12 and vi.subs(t, 2) == 8
P("E_V1", vi.subs(t, 1)); P("E_V3", vi.subs(t, 3)); P("E_V2", vi.subs(t, 2))
assert (4 + 12) / 2 == 8

# tabella: t0 = 1, Δt variabile, s = 2 t^2
righe = []
for dt in (R(2), R(1), R(1, 2), R(1, 10), R(1, 100)):
    vmx = (s.subs(t, 1 + dt) - s.subs(t, 1)) / dt
    assert vmx == 4 + 2 * dt
    righe.append((dt, vmx))
fm = lambda v: (f"{float(v):.2f}".rstrip("0").rstrip(".") if v != int(v) else str(int(v))).replace(".", ",")
tab = ('<div class="tab-wrap"><table class="tab-num"><thead><tr><th>Intervallo Δt (s)</th><th>Da t = 1 s a t = …</th><th>Velocità media (m/s)</th></tr></thead><tbody>' +
       "".join(f"<tr><td>{fm(dt)}</td><td>{fm(1 + dt)}</td><td>{fm(vmx)}</td></tr>" for dt, vmx in righe) + "</tbody></table></div>")
RAW("TAB", "", tab)
assert [float(v) for _, v in righe] == [8, 6, 5, 4.2, 4.02]

# prova tu
assert R(45) / R(5, 2) == 18 and R(18) / R(18, 5) == 5
P("P1_V", R(45) / R(5, 2)); P("P1_MS", R(18) / R(18, 5))
ta, tr = R(120) / 60, R(120) / 120; v_perc = R(240) / (ta + tr)
assert (ta, tr, v_perc) == (2, 1, 80) and R(60 + 120, 2) == 90
P("P2_TA", ta); P("P2_TR", tr); P("P2_V", v_perc); P("P2_ERR", R(90))
f3 = lambda x: 3 * x**2
vm1 = (f3(R(21, 10)) - f3(2)) / R(1, 10); vm2 = (f3(R(201, 100)) - f3(2)) / R(1, 100)
assert (f3(R(21, 10)), vm1, vm2) == (R(1323, 100), R(123, 10), R(1203, 100)) and sp.diff(3 * t**2, t).subs(t, 2) == 12
DEC("P3_S21", f3(R(21, 10)), 2); DEC("P3_DS1", f3(R(21, 10)) - f3(2), 2); DEC("P3_VM1", vm1, 1)
DEC("P3_S201", f3(R(201, 100)), 4); DEC("P3_DS2", f3(R(201, 100)) - f3(2), 4); DEC("P3_VM2", vm2, 2); P("P3_VI", 12); P("P3_S2", f3(2))

# problema nuovo: 50 km a 50 km/h, poi media di 100 km/h su 100 km
t_usato = R(50) / 50; t_totale = R(100) / 100
assert t_usato == t_totale == 1 and t_totale - t_usato == 0
P("T_T1", t_usato); P("T_TOT", t_totale)

# widget: a=4, v0=0, t0=1, dt=2
js = f"const m=require({json.dumps(str(JS))});process.stdout.write(JSON.stringify({{fig:m.figura(4,0,1,2),txt:m.lettura(4,0,1,2)}}))"
o = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
RAW("M_SVG", "", o["fig"]); RAW("M_LETTURA", "", o["txt"])
assert "velocit\u00e0 media \u00e8 8 m/s" in o["txt"] and "istantanea \u00e8 4 m/s" in o["txt"]

FAQ = [
    ("La velocità media può essere zero?",
     "Sì. Se parti e torni al punto di partenza, lo spostamento complessivo è zero, quindi la velocità media (spostamento diviso tempo) è zero, anche se hai percorso molta strada. La velocità media calcolata come distanza totale diviso tempo totale, invece, non è zero.",
     "Sì. Se parti e torni al punto di partenza, lo spostamento complessivo è zero, quindi la velocità media (spostamento diviso tempo) è zero, anche se hai percorso molta strada. La velocità media calcolata come distanza totale diviso tempo totale, invece, non è zero."),
    ("Il tachimetro dell'auto misura la velocità media o istantanea?",
     "Misura la velocità istantanea: il valore che l'auto ha in quel momento. La velocità media la calcoli tu, dividendo la strada fatta per il tempo impiegato.",
     "Misura la velocità istantanea: il valore che l'auto ha in quel momento. La velocità media la calcoli tu, dividendo la strada fatta per il tempo impiegato."),
    ("Perché la velocità istantanea non si calcola con $\\Delta t=0$?",
     "Perché con $\\Delta t=0$ anche $\\Delta s$ vale zero e il rapporto diventa $0/0$, che non ha significato. La velocità istantanea è il valore a cui si avvicina la velocità media quando $\\Delta t$ diventa sempre più piccolo, non il risultato di una divisione per zero.",
     "Perché con Δt = 0 anche Δs vale zero e il rapporto diventa 0/0, che non ha significato. La velocità istantanea è il valore a cui si avvicina la velocità media quando Δt diventa sempre più piccolo, non il risultato di una divisione per zero."),
    ("Come passo da km/h a m/s e viceversa?",
     "Da km/h a m/s dividi per $3{,}6$: $72\\ \\text{km/h}=20\\ \\text{m/s}$. Da m/s a km/h moltiplichi per $3{,}6$. Il fattore viene da $1\\ \\text{km}=1000\\ \\text{m}$ e $1\\ \\text{h}=3600\\ \\text{s}$.",
     "Da km/h a m/s dividi per 3,6: 72 km/h = 20 m/s. Da m/s a km/h moltiplichi per 3,6. Il fattore viene da 1 km = 1000 m e 1 h = 3600 s."),
]
