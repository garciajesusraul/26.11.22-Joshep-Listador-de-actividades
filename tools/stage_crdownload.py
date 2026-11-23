"""Copia los .crdownload completos (descargas que Edge no finalizó) al staging con su clave."""
import json
import os
import shutil
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS = os.path.join(os.environ["USERPROFILE"], "Downloads")
STAGING = os.path.join(ROOT, "datos", "stage")
MANIFEST = os.path.join(ROOT, "datos", "manifest_pdfs.json")

PROHIBIDO = ("correccion", "tutor", "tutores", "solucionario", "revision")


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = os.path.basename(s).lower()
    for suf in (" (1)", " (2)", " (3)", " (4)", " (5)"):
        if s.endswith(suf):
            s = s[: -len(suf)]
    if s.endswith(".crdownload"):
        s = s[: -len(".crdownload")]
    s = os.path.splitext(s)[0]
    return "".join(c if c.isalnum() else "" for c in s)


def main():
    os.makedirs(STAGING, exist_ok=True)
    man = json.load(open(MANIFEST, encoding="utf-8"))
    index = {}
    for root, _d, fs in os.walk(DOWNLOADS):
        for f in fs:
            low = f.lower()
            if low.endswith((".pdf", ".crdownload")):
                index.setdefault(norm(f), os.path.join(root, f))

    found, missing = [], []
    for key, want in man.items():
        if key.startswith("_"):
            continue
        if any(p in norm(want) for p in PROHIBIDO):
            missing.append((key, want, "prohibido"))
            continue
        hit = index.get(norm(want))
        if hit:
            dest = os.path.join(STAGING, key + ".pdf")
            shutil.copy2(hit, dest)
            found.append((key, os.path.basename(hit), os.path.getsize(dest)))
        else:
            missing.append((key, want, "no-descargado"))

    print(f"ENCONTRADOS: {len(found)}")
    for k, f, n in found:
        print(f"  {k}\t{f}\t{n}")
    print(f"FALTANTES: {len(missing)}")
    for k, f, why in missing:
        print(f"  {k}\t{f}\t{why}")


if __name__ == "__main__":
    main()
