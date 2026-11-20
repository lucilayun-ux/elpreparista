# El Preparista

Web de [elpreparista.com](https://elpreparista.com): kits de emergencia para casa, coche y evacuación, con la compra en Amazon (Programa de Afiliados).

- `index.html`: la web. Productos, códigos de Amazon (ASIN), alternativas y productos agotados están al principio del script, en `PRODUCTS` y `AGOTADOS`.
- `aviso-legal.html`, `privacidad.html`, `cookies.html`: textos legales (borrador; completar los datos entre corchetes).
- `fonts/`, `fonts.css`: tipografías Barlow y Barlow Condensed (SIL Open Font License), servidas desde la propia web.
- `CNAME`: dominio para GitHub Pages.
- `blog/`, `_posts/`, `_layouts/`, `_includes/`, `_data/`, `blog.css`: el blog (Jekyll, lo genera GitHub Pages). Cómo escribir artículos: `BLOG.md`.
- `consent.js`: aviso de cookies y Google Analytics.
- `analytics/`: backend propio de estadísticas sin cookies (opcional, ver `analytics/README.md`).
- `en.html`: versión en inglés (elpreparista.com/en). **No se edita a mano**: se genera desde `index.html`.
- **Después de cualquier cambio en `index.html`, ejecuta `bash tools/build.sh`.** Genera `en.html` (traducciones en `tools/build_en.py`, avisa si falta alguna) y deja escrito en las dos páginas el contenido de la lista y de Complementos, para que lo vean buscadores y asistentes de IA (`tools/prerender.js`).
- `tools/porque.py`: el motivo de cada producto («por qué este»), en español e inglés.
- `descargas/`: el plan de emergencia en PDF (regalo al suscribirse). Se genera con `python3 tools/plan/plan.py && node tools/plan/pdf.js`.
- `quienes-somos.md`, `en/about.md`: quiénes somos y cómo elegimos los productos.
