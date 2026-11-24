"""Copia local de las guías y cartillas en PDFs comprimidos dentro del repo.

Genera pdfs/<materia>/<clave>.pdf y escribe en el JSON el campo `pdf_local`
con la ruta relativa. Así los enlaces de descarga no dependen de Schoology
(que borra los archivos al cambiar de bimestre) ni de una sesión activa.
"""
import json
import os
import sys

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = os.path.join(ROOT, "datos", "stage")
DEST = os.path.join(ROOT, "pdfs")
DATA = os.path.join(ROOT, "datos", "bimestre-4.json")

# (materia, texto del tema, tipo del ítem) -> clave del PDF en datos/stage
MAPA = [
    ("ciencias", "Tema 14", "guia", "CV_t14_guia"),
    ("ciencias", "Tema 15", "guia", "CV_t15_guia"),
    ("ciencias", "Tema 16", "guia", "CV_t16_guia"),
    ("ciencias", "Tema 17", "guia", "CV_t17_guia"),
    ("english", "Lesson 8", "guia:Workbook 8 — Grammar", "EN_l8_grammar"),
    ("english", "Lesson 8", "guia:Workbook 8", "EN_l8_workbook"),
    ("english", "Lesson 9", "guia:Grammar", "EN_l9_grammar"),
    ("english", "Lesson 9", "guia:Workbook 9", "EN_l9_workbook"),
    ("english", "Lesson 10", "guia", "EN_l10_workbook"),
    ("historia", "Tema 13", "guia", "HG_t13_guia"),
    ("historia", "Tema 14", "guia", "HG_t14_guia"),
    ("historia", "Tema 15", "guia", "HG_t15_guia"),
    ("historia", "Tema 16", "guia", "HG_t16_guia"),
    ("lenguaje", "Tema 20", "guia", "LC_t20_guia"),
    ("lenguaje", "Tema 21", "guia", "LC_t21_guia"),
    ("lenguaje", "Tema 22", "guia", "LC_t22_guia"),
    ("lenguaje", "Tema 23", "guia", "LC_t23_guia"),
    ("lenguaje", "Tema 24", "guia", "LC_t24_guia"),
    ("lenguaje", "Tema 25", "guia", "LC_t25_guia"),
    ("luces", "Tema 16", "guia", "LYC_t16_guia"),
    ("luces", "Tema 16", "cartilla", "LYC_t16_cartilla"),
    ("luces", "Tema 17", "guia", "LYC_t17_guia"),
    ("luces", "Tema 17", "cartilla", "LYC_t17_cartilla"),
    ("luces", "Tema 18", "guia", "LYC_t18_guia"),
    ("luces", "Tema 19", "guia", "LYC_t19_guia"),
    ("luces", "Tema 19", "cartilla", "LYC_t19_cartilla"),
    ("matematicas", "Tema 21", "guia", "MAT_t21_guia"),
    ("matematicas", "Tema 22", "guia", "MAT_t22_guia"),
    ("matematicas", "Tema 23", "guia", "MAT_t23_guia"),
    ("matematicas", "Tema 24", "guia", "MAT_t24_guia"),
    ("matematicas", "Cuadernillo 13", "guia", "MAT_c13_cuadernillo"),
    ("matematicas", "Cuadernillo 14", "guia", "MAT_c14_cuadernillo"),
    ("matematicas", "Cuadernillo 15", "guia", "MAT_c15_cuadernillo"),
    ("matematicas", "Cuadernillo 16", "guia", "MAT_c16_cuadernillo"),
    ("sonidos", "Tema 13", "guia", "SN_t13_guia"),
    ("sonidos", "Tema 14", "guia", "SN_t14_guia"),
    ("sonidos", "Juegos", "guia", "SN_juegos_guia"),
    ("sonidos", "Tema 15", "guia", "SN_t15_guia"),
]

SLUG = {
    "ciencias": "ciencias",
    "english": "english",
    "historia": "historia",
    "lenguaje": "lenguaje",
    "luces": "luces",
    "matematicas": "matematicas",
    "sonidos": "sonidos",
}

d = json.load(open(DATA, encoding="utf-8"))
usados = {}
faltan = []

for materia_txt, tema_txt, spec, clave in MAPA:
    tipo, _, nombre_txt = spec.partition(":")
    origen = os.path.join(STAGE, clave + ".pdf")
    if not os.path.exists(origen):
        faltan.append(clave)
        continue

    destino_dir = os.path.join(DEST, SLUG[materia_txt])
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, clave.lower() + ".pdf")

    doc = pymupdf.open(origen)
    doc.save(destino, garbage=4, deflate=True, clean=True)
    paginas = doc.page_count
    doc.close()

    rel = f"pdfs/{SLUG[materia_txt]}/{clave.lower()}.pdf"
    usados[clave] = (rel, os.path.getsize(destino), paginas)

    # aplicar al JSON
    tocado = False
    for m in d["materias"]:
        if m["id"] != materia_txt:
            continue
        for t in m["temas"]:
            if tema_txt not in t["nombre"]:
                continue
            for it in t["items"]:
                if not isinstance(it, dict) or it.get("tipo") != tipo:
                    continue
                if nombre_txt and nombre_txt not in it.get("nombre", ""):
                    continue
                it["pdf_local"] = rel
                tocado = True
    if not tocado:
        print("NO APLICADO:", materia_txt, tema_txt, spec, clave)

json.dump(d, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

total = sum(v[1] for v in usados.values())
print(f"PDFs copiados: {len(usados)} | total {total / 1024 / 1024:.1f} MB")
print("faltan:", faltan)
