"""Simple static server to serve the annotator and accept save requests.

Usage: python scripts/serve_annotator.py

Opens http://localhost:8000/web/annotator/index.html and accepts POST /save to write
posted JSON to diagnose_report.json in the repo root. This is intended for local use only.
"""
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'diagnose_report.json'
BACKUP_DIR = ROOT / 'diagnose_backups'
BACKUP_DIR.mkdir(exist_ok=True)


class Handler(SimpleHTTPRequestHandler):
    def _write_json_response(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            try:
                obj = json.loads(data.decode('utf-8'))
                # write backup
                ts = datetime.utcnow().strftime('%Y%m%d_%H%M%SZ')
                bak = BACKUP_DIR / f'diagnose_report_{ts}.json'
                bak.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
                # also write main report
                REPORT.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
                self._write_json_response(200, {'status': 'saved', 'backup': str(bak.name)})
            except Exception as e:
                self._write_json_response(400, {'error': str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        # Add simple backups listing and download endpoints
        parsed = urlparse(self.path)
        if parsed.path == '/backups':
            files = sorted([p.name for p in BACKUP_DIR.glob('diagnose_report_*.json')], reverse=True)
            self._write_json_response(200, {'backups': files})
            return
        if parsed.path == '/download':
            qs = parse_qs(parsed.query)
            name = qs.get('name', [None])[0]
            if not name:
                self._write_json_response(400, {'error': 'missing name parameter'})
                return
            target = BACKUP_DIR / name
            if not target.exists():
                self._write_json_response(404, {'error': 'not found'})
                return
            # serve file bytes
            data = target.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        # fallback to default static handler
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    import webbrowser
    import os
    os.chdir(str(ROOT))
    server = HTTPServer(('localhost', 8000), Handler)
    print('Serving at http://localhost:8000/web/annotator/index.html')
    webbrowser.open('http://localhost:8000/web/annotator/index.html')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down...')
        server.server_close()
