# -*- coding: utf-8 -*-
"""The 3D page's data for the latest proposals (his ask, 6 Oct 2026): ريسبشن ٢ (his pick), ٣, ٢ب, ٢ — the same plans
the 2D sets draw (gen2d's edited PLANS + reception5_options option B), plus the outlines the 3D needs for the
1.80 m / 1.20 m projections. data3d.js stays untouched: it is gen2d's source (the September plans 1-6).
python3 export3d_latest.py  ->  data3d_latest.js"""
import copy, json, math, os
import gen2d as G
import reception5_options as R

ORDER = ['r2', '3', '2b', '2']
LABELS = {'r2': 'ريسبشن ٢', '3': 'ترشيح ٣', '2b': 'ترشيح ٢ب', '2': 'ترشيح ٢'}

def r2_plan():
    p = R.make(next(o for o in R.OPTIONS if o['key'] == 'B'))
    p['no_hoist'] = True                                  # his ask for this proposal: no hoist hatch
    return p

def for_3d(p, title):
    p = copy.deepcopy(p)
    d = p.get('side', 0)
    XR2, C3, P1s = G.rw2(4.05, d), G.sh(G.C2, d), G.sh(G.P1, d)
    L = lambda q: [round(q[0], 4), round(q[1], 4)]
    p['title'] = title + ':' + p['title'].split(':', 1)[1]
    p['ring_f2'] = [L((G.XL, 4.05)), L((XR2, 4.05)), L(C3), L(G.B2), L(G.A)]               # floor 2 outside walls
    p['f2_slab'] = [L((G.XL, 4.05)), L((XR2, 4.05)), L(P1s), L(G.P2), L(G.P3), L(G.B2), L(G.A)]   # slabs from floor 2 up, stair box cut out
    p['core_up'] = [L(C3), L(P1s), L(G.P2), L(G.P3)]                                        # stair box 3 x 6.2 from floor 2 up
    p['well'] = next(r['p'] for r in p['rooms'] if r['n'] == 'منور')
    p['right_off'] = round(math.hypot(G.sh(G.D2, d)[0] - XR2, G.sh(G.D2, d)[1] - 4.05), 4)   # 6 m street windows: offset from the moved corner
    p['f2_area'] = round(G.f2_area(p), 1)
    p['outline3'] = [L(q) for q in p['outline3']]
    for r in p['rows']:
        r.setdefault('dim', '')
        if r['dim'] is None: r['dim'] = ''
    for k in ('cover_note', 'extra_labels'): p.pop(k, None)
    return p

plans = {'r2': for_3d(r2_plan(), 'ترشيح ريسبشن ٢'),
         '3': for_3d(G.PLANS[8], 'ترشيح ٣'),
         '2b': for_3d(G.PLANS[7], 'ترشيح ٢ب'),
         '2': for_3d(G.PLANS[2], 'ترشيح ٢')}
data = {'plans': plans, 'shared': G.SH, 'order': ORDER, 'labels': LABELS}
out = os.path.join(G.S, 'data3d_latest.js')
open(out, 'w', encoding='utf-8').write('window.DATA=' + json.dumps(data, ensure_ascii=False) + ';\n')
print('wrote', out, os.path.getsize(out), 'bytes;', ', '.join(f"{k}: {p['title']}" for k, p in plans.items()))
