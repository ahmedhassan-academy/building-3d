# -*- coding: utf-8 -*-
"""Five layouts with a LONG reception and 3 bedrooms (his ask, 6 Oct 2026), on the outline of proposal 3:
12 m front 11.70 (1.80 + 1.20 forward), stair 3 x 6.2, same kitchen / bath / light well / flat door / columns.
Each option is a plan dict in the same shape as gen2d's PLANS, so flat_svg draws it exactly like proposals 2, 2b and 3;
the inner walls are built from the room shapes (an edge two rooms share = a wall), the back walls are proposal 3's.
python3 reception5_options.py  ->  2d/reception5.html + 2d/ريسبشن-طويل-٥-ترشيحات.pdf"""
import copy, math, os, subprocess
import gen2d as G

BASE = G.PLANS[8]                                   # proposal 3, the latest he kept
D = BASE['side']
def lw(y): return G.lw(y)
def rw(y): return G.rw2(y, D)                       # the 6 m street wall, 1.20 m out
XL, XR = G.XL, rw(4.05)
C3, P1, P2, P3 = G.sh(G.C2, D), G.sh(G.P1, D), G.P2, G.P3
def CB(x): return P2[1] + (x - P2[0]) * (P1[1] - P2[1]) / (P1[0] - P2[0])   # stair-box wall above the right-hand rooms
NOOK = [(-5.0, 12.73), (-4.784, 13.712), (-5.384, 13.712), (-5.384, 13.4)]   # the corner by the flat door
BACK = {'مطبخ', 'حمام', 'منور'}
BACK_WALLS = [w for w in BASE['walls'] if w['a'][1] >= 13.4 or w['b'][1] >= 13.71]   # kitchen / bath / light well, with their doors and windows
BACK_LEAVES = [l for l in BASE['leaves'] if l['h'][1] == 13.4]                         # kitchen and bath doors
BY0, BD = 5.55, 1.5                                 # balcony 2.5 x 1.5, recessed from the front line (y 4.05) back to y 5.55

def area(p): return G.area([tuple(q) for q in p])
def dist(a, b): return math.hypot(b[0] - a[0], b[1] - a[1])
def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]; L2 = ax * ax + ay * ay
    t = max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L2)) if L2 else 0
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)
def on_segs(p, q, segs, tol=0.035):
    pts = [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t) for t in (0, 0.25, 0.5, 0.75, 1)]
    return all(min(seg_dist(pt, a, b) for a, b in segs) < tol for pt in pts)
def edges(poly): return [(tuple(poly[i]), tuple(poly[(i + 1) % len(poly)])) for i in range(len(poly))]

def outline(bx):
    bx0, bx1 = bx
    return [G.A, (XL, 4.05), (bx0, 4.05), (bx0, BY0), (bx1, BY0), (bx1, 4.05), (XR, 4.05), C3, G.B2]

