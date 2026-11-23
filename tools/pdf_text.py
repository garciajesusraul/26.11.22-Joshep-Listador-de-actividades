"""Extrae texto de los PDF en una carpeta y escribe .txt normalizados."""
import os
import re
import sys
import unicodedata

import pymupdf


def norm(t: str) -> str:
    t = t.replace("\u00a0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def slug(name: str) -> str:
    name = os.path.splitext(name)[0]
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return name[:80] or "pdf"


def main(src: str, dst: str) -> None:
    os.makedirs(dst, exist_ok=True)
    for root, _dirs, files in os.walk(src):
        for f in sorted(files):
            if not f.lower().endswith((".pdf", ".crdownload")):
                continue
            path = os.path.join(root, f)
            try:
                doc = pymupdf.open(path)
            except Exception as exc:  # noqa: BLE001
                print(f"ERR-OPEN\t{f}\t{exc}")
                continue
            text = "\n".join(norm(p.get_text()) for p in doc)
            text = re.sub(r"\n{2,}", "\n", text)
            out = os.path.join(dst, slug(f) + ".txt")
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(f"ARCHIVO: {f}\nPAGINAS: {doc.page_count}\n\n{text}\n")
            print(f"OK\t{f}\t{doc.page_count}\t{len(text)}\t{os.path.basename(out)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])