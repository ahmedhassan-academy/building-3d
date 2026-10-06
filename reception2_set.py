# -*- coding: utf-8 -*-
"""The full 7-page building set for "ترشيح ريسبشن ٢" (his pick, 6 Oct 2026): warehouse floors 1-2, flats on floors 3-4,
columns and the warehouse stair, drawn by gen2d.build from option B of reception5_options.
python3 reception2_set.py  ->  2d/set9.html + 2d/ترشيح-ريسبشن-٢.pdf"""
import gen2d as G
import reception5_options as R

K = 9
G.DATE = '٦ أكتوبر ٢٠٢٦'                             # this set is made today; gen2d's other sets keep their date
p = R.make(next(o for o in R.OPTIONS if o['key'] == 'B'))
p['cover_note'] = ('ريسبشن طويل ٩.٤ م على حيطة الجار الشمال، من البلكونة على شارع ١٢ لحد المطبخ (≈ ٣٨ م²)، '
                   'والبلكونة ٢.٥ × ١.٥ فيه وبابها ٢ م · نوم ١ (≈ ١٧) ونوم ٢ في الركن على الشارعين (≈ ٢٢) بيفتحوا على دخلة ١ × ١.٦ من الريسبشن، '
                   'ونوم ٣ على شارع ٦ (≈ ١٩) بتفتح على الريسبشن · المطبخ والحمام والمنور والسلم وباب الشقة زي ترشيح ٣.')
p['no_hoist'] = True                                  # his ask (6 Oct): no hoist hatch in the floor-2 slab
G.PLANS[K] = p
G.COLINFO[K] = G.COLINFO[2]
G.WELL_NOTE[K] = 'ريسبشن طويل على حيطة الجار، والبلكونة فيه'
G.KNAME[K] = 'ريسبشن ٢'
G.PDFNAME[K] = '-ريسبشن-٢'

if __name__ == '__main__':
    G.build(K)
