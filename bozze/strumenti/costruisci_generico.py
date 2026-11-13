#!/usr/bin/env python3
"""Costruttore generico: python3 costruisci_generico.py <cartella-in-bozze>
Legge bozze/<cartella>/{meta.json, sorgente.html, calcoli.py}; calcoli.py importa da comuni.py e definisce D (dati) e FAQ."""
import json, re, subprocess, pathlib, html, datetime, sys, runpy

QUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
RADICE = QUI.parents[1]
BOZZA = RADICE / "bozze" / sys.argv[1]
META = json.loads((BOZZA / "meta.json").read_text(encoding="utf-8"))
SLUG = META["slug"]
URL = f"https://orbitripetizioni.it/blog/{SLUG}/"
ns = runpy.run_path(str(BOZZA / "calcoli.py"))
D, FAQ = ns["DATI"].D, ns["FAQ"]
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
SCRIPTS = "\n".join(f'<script src="../../assets/js/{n}" defer></script>' for n in META.get("scripts", []))
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
{SCRIPTS}
</body>
</html>
"""
SCRIPTS_PLACEHOLDER = None
out = RADICE / "blog" / SLUG / "index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(pagina, encoding="utf-8")
print(f"scritto {out.relative_to(RADICE)}  parole≈{n_parole}  lettura≈{minuti} min  formule={len(formule)}")
