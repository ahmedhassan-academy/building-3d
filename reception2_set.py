# -*- coding: utf-8 -*-
"""The building set for "ترشيح ريسبشن ٢" (his pick, 6 Oct 2026), as he asked for it:
land plan first, then the cover, warehouse floors 1-2, flats on floors 3-4, and one page with the 13 columns,
the distance between every two neighbouring columns, and each column's size and steel.
(The old column-sections and warehouse-stair pages are left out: "مش مهمين".)
python3 reception2_set.py  ->  2d/set9.html + 2d/ترشيح-ريسبشن-٢.pdf"""
import math, os
import gen2d as G
import reception5_options as R

K = 9
G.DATE = '٦ أكتوبر ٢٠٢٦'                             # this set is made today; gen2d's other sets keep their date
LAND_PDF = os.path.join(G.OUT, 'مخطط-الأرض.pdf')     # one landscape A4 page, goes first
p = R.make(next(o for o in R.OPTIONS if o['key'] == 'B'))
p['cover_note'] = ('ريسبشن طويل ٩.٤ م على حيطة الجار الشمال، من البلكونة على شارع ١٢ لحد المطبخ (≈ ٣٨ م²)، '
                   'والبلكونة ٢.٥ × ١.٥ فيه وبابها ٢ م · نوم ١ (≈ ١٧) ونوم ٢ في الركن على الشارعين (≈ ٢٢) بيفتحوا على دخلة ١ × ١.٦ من الريسبشن، '
                   'ونوم ٣ على شارع ٦ (≈ ١٩) بتفتح على الريسبشن · المطبخ والحمام والمنور والسلم وباب الشقة زي ترشيح ٣.')
p['no_hoist'] = True                                  # his ask (6 Oct): no hoist hatch in the floor-2 slab

# ---------------- the columns page: every pair of neighbouring columns with the distance between their centres
COLS = [tuple(c[:2]) for c in p['cols_out']] + [tuple(c) for c in p['cols_in']]
A_, B2_, P3_, C2_, P1_, D2_, F_, L1_, L2_, R1_, BK_, P2_, IN_ = COLS
OUTER = [(A_, F_), (F_, D2_), (D2_, R1_), (R1_, P1_), (P1_, C2_), (C2_, P3_), (P3_, BK_), (BK_, B2_), (B2_, L2_), (L2_, L1_), (L1_, A_)]
INNER = [(L1_, IN_), (IN_, R1_), (F_, IN_), (IN_, BK_), (L2_, P2_)]
STAIR = [(P2_, P1_), (P2_, P3_)]                   # the stair box's two inner sides: labels go outside the box
def dist(a, b): return math.hypot(b[0] - a[0], b[1] - a[1])
LONGEST = max(OUTER + INNER, key=lambda s: dist(*s))

def label(F, t, x, y, rot, color, size=11):
    X, Y = F.X(x), F.Y(y)
    return (f'<text x="{X:.1f}" y="{Y:.1f}" text-anchor="middle" dominant-baseline="central" transform="rotate({rot:.1f} {X:.1f} {Y:.1f})" '
            f'style="fill:{color};font-size:{size}px;font-weight:700;stroke:#ffffff;stroke-width:3.5px;paint-order:stroke">{t}</text>')

def columns_plan_svg():
    F = G.FR; o = [G.svg_open(title='العمدان والمسافات')] + G.site(F)
    d = p['side']
    upper = [(G.XL, 4.05), (G.rw2(4.05, d), 4.05), G.sh(G.C2, d), G.B2, G.A]
    o.append(G.poly(F, upper, fill='#f6f7f9', stroke='#9AA1AB', sw=1, dash='5 4'))
    o.append(G.poly(F, G.BLD, fill='#ffffff', stroke='#1d2126', sw=1.4))
    o.append(G.poly(F, G.CORE, fill=G.CLS['c-teal'][0], stroke=G.CLS['c-teal'][1], sw=1))
    o.append(G.text(F, 'بيت السلم', *G.cp(2.5, 1.5), cls='ts', rot=G.rot_along(G.P1, G.P2), fill='#2A8C8C'))
    cx = sum(q[0] for q in G.BLD) / len(G.BLD); cy = sum(q[1] for q in G.BLD) / len(G.BLD)
    sx = sum(q[0] for q in G.CORE) / 4; sy = sum(q[1] for q in G.CORE) / 4
    for a, b in OUTER + INNER + STAIR:
        o.append(G.line(F, a, b, '#8A4B12', 2.2))
    for a, b in OUTER + INNER + STAIR:
        L = dist(a, b); t = 0.35 if (a, b) == LONGEST else 0.5        # the long one sits clear of the beam that crosses it
        m = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        n = (-(b[1] - a[1]) / L, (b[0] - a[0]) / L)
        if (a, b) in INNER:                                 # beside the beam: above a level one, right of an upright one
            if (abs(n[1]) >= abs(n[0]) and n[1] < 0) or (abs(n[1]) < abs(n[0]) and n[0] < 0): n = (-n[0], -n[1])
            off = 0.3
        else:                                               # outside the wall / outside the stair box
            ox, oy = (cx, cy) if (a, b) in OUTER else (sx, sy)
            if (m[0] + n[0] - ox) ** 2 + (m[1] + n[1] - oy) ** 2 < (m[0] - n[0] - ox) ** 2 + (m[1] - n[1] - oy) ** 2: n = (-n[0], -n[1])
            off = 0.42
        m = (m[0] + n[0] * off, m[1] + n[1] * off)
        o.append(label(F, f'{G.ar(L, 2)} م', *m, G.rot_along(a, b), '#B3261E' if (a, b) == LONGEST else '#8A4B12'))
    o += G.columns(F, p, 1)
    o.append(G.text(F, 'حدود الأدوار اللي فوق (البروز ١.٨٠ و ١.٢٠ م)', -7.0, 4.45, cls='ts', fill='#5b6472'))
    o.append(G.text(F, 'شارع ١٢ م', -7.0, 2.6, cls='t', fill='#5b6472'))
    o.append(G.text(F, 'شارع ٦ م', 2.6, 8.6, cls='t', rot=G.rot_along(G.D2, G.C2), fill='#5b6472'))
    leg = [(G.COL_WALL, '■ عمود في الحيطة (٨)'), (G.COL_CORE, '■ ركن بيت السلم (٤)'), (G.COL_IN, '■ عمود جوه المخزن (١)'),
           ('#8A4B12', '▬ المسافة من نص العمود لنص العمود')]
    x = 668
    for color, t in leg:
        o.append(f'<text x="{x}" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="{color}" font-weight="700">{t}</text>'); x -= 150
    o.append('</svg>')
    return '\n'.join(o)

