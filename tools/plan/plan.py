"""Genera la hoja «Tu plan de emergencia en una página» (HTML) en español e inglés.
El PDF se crea con tools/plan/pdf.js a partir de estos HTML.
"""
import os

T = {
    "es": dict(
        lang="es", title="Tu plan de emergencia en una página",
        sub="Rellénalo en familia, imprímelo y déjalo en la puerta de la nevera o junto al kit.",
        c1="Teléfonos importantes", c1rows=["Emergencias: <b>112</b>", "Familiar 1", "Familiar 2", "Médico / centro de salud", "Compañía eléctrica (averías)", "Seguro de hogar"],
        c2="Punto de encuentro", c2rows=["Cerca de casa", "Fuera del barrio", "Quién recoge a los niños"],
        c3="En casa: dónde está…", c3rows=["El kit de emergencia", "El cuadro eléctrico", "La llave del agua", "La llave del gas", "Las linternas", "Las copias de documentos"],
        c4="Personas, medicación y alergias", c4h=["Nombre", "Medicación", "Alergias / notas"],
        c5="Mascotas", c5rows=["Nombre y comida", "Veterinario"],
        c6="¿Lo tenemos?", kits=[
            ("Kit Casa", ["Agua: 6 L por persona", "Comida sin cocinar (3 días)", "Linterna y farol + pilas", "Radio de pilas o dinamo", "Powerbank cargada", "Botiquín y medicación", "Efectivo en billetes pequeños"]),
            ("Kit Coche", ["Mantas y agua", "Linterna y chaleco", "Baliza V-16", "Martillo rompecristales", "Cargador de mechero", "Depósito por encima de la mitad"]),
            ("Mochila de salida", ["Una por persona", "Agua y comida para 3 días", "Linterna frontal", "Copias de DNI y recetas", "Silbato y manta térmica"]),
        ],
        c7="Revisión anual", c7rows=["Pilas y linternas", "Powerbank cargada", "Caducidad de agua y comida", "Efectivo en su sitio", "Medicación al día"], c7date="Próxima revisión:",
        foot="elpreparista.com · Kits de emergencia para casa, coche y evacuación", tick="Hecho"),
    "en": dict(
        lang="en", title="Your emergency plan on one page",
        sub="Fill it in as a family, print it and keep it on the fridge door or next to your kit.",
        c1="Important numbers", c1rows=["Emergencies (Spain/EU): <b>112</b>", "Family member 1", "Family member 2", "Doctor / health centre", "Electricity company (faults)", "Home insurance"],
        c2="Meeting point", c2rows=["Near home", "Outside the neighbourhood", "Who picks up the children"],
        c3="At home: where is…", c3rows=["The emergency kit", "The fuse box", "The water stopcock", "The gas valve", "The torches", "The document copies"],
        c4="People, medication and allergies", c4h=["Name", "Medication", "Allergies / notes"],
        c5="Pets", c5rows=["Name and food", "Vet"],
        c6="Do we have it?", kits=[
            ("Home Kit", ["Water: 6 L per person", "No-cook food (3 days)", "Torch and lantern + batteries", "Battery or crank radio", "Charged power bank", "First aid kit and medication", "Cash in small notes"]),
            ("Car Kit", ["Blankets and water", "Torch and reflective vest", "V-16 warning light", "Window breaker", "Car charger", "Tank more than half full"]),
            ("Go bag", ["One per person", "Water and food for 3 days", "Head torch", "Copies of ID and prescriptions", "Whistle and thermal blanket"]),
        ],
        c7="Yearly check", c7rows=["Batteries and torches", "Power bank charged", "Water and food expiry dates", "Cash still there", "Medication up to date"], c7date="Next check:",
        foot="elpreparista.com · Emergency kits for home, car and evacuation", tick="Done"),
}

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Barlow", "Helvetica Neue", Arial, sans-serif; color: #111; font-size: 10.5pt; }
.page { width: 210mm; height: 297mm; padding: 11mm 12mm 9mm; display: flex; flex-direction: column; gap: 4.5mm; }
header { display: flex; align-items: center; gap: 4mm; border-bottom: 1mm solid #111; padding-bottom: 3mm; }
header img { width: 14mm; height: 14mm; }
h1 { font-family: "Barlow Condensed", "Arial Narrow", sans-serif; font-weight: 800; text-transform: uppercase; font-size: 23pt; line-height: 1; margin: 0; }
header p { margin: 1mm 0 0; color: #4B4B4B; font-size: 10pt; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4.5mm; }
.box { border: .6mm solid #111; }
.box h2 { margin: 0; background: #C8102E; color: #fff; font-family: "Barlow Condensed", "Arial Narrow", sans-serif; font-weight: 800; text-transform: uppercase; font-size: 12pt; letter-spacing: .03em; padding: 1.2mm 2.5mm; }
.box.g h2 { background: #00804A; }
.box.k h2 { background: #111; }
.rows { padding: 1mm 2.5mm 2mm; }
.row { display: flex; align-items: flex-end; gap: 2mm; height: 7.2mm; border-bottom: .25mm solid #9a9a95; }
.row span { white-space: nowrap; font-weight: 600; font-size: 9.5pt; padding-bottom: .6mm; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-size: 8.5pt; text-transform: uppercase; letter-spacing: .04em; color: #4B4B4B; padding: 1.5mm 2.5mm 0; }
td { height: 7.5mm; border-bottom: .25mm solid #9a9a95; }
td:first-child { width: 28%; } td:nth-child(2) { width: 37%; }
.kits { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 3mm; padding: 2mm 2.5mm 2.5mm; }
.kits b { font-family: "Barlow Condensed", "Arial Narrow", sans-serif; text-transform: uppercase; font-size: 10.5pt; display: block; margin-bottom: 1mm; }
.kits li, .check li { list-style: none; display: flex; gap: 1.6mm; align-items: flex-start; font-size: 9pt; line-height: 1.25; margin-bottom: 1.1mm; }
.kits ul, .check ul { margin: 0; padding: 0; }
.sq { flex: none; width: 3.4mm; height: 3.4mm; border: .4mm solid #111; margin-top: .3mm; }
.check { padding: 2mm 2.5mm 2.5mm; display: grid; grid-template-columns: 1fr 1fr; gap: 0 4mm; }
.date { grid-column: 1 / -1; display: flex; gap: 2mm; align-items: flex-end; height: 7mm; border-bottom: .25mm solid #9a9a95; font-weight: 700; font-size: 9.5pt; }
footer { margin-top: auto; border-top: .6mm solid #111; padding-top: 2mm; font-size: 8.5pt; color: #4B4B4B; display: flex; justify-content: space-between; }
"""


def rows(items):
    return "".join('<div class="row"><span>%s</span></div>' % i for i in items)


def page(t, logo, fonts):
    kits = "".join("<div><b>%s</b><ul>%s</ul></div>" % (n, "".join('<li><i class="sq"></i>%s</li>' % x for x in it)) for n, it in t["kits"])
    people = "".join("<tr><td></td><td></td><td></td></tr>" for _ in range(4))
    return f"""<!doctype html><html lang="{t['lang']}"><head><meta charset="utf-8"><title>{t['title']}</title>
<link rel="stylesheet" href="{fonts}"><style>{CSS}</style></head><body><div class="page">
<header><img src="{logo}" alt=""><div><h1>{t['title']}</h1><p>{t['sub']}</p></div></header>
<div class="grid">
  <section class="box"><h2>{t['c1']}</h2><div class="rows">{rows(t['c1rows'])}</div></section>
  <section class="box g"><h2>{t['c3']}</h2><div class="rows">{rows(t['c3rows'])}</div></section>
  <section class="box g"><h2>{t['c2']}</h2><div class="rows">{rows(t['c2rows'])}</div></section>
  <section class="box"><h2>{t['c5']}</h2><div class="rows">{rows(t['c5rows'])}</div></section>
</div>
<section class="box"><h2>{t['c4']}</h2><table><tr>{''.join('<th>%s</th>' % h for h in t['c4h'])}</tr>{people}</table></section>
<section class="box k"><h2>{t['c6']}</h2><div class="kits">{kits}</div></section>
<section class="box g"><h2>{t['c7']}</h2><div class="check"><ul>{''.join('<li><i class="sq"></i>%s</li>' % x for x in t['c7rows'][:3])}</ul><ul>{''.join('<li><i class="sq"></i>%s</li>' % x for x in t['c7rows'][3:])}</ul><div class="date">{t['c7date']}</div></div></section>
<footer><span>{t["foot"]}</span></footer>
</div></body></html>"""


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    for code, t in T.items():
        html = page(t, "file://" + root + "/logo.png", "file://" + root + "/fonts.css")
        open(os.path.join(here, "plan-%s.html" % code), "w", encoding="utf-8").write(html)
    print("HTML generados")
