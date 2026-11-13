from comuni import *

DATI = Dati()
P, RAW = DATI.put, DATI.raw
x = sp.symbols("x", real=True)

# aggancio: rettangolo con perimetro 20, lati x e 10-x, area > 21
area = lambda v: v * (10 - v)
assert [area(v) for v in (2, 4, 5, 8)] == [16, 24, 25, 16] and area(3) == area(7) == 21
for v, k in ((2, "A2"), (4, "A4"), (5, "A5"), (8, "A8")):
    P(k, area(v))
d, (r1, r2) = solve(1, -10, 21); assert (d, r1, r2) == (16, 3, 7)
iv = intervalli(1, -10, 21, "<"); assert [(float(a), float(b)) for a, b, *_ in iv] == [(3, 7)]
P("A_R1", r1); P("A_R2", r2)

# esempio 1: x^2 - x - 6 > 0
d, (e1, e2) = solve(1, -1, -6); assert (d, e1, e2) == (25, -2, 3)
P("E1_D", d); P("E1_B2", 1); P("E1_M4AC", 24); P("E1_SQ", sp.sqrt(d)); P("E1_X1", e1); P("E1_X2", e2)
assert testo_sol(intervalli(1, -1, -6, ">")) == f"x < {MINUS}2 oppure x > 3"
P("E1_F0", 0**2 - 0 - 6); P("E1_F4", 4**2 - 4 - 6); P("E1_FM3", 9 + 3 - 6)
assert (0 - 6 < 0) and (4**2 - 4 - 6 == 6) and (9 + 3 - 6 == 6)

# esempio 2: -x^2 + 4x - 3 >= 0   ->   x^2 - 4x + 3 <= 0
d, (f1, f2) = solve(1, -4, 3); assert (d, f1, f2) == (4, 1, 3)
assert testo_sol(intervalli(-1, 4, -3, ">=")) == f"1 ≤ x ≤ 3"
P("E2_D", d); P("E2_X1", f1); P("E2_X2", f2); P("E2_F2", -4 + 8 - 3); P("E2_F0", -3)
assert (-4 + 8 - 3 == 1) and (-3 < 0)
# errore del verso: x^2 - 4x + 3 >= 0 -> x <= 1 o x >= 3
assert testo_sol(intervalli(1, -4, 3, ">=")) == f"x ≤ 1 oppure x ≥ 3"

# casi particolari
assert testo_sol(intervalli(1, -4, 4, ">")) == "x ≠ 2"
assert testo_sol(intervalli(1, -4, 4, "<=")) == "x = 2"
assert testo_sol(intervalli(1, -4, 4, ">=")) == "tutti i numeri reali"
assert testo_sol(intervalli(1, -4, 4, "<")) == "nessuna soluzione"
d, s = solve(1, 1, 1); assert d == -3 and s == []
assert testo_sol(intervalli(1, 1, 1, ">")) == "tutti i numeri reali" and testo_sol(intervalli(1, 1, 1, "<")) == "nessuna soluzione"
P("Z_D", 0); P("N_D", d)

# prova tu
d, (a1, a2) = solve(2, -3, -2); assert (d, a1, a2) == (25, R(-1, 2), 2)
assert testo_sol(intervalli(2, -3, -2, ">")) == f"x < {MINUS}0,5 oppure x > 2"
P("P1_D", d); P("P1_B2", 9); P("P1_M4AC", 16); P("P1_SQ", sp.sqrt(d)); P("P1_X1", a1); P("P1_X2", a2)
d, (b1, b2) = solve(1, -2, -3); assert (d, b1, b2) == (16, -1, 3)
assert testo_sol(intervalli(-1, 2, 3, ">=")) == f"{MINUS}1 ≤ x ≤ 3"
P("P2_D", d); P("P2_X1", b1); P("P2_X2", b2)
assert testo_sol(intervalli(1, -6, 9, ">")) == "x ≠ 3"
d, (c0,) = solve(1, -6, 9); assert d == 0 and c0 == 3
P("P3_D", d); P("P3_X", c0)

