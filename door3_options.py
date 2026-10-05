# -*- coding: utf-8 -*-
"""Three ways to give bedroom 3 of proposal 2 its own path from the hall — never through the living room (his ask, 5 Oct 2026).
python3 door3_options.py  ->  2d/doors3.html + 2d/باب-نوم3-اقتراحات.pdf (3 A4 pages, one per option)"""
import copy, os, subprocess
import gen2d as G

GREEN = '#2B8A3E'
W5 = [-5.0, 9.2]            # wall between the living room and bedroom 3 (x = -5.0, up to y 12.6)
W7 = [-8.6, 12.4]           # wall between the hall and the living room (y = 12.4, to x = -5.0)
W6 = [-11.235, 9.2]         # wall between the living room and bedrooms 1 + 2 (y = 9.2)

def tabs(p): return {r['n']: r for r in p['rooms']}, {r['n']: r for r in p['rows']}
def wall_at(p, a): return next(w for w in p['walls'] if w['a'] == a)
def new_wall(p, a, b, ops=()): p['walls'].append({'a': a, 'b': b, 't': 0.12, 'op': list(ops)})
def opening(p, a, u0, u1, k='open'): wall_at(p, a)['op'].append({'u0': u0, 'u1': u1, 'z0': 0, 'z1': 2.1, 'k': k})
def reshape(p, name, pts, dim=None):
    R, W = tabs(p); R[name]['p'] = pts; W[name]['a'] = G.area([G.T(q) for q in pts])
    if dim: W[name]['dim'] = dim
def leaf(p, h, along, out, w=0.9): p['leaves'].append({'h': h, 'along': along, 'out': out, 'w': w})
LV_TAIL = [[-8.6, 12.4], [-8.6, 13.4], [-10.4, 13.4]]          # living room: the old laundry corner, unchanged in every option
HALL_TAIL = [[-5.0, 12.73], [-4.78, 13.71], [-5.38, 13.71], [-5.38, 13.4], [-8.6, 13.4]]

def opt_lobby(p):
    """A 1.0 x 0.9 corner of the living room joins the hall; bedroom 3's door opens off it."""
    reshape(p, 'صالة', [[-11.355, 9.2], [-5.0, 9.2], [-5.0, 11.5], [-6.0, 11.5], [-6.0, 12.4]] + LV_TAIL, '٦.٤ × ٣.٢ + ٢ × ١')
    reshape(p, 'هول', [[-8.6, 12.4], [-6.0, 12.4], [-6.0, 11.5], [-5.0, 11.5]] + HALL_TAIL)
    opening(p, W7, 2.6, 3.6)
    new_wall(p, [-6.0, 11.5], [-6.0, 12.4]); new_wall(p, [-6.0, 11.5], [-5.0, 11.5])
    opening(p, W5, 2.35, 3.25, 'door'); leaf(p, [-5.0, 12.45], [0, -1], [1, 0])
    return (-4.55, 12.0), (-2.7, 11.55), []

def opt_corridor(p):
    """A 1.0 m corridor between the living room and bedroom 3, from the hall down to bedroom 2: bedrooms 2 and 3 open off it."""
    reshape(p, 'صالة', [[-11.355, 9.2], [-6.0, 9.2], [-6.0, 12.4]] + LV_TAIL, '٥.٤ × ٣.٢ + ٢ × ١')
    reshape(p, 'هول', [[-8.6, 12.4], [-6.0, 12.4], [-6.0, 9.2], [-5.0, 9.2]] + HALL_TAIL)
    opening(p, W7, 2.6, 3.6)
    new_wall(p, [-6.0, 9.2], [-6.0, 12.4])
    w6 = wall_at(p, W6)                                              # bedroom 2's door moves 0.2 m right, into the corridor
    for op in w6['op']:
        if abs(op['u0'] - 5.085) < 0.01: op['u0'], op['u1'] = 5.285, 6.185
    for l in p['leaves']:
        if l['h'] == [-6.15, 9.2]: l['h'] = [-5.95, 9.2]
    opening(p, W5, 1.3, 2.2, 'door'); leaf(p, [-5.0, 11.4], [0, -1], [1, 0])
    X, Y = G.FR.X(-5.5), G.FR.Y(10.4)
    lab = f'<text x="{X:.1f}" y="{Y:.1f}" transform="rotate(-90 {X:.1f} {Y:.1f})" text-anchor="middle" dominant-baseline="central" style="fill:#3a414b;font-size:10px">طرقة النوم</text>'
    return (-4.4, 10.95, 0.9), (-2.7, 11.55), [lab]

