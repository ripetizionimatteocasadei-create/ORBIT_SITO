#!/usr/bin/env python3
"""Genera la pagina "Revisione bozza": il testo del post diviso in blocchi, modificabili,
con una nota per Claude sotto ogni blocco. Le modifiche stanno nel database dell'artifact
(collezione revisione_<REV>), le legge Claude con ArtifactData.

Uso: python3 revisione.py [cartella-bozza] [REV]   -> scrive revisione_<REV>.html nella cartella della bozza
"""
import re, sys, json, html, base64, subprocess, pathlib

QUI = pathlib.Path(__file__).resolve().parent
RADICE = QUI.parents[1]
BOZZA = RADICE / "bozze" / (sys.argv[1] if len(sys.argv) > 1 else "equazioni-secondo-grado")
REV = sys.argv[2] if len(sys.argv) > 2 else "r1"
META = json.loads((BOZZA / "meta.json").read_text(encoding="utf-8"))
SRC = (BOZZA / "_risolto.html").read_text(encoding="utf-8")
SRC = re.sub(r"<!--.*?-->", "", SRC, flags=re.S)

# ---------------------------------------------------------------- blocchi
PAT = re.compile(r"<(p|h2|h3|li|summary|figcaption)\b([^>]*)>(.*?)</\1>|<div>(<strong>.*?)</div>", re.S)
blocchi = []
for m in PAT.finditer(SRC):
    tag = m.group(1) or "div"
    attrs = m.group(2) or ""
    inner = (m.group(3) if m.group(1) else m.group(4)).strip()
    if "eq-titolo" in attrs or "eq-lettura" in attrs or "<svg" in inner or not inner:
        continue
    blocchi.append({"id": f"b{len(blocchi) + 1:03d}", "tag": tag, "classe": re.search(r'class="([^"]*)"', attrs).group(1) if "class=" in attrs else "", "src": inner})

# ---------------------------------------------------------------- formule -> KaTeX
MATH = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$", re.S)
formule = []
for b in blocchi:
    for m in MATH.finditer(b["src"]):
        formule.append({"tex": (m.group(1) or m.group(2)).strip(), "display": m.group(1) is not None})
r = subprocess.run(["node", str(QUI / "katex_render.mjs")], input=json.dumps(formule), capture_output=True, text=True, cwd=QUI)
if r.returncode:
    raise SystemExit(r.stderr)
rend = iter(json.loads(r.stdout))


def a_html(src):
    def sost(m):
        d = m.group(1) is not None
        tex = (m.group(1) or m.group(2)).strip()
        return f'<span class="mf{" mfd" if d else ""}" contenteditable="false" data-d="{1 if d else 0}" data-tex="{html.escape(tex, quote=True)}">{next(rend)}</span>'
    return MATH.sub(sost, src)


for b in blocchi:
    b["html"] = a_html(b["src"])
    b["etichetta"] = {"h2": "Titolo di sezione", "h3": "Sottotitolo", "li": "Elenco", "summary": "Domanda / aiuto", "figcaption": "Didascalia", "div": "Riquadro", "p": "Paragrafo"}[b["tag"]]

# ---------------------------------------------------------------- CSS (KaTeX con font incorporati: l'artifact non può caricarli da fuori)
def font(p):
    return "data:font/woff2;base64," + base64.b64encode((RADICE / "assets/vendor/katex/fonts" / p).read_bytes()).decode()


kcss = (RADICE / "assets/vendor/katex/katex.min.css").read_text(encoding="utf-8")
kcss = re.sub(r"url\(fonts/([^)]+\.woff2)\)", lambda m: f"url({font(m.group(1))})", kcss)

