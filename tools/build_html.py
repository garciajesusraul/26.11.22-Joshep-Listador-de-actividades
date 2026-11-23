"""Genera el checklist HTML autocontenido a partir de datos/bimestre-4.json."""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "datos", "bimestre-4.json")
OUT = os.path.join(ROOT, "2do-grado-bimestre-4.html")

ICONOS = {
    "video": "🎬",
    "guia": "📘",
    "cartilla": "✂️",
    "audio": "🎧",
    "cancion": "🎵",
    "enlace": "🔗",
    "foro": "💬",
    "tarea": "📝",
    "cuestionario": "🔒",
    "tutor": "🔒",
    "nota": "•",
}

ETIQUETAS = {
    "video": "Video",
    "guia": "Guía",
    "cartilla": "Cartilla",
    "audio": "Audio",
    "cancion": "Canción",
    "enlace": "Material",
    "foro": "Foro",
    "tarea": "Tarea",
    "cuestionario": "Solo lo abre el niño",
    "tutor": "Solo lo abre el tutor",
    "nota": "Aviso",
}


def esc(t):
    return html.escape(str(t), quote=True)


def slug(s):
    out = []
    for ch in s.lower():
        if ch.isalnum():
            out.append(ch)
        else:
            out.append("-")
    return "".join(out).strip("-")


def render_sub(item_id, num, idx, texto):
    sid = f"{item_id}-s{idx}"
    letra = chr(ord("A") + idx)
    return f"""<li class="sub">
          <label class="sub-label" for="{sid}">
            <input type="checkbox" id="{sid}" data-check="{sid}">
            <span class="sub-tag">{num}-{letra}</span>
            <span class="sub-text">{esc(texto)}</span>
          </label>
        </li>"""


def render_item(materia_idx, tema_idx, item_idx, numero, item):
    tipo = item.get("tipo", "tarea")
    icono = ICONOS.get(tipo, "•")
    etiqueta = ETIQUETAS.get(tipo, tipo)
    bloqueado = item.get("bloqueado") or tipo in ("cuestionario", "tutor")
    item_id = f"m{materia_idx}t{tema_idx}i{item_idx}"
    subtareas = item.get("subtareas") or []
    nota = item.get("nota")
    nota_html = f'<p class="nota">{esc(nota)}</p>' if nota else ""

    if tipo == "nota":
        return f"""<li class="item item-nota" data-item-id="{item_id}" data-parent-id="">
          <div class="item-head">
            <span class="item-num">{numero}.</span>
            <span class="item-name">{esc(item['nombre'])}</span>
            <span class="badge badge-nota">Aviso</span>
          </div>
          {nota_html}
        </li>"""

    candado = '<span class="lock" title="Ítem que solo abren el niño y el tutor">🔒</span>' if bloqueado else ""
    if subtareas:
        hijos = "\n        ".join(render_sub(item_id, numero, i, s) for i, s in enumerate(subtareas))
        cuerpo = f"""<ul class="subs">
        {hijos}
      </ul>"""
        head = f"""<div class="item-head">
            <span class="item-num">{numero}.</span>
            <label class="item-label" for="{item_id}">
              <input type="checkbox" id="{item_id}" data-check="{item_id}" data-children="1">
              <span class="item-name">{esc(item['nombre'])}</span>
            </label>
            <span class="badge badge-{tipo}">{icono} {esc(etiqueta)}</span>
            {candado}
            <span class="item-progress" data-progress="{item_id}">0/{len(subtareas)}</span>
          </div>
          {nota_html}"""
    else:
        cuerpo = ""
        head = f"""<div class="item-head">
            <span class="item-num">{numero}.</span>
            <label class="item-label" for="{item_id}">
              <input type="checkbox" id="{item_id}" data-check="{item_id}">
              <span class="item-name">{esc(item['nombre'])}</span>
            </label>
            <span class="badge badge-{tipo}">{icono} {esc(etiqueta)}</span>
            {candado}
          </div>
          {nota_html}"""

    return f"""<li class="item" data-item-id="{item_id}" data-parent-id="">
      {head}
      {cuerpo}
    </li>"""


