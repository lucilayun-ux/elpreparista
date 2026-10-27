/*
 * Estadísticas de elpreparista.com: Cloudflare Worker + base de datos D1.
 *
 *   POST /e        recibe un evento de la web (sin cookies, sin guardar IP).
 *   GET  /stats    devuelve los datos agregados en JSON (pide la clave ADMIN_KEY).
 *   GET  /         panel para ver las estadísticas en el navegador.
 *
 * Variables del Worker:
 *   DB               base de datos D1 (binding).
 *   ADMIN_KEY        secreto: la clave para ver el panel.
 *   ALLOWED_ORIGINS  opcional: dominios que pueden enviar eventos, separados por comas.
 *
 * Privacidad: cada visitante se cuenta con un hash de IP + navegador + día + secreto.
 * El hash cambia cada día y no se puede revertir, así que no identifica a nadie
 * ni permite seguirle de un día a otro. No se guarda la IP ni se usan cookies.
 */

const TYPES = new Set(["pageview", "kit", "level", "people", "cart", "product", "extra", "remove", "subscribe"]);
const DEFAULT_ORIGINS = "https://elpreparista.com,https://www.elpreparista.com";
const BOTS = /bot|crawl|spider|slurp|headless|preview|lighthouse|monitor/i;

const SCHEMA = `
CREATE TABLE IF NOT EXISTS events (
  id      INTEGER PRIMARY KEY,
  ts      INTEGER NOT NULL,
  day     TEXT    NOT NULL,
  type    TEXT    NOT NULL,
  path    TEXT,
  kit     TEXT,
  level   TEXT,
  people  INTEGER,
  item    TEXT,
  value   REAL,
  ref     TEXT,
  country TEXT,
  device  TEXT,
  visitor TEXT
);
CREATE INDEX IF NOT EXISTS events_day_type ON events (day, type);`;

let schemaReady = false;
async function ensureSchema(db) {
  if (schemaReady) return;
  await db.exec(SCHEMA.replace(/\s*\n\s*/g, " ").replace(/; /g, ";\n"));
  schemaReady = true;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (url.pathname === "/e") return await collect(request, env);
      if (url.pathname === "/stats") return await stats(request, env, url);
      if (url.pathname === "/" && request.method === "GET") return new Response(DASHBOARD, { headers: { "content-type": "text/html; charset=utf-8" } });
      return new Response("No encontrado", { status: 404 });
    } catch (err) {
      return json({ error: String(err && err.message || err) }, 500);
    }
  },
};

/* ---------- Recogida de eventos ---------- */

async function collect(request, env) {
  const origin = request.headers.get("origin") || "";
  const allowed = (env.ALLOWED_ORIGINS || DEFAULT_ORIGINS).split(",").map(s => s.trim()).filter(Boolean);
  const cors = { "access-control-allow-origin": allowed.includes(origin) ? origin : allowed[0], "vary": "origin" };
  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: { ...cors, "access-control-allow-methods": "POST", "access-control-allow-headers": "content-type" } });
  if (request.method !== "POST") return new Response(null, { status: 405, headers: cors });
  if (origin && !allowed.includes(origin)) return new Response(null, { status: 403, headers: cors });

  const ua = request.headers.get("user-agent") || "";
  if (!ua || BOTS.test(ua)) return new Response(null, { status: 204, headers: cors });

  let e;
  try { e = JSON.parse(await request.text()); } catch { return new Response(null, { status: 400, headers: cors }); }
  if (!e || !TYPES.has(e.type)) return new Response(null, { status: 400, headers: cors });

  const now = new Date();
  const day = now.toISOString().slice(0, 10);
  const ip = request.headers.get("cf-connecting-ip") || "";
  const visitor = await hash(`${day}|${ip}|${ua}|${env.ADMIN_KEY || ""}`);
  const device = /mobi|android|iphone|ipod/i.test(ua) ? "móvil" : /ipad|tablet/i.test(ua) ? "tableta" : "ordenador";
  const country = (request.cf && request.cf.country) || "";

  await ensureSchema(env.DB);
  await env.DB.prepare(
    "INSERT INTO events (ts, day, type, path, kit, level, people, item, value, ref, country, device, visitor) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(
    now.getTime(), day, e.type, text(e.path, 120), text(e.kit, 20), text(e.level, 20),
    int(e.people), text(e.item, 60), num(e.value), text(e.ref, 80), country, device, visitor
  ).run();
  return new Response(null, { status: 204, headers: cors });
}