def inner_walls(polys, ext, doors, opens):
    """Every edge of the new rooms that is not on the outside or on a back wall becomes a wall; edges on one line merge.
    doors = [(hinge, along, out)], 0.90 wide; opens = [(a, b)] spans with no wall (a room open to the next one)."""
    back = [(tuple(w['a']), tuple(w['b'])) for w in BACK_WALLS]
    lines = []
    for poly in polys:
        for p, q in edges(poly):
            if dist(p, q) < 0.02 or on_segs(p, q, ext + back): continue
            u = ((q[0] - p[0]) / dist(p, q), (q[1] - p[1]) / dist(p, q))
            if u[0] < -1e-6 or (abs(u[0]) < 1e-6 and u[1] < 0): p, q, u = q, p, (-u[0], -u[1])
            for ln in lines:
                o, v = ln['o'], ln['u']
                if abs(v[0] * u[1] - v[1] * u[0]) < 1e-3 and abs((p[0] - o[0]) * v[1] - (p[1] - o[1]) * v[0]) < 0.01:
                    t0 = (p[0] - o[0]) * v[0] + (p[1] - o[1]) * v[1]; t1 = (q[0] - o[0]) * v[0] + (q[1] - o[1]) * v[1]
                    ln['iv'].append((min(t0, t1), max(t0, t1))); break
            else: lines.append({'o': p, 'u': u, 'iv': [(0.0, dist(p, q))]})
    walls = []
    for ln in lines:
        iv = sorted(ln['iv']); merged = [list(iv[0])]
        for a, b in iv[1:]:
            if a <= merged[-1][1] + 0.01: merged[-1][1] = max(merged[-1][1], b)
            else: merged.append([a, b])
        o, v = ln['o'], ln['u']; t0 = merged[0][0]
        P = lambda t: [round(o[0] + v[0] * t, 4), round(o[1] + v[1] * t, 4)]
        a, b = P(t0), P(merged[-1][1]); L = dist(a, b); ops = []
        for (s0, s1), (n0, n1) in zip(merged, merged[1:]): ops.append({'u0': s1 - t0, 'u1': n0 - t0, 'z0': 0, 'z1': 2.1, 'k': 'open'})
        def along(pt): return (pt[0] - a[0]) * v[0] + (pt[1] - a[1]) * v[1]
        for h, al, out in doors:
            e = (h[0] + al[0] * 0.9, h[1] + al[1] * 0.9)
            if seg_dist(h, a, b) < 0.03 and seg_dist(e, a, b) < 0.03:
                u0, u1 = sorted((along(h), along(e))); ops.append({'u0': u0, 'u1': u1, 'z0': 0, 'z1': 2.1, 'k': 'door'})
        for s, e in opens:
            if seg_dist(s, a, b) < 0.03 and seg_dist(e, a, b) < 0.03:
                u0, u1 = sorted((along(s), along(e))); ops.append({'u0': max(0, u0), 'u1': min(L, u1), 'z0': 0, 'z1': 2.1, 'k': 'open'})
        walls.append({'a': a, 'b': b, 't': 0.12, 'op': sorted(ops, key=lambda q: q['u0'])})
    return walls

def side_u(y):
    """distance along D2 -> C2 (gen2d's 'right' windows) for a point at height y on the moved 6 m street wall"""
    L = dist(G.D2, G.C2); dy = G.C2[1] - G.D2[1]
    return (y - G.D2[1] - G.NRM[1] * D) * L / dy

def make(op):
    """op: title, sub, rooms [(name, cls, poly, label centre, 'L × W' or '' for no size)], doors, opens, balc (x0, x1),
    front [(x0, x1)], side [(y0, y1)], extra labels [(text, x, y, rot)]"""
    p = copy.deepcopy(BASE)
    bx = op['balc']; out = outline(bx)
    ext = edges(out) + edges([C3, P1, P2, P3])
    rooms = [{'n': n, 'cls': cls, 'p': [list(q) for q in poly]} for n, cls, poly, c, dm in op['rooms']]
    p['rooms'] = rooms + [r for r in BASE['rooms'] if r['n'] in BACK]
    p['rows'] = [{'n': n, 'w': 0, 'h': 0, 'a': area(poly), 'c': list(c), 'lbl': bool(dm), 'dim': dm}
                 for n, cls, poly, c, dm in op['rooms']] + [r for r in BASE['rows'] if r['n'] in BACK]
    p['walls'] = BACK_WALLS + inner_walls([poly for n, cls, poly, c, dm in op['rooms']], ext, op['doors'], op.get('opens', []))
    p['leaves'] = BACK_LEAVES + [{'h': list(h), 'along': list(al), 'out': list(o), 'w': 0.9} for h, al, o in op['doors']]
    p['balc'] = [list(bx)]; p['balc_d'] = BD; p['balc_y0'] = BY0
    p['outline3'] = [list(q) for q in out]
    slide = {'u0': bx[0] + 0.25 - G.A[0], 'u1': bx[1] - 0.25 - G.A[0], 'z0': 0.02, 'z1': 2.25, 'k': 'slide', 'y': BY0}
    p['front'] = [{'u0': x0 - G.A[0], 'u1': x1 - G.A[0], 'z0': 0.9, 'z1': 2.2, 'k': 'win', 'y': 4.05} for x0, x1 in op['front']] + [slide]
    p['right'] = [{'u0': side_u(y0), 'u1': side_u(y1), 'z0': 0.9, 'z1': 2.2, 'k': 'win'} for y0, y1 in op['side']]
    p['extra_labels'] = [{'t': t, 'x': x, 'y': y, 'rot': r} for t, x, y, r in op.get('extra', [])]
    p['title'] = op['title']; p['desc'] = op['sub']
    return p

