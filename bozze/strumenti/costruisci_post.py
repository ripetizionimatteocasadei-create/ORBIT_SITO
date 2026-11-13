#!/usr/bin/env python3
"""Costruisce il post "Come risolvere le equazioni di secondo grado".

- calcola con sympy ogni numero che compare nel testo (niente conti a mente);
- pre-renderizza le formule con KaTeX (HTML completo, nessun JS per leggerle);
- genera l'SVG iniziale del grafico (lo stesso del widget);
- assembla la pagina nello stile del sito e scrive blog/<slug>/index.html.

Uso:  python3 bozze/strumenti/costruisci_post.py
"""
import json, re, subprocess, pathlib, html, datetime
import sympy as sp
from sympy import Rational as R

QUI = pathlib.Path(__file__).resolve().parent
RADICE = QUI.parents[1]
BOZZA = RADICE / "bozze" / "equazioni-secondo-grado"
META = json.loads((BOZZA / "meta.json").read_text(encoding="utf-8"))
SLUG = META["slug"]
URL = f"https://orbitripetizioni.it/blog/{SLUG}/"
MINUS = "−"


# ------------------------------------------------------------------ calcoli
def tex(v):
    return sp.latex(v).replace(".", "{,}")


def txt(v):
    """Numero in italiano per il testo normale: -1/2 -> −0,5; 3 -> 3."""
    v = sp.nsimplify(v)
    s = f"{float(v):.4f}".rstrip("0").rstrip(".").replace(".", ",")
    return s.replace("-", MINUS)


def V(v, plain=None):
    return {"tex": tex(v), "txt": plain if plain is not None else txt(v)}


def solve(a, b, c):
    x = sp.symbols("x", real=True)
    d = b * b - 4 * a * c
    sols = sorted(sp.solve(a * x**2 + b * x + c, x), key=lambda s: float(s))
    # controllo incrociato: formula a mano == sympy
    if d > 0:
        da_formula = sorted([(-b - sp.sqrt(d)) / (2 * a), (-b + sp.sqrt(d)) / (2 * a)], key=float)
        assert [sp.simplify(p - q) for p, q in zip(da_formula, sols)] == [0, 0]
    return d, sols


D = {}  # chiave -> {"tex","txt"}


def put(k, v, plain=None):
    D[k] = V(v, plain)


# rettangolo: x(10-x)=21
d, (r1, r2) = solve(1, -10, 21)
assert (d, r1, r2) == (16, 3, 7) and 3 * 7 == 21 and 2 * (3 + 7) == 20
put("RET_X1", r1); put("RET_X2", r2)
# area 30 impossibile
d30, s30 = solve(1, -10, 30)
assert d30 == -20 and s30 == []
put("P30_D", d30)

# esempio svolto 2x^2-5x-3
a, b, c = 2, -5, -3
d, (e1, e2) = solve(a, b, c)
assert (d, e1, e2) == (49, R(-1, 2), 3)
put("E_B2", b**2); put("E_M4AC", -4 * a * c); put("E_D", d); put("E_SQ", sp.sqrt(d))
put("E_X1", e1); put("E_X2", e2)
assert (5 - 7) / 4 == -0.5 and (5 + 7) / 4 == 3
put("E_X2SQ", e2**2); put("E_X2P", e2)
chk2 = 2 * e2**2 - 5 * e2 - 3
chk1 = R(1, 2) * R(1, 2) + R(5, 2) - 3  # 2*(1/4)+5/2-3 scritto passo passo nel testo
assert chk2 == 0 and 2 * e1**2 - 5 * e1 - 3 == 0 and 2 * R(1, 4) + R(5, 2) - 3 == 0
put("E_CHK2", chk2); put("E_CHK1", 0)
assert e1 + e2 == R(-b, a) and e1 * e2 == R(c, a)
put("E_SOMMA", R(-b, a)); put("E_PROD", R(c, a))
# errore 2: 5 +/- 7/4
err_hi, err_lo = 5 + R(7, 4), 5 - R(7, 4)
put("ERR2_X", err_hi, f"{txt(err_hi)} (e {txt(err_lo)})")

