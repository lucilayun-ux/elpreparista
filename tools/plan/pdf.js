// Convierte plan-es.html y plan-en.html en PDF (A4, una página) dentro de descargas/.
// Uso: python3 tools/plan/plan.py && node tools/plan/pdf.js
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

(async () => {
  const here = __dirname;
  const out = path.join(here, "..", "..", "descargas");
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [code, name] of [["es", "plan-de-emergencia.pdf"], ["en", "emergency-plan.pdf"]]) {
    await page.goto("file://" + path.join(here, `plan-${code}.html`));
    await page.waitForLoadState("networkidle");
    await page.pdf({ path: path.join(out, name), format: "A4", printBackground: true, pageRanges: "1" });
    await page.screenshot({ path: path.join(here, `plan-${code}.png`), fullPage: true });
    console.log("PDF:", name);
  }
  await browser.close();
})();
