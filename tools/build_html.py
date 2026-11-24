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
    "guia": "Descargar Guía",
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


def render_sub(item_id, num, letra, item):
    """Renderiza una subtarea recursivamente (soporta sub-subítems)."""
    sid = f"{item_id}-{letra}"
    num_tag = f"{num}-{letra}" if num else letra
    nombre = item.get("nombre", "")
    tipo = item.get("tipo", "sub")
    subtareas = item.get("subtareas") or []
    url = item.get("url")

    link_btn = ""
    if url:
        if url.lower().endswith(".pdf") or "/attachment/" in url:
            link_btn = f'<a class="btn-link" href="{esc(url)}" target="_blank" rel="noopener" title="Descargar PDF">📄 Link</a>'
        else:
            link_btn = f'<a class="btn-link" href="{esc(url)}" target="_blank" rel="noopener" title="Abrir en Schoology">🔗 Link</a>'

    hijos_html = ""
    if subtareas:
        hijos_items = []
        for j, hijo in enumerate(subtareas):
            hijo_letra = chr(ord("a") + j)
            hijos_items.append(render_sub(sid, num_tag, hijo_letra, hijo))
        hijos_html = f"""<ul class="subs">
        {"".join(hijos_items)}
      </ul>"""

    return f"""<li class="sub">
          <label class="sub-label" for="{sid}">
            <input type="checkbox" id="{sid}" data-check="{sid}">
            <span class="sub-tag">{num_tag}</span>
            <span class="sub-text">{esc(nombre)}</span>
            {link_btn}
          </label>
          {hijos_html}
        </li>"""


def render_item(materia_idx, tema_idx, item_idx, numero, item):
    tipo = item.get("tipo", "tarea")
    icono = ICONOS.get(tipo, "•")
    etiqueta = ETIQUETAS.get(tipo, tipo)
    bloqueado = item.get("bloqueado") or tipo in ("cuestionario", "tutor")
    item_id = f"m{materia_idx}t{tema_idx}i{item_idx}"
    subtareas = item.get("subtareas") or []
    nota = item.get("nota")
    url = item.get("url")
    nota_html = f'<p class="nota">{esc(nota)}</p>' if nota else ""

    # Botón Link si hay URL
    link_btn = ""
    if url:
        if url.lower().endswith(".pdf") or "/attachment/" in url:
            link_btn = f'<a class="btn-link" href="{esc(url)}" target="_blank" rel="noopener" title="Descargar PDF">📄 Link</a>'
        else:
            link_btn = f'<a class="btn-link" href="{esc(url)}" target="_blank" rel="noopener" title="Abrir en Schoology">🔗 Link</a>'

    if tipo == "nota":
        return f"""<li class="item item-nota" data-item-id="{item_id}">
          <div class="item-head">
            <span class="item-num">{numero}.</span>
            <span class="item-name">{esc(item['nombre'])}</span>
            <span class="badge badge-nota">Aviso</span>
            {link_btn}
          </div>
          {nota_html}
        </li>"""

    candado = '<span class="lock" title="Ítem que solo abren el niño y el tutor">🔒</span>' if bloqueado else ""

    # Badge de guía clickeable si hay URL de descarga
    if tipo == "guia" and url:
        badge_html = f'<a class="badge badge-guia" href="{esc(url)}" target="_blank" rel="noopener">{icono} {esc(etiqueta)}</a>'
    else:
        badge_html = f'<span class="badge badge-{tipo}">{icono} {esc(etiqueta)}</span>'

    if subtareas:
        hijos = "\n        ".join(render_sub(item_id, numero, chr(ord("A") + i), s) for i, s in enumerate(subtareas))
        cuerpo = f"""<ul class="subs">
        {hijos}
      </ul>"""
        head = f"""<div class="item-head">
            <span class="item-num">{numero}.</span>
            <label class="item-label" for="{item_id}">
              <input type="checkbox" id="{item_id}" data-check="{item_id}" data-children="1">
              <span class="item-name">{esc(item['nombre'])}</span>
            </label>
            {badge_html}
            {candado}
            <span class="item-progress" data-progress="{item_id}">0/{len(subtareas)}</span>
            {link_btn}
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
            {badge_html}
            {candado}
            {link_btn}
          </div>
          {nota_html}"""

    return f"""<li class="item" data-item-id="{item_id}">
      {head}
      {cuerpo}
    </li>"""