STILE = """
:root{
  --bg:#F6F7FA; --panel:#FFFFFF; --fg:#16202E; --muted:#5A6678; --line:#DDE2EA; --accent:#B8520A; --accent-soft:#FBE9DA;
  --ok:#0E7C66; --ok-soft:#DDF3EC; --mod:#B8520A; --focus:#1D5FD0;
  --display:'Space Grotesk',system-ui,sans-serif; --body:'Inter',system-ui,sans-serif; --mono:'IBM Plex Mono',ui-monospace,monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0A111D; --panel:#111B2B; --fg:#E7ECF4; --muted:#9AA7BE; --line:#223048; --accent:#F9A752; --accent-soft:#2A1D10;
  --ok:#5ED1B1; --ok-soft:#0F2A24; --mod:#F9A752; --focus:#7FB0FF; color-scheme:dark; } }
:root[data-theme="dark"]{
  --bg:#0A111D; --panel:#111B2B; --fg:#E7ECF4; --muted:#9AA7BE; --line:#223048; --accent:#F9A752; --accent-soft:#2A1D10;
  --ok:#5ED1B1; --ok-soft:#0F2A24; --mod:#F9A752; --focus:#7FB0FF; color-scheme:dark; }
*{box-sizing:border-box}
body{background:var(--bg); color:var(--fg); font-family:var(--body); font-size:16px; line-height:1.65; margin:0;
  padding-left:max(16px, env(safe-area-inset-left,0px)); padding-right:max(16px, env(safe-area-inset-right,0px)); padding-block:0 120px}
.wrap{max-width:760px; margin:0 auto}
header.top{position:sticky; top:env(safe-area-inset-top,0px); z-index:5; background:var(--bg); border-bottom:1px solid var(--line); margin:0 -16px; padding:12px 16px}
body::before{content:""; position:fixed; inset:0 0 auto; height:env(safe-area-inset-top,0px); background:var(--bg); z-index:10}
.bar{max-width:760px; margin:0 auto; display:flex; gap:12px; align-items:center; flex-wrap:wrap}
.bar h1{font-family:var(--display); font-size:1.05rem; margin:0; flex:1 1 220px; line-height:1.25}
.bar h1 small{display:block; font-family:var(--body); font-weight:400; color:var(--muted); font-size:.8rem}
.count{font-family:var(--mono); font-size:.76rem; color:var(--muted)}
button{font:inherit; cursor:pointer}
.go{background:var(--accent); color:#fff; border:0; border-radius:10px; padding:0 22px; min-height:44px; font-weight:600; font-family:var(--display); letter-spacing:.02em}
:root[data-theme="dark"] .go{color:#1A0E03}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]) .go{color:#1A0E03} }
.go:disabled{opacity:.5; cursor:default}
.go:focus-visible, .lnk:focus-visible, [contenteditable]:focus-visible, textarea:focus-visible{outline:2px solid var(--focus); outline-offset:2px}
.stato{max-width:760px; margin:8px auto 0; font-size:.86rem; color:var(--muted)}
.stato.ok{color:var(--ok)}
.guida{margin:22px 0; padding:16px 18px; background:var(--panel); border:1px solid var(--line); border-radius:14px; font-size:.92rem; color:var(--muted)}
.guida b{color:var(--fg)}
.guida ul{margin:8px 0 0; padding-left:20px}
.blk{position:relative; margin:0; padding:10px 14px 6px; border-left:3px solid transparent; border-radius:6px}
.blk:hover, .blk:focus-within{background:var(--panel)}
.blk.mod{border-left-color:var(--mod)}
.blk.hanota{border-left-color:var(--ok)}
.blk.mod.hanota{border-left-color:var(--mod)}
.et{font-family:var(--mono); font-size:.66rem; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin-bottom:2px; display:flex; gap:10px; align-items:center; flex-wrap:wrap}
.pill{border-radius:99px; padding:1px 8px; font-size:.64rem}
.pill.m{background:var(--accent-soft); color:var(--mod)}
.pill.n{background:var(--ok-soft); color:var(--ok)}
.t{outline:none; min-height:1.4em; overflow-wrap:anywhere}
.t[data-tag="h2"]{font-family:var(--display); font-size:1.45rem; line-height:1.3; font-weight:600; margin-top:28px}
.t[data-tag="h3"]{font-family:var(--display); font-size:1.15rem; font-weight:600}
.t[data-tag="summary"]{font-weight:600}
.t[data-tag="li"]::before{content:"•"; color:var(--accent); margin-right:8px}
.t[data-tag="figcaption"]{font-size:.9rem; color:var(--muted)}
.t strong{font-weight:700}
.t em{font-style:normal; color:var(--accent)}
.t a{color:var(--accent); text-decoration:underline}
.mf{display:inline-block; max-width:100%; overflow-x:auto; overflow-y:hidden; vertical-align:middle; user-select:none; cursor:default; border-radius:4px}
.mf.mfd{display:block; margin:6px 0; text-align:center}
.mf .katex{font-size:1.05em}
.mf .katex-display{margin:2px 0}
.azioni{display:flex; gap:14px; align-items:center; min-height:34px}
.lnk{background:none; border:0; color:var(--muted); font-size:.82rem; padding:6px 0; min-height:34px; text-decoration:underline; text-underline-offset:3px}
.lnk:hover{color:var(--fg)}
.azioni{opacity:0; transition:opacity .15s}
.blk:hover .azioni, .blk:focus-within .azioni, .blk.hanota .azioni, .blk.mod .azioni{opacity:1}
@media (hover:none){ .azioni{opacity:1} }
.nota{display:none; margin:4px 0 8px}
.blk.nota-aperta .nota{display:block}
.nota label{display:block; font-size:.76rem; color:var(--muted); font-family:var(--mono); margin-bottom:4px}
textarea{width:100%; min-height:76px; resize:vertical; font:inherit; font-size:.95rem; color:var(--fg); background:var(--bg); border:1px solid var(--line); border-radius:10px; padding:10px 12px}
.gen{margin:28px 0 0; padding:16px 18px; background:var(--panel); border:1px solid var(--line); border-radius:14px}
.gen label{display:block; font-family:var(--display); font-weight:600; margin-bottom:6px}
.fine{margin-top:34px; padding:18px; border:1px dashed var(--line); border-radius:14px; text-align:center}
@media (prefers-reduced-motion: reduce){ *{transition:none!important} }
"""

