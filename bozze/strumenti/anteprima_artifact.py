#!/usr/bin/env python3
"""Crea una pagina unica autosufficiente (CSS, font, JS, immagini incorporati) per vedere un post come anteprima.
Uso: python3 anteprima_artifact.py <slug> <file-di-uscita>"""
import re, base64, json, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[2]
slug, out = sys.argv[1], pathlib.Path(sys.argv[2])
H = (R / "blog" / slug / "index.html").read_text(encoding="utf-8")
meta = next(json.loads(p.read_text(encoding="utf-8")) for p in (R / "bozze").glob("*/meta.json") if json.loads(p.read_text(encoding="utf-8"))["slug"] == slug)
b64 = lambda p, m: f"data:{m};base64," + base64.b64encode((R / p).read_bytes()).decode()
css = ""
for f in ["assets/css/v2.css", "assets/css/v2-blog.css", "assets/vendor/katex/katex.min.css", "assets/css/v2-blog-math.css"]:
    c = (R / f).read_text(encoding="utf-8")
    if "katex" in f:
        c = re.sub(r"url\(fonts/([^)]+\.woff2)\)", lambda m: "url(" + b64("assets/vendor/katex/fonts/" + m.group(1), "font/woff2") + ")", c)
    css += c + "\n"
css += "\n:root{color-scheme:dark;} html{background:#050B18;} .reveal{opacity:1!important;transform:none!important;}\n"
body = H[H.index("<body>") + 6:H.index("</body>")]
body = re.sub(r"<script[\s\S]*?</script>", "", body)
body = re.sub(r'<div id="(cursor-glow|cursor-ring|cursor-dot|grain)"></div>\n?', "", body)
body = body.replace('onclick="window.orbitReopenCookiePrefs(); return false;"', "")
SITE = "https://orbitripetizioni.it"
body = re.sub(r'href="\.\./\.\./index\.html(#[^"]*)?"', lambda m: f'href="{SITE}/{m.group(1) or ""}"', body)
body = re.sub(r'href="\.\./\.\./privacy/index\.html"', f'href="{SITE}/privacy/"', body)
body = re.sub(r'href="\.\./([a-z0-9-]+)/"', lambda m: f'href="{SITE}/blog/{m.group(1)}/"', body)
body = re.sub(r'href="\.\./(index\.html)?"', f'href="{SITE}/blog/"', body)
body = body.replace('src="../../assets/img/logo-mark.png"', f'src="{b64("assets/img/logo-mark.png", "image/png")}"')
body = body.replace('src="../../assets/img/author-matteo.jpeg"', f'src="{b64("assets/img/author-matteo.jpeg", "image/jpeg")}"')
body = body.replace('<a href="#" >Preferenze cookie</a>', "")
assert "../" not in body.replace("https://", ""), re.findall(r'.{40}\.\./.{40}', body)[:3]
js = "\n".join((R / "assets" / "js" / n).read_text(encoding="utf-8") for n in meta.get("scripts", []))
titolo = sys.argv[3] if len(sys.argv) > 3 else "Anteprima post"
out.write_text(f"""<title>{titolo}</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
{css}
</style>
{body}
<script>
{js}
</script>
""", encoding="utf-8")
print(out, len(out.read_text(encoding="utf-8")) // 1024, "KB")
