from comuni import *

DATI = Dati()
P, RAW, DEC = DATI.put, DATI.raw, DATI.dec

# aggancio: x^2 - 4x + c
for c in (3, 4, 5):
    d, s = solve(1, -4, c)
    assert d == 16 - 4 * c
    P(f"A_D{c}", d)
    P(f"A_V{c}", R(c - 4))        # ordinata del vertice = -D/(4a)
    assert R(c - 4) == R(-d, 4)
_, (r1, r3) = solve(1, -4, 3); assert (r1, r3) == (1, 3)
_, (r2,) = solve(1, -4, 4); assert r2 == 2
_, s5 = solve(1, -4, 5); assert s5 == []
P("A_R1", r1); P("A_R3", r3); P("A_R2", r2)

# casi del discriminante con tre esempi
d, (x1, x2) = solve(1, -5, 6); assert d == 1 and (x1, x2) == (2, 3)
P("C1_D", d); P("C1_X1", x1); P("C1_X2", x2)
d, _ = solve(1, -4, 4); assert d == 0; P("C2_D", d)
d, s = solve(1, 2, 3); assert d == -8 and s == []; P("C3_D", d)

# irrazionale
d, (u1, u2) = solve(1, -2, -1); assert d == 8 and sp.simplify(u2 - (1 + sp.sqrt(2))) == 0
P("I_D", d)

# vertice e discriminante: y_V = -D/(4a), controllo su 2x^2+3x-5
a, b, c = 2, 3, -5
d, (e1, e2) = solve(a, b, c)
xv = R(-b, 2 * a); yv = a * xv**2 + b * xv + c
assert yv == R(-d, 4 * a)
P("E_B2", b**2); P("E_M4AC", -4 * a * c); P("E_D", d); P("E_SQ", sp.sqrt(d))
assert (d, e1, e2) == (49, R(-5, 2), 1)
P("E_X1", e1); P("E_X2", e2)
assert 2 * 1**2 + 3 * 1 - 5 == 0 and 2 * e1**2 + 3 * e1 - 5 == 0
P("E_X1SQ", e1**2); P("E_V", yv)
P("E_P", R(c, a)); assert e1 * e2 == R(c, a)
RAW("E_CHK1", "2\\cdot\\frac{25}{4}-\\frac{15}{2}-5=\\frac{25}{2}-\\frac{15}{2}-5=0", "")
assert R(25, 2) - R(15, 2) - 5 == 0

# scorciatoia Delta/4: x^2 - 6x + 5
d, (s1, s2) = solve(1, -6, 5); assert d == 16 and (s1, s2) == (1, 5)
assert (R(-6, 2))**2 - 1 * 5 == R(d, 4) == 4
P("S_D", d); P("S_D4", R(d, 4)); P("S_X1", s1); P("S_X2", s2); P("S_B2", R(-6, 2)**2); P("S_AC", 5)

# prova tu
d, (p1, p2) = solve(1, -6, 8); assert (d, p1, p2) == (4, 2, 4) and 36 - 32 == 4
P("P1_B2", 36); P("P1_4AC", 32); P("P1_D", d); P("P1_SQ", sp.sqrt(d)); P("P1_X1", p1); P("P1_X2", p2)
d, (q,) = solve(4, 4, 1); assert d == 0 and q == R(-1, 2) and 16 - 16 == 0
P("P2_B2", 16); P("P2_4AC", 16); P("P2_D", d); P("P2_X", q)
d, s = solve(1, -3, 4); assert d == -7 and s == [] and 9 - 16 == -7
P("P3_B2", 9); P("P3_4AC", 16); P("P3_D", d)

# errori
assert (-5)**2 - 4 * 1 * 4 == 9 and -(5**2) - 16 == -41
P("ER1_OK", 9); P("ER1_BAD", -41)
assert 3**2 - 4 * 2 * (-5) == 49 and 3**2 - 40 == -31
P("ER2_BAD", -31)
d, (z,) = solve(1, -4, 4); assert d == 0 and z == 2
P("ER3_X", z)
d, s = solve(1, -4, 5); assert d == -4 and s == []
P("ER4_D", d)

# problema nuovo: x^2 + k x + 4 = 0
k = sp.symbols("k")
Dk = sp.expand(k**2 - 16)
assert sp.solve(Dk, k) == [-4, 4]
for kv, (dd, sol) in {4: solve(1, 4, 4), -4: solve(1, -4, 4)}.items():
    assert dd == 0 and sol == [R(-kv, 2)]
P("T_XP", R(-4, 2)); P("T_XM", R(4, 2))
d0, s0 = solve(1, 0, 4); assert d0 == -16 and s0 == []
d5, (m1, m2) = solve(1, 5, 4); assert (d5, m1, m2) == (9, -4, -1)
P("T_D0", d0); P("T_D5", d5); P("T_M1", m1); P("T_M2", m2)

# widget: a=1, b=-4, c=3
widget_parabola(DATI, 1, -4, 3, "Grafico della parabola y = x² − 4x + 3: è rivolta verso l'alto, incontra l'asse x nei punti x = 1 e x = 3 e ha il vertice in (2, −1).")

FAQ = [
    ("Perché si chiama discriminante?",
     "Perché discrimina, cioè distingue i casi: dal suo segno capisci se l'equazione ha due soluzioni, una sola o nessuna soluzione reale, senza risolverla.",
     "Perché discrimina, cioè distingue i casi: dal suo segno capisci se l'equazione ha due soluzioni, una sola o nessuna soluzione reale, senza risolverla."),
    ("Cosa significa che il discriminante è un quadrato perfetto?",
     "Se i coefficienti sono interi e $\\Delta$ è il quadrato di un numero intero (come 1, 4, 9, 49), la radice si calcola esattamente e le soluzioni sono numeri razionali, cioè interi o frazioni. Se non lo è, le soluzioni contengono una radice che non si semplifica.",
     "Se i coefficienti sono interi e Δ è il quadrato di un numero intero, la radice si calcola esattamente e le soluzioni sono numeri razionali, cioè interi o frazioni. Se non lo è, le soluzioni contengono una radice che non si semplifica."),
    ("Il discriminante funziona anche se $a$ è negativo?",
     "Sì. Il segno di $\\Delta$ dice quante soluzioni reali ci sono, qualunque sia il segno di $a$. Il segno di $a$ cambia solo la direzione della parabola: verso l'alto o verso il basso.",
     "Sì. Il segno di Δ dice quante soluzioni reali ci sono, qualunque sia il segno di a. Il segno di a cambia solo la direzione della parabola: verso l'alto o verso il basso."),
    ("Quando conviene usare $\\dfrac{\\Delta}{4}$?",
     "Quando $b$ è un numero pari. I numeri sono più piccoli e le frazioni si semplificano prima, quindi sbagli meno.",
     "Quando b è un numero pari. I numeri sono più piccoli e le frazioni si semplificano prima, quindi sbagli meno."),
]
