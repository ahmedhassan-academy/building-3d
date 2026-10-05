# -*- coding: utf-8 -*-
"""Four more layouts for the flat of proposal 2 (his ask, 5 Oct 2026): same 3 bedrooms + living room + 1 balcony,
same outer walls (1.80 forward), same kitchen / bath / light well / stair / flat door; every bedroom has its own path.
python3 flat4_options.py  ->  2d/flat4.html + 2d/الشقة-٤-ترشيحات.pdf (4 A4 pages)"""
import math, os, subprocess
import gen2d as G

F = G.FR; P = G.PLANS[2]; R2 = {r['n']: r for r in P['rooms']}
lw, rw = G.lw, G.rw
XL, XR, A, D2, C2, B2, P1, P2, P3 = G.XL, G.XR, G.A, G.D2, G.C2, G.B2, G.P1, G.P2, G.P3
CB5 = 12.73 + (-5.0 + 5.03) * (11.5 - 12.73) / (-0.185 + 5.03)      # stair-box bottom wall at x = -5.0
NOOK = [(-5.0, 12.4), (-5.0, 12.73), (-4.784, 13.712), (-5.384, 13.712), (-5.384, 13.4)]   # entrance by the flat door
KITCHEN, BATH, WELL = [list(map(tuple, R2[n]['p'])) for n in ('مطبخ', 'حمام', 'منور')]
BACK_DOORS = [((-8.25, 13.4), (1, 0), (0, 1)), ((-6.334, 13.4), (1, 0), (0, 1))]            # kitchen, bath
BACK_WINS = [((-7.0, 15.05), (-7.0, 15.75)), ((-6.6, 14.9), (-5.9, 14.9))]                 # both on the light well
GREEN = '#2B8A3E'

def R(y): return (rw(y), y)
def L(y): return (lw(y), y)