# giochi con lo slider: a=2, b=-5, c variabile
dc3, rc3 = solve(2, -5, 3)
dc4, rc4 = solve(2, -5, 4)
assert (dc3, rc3) == (1, [1, R(3, 2)]) and dc4 == -7 and 25 - 8 * 3 == 1 and 25 - 8 * 4 == -7
ccrit = R(25, 8)
assert 25 - 8 * ccrit == 0
put("G_C3", 3); put("G_C4", 4); put("G_D3", dc3); put("G_D4", dc4)
put("G_R3A", rc3[0]); put("G_R3B", rc3[1], "1,5"); put("G_CCRIT", ccrit, "3,125")
D["G_CCRIT"]["tex"] = "3{,}125"

# scorciatoie
_, (s1a, s1b) = solve(1, 0, -9)
_, (s2a, s2b) = solve(1, -3, 0)
assert (s1a, s1b, s2a, s2b) == (-3, 3, 0, 3)
put("S1_X1", s1a); put("S1_X2", s1b); put("S2_X1", s2a); put("S2_X2", s2b)

# esercizi
dA, (A1, A2) = solve(3, -1, -2)
assert (dA, A1, A2) == (25, R(-2, 3), 1) and 1 + 24 == 25
put("A_B2", 1); put("A_M4AC", 24); put("A_D", dA); put("A_SQ", sp.sqrt(dA)); put("A_X1", A1); put("A_X2", A2)
assert (1 + 5) / 6 == 1 and R(1 - 5, 6) == R(-2, 3)
dB, (B1,) = solve(4, -12, 9)
assert dB == 0 and B1 == R(3, 2) and 144 - 144 == 0 and sp.factor(4 * sp.Symbol("x")**2 - 12 * sp.Symbol("x") + 9) == (2 * sp.Symbol("x") - 3)**2
put("B_B2", 144); put("B_4AC", 144); put("B_D", 0); put("B_X", B1)
dC, sC = solve(1, 2, 5)
assert dC == -16 and 4 - 20 == -16 and sC == []
put("C_B2", 4); put("C_4AC", 20); put("C_D", dC)

# errore 4: x^2 = 3x
_, (z1, z2) = solve(1, -3, 0)
put("ERR4_X1", z1); put("ERR4_X2", z2)

# problema nuovo: h(t)=3+4t-5t^2
t = sp.symbols("t")
dT, (t_neg, t_pos) = solve(5, -4, -3)
assert dT == 76 and sp.simplify(t_pos - (2 + sp.sqrt(19)) / 5) == 0 and sp.simplify(t_neg - (2 - sp.sqrt(19)) / 5) == 0
assert abs((3 + 4 * t_pos - 5 * t_pos**2).evalf()) < 1e-12
assert float(t_neg) < 0 < float(t_pos) and (2 * 3 / 10) ** 0.5 < float(t_pos)  # caduta libera 0,77 s
put("T_B2", 16); put("T_M4AC", 60); put("T_D", dT)
D["T_TEX"] = {"tex": r"2\pm\sqrt{19}", "txt": "2±√19"}
put("T_T1", t_pos, f"{float(t_pos):.2f}".replace(".", ","))
put("T_T2", t_neg, f"{float(t_neg):.2f}".replace(".", ",").replace("-", MINUS))
D["T_T1"]["tex"] = f"{float(t_pos):.2f}".replace(".", "{,}")
D["T_T2"]["tex"] = f"{float(t_neg):.2f}".replace(".", "{,}").replace("-", "-")

# ------------------------------------------------------------------ figura iniziale (stessa geometria del widget JS)
W, H, XMIN, XMAX, YMIN, YMAX = 640, 400, -6, 6, -10, 10
sx = lambda x: (x - XMIN) / (XMAX - XMIN) * W
sy = lambda y: H - (y - YMIN) / (YMAX - YMIN) * H


def num_it(n):
    s = f"{round(float(n) * 1000) / 1000:g}".replace(".", ",")
    return s.replace("-", MINUS)


