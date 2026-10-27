# -*- coding: utf-8 -*-
"""His ask (27 Oct 2026): the four layouts that share one column plan — no. 1 (ريسبشن ١), 4 (ريسبشن ٤), 6 (ترشيح ٢), 7 (ترشيح ٢ب) —
in one PDF: the warehouse floors 1 and 2 once (they are the same for all four), then floor 3 of each, nothing else.
Every column gets its own colour and number, the same on every page; doors orange; the projections hatched in their own colour.
python3 columns4_pdf.py  ->  2d/العمدان-الترشيحات-٤.pdf"""
import math, os, subprocess
import gen2d as G
import reception5_options as R

AR = lambda n: G.ar(n, 0)
# the 13 columns, numbered from the front-left corner round the outside walls, then the one inside and the stair's inner corner
ORDER = [(-12.12, 5.85), (-6.5, 5.85), (-1.62, 5.83), (-0.768, 9.2), (-0.185, 11.5), (0.55, 14.41), (-4.3, 15.64),
         (-6.5, 16.192), (-9.58, 16.97), (-10.624, 12.4), (-11.355, 9.2), (-6.5, 9.2), (-5.03, 12.73)]
COLOURS = ['#2B8A3E', '#0B7285', '#364FC7', '#6741D9', '#A0522D', '#5C940D', '#212529',
           '#E8B900', '#15AABF', '#74B816', '#862E9C', '#D62828', '#868E96']
PROJ = '#C2255C'                                        # the projections (doors stay orange, G.DOOR)
G.DEFS = G.DEFS.replace('</defs>', f'<pattern id="proj" patternUnits="userSpaceOnUse" width="9" height="9" patternTransform="rotate(45)">'
                        f'<rect width="9" height="9" fill="{PROJ}" fill-opacity="0.10"/><line x1="0" y1="0" x2="0" y2="9" stroke="{PROJ}" stroke-width="2.2" stroke-opacity="0.55"/></pattern></defs>')
# where each number sits (plan metres), picked so it clears the dimension texts, the stair and the doors
LABEL_AT = [(-12.75, 5.45), (-6.5, 6.45), (-2.2, 6.75), (-1.55, 8.75), (-1.0, 11.75), (1.15, 14.85), (-4.8, 15.25),
            (-7.35, 15.3), (-9.15, 17.45), (-9.2, 12.75), (-10.55, 8.65), (-7.0, 9.65), (-5.6, 12.3)]

def number_of(x, y):
    return min(range(len(ORDER)), key=lambda i: math.hypot(ORDER[i][0] - x, ORDER[i][1] - y))

def coloured_columns(F, plan, fl):
    o = []; shrink = 0 if fl <= 2 else 0.1
    cols = [(c[0], c[1], c[2], c[3], c[4]) for c in plan['cols_out']] + [(c[0], c[1], 0.4 if fl <= 2 else 0.3, 0.4 if fl <= 2 else 0.3, 0) for c in plan['cols_in']]
    for x, y, w, h, ang in cols:
        i = number_of(x, y); col = COLOURS[i]
        o.append(G.rect_rot(F, x, y, max(0.3, w - shrink) + 0.08, max(0.3, h - shrink) + 0.08, ang, col))
        lx, ly = LABEL_AT[i]
        o.append(f'<text x="{F.X(lx):.1f}" y="{F.Y(ly):.1f}" text-anchor="middle" dominant-baseline="central" '
                 f'style="fill:{col};font-size:13px;font-weight:800;stroke:#ffffff;stroke-width:3.5px;paint-order:stroke">{AR(i + 1)}</text>')
    return o

def new_legend(plan):
    return ['<text x="668" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="#1d2126" font-weight="700">■ العمدان: لكل عمود لون ورقم، ونفس الرقم في كل الأدوار</text>',
            f'<text x="300" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="{G.DOOR}" font-weight="700">▬ باب</text>',
            f'<rect x="222" y="10" width="16" height="12" fill="url(#proj)" stroke="{PROJ}" stroke-width="1.2"/>',
            f'<text x="242" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="{PROJ}" font-weight="700">بروز</text>',
            '<text x="130" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="#1F5FBF" font-weight="700">▬ شباك</text>']