def check(op, p):
    """the rooms must fill the flat exactly: no gap, no overlap (sum of areas = outline - stair box - kitchen/bath/well)"""
    whole = G.area(outline(op['balc'])) - G.area([C3, P1, P2, P3])
    got = sum(area(r['p']) for r in p['rooms'])
    return whole, got

# ---------------------------------------------------------------- the five options
H = (0, 1); DN = (0, -1); RT = (1, 0); LF = (-1, 0)
OPTIONS = []
L92, L134, R92 = (lw(9.2), 9.2), (lw(13.4), 13.4), (rw(9.2), 9.2)
B3TOP = (-5.0, CB(-5.0))
BAL = (-8.55, -6.05)                                # the balcony stays where it is in proposal 3
def recess(bx): return [(bx[0], 4.05), (bx[0], BY0), (bx[1], BY0), (bx[1], 4.05)]
FRONT_L = [(XL, 4.05), (-8.6, 4.05), (-8.6, 9.2), L92]                          # front-left room of proposal 3
MID = [(-8.6, 4.05)] + recess(BAL) + [(-5.0, 4.05), (-5.0, 9.2), (-8.6, 9.2)]     # front-middle room, with the balcony
CORNER = [(-5.0, 4.05), (XR, 4.05), R92, (-5.0, 9.2)]                           # front-right corner, two streets
RIGHT = [(-5.0, 9.2), R92, P1, B3TOP]                                           # on the 6 m street, under the stair
TAIL = [(-5.0, 12.73)] + NOOK[1:] + [L134]                                      # up to the flat door, then along the kitchen wall
W_CORNER_F, W_CORNER_S, W_RIGHT = (-3.67, -2.17), (6.358, 8.103), (9.342, 10.77)

# 1. proposal 3 without its middle bedroom: the reception runs from the balcony straight back to the kitchen
OPTIONS.append(dict(
    key='A', title='ترشيح ريسبشن ١: من البلكونة للمطبخ في النص',
    sub='الريسبشن في نص الشقة، طوله ٩.٤ م من البلكونة لحد المطبخ، والتلات أوض بيفتحوا عليه',
    rooms=[('ريسبشن', 'c-amber', [(-8.6, 4.05)] + recess(BAL) + [(-5.0, 4.05)] + TAIL + [L92, (-8.6, 9.2)], (-7.25, 11.25), '٩.٤ × ٤.٢'),
           ('نوم ١', 'c-blue', FRONT_L, (-10.0, 7.3), '٣.٤ × ٥.٢'),
           ('نوم ٢', 'c-blue', CORNER, (-2.7, 6.5), '٤.٨ × ٥.٢'),
           ('نوم ٣', 'c-blue', RIGHT, (-2.738, 10.656), '٥.٧ × ٢.٨')],
    doors=[((-10.6, 9.2), RT, DN), ((-5.0, 9.15), DN, RT), ((-5.0, 11.4), DN, RT)],
    balc=BAL, front=[(-11.5, -10.1), (-5.8, -5.2), W_CORNER_F], side=[W_CORNER_S, W_RIGHT],
    notes=['شلنا نوم ٢ اللي في النص ودخلناها في الصالة: الريسبشن بقى ماشي من البلكونة لحد المطبخ.',
           'الضيوف يدخلوا من باب الشقة على الريسبشن على طول، والتلات أوض بيفتحوا عليه من غير ممر.',
           'البلكونة بقت في الريسبشن مكانها زي ما هي. في عمود ٣٠ × ٣٠ في نص الريسبشن عند خط الأوض (بيتغطى بديكور).']))

