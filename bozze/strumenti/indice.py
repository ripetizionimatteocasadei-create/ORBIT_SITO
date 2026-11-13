#!/usr/bin/env python3
"""Legge bozze/indice/albero.txt e produce:
 - bozze/indice/mappa_url.csv      (materia, livello, argomento, lezione, slug proposto, stato, formato)
 - bozze/indice/anteprima.html     (indice ad albero come sulla pagina blog, file unico per l'anteprima)
Uso: python3 indice.py
"""
import re, csv, json, html, unicodedata, base64, pathlib, collections

QUI = pathlib.Path(__file__).resolve().parent
R = QUI.parents[1]
D = R / "bozze" / "indice"
STOP = set("il lo la le gli i un una uno di del dello della dei degli delle e ed in a al alla alle ai con per su tra fra che cos è da dal come cosa".split())
FORM = {"S": "Simulazione", "M": "Animazione", "G": "Grafici", "T": "Testo"}


def slug(t, maxw=7):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    w = [x for x in re.findall(r"[a-z0-9]+", t) if x not in STOP or x in ("non",)]
    return "-".join(w[:maxw])


# ------------------------------------------------------------ parsing
mat = []  # lista di materie: {nome, livelli:[{nome, argomenti:[{nome, formati, lezioni:[{t, stato}]}]}]}
cur_m = cur_l = cur_a = None
for riga in (D / "albero.txt").read_text(encoding="utf-8").splitlines():
    if not riga.strip() or riga.startswith("//"):
        continue
    if riga.startswith("### "):
        nome, _, fmt = riga[4:].partition("|")
        cur_a = {"nome": nome.strip(), "formati": [f.strip() for f in fmt.split(",") if f.strip()], "lezioni": []}
        cur_l["argomenti"].append(cur_a)
    elif riga.startswith("## "):
        if cur_m["nome"] != "Università":
            cur_l = {"nome": riga[3:].strip(), "argomenti": []}
            cur_m["livelli"].append(cur_l)
    elif riga.startswith("# "):
        titolo = riga[2:].strip()
        sogg, _, resto = titolo.partition("·")
        sogg, resto = sogg.strip(), resto.strip()
        cur_m = next((m for m in mat if m["nome"] == sogg), None)
        if cur_m is None:
            cur_m = {"nome": sogg, "livelli": []}
            mat.append(cur_m)
        if sogg == "Università":
            cur_l = {"nome": resto, "argomenti": []}
            cur_m["livelli"].append(cur_l)
    elif riga.startswith("- "):
        t = riga[2:].strip()
        stato = ""
        if t.startswith("✓"):
            stato, t = "fatta", t[1:].strip()
        elif t.startswith("~"):
            stato, t = "bozza", t[1:].strip()
        elif t.startswith("*"):
            stato, t = "prossima", t[1:].strip()
        online = "(già online)" in t
        t = t.replace("(già online)", "").strip()
        cur_a["lezioni"].append({"t": t, "stato": "online" if online else stato})

# ------------------------------------------------------------ slug univoci
SOVR = {"Il discriminante: cos'è e cosa ti dice": "discriminante-equazione-secondo-grado",
        "Come risolvere le equazioni di secondo grado": "come-risolvere-equazioni-secondo-grado",
        "Il Metodo ORBIT: perché non ti do mai la soluzione subito": "il-metodo-orbit-perche-non-ti-do-mai-la-soluzione-subito"}
visti = collections.Counter()
for m in mat:
    for l in m["livelli"]:
        for a in l["argomenti"]:
            a["slug"] = slug(a["nome"], 5)
            for z in a["lezioni"]:
                s = SOVR.get(z["t"]) or slug(z["t"])
                visti[s] += 1
                z["slug"] = s
# duplicati: aggiungi il livello
for m in mat:
    for l in m["livelli"]:
        for a in l["argomenti"]:
            for z in a["lezioni"]:
                if visti[z["slug"]] > 1:
                    z["slug"] += "-" + slug(l["nome"], 3)
