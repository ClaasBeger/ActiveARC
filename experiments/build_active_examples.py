"""Build experiments/active_examples.html: what the models author, with and without the harness."""
import json, glob, os
from pipelines.run_static_batch import load_official
from framework.grids import normalized_cell_edit_or_shape_mismatch as dist

J = '/Users/claasbeger/.claude/jobs/ba92c5b5/tmp/'
def recs(d):
    out = {}
    for f in glob.glob(f'experiments/runs/{d}/*.json'):
        if 'manifest' in f or 'summary' in f: continue
        try: r = json.load(open(f))
        except Exception: continue
        if 'task_id' in r and 'error' not in r: out[r['task_id']] = r
    return out
def ok(R, t):
    r = R.get(t)
    return None if r is None else bool(r.get('correct'))
def pairs_from_demos(r):
    return [{'i': p['input'], 'o': p['output']} for p in (r or {}).get('demonstrations', [])]

# ---------- teacher ----------
ids40 = open(J + 'ca40_std.txt').read().replace('--task-id', '').split()
arms_t = [('Official examples', None), ('Plain DeepSeek teacher', 'teachds_ca40std_off'),
          ('Harness: own rival rules', 'teachds_ca40std_advisory'), ('Harness: fresh-reader probes', 'teachds_ca40std_selfprobe')]
scor = {'ds': {'Official examples': recs('static_ca160_ds41f_br')}, 'g38': {'Official examples': recs('static_ca160_g38_br')}}
for lab, d in arms_t[1:]:
    for s in ('ds', 'g38'):
        scor[s][lab] = recs(f'{d}_scored_{s}')
demos = {lab: recs(d) for lab, d in arms_t[1:]}
teacher = []
for t in ids40:
    if not all(t in demos[lab] for lab in demos if lab != 'Harness: fresh-reader probes'): continue
    task = load_official('conceptarc', t)
    row = {'task': t, 'arms': []}
    for lab, d in arms_t:
        ps = [{'i': p.input, 'o': p.output} for p in task.train_pairs] if d is None else pairs_from_demos(demos[lab].get(t))
        if d is not None and t not in demos[lab]: ps = None
        row['arms'].append({'label': lab, 'pairs': ps, 'ds': ok(scor['ds'][lab], t), 'g38': ok(scor['g38'][lab], t)})
    diff = len({(a['ds'], a['g38']) for a in row['arms'] if a['pairs'] is not None})
    row['interest'] = diff + (2 if row['arms'][3]['pairs'] else 0)
    teacher.append(row)
teacher.sort(key=lambda r: -r['interest'])
teacher = teacher[:8]

# ---------- student ----------
ids20 = open(J + 'ca20_ds.txt').read().replace('--task-id', '').split()
arms_s = [('Plain DeepSeek student', 'dstest_ca20_off_c40k'), ('Harness: fresh readers', 'dstest_ca20_selfread_c40k'),
          ('Harness: symmetry images', 'dstest_ca20_symmetry_c16k'), ('Harness: redundancy hold', 'dstest_ca20_diverse_c16k')]
S = {lab: recs(d) for lab, d in arms_s}
stat = recs('static_ca160_ds41f_br')
student = []
for t in ids20:
    if t not in S['Plain DeepSeek student']: continue
    task = load_official('conceptarc', t)
    row = {'task': t, 'official': [{'i': p.input, 'o': p.output} for p in task.train_pairs], 'static_ok': ok(stat, t), 'arms': []}
    for lab, _ in arms_s:
        r = S[lab].get(t)
        if r is None: row['arms'].append({'label': lab, 'pairs': None}); continue
        tr = r['trial']; hs = tr['hot_start_pair']
        ps = [{'i': hs['input'], 'o': hs['output'], 'tag': 'hot start'}]
        for q in tr['query_history']:
            if q.get('input') is None or q.get('output') is None: continue
            tags = []
            if dist(q['input'], hs['input']) < 0.15: tags.append('near-copy')
            if q['input'] == q['output']: tags.append('no-op')
            ps.append({'i': q['input'], 'o': q['output'], 'tag': ', '.join(tags) or 'query'})
        items = r.get('test_item_correct') or []
        row['arms'].append({'label': lab, 'pairs': ps, 'ok': bool(r.get('correct')), 'items': f"{sum(bool(x) for x in items)}/{len(items)}",
                            'runaway': (r.get('final') or {}).get('reason') == 'reasoning_runaway'})
    row['interest'] = len({a.get('ok') for a in row['arms'] if a['pairs']}) + (1 if row['arms'][1]['pairs'] else 0)
    student.append(row)
student.sort(key=lambda r: -r['interest'])
student = student[:7]

data = json.dumps({'teacher': teacher, 'student': student}, separators=(',', ':'))
tpl = open('experiments/active_examples_template.html').read()
open('experiments/active_examples.html', 'w').write(tpl.replace('/*DATA*/null', data))
print('teacher rows', len(teacher), 'student rows', len(student), 'bytes', len(data))