B_WALL, B_LOB = 8.65, 7.6                           # his edit (6 Oct): bedroom 3 = 19 m2 from bedroom 2; the lobby reaches bedroom 2's new door
# 2. proposal 3 without its front-left bedroom: the reception runs along the neighbour wall
OPTIONS.append(dict(
    key='B', title='ترشيح ريسبشن ٢: على حيطة الجار',
    sub='الريسبشن ماشي على حيطة الجار الشمال، طوله ٩.٤ م من شباك شارع ١٢ لحد المطبخ',
    rooms=[('ريسبشن', 'c-amber', [(XL, 4.05), (-8.6, 4.05), (-8.6, 9.2), (-5.0, 9.2)] + TAIL, (-8.2, 11.3), '٩.٤ × ٤.٥'),
           ('نوم ١', 'c-blue', [(-8.6, 4.05)] + recess(BAL) + [(-5.0, 4.05), (-5.0, B_LOB), (-6.0, B_LOB), (-6.0, 9.2), (-8.6, 9.2)], (-7.3, 7.6), '٣.٦ × ٥.٢'),
           ('دخلة', 'c-gray', [(-6.0, B_LOB), (-5.0, B_LOB), (-5.0, 9.2), (-6.0, 9.2)], (-5.5, 8.4), ''),
           ('نوم ٢', 'c-blue', [(-5.0, 4.05), (XR, 4.05), (rw(B_WALL), B_WALL), (-5.0, B_WALL)], (-2.7, 6.3), '٤.٨ × ٤.٦'),
           ('نوم ٣', 'c-blue', [(-5.0, B_WALL), (rw(B_WALL), B_WALL), P1, B3TOP], (-2.6, 10.35), '٥.٧ × ٣.٣')],
    doors=[((-6.0, 9.15), DN, LF), ((-5.0, B_WALL - 0.05), DN, RT), ((-5.0, 11.4), DN, RT)],
    opens=[((-6.0, 9.2), (-5.0, 9.2))],
    balc=BAL, front=[(-11.9, -9.3), W_CORNER_F], side=[W_CORNER_S, W_RIGHT],
    notes=['شلنا نوم ١ اللي على الشمال ودخلناها في الصالة: الريسبشن بقى ماشي على حيطة الجار من الشباك لحد المطبخ.',
           'شباك الريسبشن على شارع ١٢ بقى ٢.٦ م علشان النور يكفي المساحة. البلكونة في نوم ١ زي ما هي.',
           'تعديل ٦ أكتوبر: نوم ٣ كبرت لـ ١٩ م² من نوم ٢ (الحيطة اللي بينهم نزلت ٥٥ سم)، والدخلة طالت لـ ١ × ١.٦ علشان باب نوم ٢، فنوم ١ بقت ≈ ١٣.',
           'نوم ١ ونوم ٢ بيفتحوا على الدخلة، ونوم ٣ على الريسبشن. عمود حيطة شارع ٦ القديمة بقى جوه نوم ٣.']))

# 3. proposal 3 without its bedroom on the 6 m street: the reception runs across, from the kitchen to the 6 m street
OPTIONS.append(dict(
    key='C', title='ترشيح ريسبشن ٣: بالعرض لحد شارع ٦',
    sub='الريسبشن بالعرض ورا الأوض، طوله ١١.٩ م من المطبخ لحد شباك شارع ٦، والتلات أوض على شارع ١٢',
    rooms=[('ريسبشن', 'c-amber', [L92, R92, P1] + TAIL, (-6.2, 11.0), '١١.٩ × ٣.٤'),
           ('نوم ١', 'c-blue', FRONT_L, (-10.0, 7.3), '٣.٤ × ٥.٢'),
           ('نوم ٢', 'c-blue', MID, (-6.8, 7.6), '٣.٦ × ٥.٢'),
           ('نوم ٣', 'c-blue', CORNER, (-2.7, 6.5), '٤.٨ × ٥.٢')],
    doors=[((-10.6, 9.2), RT, DN), ((-7.9, 9.2), RT, DN), ((-4.9, 9.2), RT, DN)],
    balc=BAL, front=[(-11.5, -10.1), W_CORNER_F], side=[W_CORNER_S, (9.4, 11.05)],
    notes=['شلنا نوم ٣ اللي على شارع ٦ ودخلناها في الصالة: الريسبشن بقى بالعرض من المطبخ لحد شارع ٦.',
           'التلات أوض جنب بعض على شارع ١٢ وأبوابهم على الريسبشن، من غير ممر ولا دخلة.',
           'نور الريسبشن من شباك واحد طويل على شارع ٦، فناحية المطبخ هتبقى أضلم شوية. البلكونة في نوم ٢.']))

