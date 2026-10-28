# -*- coding: utf-8 -*-
"""His ask (28 Oct 2026): floor 1 of ترشيح ١ as on page 1 of ترشيح-رقم-١.pdf, but without the building's stair house
and without the warehouse stair up to floor 2 (the whole floor open), and tell him its area.
Then: the same floor 1 with both stairs, each stair's size and area written on it; then the warehouse stair with 20 steps.
python3 floor1_open.py            ->  2d/الدور-الأول-من-غير-سلالم.pdf
python3 floor1_open.py stairs     ->  2d/الدور-الأول-بالسلمين.pdf
python3 floor1_open.py stairs 20  ->  2d/الدور-الأول-سلم-المخزن-٢٠-درجة.pdf
python3 floor1_open.py stairs 20 cols  ->  2d/الدور-الأول-سلم-المخزن-٢٠-درجة-بعمودين.pdf (his pick: two small columns under it)"""
import math, os, subprocess, sys
import gen2d as G
import columns4_pdf as C          # loading it puts the coloured columns, their legend and the hatch into gen2d

def stair_areas():
    """the stair house, and the warehouse stair's flight with its top landing (length, width, area)"""
    st = G.whst; L, W = st['s_bot'] - (st['s_top'] - 1.2), st['off1'] - st['off0']
    return G.area(G.CORE), L, W, L * W

def set_steps(n):
    """his ask (28 Oct): the warehouse stair with n steps up the same 3.75 m, same 27 cm tread, so it gets shorter;
    its top (floor 2's arrival and stair opening) stays put and its foot comes forward"""
    st = dict(G.whst); st['NR'] = n; st['s_bot'] = st['s_top'] + (n - 1) * st['tread']
    G.whst = st

# his pick (28 Oct), way 2 of holding the warehouse stair: two small 25 x 25 columns under the middle of its flight,
# one at each edge, with a small beam across on top; numbered after the building's 13, each its own colour
STAIR_COLS = [(14, '#E64980'), (15, '#BE4BDB')]       # pink and grape: no other column has them, and no green next to 10's

def stair_columns(F):
    st = G.whst; s = (st['s_top'] + st['s_bot']) / 2; ang = math.atan2(G.wd[1], G.wd[0])
    o = [G.line(F, G.wp(s, st['off0']), G.wp(s, st['off1']), '#8A4B12', 2.5, cap='round')]
    for (n, col), off, loff in zip(STAIR_COLS, (st['off0'] + 0.125, st['off1'] - 0.125), (st['off0'] + 0.15, st['off1'] - 0.15)):
        o.append(G.rect_rot(F, *G.wp(s, off), 0.3 + 0.08, 0.3 + 0.08, ang, col))      # drawn like coloured_columns: 30 cm at least, + 8
        lx, ly = G.wp(s + 0.5, loff)                     # just past each column toward the foot, clear of the middle line's text
        o.append(f'<text x="{F.X(lx):.1f}" y="{F.Y(ly):.1f}" text-anchor="middle" dominant-baseline="central" '
                 f'style="fill:{col};font-size:13px;font-weight:800;stroke:#ffffff;stroke-width:3.5px;paint-order:stroke">{G.ar(n, 0)}</text>')
    return o

def open_floor1(plan):
    """gen2d.wh_svg for floor 1 without core_svg, the flats' street door (it is the stair house's) and wh_stair"""
    F = G.FR; o = [G.svg_open(title='مسقط المخزن من غير سلالم')] + G.site(F)
    o.append(G.poly(F, G.BLD, fill='#ffffff', stroke='none'))         # the stair house's floor is warehouse now
    o += G.beams(F, plan, 1); o += G.ring(F, plan, 1)
    o += G.duct(F); o += G.columns(F, plan, 1)
    free = G.area(G.BLD) - G.area(G.DUCT)
    o.append(G.text(F, f'مساحة فاضية ≈ {G.ar(free, 0)} م²', -6.6, 10.6, cls='th'))
    o.append(G.text(F, 'ارتفاع ٣.٧٥ م', -6.6, 10.6, cls='ts', dy=16))
    o += G.dims(F, 1, 0); o += G.legend(plan); o.append('</svg>')
    return '\n'.join(o), free