# ---------------------------------------------------------------- HTML
righe = []
for b in blocchi:
    righe.append(
        f'<section class="blk" data-id="{b["id"]}" data-tag="{b["tag"]}">'
        f'<div class="et"><span>{b["etichetta"]}</span><span class="pill m" hidden>modificato</span><span class="pill n" hidden>con nota</span></div>'
        f'<div class="t" data-tag="{b["tag"]}" contenteditable="true" spellcheck="true" lang="it" role="textbox" aria-multiline="false" aria-label="{b["etichetta"]} {b["id"]}">{b["html"]}</div>'
        f'<div class="azioni"><button class="lnk" data-a="nota" type="button">Nota per Claude</button>'
        f'<button class="lnk" data-a="ripristina" type="button" hidden>Ripristina testo originale</button></div>'
        f'<div class="nota"><label for="n-{b["id"]}">Cosa vuoi che faccia qui? (es. «sviluppa di più», «più semplice», «cambia esempio»)</label>'
        f'<textarea id="n-{b["id"]}" rows="3"></textarea></div></section>'
    )

JS = r"""
(function(){
  "use strict";
  var REV = "__REV__", COLL = "revisione_" + REV;
  var blocks = Array.prototype.slice.call(document.querySelectorAll(".blk"));
  var elStato = document.getElementById("stato"), elCount = document.getElementById("count"), btnGo = document.getElementById("vai");
  var gen = document.getElementById("generale");
  var db = null, salvati = {}, timers = {}, inviato = false;

  function norm(s){ return (s||"").replace(/ /g," ").replace(/\s+/g," ").trim(); }
  function esc(s){ return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function ser(node){
    var out = "";
    node.childNodes.forEach(function(n){
      if (n.nodeType === 3) { out += esc(n.nodeValue); return; }
      if (n.nodeType !== 1) return;
      if (n.classList.contains("mf")) { var t = n.getAttribute("data-tex"); out += n.getAttribute("data-d") === "1" ? "$$" + t + "$$" : "$" + t + "$"; return; }
      var tag = n.tagName.toLowerCase();
      if (tag === "br") { out += " "; return; }
      var inner = ser(n);
      if (tag === "b" || tag === "strong") out += "<strong>" + inner + "</strong>";
      else if (tag === "i" || tag === "em") out += "<em>" + inner + "</em>";
      else if (tag === "a") out += '<a href="' + (n.getAttribute("href")||"").replace(/"/g,"&quot;") + '">' + inner + "</a>";
      else out += inner;
    });
    return out;
  }
  function stato(b){
    var t = b.querySelector(".t");
    var orig = b.__orig, ora = norm(ser(t));
    return { testo: ora, mod: ora !== orig, nota: b.querySelector("textarea").value.trim() };
  }
  blocks.forEach(function(b){ b.__orig = norm(ser(b.querySelector(".t"))); b.__origHtml = b.querySelector(".t").innerHTML; });

  function aggiorna(){
    var nm = 0, nn = 0;
    blocks.forEach(function(b){
      var s = stato(b);
      b.classList.toggle("mod", s.mod); b.classList.toggle("hanota", !!s.nota);
      b.querySelector(".pill.m").hidden = !s.mod; b.querySelector(".pill.n").hidden = !s.nota;
      b.querySelector('[data-a="ripristina"]').hidden = !s.mod;
      if (s.nota) b.classList.add("nota-aperta");
      if (s.mod) nm++; if (s.nota) nn++;
    });
    var g = gen.value.trim() ? 1 : 0;
    elCount.textContent = nm + (nm === 1 ? " modifica" : " modifiche") + " · " + nn + (nn === 1 ? " nota" : " note") + (g ? " · nota generale" : "");
    btnGo.disabled = (nm + nn + g) === 0;
    return { nm: nm, nn: nn, g: g };
  }

  function salva(b){
    if (!db) return;
    var id = b.getAttribute("data-id"), s = stato(b);
    var doc = { id: id, tag: b.getAttribute("data-tag"), originale: b.__orig, testo: s.testo, modificato: s.mod, nota: s.nota, aggiornato: new Date().toISOString() };
    var chiave = JSON.stringify([doc.testo, doc.nota]);
    if (salvati[id] === chiave) return;
    if (!s.mod && !s.nota && salvati[id] === undefined) return;
    salvati[id] = chiave;
    db.doc(COLL + "/" + id).set(doc).then(function(){ mostra("Salvato", false); }, function(e){ salvati[id] = undefined; mostra("Non riesco a salvare (" + (e && e.code || "errore") + "). Riprova tra poco.", false); });
  }
  function mostra(t, ok){ elStato.textContent = t; elStato.classList.toggle("ok", !!ok); }
  function differisci(b){ var id = b.getAttribute("data-id"); clearTimeout(timers[id]); timers[id] = setTimeout(function(){ salva(b); }, 900); }

  blocks.forEach(function(b){
    var t = b.querySelector(".t"), ta = b.querySelector("textarea");
    t.addEventListener("input", function(){ inviato = false; aggiorna(); differisci(b); });
    t.addEventListener("keydown", function(e){ if (e.key === "Enter") { e.preventDefault(); } });
    t.addEventListener("paste", function(e){ e.preventDefault(); var txt = (e.clipboardData || window.clipboardData).getData("text").replace(/\s+/g," "); document.execCommand("insertText", false, txt); });
    ta.addEventListener("input", function(){ inviato = false; aggiorna(); differisci(b); });
    b.addEventListener("click", function(e){
      var a = e.target.closest("[data-a]"); if (!a) return;
      if (a.getAttribute("data-a") === "nota") { b.classList.toggle("nota-aperta"); if (b.classList.contains("nota-aperta")) ta.focus(); }
      if (a.getAttribute("data-a") === "ripristina") { t.innerHTML = b.__origHtml; aggiorna(); salva(b); }
    });
  });
  var tg;
  gen.addEventListener("input", function(){ inviato = false; aggiorna(); clearTimeout(tg); tg = setTimeout(function(){
    if (db) db.doc(COLL + "/generale").set({ testo: gen.value.trim(), aggiornato: new Date().toISOString() }).then(function(){ mostra("Salvato", false); }, function(){ mostra("Non riesco a salvare la nota generale.", false); });
  }, 900); });

  btnGo.addEventListener("click", function(){
    if (!db) { mostra("Per inviare devi essere collegato (apri la pagina dal link dell'artifact).", false); return; }
    blocks.forEach(function(b){ clearTimeout(timers[b.getAttribute("data-id")]); salva(b); });
    var c = aggiorna();
    btnGo.disabled = true;
    db.doc(COLL + "/richiesta").set({ inviata: new Date().toISOString(), modifiche: c.nm, note: c.nn, generale: c.g, rev: REV }).then(function(){
      inviato = true; var d = new Date(); mostra("Inviato alle " + d.getHours() + ":" + ("0" + d.getMinutes()).slice(-2) + ". Adesso scrivi «vai» a Claude nella chat.", true); btnGo.disabled = false;
    }, function(){ mostra("Invio non riuscito, riprova.", false); btnGo.disabled = false; });
  });

  // carica quello che hai già scritto (anche da un'altra sessione)
  function carica(){
    var tmo = setTimeout(function(){ mostra("Il salvataggio non risponde: puoi scrivere comunque, ma controlla prima di inviare.", false); }, 10000);
    db.collection(COLL).get().then(function(snap){
      clearTimeout(tmo);
      snap.docs.forEach(function(d){
        var v = d.data() || {};
        if (d.id === "generale") { gen.value = v.testo || ""; return; }
        if (d.id === "richiesta") return;
        var b = document.querySelector('.blk[data-id="' + d.id + '"]'); if (!b) return;
        if (v.modificato && typeof v.testo === "string") {
          var t = b.querySelector(".t");
          // ricostruisce il testo salvato: le formule restano chip non modificabili
          var chips = {}; b.querySelectorAll(".mf").forEach(function(m){ chips[(m.getAttribute("data-d")==="1"?"$$":"$") + m.getAttribute("data-tex") + (m.getAttribute("data-d")==="1"?"$$":"$")] = m.outerHTML; });
          t.innerHTML = v.testo.replace(/\$\$[^$]+\$\$|\$[^$]+\$/g, function(x){ return chips[x] || x; });
        }
        if (v.nota) b.querySelector("textarea").value = v.nota;
        salvati[d.id] = JSON.stringify([norm(v.testo), v.nota || ""]);
      });
      aggiorna();
    }, function(){ clearTimeout(tmo); mostra("Non riesco a leggere le note salvate.", false); });
  }
  aggiorna();
  (window.claude && window.claude.use ? window.claude.use("db") : Promise.resolve(null)).then(function(x){
    db = x; if (!db) { mostra("Salvataggio non disponibile in questa vista: puoi modificare, ma non inviare.", false); return; }
    carica();
  }, function(){ mostra("Salvataggio non disponibile.", false); });
})();
""".replace("__REV__", REV)

