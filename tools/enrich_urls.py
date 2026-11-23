#!/usr/bin/env python3
"""Enriquece datos/bimestre-4.json con URLs desde datos/arbol_materias.json"""
import json
import re
from urllib.parse import urljoin

BASE = "https://jhs.schoology.com"

ROOT = __file__.rsplit("\\", 2)[0]  # C:\...\26.11.22 Joshep Listador de actividades
BIM = ROOT + "\\datos\\bimestre-4.json"
ARBOL = ROOT + "\\datos\\arbol_materias.json"

def norm(t):
    """Normaliza título para matching"""
    t = t.lower()
    t = re.sub(r'^\d+\.\-\s*', '', t)  # "1.- Video" -> "Video"
    t = re.sub(r'[^\w\s]', '', t)      # quita signos
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def extract_items(node, acc):
    """Recorre el árbol y acumula (norm_title, href)"""
    if isinstance(node, dict):
        title = node.get("title", "") or node.get("body", "")[:80]
        href = node.get("href")
        if title and href:
            acc[norm(title)] = urljoin(BASE, href)
        for ch in node.get("children", []):
            extract_items(ch, acc)
    elif isinstance(node, list):
        for ch in node:
            extract_items(ch, acc)

def enrich_bim(materia, arbol_map, path=""):
    """Recorre bimestre-4.json y agrega url donde coincida"""
    if isinstance(materia, dict):
        # Si es un item con nombre
        if "nombre" in materia and "tipo" in materia:
            key = norm(materia["nombre"])
            if key in arbol_map:
                materia["url"] = arbol_map[key]
            # fallback: buscar por clave parcial
            else:
                for k, v in arbol_map.items():
                    if key in k or k in key:
                        materia["url"] = v
                        break
        for k, v in materia.items():
            enrich_bim(v, arbol_map, f"{path}.{k}")
    elif isinstance(materia, list):
        for i, v in enumerate(materia):
            enrich_bim(v, arbol_map, f"{path}[{i}]")

def main():
    with open(BIM, encoding="utf-8") as f:
        bim = json.load(f)
    with open(ARBOL, encoding="utf-8") as f:
        arbol = json.load(f)

    # Mapa global de todos los ítems del árbol
    arbol_map = {}
    for mat_id, mat_data in arbol.items():
        extract_items(mat_data.get("tree", []), arbol_map)

    print(f"Ítems en árbol scrapeado: {len(arbol_map)}")

    # Enriquecer
    enrich_bim(bim, arbol_map)

    # Contar cuántos quedaron con URL
    count = 0
    def count_urls(obj):
        nonlocal count
        if isinstance(obj, dict):
            if "url" in obj:
                count += 1
            for v in obj.values():
                count_urls(v)
        elif isinstance(obj, list):
            for v in obj:
                count_urls(v)
    count_urls(bim)
    print(f"Ítems con URL en bimestre-4.json: {count}")

    # Guardar
    with open(BIM, "w", encoding="utf-8") as f:
        json.dump(bim, f, ensure_ascii=False, indent=2)
    print("OK - bimestre-4.json actualizado")

if __name__ == "__main__":
    main()