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

EMOJIS = {
    "ciencias": "🔬",
    "english": "🇬🇧",
    "historia": "📜",
    "lenguaje": "📖",
    "luces": "🎨",
    "matematicas": "🔢",
    "sonidos": "🎤",
}


def esc(t):
    return html.escape(str(t), quote=True)


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
        return f"""<li class="item item-nota" data-item-id="{item_id}">
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

    return f"""<li class="item" data-item-id="{item_id}">
      {head}
      {cuerpo}
    </li>"""


def render():
    data = json.load(open(DATA, encoding="utf-8"))
    tabs = ['<button class="tab active" role="tab" aria-selected="true" data-tab="panel-resumen" id="tab-resumen">📊 Estadísticas<span class="tab-pct" data-tab-pct-global>0%</span></button>']
    paneles = []
    total_items = 0

    for mi, materia in enumerate(data["materias"]):
        mid = f"materia-{materia['id']}"
        emoji = EMOJIS.get(materia["id"], "📁")
        tabs.append(
            f'<button class="tab" role="tab" aria-selected="false" data-tab="panel-m{mi}" id="tab-m{mi}">'
            f'<span class="tab-name">{emoji} {esc(materia["nombre"])}</span>'
            f'<span class="tab-pct" data-tab-pct="m{mi}">0%</span></button>'
        )

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

        paneles.append(f"""<div class="panel" id="panel-m{mi}" role="tabpanel" aria-labelledby="tab-m{mi}" data-materia-panel="m{mi}">
  <section class="materia" id="{mid}">
    <header class="materia-head">
      <h2 data-nombre="{esc(materia['nombre'])}">{emoji} {esc(materia['nombre'])} <small>{esc(materia.get('subtitulo', ''))}</small></h2>
      <div class="materia-meta">
        <span class="chip chip-done" data-materia-progress="m{mi}">✅ 0% hecho</span>
        <span class="chip chip-pend" data-materia-pending="m{mi}">⏳ 0% falta</span>
        <a class="btn-mini" href="{esc(materia['curso'])}" target="_blank" rel="noopener">Abrir en Schoology</a>
      </div>
    </header>
    <div class="materia-bar"><div class="materia-fill" data-materia-fill="m{mi}"></div></div>
    {chr(10).join(temas_html)}
    <p class="panel-empty hidden">¡No queda nada pendiente en esta materia! 🎉</p>
  </section>
</div>""")

    panel_resumen = f"""<div class="panel active" id="panel-resumen" role="tabpanel" aria-labelledby="tab-resumen">
  <section class="resumen">
    <h2>📊 Estadísticas del bimestre</h2>
    <div class="stats-grid">
      <div class="stat-card done">
        <div class="stat-num" id="stHechas">0</div>
        <div class="stat-lbl">Hechas</div>
      </div>
      <div class="stat-card pending">
        <div class="stat-num" id="stPendientes">0</div>
        <div class="stat-lbl">Pendientes</div>
      </div>
      <div class="stat-card pct">
        <div class="stat-num" id="stPct">0%</div>
        <div class="stat-lbl">Avance</div>
      </div>
    </div>

    <div class="stats-block">
      <div class="progress-bar big"><div class="progress-fill" id="statsFill"></div></div>
      <p class="stats-caption" id="stCaption">0 de 0 actividades completadas</p>
    </div>

    <h3 class="stats-title">Por materia</h3>
    <div class="table-wrap">
      <table class="stats-table">
        <thead>
          <tr><th>Materia</th><th>Hechas</th><th>Faltan</th><th>Progreso</th><th>%</th></tr>
        </thead>
        <tbody id="statsBody"></tbody>
      </table>
    </div>
    <p class="hint">Tocá una materia de la tabla para abrir su pestaña.</p>

    <h3 class="stats-title">Detalle por tema</h3>
    <div id="statsTemas" class="temas-stats"></div>
  </section>