const text = (v, max) => ((typeof v === "string" && v) || (typeof v === "number" && isFinite(v)) ? String(v).slice(0, max) : null);
const int = v => (Number.isInteger(v) && v >= 0 && v < 1000 ? v : null);
const num = v => (typeof v === "number" && isFinite(v) && v >= 0 && v < 1e6 ? v : null);

async function hash(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].slice(0, 8).map(b => b.toString(16).padStart(2, "0")).join("");
}

/* ---------- Estadísticas ---------- */

async function stats(request, env, url) {
  const key = (request.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!env.ADMIN_KEY || !(await sameKey(key, env.ADMIN_KEY))) return json({ error: "Clave incorrecta" }, 401);

  const days = Math.min(Math.max(parseInt(url.searchParams.get("days"), 10) || 30, 1), 365);
  const since = new Date(Date.now() - (days - 1) * 864e5).toISOString().slice(0, 10);
  const db = env.DB;
  await ensureSchema(db);

  const all = (sql, ...args) => db.prepare(sql).bind(since, ...args).all().then(r => r.results);
  const VISITS = "COUNT(DISTINCT day || visitor)";

  const [totals, daily, carts, kitViews, items, removed, refs, pages, countries, devices] = await Promise.all([
    all(`SELECT
           SUM(type = 'pageview') AS pageviews,
           COUNT(DISTINCT CASE WHEN type = 'pageview' THEN day || visitor END) AS visitors,
           SUM(type = 'cart') AS carts,
           COALESCE(SUM(CASE WHEN type = 'cart' THEN value END), 0) AS cartValue,
           SUM(type IN ('product', 'extra')) AS productClicks,
           SUM(type = 'subscribe') AS subscribers
         FROM events WHERE day >= ?`),
    all(`SELECT day,
           SUM(type = 'pageview') AS pageviews,
           COUNT(DISTINCT CASE WHEN type = 'pageview' THEN visitor END) AS visitors,
           SUM(type = 'cart') AS carts
         FROM events WHERE day >= ? GROUP BY day ORDER BY day`),
    all(`SELECT kit, level, COUNT(*) AS carts, ROUND(AVG(people), 1) AS people,
           ROUND(AVG(item), 1) AS products, COALESCE(SUM(value), 0) AS value
         FROM events WHERE day >= ? AND type = 'cart' GROUP BY kit, level ORDER BY carts DESC`),
    all(`SELECT kit, ${VISITS} AS visitors FROM events WHERE day >= ? AND type = 'kit' GROUP BY kit ORDER BY visitors DESC`),
    all(`SELECT type, item, COUNT(*) AS clicks FROM events WHERE day >= ? AND type IN ('product', 'extra')
         GROUP BY type, item ORDER BY clicks DESC LIMIT 20`),
    all(`SELECT item, COUNT(*) AS times FROM events WHERE day >= ? AND type = 'remove' GROUP BY item ORDER BY times DESC LIMIT 15`),
    all(`SELECT ref, ${VISITS} AS visitors FROM events WHERE day >= ? AND type = 'pageview' AND ref IS NOT NULL
         GROUP BY ref ORDER BY visitors DESC LIMIT 15`),
    all(`SELECT path, COUNT(*) AS pageviews FROM events WHERE day >= ? AND type = 'pageview' GROUP BY path ORDER BY pageviews DESC LIMIT 15`),
    all(`SELECT country, ${VISITS} AS visitors FROM events WHERE day >= ? AND type = 'pageview' GROUP BY country ORDER BY visitors DESC LIMIT 10`),
    all(`SELECT device, ${VISITS} AS visitors FROM events WHERE day >= ? AND type = 'pageview' GROUP BY device ORDER BY visitors DESC`),
  ]);

  return json({ days, since, totals: totals[0], daily, carts, kitViews, items, removed, refs, pages, countries, devices });
}

