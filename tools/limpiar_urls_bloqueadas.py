"""Quita URLs de ítems bloqueados (cuestionarios/tutor) por regla del proyecto."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
PATH = "datos/bimestre-4.json"
d = json.load(open(PATH, encoding="utf-8"))
quitados = []


def w(items):
    for it in items:
        if not isinstance(it, dict):
            continue
        if it.get("tipo") in ("cuestionario", "tutor") and it.get("url"):
            quitados.append(it["nombre"])
            it["url"] = None
        w(it.get("subtareas") or [])


for m in d["materias"]:
    for t in m["temas"]:
        w(t["items"])

print("urls quitadas:", quitados)
json.dump(d, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
