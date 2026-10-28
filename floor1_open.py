# -*- coding: utf-8 -*-
"""His ask (28 Oct 2026): floor 1 of ترشيح ١ as on page 1 of ترشيح-رقم-١.pdf, but without the building's stair house
and without the warehouse stair up to floor 2 (the whole floor open), and tell him its area.
python3 floor1_open.py  ->  2d/الدور-الأول-من-غير-سلالم.pdf"""
import os, subprocess
import gen2d as G
import columns4_pdf as C          # loading it puts the coloured columns, their legend and the hatch into gen2d

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

def build():
    svg, free = open_floor1(G.PLANS[2])
    page = (f'<div class="page"><div class="hdr"><div><h1>الدور الأول: المخزن من غير سلالم</h1>'
            f'<p class="sub">ترشيح رقم ١ · من غير بيت السلم ومن غير سلم المخزن للدور التاني</p></div><div class="pg"></div></div>'
            f'<div class="big">{svg}</div></div>')
    html = ('<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>الدور الأول من غير سلالم</title><style>'
            + G.CSS + '</style></head><body>' + page + '</body></html>')
    hp = os.path.join(G.OUT, 'floor1_open.html'); open(hp, 'w', encoding='utf-8').write(html)
    pdf = os.path.join(G.OUT, 'الدور-الأول-من-غير-سلالم.pdf')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=180)
    print('pdf', os.path.getsize(pdf) if os.path.exists(pdf) else 0)
    st = G.whst; stair = (st['s_bot'] - (st['s_top'] - 1.2)) * (st['off1'] - st['off0'])
    print(f'open floor {free:.2f} m2 (outline {G.area(G.BLD):.2f} - duct {G.area(G.DUCT):.2f}); '
          f'stair house {G.area(G.CORE):.2f}; warehouse stair + landing {stair:.2f}; old label {G.G_AREA:.2f}')

if __name__ == '__main__':
    build()
