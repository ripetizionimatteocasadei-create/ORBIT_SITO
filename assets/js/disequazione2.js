// ORBIT — widget "disequazione di secondo grado": parabola, segno e insieme delle soluzioni.
// La pagina è già completa in HTML (formule, grafico dell'esempio e soluzione); lo script aggiunge slider e scelta del simbolo.
// risolvi() e contiene() sono funzioni pure, verificate con sympy da bozze/strumenti/verifica_disequazione.py.
(function (root) {
  "use strict";
  var INF = Infinity;

  function iv(lo, hi, il, ih) { return { lo: lo, hi: hi, incLo: !!il, incHi: !!ih }; }

  // Risolve a x^2 + b x + c  op  0, con op in ">", "<", ">=", "<=". Restituisce {intervalli:[...], radici:[...]}.
  function risolvi(a, b, c, op) {
    var stretta = (op === ">" || op === "<");
    var pos = (op === ">" || op === ">=");
    var inc = !stretta, out = [], radici = [];
    if (a === 0) {
      if (b === 0) {
        var vero = pos ? c > 0 : c < 0;
        if (c === 0) { vero = !stretta; }
        return { intervalli: vero ? [iv(-INF, INF, false, false)] : [], radici: [] };
      }
      var r = -c / b; radici = [r];
      var destra = (b > 0) === pos;   // soluzioni a destra della radice
      out = destra ? [iv(r, INF, inc, false)] : [iv(-INF, r, false, inc)];
      return { intervalli: out, radici: radici };
    }
    var d = b * b - 4 * a * c;
    if (d > 0) {
      var s = Math.sqrt(d), p = (-b - s) / (2 * a), q = (-b + s) / (2 * a);
      var r1 = Math.min(p, q), r2 = Math.max(p, q);
      radici = [r1, r2];
      var fuori = (a > 0) === pos;    // l'insieme cercato sta fuori dalle radici
      out = fuori ? [iv(-INF, r1, false, inc), iv(r2, INF, inc, false)] : [iv(r1, r2, inc, inc)];
    } else if (d === 0) {
      var r0 = -b / (2 * a); radici = [r0];
      var concorde = (a > 0) === pos;  // il segno di f (uguale a quello di a, tranne in r0) è quello cercato
      if (concorde) { out = inc ? [iv(-INF, INF, false, false)] : [iv(-INF, r0, false, false), iv(r0, INF, false, false)]; }
      else { out = inc ? [iv(r0, r0, true, true)] : []; }
    } else {
      out = ((a > 0) === pos) ? [iv(-INF, INF, false, false)] : [];
    }
    return { intervalli: out, radici: radici };
  }

  function contiene(res, x) {
    for (var i = 0; i < res.intervalli.length; i++) {
      var t = res.intervalli[i];
      var okLo = t.incLo ? x >= t.lo : x > t.lo;
      var okHi = t.incHi ? x <= t.hi : x < t.hi;
      if (okLo && okHi) { return true; }
    }
    return false;
  }

  if (typeof module !== "undefined" && module.exports) { module.exports = { risolvi: risolvi, contiene: contiene }; }
  if (typeof document === "undefined") { return; }

  // ---------------------------------------------------------------- parte grafica
  var W = 640, H = 400, XMIN = -6, XMAX = 6, YMIN = -10, YMAX = 10;
  function sx(x) { return (x - XMIN) / (XMAX - XMIN) * W; }
  function sy(y) { return H - (y - YMIN) / (YMAX - YMIN) * H; }
  function num(n) { return (Math.round(n * 1000) / 1000).toString().replace(".", ",").replace("-", "−"); }
  var SIMBOLO = { ">": ">", "<": "<", ">=": "≥", "<=": "≤" };

  function termine(co, pot, primo) {
    if (co === 0) { return ""; }
    var sg = co < 0 ? "−" : (primo ? "" : "+"), ab = Math.abs(co);
    var cifra = (ab === 1 && pot !== "") ? "" : num(ab);
    return (primo ? sg : " " + sg + " ") + cifra + pot;
  }
  function espressione(a, b, c) {
    var s = termine(a, "x²", true), t = termine(b, "x", s === ""), u = termine(c, "", s === "" && t === "");
    return (s + t + u) || "0";
  }
  function testo(res) {
    var v = res.intervalli;
    if (v.length === 0) { return "nessuna soluzione"; }
    var f = function (t, sinistra) { return (sinistra ? (t.incLo ? "≤" : "<") : (t.incHi ? "≤" : "<")); };
    if (v.length === 1 && v[0].lo === -INF && v[0].hi === INF) { return "tutti i numeri reali"; }
    if (v.length === 2 && v[0].hi === v[1].lo && !v[0].incHi && !v[1].incLo && v[0].lo === -INF && v[1].hi === INF) { return "x ≠ " + num(v[0].hi); }
    var parti = v.map(function (t) {
      if (t.lo === t.hi) { return "x = " + num(t.lo); }
      if (t.lo === -INF) { return "x " + (t.incHi ? "≤" : "<") + " " + num(t.hi); }
      if (t.hi === INF) { return "x " + (t.incLo ? "≥" : ">") + " " + num(t.lo); }
      return num(t.lo) + " " + f(t, true) + " x " + f(t, false) + " " + num(t.hi);
    });
    return parti.join(" oppure ");
  }

  function init() {
    var box = document.getElementById("ineq-widget");
    if (!box) { return; }
    var curva = box.querySelector("[data-q='curva']"), sol = box.querySelector("[data-q='soluzione']");
    var lett = box.querySelector("[data-q='lettura']"), tit = box.querySelector("[data-q='titolo']"), ctl = box.querySelectorAll("[data-q='controlli']");
    var inp = { a: box.querySelector("#q-a"), b: box.querySelector("#q-b"), c: box.querySelector("#q-c") };
    var val = { a: box.querySelector("[data-val='a']"), b: box.querySelector("[data-val='b']"), c: box.querySelector("[data-val='c']") };
    var bott = Array.prototype.slice.call(box.querySelectorAll("[data-op]"));
    if (!curva || !sol || !lett || !ctl.length || !inp.a) { return; }
    Array.prototype.forEach.call(ctl, function (e) { e.hidden = false; });
    var op = ">";
    bott.forEach(function (bt) { if (bt.getAttribute("aria-pressed") === "true") { op = bt.getAttribute("data-op"); } });

    function render() {
      var a = parseFloat(inp.a.value), b = parseFloat(inp.b.value), c = parseFloat(inp.c.value);
      val.a.textContent = num(a); val.b.textContent = num(b); val.c.textContent = num(c);
      var res = risolvi(a, b, c, op);
      tit.textContent = espressione(a, b, c) + " " + SIMBOLO[op] + " 0";
      var d = "";
      for (var x = XMIN; x <= XMAX + 1e-9; x += 0.05) { d += (d === "" ? "M" : "L") + sx(x).toFixed(1) + " " + sy(a * x * x + b * x + c).toFixed(1); }
      curva.setAttribute("d", d);
      var g = "";
      res.intervalli.forEach(function (t) {
        var lo = Math.max(t.lo, XMIN), hi = Math.min(t.hi, XMAX);
        if (lo > hi) { return; }
        if (lo === hi) { return; }
        g += '<line class="q-sol" x1="' + sx(lo).toFixed(1) + '" y1="' + sy(0).toFixed(1) + '" x2="' + sx(hi).toFixed(1) + '" y2="' + sy(0).toFixed(1) + '"></line>';
      });
      res.intervalli.forEach(function (t) {
        [[t.lo, t.incLo], [t.hi, t.incHi]].forEach(function (e) {
          if (e[0] >= XMIN && e[0] <= XMAX && isFinite(e[0])) { g += '<circle class="' + (e[1] ? "q-pieno" : "q-vuoto") + '" cx="' + sx(e[0]).toFixed(1) + '" cy="' + sy(0).toFixed(1) + '" r="7"></circle>'; }
        });
      });
      sol.innerHTML = g;
      lett.textContent = "Soluzione: " + testo(res) + ".";
    }
    ["a", "b", "c"].forEach(function (k) { inp[k].addEventListener("input", render); });
    bott.forEach(function (bt) {
      bt.addEventListener("click", function () {
        op = bt.getAttribute("data-op");
        bott.forEach(function (o) { o.setAttribute("aria-pressed", o === bt ? "true" : "false"); });
        render();
      });
    });
    render();
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", init); } else { init(); }
})(typeof window !== "undefined" ? window : globalThis);
