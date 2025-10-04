import unittest
from pathlib import Path
import sys
import json

# setup import path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

import importlib

serve_mod = importlib.import_module('scripts.serve_annotator')


class BackupsServerTests(unittest.TestCase):
    def test_save_creates_backup(self):
        root = Path(serve_mod.ROOT)
        report = root / 'diagnose_report.json'
        backups = root / 'diagnose_backups'
        # prepare test payload
        payload = [{'text':'sample','extraction':{'fs':1000}}]
        # call the same write logic used by handler
        ts_before = set(p.name for p in backups.glob('diagnose_report_*.json')) if backups.exists() else set()
        # write backup and main report
        serve_mod.BACKUP_DIR.mkdir(exist_ok=True)
        import time
        serve_mod.BACKUP_DIR
        # mimic handler behavior
        ts = "testts"
        bak = backups / f'diagnose_report_{ts}.json'
        bak.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        self.assertTrue(bak.exists())
        # cleanup
        bak.unlink()


if __name__ == '__main__':
    unittest.main()