def render():
    data = json.load(open(DATA, encoding="utf-8"))
    secciones = []
    nav = []
    total_items = 0

    for mi, materia in enumerate(data["materias"]):
        mid = f"materia-{materia['id']}"
        nav.append(f'<a class="chip" href="#{mid}">{esc(materia["nombre"])}</a>')
        temas_html = []
        for ti, tema in enumerate(materia["temas"]):
            items_html = []
            numero = 0
            for ii, item in enumerate(tema["items"]):
                numero += 1
                total_items += 1
                items_html.append(render_item(mi, ti, ii, numero, item))
            extra = " tema-extra" if tema.get("extra") else ""
            temas_html.append(f"""<section class="tema{extra}" data-tema="m{mi}t{ti}">
      <header class="tema-head">
        <h3>{esc(tema['nombre'])}</h3>
        <span class="tema-progress" data-tema-progress="m{mi}t{ti}"></span>
      </header>
      <ul class="items">
        {chr(10).join(items_html)}
      </ul>
    </section>""")

        secciones.append(f"""<section class="materia" id="{mid}" data-materia="m{mi}">
    <header class="materia-head">
      <h2>{esc(materia['nombre'])} <small>{esc(materia.get('subtitulo', ''))}</small></h2>
      <div class="materia-meta">
        <span class="materia-progress" data-materia-progress="m{mi}">0%</span>
        <a class="btn-mini" href="{esc(materia['curso'])}" target="_blank" rel="noopener">Abrir en Schoology</a>
      </div>
    </header>
    {chr(10).join(temas_html)}
  </section>""")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(data['titulo'])} — {esc(data['colegio'])}</title>