# 4. like 2, but the bedrooms get their own corridor with a door, away from the guests
OPTIONS.append(dict(
    key='D', title='ترشيح ريسبشن ٤: على حيطة الجار + طرقة للنوم',
    sub='زي ترشيح ٢، بس الأوض ليها طرقة لوحدها بباب، والضيوف مايشوفوش أبواب الأوض',
    rooms=[('ريسبشن', 'c-amber', [(XL, 4.05), (-8.6, 4.05), (-8.6, 9.2), (-6.0, 9.2), (-6.0, 12.4), (-5.0, 12.4)] + TAIL, (-8.2, 11.3), '٩.٤ × ٤.١'),
           ('نوم ١', 'c-blue', [(-8.6, 4.05)] + recess(BAL) + [(-5.0, 4.05), (-5.0, 8.2), (-6.0, 8.2), (-6.0, 9.2), (-8.6, 9.2)], (-7.3, 7.6), '٣.٦ × ٥.٢'),
           ('طرقة', 'c-gray', [(-6.0, 8.2), (-5.0, 8.2), (-5.0, 12.4), (-6.0, 12.4)], (-5.5, 10.6), ''),
           ('نوم ٢', 'c-blue', CORNER, (-2.7, 6.5), '٤.٨ × ٥.٢'),
           ('نوم ٣', 'c-blue', RIGHT, (-2.738, 10.656), '٥.٧ × ٢.٨')],
    doors=[((-5.95, 12.4), RT, DN), ((-6.0, 9.15), DN, LF), ((-5.0, 9.15), DN, RT), ((-5.0, 11.4), DN, RT)],
    balc=BAL, front=[(-11.9, -9.3), W_CORNER_F], side=[W_CORNER_S, W_RIGHT],
    notes=['زي ترشيح ٢: الريسبشن على حيطة الجار من الشباك لحد المطبخ.',
           'الجديد: طرقة عرضها ١ م من عند باب الشقة لحد الأوض، عليها باب. التلات أوض بيفتحوا عليها، فالنوم بعيد عن الضيوف.',
           'الريسبشن بيصغر حوالي ٣ م² علشان الطرقة. البلكونة في نوم ١ زي ما هي.']))

# 5. like 4, but the reception also wraps round towards the corner along the 6 m street: the biggest and brightest one
Y7 = 7.0
OPTIONS.append(dict(
    key='E', title='ترشيح ريسبشن ٥: بالعرض ولافف على شارع ٦',
    sub='زي ترشيح ٤، بس الريسبشن لافف كمان على شارع ٦ ناحية الركن، فبقى أكبر وشبابيكه أطول',
    rooms=[('ريسبشن', 'c-amber', [L92, (-5.0, 9.2), (-5.0, Y7), (rw(Y7), Y7), P1] + TAIL, (-6.2, 11.0), '١١.٩ × ٤.٤'),
           ('نوم ١', 'c-blue', FRONT_L, (-10.0, 7.3), '٣.٤ × ٥.٢'),
           ('نوم ٢', 'c-blue', MID, (-6.8, 7.6), '٣.٦ × ٥.٢'),
           ('نوم ٣', 'c-blue', [(-5.0, 4.05), (XR, 4.05), (rw(Y7), Y7), (-5.0, Y7)], (-3.2, 4.85), '٤.٥ × ٣')],
    doors=[((-10.6, 9.2), RT, DN), ((-7.9, 9.2), RT, DN), ((-4.2, Y7), RT, DN)],
    balc=BAL, front=[(-11.5, -10.1), W_CORNER_F], side=[(4.9, 6.6), (7.4, 8.8), (9.6, 11.0)],
    notes=['زي ترشيح ٤: الريسبشن بالعرض من المطبخ لحد شارع ٦، بس كمان لافف ناحية الركن على شارع ٦.',
           'ده أكبر ريسبشن (≈ ٥٢ م²) وأنور واحد: شباكين على شارع ٦. التلات أوض على شارع ١٢ وأبوابهم عليه.',
           'التمن: نوم ٣ اللي في الركن بتصغر لـ ≈ ١٣ م². وفي عمود ٣٠ × ٣٠ جوه الريسبشن قريب من شباك شارع ٦.']))

