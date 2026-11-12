// ORBIT — widget "parabola e soluzioni" per il post sulle equazioni di secondo grado.
// La pagina è già completa in HTML (formule e grafico dell'esempio); questo script
// aggiunge solo gli slider. La funzione risolvi() è pura: la stessa che viene
// confrontata con sympy dal test bozze/strumenti/verifica_widget.mjs.
(function (root) {
  "use strict";

  function risolvi(a, b, c) {
    if (a === 0) {
      return { grado: 1, delta: null, tipo: "retta", x1: b !== 0 ? -c / b : null, x2: null, vertice: null };
    }
    var delta = b * b - 4 * a * c;
    var xv = -b / (2 * a);
    var yv = a * xv * xv + b * xv + c;
    if (delta > 0) {
      var r = Math.sqrt(delta);
      var p = (-b - r) / (2 * a), q = (-b + r) / (2 * a);
      return { grado: 2, delta: delta, tipo: "due", x1: Math.min(p, q), x2: Math.max(p, q), vertice: [xv, yv] };
    }
    if (delta === 0) {
      return { grado: 2, delta: 0, tipo: "una", x1: xv, x2: null, vertice: [xv, yv] };
    }
    return { grado: 2, delta: delta, tipo: "nessuna", x1: null, x2: null, vertice: [xv, yv] };
  }

  if (typeof module !== "undefined" && module.exports) { module.exports = { risolvi: risolvi }; }
  if (typeof document === "undefined") { return; }

  // ---------- parte grafica (solo nel browser) ----------
  var W = 640, H = 400, XMIN = -6, XMAX = 6, YMIN = -10, YMAX = 10;
  function sx(x) { return (x - XMIN) / (XMAX - XMIN) * W; }
  function sy(y) { return H - (y - YMIN) / (YMAX - YMIN) * H; }
  function num(n) {
    var s = (Math.round(n * 1000) / 1000).toString().replace(".", ",").replace("-", "−");
    return s;
  }

  function init() {
    var box = document.getElementById("eq-widget");
    if (!box) { return; }
    var svgCurve = box.querySelector("[data-eq='curva']");
    var svgMarks = box.querySelector("[data-eq='punti']");
    var out = box.querySelector("[data-eq='lettura']");
    var eqLabel = box.querySelector("[data-eq='equazione']");
    var controls = box.querySelector("[data-eq='controlli']");
    var inputs = { a: box.querySelector("#eq-a"), b: box.querySelector("#eq-b"), c: box.querySelector("#eq-c") };
    var vals = { a: box.querySelector("[data-val='a']"), b: box.querySelector("[data-val='b']"), c: box.querySelector("[data-val='c']") };
    if (!svgCurve || !svgMarks || !out || !controls || !inputs.a) { return; }
    controls.hidden = false;

    function termine(coef, pot, primo) {
      if (coef === 0) { return ""; }
      var segno = coef < 0 ? "−" : (primo ? "" : "+");
      var abs = Math.abs(coef);
      var cifra = (abs === 1 && pot !== "") ? "" : num(abs);
      return (primo ? segno : " " + segno + " ") + cifra + pot;
    }
    function equazione(a, b, c) {
      var s = termine(a, "x²", true);
      var t = termine(b, "x", s === "");
      var u = termine(c, "", s === "" && t === "");
      s = s + t + u;
      return (s === "" ? "0" : s) + " = 0";
    }
    function dentro(x, y) { return x >= XMIN && x <= XMAX && y >= YMIN && y <= YMAX; }
    function punto(x, y, cls, r, etichetta, ldx, ldy) {
      if (!dentro(x, y)) { return ""; }
      var cx = sx(x), cy = sy(y);
      var s = '<circle class="' + cls + '" cx="' + cx.toFixed(1) + '" cy="' + cy.toFixed(1) + '" r="' + r + '"></circle>';
      var lab = cls === "eq-vertice" ? "g-lab-vertice" : "g-lab-radice";
      s += '<text class="' + lab + '" x="' + (cx + ldx).toFixed(1) + '" y="' + (cy + ldy).toFixed(1) + '" text-anchor="middle" font-size="15">' + etichetta + '</text>';
      return s;
    }

    function render() {
      var a = parseFloat(inputs.a.value), b = parseFloat(inputs.b.value), c = parseFloat(inputs.c.value);
      vals.a.textContent = num(a); vals.b.textContent = num(b); vals.c.textContent = num(c);
      var r = risolvi(a, b, c);
      eqLabel.textContent = equazione(a, b, c);

      var d = "";
      for (var x = XMIN; x <= XMAX + 1e-9; x += 0.05) {
        var y = a * x * x + b * x + c;
        d += (d === "" ? "M" : "L") + sx(x).toFixed(1) + " " + sy(y).toFixed(1);
      }
      svgCurve.setAttribute("d", d);

      var marks = "", testo, ldy = a > 0 ? 26 : -16, vdy = a > 0 ? 24 : -14;
      if (r.tipo === "due") {
        marks += punto(r.x1, 0, "eq-radice", 7, "x\u2081", -16, ldy) + punto(r.x2, 0, "eq-radice", 7, "x\u2082", 16, ldy);
        testo = "Δ = " + num(r.delta) + " > 0: due soluzioni, x₁ = " + num(r.x1) + " e x₂ = " + num(r.x2) +
                ". La parabola taglia l’asse x in due punti.";
      } else if (r.tipo === "una") {
        marks += punto(r.x1, 0, "eq-radice", 7, "x", 0, ldy);
        testo = "Δ = 0: una sola soluzione (doppia), x = " + num(r.x1) + ". La parabola tocca l’asse x in un punto.";
      } else if (r.tipo === "nessuna") {
        testo = "Δ = " + num(r.delta) + " < 0: nessuna soluzione reale. La parabola non incontra l’asse x.";
      } else {
        testo = "Con a = 0 non c’è più il termine x²: non è un’equazione di secondo grado, ma una retta." +
                (r.x1 === null ? "" : " Si annulla in x = " + num(r.x1) + ".");
        if (r.x1 !== null) { marks += punto(r.x1, 0, "eq-radice", 7, "x", 0, ldy); }
      }
      if (r.vertice) { marks += punto(r.vertice[0], r.vertice[1], "eq-vertice", 6, "V", 0, vdy); }
      svgMarks.innerHTML = marks;
      out.textContent = testo;
    }
    ["a", "b", "c"].forEach(function (k) { inputs[k].addEventListener("input", render); });
    render();
  }

  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", init); } else { init(); }
})(typeof window !== "undefined" ? window : globalThis);
