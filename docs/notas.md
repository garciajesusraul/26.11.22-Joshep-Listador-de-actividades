# Notas de armado — 2do grado, Bimestre 4

## Método

1. Se recorrió el árbol de cada materia en Schoology (`/course/<id>/materials`) buscando la carpeta
   del Bimestre 4 de cada curso, con un scraper `fetch` same-origin ejecutado desde la página
   (`browse.eval`). El resultado crudo quedó en `datos/arbol_materias.json`.
2. Se descargaron las **guías de trabajo (PDF)** de cada tema y se extrajo su texto con PyMuPDF
   (`tools/pdf_text.py` → `datos/pdfs/*.txt`).
3. De cada guía se leyeron las secciones **«Aplicando lo aprendido» / «Apliquemos lo aprendido»**
   y se transcribieron las actividades como subtareas (`2-A`, `2-B`, …).
4. Se leyeron además las páginas de los ítems que no son PDF (foros, tareas de redacción) para no
   inventar contenido.
5. Los datos curados se volcaron en `datos/bimestre-4.json` y el HTML se genera con
   `tools/build_html.py`.

## Lo que NO se abrió (regla del proyecto)

- Ningún `Cuestionario` / `Quiz`.
- Ninguna carpeta `Para el Tutor` / `For the tutor` / `Cartilla para tutor`
  (contienen las correcciones del tutor).
- Ningún video se reprodujo: solo se registró que existe.

Estos ítems se listan con candado y sin enlace, para que el adulto sepa que existen pero el
listado no invite a abrirlos.

## Normalizaciones aplicadas

| En la plataforma | En el listado |
| --- | --- |
| `3.- Cuestionario - Tema NN …` | `Cuestionario (niño)` |
| `Para el Tutor - Tema NN …` / `For the tutor` | `Cuestionario tutor` |

Numeración: los ítems se renumeran 1, 2, 3… dentro de cada tema (sin huecos) y las subtareas
toman la letra del ítem (`2-A`, `2-B`, …). El HTML hace la numeración automáticamente, así que
al agregar o quitar ítems del JSON no hay que renumerar a mano.

## Detalles por materia

- **Ciencias de la Vida** — 6 bloques: Instrucciones B4, Tema 14, Tema 15, Medio Tiempo, Tema 16 y
  Tema 17. El Tema 17 no tiene video ni carpeta de tutor.
- **English** — el bimestre se llama «4th Bimester» y las lecciones son Lesson 8, 9 y 10. Cada una
  tiene videos, workbook, grammar (excepto L10), quiz, audio de apoyo y carpeta del tutor.
- **Historia** — Temas 13 a 16, más dos foros extra: «Practicando los principios de vida» y
  «Mi maqueta».
- **Lenguaje** — Temas 20 a 25. En cada tema hay una tarea de oraciones/palabras (mp3) antes de la
  guía. En T21 y T22 la plataforma **no publica instrucciones escritas** para esa tarea: se listó
  sin inventar contenido. Al final está la tarea «Semana de ponerse al día con el material».
- **Luces y Colores** — Temas 16 a 19, con cartillas de motricidad/manualidad y tres foros extra
  («Clase en vivo» del 17 de noviembre, «La creatividad» y el foro de cada tema).
- **Matemáticas** — Temas 21 a 24 y Cuadernillos 13 a 16, cada uno con su canción de la tabla
  (6, 7, 8 o 9) en mp3 y PDF.
- **Sonidos** — Temas 13, 14 y 15, la cartilla «Juegos y prácticas», dos semanas sin actividades,
  la semana de clases en vivo y el foro «Descubramos: Sonidos y Tecnología».

## Detalles que quedaron documentados, no inventados

- **T21 y T22 de Lenguaje**: la tarea «Palabras para escribir» y «Oraciones Mi huerta» no tienen
  descripción en Schoology. Se listan con una nota que remite a la guía.
- **Hoja de oraciones de Lenguaje**: el PDF adjunto (`Proyecto Jess con trenes difuminados…`) es una
  hoja cuadriculada en blanco para escribir a mano; se verificó renderizando la página a imagen.
- **Foros de Luces y Colores**: la plataforma no trae descripción; las instrucciones (subir la foto
  del trabajo) están en la guía y en la cartilla del tema, y así se anotaron.

## Interfaz

La vista está organizada en **pestañas**: una por materia y una de **estadísticas**. Solo se
muestra la pestaña activa (se recuerda la última usada en `localStorage`). Cada pestaña de materia
muestra el **% hecho** y el **% que falta**, con su barra de avance; la pestaña de estadísticas
resume el total hecho/pendiente y el desglose por materia y por tema.

El buscador recorre todas las materias a la vez (muestra los paneles con coincidencias) y el botón
**«Ocultar tildados»** esconde lo que ya está completo dentro de la materia abierta.

## Cómo seguir con Kinder

Kinder tiene una sola materia: alcanza con repetir el recorrido sobre ese curso y agregar las
materias a `datos/bimestre-4.json` (el HTML se regenera solo). El generador ya soporta cualquier
cantidad de materias, temas e ítems.