ZONE = None
def projection(F, plan):
    d = plan.get('side', 0)
    zone = [(G.XL, 4.05), (G.rw2(4.05, d), 4.05), G.sh(G.C2, d), G.C2, G.D2, G.A]
    return [G.poly(F, zone, fill='url(#proj)', stroke=PROJ, sw=1.4)]

def flat(plan):
    svg = G.flat_svg(plan, 3)
    for a in ('fill:#B3261E;font-size:10px', 'fill:#B3261E;font-size:9px'): svg = svg.replace(a, a.replace('#B3261E', PROJ))
    for w in ('2.2', '1.4', '0.8'): svg = svg.replace(f'stroke="#B3261E" stroke-width="{w}"', f'stroke="{PROJ}" stroke-width="{w}"')
    return svg

_wall_lines = G.wall_lines
def wall_lines_with_projection(F, plan):                # flat_svg draws walls right after the rooms: the hatch goes in just before them
    return projection(F, plan) + _wall_lines(F, plan)

G.columns = coloured_columns
G.legend = new_legend
G.wall_lines = wall_lines_with_projection

# ---------------- the raft (his ask, 27 Oct): under the whole ground floor, on the neighbour lines, 1.0 m out toward both streets
def _off(p, q, d):                                     # the line p->q moved d metres to its right (outside of the building)
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); return (p[0] + dy / L * d, p[1] - dx / L * d), (q[0] + dy / L * d, q[1] - dx / L * d)
def _x(p1, p2, p3, p4):
    den = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])
    t = ((p1[0] - p3[0]) * (p3[1] - p4[1]) - (p1[1] - p3[1]) * (p3[0] - p4[0])) / den
    return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
def raft_poly(ext):
    A, D2, C2, B2 = G.A, G.D2, G.C2, G.B2
    f = _off(A, D2, ext); r = _off(D2, C2, ext)
    return [_x(B2, A, *f), _x(*f, *r), _x(*r, C2, B2), B2]
RAFT, PC = raft_poly(1.0), raft_poly(1.2)
RAFT_T, PC_T, RAFT_DEPTH = 0.60, 0.20, 1.50              # my working sizes until the structural engineer has the soil report

def txt(F, t, x, y, col='#1d2126', size=10, rot=None, bold=True):
    X, Y = F.X(x), F.Y(y); r = f' transform="rotate({rot:.1f} {X:.1f} {Y:.1f})"' if rot is not None else ''
    return (f'<text x="{X:.1f}" y="{Y:.1f}" text-anchor="middle" dominant-baseline="central"{r} style="fill:{col};font-size:{size}px;'
            f'font-weight:{700 if bold else 400};stroke:#fff;stroke-width:3px;paint-order:stroke">{t}</text>')

