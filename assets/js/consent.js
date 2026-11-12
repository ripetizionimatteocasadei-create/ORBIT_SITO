// ORBIT — consenso cookie: Google Analytics e Microsoft Clarity partono
// solo dopo un consenso esplicito (opt-in), come richiesto da GDPR/ePrivacy
// per i cookie non strettamente necessari. Il banner compare con un piccolo
// ritardo e un'animazione morbida, non è un overlay bloccante a schermo intero.
// Stile completamente autonomo (niente dipendenze da v2.css o altri fogli di
// stile) cosi' funziona identico su ogni pagina del sito, nuova o vecchia.
(function () {
  var KEY = "orbit_cookie_consent";
  var GA_ID = "G-YY2LC22Q1R";
  var CLARITY_ID = "xrq9zhbsk7";

  function getConsent() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function setConsent(value) {
    try { localStorage.setItem(KEY, value); } catch (e) {}
  }

  function loadAnalytics() {
    if (window.__orbitAnalyticsLoaded) return;
    window.__orbitAnalyticsLoaded = true;

    var gtagScript = document.createElement("script");
    gtagScript.async = true;
    gtagScript.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(gtagScript);
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag("js", new Date());
    gtag("config", GA_ID);

    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, "clarity", "script", CLARITY_ID);
  }

  function layoutBanner(el) {
    // Ancorato da sinistra (sempre affidabile) con una larghezza calcolata
    // via JS su clientWidth, non su CSS left/right/vw: su alcune pagine con
    // elementi decorativi volutamente più larghi del viewport (il testo
    // cinetico di sfondo, il marquee) alcuni motori di rendering mobile
    // calcolano `right`/percentuali su una larghezza di viewport gonfiata.
    var vw = document.documentElement.clientWidth;
    var small = vw <= 620;
    var margin = small ? 14 : 24;
    var width = Math.min(640, vw - margin * 2);
    el.style.width = width + "px";
    el.style.left = Math.round((vw - width) / 2) + "px";
    el.style.bottom = (small ? 14 : 24) + "px";
    el.style.padding = small ? "20px 22px" : "24px 28px";
  }

  function injectStyle() {
    if (document.getElementById("cookie-banner-style")) return;
    var style = document.createElement("style");
    style.id = "cookie-banner-style";
    style.textContent =
      "#cookie-banner{position:fixed;z-index:9999;box-sizing:border-box;" +
      "display:flex;flex-direction:column;gap:16px;" +
      "background:rgba(16,27,48,0.96);border:1px solid rgba(255,255,255,0.08);border-radius:20px;" +
      "box-shadow:0 24px 60px -20px rgba(0,0,0,0.6);" +
      "font-family:'Inter',system-ui,sans-serif;" +
      "transform:translateY(140%);opacity:0;" +
      "transition:transform 0.7s cubic-bezier(.16,.84,.44,1),opacity 0.7s cubic-bezier(.16,.84,.44,1);" +
      "pointer-events:none;}" +
      "#cookie-banner.visible{transform:translateY(0);opacity:1;pointer-events:auto;}" +
      "#cookie-banner p{font-size:0.88rem;line-height:1.6;color:#9AA7BE;margin:0;}" +
      "#cookie-banner a{color:#F9A752;border-bottom:1px solid rgba(249,167,82,0.4);text-decoration:none;}" +
      "#cookie-banner .cookie-banner-actions{display:flex;gap:12px;flex-wrap:wrap;}" +
      "#cookie-banner button{font-family:inherit;border:none;cursor:pointer;border-radius:100px;" +
      "padding:11px 24px;font-size:0.88rem;font-weight:600;transition:transform 0.2s ease;}" +
      "#cookie-banner button:hover{transform:translateY(-2px);}" +
      "#cookie-banner button[data-cookie-action='accept']{background:linear-gradient(135deg,#F2811D,#F9A752);color:#050B18;}" +
      "#cookie-banner button[data-cookie-action='reject']{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);color:#FFFFFF;}";
    document.head.appendChild(style);
  }

  function buildBanner() {
    injectStyle();
    var prefix = window.ORBIT_ASSET_PREFIX || "";
    var el = document.createElement("div");
    el.id = "cookie-banner";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-label", "Preferenze cookie");
    el.innerHTML =
      "<p>Usiamo cookie tecnici necessari al funzionamento del sito. Solo con il tuo consenso usiamo anche cookie di analisi (Google Analytics, Microsoft Clarity) per capire come viene usato il sito. <a href=\"" + prefix + "privacy/index.html\">Scopri di più</a></p>" +
      "<div class=\"cookie-banner-actions\">" +
        "<button type=\"button\" data-cookie-action=\"reject\">Rifiuta</button>" +
        "<button type=\"button\" data-cookie-action=\"accept\">Accetta</button>" +
      "</div>";
    document.body.appendChild(el);
    layoutBanner(el);
    window.addEventListener("resize", function () { layoutBanner(el); });
    return el;
  }

  function hideBanner(el) {
    el.classList.remove("visible");
    setTimeout(function () {
      if (el.parentNode) el.parentNode.removeChild(el);
    }, 650);
  }

  function showBanner() {
    var el = document.getElementById("cookie-banner") || buildBanner();
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { el.classList.add("visible"); });
    });
    el.querySelector('[data-cookie-action="accept"]').addEventListener("click", function () {
      setConsent("accepted");
      hideBanner(el);
      loadAnalytics();
    });
    el.querySelector('[data-cookie-action="reject"]').addEventListener("click", function () {
      setConsent("rejected");
      hideBanner(el);
    });
  }

  function init() {
    var consent = getConsent();
    if (consent === "accepted") { loadAnalytics(); return; }
    if (consent === "rejected") { return; }
    setTimeout(showBanner, 2500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Link "Preferenze cookie" nel footer: permette di rivedere la scelta.
  window.orbitReopenCookiePrefs = function () {
    setConsent(null);
    try { localStorage.removeItem(KEY); } catch (e) {}
    var existing = document.getElementById("cookie-banner");
    if (existing && existing.parentNode) existing.parentNode.removeChild(existing);
    showBanner();
  };
})();
