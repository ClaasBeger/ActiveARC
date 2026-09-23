"""Build experiments/active_trials.html: full active-discovery trials, plain versus harness, step by step."""
import json, glob
from pipelines.run_static_batch import load_official
from framework.tasks.eval_items import sampled_item
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
def rect(g): return isinstance(g, list) and g and all(isinstance(x, list) and x and len(x) == len(g[0]) for x in g)

ARMS = [('Plain DeepSeek', 'dstest_ca20_off_c40k', False), ('Harness: fresh readers', 'dstest_ca20_selfread_c40k', True)]
R = {lab: recs(d) for lab, d, _ in ARMS}
stat = recs('static_ca160_ds41f_br')
ids = open(J + 'ca20_ds.txt').read().replace('--task-id', '').split()

def trial(r):
    hs = r['trial']['hot_start_pair']
    steps = [{'kind': 'hot', 'i': hs['input'], 'o': hs['output']}]
    for t in r['transcript']:
        if t.get('phase') == 'test': continue
        for call, res in zip(t.get('tool_calls', []), t.get('tool_results', [])):
            name = call.get('name'); out = res.get('result', {})
            if name == 'submit_query':
                try: g = json.loads(call.get('arguments') or '{}').get('grid')
                except Exception: g = None
                if not rect(g): continue
                if out.get('held'):
                    steps.append({'kind': 'held', 'i': g, 'why': (out.get('error') or '')[:160]})
                elif not out.get('ok'):
                    steps.append({'kind': 'refused', 'i': g, 'why': (out.get('error') or '')[:120]})
                else:
                    rd = out.get('readings') or {}
                    flags = []
                    if dist(g, hs['input']) < 0.15: flags.append('near-copy of hot start')
                    if g == out.get('output_grid'): flags.append('no-op')
                    steps.append({'kind': 'query', 'i': g, 'o': out.get('output_grid'), 'flags': flags,
                                  'readings': f"{rd.get('n_right')}/{rd.get('n')} readings right, {rd.get('n_distinct')} distinct" if rd else None})
            elif name in ('request_test', 'finish_exploration') and out.get('ok'):
                steps.append({'kind': 'test_start'})
    answers = {}
    for t in r['transcript']:
        if t.get('phase') != 'test': continue
        for call in t.get('tool_calls', []):
            if call.get('name') == 'submit_final_answer':
                try: g = json.loads(call.get('arguments') or '{}').get('grid')
                except Exception: g = None
                answers.setdefault(t.get('test_item'), g)
    return steps, answers

rows = []
for t in ids:
    if not all(t in R[lab] for lab, _, _ in ARMS): continue
    task = load_official('conceptarc', t)
    items = list(zip(task.test_inputs, task.test_outputs))
    si = sampled_item('conceptarc', 0, t)
    if si: items.append(si)
    row = {'task': t, 'official': [{'i': p.input, 'o': p.output} for p in task.train_pairs], 'static_ok': bool((stat.get(t) or {}).get('correct')), 'arms': []}
    for lab, d, harness in ARMS:
        r = R[lab][t]; steps, ans = trial(r)
        corr = r.get('test_item_correct') or []
        tests = [{'i': ti, 'gold': to, 'ans': ans.get(k), 'ok': bool(corr[k]) if k < len(corr) else None} for k, (ti, to) in enumerate(items)]
        row['arms'].append({'label': lab, 'harness': harness, 'steps': steps, 'tests': tests, 'ok': bool(r.get('correct')),
                            'runaway': (r.get('final') or {}).get('reason') == 'reasoning_runaway',
                            'items': f"{sum(bool(x) for x in corr)}/{len(corr)}"})
    rows.append(row)
tpl = open('experiments/active_trials_template.html').read()
open('experiments/active_trials.html', 'w').write(tpl.replace('/*DATA*/null', json.dumps(rows, separators=(',', ':'))))
print('tasks', len(rows))
