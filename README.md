# Listador de actividades — 2do grado, Bimestre 4

Checklist estático de las actividades del **Bimestre 4 de 2do grado** de Joseph's House School,
armado a partir de los materiales publicados en Schoology.

**Producto:** [`2do-grado-bimestre-4.html`](2do-grado-bimestre-4.html) — un solo archivo HTML,
sin dependencias, sin build y sin CDN. Se puede abrir con doble clic o publicar tal cual.

## Qué incluye

- 7 materias: Ciencias de la Vida, English, Historia, Lenguaje, Luces y Colores, Matemáticas y Sonidos.
- Cada tema con sus ítems numerados (1, 2, 3…) y las subtareas reales de cada guía en PDF
  etiquetadas como `2-A)`, `2-B)`, `2-C)`…
- Los **cuestionarios** aparecen listados con candado 🔒 y **sin enlace**: los abren únicamente
  el niño y el tutor.
- Progreso guardado en `localStorage`, con **Exportar / Importar** en JSON.
- Navegación por **pestañas: una por materia + una de estadísticas**; se recuerda la última pestaña abierta.
- Cada pestaña muestra el **% hecho y el % que falta**, con barra de avance por materia.
- Pestaña **Estadísticas**: total hecho/pendiente, avance global y desglose por materia y por tema.
- Botón **«Ocultar tildados»** para ver únicamente lo que falta.
- Buscador de actividades que recorre todas las materias a la vez.

## Cómo usarlo

1. Abrir `2do-grado-bimestre-4.html` en el navegador.
2. Elegir la materia en las pestañas (o mirar **📊 Estadísticas** para el panorama general).
3. Tildar las subtareas a medida que se completan (el ítem padre se tilda solo cuando están todas).
4. Usar «Ocultar tildados» para quedarse solo con lo pendiente.
5. Exportar el progreso de vez en cuando como respaldo (`progreso-2do-bimestre-4.json`).

## Publicarlo en GitHub Pages

```bash
git init
git add .
git commit -m "Listador de actividades 2do grado - Bimestre 4"
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
```

Después, en el repo: *Settings → Pages → Source: Deploy from a branch → main / (root)*.
La página queda en `https://<usuario>.github.io/<repo>/2do-grado-bimestre-4.html`.

## En Cloudflare Pages

- *Create a project → Connect to Git* (o subida directa de la carpeta).
- **Build command:** vacío. **Output directory:** `/`.

## Estructura del proyecto

```
2do-grado-bimestre-4.html   ← checklist final (autocontenido)
datos/bimestre-4.json       ← fuente de verdad curada
tools/build_html.py         ← genera el HTML a partir del JSON
tools/pdf_text.py           ← extrae texto de los PDF de las guías
tools/show_tree.py          ← imprime el árbol scrapeado de Schoology
docs/notas.md               ← método, decisiones y pendientes
AGENTS.md                   ← reglas del proyecto (incluye la prohibición de cuestionarios)
```

Para regenerar el HTML después de editar el JSON:

```bash
python tools/build_html.py
```

## Regla principal

Los cuestionarios (`Cuestionario`, `Para el Tutor`, evaluaciones) **no se abren, ni se leen,
ni se descargan**: solo se listan. Ver `AGENTS.md`.
