"""Audit deliverables and arithmetic; does not validate robots or research novelty."""
import csv
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks = []

def check(name, ok, detail=''):
    checks.append({'name': name, 'passed': bool(ok), 'detail': detail})

required = ['README.md', 'research/01_调研结论与立项建议.md', 'research/02_场景与痛点筛选.md',
            'research/03_相关工作与研究边界.md', 'research/04_架构与技术路线.md',
            'research/05_硬件成本与复用.md', 'research/06_检索与证据台账.md',
            'research/07_专利与成果初筛.md', 'research/08_容量模型与结果.md',
            'research/09_问题形式化与数据准备.md',
            'planning/01_实验与验收方案.md', 'planning/02_执行计划与任务.md',
            'planning/03_立项论证草案.md', 'planning/04_访谈询价与实测表.md',
            'planning/05_完成性核对.md', 'planning/06_风险与决策.md',
            'literature/papers.json', 'literature/papers.csv', 'literature/references.bib',
            'literature/论文阅读库.md', 'planning/measurement_template.csv']
check('required_artifacts', all((ROOT/p).is_file() and (ROOT/p).stat().st_size > 20 for p in required))
broken=[]
for md in ROOT.rglob('*.md'):
    text=md.read_text()
    for link in re.findall(r'\]\(([^)]+)\)', text):
        if link.startswith(('https://','http://','#')):
            continue
        path=link.split('#')[0]
        path=re.sub(r':\d+$', '', path)
        dest=Path(path) if path.startswith('/') else md.parent/path
        if not dest.exists(): broken.append(str(md.relative_to(ROOT))+' -> '+link)
check('local_document_links_exist', not broken, broken)
papers=json.loads((ROOT/'literature/papers.json').read_text())
check('paper_register_unique_and_complete', len(papers)>=16 and len({p['id'] for p in papers})==len(papers))
check('paper_fields_and_read_depth', all(p.get('url') and p.get('title') and p.get('read_level') and p.get('limitation') for p in papers))
check('paper_csv_matches', len(list(csv.DictReader((ROOT/'literature/papers.csv').open(encoding='utf-8-sig'))))==len(papers))
manifest=json.loads((ROOT/'literature/download_manifest.json').read_text())
for m in manifest:
    path=ROOT/m.get('file','missing')
    ok=m['status']=='downloaded' and path.is_file()
    if ok:
        data=path.read_bytes()
        ok=data.startswith(b'%PDF') and len(data)==m['bytes'] and hashlib.sha256(data).hexdigest()==m['sha256']
    check('pdf_'+m['id'],ok)
check('six_fulltexts', len(manifest)==6)
spec=importlib.util.spec_from_file_location('capacity_model',ROOT/'tools/capacity_model.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
a=module.capacity(10,5,28000,8,30)
check('bandwidth_units_independent_example',math.isclose(a['offered_mbps'],11.4048,rel_tol=1e-10))
check('unstable_queue_not_reported_as_stable',not a['stable_under_assumptions'] and a['host_wq_ms'] is None)
b=module.capacity(10,2,28000,8,30)
check('queue_formula_independent_example',math.isclose(b['host_wq_ms'],22.5,rel_tol=1e-10))
c=module.capacity(3,2,28000,8,30)
d=module.capacity(3,2,28000,20,30)
check('bandwidth_monotonicity',d['max_fps_link']>c['max_fps_link'])
check('raw_rgb_units',640*480*3*10*10*8/1e6==737.28)
rejected=0
for args in [(0,1,1,1,1),(1,0,1,1,1),(1,1,1,0,1)]:
    try: module.capacity(*args)
    except ValueError: rejected+=1
check('invalid_capacity_inputs_rejected',rejected==3)
sweep=list(csv.DictReader((ROOT/'results/capacity_sweep.csv').open(encoding='utf-8-sig')))
check('capacity_grid_coverage',len(sweep)==4*4*3*3 and {int(r['nodes']) for r in sweep}=={1,3,6,10})
budgets=list(csv.DictReader((ROOT/'results/budget_scenarios.csv').open(encoding='utf-8-sig')))
ten=next(r for r in budgets if r['active_nodes']=='10' and r['host']=='reuse')
check('budget_independent_total',ten['spare_nodes']=='2' and int(ten['total_low'])==12650 and int(ten['total_high'])==28290)
text=(ROOT/'research/02_场景与痛点筛选.md').read_text()
for line in text.splitlines():
    cells=[x.strip() for x in line.split('|')[1:-1]]
    if len(cells)==7:
        try:
            nums=list(map(float,cells[1:]))
        except ValueError: continue
        expected=sum(x*w for x,w in zip(nums[:5],[.25,.20,.25,.20,.10]))
        check('scenario_score_'+cells[0],math.isclose(expected,nums[5],abs_tol=.001))
check('measurement_template_has_no_fabricated_runs',len(list(csv.reader((ROOT/'planning/measurement_template.csv').open())))==1)
report={'scope':'Deliverable integrity and planning arithmetic only; not field validation',
        'checked_on':'2026-10-20','passed':all(c['passed'] for c in checks),'checks':checks}
(ROOT/'results/preflight_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'passed':report['passed'],'checks':len(checks),'failed':[c for c in checks if not c['passed']]},ensure_ascii=False,indent=2))
raise SystemExit(0 if report['passed'] else 1)
