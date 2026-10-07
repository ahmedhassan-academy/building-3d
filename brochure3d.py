# -*- coding: utf-8 -*-
"""A designed PDF of the 3D model for "ترشيح ريسبشن ٢" (his ask, 7 Oct 2026): cover, outside views, the flat from above,
inside views, the warehouse floors. Pictures are renders of index.html (?p=r2&ui=0&cam=...) saved in a folder.
python3 brochure3d.py <renders folder>  ->  2d/ترشيح-ريسبشن-٢-3D.pdf"""
import os, subprocess, sys
import gen2d as G

RENDERS = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(os.path.dirname(RENDERS), 'pylib'))
import fitz

def jpg(name, width, crop=(0, 0, 1, 1)):
    """the render as a JPEG at the given pixel width, cropped to (x0, y0, x1, y1) as fractions (keeps the PDF light)"""
    src = os.path.join(RENDERS, name + '.png'); out = os.path.join(RENDERS, f'{name}_{width}.jpg')
    pix = fitz.Pixmap(src)
    if pix.alpha: pix = fitz.Pixmap(pix, 0)
    doc = fitz.open(); page = doc.new_page(width=pix.width, height=pix.height); page.insert_image(page.rect, pixmap=pix)
    W, H = pix.width, pix.height; clip = fitz.Rect(crop[0] * W, crop[1] * H, crop[2] * W, crop[3] * H)
    page.get_pixmap(clip=clip, matrix=fitz.Matrix(width / clip.width, width / clip.width)).save(out, jpg_quality=84)
    return out

DATE = '٧ أكتوبر ٢٠٢٦'
LINK = 'ahmedhassan-academy.github.io/building-3d'
ROOMS = [('ريسبشن', '٩.٤ × ٤.١', '٣٨'), ('نوم ١', '٣.٦ × ٤.٧', '١٧'), ('نوم ٢', '٤.٨ × ٤.٦', '٢٢'), ('نوم ٣', '٥.٧ × ٣.٣', '١٩'),
         ('مطبخ', '٣ × ٣.٣', '١٠'), ('حمام', '٢.٥ × ١.٥', '٣'), ('دخلة', '١ × ١.٦', '٢')]

CSS = '''
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
@page{size:A4 landscape;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;color:#1D2026;font-family:"Cairo","Geeza Pro","Al Nile",sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:297mm;height:210mm;position:relative;overflow:hidden;page-break-after:always;padding:14mm 16mm 12mm}
.page:last-child{page-break-after:auto}
.cover{padding:0}
.cover img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.cover .panel{position:absolute;top:0;right:0;bottom:0;width:112mm;background:linear-gradient(90deg,rgba(255,255,255,0) 0,rgba(255,255,255,.93) 16mm,#fff 30mm);padding:20mm 16mm 14mm 26mm;display:flex;flex-direction:column}
.over{font-size:3.4mm;color:#5B6270;font-weight:600;letter-spacing:.2mm}
.cover h1{font-size:15mm;line-height:1.15;margin:4mm 0 2mm;font-weight:800;color:#1D2026}
.cover h1 span{color:#1F5FBF}
.cover .sub{font-size:5.2mm;font-weight:600;color:#3A414B;margin:0 0 7mm;line-height:1.5}
.chips{display:flex;flex-direction:column;gap:2.6mm}
.chip{display:flex;justify-content:space-between;align-items:baseline;border-bottom:.3mm solid #D5D9E0;padding:0 0 2mm;font-size:3.8mm}
.chip b{font-size:4.4mm;color:#1F5FBF;font-weight:700}
.cover .foot{margin-top:auto;font-size:3mm;color:#5B6270;line-height:1.7}
.hdr{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:6mm}
.hdr h2{font-size:8mm;margin:0;font-weight:800;line-height:1.2}
.hdr h2 small{display:block;font-size:3.6mm;font-weight:600;color:#5B6270;margin-top:1mm}
.hdr .pg{font-size:3.2mm;color:#5B6270;font-weight:600}
.bar{height:1.2mm;width:18mm;background:#1F5FBF;border-radius:1mm;margin-bottom:3mm}
figure{margin:0}
figure img{width:100%;display:block;border-radius:3mm}
figcaption{font-size:3.4mm;color:#3A414B;margin-top:2.2mm;line-height:1.6}
figcaption b{color:#1D2026}
.two{display:grid;grid-template-columns:1fr 1fr;gap:7mm}
.wide{display:grid;grid-template-columns:2.1fr 1fr;gap:8mm;align-items:start}
.three{display:grid;grid-template-columns:1.55fr 1fr;grid-template-rows:auto auto;gap:6mm 7mm}
.three figure.big{grid-row:1 / span 2}
table{border-collapse:collapse;width:100%;font-size:3.8mm}
th,td{padding:2mm 1mm;border-bottom:.3mm solid #D5D9E0;text-align:right}
th{font-size:3.2mm;color:#5B6270;font-weight:600}
td.n,th.n{text-align:left;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.tot td{border-bottom:0;font-weight:700;color:#1F5FBF;font-size:4.2mm}
.note{font-size:3.2mm;color:#5B6270;line-height:1.7;margin-top:4mm}
.det figure img{height:58mm;object-fit:cover} .det figcaption{font-size:3.1mm;margin-top:1.2mm}
.pfoot{position:absolute;left:16mm;right:16mm;bottom:7mm;display:flex;justify-content:space-between;font-size:2.8mm;color:#8A8F99}
'''

