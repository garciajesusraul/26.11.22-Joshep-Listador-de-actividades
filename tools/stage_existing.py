"""Copia a la carpeta de staging los PDFs que ya existen en Descargas del usuario."""
import json
import os
import shutil
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS = os.path.join(os.environ["USERPROFILE"], "Downloads")
STAGING = os.path.join(ROOT, "datos", "stage")
MANIFEST = os.path.join(ROOT, "datos", "manifest_pdfs.json")

PROHIBIDO = ("correccion", "tutor", "tutores", "solucionario", "sol_", "_sol", "revision")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = os.path.basename(s).lower()
    for suf in [" (1)", " (2)", " (3)", " (4)", " (5)"]:
        if s.endswith(suf):
            s = s[: -len(suf)]
    s = os.path.splitext(s)[0]
    return "".join(c if c.isalnum() else "" for c in s)


def main() -> None:
    os.makedirs(STAGING, exist_ok=True)
    man = json.load(open(MANIFEST, encoding="utf-8"))
    files = []
    for root, _d, fs in os.walk(DOWNLOADS):
        if os.path.abspath(root) == os.path.abspath(STAGING):
            continue
        for f in fs:
            if f.lower().endswith(".pdf"):
                files.append(os.path.join(root, f))
    index = {}
    for path in files:
        index.setdefault(norm(os.path.basename(path)), path)

    found, missing = [], []
    for key, want in man.items():
        if key.startswith("_"):
            continue
        if any(p in want.lower().replace("_", "") for p in PROHIBIDO):
            missing.append((key, want, "PROHIBIDO-material-de-tutor"))
            continue
        hit = index.get(norm(want))
        if hit:
            dest = os.path.join(STAGING, key + ".pdf")
            shutil.copy2(hit, dest)
            found.append((key, os.path.basename(hit)))
        else:
            missing.append((key, want, "no-descargado"))

    print("--- ENCONTRADOS ---")
    for k, f in found:
        print(f"{k}\t{f}")
    print("--- FALTANTES ---")
    for k, f, why in missing:
        print(f"{k}\t{f}\t{why}")


if __name__ == "__main__":
    main()