// Deja escrito en index.html y en.html el contenido que normalmente dibuja el JavaScript
// (kits, niveles, lista del Kit Casa Completo para 2 personas y Complementos), para que lo vean
// los buscadores y asistentes de IA que no ejecutan JavaScript. Al cargar la página, el script
// lo vuelve a dibujar igual, así que para el visitante no cambia nada.
//
// Uso (desde la carpeta del repositorio):  node tools/prerender.js
// Ejecutar SIEMPRE después de tocar index.html y de generar en.html (tools/build.sh lo hace todo).
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const IDS = ["tabs", "kArt", "kArtCap", "kTitle", "kScene", "levels", "rName", "rList", "rCount", "extras"];

function inject(html, id, inner) {
  const open = `<!--pre:${id}-->`, close = `<!--/pre:${id}-->`;
  const block = open + inner + close;
  const i = html.indexOf(open);
  if (i !== -1) {
    const j = html.indexOf(close, i);
    if (j === -1) throw new Error("Marca sin cerrar: " + id);
    return html.slice(0, i) + block + html.slice(j + close.length);
  }
  // Primera vez: el contenedor está vacío, se meten las marcas dentro.
  const re = new RegExp(`(<[a-z0-9]+\\b[^>]*\\bid="${id}"[^>]*>)(</[a-z0-9]+>)`);
  if (!re.test(html)) throw new Error("No encuentro el contenedor vacío #" + id);
  return html.replace(re, `$1${block}$2`);
}

(async () => {
  const browser = await chromium.launch();
  for (const file of ["index.html", "en.html"]) {
    const full = path.join(ROOT, file);
    const ctx = await browser.newContext();
    await ctx.addInitScript(() => { try { localStorage.setItem("ep-cookies", "no"); localStorage.setItem("ep-sub", "1"); } catch (e) {} });
    // Sin red: el contenido sale de la propia página y no se envían estadísticas.
    await ctx.route(/^https?:/, r => r.abort());
    const page = await ctx.newPage();
    await page.goto("file://" + full);
    const parts = await page.evaluate(ids => Object.fromEntries(ids.map(id => [id, document.getElementById(id).innerHTML])), IDS);
    await ctx.close();
    let html = fs.readFileSync(full, "utf8");
    for (const id of IDS) html = inject(html, id, parts[id].replace(/<!--\/?pre:[^>]*-->/g, ""));
    fs.writeFileSync(full, html);
    console.log("Prerenderizado:", file, Object.entries(parts).map(([k, v]) => `${k} ${v.length}`).join(", "));
  }
  await browser.close();
})();