# errori
assert testo_sol(intervalli(1, -1, -6, ">")) != f"{MINUS}2 < x < 3"
assert 0**2 - 0 - 6 == -6                       # x = 0 non soddisfa x^2 - x - 6 > 0
P("ER1_F0", -6)

# problema nuovo: h(t) = 1 + 8t - 5t^2 > 4
t = sp.symbols("t", real=True)
h = 1 + 8 * t - 5 * t**2
d, (t1, t2) = solve(5, -8, 3); assert (d, t1, t2) == (4, R(3, 5), 1)
S = sp.solve_univariate_inequality(h > 4, t, relational=False); assert S == sp.Interval.open(R(3, 5), 1)
P("T_D", d); P("T_T1", t1); P("T_T2", t2); P("T_DUR", t2 - t1)
assert h.subs(t, R(4, 5)) == R(21, 5) > 4 and h.subs(t, R(1, 2)) == R(15, 4) < 4
DATI.dec("T_T1D", t1, 1); DATI.dec("T_DURD", t2 - t1, 1)
DATI.dec("T_H08", h.subs(t, R(4, 5)), 1); DATI.dec("T_H05", h.subs(t, R(1, 2)), 2)

widget_disequazione(DATI, 1, -1, -6, ">", "Grafico della parabola y = x² − x − 6, rivolta verso l'alto, che incontra l'asse x in x = −2 e x = 3. Sono evidenziate sull'asse le zone x < −2 e x > 3, dove la parabola sta sopra l'asse.")

FAQ = [
    ("Qual è la differenza tra $>$ e $\\geq$ in una disequazione?",
     "Con $>$ i valori che annullano l'espressione non sono soluzioni: gli estremi sono esclusi (cerchio vuoto sul grafico). Con $\\geq$ gli estremi sono soluzioni e sono inclusi (cerchio pieno).",
     "Con > i valori che annullano l'espressione non sono soluzioni: gli estremi sono esclusi (cerchio vuoto sul grafico). Con ≥ gli estremi sono soluzioni e sono inclusi (cerchio pieno)."),
    ("Perché si inverte il verso quando moltiplico per $-1$?",
     "Perché moltiplicare per un numero negativo inverte l'ordine: $2<3$ ma $-2>-3$. Se moltiplichi entrambi i membri per $-1$, devi scambiare $>$ con $<$ (e $\\geq$ con $\\leq$).",
     "Perché moltiplicare per un numero negativo inverte l'ordine: 2 < 3 ma −2 > −3. Se moltiplichi entrambi i membri per −1, devi scambiare > con < (e ≥ con ≤)."),
    ("Come posso controllare di aver risolto bene?",
     "Scegli un numero in ogni zona dell'asse delimitata dalle radici e sostituiscilo nella disequazione originale: deve risultare vera solo nelle zone che hai indicato come soluzione. Controlla anche le radici, per capire se gli estremi sono inclusi.",
     "Scegli un numero in ogni zona dell'asse delimitata dalle radici e sostituiscilo nella disequazione originale: deve risultare vera solo nelle zone che hai indicato come soluzione. Controlla anche le radici, per capire se gli estremi sono inclusi."),
    ("Se il discriminante è negativo la disequazione non ha soluzioni?",
     "Dipende. Con $\\Delta<0$ la parabola non tocca l'asse $x$: sta tutta sopra o tutta sotto. Se $a>0$ è tutta sopra, quindi $>0$ vale per ogni $x$ e $<0$ non ha soluzioni. Se $a<0$ succede il contrario.",
     "Dipende. Con Δ < 0 la parabola non tocca l'asse x: sta tutta sopra o tutta sotto. Se a > 0 è tutta sopra, quindi > 0 vale per ogni x e < 0 non ha soluzioni. Se a < 0 succede il contrario."),
]