def svg_iniziale(a, b, c):
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
        for rr, lab, ldx in ((r1_, "x₁", -16), (r2_, "x₂", 16)):
            marks += (f'<circle class="eq-radice" cx="{sx(rr):.1f}" cy="{sy(0):.1f}" r="7"></circle>'
                      f'<text class="g-lab-radice" x="{sx(rr) + ldx:.1f}" y="{sy(0) + ldy:.1f}" text-anchor="middle" font-size="15">{lab}</text>')
    vdy = 24 if a > 0 else -14
    marks += (f'<circle class="eq-vertice" cx="{sx(xv):.1f}" cy="{sy(yv):.1f}" r="6"></circle>'
              f'<text class="g-lab-vertice" x="{sx(xv):.1f}" y="{sy(yv) + vdy:.1f}" text-anchor="middle" font-size="15">V</text>')
    alt = (f"Grafico della parabola y = 2x² − 5x − 3: è rivolta verso l'alto, incontra l'asse x nei punti x = −0,5 e x = 3 "
           f"e ha il vertice in basso, circa in (1,25; −6,1).")
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(alt)}" width="{W}" height="{H}">'
            f'<defs><clipPath id="eq-clip"><rect width="{W}" height="{H}"/></clipPath></defs>'
            f'<g>{grid}</g>'
            f'<line class="g-axis" x1="0" y1="{sy(0):.1f}" x2="{W}" y2="{sy(0):.1f}"/><line class="g-axis" x1="{sx(0):.1f}" y1="0" x2="{sx(0):.1f}" y2="{H}"/>'
            f'<g>{ticks}</g>'
            f'<path class="g-curva" data-eq="curva" clip-path="url(#eq-clip)" d="{"".join(pts)}"/>'
            f'<g data-eq="punti">{marks}</g></svg>')


assert abs(-b / (2 * a) - 1.25) < 1e-12 and abs(2 * 1.25**2 - 5 * 1.25 - 3 + 6.125) < 1e-12
D["W_EQ"] = {"tex": "", "txt": f"2x² {MINUS} 5x {MINUS} 3 = 0"}
D["W_SVG"] = {"tex": "", "txt": svg_iniziale(2, -5, -3)}
D["W_LETTURA"] = {"tex": "", "txt": f"Δ = 49 > 0: due soluzioni, x₁ = {MINUS}0,5 e x₂ = 3. La parabola taglia l’asse x in due punti."}

# ------------------------------------------------------------------ FAQ (html con math + testo semplice per JSON-LD)
FAQ = [
    ("Cosa significa che il discriminante è negativo?",
     "Significa che l'equazione non ha soluzioni reali: la parabola non incontra mai l'asse $x$. Non puoi scrivere due soluzioni con la radice di un numero negativo: ti fermi e scrivi \"nessuna soluzione reale\". (Esistono numeri più avanzati, i complessi, ma si studiano dopo.)",
     "Significa che l'equazione non ha soluzioni reali: la parabola non incontra mai l'asse x. Non si possono scrivere due soluzioni con la radice di un numero negativo: ci si ferma e si scrive nessuna soluzione reale."),
    ("Posso usare la formula risolutiva sempre?",
     "Sì, funziona per ogni equazione di secondo grado scritta in forma normale. Ma quando manca $b$ o manca $c$ ci sono scorciatoie più rapide (isolare $x^2$, oppure raccogliere $x$) e meno soggette a errori di segno.",
     "Sì, funziona per ogni equazione di secondo grado scritta in forma normale. Ma quando manca b o manca c ci sono scorciatoie più rapide: isolare x al quadrato oppure raccogliere x."),
    ("Perché con $\\Delta=0$ si parla di soluzione doppia?",
     "Perché le due soluzioni della formula, $\\dfrac{-b+\\sqrt{\\Delta}}{2a}$ e $\\dfrac{-b-\\sqrt{\\Delta}}{2a}$, coincidono: la radice di zero è zero. Sul grafico, la parabola tocca l'asse $x$ in un solo punto senza attraversarlo.",
     "Perché le due soluzioni della formula coincidono: la radice di zero è zero. Sul grafico, la parabola tocca l'asse x in un solo punto senza attraversarlo."),
    ("Cosa succede se $a$ è uguale a zero?",
     "Il termine $x^2$ sparisce e l'equazione diventa $bx+c=0$, cioè di primo grado: una retta, con una sola soluzione $x=-\\dfrac{c}{b}$ (se $b\\neq0$). Per questo nella forma normale si richiede $a\\neq0$.",
     "Il termine x al quadrato sparisce e l'equazione diventa di primo grado: una retta, con una sola soluzione x = −c/b (se b è diverso da zero). Per questo nella forma normale si richiede a diverso da zero."),
]
faq_html = ""
for q, ans, _ in FAQ:
    faq_html += f"  <details><summary><span>{q}</span></summary><div><p>{ans}</p></div></details>\n"
D["FAQ_HTML"] = {"tex": faq_html, "txt": faq_html}


# ------------------------------------------------------------------ sostituzione placeholder e formule
sorgente = (BOZZA / "sorgente.html").read_text(encoding="utf-8")
sorgente = sorgente.replace("<<FAQ_HTML>>", faq_html)  # le FAQ contengono $...$ e <<>>? (no <<>>), ma $...$ sì