async function sameKey(a, b) {
  const [x, y] = await Promise.all([hash("k|" + a), hash("k|" + b)]);
  return x === y;
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}

/* ---------- Panel ---------- */

const DASHBOARD = `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Estadísticas · El Preparista</title>
<style>
:root { --ink: #111111; --muted: #5A5A5A; --hair: #DADAD5; --paper: #FFFFFF; --bg: #F4F4F1; --red: #C8102E; --green: #00804A; --bar: #1F6F4A; color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.45 "Helvetica Neue", Arial, sans-serif; }
header { background: var(--ink); color: #fff; padding: 14px max(16px, 3vw); display: flex; flex-wrap: wrap; gap: 10px 20px; align-items: center; justify-content: space-between; }
header b { font: 800 20px/1 "Arial Narrow", Arial, sans-serif; letter-spacing: .03em; text-transform: uppercase; }
main { max-width: 1100px; margin: 0 auto; padding: 20px max(16px, 3vw) 48px; display: grid; gap: 20px; }
.ctrl { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.ctrl button, .ctrl select, .ctrl input { font: inherit; padding: 6px 10px; border: 1px solid #888; background: #fff; color: var(--ink); border-radius: 2px; }
.ctrl button { cursor: pointer; }
.ctrl button[aria-pressed="true"] { background: var(--green); border-color: var(--green); color: #fff; }
.login { background: var(--paper); border: 1px solid var(--hair); padding: 24px; max-width: 420px; display: grid; gap: 10px; }
.login input, .login button { font: inherit; padding: 10px; border: 1px solid #888; }
.login button { background: var(--ink); color: #fff; border: 0; cursor: pointer; font-weight: 700; }
.err { color: var(--red); margin: 0; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.tile { background: var(--paper); border: 1px solid var(--hair); padding: 14px 16px; }
.tile span { display: block; color: var(--muted); font-size: 13px; }
.tile b { display: block; font: 800 30px/1.1 "Arial Narrow", Arial, sans-serif; margin-top: 4px; font-variant-numeric: tabular-nums; }
.tile small { color: var(--muted); font-size: 12px; }
.card { background: var(--paper); border: 1px solid var(--hair); padding: 16px; min-width: 0; }
.card h2 { font: 700 15px/1.2 "Arial Narrow", Arial, sans-serif; text-transform: uppercase; letter-spacing: .04em; margin: 0 0 4px; }
.card p.sub { margin: 0 0 12px; color: var(--muted); font-size: 13px; }
.grid2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
.wide { grid-column: 1 / -1; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { text-align: left; padding: 6px 4px; border-bottom: 1px solid var(--hair); }
th { color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .03em; }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; }
td.empty { color: var(--muted); }
.chart { position: relative; }
.chart svg { display: block; width: 100%; height: auto; }
.chart .axis { fill: var(--muted); font-size: 11px; }
.chart .grid { stroke: #ECECE8; }
.chart .hit { fill: transparent; }
.chart .bar { pointer-events: none; }
.chart .hit:hover + .bar, .chart .bar.on { fill: var(--ink); }
.tip { position: absolute; pointer-events: none; background: var(--ink); color: #fff; padding: 6px 8px; font-size: 12px; line-height: 1.35; border-radius: 2px; white-space: nowrap; transform: translate(-50%, -100%); }
.tip[hidden] { display: none; }
details summary { cursor: pointer; color: var(--muted); font-size: 13px; margin-top: 10px; }
</style>
</head>
<body>
<header><b>El Preparista · Estadísticas</b>
  <div class="ctrl" id="ctrl" hidden>
    <span>Periodo:</span>
    <button type="button" data-days="7">7 días</button>
    <button type="button" data-days="30" aria-pressed="true">30 días</button>
    <button type="button" data-days="90">90 días</button>
    <button type="button" data-days="365">1 año</button>
    <button type="button" id="logout">Salir</button>
  </div>
</header>
<main id="app">
  <form class="login" id="login">
    <label for="key"><b>Clave del panel</b></label>
    <input id="key" type="password" autocomplete="current-password" required>
    <button type="submit">Entrar</button>
    <p class="err" id="err" hidden></p>
  </form>
</main>
<script>
var KIT = { casa: "Kit Casa", coche: "Kit Coche", salida: "Kit Salida" };
var state = { key: "", days: 30 };
try { state.key = localStorage.getItem("ep-key") || ""; } catch (e) {}
var app = document.getElementById("app");
var fmt = function (n) { return Number(n || 0).toLocaleString("es-ES"); };
var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
var pct = function (a, b) { return b ? (100 * a / b).toLocaleString("es-ES", { maximumFractionDigits: 1 }) + " %" : "–"; };

document.getElementById("login").addEventListener("submit", function (e) {
  e.preventDefault(); state.key = document.getElementById("key").value; load();
});
document.getElementById("ctrl").addEventListener("click", function (e) {
  var b = e.target.closest("[data-days]");
  if (b) { state.days = +b.dataset.days; load(); }
  if (e.target.id === "logout") { try { localStorage.removeItem("ep-key"); } catch (x) {} location.reload(); }
});

function load() {
  fetch("/stats?days=" + state.days, { headers: { authorization: "Bearer " + state.key } })
    .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
    .then(function (res) {
      if (!res.ok) throw new Error(res.d.error || "Error");
      try { localStorage.setItem("ep-key", state.key); } catch (e) {}
      document.getElementById("ctrl").hidden = false;
      document.querySelectorAll("[data-days]").forEach(function (b) { b.setAttribute("aria-pressed", String(+b.dataset.days === state.days)); });
      render(res.d);
    })
    .catch(function (err) {
      var el = document.getElementById("err");
      if (el) { el.hidden = false; el.textContent = err.message; }
    });
}

function table(cols, rows) {
  var head = "<tr>" + cols.map(function (c) { return "<th" + (c.n ? ' class="n"' : "") + ">" + c.label + "</th>"; }).join("") + "</tr>";
  var body = rows.length ? rows.map(function (r) {
    return "<tr>" + cols.map(function (c) { var v = c.get(r); return "<td" + (c.n ? ' class="n"' : "") + ">" + (c.n ? fmt(v) : esc(v)) + "</td>"; }).join("") + "</tr>";
  }).join("") : '<tr><td class="empty" colspan="' + cols.length + '">Sin datos todavía</td></tr>';
  return "<table>" + head + body + "</table>";
}

function fillDays(daily, days) {
  var map = {}; daily.forEach(function (d) { map[d.day] = d; });
  var out = [];
  for (var i = days - 1; i >= 0; i--) {
    var day = new Date(Date.now() - i * 864e5).toISOString().slice(0, 10);
    out.push(map[day] || { day: day, pageviews: 0, visitors: 0, carts: 0 });
  }
  return out;
}

function chart(daily, W) {
  var H = 220, L = 36, B = 22, T = 8;
  var max = Math.max(1, Math.max.apply(null, daily.map(function (d) { return d.visitors; })));
  var step = Math.pow(10, Math.floor(Math.log10(max)));
  var top = Math.ceil(max / step) * step;
  var slot = (W - L) / daily.length, bw = Math.max(1, slot - 2);
  var y = function (v) { return T + (H - T - B) * (1 - v / top); };
  var s = "";
  [0, top / 2, top].forEach(function (v) {
    s += '<line class="grid" x1="' + L + '" x2="' + W + '" y1="' + y(v) + '" y2="' + y(v) + '"/>';
    s += '<text class="axis" x="' + (L - 6) + '" y="' + (y(v) + 4) + '" text-anchor="end">' + fmt(v) + "</text>";
  });
  daily.forEach(function (d, i) {
    var x = L + i * slot + 1, h = (H - T - B) * d.visitors / top;
    s += '<rect class="hit" data-i="' + i + '" x="' + (L + i * slot) + '" y="' + T + '" width="' + slot + '" height="' + (H - T - B) + '"/>';
    if (h > 0) s += '<path class="bar" fill="var(--bar)" d="M' + x + "," + (H - B) + "V" + (H - B - h + Math.min(4, h)) + "q0,-" + Math.min(4, h) + " " + Math.min(4, h) + ",-" + Math.min(4, h) + "h" + Math.max(0, bw - 2 * Math.min(4, h)) + "q" + Math.min(4, h) + ",0 " + Math.min(4, h) + "," + Math.min(4, h) + "V" + (H - B) + 'z"/>';
    else s += '<path class="bar"/>';
  });
  var every = Math.ceil(daily.length / Math.max(3, Math.floor(W / 90)));
  daily.forEach(function (d, i) {
    var lastOne = i === daily.length - 1;
    if ((i % every === 0 && i < daily.length - every / 2) || lastOne) s += '<text class="axis" x="' + (lastOne ? W : L + i * slot + slot / 2) + '" y="' + (H - 6) + '" text-anchor="' + (lastOne ? "end" : "middle") + '">' + d.day.slice(8, 10) + "/" + d.day.slice(5, 7) + "</text>";
  });
  return '<div class="chart" id="chart"><svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Visitantes por día">' + s + '</svg><div class="tip" id="tip" hidden></div></div>';
}

var last = null, resizeTimer = 0;
window.addEventListener("resize", function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(function () { if (last) render(last); }, 200); });

function render(d) {
  last = d;
  var t = d.totals || {};
  var W = Math.max(280, Math.min(app.clientWidth, 1100) - 34);
  var daily = fillDays(d.daily, d.days);
  var kitName = function (r) { return (KIT[r.kit] || r.kit || "–") + (r.level ? " · " + r.level : ""); };
  app.innerHTML =
    '<section class="tiles">' +
      '<div class="tile"><span>Visitantes</span><b>' + fmt(t.visitors) + '</b><small>' + fmt(t.pageviews) + ' páginas vistas</small></div>' +
      '<div class="tile"><span>Clics al carrito de Amazon</span><b>' + fmt(t.carts) + '</b><small>' + pct(t.carts, t.visitors) + ' de los visitantes</small></div>' +
      '<div class="tile"><span>Valor enviado a Amazon</span><b>' + fmt(Math.round(t.cartValue)) + ' €</b><small>Suma de precios orientativos</small></div>' +
      '<div class="tile"><span>Clics en productos sueltos</span><b>' + fmt(t.productClicks) + '</b><small>Miniaturas y complementos</small></div>' +
      '<div class="tile"><span>Suscripciones</span><b>' + fmt(t.subscribers) + '</b><small>Avisos + newsletter</small></div>' +
    "</section>" +
    '<section class="card"><h2>Visitantes por día</h2><p class="sub">Últimos ' + d.days + " días</p>" + chart(daily, W) +
      "<details><summary>Ver como tabla</summary>" + table([
        { label: "Día", get: function (r) { return r.day; } },
        { label: "Visitantes", n: 1, get: function (r) { return r.visitors; } },
        { label: "Páginas vistas", n: 1, get: function (r) { return r.pageviews; } },
        { label: "Clics al carrito", n: 1, get: function (r) { return r.carts; } }
      ], daily.slice().reverse()) + "</details></section>" +
    '<div class="grid2">' +
      '<section class="card wide"><h2>Kits enviados al carrito</h2><p class="sub">Por kit y nivel</p>' + table([
        { label: "Kit", get: kitName },
        { label: "Clics", n: 1, get: function (r) { return r.carts; } },
        { label: "Personas (media)", n: 1, get: function (r) { return r.people; } },
        { label: "Productos (media)", n: 1, get: function (r) { return r.products; } },
        { label: "Valor €", n: 1, get: function (r) { return Math.round(r.value); } }
      ], d.carts) + "</section>" +
      '<section class="card"><h2>Kits que se miran</h2><p class="sub">Visitantes que abren cada kit</p>' + table([
        { label: "Kit", get: kitName },
        { label: "Visitantes", n: 1, get: function (r) { return r.visitors; } }
      ], d.kitViews) + "</section>" +
      '<section class="card"><h2>Productos sueltos</h2><p class="sub">Clics en miniaturas y complementos</p>' + table([
        { label: "Producto", get: function (r) { return r.item; } },
        { label: "Dónde", get: function (r) { return r.type === "extra" ? "Complementos" : "Lista del kit"; } },
        { label: "Clics", n: 1, get: function (r) { return r.clicks; } }
      ], d.items) + "</section>" +
      '<section class="card"><h2>Productos que se quitan</h2><p class="sub">Desmarcados antes de ir a Amazon</p>' + table([
        { label: "Producto", get: function (r) { return r.item; } },
        { label: "Veces", n: 1, get: function (r) { return r.times; } }
      ], d.removed) + "</section>" +
      '<section class="card"><h2>De dónde vienen</h2><p class="sub">Web de origen o campaña (utm_source)</p>' + table([
        { label: "Origen", get: function (r) { return r.ref; } },
        { label: "Visitantes", n: 1, get: function (r) { return r.visitors; } }
      ], d.refs) + "</section>" +
      '<section class="card"><h2>Páginas</h2><p class="sub">Páginas vistas</p>' + table([
        { label: "Página", get: function (r) { return r.path; } },
        { label: "Vistas", n: 1, get: function (r) { return r.pageviews; } }
      ], d.pages) + "</section>" +
      '<section class="card"><h2>Países</h2><p class="sub">Visitantes</p>' + table([
        { label: "País", get: function (r) { return r.country || "–"; } },
        { label: "Visitantes", n: 1, get: function (r) { return r.visitors; } }
      ], d.countries) + "</section>" +
      '<section class="card"><h2>Dispositivos</h2><p class="sub">Visitantes</p>' + table([
        { label: "Dispositivo", get: function (r) { return r.device; } },
        { label: "Visitantes", n: 1, get: function (r) { return r.visitors; } }
      ], d.devices) + "</section>" +
    "</div>";

  var box = document.getElementById("chart"), tip = document.getElementById("tip");
  var bars = box.querySelectorAll(".bar");
  box.addEventListener("mousemove", function (e) {
    var h = e.target.closest(".hit");
    bars.forEach(function (b) { b.classList.remove("on"); });
    if (!h) { tip.hidden = true; return; }
    var i = +h.dataset.i, r = daily[i];
    bars[i].classList.add("on");
    var rect = box.getBoundingClientRect(), hr = h.getBoundingClientRect();
    tip.innerHTML = "<b>" + r.day.split("-").reverse().join("/") + "</b><br>" + fmt(r.visitors) + " visitantes · " + fmt(r.pageviews) + " páginas<br>" + fmt(r.carts) + " clics al carrito";
    tip.style.left = Math.min(Math.max(hr.left - rect.left + hr.width / 2, 80), rect.width - 80) + "px";
    tip.style.top = (e.clientY - rect.top - 10) + "px";
    tip.hidden = false;
  });
  box.addEventListener("mouseleave", function () { tip.hidden = true; bars.forEach(function (b) { b.classList.remove("on"); }); });
}

if (state.key) load();
</script>
</body>
</html>`;
