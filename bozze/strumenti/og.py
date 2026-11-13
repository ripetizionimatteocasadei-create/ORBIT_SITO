#!/usr/bin/env python3
"""Immagine social 1200x630 per un post. Uso: python3 og.py <slug> "<kicker>" "<titolo con <span>>" <motivo>
motivi: parabola | disequazione | moto"""
import sys, subprocess, pathlib, json, tempfile
QUI = pathlib.Path(__file__).resolve().parent
R = QUI.parents[1]
slug, kicker, titolo, motivo = sys.argv[1:5]

def path(f, x0, x1, step=0.05, ylim=12):
    d, x = "", x0
    while x <= x1 + 1e-9:
        y = -f(x)
        if abs(y) <= ylim:
            d += ("L" if d else "M") + f"{x:.2f} {y:.2f}"
        x += step
    return d

if motivo == "parabola":
    f = lambda x: x * x - 4 * x + 3
    corpo = (f'<path d="{path(f,-6,8)}" fill="none" stroke="#F2811D" stroke-width=".16" stroke-linecap="round"/>'
             '<circle cx="2" cy="1" r=".26" fill="#7C6CF9" stroke="#050B18" stroke-width=".08"/>'
             '<circle cx="1" cy="0" r=".3" fill="#22D3EE" stroke="#050B18" stroke-width=".08"/><circle cx="3" cy="0" r=".3" fill="#22D3EE" stroke="#050B18" stroke-width=".08"/>')
    vb = "-6 -10 12 20"
elif motivo == "disequazione":
    f = lambda x: x * x - x - 6
    corpo = ('<path d="M-6 0H-2M3 0H6" stroke="#22D3EE" stroke-width=".42" stroke-linecap="round"/>'
             f'<path d="{path(f,-6,6)}" fill="none" stroke="#F2811D" stroke-width=".16" stroke-linecap="round"/>'
             '<circle cx="-2" cy="0" r=".3" fill="#050B18" stroke="#22D3EE" stroke-width=".12"/><circle cx="3" cy="0" r=".3" fill="#050B18" stroke="#22D3EE" stroke-width=".12"/>')
    vb = "-6 -10 12 20"
else:
    f = lambda t: 2 * t * t
    corpo = (f'<path d="{path(f,0,3.1,ylim=20)}" fill="none" stroke="#F2811D" stroke-width=".07" stroke-linecap="round"/>'
             '<path d="M1 -2L3 -18" stroke="#22D3EE" stroke-width=".05" opacity=".9"/><path d="M0 4L2 -4" stroke="#7C6CF9" stroke-width=".05"/>'
             '<circle cx="1" cy="-2" r=".11" fill="#7C6CF9"/><circle cx="3" cy="-18" r=".11" fill="#22D3EE"/>')
    vb = "-.5 -21 4 23"
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;width:1200px;height:630px;background:#050B18;font-family:'Space Grotesk','Inter',sans-serif;color:#fff;position:relative;overflow:hidden}}
.b1{{position:absolute;width:620px;height:620px;border-radius:50%;background:radial-gradient(circle,#F2811D 0%,transparent 70%);top:-220px;left:-160px;opacity:.55;filter:blur(40px)}}
.b2{{position:absolute;width:560px;height:560px;border-radius:50%;background:radial-gradient(circle,#7C6CF9 0%,transparent 70%);bottom:-260px;right:-100px;opacity:.5;filter:blur(40px)}}
.t{{position:absolute;left:72px;top:96px;width:640px}}
.k{{font:500 22px 'IBM Plex Mono','Inter',monospace;letter-spacing:.1em;color:#F9A752;text-transform:uppercase;margin-bottom:26px}}
h1{{font-size:62px;line-height:1.1;margin:0;font-weight:700;letter-spacing:-.02em}} h1 span{{color:#F9A752}}
.f{{position:absolute;left:72px;bottom:56px;font:500 24px 'Inter',sans-serif;color:#9AA7BE}}
svg{{position:absolute;right:40px;top:80px}}
</style></head><body><div class="b1"></div><div class="b2"></div>
<div class="t"><div class="k">{kicker}</div><h1>{titolo}</h1></div><div class="f">orbitripetizioni.it · Matteo Casadei</div>
<svg width="440" height="460" viewBox="{vb}"><g stroke="rgba(255,255,255,.5)" stroke-width=".06"><path d="M-6 0H8M0 -22V12"/></g>{corpo}</svg></body></html>"""
out = R / "assets" / "img" / "blog" / f"{slug}-og.png"
tmp = pathlib.Path(tempfile.mkdtemp()) / "og.html"; tmp.write_text(html, encoding="utf-8")
js = f"const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1200,height:630}}}});await p.goto('file://{tmp}');await p.waitForTimeout(300);await p.screenshot({{path:'{out}'}});await b.close()}})();"
subprocess.run(["node", "-e", js], check=True)
print(out)
