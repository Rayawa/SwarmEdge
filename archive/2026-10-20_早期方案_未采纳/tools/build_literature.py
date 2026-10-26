"""Build human-readable notes, CSV and BibTeX from the verified paper register."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
papers = json.loads((ROOT / 'literature/papers.json').read_text())
with (ROOT / 'literature/papers.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(papers[0]))
    w.writeheader()
    w.writerows(papers)
notes = ['# 论文阅读库', '', f'检索截至2026-10-20。共{len(papers)}篇。阅读层级逐条标注；未标为全文精读的条目不作全文复现依据。年份区分首发、修订和会议发表。未核实的录用状态不推定。', '', '优先顺序：P17 → P19 → P18（2026 近邻，差异表见 research/10）→ P14 → P01 → P07 → P06 → P09 → P10 → P16；其余按研究路线选读。', '']
bib = []
for p in papers:
    notes += [f"## {p['id']} · {p['title']}", '', f"- 作者：{p['authors'].replace(' and ', '；')}", f"- 年份/版本：{p['year']}；{p['status']}", f"- 原文：[原始页面]({p['url']})", f"- 阅读层级：{p['read_level']}", f"- 可借鉴：{p['contribution']}", f"- 不可直接外推：{p['limitation']}"]
    if p['code']:
        notes += [f"- 作者项目/代码：{p['code']}"]
    notes += ['']
    fields = {'title': '{' + p['title'] + '}', 'author': p['authors'], 'year': str(p['year']), 'url': p['url'], 'note': p['status']}
    if p['arxiv']:
        fields.update(eprint=p['arxiv'], archivePrefix='arXiv')
    bib.append('@misc{' + p['id'] + ',\n' + ',\n'.join('  ' + k + ' = {' + v + '}' for k, v in fields.items()) + '\n}\n')
(ROOT / 'literature/论文阅读库.md').write_text('\n'.join(notes), encoding='utf-8')
(ROOT / 'literature/references.bib').write_text('\n'.join(bib), encoding='utf-8')
print(f'Built {len(papers)} paper notes, CSV and BibTeX')