pagina = f"""<title>Revisione bozza</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
{kcss}
{STILE}
</style>
<header class="top">
  <div class="bar">
    <h1>Revisione bozza<small>{html.escape(META["h1_plain"])}</small></h1>
    <span class="count" id="count">0 modifiche · 0 note</span>
    <button class="go" id="vai" type="button" disabled>Vai</button>
  </div>
  <div class="stato" id="stato" role="status" aria-live="polite">Le modifiche si salvano da sole. Quando hai finito premi «Vai».</div>
</header>
<main class="wrap">
  <div class="guida">
    <b>Come si usa</b>
    <ul>
      <li>Clicca su un testo e scrivi: cambi le parole direttamente. Le formule non si modificano da qui: lascia una nota.</li>
      <li>Sotto ogni blocco c'è <b>Nota per Claude</b>: scrivi cosa vuoi (per esempio «sviluppa di più», «troppo lungo», «metti un esempio»).</li>
      <li>Quando hai finito premi <b>Vai</b>, poi scrivi «vai» a Claude nella chat: applico tutto, ricostruisco il post e ti rimando la pagina aggiornata.</li>
    </ul>
  </div>
{chr(10).join(righe)}
  <div class="gen"><label for="generale">Nota generale (tono, ordine, cosa manca, cosa togliere)</label><textarea id="generale" rows="4"></textarea></div>
  <div class="fine">Hai finito? Premi <b>Vai</b> in alto, poi scrivi «vai» a Claude.</div>
</main>
<script>
{JS}
</script>
"""
out = BOZZA / f"revisione_{REV}.html"
out.write_text(pagina, encoding="utf-8")
(BOZZA / f"_blocchi_{REV}.json").write_text(json.dumps(blocchi, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{out.name}: {len(blocchi)} blocchi, {len(pagina) // 1024} KB")