OPTIONS = [
 dict(title='ترشيح أ: الصالة على الواجهة بالبلكونة',
  rooms=[('صالة', 'c-amber', [(XL, 4.05), (-11.95, 4.05), (-11.95, 5.55), (-9.45, 5.55), (-9.45, 4.05), (-9.2, 4.05), (-9.2, 9.2), (-6.5, 9.2), (-6.5, 12.4), (-8.6, 12.4), (-8.6, 13.4), (-10.396, 13.4)], (-9.6, 10.8)),
         ('نوم ١', 'c-blue', [(-9.2, 4.05), (-6.5, 4.05), (-6.5, 9.2), (-9.2, 9.2)], (-7.85, 6.6)),
         ('نوم ٢', 'c-blue', [(-6.5, 4.05), (XR, 4.05), R(8.4), (-5.5, 8.4), (-5.5, 7.0), (-6.5, 7.0)], (-3.8, 6.0)),
         ('نوم ٣', 'c-blue', [(-5.5, 8.4), R(8.4), P1, (-5.0, CB5), (-5.0, 12.4), (-5.5, 12.4)], (-3.0, 10.2)),
         ('هول', 'c-gray', [(-8.6, 12.4), (-6.5, 12.4), (-6.5, 7.0), (-5.5, 7.0), (-5.5, 12.4)] + NOOK + [(-8.6, 13.4)], (-7.5, 12.9))],
  doors=[((-8.4, 12.4), (1, 0), (0, -1)), ((-6.5, 8.2), (0, -1), (-1, 0)), ((-5.5, 8.25), (0, -1), (1, 0)), ((-5.5, 11.0), (0, -1), (1, 0))],
  wins=[((-8.45, 4.05), (-7.25, 4.05)), ((-5.2, 4.05), (-3.4, 4.05)), (R(6.2), R(7.6)), (R(9.7), R(11.1))],
  balc=(-11.95, -9.45), slide=((-11.7, 5.55), (-9.7, 5.55)), corridor=(-6.0, 9.7),
  notes=['الصالة على شارع ١٢ وبالبلكونة، فبقى ليها شباك، وجواها حتة للسفرة.',
         'نوم ٢ على الناصية بشباكين، ونوم ٣ على شارع ٦.',
         'العيب: نوم ١ ضيقة، عرضها ٢.٧ م بس.']),
 dict(title='ترشيح ب: الصالة على الناصية',
  rooms=[('صالة', 'c-amber', [(-6.5, 4.05), (-5.6, 4.05), (-5.6, 5.55), (-3.1, 5.55), (-3.1, 4.05), (XR, 4.05), R(8.4), (-6.5, 8.4)], (-4.2, 7.0)),
         ('نوم ١', 'c-blue', [(XL, 4.05), (-9.0, 4.05), (-9.0, 9.2), L(9.2)], (-10.6, 6.6)),
         ('نوم ٢', 'c-blue', [(-9.0, 4.05), (-6.5, 4.05), (-6.5, 9.2), (-9.0, 9.2)], (-7.75, 6.6)),
         ('نوم ٣', 'c-blue', [(-5.5, 8.4), R(8.4), P1, (-5.0, CB5), (-5.0, 12.4), (-5.5, 12.4)], (-3.0, 10.2)),
         ('هول', 'c-gray', [L(9.2), (-6.5, 9.2), (-6.5, 8.4), (-5.5, 8.4), (-5.5, 12.4)] + NOOK + [(-10.396, 13.4)], (-8.8, 11.0))],
  doors=[((-10.7, 9.2), (1, 0), (0, -1)), ((-8.6, 9.2), (1, 0), (0, -1)), ((-6.45, 8.4), (1, 0), (0, -1)), ((-5.5, 11.0), (0, -1), (1, 0))],
  wins=[((-11.7, 4.05), (-10.3, 4.05)), ((-8.35, 4.05), (-7.15, 4.05)), (R(6.2), R(7.8)), (R(9.7), R(11.1))],
  balc=(-5.6, -3.1), slide=((-5.35, 5.55), (-3.35, 5.55)), hall_note='هول واسع (ممكن سفرة)',
  notes=['الصالة على ناصية الشارعين، شبابيك على الاتنين، وبالبلكونة.',
         'نوم ١ ونوم ٢ على شارع ١٢ وبيفتحوا على هول واسع، ونوم ٣ على شارع ٦.',
         'العيب: الضيف بيمشي في الطرقة جنب باب نوم ٣ لحد ما يوصل للصالة.']),
 dict(title='ترشيح ج: الصالة جنب المدخل على شارع ٦',
  rooms=[('صالة', 'c-amber', [(-5.5, 7.4), R(7.4), P1, (-5.0, CB5), (-5.0, 12.4), (-5.5, 12.4)], (-3.1, 9.9)),
         ('نوم ١', 'c-blue', [(XL, 4.05), (-9.0, 4.05), (-9.0, 9.2), L(9.2)], (-10.6, 6.6)),
         ('نوم ٢', 'c-blue', [(-9.0, 4.05), (-6.5, 4.05), (-6.5, 9.2), (-9.0, 9.2)], (-7.75, 6.6)),
         ('نوم ٣', 'c-blue', [(-6.5, 4.05), (-5.4, 4.05), (-5.4, 5.55), (-2.9, 5.55), (-2.9, 4.05), (XR, 4.05), R(7.4), (-5.5, 7.4), (-5.5, 7.0), (-6.5, 7.0)], (-4.2, 6.45)),
         ('هول', 'c-gray', [L(9.2), (-6.5, 9.2), (-6.5, 7.0), (-5.5, 7.0), (-5.5, 12.4)] + NOOK + [(-10.396, 13.4)], (-8.8, 11.0))],
  doors=[((-10.7, 9.2), (1, 0), (0, -1)), ((-6.5, 8.2), (0, -1), (-1, 0)), ((-6.45, 7.0), (1, 0), (0, -1)), ((-5.5, 12.2), (0, -1), (1, 0))],
  wins=[((-11.7, 4.05), (-10.3, 4.05)), ((-8.35, 4.05), (-7.15, 4.05)), (R(6.0), R(7.2)), (R(7.7), R(8.9)), (R(9.6), R(11.0))],
  balc=(-5.4, -2.9), slide=((-5.15, 5.55), (-3.15, 5.55)), hall_note='هول واسع (ممكن سفرة)',
  notes=['الصالة أول ما تدخل على اليمين، فالضيف مش بيدخل جوه الشقة، وليها شبابيك على شارع ٦.',
         'التلات أوض على شارع ١٢، ونوم ٣ على الناصية بالبلكونة.',
         'العيب: الصالة أصغر من الترشيحات التانية، ونوم ١ بتفتح على الهول الواسع.']),
 dict(title='ترشيح د: صالة كبيرة على الواجهة والأوض على شارع ٦',
  rooms=[('صالة', 'c-amber', [(XL, 4.05), (-10.77, 4.05), (-10.77, 5.55), (-8.27, 5.55), (-8.27, 4.05), (-6.5, 4.05), (-6.5, 12.4), (-8.6, 12.4), (-8.6, 13.4), (-10.396, 13.4)], (-9.3, 8.6)),
         ('نوم ١', 'c-blue', [(-6.5, 4.05), (XR, 4.05), R(6.9), (-6.5, 6.9)], (-3.9, 5.5)),
         ('نوم ٢', 'c-blue', [(-5.5, 6.9), R(6.9), R(9.7), (-5.5, 9.7)], (-3.1, 8.3)),
         ('نوم ٣', 'c-blue', [(-5.5, 9.7), R(9.7), P1, (-5.0, CB5), (-5.0, 12.4), (-5.5, 12.4)], (-2.9, 10.85)),
         ('هول', 'c-gray', [(-8.6, 12.4), (-6.5, 12.4), (-6.5, 6.9), (-5.5, 6.9), (-5.5, 12.4)] + NOOK + [(-8.6, 13.4)], (-7.5, 12.9))],
  doors=[((-8.4, 12.4), (1, 0), (0, -1)), ((-6.45, 6.9), (1, 0), (0, -1)), ((-5.5, 8.9), (0, -1), (1, 0)), ((-5.5, 11.4), (0, -1), (1, 0))],
  wins=[((-7.85, 4.05), (-6.85, 4.05)), ((-5.2, 4.05), (-3.4, 4.05)), (R(5.95), R(6.75)), (R(7.4), R(8.8)), (R(9.9), R(11.2))],
  balc=(-10.77, -8.27), slide=((-10.52, 5.55), (-8.52, 5.55)), corridor=(-6.0, 9.4), living_name='صالة + سفرة',
  notes=['صالة كبيرة على شارع ١٢ بالبلكونة، ومعاها السفرة.',
         'التلات أوض جنب بعض على شارع ٦، وكلهم بيفتحوا على طرقة لوحدهم.',
         'العيب: الأوض أصغر، كل واحدة حوالي ١٢ لـ ١٤ م².']),
]

