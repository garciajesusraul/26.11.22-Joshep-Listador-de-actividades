"""Rellena URLs faltantes de cartillas, foros y canciones/audios."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "https://jhs.schoology.com"
PATH = "datos/bimestre-4.json"

URLS = {
    # luces: cartillas (PDF directo) y foros
    ("luces", "Tema 16 — El ritmo en el dibujo", "3. Cartilla de motricidad — Tema 16"):
        BASE + "/attachment/3566815129/source/2da0117b4e5a96383d36fbf20277bcbd.pdf",
    ("luces", "Tema 17 — Telar", "3. Cartilla de motricidad — Tema 17"):
        BASE + "/attachment/3566815137/source/8ac1ffa1bbaa54d1f2d9af1f17eb9b6a.pdf",
    ("luces", "Tema 19 — A cada escultura su técnica", "4. Cartilla de manualidad — Tema 19"):
        BASE + "/attachment/3566815163/source/7d8f8bee6648c2e8b080645c40485eaa.pdf",
    ("luces", "Tema 17 — Telar", "4. Foro — Telar"):
        BASE + "/course/8201804045/materials/discussion/view/8600338370",
    ("luces", "Tema 18 — El collage", "4. Foro — El collage"):
        BASE + "/course/8201804045/materials/discussion/view/8600338405",
    # sonidos: foro del tema 16
    ("sonidos", "Tema 16 — Descubramos: sonidos y tecnología", "Foro — DESCUBRAMOS: Sonidos y Tecnología"):
        BASE + "/course/8201681261/materials/discussion/view/8598507686",
    # matematicas: canciones en mp3 y en PDF (páginas de archivo de Schoology)
    ("matematicas", "Tema 21 — Estimaciones a la decena", "c. Canción — Tabla del 6 (mp3)"):
        BASE + "/course/8202767047/materials/gp/8603737006",
    ("matematicas", "Tema 21 — Estimaciones a la decena", "d. Canción Tabla del 6 (PDF)"):
        BASE + "/course/8202767047/materials/gp/8603737420",
    ("matematicas", "Tema 23 — Unión e intersección de conjuntos", "c. Canción — Tabla del 7 (mp3)"):
        BASE + "/course/8202767047/materials/gp/8603742650",
    ("matematicas", "Tema 23 — Unión e intersección de conjuntos", "d. Canción Tabla del 7 (PDF)"):
        BASE + "/course/8202767047/materials/gp/8603742439",
    ("matematicas", "Cuadernillo 13 — Relación de comparación", "b. Canción — Tabla del 8 (mp3)"):
        BASE + "/course/8202767047/materials/gp/8600596336",
    ("matematicas", "Cuadernillo 13 — Relación de comparación", "c. Canción Tabla del 8 (PDF)"):
        BASE + "/course/8202767047/materials/gp/8603758315",
    ("matematicas", "Cuadernillo 15 — Estimaciones a la decena", "b. Canción — Tabla del 9 (mp3)"):
        BASE + "/course/8202767047/materials/gp/8603759637",
    ("matematicas", "Cuadernillo 15 — Estimaciones a la decena", "c. Canción Tabla del 9 (PDF)"):
        BASE + "/course/8202767047/materials/gp/8603759655",
}

d = json.load(open(PATH, encoding="utf-8"))
aplicados = 0
for m in d["materias"]:
    for t in m["temas"]:
        for it in t["items"]:
            if not isinstance(it, dict):
                continue
            key = (m["id"], t["nombre"], it.get("nombre"))
            if key in URLS:
                if it.get("url"):
                    print("YA TIENE URL, no se toca:", key)
                    continue
                it["url"] = URLS.pop(key)
                aplicados += 1

print("aplicados:", aplicados, "| sin aplicar:", list(URLS))
json.dump(d, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("guardado", PATH)