</div>"""

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
    color: #fff; padding: 22px 0 18px;
  }}
  header.top .wrap {{ padding-bottom: 0; }}
  header.top h1 {{ margin: 0 0 3px; font-size: clamp(20px, 3vw, 30px); letter-spacing: .2px; }}
  header.top p {{ margin: 0; opacity: .9; font-size: 13.5px; }}

  .toolbar {{
    position: sticky; top: 0; z-index: 30;
    background: rgba(246,244,239,.96); backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--line); padding: 9px 0;
  }}
  .toolbar .wrap {{ display: flex; gap: 9px; flex-wrap: wrap; align-items: center; padding-bottom: 0; }}
  .progress-shell {{ flex: 1 1 200px; min-width: 160px; }}
  .progress-bar {{ height: 9px; background: #e2ded4; border-radius: 99px; overflow: hidden; }}
  .progress-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, #2b8a72, #7cc4a9); transition: width .25s; }}
  .progress-text {{ font-size: 12.5px; color: var(--muted); margin-top: 3px; }}
  .progress-text b {{ color: var(--brand); }}

  .btn {{
    appearance: none; border: 1px solid var(--line); background: #fff; color: var(--ink);
    padding: 7px 12px; border-radius: 9px; font-size: 13px; cursor: pointer; font-weight: 600;
    transition: .15s; white-space: nowrap;
  }}
  .btn:hover {{ border-color: var(--brand); color: var(--brand); }}
  .btn.on {{ background: var(--brand); border-color: var(--brand); color: #fff; }}
  .btn-ghost {{ background: transparent; }}
  .btn-mini {{ font-size: 12px; color: var(--brand); text-decoration: none; border: 1px solid #cfe3dc; padding: 4px 9px; border-radius: 8px; }}
  .btn-mini:hover {{ background: var(--brand-soft); }}
  input[type="search"] {{
    padding: 7px 12px; border-radius: 9px; border: 1px solid var(--line); font-size: 13px;
    min-width: 150px; background: #fff;
  }}

  /* --- Pestañas --- */
  nav.tabs {{
    display: flex; gap: 6px; overflow-x: auto; padding: 12px 0 0; margin-bottom: 14px;
    scrollbar-width: thin;
  }}
  .tab {{
    flex: 0 0 auto; cursor: pointer; border: 1px solid var(--line); background: #fff;
    color: #4b5563; font: inherit; font-size: 13.5px; font-weight: 600;
    padding: 9px 14px; border-radius: 11px 11px 0 0; border-bottom: 3px solid transparent;
    transition: .15s; white-space: nowrap;
  }}
  .tab:hover {{ color: var(--brand); border-color: #cfe3dc; }}
  .tab.active {{
    background: var(--brand); color: #fff; border-color: var(--brand);
    border-bottom-color: #f0b46a;
  }}
  .tab .mini {{ font-size: 11px; opacity: .8; margin-left: 5px; }}
  .tab-name {{ display: inline; }}
  .tab-pct {{
    display: inline-block; margin-left: 7px; font-size: 10.5px; font-weight: 800;
    background: #eef1f0; color: #55605f; border-radius: 20px; padding: 0 7px;
    font-variant-numeric: tabular-nums; letter-spacing: 0;
  }}
  .tab.active .tab-pct {{ background: rgba(255,255,255,.22); color: #fff; }}

  .panel {{ display: none; }}
  .panel.active {{ display: block; }}
  body.searching .panel {{ display: block; }}
  body.searching #panel-resumen {{ display: none; }}
  body.searching nav.tabs {{ display: none; }}

  /* --- Materia / tema --- */
  .materia {{ margin-bottom: 4px; }}
  .materia-head {{
    display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap;
    border-bottom: 3px solid var(--brand); padding-bottom: 6px; margin-bottom: 12px;
  }}
  .materia-head h2 {{ margin: 0; font-size: clamp(17px, 2.3vw, 22px); color: var(--brand); }}
  .materia-head h2 small {{ font-weight: 500; color: var(--muted); font-size: 13px; }}
  .materia-meta {{ display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }}
  .materia-progress {{ font-size: 12.5px; font-weight: 700; color: var(--brand); }}
  .chip {{
    font-size: 11.5px; font-weight: 700; padding: 3px 9px; border-radius: 99px;
    white-space: nowrap; font-variant-numeric: tabular-nums;
  }}
  .chip-done {{ background: var(--brand-soft); color: #17614f; }}
  .chip-pend {{ background: #fdf1e3; color: #a9611f; }}
  .materia-bar {{ height: 8px; background: #e2ded4; border-radius: 99px; overflow: hidden; margin: 0 0 14px; }}
  .materia-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, #2b8a72, #7cc4a9); transition: width .25s; }}

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

  .hide-done li.item.is-done {{ display: none; }}
  .hidden {{ display: none !important; }}

  /* --- Resumen --- */
  .resumen h2 {{ margin: 4px 0 14px; font-size: clamp(18px, 2.4vw, 23px); color: var(--brand); }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }}
  .stat-card {{
    background: #fff; border: 1px solid var(--line); border-radius: 14px;
    padding: 14px 10px; text-align: center; box-shadow: var(--shadow);
  }}
  .stat-num {{ font-size: clamp(24px, 5vw, 34px); font-weight: 800; line-height: 1.1; font-variant-numeric: tabular-nums; }}
  .stat-lbl {{ font-size: 12px; text-transform: uppercase; letter-spacing: .5px; color: var(--muted); font-weight: 700; }}
  .stat-card.done .stat-num {{ color: var(--brand); }}
  .stat-card.pending .stat-num {{ color: var(--accent); }}
  .stat-card.pct .stat-num {{ color: #2e5d8a; }}

  .stats-block {{ background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px; box-shadow: var(--shadow); }}
  .progress-bar.big {{ height: 16px; }}
  .stats-caption {{ margin: 8px 0 0; font-size: 12.5px; color: var(--muted); }}
  .stats-title {{ margin: 22px 0 8px; font-size: 14px; text-transform: uppercase; letter-spacing: .6px; color: var(--muted); }}

  .table-wrap {{ overflow-x: auto; background: #fff; border: 1px solid var(--line); border-radius: 14px; box-shadow: var(--shadow); }}
  table.stats-table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
  table.stats-table th {{ text-align: left; font-size: 11.5px; text-transform: uppercase; letter-spacing: .4px; color: var(--muted); padding: 9px 12px; border-bottom: 1px solid var(--line); }}
  table.stats-table th:nth-child(n+2), table.stats-table td:nth-child(n+2) {{ text-align: center; }}
  table.stats-table td {{ padding: 9px 12px; border-bottom: 1px solid #f1eee7; vertical-align: middle; }}
  table.stats-table tr:last-child td {{ border-bottom: 0; }}
  table.stats-table tr.row-link {{ cursor: pointer; }}
  table.stats-table tr.row-link:hover td {{ background: #f7fbf9; }}
  .cell-name {{ font-weight: 600; white-space: nowrap; }}
  .cell-num {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .cell-bar {{ min-width: 110px; }}
  .mini-bar {{ height: 7px; background: #ece8df; border-radius: 99px; overflow: hidden; }}
  .mini-fill {{ height: 100%; background: var(--brand); }}
  .pct-tag {{ font-weight: 700; color: var(--brand); font-variant-numeric: tabular-nums; }}

  .temas-stats {{ display: grid; gap: 7px; }}
  .tema-group {{
    margin: 12px 0 2px; font-size: 11.5px; font-weight: 800; letter-spacing: .5px;
    text-transform: uppercase; color: var(--brand);
  }}
  .tema-group:first-child {{ margin-top: 0; }}
  .tema-stat {{
    display: flex; justify-content: space-between; gap: 10px; align-items: center;
    background: #fff; border: 1px solid var(--line); border-radius: 10px; padding: 8px 12px; font-size: 13px;
  }}
  .tema-stat .t-name {{ font-weight: 600; }}
  .tema-stat .t-nums {{ font-size: 12px; color: var(--muted); white-space: nowrap; }}
  .tema-stat.full {{ opacity: .55; }}
  .hint {{ font-size: 12px; color: var(--muted); margin: 8px 0 0; }}

  .panel-empty {{ text-align: center; background: #fff; border: 1px dashed #cfe3dc; color: var(--brand); border-radius: 12px; padding: 22px; font-weight: 600; }}

  footer {{ text-align: center; color: var(--muted); font-size: 12px; padding: 26px 10px 0; }}
  footer code {{ background: #efede6; padding: 1px 5px; border-radius: 4px; }}

  @media (max-width: 640px) {{
    .badge {{ display: none; }}
    .item-name {{ font-size: 14px; }}
    .sub-text {{ font-size: 13px; }}
    header.top {{ padding: 16px 0 14px; }}
    .tab {{ font-size: 12.5px; padding: 8px 11px; }}
    .stats-grid {{ gap: 7px; }}
    .cell-bar {{ display: none; }}
  }}
  @media print {{
    .toolbar, nav.tabs, .btn, .btn-mini {{ display: none !important; }}
    body {{ background: #fff; }}
    .panel {{ display: block !important; }}
    #panel-resumen {{ page-break-after: always; }}
    .tema {{ box-shadow: none; break-inside: avoid; }}
    .hide-done li.item.is-done {{ display: list-item; }}
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
  <nav class="tabs" role="tablist" aria-label="Materias y estadísticas">
    {chr(10).join(tabs)}
  </nav>

  {panel_resumen}

  {chr(10).join(paneles)}

  <div class="empty hidden" id="sinResultados">No hay actividades que coincidan con la búsqueda.</div>

  <footer>
    Progreso guardado en este navegador (localStorage). Usá <strong>Exportar</strong> para guardar un respaldo en <code>.json</code>.
  </footer>
</div>

<script>
(function () {{
  "use strict";
  var KEY = "jhs-2do-b4-v1";
  var TAB_KEY = "jhs-2do-b4-tab";
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
  function leaves() {{
    return allInputs().filter(function (i) {{ return !i.hasAttribute('data-children'); }});
  }}
  function subsOf(id) {{
    return Array.prototype.slice.call(document.querySelectorAll('input[data-check^="' + id + '-s"]'));
  }}
  function setSub(id, val) {{
    if (val) checks[id] = true; else delete checks[id];
  }}

  /* ---------- pestañas ---------- */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[data-tab]'));
  function activateTab(panelId, remember) {{
    var activeBtn = null;
    tabs.forEach(function (t) {{
      var on = t.getAttribute('data-tab') === panelId;
      if (on) activeBtn = t;
      t.classList.toggle('active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    }});
    Array.prototype.forEach.call(document.querySelectorAll('.panel'), function (p) {{
      p.classList.toggle('active', p.id === panelId);
    }});
    if (activeBtn && activeBtn.parentNode) {{
      var nav = activeBtn.parentNode;
      var navRect = nav.getBoundingClientRect();
      var btnRect = activeBtn.getBoundingClientRect();
      if (btnRect.left < navRect.left || btnRect.right > navRect.right) {{
        nav.scrollLeft += (btnRect.left - navRect.left) - 12;
        if (nav.scrollLeft < 0) nav.scrollLeft = 0;
      }}
    }}
    if (remember !== false) {{
      try {{ localStorage.setItem(TAB_KEY, panelId); }} catch (e) {{}}
    }}
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }}
  tabs.forEach(function (t) {{
    t.addEventListener('click', function () {{
      document.getElementById('buscar').value = '';
      document.body.classList.remove('searching');
      activateTab(t.getAttribute('data-tab'));
      applyFilters();
    }});
  }});

  /* ---------- estado de ítems ---------- */
  function refreshItem(li) {{
    var id = li.getAttribute('data-item-id');
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
    li.classList.toggle('is-done', isDone);
  }}

  function refreshAll() {{
    allInputs().forEach(function (i) {{
      if (!i.hasAttribute('data-children')) i.checked = !!checks[i.id];
    }});
    Array.prototype.forEach.call(document.querySelectorAll('li.item[data-item-id]'), refreshItem);
    updateProgress();
  }}

  function updateProgress() {{
    var ls = leaves();
    var total = ls.length;
    var done = ls.filter(function (i) {{ return i.checked; }}).length;
    var raw = total ? done * 100 / total : 0;
    var pct = Math.round(raw);
    var pctLabel = (raw > 0 && raw < 1) ? raw.toFixed(1) : String(pct);

    document.getElementById('globalFill').style.width = pct + "%";
    document.getElementById('globalPct').textContent = pctLabel + "%";
    document.getElementById('globalCount').textContent = done + " de " + total;

    var tabGlobal = document.querySelector('[data-tab-pct-global]');
    if (tabGlobal) tabGlobal.textContent = pctLabel + "%";

    document.getElementById('stHechas').textContent = done;
    document.getElementById('stPendientes').textContent = total - done;
    document.getElementById('stPct').textContent = pctLabel + "%";
    document.getElementById('statsFill').style.width = pct + "%";
    document.getElementById('stCaption').textContent = done + " de " + total + " actividades completadas";

    var body = document.getElementById('statsBody');
    body.innerHTML = "";
    var temasBox = document.getElementById('statsTemas');
    temasBox.innerHTML = "";

    Array.prototype.forEach.call(document.querySelectorAll('[data-materia-panel]'), function (panel) {{
      var mi = panel.getAttribute('data-materia-panel');
      var pleaves = ls.filter(function (i) {{ return panel.contains(i); }});
      var pdone = pleaves.filter(function (i) {{ return i.checked; }}).length;
      var ppct = pleaves.length ? Math.round(pdone * 100 / pleaves.length) : 0;
      var praw = pleaves.length ? pdone * 100 / pleaves.length : 0;
      var ppctLabel = (praw > 0 && praw < 1) ? praw.toFixed(1) : String(ppct);
      var name = panel.querySelector('.materia-head h2').getAttribute('data-nombre');
      var emoji = (panel.querySelector('.materia-head h2').textContent || '').trim().split(' ')[0];

      var tag = panel.querySelector('[data-materia-progress]');
      if (tag) tag.textContent = '✅ ' + ppctLabel + '% hecho';

      var pendNum = Math.round((100 - parseFloat(ppctLabel)) * 10) / 10;
      var pendTag = panel.querySelector('[data-materia-pending]');
      if (pendTag) pendTag.textContent = '⏳ ' + pendNum + '% falta';

      var mfill = panel.querySelector('[data-materia-fill]');
      if (mfill) mfill.style.width = ppct + '%';

      var tabPct = document.querySelector('[data-tab-pct="' + mi + '"]');
      if (tabPct) {{
        tabPct.textContent = ppctLabel + '%';
        tabPct.title = ppctLabel + '% hecho · ' + pendNum + '% falta';
      }}

      var tr = document.createElement('tr');
      tr.className = 'row-link';
      tr.innerHTML = '<td class="cell-name">' + name + '</td>' +
        '<td class="cell-num">' + pdone + '</td>' +
        '<td class="cell-num">' + (pleaves.length - pdone) + '</td>' +
        '<td class="cell-bar"><div class="mini-bar"><div class="mini-fill" style="width:' + ppct + '%"></div></div></td>' +
        '<td class="cell-num pct-tag">' + ppctLabel + '%</td>';
      tr.addEventListener('click', function () {{
        document.getElementById('buscar').value = '';
        document.body.classList.remove('searching');
        activateTab('panel-' + mi);
        applyFilters();
      }});
      body.appendChild(tr);

      var grupo = document.createElement('div');
      grupo.className = 'tema-group';
      grupo.textContent = emoji + ' ' + name;
      temasBox.appendChild(grupo);

      Array.prototype.forEach.call(panel.querySelectorAll('[data-tema]'), function (tema) {{
        var tleaves = ls.filter(function (i) {{ return tema.contains(i); }});
        var tdone = tleaves.filter(function (i) {{ return i.checked; }}).length;
        var ttag = tema.querySelector('[data-tema-progress]');
        if (ttag) ttag.textContent = tdone + "/" + tleaves.length;
        tema.classList.toggle('all-done', tleaves.length > 0 && tdone === tleaves.length);

        var row = document.createElement('div');
        row.className = 'tema-stat' + (tleaves.length > 0 && tdone === tleaves.length ? ' full' : '');
        var tpct = tleaves.length ? Math.round(tdone * 100 / tleaves.length) : 0;
        row.innerHTML = '<span class="t-name">' + tema.querySelector('h3').textContent + '</span>' +
          '<span class="t-nums">' + tdone + '/' + tleaves.length + ' · ' + tpct + '%' +
          (tleaves.length > 0 && tdone === tleaves.length ? ' ✔' : '') + '</span>';
        temasBox.appendChild(row);
      }});
    }});
  }}

  document.addEventListener('change', function (ev) {{
    var el = ev.target;
    if (!el.matches || !el.matches('input[data-check]')) return;
    if (el.hasAttribute('data-children')) {{
      subsOf(el.id).forEach(function (s) {{
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

  /* ---------- filtros ---------- */
  function applyFilters() {{
    var q = document.getElementById('buscar').value.trim().toLowerCase();
    var searching = q.length > 0;
    document.body.classList.toggle('searching', searching);
    document.body.classList.toggle('hide-done', filterPending);

    Array.prototype.forEach.call(document.querySelectorAll('li.item[data-item-id]'), function (li) {{
      var text = li.textContent.toLowerCase();
      var match = !q || text.indexOf(q) !== -1;
      var done = li.classList.contains('is-done');
      li.classList.toggle('hidden', !match || (filterPending && done));
    }});

    Array.prototype.forEach.call(document.querySelectorAll('[data-tema]'), function (tema) {{
      var vis = tema.querySelectorAll('li.item[data-item-id]:not(.hidden)');
      tema.classList.toggle('hidden', vis.length === 0);
    }});

    var shown = 0;
    Array.prototype.forEach.call(document.querySelectorAll('[data-materia-panel]'), function (panel) {{
      var vis = panel.querySelectorAll('li.item[data-item-id]:not(.hidden)');
      shown += vis.length;
      var empty = panel.querySelector('.panel-empty');
      if (empty) empty.classList.toggle('hidden', !(vis.length === 0 && !searching));
    }});

    var box = document.getElementById('sinResultados');
    box.classList.toggle('hidden', !(searching && shown === 0));
  }}

  document.getElementById('buscar').addEventListener('input', applyFilters);

  document.getElementById('btnPendientes').addEventListener('click', function () {{
    filterPending = !filterPending;
    this.classList.toggle('on', filterPending);
    this.setAttribute('aria-pressed', filterPending ? 'true' : 'false');
    this.textContent = filterPending ? 'Mostrar todos' : 'Ocultar tildados';
    applyFilters();
  }});

  /* ---------- exportar / importar ---------- */
  document.getElementById('btnExportar').addEventListener('click', function () {{
    var payload = {{
      app: 'listador-actividades',
      grado: '2do grado',
      bimestre: 'Bimestre 4',
      exportado: new Date().toISOString(),
      tildes: checks
    }};
    var blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'progreso-2do-bimestre-4.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  }});

  document.getElementById('btnImportar').addEventListener('click', function () {{
    document.getElementById('fileImport').click();
  }});

  document.getElementById('fileImport').addEventListener('change', function (ev) {{
    var file = ev.target.files && ev.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () {{
      try {{
        var obj = JSON.parse(reader.result);
        var next = obj.tildes || obj.checks || obj;
        if (!next || typeof next !== 'object') throw new Error('formato');
        checks = next;
        save();
        refreshAll();
        applyFilters();
        alert('Progreso importado correctamente.');
      }} catch (e) {{
        alert('No se pudo leer el archivo. Verificá que sea el JSON exportado desde esta página.');
      }}
    }};
    reader.readAsText(file);
    ev.target.value = '';
  }});

  document.getElementById('btnReset').addEventListener('click', function () {{
    if (!confirm('¿Borrar todas las tildes guardadas en este navegador?')) return;
    checks = {{}};
    save();
    refreshAll();
    applyFilters();
  }});

  /* ---------- arranque ---------- */
  var savedTab = null;
  try {{ savedTab = localStorage.getItem(TAB_KEY); }} catch (e) {{}}
  if (!savedTab || !document.getElementById(savedTab)) savedTab = 'panel-resumen';

  refreshAll();
  activateTab(savedTab, false);
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
