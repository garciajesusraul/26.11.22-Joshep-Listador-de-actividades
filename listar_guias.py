import json

path = r"C:\Users\Usuario\Documents\2026 Opencode\26.11.22  Joshep Listador de actividades\datos\bimestre-4.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

guias = []
for mi, materia in enumerate(data["materias"]):
    for ti, tema in enumerate(materia["temas"]):
        for ii, item in enumerate(tema["items"]):
            if item.get("tipo") == "guia":
                guias.append({
                    "materia": materia["nombre"],
                    "tema": tema["nombre"],
                    "item": item["nombre"],
                    "url": item.get("url", "SIN URL")
                })

for g in guias:
    url = g["url"][:50] if g["url"] != "SIN URL" else "SIN URL"
    print(g["materia"] + " | " + g["tema"][:35] + " | " + g["item"][:45] + " | " + url)

print("\nTotal: " + str(len(guias)) + " guias")
print("Con URL: " + str(sum(1 for g in guias if g["url"] != "SIN URL")))
print("Sin URL: " + str(sum(1 for g in guias if g["url"] == "SIN URL")))