dup = collections.Counter(z["slug"] for m in mat for l in m["livelli"] for a in l["argomenti"] for z in a["lezioni"])
assert max(dup.values()) == 1, [k for k, v in dup.items() if v > 1]

# ------------------------------------------------------------ CSV
with (D / "mappa_url.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["materia", "livello", "argomento_guida", "lezione", "url_proposto", "stato", "formato"])
    for m in mat:
        for l in m["livelli"]:
            for a in l["argomenti"]:
                for z in a["lezioni"]:
                    w.writerow([m["nome"], l["nome"], a["nome"], z["t"], f"/blog/{z['slug']}/", {"fatta": "approvato", "bozza": "bozza in revisione", "online": "online", "prossima": "prima ondata"}.get(z["stato"], "in programma"), "+".join(a["formati"])])

tot_l = sum(len(a["lezioni"]) for m in mat for l in m["livelli"] for a in l["argomenti"])
tot_a = sum(len(l["argomenti"]) for m in mat for l in m["livelli"])
print(f"{len(mat)} aree, {tot_a} guide, {tot_l} lezioni")
for m in mat:
    n = sum(len(a["lezioni"]) for l in m["livelli"] for a in l["argomenti"])
    print(f"  {m['nome']}: {n}")

# ------------------------------------------------------------ HTML anteprima
b64 = lambda p, mime: f"data:{mime};base64," + base64.b64encode((R / p).read_bytes()).decode()
css = (R / "assets/css/v2.css").read_text(encoding="utf-8") + (R / "assets/css/v2-blog.css").read_text(encoding="utf-8")
css += """
:root{color-scheme:dark} html{background:#050B18} .reveal{opacity:1!important;transform:none!important}
.ind-hero{padding:130px 0 0;min-height:0!important} section.mat{min-height:0!important;padding:0!important} .ind-hero h1{font-family:var(--display);font-size:clamp(2rem,4.6vw,3.2rem);line-height:1.1;letter-spacing:-.02em;margin:14px 0}
.ind-hero p{color:var(--slate);max-width:640px}
.ind-stat{display:flex;gap:26px;flex-wrap:wrap;margin:22px 0 6px;font-family:var(--mono);font-size:.8rem;color:var(--slate)} .ind-stat b{color:var(--white);font-size:1.3rem;display:block;font-family:var(--display)}
.ind-tools{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:26px 0 8px}
.ind-tools input{flex:1 1 280px;min-height:48px;border-radius:14px;border:1px solid var(--line);background:var(--glass);color:var(--white);padding:0 18px;font:inherit}
.ind-tools input:focus{outline:2px solid var(--cyan);outline-offset:2px}
.ind-tools button{min-height:48px;padding:0 18px;border-radius:14px;border:1px solid var(--line);background:var(--glass);color:var(--white);font:inherit;cursor:pointer}
.ind-tools button:hover{background:var(--glass-hover)}
#esito{font-family:var(--mono);font-size:.78rem;color:var(--slate-light);margin:4px 0 0;min-height:1.2em}
.mat{margin:34px 0 0}
.mat > h2{font-family:var(--display);font-size:1.7rem;font-weight:600;display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:14px}
.mat > h2 small{font-family:var(--mono);font-size:.72rem;font-weight:400;color:var(--slate-light);letter-spacing:.04em}
details.liv{border:1px solid var(--line);border-radius:18px;background:var(--glass);margin:10px 0;overflow:hidden}
details.liv > summary{cursor:pointer;list-style:none;min-height:56px;display:flex;align-items:center;justify-content:space-between;gap:14px;padding:12px 22px;font-family:var(--display);font-weight:600;font-size:1.15rem}
details.liv > summary::-webkit-details-marker{display:none}
details.liv > summary::after{content:"+";font-family:var(--mono);color:var(--orange);font-size:1.4rem;flex:none}
details.liv[open] > summary::after{content:"\\2212"}
details.liv > summary:focus-visible{outline:2px solid var(--cyan);outline-offset:-2px}
.liv-n{font-family:var(--mono);font-size:.7rem;font-weight:400;color:var(--slate-light);margin-left:10px}
.arg-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;padding:4px 18px 20px}
.arg{border:1px solid var(--line);border-radius:14px;padding:16px 18px;background:rgba(255,255,255,.025)}
.arg h3{font-family:var(--display);font-size:1rem;font-weight:600;margin:0 0 8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.fm{font-family:var(--mono);font-size:.6rem;letter-spacing:.05em;text-transform:uppercase;border-radius:99px;padding:2px 8px;background:rgba(34,211,238,.1);color:var(--cyan);font-weight:400}
.arg ul{list-style:none;margin:0;padding:0}
.arg li{position:relative;padding:3px 0 3px 18px;font-size:.88rem;line-height:1.5;color:var(--slate)}
.arg li::before{content:"";position:absolute;left:3px;top:.85em;width:5px;height:5px;border-radius:50%;background:var(--slate-light)}
.arg li.fatta::before,.arg li.online::before{background:#34d399} .arg li.bozza::before{background:#FACC15} .arg li.bozza{color:var(--white)}
.tag.bozza{background:rgba(250,204,21,.14);color:#FACC15}
.arg li.prossima::before{background:var(--orange)}
.arg li.fatta,.arg li.online{color:var(--white)}
.arg li.prossima{color:var(--white)}
.tag{font-family:var(--mono);font-size:.58rem;letter-spacing:.05em;text-transform:uppercase;margin-left:8px;border-radius:99px;padding:1px 7px}
.tag.fatta,.tag.online{background:rgba(52,211,153,.14);color:#34d399}
.tag.prossima{background:rgba(242,129,29,.16);color:var(--orange-soft)}
.arg li.nasc,.arg.nasc,details.liv.nasc{display:none}
.legenda{display:flex;gap:18px;flex-wrap:wrap;font-family:var(--mono);font-size:.72rem;color:var(--slate);margin:8px 0 0}
.legenda i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
@media (max-width:760px){.arg-grid{grid-template-columns:1fr;padding:4px 12px 16px} details.liv > summary{padding:10px 16px;font-size:1.05rem}}
"""

def li(z):
    t = html.escape(z["t"])
    if z["stato"] == "fatta":
        t += '<span class="tag fatta">approvato</span>'
    elif z["stato"] == "online":
        t += '<span class="tag online">online</span>'
    elif z["stato"] == "bozza":
        t += '<span class="tag bozza">in revisione</span>'
    elif z["stato"] == "prossima":
        t += '<span class="tag prossima">prossima</span>'
    return f'<li class="{z["stato"]}" data-k="{html.escape(z["t"].lower())}">{t}</li>'


sez = []
for i, m in enumerate(mat):
    n_m = sum(len(a["lezioni"]) for l in m["livelli"] for a in l["argomenti"])
    liv = []
    for j, l in enumerate(m["livelli"]):
        n_l = sum(len(a["lezioni"]) for a in l["argomenti"])
        args = "".join(
            f'<div class="arg" data-k="{html.escape(a["nome"].lower())}"><h3>{html.escape(a["nome"])}' +
            "".join(f'<span class="fm">{FORM[f]}</span>' for f in a["formati"] if f in FORM) +
            f'</h3><ul>{"".join(li(z) for z in a["lezioni"])}</ul></div>'
            for a in l["argomenti"])
        aperto = " open" if (i == 0 and j == 1) or any(z["stato"] in ("fatta", "prossima") for a in l["argomenti"] for z in a["lezioni"]) and False else ""
        liv.append(f'<details class="liv"{aperto}><summary><span>{html.escape(l["nome"])}<span class="liv-n">{len(l["argomenti"])} guide · {n_l} lezioni</span></span></summary><div class="arg-grid">{args}</div></details>')
    sez.append(f'<section class="mat"><h2>{html.escape(m["nome"])}<small>{sum(len(l["argomenti"]) for l in m["livelli"])} guide · {n_m} lezioni</small></h2>{"".join(liv)}</section>')

nav = """<header><nav><a href="https://orbitripetizioni.it/" class="brand"><img src="%s" alt="" class="brand-mark"><span class="brand-word">ORBIT</span></a>
<div class="nav-links"><a href="https://orbitripetizioni.it/#chi-sono">Chi sono</a><a href="https://orbitripetizioni.it/#materie">Materie</a><a href="https://orbitripetizioni.it/#corsi">Corsi</a><a href="https://orbitripetizioni.it/blog/" class="active">Blog</a><a href="https://wa.me/393319241103" class="nav-cta">Scrivimi</a></div></nav></header>""" % b64("assets/img/logo-mark.png", "image/png")

JS = """
(function(){var q=document.getElementById('q'),es=document.getElementById('esito'),lv=[].slice.call(document.querySelectorAll('details.liv'));
function filtra(){var t=q.value.trim().toLowerCase(),n=0;
 lv.forEach(function(d){var tot=0;d.querySelectorAll('.arg').forEach(function(a){var ta=a.getAttribute('data-k').indexOf(t)>-1,m=0;
  a.querySelectorAll('li').forEach(function(l){var ok=!t||ta||l.getAttribute('data-k').indexOf(t)>-1;l.classList.toggle('nasc',!ok);if(ok){m++;}});
  a.classList.toggle('nasc',m===0);tot+=m;});
  d.classList.toggle('nasc',tot===0);if(t&&tot>0)d.open=true;n+=tot;});
 es.textContent=t?(n+(n===1?' lezione trovata':' lezioni trovate')):'';}
q.addEventListener('input',filtra);
document.getElementById('apri').addEventListener('click',function(){lv.forEach(function(d){d.open=true;});});
document.getElementById('chiudi').addEventListener('click',function(){lv.forEach(function(d){d.open=false;});});})();
"""

pagina = f"""<title>Blog ORBIT: tutte le guide</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{css}</style>
<div id="mesh"><div class="blob blob-1"></div><div class="blob blob-2"></div><div class="blob blob-3"></div></div>
{nav}
<div id="smooth-content"><main>
<section class="ind-hero"><div class="wrap">
  <span class="eyebrow">Blog · Indice delle guide</span>
  <h1>Matematica e fisica, <span class="gradient-text">dalla prima superiore all'università</span>.</h1>
  <p>Guide complete e lezioni singole, spiegate con il Metodo ORBIT: prima ragioni tu, poi la regola. Scegli la materia, il livello e l'argomento.</p>
  <div class="ind-stat"><div><b>{tot_a}</b>guide complete</div><div><b>{tot_l}</b>lezioni</div><div><b>{len(mat)}</b>aree</div></div>
  <div class="ind-tools"><input id="q" type="search" placeholder="Cerca una lezione (es. derivata, discriminante, urti…)" aria-label="Cerca una lezione"><button id="apri" type="button">Apri tutto</button><button id="chiudi" type="button">Chiudi tutto</button></div>
  <div id="esito" aria-live="polite"></div>
  <div class="legenda"><span><i style="background:#34d399"></i>approvata</span><span><i style="background:#FACC15"></i>bozza in revisione</span><span><i style="background:#F2811D"></i>prossima da scrivere</span><span><i style="background:#6B7690"></i>in programma</span></div>
</div></section>
<div class="wrap">
{''.join(sez)}
</div>
<div style="height:90px"></div>
</main></div>
<script>{JS}</script>
"""
(D / "anteprima.html").write_text(pagina, encoding="utf-8")
print("anteprima.html", len(pagina) // 1024, "KB")