def raft_svg(plan):
    F = G.FR; o = [G.svg_open(title='اللبشة')] + G.site(F)
    o.append(G.poly(F, PC, fill='#EFEDE8', stroke='#8A8F99', sw=1.2, dash='6 4'))
    o.append(G.poly(F, RAFT, fill='#D9D5CC', stroke='#3A414B', sw=2.6))
    o.append(G.poly(F, G.BLD, fill='none', stroke='#1d2126', sw=1, dash='3 3'))
    o.append(G.poly(F, G.CORE, fill='none', stroke='#2A8C8C', sw=1, dash='3 3'))
    for p, q, t in ((RAFT[0], RAFT[1], 'front'), (RAFT[1], RAFT[2], 'side'), (RAFT[2], RAFT[3], 'back'), (RAFT[3], RAFT[0], 'left')):
        L = math.hypot(q[0] - p[0], q[1] - p[1]); m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        n = ((q[1] - p[1]) / L, -(q[0] - p[0]) / L)          # outside
        far = 0.55 if t in ('front', 'side') else 0.5
        lab = f'{G.ar(L, 2)} م' + (' — على حد الجار' if t in ('back', 'left') else '')
        o.append(txt(F, lab, m[0] + n[0] * far, m[1] + n[1] * far, '#3A414B', 10, G.rot_along(p, q)))
    # how far the raft goes past the walls toward the streets
    for (p, q), at in (((G.A, G.D2), 0.18), ((G.D2, G.C2), 0.5)):
        L = math.hypot(q[0] - p[0], q[1] - p[1]); u = ((q[0] - p[0]) / L, (q[1] - p[1]) / L); n = (u[1], -u[0])
        b = (p[0] + u[0] * L * at, p[1] + u[1] * L * at); e = (b[0] + n[0], b[1] + n[1])
        o.append(f'<line x1="{F.X(b[0]):.1f}" y1="{F.Y(b[1]):.1f}" x2="{F.X(e[0]):.1f}" y2="{F.Y(e[1]):.1f}" stroke="#B3261E" stroke-width="1.4" marker-start="url(#arw)" marker-end="url(#arw)"/>')
        o.append(txt(F, '١.٠ م', b[0] + n[0] * 0.5 + u[0] * 0.75, b[1] + n[1] * 0.5 + u[1] * 0.75, '#B3261E', 10))
    o.append(txt(F, f'لبشة {G.ar(RAFT_T * 100, 0)} سم · ≈ {G.ar(G.area(RAFT), 0)} م²', -6.2, 10.9, '#1d2126', 13))
    o.append(txt(F, 'المتقطع الرفيع = حيطان الدور الأول', -6.2, 10.25, '#3A414B', 9, bold=False))
    o += coloured_columns(F, plan, 1)
    o += ['<text x="668" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="#1d2126" font-weight="700">■ العمدان: نفس الألوان والأرقام</text>',
          '<rect x="452" y="10" width="16" height="12" fill="#D9D5CC" stroke="#3A414B" stroke-width="1.5"/><text x="446" y="16" class="ts" text-anchor="start" dominant-baseline="central" font-weight="700">لبشة ٦٠ سم</text>',
          '<rect x="352" y="10" width="16" height="12" fill="#EFEDE8" stroke="#8A8F99" stroke-dasharray="3 2"/><text x="346" y="16" class="ts" text-anchor="start" dominant-baseline="central" font-weight="700">خرسانة عادية ٢٠ سم</text>']
    o.append('</svg>'); return '\n'.join(o)

def raft_section_svg():
    """a schematic cut through the raft (not to scale across, to scale in height)"""
    W, H, s = 680, 150, 52                                # px per metre in height
    g0 = 40                                               # ground line y (px)
    Y = lambda z: g0 - z * s
    o = [f'<svg viewBox="0 0 {W} {H}" role="img"><title>قطاع في اللبشة</title>{G.DEFS}']
    o.append(f'<rect x="40" y="{Y(0):.0f}" width="600" height="{Y(-2.1) - Y(0):.0f}" fill="#efe6d6"/>')                  # soil
    o.append(f'<rect x="60" y="{Y(-RAFT_DEPTH):.0f}" width="560" height="{PC_T * s:.0f}" fill="#EFEDE8" stroke="#8A8F99" stroke-dasharray="4 3"/>')
    o.append(f'<rect x="60" y="{Y(-RAFT_DEPTH + RAFT_T):.0f}" width="545" height="{RAFT_T * s:.0f}" fill="#D9D5CC" stroke="#3A414B" stroke-width="2"/>')
    for x, col in ((120, '#2B8A3E'), (330, '#D62828'), (540, '#364FC7')):
        o.append(f'<rect x="{x - 10}" y="{Y(0.45):.0f}" width="20" height="{(0.45 + RAFT_DEPTH - RAFT_T) * s:.0f}" fill="{col}"/>')
    o.append(f'<rect x="60" y="{Y(0):.0f}" width="545" height="{0.15 * s:.0f}" fill="#BDB8AD" stroke="#3A414B" stroke-width="1"/>')       # ground slab
    o.append(f'<line x1="20" y1="{Y(0):.0f}" x2="660" y2="{Y(0):.0f}" stroke="#1d2126" stroke-width="1" stroke-dasharray="6 3"/>')
    o.append(f'<line x1="60" y1="10" x2="60" y2="{Y(-2.0):.0f}" stroke="#1d2126" stroke-width="2.5"/>')
    def t(x, y, s_, col='#1d2126', anchor='middle', size=11): return f'<text x="{x}" y="{y:.0f}" text-anchor="{anchor}" dominant-baseline="central" style="fill:{col};font-size:{size}px;font-weight:700">{s_}</text>'
    o += [t(66, 14, 'حد الجار', anchor='end'), t(660, Y(0) - 10, 'أرضية المخزن', anchor='start'),
          t(330, Y(-RAFT_DEPTH + RAFT_T / 2), f'لبشة مسلحة {G.ar(RAFT_T * 100, 0)} سم: شبكة تحت وشبكة فوق'),
          t(330, Y(-RAFT_DEPTH - PC_T / 2), f'خرسانة عادية {G.ar(PC_T * 100, 0)} سم', size=10),
          t(660, Y(-RAFT_DEPTH) + 6, f'{G.ar(RAFT_DEPTH, 2)} م تحت الأرض', anchor='start', size=10),
          t(610, Y(-RAFT_DEPTH + RAFT_T) - 10, '١.٠ م ناحية الشارع ←', anchor='end', size=10),
          t(440, Y(-0.45), 'رقبة العمود من اللبشة لفوق', size=10)]
    o.append('</svg>'); return '\n'.join(o)