MATH_RE = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$", re.S)
formule = []  # (tex, display)


def fix_tokens(s, key):
    def r(m):
        k = m.group(1)
        if k not in D:
            raise KeyError(f"placeholder sconosciuto: {k}")
        return D[k][key]
    return re.sub(r"<<(\w+)>>", r, s)


def pezzi(src):
    out, pos = [], 0
    for m in MATH_RE.finditer(src):
        out.append(("t", src[pos:m.start()]))
        if m.group(1) is not None:
            out.append(("M", m.group(1)))
        else:
            out.append(("m", m.group(2)))
        pos = m.end()
    out.append(("t", src[pos:]))
    return out


parti = []
for kind, s in pezzi(sorgente):
    if kind == "t":
        parti.append(("t", fix_tokens(s, "txt")))
    else:
        parti.append((kind, fix_tokens(s, "tex").strip()))
        formule.append({"tex": parti[-1][1], "display": kind == "M"})

# copia del sorgente con i numeri già risolti (serve allo strumento di revisione)
(BOZZA / "_risolto.html").write_text("".join(x if k == "t" else (f"$${x}$$" if k == "M" else f"${x}$") for k, x in parti), encoding="utf-8")

res = subprocess.run(["node", str(QUI / "katex_render.mjs")], input=json.dumps(formule), capture_output=True, text=True, cwd=QUI)
if res.returncode != 0:
    raise SystemExit("KaTeX ha rifiutato una formula:\n" + res.stderr)
rendered = iter(json.loads(res.stdout))
corpo = ""
for kind, s in parti:
    corpo += s if kind == "t" else next(rendered)

# ------------------------------------------------------------------ metadati e pagina
def senza_formule(h):
    """Toglie formule KaTeX, svg e script (conteggio bilanciato dei tag) per contare solo la prosa."""
    out, i = [], 0
    pat = re.compile(r'<span class="katex(?:-display)?">|<svg|<script')
    while True:
        m = pat.search(h, i)
        if not m:
            out.append(h[i:]); break
        out.append(h[i:m.start()])
        tag = "span" if m.group(0).startswith("<span") else ("svg" if "svg" in m.group(0) else "script")
        depth, j = 0, m.start()
        for t in re.finditer(rf"<{tag}\b|</{tag}>", h[j:]):
            depth += 1 if t.group(0).startswith("<" + tag) else -1
            if depth == 0:
                j += t.end(); break
        i = j
    return "".join(out)


testo_visibile = re.sub(r"<[^>]+>", " ", senza_formule(corpo))
n_parole = len(re.findall(r"[\wÀ-ÿ']+", html.unescape(testo_visibile)))
minuti = max(1, round(n_parole / 200))
data = META["data"]
mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
dd = datetime.date.fromisoformat(data)
data_it = f"{dd.day} {mesi[dd.month - 1]} {dd.year}"

jsonld = [
    {"@context": "https://schema.org", "@type": "BlogPosting", "headline": META["h1_plain"], "description": META["description"],
     "author": {"@type": "Person", "name": "Matteo Casadei", "url": "https://orbitripetizioni.it/#chi-sono"},
     "publisher": {"@type": "Organization", "name": "Orbit Ripetizioni", "logo": {"@type": "ImageObject", "url": "https://orbitripetizioni.it/assets/img/logo.png"}},
     "mainEntityOfPage": URL, "image": f"https://orbitripetizioni.it{META['og_image']}",
     "datePublished": data, "dateModified": data, "inLanguage": "it", "keywords": ", ".join([META["keyword"]] + META["keyword_secondarie"]),
     "wordCount": n_parole},
    {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://orbitripetizioni.it/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://orbitripetizioni.it/blog/"},
        {"@type": "ListItem", "position": 3, "name": META["h1_plain"], "item": URL}]},
    {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": re.sub(r"\$([^$]*)\$", lambda m: m.group(1).replace("\\Delta", "Δ"), q),
         "acceptedAnswer": {"@type": "Answer", "text": plain}} for q, _, plain in FAQ]},
]
jsonld_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(j, ensure_ascii=False, indent=2) + "\n</script>" for j in jsonld)