def stairs_floor1(plan, cols=False):
    """gen2d.wh_svg for floor 1 as it is, with each stair's area on it; the free area takes out both stairs
    (gen2d's G_AREA only takes out the stair house)"""
    core, L, W, ws = stair_areas()
    free = G.area(G.BLD) - core - ws - G.area(G.DUCT)
    if cols:                                             # column 10's number sat at the stair's open edge, where 15 now stands: put it right by column 10
        x, y = C.ORDER[9]; s10 = (x - G.wA[0]) * G.wd[0] + (y - G.wA[1]) * G.wd[1]
        C.LABEL_AT[9] = G.wp(s10, 0.45)
    old = G.G_AREA; G.G_AREA = free
    try: svg = G.wh_svg(plan, 1)
    finally: G.G_AREA = old
    F, st = G.FR, G.whst; om = (st['off0'] + st['off1']) / 2
    if st['NR'] != 22:                                   # wh_stair writes the 22 x 17 cm of the stair as drawn till now
        k = '٢٢ درجة × ١٧ سم'; assert svg.count(k) == 1
        svg = svg.replace(k, f'{G.ar(st["NR"], 0)} درجة × {G.ar(st["rise"] / st["NR"] * 100, 2)} سم')
    labs = [G.text(F, f'مساحة بيت السلم: ٣ × ٥ = {G.ar(core, 0)} م²', *G.cp(2.5, -0.5), rot=G.rot_along(G.cp(0, 0), G.cp(5, 0))),   # outside its wall: the box itself is full of stair lines
            G.text(F, f'مساحة سلم المخزن: {G.ar(L, 2)} × {G.ar(W, 2)} ≈ {G.ar(ws, 1)} م²', *G.wp((st['s_bot'] + st['s_top']) / 2 - 0.4, st['off1'] + 0.95),
                   rot=G.rot_along(G.wp(st['s_bot'], om), G.wp(st['s_top'], om)))]
    if cols: labs += stair_columns(F)
    return svg[:svg.rindex('</svg>')] + '\n'.join(labs) + '\n</svg>', free

def build(kind='open', steps=None, cols=False):
    if steps: set_steps(steps)
    core, L, W, ws = stair_areas()
    sub2 = ''
    if kind == 'stairs':
        svg, free = stairs_floor1(G.PLANS[2], cols)
        title, name, hname = 'الدور الأول: المخزن بالسلمين', 'الدور-الأول-بالسلمين', 'floor1_stairs.html'
        if steps: name, hname = f'الدور-الأول-سلم-المخزن-{G.ar(steps, 0)}-درجة', f'floor1_stairs{steps}.html'
        if cols:
            name, hname = name + '-بعمودين', hname.replace('.html', '_cols.html')
            sub2 = '<p class="sub">عمود ١٤ و١٥: عمودين صغيرين ٢٥ × ٢٥ سم تحت نص سلم المخزن، وفوقهم كمرة صغيرة</p>'
        sub = (f'ترشيح رقم ١ · الدور كله ≈ {G.ar(G.area(G.BLD) - G.area(G.DUCT), 0)} م²: بيت السلم {G.ar(core, 0)} م²، '
               f'سلم المخزن {G.ar(ws, 1)} م²، والفاضي ≈ {G.ar(free, 0)} م²')
    else:
        svg, free = open_floor1(G.PLANS[2])
        title, name, hname = 'الدور الأول: المخزن من غير سلالم', 'الدور-الأول-من-غير-سلالم', 'floor1_open.html'
        sub = 'ترشيح رقم ١ · من غير بيت السلم ومن غير سلم المخزن للدور التاني'
    page = (f'<div class="page"><div class="hdr"><div><h1>{title}</h1>'
            f'<p class="sub">{sub}</p>{sub2}</div><div class="pg"></div></div>'
            f'<div class="big">{svg}</div></div>')
    html = ('<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>' + title.replace(': ', ' — ') + '</title><style>'
            + G.CSS + '</style></head><body>' + page + '</body></html>')
    hp = os.path.join(G.OUT, hname); open(hp, 'w', encoding='utf-8').write(html)
    pdf = os.path.join(G.OUT, name + '.pdf')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=180)
    print('pdf', os.path.getsize(pdf) if os.path.exists(pdf) else 0)
    print(f'whole floor {G.area(G.BLD):.2f} m2; stair house {core:.2f}; warehouse stair + landing {L:.2f} x {W:.2f} = {ws:.2f}; '
          f'free {free:.2f} (duct {G.area(G.DUCT):.2f}); old label {G.G_AREA:.2f}')

if __name__ == '__main__':
    build('stairs' if 'stairs' in sys.argv[1:] else 'open', next((int(a) for a in sys.argv[1:] if a.isdigit()), None), 'cols' in sys.argv[1:])