def columns_page(hdr, foot, i):
    rows = [('في الحيطان الخارجية', '٨', '٢٥ × ٧٠ — ٨ أسياخ ١٦ مم', '٢٥ × ٦٠ — ٦ أسياخ ١٦ مم'),
            ('أركان بيت السلم', '٤', '٤٠ × ٤٠ — ٨ أسياخ ١٦ مم', '٣٠ × ٣٠ — ٤ أسياخ ١٦ مم'),
            ('جوه المخزن', '١', '٤٠ × ٤٠ — ٨ أسياخ ١٦ مم', '٣٠ × ٣٠ — ٤ أسياخ ١٦ مم')]
    tr = ''.join(f'<tr><td>{a}</td><td class="n">{b}</td><td class="n">{c}</td><td class="n">{d}</td></tr>' for a, b, c, d in rows)
    a, b = LONGEST
    return f'''<div class="page">{hdr('العمدان والمسافات اللي بينهم', 'ترشيح ريسبشن ٢ · نفس العمدان في الأربع أدوار · المسافة من نص العمود لنص العمود', i)}
<div class="big">{columns_plan_svg()}</div>
<table><tr><th>العمود</th><th class="n">العدد</th><th class="n">المخزن (الدور ١ و ٢)</th><th class="n">الشقق (الدور ٣ و ٤)</th></tr>{tr}</table>
<div class="fact"><b>الكانات:</b> حديد ٨ مم كل ١٥ سم، وكل ١٠ سم عند السقف والأرض. العمود ٤٠ × ٤٠ بياخد كانة صغيرة جوه الكانة الكبيرة · <b>أطول مسافة:</b> {G.ar(dist(a, b), 2)} م بين العمود اللي جوه المخزن والعمود اللي في الحيطة اللي ورا · البروز ١.٨٠ م على شارع ١٢ و ١.٢٠ م على شارع ٦ شايلاه كمرات طالعة من نفس العمدان (كابولي)، من غير عمدان زيادة.</div>
<p class="legend">دي أقل حاجة في الكود المصري (خرسانة ٢٥٠ وحديد ٣٦/٥٢). المهندس الإنشائي لازم يحسب الحديد النهائي، خصوصًا عمدان الواجهة بسبب حمل التخزين والبروز.</p>
{foot(i)}</div>'''

p['page_offset'] = 1                                   # the land plan is page 1
p['keep_pages'] = 5                                    # cover + floors 1-4
p['extra_pages'] = [columns_page]
p['n_pages'] = 1 + 5 + 1
G.PLANS[K] = p
G.COLINFO[K] = G.COLINFO[2]
G.WELL_NOTE[K] = 'ريسبشن طويل على حيطة الجار، والبلكونة فيه'
G.KNAME[K] = 'ريسبشن ٢'
G.PDFNAME[K] = '-ريسبشن-٢'

def page_number_overlay(n, N):
    """a transparent landscape A4 page carrying only "صفحة n من N" (top-left and bottom-left, like the other pages)"""
    import subprocess
    t = f'صفحة {G.ar(n, 0)} من {G.ar(N, 0)}'
    html = ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>@page{size:A4 landscape;margin:0}'
            'html,body{margin:0;padding:0;background:transparent}'
            '.n{position:absolute;left:12mm;font-family:"Geeza Pro","Al Nile","Noto Naskh Arabic","Arial",sans-serif;font-size:3mm;color:#5b6472}'
            f'</style></head><body><div class="n" style="top:8mm">{t}</div><div class="n" style="top:201.5mm">{t}</div></body></html>')
    hp = os.path.join(G.OUT, 'pagenum.html'); pdf = hp[:-5] + '.pdf'
    open(hp, 'w', encoding='utf-8').write(html)
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=120)
    return hp, pdf

def with_land_first():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(G.S), 'pylib'))
    import fitz
    out = os.path.join(G.OUT, f'ترشيح{G.PDFNAME[K]}.pdf')
    doc = fitz.open(); doc.insert_pdf(fitz.open(LAND_PDF)); doc.insert_pdf(fitz.open(out))
    hp, ov = page_number_overlay(1, p['n_pages'])            # his ask: the land plan page carries number 1 like the rest
    doc[0].show_pdf_page(doc[0].rect, fitz.open(ov), 0, overlay=True)
    os.remove(hp); os.remove(ov)
    tmp = out + '.tmp'; doc.save(tmp); os.replace(tmp, out)
    print('final pages', len(fitz.open(out)))

if __name__ == '__main__':
    G.build(K)
    with_land_first()