e = html.escape
pagina = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<link rel="icon" type="image/x-icon" href="../../favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="../../assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="../../assets/img/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="../../assets/img/apple-touch-icon.png">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(META['title'])}</title>
<meta name="description" content="{e(META['description'])}">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="article">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="Orbit Ripetizioni">
<meta property="og:url" content="{URL}">
<meta property="og:title" content="{e(META['h1_plain'])}">
<meta property="og:description" content="{e(META['description'])}">
<meta property="og:image" content="https://orbitripetizioni.it{META['og_image']}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(META['og_alt'])}">
<meta property="article:published_time" content="{data}">
<meta property="article:author" content="Matteo Casadei">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(META['h1_plain'])}">
<meta name="twitter:description" content="{e(META['description'])}">
<meta name="twitter:image" content="https://orbitripetizioni.it{META['og_image']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/v2.css">
<link rel="stylesheet" href="../../assets/css/v2-blog.css">
<link rel="stylesheet" href="../../assets/vendor/katex/katex.min.css">
<link rel="stylesheet" href="../../assets/css/v2-blog-math.css">
{jsonld_html}
</head>
<body>

<div id="mesh"><div class="blob blob-1"></div><div class="blob blob-2"></div><div class="blob blob-3"></div></div>
<div id="grain"></div>
<div id="cursor-glow"></div>
<div id="cursor-ring"></div>
<div id="cursor-dot"></div>
<div id="scroll-progress"></div>

<header>
  <nav>
    <a href="../../index.html#hero" class="brand">
      <img src="../../assets/img/logo-mark.png" alt="" class="brand-mark">
      <span class="brand-word">ORBIT</span>
    </a>
    <div class="nav-links">
      <a href="../../index.html#chi-sono">Chi sono</a>
      <a href="../../index.html#materie">Materie</a>
      <a href="../../index.html#corsi">Corsi</a>
      <a href="../index.html" class="active">Blog</a>
      <a href="https://wa.me/393319241103" class="nav-cta magnetic">Scrivimi</a>
    </div>
    <button class="nav-toggle" aria-label="Menu"><span></span></button>
  </nav>
</header>

<div id="smooth-spacer"></div>
<div id="smooth-content">
<main>

<section id="post-header">
  <div class="wrap blog-header-inner">
    <span class="eyebrow reveal"><svg class="eyebrow-orbit" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.2"/><circle class="eyebrow-orbit-dot" cx="8" cy="1.7" r="1.4"/></svg>Blog · Matematica</span>
    <h1 class="hero-title reveal" style="font-size:clamp(2rem, 4.4vw, 3.1rem);">{META['h1_html']}</h1>
    <div class="post-header-meta reveal">
      <span class="author"><img src="../../assets/img/author-matteo.jpeg" alt="Matteo Casadei" width="32" height="32"> Matteo Casadei</span>
      <span><time datetime="{data}">{data_it}</time></span>
      <span>{minuti} min di lettura</span>
    </div>
  </div>
</section>

<article class="post-body math-post">

{corpo}

</article>

<div class="post-cta reveal">
  <div class="glass">
    <h3>Vuoi farlo insieme su un tuo esercizio?</h3>
    <p>Scrivimi su WhatsApp: portami l'equazione che ti blocca e la guardiamo con il Metodo ORBIT, una domanda alla volta.</p>
    <a href="https://wa.me/393319241103" class="btn btn-primary magnetic">Scrivimi su WhatsApp →</a>
  </div>
</div>

</main>

<footer>
  <div class="wrap footer-inner">
    <div class="footer-brand"><img src="../../assets/img/logo-mark.png" alt="" class="brand-mark"><span class="brand-word">ORBIT</span></div>
    <div class="footer-links">
      <a href="../index.html">Altri articoli</a>
      <a href="https://wa.me/393319241103">WhatsApp</a>
      <a href="../../privacy/index.html">Privacy</a>
      <a href="#" onclick="window.orbitReopenCookiePrefs(); return false;">Preferenze cookie</a>
    </div>
  </div>
</footer>
</div><!-- /#smooth-content -->

<script>window.ORBIT_ASSET_PREFIX = "../../";</script>
<script src="../../assets/js/consent.js"></script>
<script src="../../assets/js/v2.js"></script>
<script src="../../assets/js/equazione2.js" defer></script>
</body>
</html>
"""
out = RADICE / "blog" / SLUG / "index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(pagina, encoding="utf-8")
print(f"scritto {out.relative_to(RADICE)}  parole≈{n_parole}  lettura≈{minuti} min  formule={len(formule)}")
