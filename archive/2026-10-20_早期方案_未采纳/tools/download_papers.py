"""Fetch selected public author manuscripts; retain source URLs and integrity hashes."""
import hashlib
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'literature/pdfs'
PDF.mkdir(exist_ok=True)
selected = {'P01': '2205.09778v3', 'P06': '2209.12836v1', 'P07': '2409.09975v2', 'P09': '2609.12502v1', 'P10': '2508.07657v2', 'P14': '2610.15966v1'}
manifest = []
for pid, version in selected.items():
    url = 'https://arxiv.org/pdf/' + version
    dest = PDF / (pid + '_' + version + '.pdf')
    item = {'id': pid, 'version': version, 'url': url, 'retrieved_on': '2026-10-20'}
    try:
        if dest.exists() and dest.read_bytes().startswith(b'%PDF'):
            data = dest.read_bytes()
        else:
            req = urllib.request.Request(url, headers={'User-Agent': 'SwarmEdgeResearch/1.0 (personal academic reading)'})
            with urllib.request.urlopen(req, timeout=25) as response:
                data = response.read()
            if not data.startswith(b'%PDF'):
                raise ValueError('Response is not PDF')
            dest.write_bytes(data)
        item.update(status='downloaded', file=str(dest.relative_to(ROOT)), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as exc:
        item.update(status='failed', error=str(exc))
    manifest.append(item)
    (ROOT / 'literature/download_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(pid, item['status'], flush=True)
    time.sleep(3)