# ---------------- geometry helpers ----------------
def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]; L2 = ax * ax + ay * ay
    t = max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L2)) if L2 else 0
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)
def on_any(p, q, segs, tol=0.03): return any(seg_dist(p, a, b) < tol and seg_dist(q, a, b) < tol for a, b in segs)
def on_ext(p, q, segs, tol=0.035):
    pts = [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t) for t in (0, 0.25, 0.5, 0.75, 1)]
    return all(min(seg_dist(pt, a, b) for a, b in segs) < tol for pt in pts)
def edges(poly): return [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]

def walls_svg(polys, exterior, doors):
    seen = []; o = []; wpx = 0.12 * F.s
    for poly in polys:
        for p, q in edges(poly):
            if math.hypot(q[0] - p[0], q[1] - p[1]) < 0.02 or on_ext(p, q, exterior): continue
            if any(on_any(p, q, [s]) and on_any(*s, [(p, q)]) for s in seen): continue
            seen.append((p, q))
            Lg = math.hypot(q[0] - p[0], q[1] - p[1]); ux, uy = (q[0] - p[0]) / Lg, (q[1] - p[1]) / Lg
            cuts = []
            for h, al, out in doors:
                e = (h[0] + al[0] * 0.9, h[1] + al[1] * 0.9)
                if seg_dist(h, p, q) < 0.03 and seg_dist(e, p, q) < 0.03:
                    t0 = (h[0] - p[0]) * ux + (h[1] - p[1]) * uy; t1 = (e[0] - p[0]) * ux + (e[1] - p[1]) * uy
                    cuts.append((min(t0, t1), max(t0, t1)))
            u = 0
            for c0, c1 in sorted(cuts) + [(Lg, Lg)]:
                if c0 - u > 0.01: o.append(G.line(F, (p[0] + ux * u, p[1] + uy * u), (p[0] + ux * c0, p[1] + uy * c0), '#1d2126', wpx))
                u = max(u, c1)
    return o

def label(t, x, y, cls='t', dy=0, rot=None, color=None):
    X, Y = F.X(x), F.Y(y) + dy; tr = f' transform="rotate({rot} {X:.1f} {Y:.1f})"' if rot else ''
    st = f' style="fill:{color};font-weight:700"' if color else ''
    return f'<text x="{X:.1f}" y="{Y:.1f}" class="{cls}" text-anchor="middle" dominant-baseline="central"{tr}{st}>{t}</text>'

