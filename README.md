# El Preparista

Web de [elpreparista.com](https://elpreparista.com): kits de emergencia para casa, coche y evacuación, con la compra en Amazon (Programa de Afiliados).

- `index.html`: la web. Productos, códigos de Amazon (ASIN), alternativas y productos agotados están al principio del script, en `PRODUCTS` y `AGOTADOS`.
- `aviso-legal.html`, `privacidad.html`, `cookies.html`: textos legales (borrador; completar los datos entre corchetes).
- `fonts/`, `fonts.css`: tipografías Barlow y Barlow Condensed (SIL Open Font License), servidas desde la propia web.
- `CNAME`: dominio para GitHub Pages.
- `blog/`, `_posts/`, `_layouts/`, `_includes/`, `_data/`, `blog.css`: el blog (Jekyll, lo genera GitHub Pages). Cómo escribir artículos: `BLOG.md`.
- `consent.js`: aviso de cookies y Google Analytics.
- `analytics/`: backend propio de estadísticas sin cookies (opcional, ver `analytics/README.md`).
- `en.html`: versión en inglés (elpreparista.com/en). **No se edita a mano**: se genera desde `index.html` con `python3 tools/build_en.py`, que contiene todas las traducciones y avisa si algún texto español ha cambiado y falta traducirlo.
