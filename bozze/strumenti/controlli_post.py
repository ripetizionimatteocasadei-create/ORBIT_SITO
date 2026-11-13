#!/usr/bin/env python3
"""Controlli del §9 delle conoscenze, una riga per controllo. Uso: python3 controlli_post.py [cartella-bozza]"""
import json, re, sys, pathlib, html
from html.parser import HTMLParser

QUI = pathlib.Path(__file__).resolve().parent
RADICE = QUI.parents[1]
BOZZA = RADICE / "bozze" / (sys.argv[1] if len(sys.argv) > 1 else "equazioni-secondo-grado")
META = json.loads((BOZZA / "meta.json").read_text(encoding="utf-8"))
PAGINA = RADICE / "blog" / META["slug"] / "index.html"
H = PAGINA.read_text(encoding="utf-8")


class P(HTMLParser):
    """Raccoglie il testo 'in prosa' (senza formule, svg, script, nav, footer)."""
    SKIP = {"script", "style", "svg", "header", "footer", "nav"}
    def __init__(s):
        super().__init__(); s.stack = []; s.testo = []; s.h1 = 0; s.imgs = []; s.links = []
    def handle_starttag(s, t, a):
        a = dict(a)
        void = t in ("img", "br", "meta", "link", "input", "line", "circle", "rect", "path")
        if t == "h1": s.h1 += 1
        if t == "img": s.imgs.append(a)
        if t == "a" and a.get("href"): s.links.append(a["href"])
        cl = (a.get("class") or "").split()
        if not void: s.stack.append((t, t == "figcaption" or bool({"katex", "eq-lettura", "eq-titolo", "fig-key", "correlati", "prova-n"} & set(cl))))
    def handle_endtag(s, t):
        for i in range(len(s.stack) - 1, -1, -1):
            if s.stack[i][0] == t:
                del s.stack[i:]; break
    def handle_data(s, d):
        if any(t in s.SKIP or k for t, k in s.stack): return
        if s.stack and s.stack[-1][0] == "title": return
        s.testo.append(d)


p = P(); p.feed(H)
corpo = H[H.index('<article'):H.index('</article>')]
q = P(); q.feed(corpo)
prosa = " ".join(q.testo)
parole = re.findall(r"[\wÀ-ÿ']+", prosa)
ok = True
def rep(nome, esito, dettaglio=""):
    global ok
    ok &= bool(esito)
    print(f"[{'OK ' if esito else 'NO '}] {nome}{(' — ' + dettaglio) if dettaglio else ''}")

# 1 frontmatter
chiavi = ["slug", "title", "description", "data", "tag", "cluster", "keyword", "keyword_secondarie", "og_image"]
rep("1 Metadati completi", all(META.get(k) for k in chiavi) and (RADICE / META["og_image"].lstrip("/")).exists(), "immagine social presente")
# 2 SEO on-page
tit = html.unescape(re.search(r"<title>(.*?)</title>", H).group(1))
des = html.unescape(re.search(r'<meta name="description" content="(.*?)"', H).group(1))
kw = META["keyword"].lower()
prime = " ".join(parole[:120]).lower()
rep("2a Un solo H1", p.h1 == 1)
rep("2b title <= 60 car.", len(html.unescape(tit)) <= 60, f"{len(html.unescape(tit))}")
rep("2c description <= 155 car.", len(html.unescape(des)) <= 155, f"{len(html.unescape(des))}")
h1txt = re.sub(r"<[^>]+>", "", META["h1_html"]).lower()
rep("2d keyword in title, H1, description e prime righe", kw in tit.lower() and kw in h1txt and kw in des.lower() and kw in prime)
rep("2e parole (prosa, formule escluse) 1200-2000", 1200 <= len(parole) <= 2000, f"{len(parole)} parole")
for need in ['rel="canonical"', 'lang="it"', 'og:image', 'BlogPosting', 'FAQPage', 'BreadcrumbList']:
    pass
