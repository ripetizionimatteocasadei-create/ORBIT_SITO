// ORBIT — widget "velocità media e istantanea": grafico spazio-tempo s(t) = v0 t + 1/2 a t^2,
// secante tra t0 e t0+Δt (velocità media) e tangente in t0 (velocità istantanea).
// calcola() è una funzione pura verificata con sympy da bozze/strumenti/verifica_moto.py.
// figura() e lettura() restituiscono testo/SVG: la pagina HTML ne contiene già la versione iniziale.
(function (root) {
  "use strict";
  var W = 640, H = 400, TMAX = 6;

  function calcola(a, v0, t0, dt) {
    var f = function (t) { return v0 * t + 0.5 * a * t * t; };
    var t1 = t0 + dt, s0 = f(t0), s1 = f(t1);
    return { t0: t0, t1: t1, dt: dt, s0: s0, s1: s1, ds: s1 - s0, vm: (s1 - s0) / dt, vi: v0 + a * t0 };
  }

  function num(n) {
    var r = Math.round(n * 1000) / 1000;
    if (r === 0) { r = 0; }
    return r.toString().replace(".", ",").replace("-", "−");
  }
  function passo(r) {
    var raw = r / 5, p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    return (m <= 1 ? 1 : m <= 2 ? 2 : m <= 5 ? 5 : 10) * p;
  }
  function f1(x) { return x.toFixed(1); }

  function lettura(a, v0, t0, dt) {
    var r = calcola(a, v0, t0, dt);
    return "Tra t = " + num(r.t0) + " s e t = " + num(r.t1) + " s lo spazio passa da " + num(r.s0) + " m a " + num(r.s1) + " m: Δs = " + num(r.ds) +
      " m in Δt = " + num(r.dt) + " s, quindi la velocità media è " + num(r.vm) + " m/s. All’istante t = " + num(r.t0) +
      " s la velocità istantanea è " + num(r.vi) + " m/s.";
  }

  function figura(a, v0, t0, dt) {
    var r = calcola(a, v0, t0, dt);
    var f = function (t) { return v0 * t + 0.5 * a * t * t; };
    var smin = 0, smax = 0, t;
    for (t = 0; t <= TMAX + 1e-9; t += 0.05) { var v = f(t); if (v < smin) { smin = v; } if (v > smax) { smax = v; } }
    var pad = 0.1 * ((smax - smin) || 1);
    var lo = smin < 0 ? smin - pad : 0, hi = smax + pad;
    var sx = function (x) { return x / TMAX * W; };
    var sy = function (y) { return H - (y - lo) / (hi - lo) * H; };
    var g = "", i;
    for (i = 0; i <= TMAX; i++) { g += '<line class="g-grid" x1="' + f1(sx(i)) + '" y1="0" x2="' + f1(sx(i)) + '" y2="' + H + '"/>'; }
    var st = passo(hi - lo), ticks = "";
    for (var y = Math.ceil(lo / st) * st; y <= hi + 1e-9; y += st) {
      g += '<line class="g-grid" x1="0" y1="' + f1(sy(y)) + '" x2="' + W + '" y2="' + f1(sy(y)) + '"/>';
      if (Math.abs(y) > 1e-9) { ticks += '<text x="6" y="' + f1(sy(y) - 5) + '" font-size="12">' + num(y) + '</text>'; }
    }
    for (i = 1; i <= TMAX; i++) { ticks += '<text x="' + f1(sx(i)) + '" y="' + f1(sy(0) - 6) + '" font-size="12" text-anchor="middle">' + i + '</text>'; }
    var d = "";
    for (t = 0; t <= TMAX + 1e-9; t += 0.05) { d += (d === "" ? "M" : "L") + f1(sx(t)) + " " + f1(sy(f(t))); }
    var yt = function (x) { return r.s0 + r.vi * (x - r.t0); };       // tangente
    var ys = function (x) { return r.s0 + r.vm * (x - r.t0); };       // secante
    var tang = '<line class="m-tang" x1="0" y1="' + f1(sy(yt(0))) + '" x2="' + W + '" y2="' + f1(sy(yt(TMAX))) + '" clip-path="url(#m-clip)"/>';
    var sec = '<line class="m-sec" x1="0" y1="' + f1(sy(ys(0))) + '" x2="' + W + '" y2="' + f1(sy(ys(TMAX))) + '" clip-path="url(#m-clip)"/>';
    var pts = '<circle class="eq-vertice" cx="' + f1(sx(r.t0)) + '" cy="' + f1(sy(r.s0)) + '" r="7"></circle>' +
              '<circle class="eq-radice" cx="' + f1(sx(r.t1)) + '" cy="' + f1(sy(r.s1)) + '" r="7"></circle>';
    var alt = "Grafico spazio-tempo: la curva s(t) con la secante tra t = " + num(r.t0) + " s e t = " + num(r.t1) + " s (pendenza " + num(r.vm) + " m/s) e la tangente in t = " + num(r.t0) + " s (pendenza " + num(r.vi) + " m/s).";
    return '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + alt + '" width="' + W + '" height="' + H + '">' +
      '<defs><clipPath id="m-clip"><rect width="' + W + '" height="' + H + '"/></clipPath></defs>' +
      '<g>' + g + '</g><line class="g-axis" x1="0" y1="' + f1(sy(0)) + '" x2="' + W + '" y2="' + f1(sy(0)) + '"/><line class="g-axis" x1="0" y1="0" x2="0" y2="' + H + '"/>' +
      '<g>' + ticks + '</g><text x="' + (W - 8) + '" y="' + f1(sy(0) - 24) + '" font-size="13" text-anchor="end">t (s)</text><text x="12" y="16" font-size="13">s (m)</text>' +
      '<path class="g-curva" clip-path="url(#m-clip)" d="' + d + '"/>' + tang + sec + pts + '</svg>';
  }

  if (typeof module !== "undefined" && module.exports) { module.exports = { calcola: calcola, figura: figura, lettura: lettura }; }
  if (typeof document === "undefined") { return; }

  function init() {
    var box = document.getElementById("moto-widget");
    if (!box) { return; }
    var fig = box.querySelector("[data-m='fig']"), lett = box.querySelector("[data-m='lettura']"), ctl = box.querySelector("[data-m='controlli']");
    var inp = { a: box.querySelector("#m-a"), v0: box.querySelector("#m-v0"), t0: box.querySelector("#m-t0"), dt: box.querySelector("#m-dt") };
    var val = { a: box.querySelector("[data-val='a']"), v0: box.querySelector("[data-val='v0']"), t0: box.querySelector("[data-val='t0']"), dt: box.querySelector("[data-val='dt']") };
    if (!fig || !lett || !ctl || !inp.a) { return; }
    ctl.hidden = false;
    function render() {
      var a = parseFloat(inp.a.value), v0 = parseFloat(inp.v0.value), t0 = parseFloat(inp.t0.value), dt = parseFloat(inp.dt.value);
      val.a.textContent = num(a); val.v0.textContent = num(v0); val.t0.textContent = num(t0); val.dt.textContent = num(dt);
      fig.innerHTML = figura(a, v0, t0, dt);
      lett.textContent = lettura(a, v0, t0, dt);
    }
    ["a", "v0", "t0", "dt"].forEach(function (k) { inp[k].addEventListener("input", render); });
    render();
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", init); } else { init(); }
})(typeof window !== "undefined" ? window : globalThis);
