#!/usr/bin/env python3
"""Genera en.html (versión en inglés, elpreparista.com/en) a partir de index.html.

Uso:  python3 tools/build_en.py            (desde la carpeta del repositorio)
      python3 tools/build_en.py ORIGEN DESTINO

Cada texto en español de la lista TRADUCCIONES se sustituye por su versión inglesa.
Si un texto ya no existe en index.html (porque se ha cambiado en español), el script
se para y dice cuál es, para actualizar aquí la traducción antes de publicar.
"""
import sys

src = sys.argv[1] if len(sys.argv) > 1 else "index.html"
dst = sys.argv[2] if len(sys.argv) > 2 else "en.html"

# Orden: primero los textos largos y concretos, al final los genéricos.
TRADUCCIONES = [
    # --- Cabecera del documento e idioma ---
    ('<html lang="es">', '<html lang="en">'),
    ('<title>El Preparista · Kits de emergencia para casa, coche y evacuación</title>',
     '<title>El Preparista · Emergency kits for home, car and evacuation</title>'),
    ('content="Kits de emergencia para 72 horas: casa, coche y evacuación. Elige tu kit y el nivel y te lo dejamos en tu cesta de Amazon en un clic."',
     'content="72-hour emergency kits for home, car and evacuation in Spain. Choose your kit and level and we put it in your Amazon basket in one click."'),
    ('<link rel="canonical" href="https://elpreparista.com/">', '<link rel="canonical" href="https://elpreparista.com/en">'),
    ('<a class="lang" href="/en" hreflang="en" lang="en" aria-label="English version">EN</a>',
     '<a class="lang" href="/" hreflang="es" lang="es" aria-label="Versión en español">ES</a>'),

    # --- Menú ---
    ('aria-label="El Preparista, inicio"', 'aria-label="El Preparista, home"'),
    ('aria-label="Secciones"', 'aria-label="Sections"'),
    ('<a href="#complementos">Complementos</a>', '<a href="#complementos">Add-ons</a>'),
    ('<a href="#reposicion">Reposición</a>', '<a href="#reposicion">Restocking</a>'),
    ('<a href="#faq">Preguntas</a>', '<a href="#faq">FAQ</a>'),
    ('      <a href="/blog/">Blog</a>\n    </nav>', '      <a href="/en/blog/">Blog</a>\n    </nav>'),
    ('box-shadow:3px 3px 0 var(--ink)">Elegir kit</a>', 'box-shadow:3px 3px 0 var(--ink)">Choose kit</a>'),

    # --- Portada ---
    ('<span class="alert cap">En caso de alerta</span>', '<span class="alert cap">In an emergency</span>'),
    ('<h1>Tu kit de emergencia está <em>preparado</em></h1>', '<h1>Your emergency kit is <em>ready</em></h1>'),
    ('Casi todo el mundo vende la mochila de evacuación. Pero lo que más pasa es <strong>un apagón en casa o horas atrapado en el coche</strong>. Elige tu kit, elige el nivel, revisa productos y te creamos el carrito para comprarlo en Amazon. Así de fácil.',
     'Almost everyone sells the evacuation backpack. But what happens most is <strong>a blackout at home or hours stuck in your car</strong>. Choose your kit, choose the level, review the products and we build the basket for you to buy on Amazon. It&#8217;s that easy.'),
    ('>Elegir mi kit</a>', '>Choose my kit</a>'),
    ('Reposición automática', 'Automatic restocking'),
    ('aria-label="Cómo funciona en cuatro pasos"', 'aria-label="How it works in four steps"'),
    ('<b>En cuatro pasos</b><span class="cap">Cómo funciona</span>', '<b>In four steps</b><span class="cap">How it works</span>'),
    ('alt="Persona de espaldas con la mochila de emergencia puesta"', 'alt="Person seen from behind wearing an emergency backpack"'),
    ('alt="Persona con una mochila de tres módulos: Esencial, Completo y Total"', 'alt="Person wearing a three-module backpack: Essential, Complete and Total"'),
    ('alt="Mano sujetando un móvil con el pedido del kit de emergencia"', 'alt="Hand holding a phone with the emergency kit order"'),
    ('alt="Mujer con una caja de kit de emergencia haciendo el gesto de OK con el pulgar"', 'alt="Woman holding an emergency kit box and giving a thumbs-up"'),
    ('<p>Elige tu kit</p><small>Casa, coche o evacuación.</small>', '<p>Choose your kit</p><small>Home, car or evacuation.</small>'),
    ('<p>¿Esencial o Pro?</p><small>Esencial, Completo o Total.</small>', '<p>Essential or Pro?</p><small>Essential, Complete or Total.</small>'),
    ('<p>Todo al carrito</p><small>Un clic y te creamos el pedido.</small>', '<p>All in the basket</p><small>One click and we build your order.</small>'),
    ('<p>Recíbelo en casa</p><small>¡Estamos preparados!</small>', '<p>Delivered to your door</p><small>We&#8217;re ready!</small>'),

    # --- Kits ---
    ('<h2>Tres kits, tres niveles</h2>', '<h2>Three kits, three levels</h2>'),
    ('<p>Cada kit cubre una situación distinta. Dentro de cada uno, elige de menos a más completo.</p>',
     '<p>Each kit covers a different situation. Within each one, choose from basic to most complete.</p>'),
    ('aria-label="Tipo de kit"', 'aria-label="Kit type"'),
    ('<span class="ex">Imagen de ejemplo</span>', '<span class="ex">Sample image</span>'),
    ('<h3>Elige el nivel</h3>', '<h3>Choose the level</h3>'),
    ('¿Cuántos sois?', 'How many of you?'),
    ('aria-label="Una persona menos"', 'aria-label="One person fewer"'),
    ('aria-label="Una persona más"', 'aria-label="One more person"'),
    ('aria-label="Nivel del kit"', 'aria-label="Kit level"'),
    ('<h3>Revisa y compra</h3>', '<h3>Review and buy</h3>'),
    ('<span class="cap">Contenido del kit</span>', '<span class="cap">Kit contents</span>'),
    ('Desmarca lo que ya tengas. Se abre Amazon con los productos ya en tu cesta; pagas allí, con tu cuenta y tu envío.',
     'Untick anything you already have. Amazon opens with the products already in your basket; you pay there, with your own account and delivery. Products are sold on Amazon Spain (amazon.es).'),
    ('rel="noopener sponsored">Revisa y compra tu kit</a>', 'rel="noopener sponsored">Review and buy your kit</a>'),

    # --- Complementos ---
    ('<span class="cap" style="color:var(--red)">Complementos</span>', '<span class="cap" style="color:var(--red)">Add-ons</span>'),
    ('<h2>Mejora tu kit</h2>', '<h2>Upgrade your kit</h2>'),
    ('<p>Piezas sueltas para ampliar el kit que ya tienes o reponer lo que hayas usado.</p>',
     '<p>Individual items to expand the kit you already have or replace what you have used.</p>'),

    # --- Reposición ---
    ('<h2>No te vendemos un kit, te ponemos fácil conseguirlo</h2>', '<h2>We don&#8217;t sell you a kit, we make it easy to get one</h2>'),
    ('<p>Te recordamos por mail las fechas de caducidad. Un kit con el agua caducada no sirve de nada.</p>',
     '<p>We email you when things are about to expire. A kit with expired water is no use to anyone.</p>'),
    ('<span class="when">Hoy</span><p><b>Compras tu kit.</b> Guardamos la fecha de caducidad aproximada de cada pieza.</p>',
     '<span class="when">Today</span><p><b>You buy your kit.</b> We store the approximate expiry date of each item.</p>'),
    ('<span class="when">Cada año</span><p><b>Te recordamos revisarlo:</b> pilas, linterna, que el efectivo siga en el sobre.</p>',
     '<span class="when">Every year</span><p><b>We remind you to check it:</b> batteries, torch, and that the cash is still in the envelope.</p>'),
    ('<span class="when">Cada mes</span><p><b>Información de interés</b> en nuestra newsletter: consejos de preparación y novedades en los kits.</p>',
     '<span class="when">Every month</span><p><b>Useful information</b> in our newsletter: preparedness tips and kit updates.</p>'),
    ('<span class="when">Siempre</span><p><b>Compartimos</b> noticias, alertas y avisos de temporal.</p>',
     '<span class="when">Always</span><p><b>We share</b> news, alerts and storm warnings.</p>'),
    ('<b>Entra en la comunidad</b><span class="cap">Avisos + newsletter</span>', '<b>Join the community</b><span class="cap">Reminders + newsletter</span>'),
    ('<label for="rEmail">Tu email</label>', '<label for="rEmail">Your email</label>'),
    ('placeholder="nombre@correo.com"', 'placeholder="name@email.com"'),
    ('<label for="rPhone">Teléfono (opcional)</label>', '<label for="rPhone">Phone (optional)</label>'),
    ('placeholder="600 000 000"', 'placeholder="+34 600 000 000"'),
    ('<label for="rFullName">Nombre y apellido</label>', '<label for="rFullName">Full name</label>'),
    ('placeholder="Nombre Apellido"', 'placeholder="First and last name"'),
    ('<label for="rWeb">No rellenes este campo</label>', '<label for="rWeb">Leave this field empty</label>'),
    ('<li>Avisos antes de que caduque tu kit</li><li>Newsletter con información de interés</li><li>Alertas cuando se acerca un temporal</li>',
     '<li>Reminders before your kit expires</li><li>Newsletter with useful information</li><li>Alerts when a storm is coming</li>'),
    ('style="background:var(--green)">Suscribirme</button>', 'style="background:var(--green)">Subscribe</button>'),
    ('Al suscribirte recibirás los avisos de caducidad y nuestra newsletter. Puedes darte de baja con un clic en cualquier email.',
     'By subscribing you will receive expiry reminders and our newsletter. You can unsubscribe with one click from any email.'),

    # --- Preguntas frecuentes ---
    ('<span class="cap" style="color:var(--red)">Preguntas frecuentes</span>', '<span class="cap" style="color:var(--red)">Frequently asked questions</span>'),
    ('<h2>Lo que nos preguntáis</h2>', '<h2>What people ask us</h2>'),
    ('<summary>¿Por qué tres kits y no una mochila?</summary><p>Porque las emergencias más habituales en España no son evacuaciones. Son apagones como el de abril de 2025, temporales y DANAs, y nevadas que dejan a la gente horas en la carretera. Cada situación pide cosas distintas y en un sitio distinto: una caja en el armario, una bolsa en el maletero y una mochila en la entrada.</p>',
     '<summary>Why three kits and not just a backpack?</summary><p>Because the most common emergencies in Spain are not evacuations. They are blackouts like the one in April 2025, storms and flash floods (DANAs), and snowfalls that leave people stuck on the road for hours. Each situation calls for different things in a different place: a box in the cupboard, a bag in the car boot and a backpack by the door.</p>'),
    ('<summary>¿Qué nivel elijo?</summary><p>Si no tienes nada, el Esencial ya te cubre lo básico. El Completo es el que recomendamos para una familia. El Total es para quien vive en zona de nevadas, inundaciones o lejos de todo.</p>',
     '<summary>Which level should I choose?</summary><p>If you have nothing yet, Essential already covers the basics. Complete is the one we recommend for a family. Total is for people who live in areas prone to snow or flooding, or far from everything.</p>'),
    ('<summary>¿Quién me vende los productos?</summary><p>Amazon. Nosotros elegimos los productos y calculamos las cantidades; la compra, el pago, el envío y las devoluciones son con Amazon, igual que cualquier otro pedido tuyo.</p>',
     '<summary>Who sells me the products?</summary><p>Amazon. We choose the products and calculate the quantities; the purchase, payment, delivery and returns are with Amazon, just like any other order of yours. The links go to Amazon Spain (amazon.es), where you can switch the site language to English.</p>'),
    ('<summary>¿Me cuesta más comprar desde aquí?</summary><p>No. Pagas lo mismo que si buscaras cada producto tú. Amazon nos da una pequeña comisión por recomendarlos.</p>',
     '<summary>Does it cost more to buy through you?</summary><p>No. You pay the same as if you searched for each product yourself. Amazon pays us a small commission for recommending them.</p>'),
    ('<summary>¿Cuánta agua hace falta?</summary><p>En casa, 2 litros para beber por persona y día, que es lo que recomienda Protección Civil: 6 litros por persona para 72 horas. En el coche calculamos 1,5 litros por persona para un atasco largo.</p>',
     '<summary>How much water do I need?</summary><p>At home, 2 litres of drinking water per person per day, as recommended by Spanish Civil Protection: 6 litres per person for 72 hours. In the car we allow 1.5 litres per person for a long traffic jam.</p>'),

    # --- Pie ---
    ('Como Afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables.',
     'As an Amazon Associate I earn from qualifying purchases.'),
    ('<p><a href="/blog/">Blog</a> · <a href="aviso-legal.html">Aviso legal</a> · <a href="privacidad.html">Privacidad</a> · <a href="cookies.html">Cookies</a> · <a href="#" data-cookies>Configurar cookies</a></p>',
     '<p><a href="/en/blog/">Blog</a> · <a href="aviso-legal.html" hreflang="es">Legal notice</a> · <a href="privacidad.html" hreflang="es">Privacy</a> · <a href="cookies.html" hreflang="es">Cookies</a> (in Spanish) · <a href="#" data-cookies>Cookie settings</a> · <a href="/" hreflang="es" lang="es">Versión en español</a></p>'),

    # --- Ilustraciones de los kits ---
    ('cap: "Formato caja"', 'cap: "Box format"'),
    ('cap: "Formato bolsa"', 'cap: "Bag format"'),
    ('cap: "Formato mochila"', 'cap: "Backpack format"'),
    ('aria-label="Imagen de ejemplo: caja roja del Kit Casa"', 'aria-label="Sample image: red Home Kit box"'),
    ('aria-label="Imagen de ejemplo: bolsa negra con banda reflectante del Kit Coche"', 'aria-label="Sample image: black Car Kit bag with a reflective band"'),
    ('aria-label="Imagen de ejemplo: mochila verde del Kit Salida"', 'aria-label="Sample image: green Go Bag backpack"'),
    ('>KIT CASA</text>', '>HOME KIT</text>'),
    ('>72 HORAS</text>', '>72 HOURS</text>'),
    ('>KIT COCHE</text>', '>CAR KIT</text>'),
    ('>KIT SALIDA · 72 H</text>', '>GO BAG · 72 H</text>'),

    # --- Productos (solo el nombre que se ve; las búsquedas en amazon.es siguen en español) ---
    ('name: "Caja de almacenaje con tapa"', 'name: "Storage box with lid"'),
    ('name: "Agua de emergencia en sobres (5 años)"', 'name: "Emergency water pouches (5-year shelf life)"'),
    ('name: "Raciones de 3.600 kcal sin cocinar (5 años)"', 'name: "3,600 kcal no-cook rations (5-year shelf life)"'),
    ('name: "Raciones de emergencia NRG-5 sin cocinar"', 'name: "NRG-5 no-cook emergency rations"'),
    ('name: "Linterna LED"', 'name: "LED torch"'),
    ('name: "Farol LED de mesa"', 'name: "LED table lantern"'),
    ('name: "Pilas Duracell AA y AAA (24 uds)"', 'name: "Duracell AA and AAA batteries (24 pack)"'),
    ('name: "Radio de dinamo y solar con USB"', 'name: "Hand-crank and solar radio with USB"'),
    ('name: "Powerbank 20.000 mAh"', 'name: "20,000 mAh power bank"'),
    ('name: "Funda estanca para documentos y efectivo"', 'name: "Waterproof pouch for documents and cash"'),
    ('name: "Efectivo en billetes pequeños", diy: "Lo pones tú: 150–200 €"', 'name: "Cash in small notes", diy: "You add it: €150–200"'),
    ('name: "Copias de DNI, seguros y recetas", diy: "Lo pones tú: fotocopias"', 'name: "Copies of ID, insurance and prescriptions", diy: "You add it: photocopies"'),
    ('name: "Botiquín de primeros auxilios (120 piezas)"', 'name: "First aid kit (120 pieces)"'),
    ('name: "Botiquín de primeros auxilios (200 piezas)"', 'name: "First aid kit (200 pieces)"'),
    ('name: "Mantas térmicas"', 'name: "Emergency thermal blankets"'),
    ('name: "Garrafa de 10 L con grifo"', 'name: "10 L water container with tap"'),
    ('name: "Estación de energía portátil 300 W"', 'name: "300 W portable power station"'),
    ('name: "Panel solar plegable USB"', 'name: "Foldable USB solar panel"'),
    ('name: "Filtro de agua portátil"', 'name: "Portable water filter"'),
    ('name: "Bolsa organizadora para maletero"', 'name: "Car boot organiser bag"'),
    ('name: "Barritas de emergencia NRG-5"', 'name: "NRG-5 emergency food bars"'),
    ('name: "Manta polar de viaje"', 'name: "Fleece travel blanket"'),
    ('name: "Chalecos reflectantes"', 'name: "Reflective vests"'),
    ('name: "Martillo rompecristales con cortacinturones"', 'name: "Window breaker with seatbelt cutter"'),
    ('name: "Cargador USB de mechero"', 'name: "USB car charger"'),
    ('name: "Baliza V-16 conectada (obligatoria desde 2026)"', 'name: "V-16 connected warning light (mandatory in Spain from 2026)"'),
    ('name: "Guantes térmicos impermeables"', 'name: "Waterproof thermal gloves"'),
    ('name: "Pala plegable"', 'name: "Folding shovel"'),
    ('name: "Fundas textiles de nieve AutoSock"', 'name: "AutoSock textile snow socks"'),
    ('note: "Elige la medida de tu rueda"', 'note: "Choose your tyre size"'),
    ('name: "Arrancador de batería con powerbank"', 'name: "Car jump starter with power bank"'),
    ('name: "Botiquín de coche"', 'name: "Car first aid kit"'),
    ('name: "Mochila de 40 L"', 'name: "40 L backpack"'),
    ('name: "Linterna frontal"', 'name: "Head torch"'),
    ('name: "Ponchos de lluvia"', 'name: "Rain ponchos"'),
    ('name: "Silbatos de emergencia"', 'name: "Emergency whistles"'),
    ('name: "Navaja suiza multiusos"', 'name: "Swiss army knife"'),
    ('name: "Cuerda paracord 30 m"', 'name: "30 m paracord rope"'),
    ('name: "Saco vivac de emergencia"', 'name: "Emergency bivvy bag"'),
    ('name: "Neceser con botes rellenables"', 'name: "Toiletry bag with refillable bottles"'),
    ('name: "Pastillas potabilizadoras"', 'name: "Water purification tablets"'),
    ('name: "Hornillo de gas compacto"', 'name: "Compact gas stove"'),

    # --- Kits y niveles ---
    ('name: "Kit Casa", tab: "Apagón y cortes de agua"', 'name: "Home Kit", tab: "Blackouts and water cuts"'),
    ('scene: "No es una mochila: es una caja que vive en un armario. Luz, agua, comida sin cocinar, radio, batería, efectivo y documentos para aguantar 72 horas."',
     'scene: "Not a backpack: a box that lives in a cupboard. Light, water, no-cook food, radio, battery, cash and documents to get through 72 hours."'),
    ('blurb: "Lo mínimo para un apagón de tres días."', 'blurb: "The minimum for a three-day blackout."'),
    ('blurb: "Con batería para los móviles, botiquín y luz para toda la casa."', 'blurb: "With a battery for phones, a first aid kit and light for the whole home."'),
    ('blurb: "Energía propia para días: estación, panel solar y filtro de agua."', 'blurb: "Your own power for days: power station, solar panel and water filter."'),
    ('name: "Kit Coche", tab: "Nevada, DANA, atasco de horas"', 'name: "Car Kit", tab: "Snow, flash floods, hours-long jams"'),
    ('scene: "Una bolsa que vive en el maletero. Para pasar una noche en la carretera con frío, sin quedarte sin móvil y pudiendo salir del coche si hace falta."',
     'scene: "A bag that lives in the car boot. To spend a cold night on the road without your phone dying, and able to get out of the car if you need to."'),
    ('blurb: "Abrigo, agua, luz y la herramienta para salir del coche."', 'blurb: "Warmth, water, light and the tool to get out of the car."'),
    ('blurb: "Para nevadas: comida, guantes, pala y batería extra."', 'blurb: "For snow: food, gloves, shovel and an extra battery."'),
    ('blurb: "Para quien conduce mucho o en zona de montaña."', 'blurb: "For people who drive a lot or in mountain areas."'),
    ('name: "Kit Salida", tab: "Evacuar con lo puesto"', 'name: "Go Bag", tab: "Evacuate with just the essentials"'),
    ('scene: "La mochila para salir de casa en un minuto: incendio, inundación o aviso de evacuación. Una por persona, colgada junto a la puerta."',
     'scene: "The backpack to leave home in a minute: fire, flood or an evacuation order. One per person, hanging by the door."'),
    ('blurb: "Agua, comida, luz y abrigo para 72 horas."', 'blurb: "Water, food, light and warmth for 72 hours."'),
    ('blurb: "Con botiquín, radio, batería y herramientas."', 'blurb: "With a first aid kit, radio, battery and tools."'),
    ('blurb: "Para pasar noches fuera: agua filtrada, refugio y cocina."', 'blurb: "For nights away: filtered water, shelter and cooking."'),
    ('name: "Esencial",', 'name: "Essential",'),
    ('name: "Completo",', 'name: "Complete",'),

    # --- Textos generados por el script ---
    ('''  if (l.unit === "raciones") return `${fmt(l.amount)} raciones`;
  if (l.pack > 1) return `${fmt(l.amount)} uds`;
  const plural = { ud: "uds", pack: "packs", par: "pares", juego: "juegos" };
  return `${l.qty} ${l.qty > 1 ? plural[l.unit] : l.unit}`;''',
     '''  if (l.unit === "raciones") return `${fmt(l.amount)} rations`;
  if (l.pack > 1) return `${fmt(l.amount)} pcs`;
  const UNIT = { ud: ["unit", "units"], pack: ["pack", "packs"], par: ["pair", "pairs"], juego: ["set", "sets"] };
  return `${l.qty} ${UNIT[l.unit][l.qty > 1 ? 1 : 0]}`;'''),
    ('<span class="badge">Recomendado</span>', '<span class="badge">Recommended</span>'),
    ('"Todo lo del " + kit.levels[i - 1].name + ", más: "', '"Everything in " + kit.levels[i - 1].name + ", plus: "'),
    ('${n} artículos', '${n} items'),
    ('"1 persona" : p + " personas"', '"1 person" : p + " people"'),
    ('title="No se compra"', 'title="Not bought online"'),
    ('aria-label="Ver ${l.name} en Amazon"', 'aria-label="View ${l.name} on Amazon"'),
    ('aria-label="Ver ${pr.name} en Amazon"', 'aria-label="View ${pr.name} on Amazon"'),
    ('aria-label="Incluir ${l.name} en el carrito"', 'aria-label="Include ${l.name} in the basket"'),
    ('`${toBuy.length} productos para comprar`', '`${toBuy.length} products to buy`'),
    ('`${toBuy.length} de ${buyable.length} productos para comprar`', '`${toBuy.length} of ${buyable.length} products to buy`'),
    ('` · ${units} unidades en la cesta`', '` · ${units} units in the basket`'),
    ('"No has elegido ningún producto"', '"You haven\'t chosen any products"'),
    ('"Revisa y compra tu kit" : `Revisa y compra tu kit (${toBuy.length} productos)`', '"Review and buy your kit" : `Review and buy your kit (${toBuy.length} products)`'),
    ('"Empezar la compra en Amazon"', '"Start shopping on Amazon"'),
    ('["estacion", "Carga móviles, luces y una nevera pequeña durante días."]', '["estacion", "Charges phones, lights and a small fridge for days."]'),
    ('["solar", "Recarga baterías con el sol si el apagón se alarga."]', '["solar", "Recharges batteries from the sun if the blackout drags on."]'),
    ('["radio", "Noticias sin luz ni cobertura, a manivela o solar."]', '["radio", "News without power or signal, by hand crank or solar."]'),
    ('["frontal", "Luz sin ocupar las manos."]', '["frontal", "Light with your hands free."]'),
    ('["powerbank", "Dos o tres cargas completas de móvil."]', '["powerbank", "Two or three full phone charges."]'),
    ('["filtro", "Agua potable a partir de agua dudosa."]', '["filtro", "Drinking water from water you are unsure about."]'),
    ('["pastillas", "Para potabilizar agua almacenada o del grifo."]', '["pastillas", "To make stored or tap water safe to drink."]'),
    ('["garrafa", "Llénala cuando avisen de cortes de agua."]', '["garrafa", "Fill it up when water cuts are announced."]'),
    ('["botiquin", "Para casa, coche o mochila."]', '["botiquin", "For home, car or backpack."]'),
    ('["hornillo", "Comida caliente sin electricidad."]', '["hornillo", "Hot food without electricity."]'),
    ('["v16", "Avisa de tu posición si te quedas parado en la carretera."]', '["v16", "Signals your position if you break down on the road."]'),
    ('["mantas", "Ligeras y pequeñas, para casa, coche o mochila."]', '["mantas", "Light and small, for home, car or backpack."]'),
    ('>Ver en Amazon</a>', '>View on Amazon</a>'),
    ('"Escribe un email válido para poder avisarte."', '"Please enter a valid email so we can reach you."'),
    ('"Las suscripciones abren muy pronto. Vuelve en unos días."', '"Subscriptions open very soon. Please come back in a few days."'),
    ('"No hemos podido guardar tu suscripción. Inténtalo de nuevo en unos minutos."', '"We couldn\'t save your subscription. Please try again in a few minutes."'),
    ('btn.textContent = "Guardando…"', 'btn.textContent = "Saving…"'),
    ('btn.textContent = "Suscribirme"', 'btn.textContent = "Subscribe"'),
    ('btn.textContent = "Suscrito ✓"', 'btn.textContent = "Subscribed ✓"'),
    ('`Listo${name ? ", " + name : ""}, ya estás suscrito. Primera revisión: ${yearly}. Aviso de reposición del agua y la comida: ${due}.`',
     '`Done${name ? ", " + name : ""}, you\'re subscribed. First check-up: ${yearly}. Water and food restock reminder: ${due}.`'),
    ('source: "web" }', 'source: "web-en" }'),
    ('"es-ES"', '"en-GB"'),

    ('Elige tu kit', 'Choose your kit'),
]

# Genéricos: se aplican al final si queda alguno suelto (pueden no aparecer).
OPCIONALES = [
    ('Kit Casa', 'Home Kit'),
    ('Kit Coche', 'Car Kit'),
    ('Kit Salida', 'Go Bag'),
]

html = open(src, encoding="utf-8").read()
faltan = []
for es, en in TRADUCCIONES:
    if es not in html:
        faltan.append(es)
        continue
    html = html.replace(es, en)

for es, en in OPCIONALES:
    html = html.replace(es, en)

if faltan:
    print("Estos textos ya no están en %s; actualiza su traducción en tools/build_en.py:" % src)
    for t in faltan:
        print("  -", t[:110].replace("\n", " "))
    sys.exit(1)

open(dst, "w", encoding="utf-8").write(html)
print("OK: %s generado (%d traducciones)" % (dst, len(TRADUCCIONES)))