<style>
  :root {{
    --bg: #f6f4ef;
    --card: #ffffff;
    --ink: #23262b;
    --muted: #6b7280;
    --line: #e5e1d8;
    --brand: #1f6f5c;
    --brand-soft: #e6f2ee;
    --accent: #c9752b;
    --done: #97a3a0;
    --shadow: 0 1px 2px rgba(0,0,0,.06), 0 8px 24px rgba(0,0,0,.05);
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg); color: var(--ink); line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 1000px; margin: 0 auto; padding: 0 16px 64px; }}

  header.top {{
    background: linear-gradient(160deg, #1f6f5c 0%, #2b8a72 60%, #3ba07f 100%);
    color: #fff; padding: 28px 0 22px; margin-bottom: 18px;
  }}
  header.top .wrap {{ padding-bottom: 0; }}
  header.top h1 {{ margin: 0 0 4px; font-size: clamp(22px, 3.4vw, 34px); letter-spacing: .2px; }}
  header.top p {{ margin: 0; opacity: .9; font-size: 14px; }}

  .toolbar {{
    position: sticky; top: 0; z-index: 20;
    background: rgba(246,244,239,.94); backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--line); padding: 10px 0; margin-bottom: 18px;
  }}
  .toolbar .wrap {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; padding-bottom: 0; }}
  .progress-shell {{ flex: 1 1 220px; min-width: 180px; }}
  .progress-bar {{ height: 10px; background: #e2ded4; border-radius: 99px; overflow: hidden; }}
  .progress-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, #2b8a72, #7cc4a9); transition: width .25s; }}
  .progress-text {{ font-size: 12.5px; color: var(--muted); margin-top: 4px; }}
  .progress-text b {{ color: var(--brand); }}

  .btn {{
    appearance: none; border: 1px solid var(--line); background: #fff; color: var(--ink);
    padding: 8px 13px; border-radius: 9px; font-size: 13.5px; cursor: pointer; font-weight: 600;
    transition: .15s; white-space: nowrap;
  }}
  .btn:hover {{ border-color: var(--brand); color: var(--brand); }}
  .btn.on {{ background: var(--brand); border-color: var(--brand); color: #fff; }}
  .btn-ghost {{ background: transparent; }}
  .btn-mini {{ font-size: 12px; color: var(--brand); text-decoration: none; border: 1px solid #cfe3dc; padding: 4px 9px; border-radius: 8px; }}
  .btn-mini:hover {{ background: var(--brand-soft); }}
  input[type="search"] {{
    padding: 8px 12px; border-radius: 9px; border: 1px solid var(--line); font-size: 13.5px;
    min-width: 170px; background: #fff;
  }}

  nav.chips {{ display: flex; gap: 8px; overflow-x: auto; padding: 4px 0 10px; }}
  .chip {{
    flex: 0 0 auto; text-decoration: none; color: var(--brand); background: var(--brand-soft);
    border: 1px solid #cfe3dc; padding: 6px 12px; border-radius: 99px; font-size: 13px; font-weight: 600;
  }}
  .chip:hover {{ background: #d5ebe3; }}

  .materia {{ margin-bottom: 26px; scroll-margin-top: 96px; }}
  .materia-head {{
    display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap;
    border-bottom: 3px solid var(--brand); padding-bottom: 6px; margin-bottom: 12px;
  }}
  .materia-head h2 {{ margin: 0; font-size: clamp(18px, 2.4vw, 23px); color: var(--brand); }}
  .materia-head h2 small {{ font-weight: 500; color: var(--muted); font-size: 13px; }}
  .materia-meta {{ display: flex; align-items: center; gap: 10px; }}
  .materia-progress {{ font-size: 12.5px; font-weight: 700; color: var(--brand); }}

  .tema {{
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    padding: 14px 16px 8px; margin-bottom: 12px; box-shadow: var(--shadow);
  }}
  .tema-extra {{ border-left: 4px solid var(--accent); }}
  .tema-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 10px; }}
  .tema-head h3 {{ margin: 0 0 8px; font-size: 15.5px; }}
  .tema-progress {{ font-size: 12px; color: var(--muted); white-space: nowrap; }}

  ul.items, ul.subs {{ list-style: none; margin: 0; padding: 0; }}
  li.item {{ padding: 7px 0; border-top: 1px dashed #eeebe3; }}
  li.item:first-child {{ border-top: 0; }}
  .item-head {{ display: flex; align-items: flex-start; gap: 8px; }}
  .item-num {{ font-size: 13px; color: var(--muted); font-variant-numeric: tabular-nums; padding-top: 2px; min-width: 20px; }}
  .item-label {{ display: flex; align-items: flex-start; gap: 9px; cursor: pointer; flex: 1 1 auto; }}
  .item-label input {{ margin: 4px 0 0; width: 17px; height: 17px; accent-color: var(--brand); cursor: pointer; }}
  .item-name {{ font-size: 14.5px; font-weight: 600; }}
  .badge {{
    flex: 0 0 auto; font-size: 11px; font-weight: 700; letter-spacing: .2px; text-transform: uppercase;
    padding: 2px 7px; border-radius: 6px; background: #f0eee8; color: var(--muted); white-space: nowrap;
  }}
  .badge-video {{ background: #eef2fb; color: #3a5ba0; }}
  .badge-guia {{ background: #e9f5ef; color: #1f6f5c; }}
  .badge-foro {{ background: #fdf1e3; color: #a9611f; }}
  .badge-cuestionario, .badge-tutor {{ background: #f3e9ee; color: #8c4a63; }}
  .badge-audio, .badge-cancion {{ background: #f2ecfa; color: #6a4a9e; }}
  .badge-cartilla {{ background: #eef7f9; color: #2c7a8c; }}
  .lock {{ font-size: 12px; }}

  .item-progress {{ font-size: 11.5px; color: var(--muted); padding-top: 3px; font-variant-numeric: tabular-nums; }}
  .nota {{ margin: 4px 0 2px 29px; font-size: 12.5px; color: var(--muted); font-style: italic; }}

  ul.subs {{ margin: 4px 0 6px 29px; border-left: 2px solid var(--brand-soft); padding-left: 12px; }}
  li.sub {{ padding: 3px 0; }}
  .sub-label {{ display: flex; align-items: flex-start; gap: 8px; cursor: pointer; }}
  .sub-label input {{ margin: 3px 0 0; width: 15px; height: 15px; accent-color: var(--brand); cursor: pointer; }}
  .sub-tag {{ font-size: 11.5px; font-weight: 700; color: var(--brand); background: var(--brand-soft); padding: 1px 6px; border-radius: 5px; white-space: nowrap; }}
  .sub-text {{ font-size: 13.5px; color: #3b4048; }}

  input[type="checkbox"]:checked + .item-name,
  input[type="checkbox"]:checked ~ .sub-text {{ text-decoration: line-through; color: var(--done); }}
  li.is-done .item-name {{ color: var(--done); }}

  .hide-done li.is-done, .hide-done li.item.is-done {{ display: none; }}
  .hide-done section.tema.all-done, .hide-done section.materia.all-done {{ display: none; }}
  .hidden {{ display: none !important; }}

  .empty {{ text-align: center; color: var(--muted); padding: 40px 10px; }}

  footer {{ text-align: center; color: var(--muted); font-size: 12px; padding: 26px 10px 0; }}
  footer code {{ background: #efede6; padding: 1px 5px; border-radius: 4px; }}

  @media (max-width: 640px) {{
    .badge {{ display: none; }}
    .item-name {{ font-size: 14px; }}
    .sub-text {{ font-size: 13px; }}
    header.top {{ padding: 20px 0 16px; }}
  }}
  @media print {{
    .toolbar, nav.chips, .btn, .btn-mini {{ display: none !important; }}
    body {{ background: #fff; }}
    .tema {{ box-shadow: none; break-inside: avoid; }}
    .hide-done li.is-done {{ display: list-item; }}
  }}
</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <h1>✅ {esc(data['titulo'])}</h1>
    <p>{esc(data['colegio'])} · {total_items} ítems · tildá lo que ya está hecho</p>
  </div>
</header>

<div class="toolbar">
  <div class="wrap">
    <div class="progress-shell">
      <div class="progress-bar"><div class="progress-fill" id="globalFill"></div></div>
      <div class="progress-text"><b id="globalPct">0%</b> completado · <span id="globalCount">0 de 0</span></div>
    </div>
    <input type="search" id="buscar" placeholder="Buscar actividad…" aria-label="Buscar actividad">
    <button class="btn" id="btnPendientes" aria-pressed="false">Ocultar tildados</button>
    <button class="btn btn-ghost" id="btnExportar">Exportar</button>
    <button class="btn btn-ghost" id="btnImportar">Importar</button>
    <input type="file" id="fileImport" accept="application/json" class="hidden">
    <button class="btn btn-ghost" id="btnReset" title="Borra todo el progreso guardado">Reiniciar</button>
  </div>
</div>

<div class="wrap">
  <nav class="chips">
    {chr(10).join(nav)}
  </nav>

  {chr(10).join(secciones)}

  <div class="empty hidden" id="sinResultados">No hay actividades pendientes con ese filtro. ¡Felicitaciones! 🎉</div>

  <footer>
    Progreso guardado en este navegador (localStorage). Usá <strong>Exportar</strong> para guardar un respaldo en <code>.json</code>.
  </footer>
</div>

<script>
(function () {{
  "use strict";
  var KEY = "jhs-2do-b4-v1";
  var checks = {{}};
  var filterPending = false;

  try {{
    var raw = localStorage.getItem(KEY);
    if (raw) checks = JSON.parse(raw) || {{}};
  }} catch (e) {{ checks = {{}}; }}

  function save() {{
    try {{ localStorage.setItem(KEY, JSON.stringify(checks)); }} catch (e) {{}}
  }}

  function allInputs() {{
    return Array.prototype.slice.call(document.querySelectorAll('input[data-check]'));
  }}

  function subsOf(id) {{
    return Array.prototype.slice.call(document.querySelectorAll('input[data-check^="' + id + '-s"]'));
  }}

  function setSub(id, val) {{
    if (val) checks[id] = true; else delete checks[id];
  }}

  function refreshItem(li) {{
    var id = li.getAttribute("data-item-id");
    var parent = li.querySelector('input[data-children]');
    var subs = subsOf(id);
    if (subs.length) {{
      var done = subs.filter(function (s) {{ return s.checked; }}).length;
      if (parent) parent.checked = done === subs.length;
      var prog = li.querySelector('[data-progress]');
      if (prog) prog.textContent = done + "/" + subs.length;
    }}
    var own = li.querySelector('input[data-check]');
    var isDone = subs.length ? subs.every(function (s) {{ return s.checked; }})
                             : !!(own && own.checked);
    li.classList.toggle("is-done", isDone);
  }}

  function refreshAll() {{
    allInputs().forEach(function (i) {{
      if (!i.hasAttribute("data-children")) i.checked = !!checks[i.id];
    }});
    Array.prototype.forEach.call(document.querySelectorAll("li.item[data-item-id]"), refreshItem);
    updateProgress();
  }}

  function updateProgress() {{
    var leaves = allInputs().filter(function (i) {{ return !i.hasAttribute("data-children"); }});
    var total = leaves.filter(function (i) {{ return i.id.indexOf("-s") === -1 || !isNota(i); }}).length;
    var done = leaves.filter(function (i) {{ return i.checked; }}).length;
    var pct = total ? Math.round(done * 100 / total) : 0;
    document.getElementById("globalFill").style.width = pct + "%";
    document.getElementById("globalPct").textContent = pct + "%";
    document.getElementById("globalCount").textContent = done + " de " + total;

    Array.prototype.forEach.call(document.querySelectorAll("section[data-materia]"), function (sec) {{
      var ls = leaves.filter(function (i) {{ return sec.contains(i); }});
      var d = ls.filter(function (i) {{ return i.checked; }}).length;
      var p = ls.length ? Math.round(d * 100 / ls.length) : 0;
      var tag = sec.querySelector("[data-materia-progress]");
      if (tag) tag.textContent = p + "%";
      sec.classList.toggle("all-done", ls.length > 0 && d === ls.length);
    }});

    Array.prototype.forEach.call(document.querySelectorAll("section[data-tema]"), function (sec) {{
      var ls = leaves.filter(function (i) {{ return sec.contains(i); }});
      var d = ls.filter(function (i) {{ return i.checked; }}).length;
      var tag = sec.querySelector("[data-tema-progress]");
      if (tag) tag.textContent = d + "/" + ls.length;
      sec.classList.toggle("all-done", ls.length > 0 && d === ls.length);
    }});
  }}

  function isNota(i) {{
    var li = i.closest("li.item");
    return li && li.classList.contains("item-nota");
  }}

  document.addEventListener("change", function (ev) {{
    var el = ev.target;
    if (!el.matches || !el.matches("input[data-check]")) return;
    if (el.hasAttribute("data-children")) {{
      var id = el.id;
      subsOf(id).forEach(function (s) {{
        s.checked = el.checked;
        setSub(s.id, el.checked);
      }});
    }} else {{
      setSub(el.id, el.checked);
    }}
    save();
    refreshAll();
    applyFilters();
  }});

  function applyFilters() {{
    var q = document.getElementById("buscar").value.trim().toLowerCase();
    document.body.classList.toggle("hide-done", filterPending);

    Array.prototype.forEach.call(document.querySelectorAll("li.item[data-item-id]"), function (li) {{
      var text = li.textContent.toLowerCase();
      var match = !q || text.indexOf(q) !== -1;
      li.classList.toggle("hidden", !match);
      if (match && filterPending && li.classList.contains("is-done")) li.classList.add("hidden");
    }});

    Array.prototype.forEach.call(document.querySelectorAll("section[data-tema]"), function (sec) {{
      var visibles = Array.prototype.filter.call(sec.querySelectorAll("li.item[data-item-id]"), function (li) {{
        return !li.classList.contains("hidden");
      }});
      sec.classList.toggle("hidden", visibles.length === 0);
    }});

    var shown = 0;
    Array.prototype.forEach.call(document.querySelectorAll("section[data-materia]"), function (sec) {{
      var visibles = Array.prototype.filter.call(sec.querySelectorAll("li.item[data-item-id]"), function (li) {{
        return !li.classList.contains("hidden");
      }});
      sec.classList.toggle("hidden", visibles.length === 0);
      shown += visibles.length;
    }});
    document.getElementById("sinResultados").classList.toggle("hidden", shown !== 0);
  }}

  document.getElementById("buscar").addEventListener("input", applyFilters);

  document.getElementById("btnPendientes").addEventListener("click", function () {{
    filterPending = !filterPending;
    this.classList.toggle("on", filterPending);
    this.setAttribute("aria-pressed", filterPending ? "true" : "false");
    this.textContent = filterPending ? "Mostrar todos" : "Ocultar tildados";
    applyFilters();
  }});

  document.getElementById("btnExportar").addEventListener("click", function () {{
    var payload = {{
      app: "listador-actividades",
      grado: "2do grado",
      bimestre: "Bimestre 4",
      exportado: new Date().toISOString(),
      tildes: checks
    }};
    var blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: "application/json" }});
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "progreso-2do-bimestre-4.json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  }});

  document.getElementById("btnImportar").addEventListener("click", function () {{
    document.getElementById("fileImport").click();
  }});

  document.getElementById("fileImport").addEventListener("change", function (ev) {{
    var file = ev.target.files && ev.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () {{
      try {{
        var obj = JSON.parse(reader.result);
        var next = obj.tildes || obj.checks || obj;
        if (!next || typeof next !== "object") throw new Error("formato");
        checks = next;
        save();
        refreshAll();
        applyFilters();
        alert("Progreso importado correctamente.");
      }} catch (e) {{
        alert("No se pudo leer el archivo. Verificá que sea el JSON exportado desde esta página.");
      }}
    }};
    reader.readAsText(file);
    ev.target.value = "";
  }});

  document.getElementById("btnReset").addEventListener("click", function () {{
    if (!confirm("¿Borrar todas las tildes guardadas en este navegador?")) return;
    checks = {{}};
    save();
    refreshAll();
    applyFilters();
  }});

  refreshAll();
  applyFilters();
}})();
</script>
</body>
</html>
"""


def main():
    html_out = render()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html_out)
    print(f"OK  {OUT}  {len(html_out)} bytes")


if __name__ == "__main__":
    main()
