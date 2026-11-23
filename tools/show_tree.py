"""Muestra el árbol de materias scrapeado de forma legible."""
import json
import sys


def walk(n, depth=0):
    pad = "  " * depth
    t = n.get("type", "")
    ti = n.get("title", "")
    extra = ""
    if n.get("atts"):
        names = "; ".join(a["name"] for a in n["atts"])
        extra = f"  <<PDF: {names}>>"
    print(f"{pad}[{t}] {ti}{extra}")
    if n.get("body"):
        print(f"{pad}   · {n['body'][:200]}")
    for c in n.get("children", []):
        walk(c, depth + 1)


def main(path):
    d = json.load(open(path, encoding="utf-8"))
    for k, v in d.items():
        print("#" * 5, k, "  b4=", v.get("b4"))
        for n in v.get("tree", []):
            walk(n, 1)
        print()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "datos/arbol_materias.json")