def opt_foyer(p):
    """A small entry passage cut from bedroom 3 itself (plus a 0.5 x 0.8 corner of the living room); the door is at its end."""
    yc = lambda x: 12.72 + (x + 5.0) * (11.5 - 12.72) / (-0.18 + 5.0)          # the stair box wall above bedroom 3
    reshape(p, 'صالة', [[-11.355, 9.2], [-5.0, 9.2], [-5.0, 11.6], [-5.5, 11.6], [-5.5, 12.4]] + LV_TAIL, '٦.٤ × ٣.٢ + ٢ × ١')
    reshape(p, 'هول', [[-8.6, 12.4], [-5.5, 12.4], [-5.5, 11.6], [-5.0, 11.6], [-5.0, 11.4], [-3.9, 11.4], [-3.9, yc(-3.9)]] + HALL_TAIL)
    R, W = tabs(p); b3 = R['نوم ٣']['p']
    reshape(p, 'نوم ٣', [b3[0], b3[1], b3[2], [-3.9, yc(-3.9)], [-3.9, 11.4], [-5.0, 11.4]])
    opening(p, W7, 3.1, 3.6); opening(p, W5, 2.4, 3.402)
    new_wall(p, [-5.5, 11.6], [-5.5, 12.4]); new_wall(p, [-5.5, 11.6], [-5.0, 11.6])
    new_wall(p, [-5.0, 11.4], [-3.9, 11.4], [{'u0': 0.05, 'u1': 0.95, 'z0': 0, 'z1': 2.1, 'k': 'door'}])
    new_wall(p, [-3.9, 11.4], [-3.9, yc(-3.9)])
    leaf(p, [-4.95, 11.4], [1, 0], [0, -1])
    lab = f'<text x="{G.FR.X(-4.45):.1f}" y="{G.FR.Y(11.95):.1f}" text-anchor="middle" dominant-baseline="central" style="fill:#3a414b;font-size:9px">ممر</text>'
    return (-4.4, 10.95, 0.9), (-2.6, 10.0), [lab]

OPTIONS = [
    ('اقتراح ١: ممر صغير من ركن الصالة', opt_lobby,
     ['بناخد ركن ١ × ٠.٩ م من الصالة ونضمه للطرقة، وباب نوم ٣ يفتح عليه.',
      'تدخل الأوضة من المدخل على طول، من غير ما تعدّي في الصالة.',
      'الصالة بتصغر من ٢١ لـ ٢٠ م²، ونوم ٣ زي ما هي.']),
    ('اقتراح ٢: طرقة لأوض النوم', opt_corridor,
     ['طرقة عرضها ١ م بين الصالة ونوم ٣، من المدخل لحد باب نوم ٢.',
      'نوم ٢ ونوم ٣ الاتنين بيفتحوا على الطرقة، فخصوصية أكتر.',
      'الصالة بتصغر من ٢١ لـ ١٨ م².']),
    ('اقتراح ٣: دخلة من نوم ٣ نفسها', opt_foyer,
     ['بناخد ممر صغير من نوم ٣ نفسها، وركن صغير ٠.٥ × ٠.٨ م من الصالة.',
      'الصالة تقريبًا زي ما هي، والسرير مش باين من باب الأوضة.',
      'نوم ٣ بتصغر من ١٣ لـ ١٢ م².']),
]

def mark(svg, c, lab, extra):
    F = G.FR; X, Y = F.X(c[0]), F.Y(c[1])
    m = (f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{(c[2] if len(c) > 2 else 1.15) * F.s:.1f}" fill="{GREEN}" fill-opacity="0.10" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="6 4"/>'
         f'<text x="{F.X(lab[0]):.1f}" y="{F.Y(lab[1]):.1f}" text-anchor="middle" dominant-baseline="central" style="fill:{GREEN};font-size:12px;font-weight:700">الباب الجديد</text>')
    return svg.replace('</svg>', ''.join(extra) + m + '</svg>')

def build():
    pages = []
    for i, (title, apply, notes) in enumerate(OPTIONS, 1):
        p = copy.deepcopy(G.PLANS[2]); c, lab, extra = apply(p)
        svg = mark(G.flat_svg(p, 3), c, lab, extra)
        foot = f'<div class="foot"><span>ترشيح ٢: باب أوضة نوم ٣ · {G.DATE}</span><span>صفحة {G.ar(i, 0)} من ٣</span></div>'
        pages.append(f'''<div class="page"><div class="hdr"><div><h2>{title}</h2><p class="sub">الدور الثالث (والرابع زيه) · الدايرة الخضرا = الباب الجديد ٠.٩٠ · الأوضة ليها ممر لوحدها من المدخل</p></div><div class="pg">صفحة {G.ar(i, 0)} من ٣</div></div>
<div class="big">{svg}</div>
<div class="fact">{'<br>'.join(notes)}</div>
{foot}</div>''')
    html = '<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>باب نوم ٣</title><style>' + G.CSS + '</style></head><body>' + ''.join(pages) + '</body></html>'
    hp = os.path.join(G.OUT, 'doors3.html'); open(hp, 'w', encoding='utf-8').write(html)
    pdf = os.path.join(G.OUT, 'باب-نوم3-اقتراحات.pdf')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=180)
    print('pdf', os.path.getsize(pdf) if os.path.exists(pdf) else 0)

if __name__ == '__main__':
    build()