rep("2f canonical, lang, og, JSON-LD (BlogPosting/Breadcrumb/FAQ)", all(x in H for x in ['rel="canonical"', '<html lang="it"', 'og:image', '"BlogPosting"', '"FAQPage"', '"BreadcrumbList"']))
# 3 link interni
interni = [l for l in q.links if not l.startswith(("http", "mailto", "#"))]
rotti = []
for l in interni:
    t = (PAGINA.parent / l.split("#")[0]).resolve()
    if t.is_dir(): t = t / "index.html"
    if not t.exists(): rotti.append(l)
rep("3 Link interni 3-6 e non rotti", 3 <= len(interni) <= 6 and not rotti, f"{len(interni)} link, rotti: {rotti or 'nessuno'}")
ancore = [l[1:] for l in q.links if l.startswith("#") and len(l) > 1]
rep("3b Ancore interne esistenti", all(f'id="{a}"' in H for a in ancore), ", ".join(ancore))
# 4 immagini
rep("4 Immagini con alt; figura SVG con aria-label", all(i.get("alt") is not None for i in p.imgs) and 'role="img" aria-label="' in H)
# 5 formule + calcoli
rep("5a Formule compilate da KaTeX (strict)", "katex-error" not in H and H.count('class="katex"') > 100, f"{H.count('class=\"katex\"')} formule")
rep("5b Nessun segnaposto rimasto", "<<" not in H and "$" not in prosa)
# 6 stile
vietate = [r"\bbanale\b", r"\bovvio\b", r"\bovviamente\b", r"\bè facile\b", r"\bfacilissim", r"\bgenio\b", r"\bporca", r"\bcazzo", r"\bmerda\b", r"!!"]
trovate = [v for v in vietate if re.search(v, prosa, re.I)]
wl = ["caspita", "cavolo", "mannaggia", "accidenti", "ops", "eh già", "urca", "ammettilo"]
n_int = sum(len(re.findall(rf"\b{w}\b", prosa, re.I)) for w in wl)
rep("6a Nessuna parola vietata", not trovate, ", ".join(trovate))
rep("6b Interiezioni solo whitelist, <= 2", n_int <= 2, f"{n_int}")
rep("6c Esclamativi <= 1", prosa.count("!") <= 1, f"{prosa.count('!')}")
sezioni = {"risposta breve": "La risposta breve", "aggancio": 'id="aggancio"', "prova tu": 'id="prova-tu"', "errori": 'id="errori"',
           "problema nuovo": 'id="problema-nuovo"', "in breve": 'id="in-breve"', "FAQ": 'id="faq"', "esempio svolto": 'id="esempio"', "CTA unica": "post-cta"}
mancano = [k for k, v in sezioni.items() if v not in H]
rep("6d Sezioni chiave presenti", not mancano, ", ".join(mancano))
rep("6e Un solo invito finale (1 CTA)", H.count('class="post-cta') == 1)
# 7 anti-copia: sequenze di 8 parole uguali a post esistenti e alle conoscenze
def seq(t, n=8):
    w = re.findall(r"[\wÀ-ÿ']+", t.lower()); return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
fonti = list((RADICE / "blog").glob("*/index.html")); fonti = [f for f in fonti if f != PAGINA]
fonti += list(pathlib.Path("/root/.claude/uploads").glob("**/*CONOSCENZE*.md"))
mie = seq(prosa); doppie_ext = set(); doppie_sito = set()
for f in fonti:
    t = f.read_text(encoding="utf-8", errors="ignore")
    if f.suffix == ".html":
        r = P(); r.feed(t); t = " ".join(r.testo); doppie_sito |= mie & seq(t)
    else:
        doppie_ext |= mie & seq(t)
rep("7a Anti-copia (8 parole uguali) vs fonti esterne e conoscenze", not doppie_ext, f"coincidenze: {len(doppie_ext)}")
rep("7b Somiglianza con gli altri post del sito (formule ricorrenti della scheda ammesse, max 40)", len(doppie_sito) <= 40, f"{len(doppie_sito)} sequenze")
# slug univoco
altri = [f.parent.name for f in (RADICE / "blog").glob("*/index.html")]
rep("7c Slug univoco / nessun conflitto di keyword", altri.count(META["slug"]) == 1)
print("\nESITO:", "tutti i controlli superati" if ok else "ci sono controlli da sistemare")
sys.exit(0 if ok else 1)