def render():
    data = json.load(open(DATA, encoding="utf-8"))

    # Convertir subtareas de string a objetos para soportar jerarquía recursiva
    def normalizar_subtareas(items):
        for item in items:
            subs = item.get("subtareas")
            if subs:
                item["subtareas"] = [
                    s if isinstance(s, dict) else {"nombre": s}
                    for s in subs
                ]
                normalizar_subtareas(item["subtareas"])
    for materia in data["materias"]:
        for tema in materia["temas"]:
            normalizar_subtareas(tema["items"])

    # Sidebar tabs (vertical)
    sidebar_tabs = ['<button class="stab active" role="tab" aria-selected="true" data-tab="panel-resumen" id="stab-resumen"><span class="stab-icon">📊</span><span class="stab-name">Estadísticas</span><span class="stab-pct" data-tab-pct-global>0%</span></button>']
    paneles = []
    total_items = 0

    for mi, materia in enumerate(data["materias"]):
        mid = f"materia-{materia['id']}"
        emoji = EMOJIS.get(materia["id"], "📁")
        sidebar_tabs.append(
            f'<button class="stab" role="tab" aria-selected="false" data-tab="panel-m{mi}" id="stab-m{mi}">'
            f'<span class="stab-icon">{emoji}</span><span class="stab-name">{esc(materia["nombre"])}</span>'
            f'<span class="stab-pct" data-tab-pct="m{mi}">0%</span></button>'
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

        paneles.append(f"""<div class="panel" id="panel-m{mi}" role="tabpanel" aria-labelledby="stab-m{mi}" data-materia-panel="m{mi}">
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

    panel_resumen = f"""<div class="panel active" id="panel-resumen" role="tabpanel" aria-labelledby="stab-resumen">
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
    <p class="hint">Click en una fila para abrir su materia.</p>
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
    --sidebar-w: 220px;
    --sidebar-w-collapsed: 56px;
    --shadow: 0 1px 2px rgba(0,0,0,.06), 0 8px 24px rgba(0,0,0,.05);
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; height: 100%; }}
  body {{
    font-family: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg); color: var(--ink); line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    display: flex; flex-direction: column;
  }}

  /* --- Layout principal: sidebar fija + contenido --- */
  .app {{ display: flex; flex: 1; overflow: hidden; }}
  .sidebar {{
    width: var(--sidebar-w);
    min-width: var(--sidebar-w);
    background: #fff;
    border-right: 1px solid var(--line);
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    z-index: 50;
    transition: width .2s;
  }}
  .sidebar.collapsed {{ width: var(--sidebar-w-collapsed); min-width: var(--sidebar-w-collapsed); }}
  .sidebar-header {{
    padding: 14px 10px;
    border-bottom: 1px solid var(--line);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }}
  .sidebar-title {{
    font-size: 13px; font-weight: 800; color: var(--brand);
    text-transform: uppercase; letter-spacing: .5px; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
  }}
  .sidebar.collapsed .sidebar-title {{ display: none; }}
  .btn-toggle {{
    background: none; border: 1px solid var(--line); border-radius: 6px;
    width: 28px; height: 28px; cursor: pointer; display: flex; align-items: center; justify-content: center;
    color: var(--muted); font-size: 14px;
  }}
  .btn-toggle:hover {{ background: var(--brand-soft); border-color: var(--brand); color: var(--brand); }}

  .stab-list {{ list-style: none; margin: 0; padding: 8px 6px; flex: 1; }}
  .stab {{
    width: 100%; display: flex; align-items: center; gap: 8px;
    padding: 8px 10px; border: 1px solid transparent; background: transparent;
    border-radius: 8px; cursor: pointer; text-align: left; font: inherit;
    font-size: 13px; font-weight: 600; color: #4b5563; white-space: nowrap;
    transition: .15s;
  }}
  .stab:hover {{ background: var(--brand-soft); border-color: #cfe3dc; color: var(--brand); }}
  .stab.active {{ background: var(--brand); color: #fff; border-color: var(--brand); }}
  .stab-icon {{ font-size: 16px; flex-shrink: 0; }}
  .stab-name {{ flex: 1 1 auto; overflow: hidden; text-overflow: ellipsis; }}
  .stab-pct {{
    font-size: 10.5px; font-weight: 800; background: #eef1f0; color: #55605f;
    border-radius: 20px; padding: 0 7px; font-variant-numeric: tabular-nums;
    flex-shrink: 0; opacity: 0; transform: translateX(-10px); transition: .15s;
    white-space: nowrap;
  }}
  .stab.active .stab-pct {{ background: rgba(255,255,255,.22); color: #fff; }}
  .stab:not(.collapsed) .stab-pct {{ opacity: 1; transform: translateX(0); }}
  .sidebar.collapsed .stab-name,
  .sidebar.collapsed .stab-pct {{ display: none; }}
  .sidebar.collapsed .stab {{ justify-content: center; padding: 8px; }}

  .main {{ flex: 1; overflow-y: auto; padding: 0; }}

  /* --- Toolbar superior (solo en main) --- */
  .toolbar {{
    position: sticky; top: 0; z-index: 30;
    background: rgba(246,244,239,.96); backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--line); padding: 8px 16px;
  }}
  .toolbar-inner {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; max-width: 1000px; margin: 0 auto; }}
  .progress-shell {{ flex: 1 1 200px; min-width: 160px; }}
  .progress-bar {{ height: 8px; background: #e2ded4; border-radius: 99px; overflow: hidden; }}
  .progress-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, #2b8a72, #7cc4a9); transition: width .25s; }}
  .progress-text {{ font-size: 11.5px; color: var(--muted); margin-top: 3px; }}
  .progress-text b {{ color: var(--brand); }}

  .btn {{
    appearance: none; border: 1px solid var(--line); background: #fff; color: var(--ink);
    padding: 6px 11px; border-radius: 8px; font-size: 12.5px; cursor: pointer; font-weight: 600;
    transition: .15s; white-space: nowrap;
  }}
  .btn:hover {{ border-color: var(--brand); color: var(--brand); }}
  .btn.on {{ background: var(--brand); border-color: var(--brand); color: #fff; }}
  .btn-ghost {{ background: transparent; }}
  .btn-mini {{ font-size: 11.5px; color: var(--brand); text-decoration: none; border: 1px solid #cfe3dc; padding: 3px 8px; border-radius: 6px; }}
  .btn-mini:hover {{ background: var(--brand-soft); }}
  .btn-link {{
    appearance: none; border: 1px solid var(--line); background: #fff; color: var(--brand);
    padding: 2px 8px; border-radius: 6px; font-size: 10.5px; font-weight: 700;
    text-decoration: none; white-space: nowrap; transition: .15s;
    margin-left: 6px; flex-shrink: 0;
  }}
  .btn-link:hover {{ background: var(--brand-soft); border-color: var(--brand); color: var(--brand); }}
  input[type="search"] {{
    padding: 6px 10px; border-radius: 8px; border: 1px solid var(--line); font-size: 12.5px;
    min-width: 140px; background: #fff; flex: 1 1 200px;
  }}

  header.top {{
    background: linear-gradient(160deg, #1f6f5c 0%, #2b8a72 60%, #3ba07f 100%);
    color: #fff; padding: 16px 16px 14px; margin-left: var(--sidebar-w);
    transition: margin-left .2s;
  }}
  .sidebar.collapsed ~ .main header.top {{ margin-left: var(--sidebar-w-collapsed); }}
  header.top .wrap {{ max-width: 1000px; margin: 0 auto; }}
  header.top h1 {{ margin: 0 0 3px; font-size: clamp(18px, 2.5vw, 26px); letter-spacing: .2px; }}
  header.top p {{ margin: 0; opacity: .9; font-size: 12.5px; }}

  .wrap {{ max-width: 1000px; margin: 0 auto; padding: 0 16px 48px; }}

  /* --- Paneles --- */
  .panel {{ display: none; animation: fadeIn .15s; }}
  .panel.active {{ display: block; }}
  body.searching .panel {{ display: block; }}
  body.searching .sidebar {{ display: none; }}
  body.searching header.top {{ margin-left: 0; }}
  @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: none; }} }}

  /* --- Materia / tema --- */
  .materia {{ margin-bottom: 4px; }}
  .materia-head {{
    display: flex; align-items: baseline; justify-content: space-between; gap: 10px; flex-wrap: wrap;
    border-bottom: 2px solid var(--brand); padding-bottom: 5px; margin-bottom: 10px;
  }}
  .materia-head h2 {{ margin: 0; font-size: clamp(16px, 2vw, 20px); color: var(--brand); }}
  .materia-head h2 small {{ font-weight: 500; color: var(--muted); font-size: 12px; }}
  .materia-meta {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
  .chip {{
    font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 99px;
    white-space: nowrap; font-variant-numeric: tabular-nums;
  }}
  .chip-done {{ background: var(--brand-soft); color: #17614f; }}
  .chip-pend {{ background: #fdf1e3; color: #a9611f; }}
  .materia-bar {{ height: 6px; background: #e2ded4; border-radius: 99px; overflow: hidden; margin: 0 0 10px; }}
  .materia-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, #2b8a72, #7cc4a9); transition: width .25s; }}

  .tema {{
    background: var(--card); border: 1px solid var(--line); border-radius: 10px;
    padding: 10px 12px 6px; margin-bottom: 8px; box-shadow: var(--shadow);
  }}
  .tema-extra {{ border-left: 3px solid var(--accent); }}
  .tema-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; margin-bottom: 6px; }}
  .tema-head h3 {{ margin: 0; font-size: 14px; }}
  .tema-progress {{ font-size: 11px; color: var(--muted); white-space: nowrap; }}

  ul.items, ul.subs {{ list-style: none; margin: 0; padding: 0; }}
  li.item {{ padding: 5px 0; border-top: 1px dashed #eeebe3; }}
  li.item:first-child {{ border-top: 0; }}
  .item-head {{ display: flex; align-items: flex-start; gap: 6px; flex-wrap: wrap; }}
  .item-num {{ font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; padding-top: 2px; min-width: 18px; }}
  .item-label {{ display: flex; align-items: flex-start; gap: 7px; cursor: pointer; flex: 1 1 auto; min-width: 0; }}
  .item-label input {{ margin: 3px 0 0; width: 15px; height: 15px; accent-color: var(--brand); cursor: pointer; flex-shrink: 0; }}
  .item-name {{ font-size: 13.5px; font-weight: 600; word-break: break-word; }}
  .badge {{
    flex: 0 0 auto; font-size: 10px; font-weight: 700; letter-spacing: .2px; text-transform: uppercase;
    padding: 2px 6px; border-radius: 5px; background: #f0eee8; color: var(--muted); white-space: nowrap;
  }}
  .badge-video {{ background: #eef2fb; color: #3a5ba0; }}
  .badge-guia {{ background: #e9f5ef; color: #1f6f5c; }}
  .badge-foro {{ background: #fdf1e3; color: #a9611f; }}
  .badge-cuestionario, .badge-tutor {{ background: #f3e9ee; color: #8c4a63; }}
  .badge-audio, .badge-cancion {{ background: #f2ecfa; color: #6a4a9e; }}
  .badge-cartilla {{ background: #eef7f9; color: #2c7a8c; }}
  .badge-nota {{ background: #f0eee8; color: var(--muted); }}
  .lock {{ font-size: 11px; flex-shrink: 0; }}
  .item-progress {{ font-size: 10.5px; color: var(--muted); padding-top: 2px; font-variant-numeric: tabular-nums; flex-shrink: 0; }}

  .nota {{ margin: 3px 0 1px 24px; font-size: 11.5px; color: var(--muted); font-style: italic; }}

  ul.subs {{ margin: 3px 0 4px 24px; border-left: 2px solid var(--brand-soft); padding-left: 10px; }}
  li.sub {{ padding: 2px 0; }}
  .sub-label {{ display: flex; align-items: flex-start; gap: 6px; cursor: pointer; }}
  .sub-label input {{ margin: 2px 0 0; width: 13px; height: 13px; accent-color: var(--brand); cursor: pointer; flex-shrink: 0; }}
  .sub-tag {{ font-size: 10.5px; font-weight: 700; color: var(--brand); background: var(--brand-soft); padding: 1px 5px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; }}
  .sub-text {{ font-size: 12.5px; color: #3b4048; }}

  input[type="checkbox"]:checked + .item-name,
  input[type="checkbox"]:checked ~ .sub-text {{ text-decoration: line-through; color: var(--done); }}
  li.is-done .item-name {{ color: var(--done); }}

  .hide-done li.item.is-done {{ display: none; }}
  .hidden {{ display: none !important; }}

  /* --- Resumen / Estadísticas --- */
  .resumen h2 {{ margin: 4px 0 12px; font-size: clamp(17px, 2.2vw, 21px); color: var(--brand); }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 12px; }}
  .stat-card {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    padding: 12px 8px; text-align: center; box-shadow: var(--shadow);
  }}
  .stat-num {{ font-size: clamp(22px, 4vw, 30px); font-weight: 800; line-height: 1.1; font-variant-numeric: tabular-nums; }}
  .stat-lbl {{ font-size: 11px; text-transform: uppercase; letter-spacing: .5px; color: var(--muted); font-weight: 700; }}
  .stat-card.done .stat-num {{ color: var(--brand); }}
  .stat-card.pending .stat-num {{ color: var(--accent); }}
  .stat-card.pct .stat-num {{ color: #2e5d8a; }}

  .stats-block {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; box-shadow: var(--shadow); }}
  .progress-bar.big {{ height: 14px; }}
  .stats-caption {{ margin: 6px 0 0; font-size: 11.5px; color: var(--muted); }}
  .stats-title {{ margin: 18px 0 6px; font-size: 13px; text-transform: uppercase; letter-spacing: .6px; color: var(--muted); }}

  .table-wrap {{ overflow-x: auto; background: #fff; border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--shadow); }}
  table.stats-table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
  table.stats-table th {{ text-align: left; font-size: 10.5px; text-transform: uppercase; letter-spacing: .4px; color: var(--muted); padding: 7px 10px; border-bottom: 1px solid var(--line); }}
  table.stats-table th:nth-child(n+2), table.stats-table td:nth-child(n+2) {{ text-align: center; }}
  table.stats-table td {{ padding: 7px 10px; border-bottom: 1px solid #f1eee7; vertical-align: middle; }}
  table.stats-table tr:last-child td {{ border-bottom: 0; }}
  table.stats-table tr.row-link {{ cursor: pointer; }}
  table.stats-table tr.row-link:hover td {{ background: #f7fbf9; }}
  .cell-name {{ font-weight: 600; white-space: nowrap; }}
  .cell-num {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .cell-bar {{ min-width: 100px; }}
  .mini-bar {{ height: 6px; background: #ece8df; border-radius: 99px; overflow: hidden; }}
  .mini-fill {{ height: 100%; background: var(--brand); }}
  .pct-tag {{ font-weight: 700; color: var(--brand); font-variant-numeric: tabular-nums; }}

  .temas-stats {{ display: grid; gap: 5px; }}
  .tema-group {{
    margin: 10px 0 1px; font-size: 10.5px; font-weight: 800; letter-spacing: .5px;
    text-transform: uppercase; color: var(--brand);
  }}
  .tema-group:first-child {{ margin-top: 0; }}
  .tema-stat {{
    display: flex; justify-content: space-between; gap: 8px; align-items: center;
    background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 6px 10px; font-size: 12px;
  }}
  .tema-stat .t-name {{ font-weight: 600; }}
  .tema-stat .t-nums {{ font-size: 11px; color: var(--muted); white-space: nowrap; }}
  .tema-stat.full {{ opacity: .55; }}

  .panel-empty {{ text-align: center; background: #fff; border: 1px dashed #cfe3dc; color: var(--brand); border-radius: 10px; padding: 18px; font-weight: 600; font-size: 13.5px; }}

  .empty {{ text-align: center; color: var(--muted); padding: 24px; font-size: 13.5px; }}

  footer {{ text-align: center; color: var(--muted); font-size: 11px; padding: 20px 10px 0; }}
  footer code {{ background: #efede6; padding: 1px 4px; border-radius: 4px; }}

  @media (max-width: 900px) {{
    .sidebar {{ width: var(--sidebar-w-collapsed); min-width: var(--sidebar-w-collapsed); }}
    .sidebar .sidebar-title, .sidebar .stab-name, .sidebar .stab-pct {{ display: none; }}
    .sidebar .stab {{ justify-content: center; padding: 8px; }}
    header.top, .sidebar.collapsed ~ .main header.top {{ margin-left: var(--sidebar-w-collapsed); }}
    .badge, .item-progress {{ display: none; }}
    .stats-grid {{ gap: 6px; }}
    .cell-bar {{ display: none; }}
  }}
  @media (max-width: 600px) {{
    .sidebar {{ position: fixed; left: 0; top: 0; bottom: 0; z-index: 100; transform: translateX(-100%); box-shadow: 4px 0 20px rgba(0,0,0,.1); }}
    .sidebar.open {{ transform: none; }}
    header.top, .sidebar.collapsed ~ .main header.top {{ margin-left: 0; }}
    .toolbar {{ padding: 8px 12px; }}
    .btn-mini, .btn-ghost {{ display: none; }}
    .stab-list {{ padding-bottom: 60px; }}
  }}
  @media print {{
    .sidebar, .toolbar, .btn, .btn-mini, .btn-link {{ display: none !important; }}
    body {{ background: #fff; }}
    .panel {{ display: block !important; page-break-inside: avoid; }}
    #panel-resumen {{ page-break-after: always; }}
    .tema {{ box-shadow: none; break-inside: avoid; }}
    .hide-done li.item.is-done {{ display: list-item; }}
    header.top {{ margin-left: 0; }}
  }}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar" id="sidebar" role="navigation" aria-label="Materias y estadísticas">
    <div class="sidebar-header">
      <span class="sidebar-title">Materias</span>
      <button class="btn-toggle" id="btnToggleSidebar" aria-label="Colapsar sidebar" title="Colapsar/Expandir">◀</button>
    </div>
    <ul class="stab-list" role="tablist">
      {chr(10).join(sidebar_tabs)}
    </ul>
  </aside>

  <main class="main" id="main">
    <div class="toolbar">
      <div class="toolbar-inner">
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
      {panel_resumen}
      {chr(10).join(paneles)}
      <div class="empty hidden" id="sinResultados">No hay actividades que coincidan con la búsqueda.</div>
      <footer>
        Progreso guardado en este navegador (localStorage). Usá <strong>Exportar</strong> para guardar un respaldo en <code>.json</code>.
      </footer>
    </div>
  </main>
</div>

<script>
(function () {{
  "use strict";
  var KEY = "jhs-2do-b4-v1";
  var TAB_KEY = "jhs-2do-b4-tab";
  var SIDEBAR_KEY = "jhs-2do-b4-sidebar";
  var checks = {{}};
  var filterPending = false;

  /* ---------- Supabase (sincronización entre PCs) ---------- */
  var SUPABASE_URL = "https://ztigjbhktpvwtkdjjdjl.supabase.co";
  var SUPABASE_KEY = "sb_publishable_6mx_PPNIOms3ZiyeCy4gBA_wR3zApgs";
  var SUPABASE_TABLE = "progreso_2do_b4";
  var supabaseReady = false;

  async function supabaseGet() {{
    try {{
      var res = await fetch(SUPABASE_URL + "/rest/v1/" + SUPABASE_TABLE + "?select=item_id,checked", {{
        headers: {{
          apikey: SUPABASE_KEY,
          Authorization: "Bearer " + SUPABASE_KEY
        }}
      }});
      if (!res.ok) return null;
      var data = await res.json();
      var out = {{}};
      data.forEach(function (row) {{ out[row.item_id] = row.checked === true; }});
      return out;
    }} catch (e) {{ return null; }}
  }}

  async function supabaseSave(obj) {{
    try {{
      var rows = Object.keys(obj).map(function (k) {{
        return {{ item_id: k, checked: obj[k] === true }};
      }});
      if (rows.length === 0) return;
      await fetch(SUPABASE_URL + "/rest/v1/" + SUPABASE_TABLE, {{
        method: "POST",
        headers: {{
          apikey: SUPABASE_KEY,
          Authorization: "Bearer " + SUPABASE_KEY,
          "Content-Type": "application/json",
          Prefer: "resolution=merge-duplicates"
        }},
        body: JSON.stringify(rows)
      }});
    }} catch (e) {{}}
  }}

  /* Cargar desde Supabase al arrancar (si hay datos más recientes que localStorage) */
  (function cargarSupabase() {{
    supabaseGet().then(function (remoto) {{
      if (remoto && Object.keys(remoto).length > 0) {{
        checks = remoto;
        save();
        refreshAll();
        applyFilters();
      }}
      supabaseReady = true;
    }});
  }})();

  function allInputs() {{
    return Array.prototype.slice.call(document.querySelectorAll('input[data-check]'));
  }}
  function leaves() {{
    return allInputs().filter(function (i) {{ return !i.hasAttribute('data-children'); }});
  }}
  function subsOf(id) {{
    return Array.prototype.slice.call(document.querySelectorAll('input[data-check^="' + id + '-"]'));
  }}
  function setSub(id, val) {{
    if (val) checks[id] = true; else delete checks[id];
  }}

  /* ---------- pestañas / sidebar ---------- */
  var stabs = Array.prototype.slice.call(document.querySelectorAll('[data-tab]'));
  var sidebar = document.getElementById('sidebar');
  var main = document.getElementById('main');
  var btnToggle = document.getElementById('btnToggleSidebar');

  function activateTab(panelId, remember) {{
    var activeBtn = null;
    stabs.forEach(function (t) {{
      var on = t.getAttribute('data-tab') === panelId;
      if (on) activeBtn = t;
      t.classList.toggle('active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    }});
    Array.prototype.forEach.call(document.querySelectorAll('.panel'), function (p) {{
      p.classList.toggle('active', p.id === panelId);
    }});
    if (remember !== false) {{
      try {{ localStorage.setItem(TAB_KEY, panelId); }} catch (e) {{}}
    }}
    // Scroll suave al top del contenido
    main.scrollTo({{ top: 0, behavior: 'smooth' }});
  }}

  stabs.forEach(function (t) {{
    t.addEventListener('click', function () {{
      document.getElementById('buscar').value = '';
      document.body.classList.remove('searching');
      activateTab(t.getAttribute('data-tab'));
      applyFilters();
      // En móvil, cerrar sidebar al elegir
      if (window.innerWidth <= 600) sidebar.classList.remove('open');
    }});
  }});

  // Toggle sidebar collapse
  var sidebarCollapsed = false;
  try {{ sidebarCollapsed = localStorage.getItem(SIDEBAR_KEY) === '1'; }} catch (e) {{}}
  if (sidebarCollapsed) {{ sidebar.classList.add('collapsed'); btnToggle.textContent = '▶'; btnToggle.setAttribute('aria-label', 'Expandir sidebar'); }}
  btnToggle.addEventListener('click', function () {{
    sidebarCollapsed = !sidebarCollapsed;
    sidebar.classList.toggle('collapsed', sidebarCollapsed);
    btnToggle.textContent = sidebarCollapsed ? '▶' : '◀';
    btnToggle.setAttribute('aria-label', sidebarCollapsed ? 'Expandir sidebar' : 'Colapsar sidebar');
    try {{ localStorage.setItem(SIDEBAR_KEY, sidebarCollapsed ? '1' : '0'); }} catch (e) {{}}
  }});

  /* ---------- estado de ítems ---------- */
  function refreshItem(li) {{
    var id = li.getAttribute('data-item-id');
    var parent = li.querySelector('input[data-children]');
    var allSubs = subsOf(id);
    var leafSubs = allSubs.filter(function (s) {{ return !s.hasAttribute('data-children'); }});
    if (leafSubs.length) {{
      var done = leafSubs.filter(function (s) {{ return s.checked; }}).length;
      if (parent) parent.checked = done === leafSubs.length;
      var prog = li.querySelector('[data-progress]');
      if (prog) prog.textContent = done + "/" + leafSubs.length;
    }}
    var own = li.querySelector('input[data-check]');
    var isDone = leafSubs.length ? leafSubs.every(function (s) {{ return s.checked; }}) : !!(own && own.checked);
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
    save();           // <-- AUTO-GUARDADO en cada cambio
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
</html>"""

def main():
    html_out = render()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html_out)
    print(f"OK  {OUT}  {len(html_out)} bytes")

if __name__ == "__main__":
    main()