# ---------------- where every column is: the distance between neighbours + each one from the facade line and the north neighbour
OUTER = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 0)]
INNER = [(10, 11), (11, 3), (1, 11), (11, 7), (12, 4), (12, 6), (9, 12)]
def distances_svg(plan):
    F = G.FR; o = [G.svg_open(title='أماكن العمدان')] + G.site(F)
    o.append(G.poly(F, G.BLD, fill='#ffffff', stroke='#1d2126', sw=1.4))
    o.append(G.poly(F, G.CORE, fill=G.CLS['c-teal'][0], stroke=G.CLS['c-teal'][1], sw=1))
    P = ORDER; cx = sum(p[0] for p in G.BLD) / 4; cy = sum(p[1] for p in G.BLD) / 4
    longest = max(OUTER + INNER, key=lambda ij: math.hypot(P[ij[1]][0] - P[ij[0]][0], P[ij[1]][1] - P[ij[0]][1]))
    for i, j in OUTER + INNER: o.append(G.line(F, P[i], P[j], '#8A4B12', 2))
    for i, j in OUTER + INNER:
        a, b = P[i], P[j]; L = math.hypot(b[0] - a[0], b[1] - a[1]); t = 0.35 if (i, j) == longest else 0.5
        m = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t); n = (-(b[1] - a[1]) / L, (b[0] - a[0]) / L)
        if (i, j) in OUTER:
            if (m[0] + n[0] - cx) ** 2 + (m[1] + n[1] - cy) ** 2 < (m[0] - n[0] - cx) ** 2 + (m[1] - n[1] - cy) ** 2: n = (-n[0], -n[1])
            off = 0.45
        else:
            if (abs(n[1]) >= abs(n[0]) and n[1] < 0) or (abs(n[1]) < abs(n[0]) and n[0] < 0): n = (-n[0], -n[1])
            off = 0.3
        o.append(txt(F, f'{G.ar(L, 2)} م', m[0] + n[0] * off, m[1] + n[1] * off, '#B3261E' if (i, j) == longest else '#8A4B12', 11, G.rot_along(a, b)))
    o += coloured_columns(F, plan, 1)
    o += ['<text x="668" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="#1d2126" font-weight="700">■ العمدان: نفس الألوان والأرقام</text>',
          '<text x="420" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="#8A4B12" font-weight="700">▬ المسافة من نص العمود لنص العمود</text>']
    o.append('</svg>'); return '\n'.join(o)

def column_table():
    A, D2 = G.A, G.D2; B2 = G.B2
    def dist(p, a, b):                                   # distance of p from the line a-b
        return abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / math.hypot(b[0] - a[0], b[1] - a[1])
    sizes = {0: '٤٠ × ٤٠', 2: '٤٠ × ٤٠', 4: '٤٠ × ٤٠', 5: '٤٠ × ٤٠', 6: '٤٠ × ٤٠', 8: '٤٠ × ٤٠', 11: '٤٠ × ٤٠', 12: '٤٠ × ٤٠'}
    rows = []
    for i, p in enumerate(ORDER):
        rows.append(f'<tr><td><b style="color:{COLOURS[i]}">■ {AR(i + 1)}</b></td><td class="n">{G.ar(dist(p, A, D2), 2)}</td>'
                    f'<td class="n">{G.ar(dist(p, A, B2), 2)}</td><td class="n">{sizes.get(i, "٢٥ × ٧٠")}</td></tr>')
    head = '<tr><th>العمود</th><th class="n">من خط الواجهة (م)</th><th class="n">من حد الجار الشمال (م)</th><th class="n">المقاس في المخزن (سم)</th></tr>'
    return (f'<table class="ctab">{head}{"".join(rows)}</table>'
            '<p class="legend">الأرقام من نص العمود. خط الواجهة = حيطة الدور الأول على شارع ١٢، وحد الجار الشمال = الحيطة اللي على الجار. في الشقق العمدان بتصغر لـ ٢٥ × ٦٠ و ٣٠ × ٣٠.</p>')