def foot(i, N): return f'<div class="pfoot"><span>عمارة المخزن والشقتين · ترشيح ريسبشن ٢ · صور من الموديل الـ 3D · {DATE}</span><span>{G.ar(i, 0)} / {G.ar(N, 0)}</span></div>'
def hdr(t, sub, i, N): return f'<div class="bar"></div><div class="hdr"><h2>{t}<small>{sub}</small></h2><div class="pg">{G.ar(i, 0)} / {G.ar(N, 0)}</div></div>'
def fig(src, cap, cls=''): return f'<figure class="{cls}"><img src="file://{src}"><figcaption>{cap}</figcaption></figure>'

def build():
    N = 6
    cover = jpg('cover', 3200)
    pages = [f'''<div class="page cover"><img class="bg" src="file://{cover}"><div class="panel">
<div class="over">عمارة المخزن والشقتين · ناصية شارع&nbsp;١٢ وشارع&nbsp;٦</div>
<h1>ترشيح <span>ريسبشن ٢</span></h1>
<p class="sub">ريسبشن طويل على حيطة الجار<br>و٣ أوض نوم في كل شقة<br><span style="color:#1F5FBF">واجهة على طريقة أليفا — ماونتن فيو</span></p>
<div class="chips">
<div class="chip"><span>الأدوار</span><b>٤ أدوار</b></div>
<div class="chip"><span>المخزن (الدور الأول + التاني)</span><b>≈ ٨٩ + ١١٣ م²</b></div>
<div class="chip"><span>شقة في الدور التالت والرابع</span><b>≈ ١١١ م² صافي</b></div>
<div class="chip"><span>البروز من الدور التاني لفوق</span><b>١.٨٠ م + ١.٢٠ م</b></div>
</div>
<div class="foot">صور من الموديل الـ 3D · {DATE}<br>الموديل كامل وتقدر تمشي جواه:<br><span dir="ltr">{LINK}</span></div>
</div></div>''']
    pages.append(f'''<div class="page">{hdr('العمارة من بره', 'واجهة على طريقة عمارات أليفا (ماونتن فيو)، على الشارعين', 2, N)}
<div class="two">{fig(jpg('front12', 2000, (0.12, 0, 0.88, 1)), '<b>الواجهة على شارع ١٢:</b> سقف أزرق مايل بشبابيك، وإطارات وكرانيش بيضا، والبروز ١.٨٠ م من الدور التاني لفوق.')}
{fig(jpg('side6', 2000, (0.06, 0, 0.74, 1)), '<b>من شارع ٦:</b> نفس الواجهة لافة على الناصية، والبروز ١.٢٠ م من الدور التاني لفوق.')}</div>
{foot(2, N)}</div>''')
    pages.append(f'''<div class="page">{hdr('تفاصيل الواجهة', 'كل حتة في الواجهة، ومن إيه ممكن تتعمل', 3, N)}
<div class="two det" style="gap:4mm 7mm">{fig(jpg('d_roof', 1600, (0.08, 0.05, 0.92, 0.95)), '<b>السقف:</b> تاج مايل ١.٤٥ م بقرميد أزرق، فيه شبابيك بارزة بيضا على نفس خط الشبابيك اللي تحت، وشباك دايري في النص.')}
{fig(jpg('d_win', 1600, (0.08, 0.05, 0.92, 0.95)), '<b>الشبابيك والبلكونة:</b> إطار أبيض حوالين كل شباك، ومثلث فوق شبابيك الدور الرابع، وكرنيشة عند كل دور، ودرابزين أبيض بعواميد.')}
{fig(jpg('d_ground', 1600, (0.08, 0.05, 0.92, 0.95)), '<b>الدور الأرضي:</b> حجر أبيض بفواصل بالعرض، وعمودين حجر حوالين باب المخزن، وكوابيل بيضا تحت البروز.')}
{fig(jpg('d_door', 1600, (0.08, 0.05, 0.92, 0.95)), '<b>باب السلم على شارع ٦:</b> قوس أبيض وزجاج نص دايرة فوق الباب، وحجر في النص (مفتاح القوس).')}</div>
<p class="note">الحيطان دهان رمادي فاتح بحزوز بالعرض · الإطارات والكرانيش والكوابيل فوم أو GRC أبيض · الأرضي حجر جلالة أبيض · السقف قرميد أزرق على هيكل حديد خفيف فوق السطح · الدرابزين خرسانة مسبوقة أو GRC أبيض.</p>
{foot(3, N)}</div>''')
    rows = ''.join(f'<tr><td>{n}</td><td class="n">{d}</td><td class="n">≈ {a}</td></tr>' for n, d, a in ROOMS)
    pages.append(f'''<div class="page">{hdr('الشقة من فوق', 'الدور التالت (والرابع زيه) بالفرش، والسقف مشال علشان تبان', 4, N)}
<div class="wide">{fig(jpg('flat3', 2400, (0.13, 0.08, 0.87, 0.97)), 'الريسبشن ماشي على حيطة الجار من البلكونة لحد المطبخ: قعدة عند البلكونة وسفرة جنب المطبخ. التلات أوض على الشارعين.')}
<div><table><tr><th>الأوضة</th><th class="n">المقاس (م)</th><th class="n">م²</th></tr>{rows}<tr class="tot"><td>الصافي</td><td></td><td class="n">≈ ١١١</td></tr></table>
<p class="note">بلكونة ٢.٥ × ١.٥ في الريسبشن · بيت السلم ٣ × ٦.٢ · المنور ٢.٥ × ١.١ للمطبخ والحمام.</p></div></div>
{foot(4, N)}</div>''')
    pages.append(f'''<div class="page">{hdr('الشقة من زوايا تانية', 'الدور التالت والسقف مشال، وصورة من جوه نوم ٢', 5, N)}
<div class="three">{fig(jpg('dh_rec', 2400, (0.27, 0.06, 0.9, 0.97)), '<b>الريسبشن الطويل:</b> من البلكونة على شارع ١٢ لحد المطبخ، قعدة عند البلكونة وسفرة عند المطبخ.', 'big')}
{fig(jpg('dh_corner', 1400, (0.1, 0.12, 0.95, 0.97)), '<b>من ناصية الشارعين:</b> نوم ١ ونوم ٢ على شارع ١٢، ونوم ٣ على شارع ٦.')}
{fig(jpg('bed2', 1400), '<b>جوه نوم ٢:</b> أوضة الركن، شباك على كل شارع.')}</div>
{foot(5, N)}</div>''')
    pages.append(f'''<div class="page">{hdr('المخزن', 'الدور الأول والتاني، والسقف مشال علشان تبان', 6, N)}
<div class="two">{fig(jpg('wh1', 2000, (0.16, 0, 0.84, 1)), '<b>الدور الأول ≈ ٨٩ م²:</b> باب رول ٤.٥ م على شارع ١٢، وسلم داخلي للدور التاني على حيطة الجار.')}
{fig(jpg('wh2', 2000, (0.16, 0, 0.84, 1)), '<b>الدور التاني ≈ ١١٣ م²:</b> فيه البروز على الشارعين، ومن غير فتحة ونش.')}</div>
{foot(6, N)}</div>''')
    html = '<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>ترشيح ريسبشن ٢ — 3D</title><style>' + CSS + '</style></head><body>' + ''.join(pages) + '</body></html>'
    hp = os.path.join(RENDERS, 'brochure3d.html'); open(hp, 'w', encoding='utf-8').write(html)
    pdf = os.path.join(G.OUT, 'ترشيح-ريسبشن-٢-3D.pdf')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-sandbox', '--allow-file-access-from-files',
                    '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file://' + hp], capture_output=True, text=True, timeout=240)
    print('pdf', os.path.getsize(pdf) if os.path.exists(pdf) else 0, 'pages', len(fitz.open(pdf)) if os.path.exists(pdf) else 0)
    return pdf

if __name__ == '__main__':
    build()