ORDER = ['A', 'B', 'D', 'C', 'E']                    # the two "along the neighbour" ones together, then the two "across" ones
NAMES = {'A': '١', 'B': '٢', 'D': '٣', 'C': '٤', 'E': '٥'}
OPTIONS.sort(key=lambda o: ORDER.index(o['key']))
for o in OPTIONS:
    o['title'] = 'ترشيح ريسبشن ' + NAMES[o['key']] + ':' + o['title'].split(':', 1)[1]
    o['notes'] = [n.replace('زي ترشيح ٢', 'زي ترشيح ريسبشن ٢').replace('زي ترشيح ٤', 'زي ترشيح ريسبشن ٤') for n in o['notes']]
    o['sub'] = o['sub'].replace('زي ترشيح ٢', 'زي ترشيح ريسبشن ٢').replace('زي ترشيح ٤', 'زي ترشيح ريسبشن ٤')

def pages_html():
    pages = []; N = len(OPTIONS)
    for i, op in enumerate(OPTIONS, 1):
        p = make(op)
        rooms = [(n, area(poly)) for n, cls, poly, c, dm in op['rooms'] if dm]
        net = sum(area(r['p']) for r in p['rooms'] if r['n'] != 'منور')
        facts = ' · '.join(f'{n} ≈ {G.ar(a, 0)} م²' for n, a in rooms)
        pages.append(f'''<div class="page"><div class="hdr"><div><h1>{op["title"]}</h1><p class="sub">{op["sub"]} · الدور الثالث (والرابع زيه)</p></div><div class="pg">{G.ar(i, 0)} من {G.ar(N, 0)}</div></div>
<div class="big">{G.flat_svg(p, 3)}</div>
<div class="fact"><b>المساحات:</b> {facts} · مطبخ ≈ ١٠ · حمام ≈ ٣ · <b>الصافي ≈ {G.ar(net, 0)} م²</b></div>
<div class="fact">{'<br>'.join(op['notes'])}</div>
<div class="foot"><span>ريسبشن طويل + ٣ أوض نوم · ٦ أكتوبر ٢٠٢٦</span><span>صفحة {G.ar(i, 0)} من {G.ar(N, 0)}</span></div></div>''')
    return pages

def build():
    html = '<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>ريسبشن طويل</title><style>' + G.CSS + '</style></head><body>' + ''.join(pages_html()) + '</body></html>'
    hp = os.path.join(G.OUT, 'reception5.html'); open(hp, 'w', encoding='utf-8').write(html)
    pdf = os.path.join(G.OUT, 'ريسبشن-طويل-٥-ترشيحات.pdf')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=180)
    print('pdf', os.path.getsize(pdf) if os.path.exists(pdf) else 0)
    return pdf

if __name__ == '__main__':
    for op in OPTIONS:
        p = make(op); w, g = check(op, p); print(op['key'], f'outline {w:.2f}  rooms {g:.2f}  diff {w - g:+.2f}',
              ' | '.join(f'{n} {area(poly):.1f}' for n, cls, poly, c, dm in op['rooms']))
    build()
