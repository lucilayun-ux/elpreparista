# Cómo escribir en el blog

Cada artículo es un archivo de texto en la carpeta `_posts`. GitHub lo convierte en página automáticamente en 1 o 2 minutos: no hay que tocar nada más.

## Publicar un artículo nuevo desde GitHub

1. Entra en el repositorio, abre la carpeta **`_posts`** y pulsa **Add file → Create new file**.
2. Nombre del archivo: **fecha + título con guiones + `.md`**. Por ejemplo: `2026-11-15-agua-de-emergencia.md`.
   - El título del nombre será la dirección: `elpreparista.com/blog/agua-de-emergencia/`.
   - No uses tildes, eñes ni espacios en el nombre del archivo.
   - Si pones una fecha futura, el artículo no aparece hasta ese día (al volver a publicar algo).
3. Copia esta plantilla y rellénala:

```
---
title: "Título del artículo"
description: "Una o dos frases que resuman el artículo. Salen en la portada del blog y en Google."
category: Apagón
kit: casa
---

Primer párrafo del artículo.

## Un apartado

Texto normal. **Negrita** con dos asteriscos.

- Un punto de una lista
- Otro punto

1. Un paso numerado
2. Otro paso

> Un aviso destacado (sale con fondo amarillo).

| Columna | Otra columna |
|---|---|
| Dato | Dato |
```

4. Pulsa **Commit changes**. En un par de minutos estará en el blog.

## Campos de la cabecera

| Campo | Para qué |
|---|---|
| `title` | Título del artículo. |
| `description` | Resumen. Aparece en la portada del blog, debajo del título y en Google. |
| `category` | Etiqueta negra que sale encima del título (Apagón, Coche, Evacuación…). |
| `kit` | Recuadro final con botón al kit: `casa`, `coche` o `salida`. Si no lo pones, no sale recuadro. |
| `image` | Opcional: una imagen de portada, por ejemplo `/blog/img/apagon.jpg` (sube antes la imagen a esa carpeta). |
| `image_alt` | Descripción de la imagen, para personas ciegas y para Google. |
| `summary` | Opcional: «Respuesta rápida» al principio, en 2-3 frases. Ayuda a salir en Google y en asistentes como ChatGPT. |
| `faq` | Opcional: preguntas frecuentes al final (ver los artículos de 72 horas como ejemplo). Google las entiende como preguntas y respuestas. |

## Enlazar a un kit desde el texto

`[prepara tu Kit Casa](/?kit=casa#kits)` abre la web con ese kit ya elegido. También funciona con `coche` y `salida`.

## Versión en inglés de un artículo

Los artículos en inglés están en la misma carpeta `_posts` y se publican en `elpreparista.com/en/blog/...`. Para que un artículo y su traducción se enlacen entre sí (botón ES/EN y aviso a Google), los dos llevan el mismo `ref`:

```
---
ref: apagon                 ← el mismo en el artículo español y en el inglés
lang: en                    ← solo en el inglés
permalink: /en/blog/power-outage-guide-72-hours/   ← solo en el inglés
title: "What to do in a power outage..."
description: "..."
category: Blackout
kit: casa
---
```

El artículo español solo necesita añadir `ref: apagon`. Los enlaces dentro de un artículo en inglés deben ir a `/en/blog/...` y los botones de kit llevan solos a la web en inglés.
