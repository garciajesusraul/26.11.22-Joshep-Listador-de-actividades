# AGENTS.md — Listador de actividades (Joseph's House School)

## ⛔ REGLA #1 — PROHIBIDO ENTRAR A CUESTIONARIOS

**Bajo ninguna circunstancia abrir, clickear, navegar ni descargar** ningún ítem que sea un
cuestionario/evaluación. Esos ítems **solo los abre el niño y el padre**.

Está prohibido entrar a:

- `Cuestionario`
- `Cuestionario (niño)` (nombre normalizado de `Cuestionario`)
- `Para el Tutor`
- `Cuestionario tutor` (nombre normalizado de `Para el Tutor`)
- Cualquier ítem de tipo **Evaluación** / **Prueba** / **Examen** / **Test** en Schoology
- Cualquier carpeta que contenga estos ítems (ej. la carpeta `Para el Tutor - Tema NN`)

Se permite únicamente **leer el título** para listarlo. Nada más. Ni siquiera "para ver
si tiene instrucciones".

Válido para todos los grados, todas las materias y todas las sesiones futuras.

## Reglas de normalización

| En la plataforma | En el listado |
| --- | --- |
| `3.- Cuestionario - Tema NN ...` | `3.- Cuestionario (niño)` |
| `Para el Tutor - Tema NN ...` | `4.- Cuestionario tutor` |

Los ítems se **renumeran prolijo** (1, 2, 3, …) dentro de cada tema, sin huecos.

## Jerarquía del listado

```
Grado (2do grado | Kinder)
└── Materia (7 en 2do grado, 1 en Kinder)
    └── Bimestre (4 por materia)
        └── Ítem  (Tema NN, Medio Tiempo, Instrucciones, Foro, …)
            └── Sub-ítem (Video, Guía de Trabajo, Foro, Cuestionario niño, Cuestionario tutor)
                └── Subtarea (2-A, 2-B, … extraídas del PDF de la Guía)
```

## Reglas de contenido

1. **Guías de Trabajo**: abrir la Tarea, anotar instrucciones escritas que no estén en el
   PDF, descargar el PDF y extraer las subtareas reales (`2-A`, `2-B`, …) como acciones
   cortas y concretas. Si el PDF es escaneado, renderizar páginas y leerlas visualmente.
2. **Videos / Enlaces web**: abrir solo la ficha del ítem para detectar actividades extra.
   **No reproducir ni mirar el video.**
3. **Ítems extra** (`Instrucciones Bimestre 4`, `Medio Tiempo`, foros, clases en vivo,
   etc.): se listan como ítem propio con su checkbox.
4. Nunca inventar contenido. Si un PDF no se puede leer: `[pendiente de lectura]`.

## Producto final

- `2do-grado-bimestre-4.html` — checklist estático, autocontenido, sin CDN ni build
  (se publica en GitHub Pages / Cloudflare Pages).
- Tildes guardados en `localStorage` + exportar/importar progreso en JSON.
- Ítems de cuestionario listados sin enlace y con candado visual.
- Fuente de verdad en `datos/bimestre-4.json`.

## Notas técnicas

- Navegador: extensión `browse` sobre el Edge ya logueado en `https://jhs.schoology.com`.
- Extracción: `fetch` same-origin dentro de la página (más rápido y estable que clickear),
  `browse.eval` para parsear y devolver JSON.
- PDFs: descarga por `/attachment/<id>/source/<token>.pdf` y extracción de texto con
  PyMuPDF (`pymupdf`). Fallback: render de páginas a PNG + lectura visual.