def warehouse(plan, fl):
    svg = G.wh_svg(plan, fl)
    if fl == 2:                                          # the floor-2 projection gets the same hatch instead of its green fill
        svg = svg.replace('fill="#E6F0E6" stroke="#4C8C4A"', f'fill="url(#proj)" stroke="{PROJ}"')
        svg = svg.replace('fill:#2f6b2f', f'fill:{PROJ}').replace('fill="#2f6b2f"', f'fill="{PROJ}"')
    return svg

def build():
    base = G.PLANS[2]
    plans = [('١', 'ريسبشن ١', R.make(next(o for o in R.OPTIONS if o['key'] == 'A'))),
             ('٤', 'ريسبشن ٤', R.make(next(o for o in R.OPTIONS if o['key'] == 'C'))),
             ('٦', 'ترشيح ٢', G.PLANS[2]),
             ('٧', 'ترشيح ٢ب', G.PLANS[7])]
    N = 3 + len(plans)                                 # his ask (27 Oct): the raft page is out
    def page(i, title, sub, svg, extra='', cls='big'):
        return (f'<div class="page"><div class="hdr"><div><h1>{title}</h1><p class="sub">{sub}</p></div><div class="pg">صفحة {AR(i)} من {AR(N)}</div></div>'
                f'<div class="{cls}">{svg}</div>{extra}</div>')
    notes = ('<div class="fact"><b>اللبشة:</b> خرسانة مسلحة سمكها ٦٠ سم تحت المبنى كله، لازقة في حد الجارين، وطالعة ١.٠ م ناحية شارع ١٢ وشارع ٦ جوه أرضنا · '
             'تحتها خرسانة عادية ٢٠ سم طالعة ٢٠ سم زيادة · شبكة حديد تحت وشبكة فوق (١٦ مم كل ٢٠ سم في الاتجاهين) وحديد زيادة فوق تحت العمدان · '
             'وشها التحتاني حوالي ١.٥٠ م تحت الأرض.</div>'
             '<p class="legend">المقاسات دي تقديرية. السمك والحديد والعمق النهائي بيحددهم المهندس الإنشائي بعد جسات وتقرير التربة.</p>')
    pages = [page(1, 'أماكن العمدان والمسافات', 'المسافة بين كل عمودين جنب بعض، وبُعد كل عمود عن الواجهة والجار', distances_svg(base), column_table(), 'cpos'),
             page(2, 'الدور الأول: المخزن', 'نفس الدور في الأربع ترشيحات (١ و٤ و٦ و٧)', warehouse(base, 1)),
             page(3, 'الدور الثاني: المخزن والبروز', 'نفس الدور في الأربع ترشيحات (١ و٤ و٦ و٧)', warehouse(base, 2))]
    for j, (num, name, p) in enumerate(plans, 4):
        pages.append(page(j, f'الدور الثالث: ترشيح رقم {num}', f'{name} · العمدان في نفس أماكن الدور الأول والتاني', flat(p)))
    css = G.CSS + '.sect svg{width:186mm;height:auto;display:block;margin:0 auto 1mm} .cpos svg{width:186mm;height:140mm;display:block;margin:0 auto 1mm} .ctab{font-size:3mm} .ctab td,.ctab th{padding:.7mm 1.6mm}'
    html = '<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>العمدان — الترشيحات ١ و٤ و٦ و٧</title><style>' + css + '</style></head><body>' + ''.join(pages) + '</body></html>'
    hp = os.path.join(G.OUT, 'columns4.html'); open(hp, 'w', encoding='utf-8').write(html)
    pdf = os.path.join(G.OUT, 'العمدان-الترشيحات-٤.pdf')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=180)
    print('pdf', os.path.getsize(pdf) if os.path.exists(pdf) else 0)

if __name__ == '__main__':
    build()
