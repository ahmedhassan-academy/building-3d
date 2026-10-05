# -*- coding: utf-8 -*-
"""Proposal 2 vs 2b with the one difference circled (his ask, 5 Oct 2026).
python3 compare_2_2b.py  ->  2d/compare_2_2b.html + 2d/الفرق-بين-٢-و-٢ب.pdf (2 A4 pages)"""
import os, subprocess
import gen2d as G

F = G.FR; PINK = '#C2185B'
def mark(svg, note):
    X, Y = F.X(-6.9), F.Y(12.85)
    m = (f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{2.4 * F.s:.1f}" ry="{1.05 * F.s:.1f}" fill="{PINK}" fill-opacity="0.08" stroke="{PINK}" stroke-width="3" stroke-dasharray="8 5"/>'
         f'<ellipse cx="{F.X(-6.0):.1f}" cy="{F.Y(10.8):.1f}" rx="{0.55 * F.s:.1f}" ry="{1.75 * F.s:.1f}" fill="{PINK}" fill-opacity="0.08" stroke="{PINK}" stroke-width="3" stroke-dasharray="8 5"/>'
         f'<line x1="{F.X(-8.2):.1f}" y1="{F.Y(10.0):.1f}" x2="{F.X(-7.5):.1f}" y2="{F.Y(11.85):.1f}" stroke="{PINK}" stroke-width="2"/>'
         f'<line x1="{F.X(-7.6):.1f}" y1="{F.Y(9.85):.1f}" x2="{F.X(-6.5):.1f}" y2="{F.Y(10.3):.1f}" stroke="{PINK}" stroke-width="2"/>'
         f'<text x="{F.X(-8.6):.1f}" y="{F.Y(9.72):.1f}" text-anchor="middle" dominant-baseline="central" style="fill:{PINK};font-size:12px;font-weight:700">{note}</text>')
    return svg.replace('</svg>', m + '</svg>')

pages = []
for i, (k, title, note) in enumerate(((2, 'ترشيح ٢: الهول ليه حيطة وباب على الصالة', 'هنا الحيطتين والباب'),
                                      (7, 'ترشيح ٢ب: الصالة مفتوحة على المدخل والهول', 'الحيطتين اتشالوا')), 1):
    svg = mark(G.flat_svg(G.PLANS[k], 3), note)
    pages.append(f'''<div class="page"><div class="hdr"><div><h2>{title}</h2><p class="sub">الدور الثالث · الدواير الوردي = الفرق بين الترشيحين</p></div><div class="pg">صفحة {G.ar(i, 0)} من ٢</div></div>
<div class="big">{svg}</div>
<div class="foot"><span>الفرق بين ترشيح ٢ و ٢ب · {G.DATE}</span><span>صفحة {G.ar(i, 0)} من ٢</span></div></div>''')
html = '<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>الفرق بين ٢ و ٢ب</title><style>' + G.CSS + '</style></head><body>' + ''.join(pages) + '</body></html>'
hp = os.path.join(G.OUT, 'compare_2_2b.html'); open(hp, 'w', encoding='utf-8').write(html)
pdf = os.path.join(G.OUT, 'الفرق-بين-٢-و-٢ب.pdf')
subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=180)
print('pdf', os.path.getsize(pdf) if os.path.exists(pdf) else 0)
