/* Aviso de cookies + Google Analytics.
   Analytics solo se carga si el visitante pulsa «Aceptar». La elección se guarda en este navegador
   y se puede cambiar con cualquier enlace que tenga data-cookies (p. ej. «Configurar cookies» del pie). */
(function () {
  var GA_ID = "G-99NHJYTTD8";
  var KEY = "ep-cookies";

  var get = function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
  var set = function (v) { try { localStorage.setItem(KEY, v); } catch (e) {} };

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { dataLayer.push(arguments); };

  var loaded = false;
  function loadGA() {
    if (loaded || !GA_ID) return;
    loaded = true;
    gtag("js", new Date());
    gtag("config", GA_ID);
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
  }
  // Para que la web envíe eventos (kit, carrito…) solo cuando hay permiso.
  window.analyticsAllowed = function () { return loaded; };

  var css = "" +
    "#cookies{position:fixed;left:0;right:0;bottom:0;z-index:1000;background:#fff;border-top:3px solid #111;box-shadow:0 -6px 20px rgba(0,0,0,.12);" +
    "padding:14px max(16px,env(safe-area-inset-left,0px)) calc(14px + env(safe-area-inset-bottom,0px));font:15px/1.45 'Barlow','Helvetica Neue',Arial,sans-serif;color:#111}" +
    "#cookies .in{max-width:72rem;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:10px 20px}" +
    "#cookies p{margin:0;flex:1 1 22rem}#cookies a{color:#111}" +
    "#cookies .bt{display:flex;gap:10px;flex-wrap:wrap}" +
    "#cookies button{font:700 15px/1 'Barlow Condensed','Arial Narrow',Arial,sans-serif;text-transform:uppercase;letter-spacing:.04em;padding:12px 22px;min-width:9rem;" +
    "border:2px solid #111;background:#fff;color:#111;cursor:pointer}" +
    "#cookies button:hover,#cookies button:focus-visible{background:#111;color:#fff}";

  function show() {
    if (document.getElementById("cookies")) return;
    if (!document.getElementById("cookies-css")) {
      var st = document.createElement("style"); st.id = "cookies-css"; st.textContent = css; document.head.appendChild(st);
    }
    var box = document.createElement("div");
    box.id = "cookies";
    box.setAttribute("role", "region");
    box.setAttribute("aria-label", "Aviso de cookies");
    box.innerHTML = '<div class="in"><p>Usamos cookies de Google Analytics para saber cuántas personas visitan la web y mejorarla. Solo se activan si las aceptas. ' +
      '<a href="cookies.html">Más información</a>.</p><div class="bt"><button type="button" data-v="no">Rechazar</button><button type="button" data-v="si">Aceptar</button></div></div>';
    box.addEventListener("click", function (e) {
      var v = e.target.getAttribute && e.target.getAttribute("data-v");
      if (!v) return;
      set(v);
      box.remove();
      if (v === "si") loadGA();
      else {
        // Al rechazar, borra las cookies de Analytics que hubiera y deja de medir al recargar.
        document.cookie.split(";").forEach(function (c) {
          var name = c.split("=")[0].trim();
          if (/^_ga/.test(name)) ["", location.hostname, "." + location.hostname.replace(/^www\./, "")].forEach(function (d) {
            document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/" + (d ? "; domain=" + d : "");
          });
        });
        if (loaded) location.reload();
      }
    });
    document.body.appendChild(box);
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-cookies]");
    if (a) { e.preventDefault(); show(); }
  });

  if (get() === "si") loadGA();
  else if (get() !== "no") {
    if (document.body) show(); else document.addEventListener("DOMContentLoaded", show);
  }
})();
