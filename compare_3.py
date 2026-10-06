# -*- coding: utf-8 -*-
"""The three flat layouts we kept, one page each with a big title, for side-by-side viewing (his ask, 6 Oct 2026).
python3 compare_3.py  ->  2d/compare_3.html + 2d/الترشيحات-التلاتة.pdf"""
import os, subprocess
import gen2d as G
items = [(2, 'ترشيح ٢', 'الهول بحيطة وباب، و٣ أوض نوم'), (7, 'ترشيح ٢ب', 'الصالة مفتوحة على المدخل، و٣ أوض نوم'),
         (8, 'ترشيح ٣', 'الصالة مفتوحة، و٤ أوض نوم')]
pages = []
for i, (k, title, sub) in enumerate(items, 1):
    pages.append(f'''<div class="page"><div class="hdr"><div><h1>{title}</h1><p class="sub">{sub} · الدور الثالث (والرابع زيه)</p></div><div class="pg">{G.ar(i, 0)} من ٣</div></div>
<div class="big">{G.flat_svg(G.PLANS[k], 3)}</div></div>''')
html = '<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>الترشيحات التلاتة</title><style>' + G.CSS + '</style></head><body>' + ''.join(pages) + '</body></html>'
hp = os.path.join(G.OUT, 'compare_3.html'); open(hp, 'w', encoding='utf-8').write(html)
pdf = os.path.join(G.OUT, 'الترشيحات-التلاتة.pdf')
subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=180)
print('pdf', os.path.getsize(pdf) if os.path.exists(pdf) else 0)
