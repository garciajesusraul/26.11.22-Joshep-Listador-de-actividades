"""Servidor local mínimo para recibir URLs firmadas desde el navegador y bajar los PDFs.

Uso:
    python tools/pdf_server.py <carpeta_destino> [puerto]

El navegador (página de Schoology) hace POST a http://127.0.0.1:<puerto>/save
con JSON {"name": "...", "url": "..."} y el servidor descarga el archivo.
"""
import json
import os
import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DEST = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "pdfs")
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
os.makedirs(DEST, exist_ok=True)

LOCK = threading.Lock()
LOG = os.path.join(DEST, "_descargas.log")


def safe(name: str) -> str:
    keep = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789áéíóúÁÉÍÓÚñÑüÜ"
    out = "".join(c if c in keep else "_" for c in name)
    return out.strip()[:150] or "archivo"


def log(line: str) -> None:
    with LOCK:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def download(name: str, url: str) -> tuple[str, int]:
    fname = safe(name)
    path = os.path.join(DEST, fname)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as res:
        data = res.read()
    with open(path, "wb") as fh:
        fh.write(data)
    return fname, len(data)


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            name = payload["name"]
            url = payload["url"]
            fname, size = download(name, url)
            log(f"OK\t{fname}\t{size}")
            body = json.dumps({"ok": True, "file": fname, "bytes": size}).encode()
            status = 200
        except Exception as exc:  # noqa: BLE001
            log(f"ERR\t{raw[:200]!r}\t{exc}")
            body = json.dumps({"ok": False, "error": str(exc)}).encode()
            status = 500
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        body = json.dumps({"ok": True, "dest": DEST}).encode()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silencio
        pass


if __name__ == "__main__":
    print(f"sirviendo en http://127.0.0.1:{PORT} -> {DEST}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