def plan_svg(op):
    o = [G.svg_open(title=op['title'])] + G.site(F)
    bx0, bx1 = op['balc']
    outline = [A, (XL, 4.05), (bx0, 4.05), (bx0, 5.55), (bx1, 5.55), (bx1, 4.05), (XR, 4.05), D2, C2, B2]
    exterior = edges(outline) + edges([C2, P1, P2, P3])
    polys = []; areas = {}
    for n, cls, poly, c in op['rooms']:
        fill, stroke = G.CLS[cls]; o.append(G.poly(F, poly, fill=fill, stroke=stroke, sw=0.8)); polys.append(poly); areas[n] = G.area(poly)
    for n, poly in (('مطبخ', KITCHEN), ('حمام', BATH), ('منور', WELL)):
        fill, stroke = G.CLS[{'مطبخ': 'c-green', 'حمام': 'c-purple', 'منور': 'c-gray'}[n]]
        o.append(G.poly(F, poly, fill=fill, stroke=stroke, sw=0.8)); polys.append(poly)
    o.append(G.poly(F, [(bx0, 4.05), (bx1, 4.05), (bx1, 5.55), (bx0, 5.55)], fill='#ECEEF1', stroke='#1d2126', sw=1.6))
    doors = op['doors'] + BACK_DOORS
    o += walls_svg(polys, exterior, doors)
    o.append(G.poly(F, outline, fill='none', stroke='#1d2126', sw=3))
    for a, b in op['wins'] + BACK_WINS: o.append(G.win(F, a, b))
    o.append(G.slide(F, *op['slide']))
    o += G.core_svg(F, 3, P); o += G.columns(F, P, 3)
    for h, al, out in doors: o.append(G.leaf(F, h, al, out, 0.9))
    for n, cls, poly, c in op['rooms']:
        if n == 'هول':
            o.append(label(op.get('hall_note', 'هول'), *c, cls='ts'))
            continue
        nm = op.get('living_name', n) if n == 'صالة' else n
        o.append(label(nm, *c, dy=-7)); o.append(label(f'≈ {G.ar(areas[n], 0)} م²', *c, cls='ts', dy=8))
    if op.get('corridor'): o.append(label('طرقة النوم', *op['corridor'], cls='ts', rot=-90))
    o.append(label(f'بلكونة ٢.٥ × ١.٥٠', (bx0 + bx1) / 2, 4.8, cls='ts'))
    o.append(label('مطبخ', -8.5, 15.0, dy=-7)); o.append(label(f'≈ {G.ar(G.area(KITCHEN), 0)} م²', -8.5, 15.0, cls='ts', dy=8))
    o.append(label('حمام', -5.75, 14.5, dy=-7)); o.append(label(f'≈ {G.ar(G.area(BATH), 0)} م²', -5.75, 14.5, cls='ts', dy=8))
    o.append(label('منور ٢.٥ × ١.١', -5.8, 15.45, cls='ts'))
    o += G.dims(F, 3); o += G.legend(P); o.append('</svg>')
    return '\n'.join(o), areas

def build():
    pages = []; N = len(OPTIONS)
    for i, op in enumerate(OPTIONS, 1):
        svg, ar_ = plan_svg(op)
        net = sum(ar_.values()) + G.area(KITCHEN) + G.area(BATH)
        rooms = ' · '.join(f'{op.get("living_name", n) if n == "صالة" else n} ≈ {G.ar(ar_[n], 0)} م²' for n in ('صالة', 'نوم ١', 'نوم ٢', 'نوم ٣'))
        pages.append(f'''<div class="page"><div class="hdr"><div><h2>{op["title"]}</h2><p class="sub">الدور الثالث (والرابع زيه) · نفس الحيطان الخارجية والمطبخ والحمام والمنور والسلم · ٣ أوض نوم + صالة + بلكونة واحدة</p></div><div class="pg">صفحة {G.ar(i, 0)} من {G.ar(N, 0)}</div></div>
<div class="big">{svg}</div>
<div class="fact"><b>المساحات:</b> {rooms} · <b>الصافي:</b> ≈ {G.ar(net, 0)} م²</div>
<div class="fact">{'<br>'.join(op['notes'])}</div>
<div class="foot"><span>ترشيح ٢: ٤ ترشيحات للشقة · {G.DATE}</span><span>صفحة {G.ar(i, 0)} من {G.ar(N, 0)}</span></div></div>''')
    html = '<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>٤ ترشيحات للشقة</title><style>' + G.CSS + '</style></head><body>' + ''.join(pages) + '</body></html>'
    hp = os.path.join(G.OUT, 'flat4.html'); open(hp, 'w', encoding='utf-8').write(html)
    pdf = os.path.join(G.OUT, 'الشقة-٤-ترشيحات.pdf')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=180)
    print('pdf', os.path.getsize(pdf) if os.path.exists(pdf) else 0)

if __name__ == '__main__':
    build()
