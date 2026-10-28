# Estadísticas y suscriptores de El Preparista

Backend propio de estadísticas y suscriptores para elpreparista.com. Funciona en **Cloudflare Workers** con una base de datos **D1**. El plan gratuito da de sobra: 100.000 eventos al día y 5 GB de base de datos.

- No usa cookies ni guarda la IP. Cada visitante se cuenta con un código que cambia cada día, así que no hace falta aviso de cookies.
- Descarta robots y buscadores.
- Solo acepta eventos que vengan de elpreparista.com.

## Qué mide

| Evento | Cuándo se envía |
|---|---|
| Visita | Al abrir la web. Guarda de dónde viene (Google, Instagram…) o la campaña `?utm_source=`. |
| Kit | Al elegir Kit Casa, Coche o Salida. |
| Nivel | Al elegir Esencial, Completo o Total. |
| Carrito | Al pulsar «Revisa y compra tu kit». Guarda kit, nivel, personas, número de productos y precio orientativo. |
| Producto | Al pulsar la miniatura de un producto de la lista. |
| Complemento | Al pulsar un producto de Complementos. |
| Quitado | Al desmarcar un producto de la lista. |
| Suscripción | Al suscribirse (solo si dio teléfono o no; nunca el email ni el nombre). |

## Suscriptores (leads)

El formulario «Suscríbete gratis» de la web guarda cada suscripción (nombre, email, teléfono y fecha) en la misma base de datos. Se ven en el panel, pestaña **Suscriptores**: buscador, botón **Descargar Excel (CSV)** y botón **Borrar** (para cuando alguien pida que borres sus datos).

- Si un email ya estaba, no se duplica: se actualizan el nombre y el teléfono.
- Solo se aceptan suscripciones enviadas desde elpreparista.com, y un campo invisible frena a los robots.
- La dirección del backend está en `index.html`, en `ANALYTICS_URL` (https://elpreparista-stats.lucialayunta.workers.dev).

El panel muestra visitantes por día, clics al carrito, el valor enviado a Amazon, qué kits y niveles se compran, qué productos se miran y cuáles se quitan, de dónde vienen las visitas, países y dispositivos.

## Ponerlo en marcha (desde la web de Cloudflare, sin programar)

1. Crea una cuenta gratuita en [dash.cloudflare.com](https://dash.cloudflare.com).
2. **Base de datos:** menú *Storage & Databases → D1 → Create database*. Nombre: `elpreparista-stats`. No hace falta crear tablas: el Worker las crea solo.
3. **Worker:** menú *Workers & Pages → Create → Create Worker*. Nombre: `elpreparista-stats`. Pulsa *Deploy*, luego *Edit code*, borra lo que haya, pega el contenido de `worker.js` y pulsa *Deploy*.
4. **Conectar la base de datos:** en el Worker, *Settings → Bindings → Add → D1 database*. Variable name: `DB`. Database: `elpreparista-stats`. Guarda.
5. **Clave del panel:** en el Worker, *Settings → Variables and Secrets → Add*. Tipo *Secret*, nombre `ADMIN_KEY`, y como valor una contraseña larga que solo sepas tú. Guarda.
6. Copia la dirección del Worker. Es parecida a `https://elpreparista-stats.TU-USUARIO.workers.dev`.
7. En `index.html`, busca `const ANALYTICS_URL = "";` y pon esa dirección entre las comillas, sin barra al final:
   ```js
   const ANALYTICS_URL = "https://elpreparista-stats.TU-USUARIO.workers.dev";
   ```
   Sube el cambio a GitHub. Desde ese momento la web empieza a enviar datos.
8. **Ver el panel:** abre la dirección del Worker en el navegador y escribe la clave del paso 5.

## Opcional

- **Dirección propia** (por ejemplo `stats.elpreparista.com`): en el Worker, *Settings → Domains & Routes → Add → Custom domain*. Requiere que el dominio esté en Cloudflare; si sigue en IONOS, usa la dirección `workers.dev`.
- **Otros dominios** que puedan enviar datos: variable `ALLOWED_ORIGINS` con los dominios separados por comas. Por defecto: `https://elpreparista.com,https://www.elpreparista.com`.
- **Con la línea de comandos:** pon el id de la base D1 en `wrangler.toml` y ejecuta `npx wrangler deploy` y `npx wrangler secret put ADMIN_KEY` dentro de esta carpeta.
- **Campañas:** añade `?utm_source=instagram` (o el nombre que quieras) a los enlaces que compartas y aparecerán en «De dónde vienen».
