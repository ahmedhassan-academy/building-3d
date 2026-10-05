# -*- coding: utf-8 -*-
"""Three ways to give bedroom 3 of proposal 2 a door (his ask, 5 Oct 2026).
python3 door3_options.py  ->  2d/doors3.html + 2d/باب-نوم3-اقتراحات.pdf (3 A4 pages, one per option)"""
import copy, os, subprocess
import gen2d as G

GREEN = '#2B8A3E'
W5 = [-5.0, 9.2]                       # start of the wall between the living room / hall and bedroom 3 (runs up to y 12.6)

def add_door(p, y0, y1, hinge_top):
    """0.90 door in the x = -5.0 wall, opening into bedroom 3."""
    w = next(w for w in p['walls'] if w['a'] == W5)
    w['op'].append({'u0': y0 - 9.2, 'u1': y1 - 9.2, 'z0': 0, 'z1': 2.1, 'k': 'door'})
    h = [-5.0, y1] if hinge_top else [-5.0, y0]
    p['leaves'].append({'h': h, 'along': [0, -1] if hinge_top else [0, 1], 'out': [1, 0], 'w': round(y1 - y0, 2)})
    return (-4.55, (y0 + y1) / 2)

def lobby(p):
    """Take a 1.0 x 0.9 corner of the living room and add it to the hall, so bedroom 3 opens off the hall."""
    R = {r['n']: r for r in p['rooms']}; W = {r['n']: r for r in p['rows']}
    lv = R['صالة']['p']; hl = R['هول']['p']
    R['صالة']['p'] = lv[:2] + [[-5.0, 11.5], [-6.0, 11.5], [-6.0, 12.4]] + lv[3:]
    R['هول']['p'] = [hl[0], [-6.0, 12.4], [-6.0, 11.5], [-5.0, 11.5]] + hl[2:]
    W['صالة'].update(a=G.area([G.T(q) for q in R['صالة']['p']]), dim='٦.٤ × ٣.٢ + ٢ × ١ − ١ × ٠.٩')
    W['هول']['a'] = G.area([G.T(q) for q in R['هول']['p']])
    w7 = next(w for w in p['walls'] if w['a'] == [-8.6, 12.4] and w['b'][1] == 12.4)
    w7['op'].append({'u0': 2.6, 'u1': 3.6, 'z0': 0, 'z1': 2.1, 'k': 'open'})     # the old hall wall opens over the new corner
    p['walls'] += [{'a': [-6.0, 11.5], 'b': [-6.0, 12.4], 't': 0.12, 'op': []},
                   {'a': [-6.0, 11.5], 'b': [-5.0, 11.5], 't': 0.12, 'op': []}]

def mark(svg, c, lab):
    F = G.FR; X, Y = F.X(c[0]), F.Y(c[1])
    m = (f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{1.15 * F.s:.1f}" fill="{GREEN}" fill-opacity="0.10" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="6 4"/>'
         f'<text x="{F.X(lab[0]):.1f}" y="{F.Y(lab[1]):.1f}" text-anchor="middle" dominant-baseline="central" style="fill:{GREEN};font-size:12px;font-weight:700">الباب الجديد</text>')
    return svg.replace('</svg>', m + '</svg>')

OPTIONS = [
    ('اقتراح ١: باب من الصالة، فوق جنب الطرقة',
     lambda p: add_door(p, 11.4, 12.3, True), (-2.7, 11.55),
     ['الباب في الحيطة اللي بين الصالة ونوم ٣، في الحتة اللي جنب الطرقة.',
      'مفيش ولا متر بيضيع: الصالة ٢١ م² ونوم ٣ زي ما هي.',
      'العيب: اللي قاعد في الصالة بيشوف باب الأوضة.']),
    ('اقتراح ٢: باب من الصالة، تحت جنب باب نوم ٢',
     lambda p: add_door(p, 9.35, 10.25, False), (-2.9, 9.6),
     ['الباب في نفس الحيطة، بس في الركن اللي تحت جنب باب نوم ٢.',
      'مفيش ولا متر بيضيع، وأبواب أوض النوم كلها بقت في ناحية واحدة من الصالة.',
      'العيب: اللي قاعد في الصالة بيشوف الباب، وفيه بابين جنب بعض في الركن.']),
    ('اقتراح ٣: باب من الطرقة',
     lambda p: (lobby(p), add_door(p, 11.55, 12.45, True))[1], (-2.7, 11.55),
     ['بناخد ركن صغير ١ × ٠.٩ م من الصالة ونضمه للطرقة، والباب يفتح منه.',
      'الأوضة بتتدخل من المدخل على طول من غير ما تعدّي في الصالة، فيه خصوصية أكتر.',
      'العيب: الصالة بتصغر حوالي ١ م² (من ٢١ لـ ٢٠ م²).']),
]

def build():
    pages = []
    for i, (title, apply, lab, notes) in enumerate(OPTIONS, 1):
        p = copy.deepcopy(G.PLANS[2]); c = apply(p)
        svg = mark(G.flat_svg(p, 3), c, lab)
        foot = f'<div class="foot"><span>ترشيح ٢: باب أوضة نوم ٣ · {G.DATE}</span><span>صفحة {G.ar(i, 0)} من ٣</span></div>'
        pages.append(f'''<div class="page"><div class="hdr"><div><h2>{title}</h2><p class="sub">الدور الثالث (والرابع زيه) · الدايرة الخضرا = الباب الجديد ٠.٩٠، بيفتح لجوه الأوضة</p></div><div class="pg">صفحة {G.ar(i, 0)} من ٣</div></div>
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
