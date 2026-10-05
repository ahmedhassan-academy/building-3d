# -*- coding: utf-8 -*-
"""Regenerate the 2D A4 sets (7 pages per proposal) from the 3D model data (b3d/data3d.js).
python3 gen2d.py  ->  2d/set{k}.html + b3d/2d/ترشيح{k}.pdf  for k = 1..6"""
import json, math, os, re, subprocess
S=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(S,'2d'); os.makedirs(OUT,exist_ok=True)
raw=open(os.path.join(S,'data3d.js'),encoding='utf-8').read()
D=json.loads(raw[raw.index('{'):raw.rindex('}')+1])
SH=D['shared']; PLANS={int(k):v for k,v in D['plans'].items()}
DATE='٥ أكتوبر ٢٠٢٦'
AR='٠١٢٣٤٥٦٧٨٩'
def ar(v,d=1):
    if isinstance(v,str): return v
    s=f'{v:.{d}f}' if d else str(int(round(v)))
    if s.startswith('-') and float(s)==0: s=s[1:]
    return ''.join(AR[int(c)] if c.isdigit() else c for c in s)
lw=lambda y: SH['lw'][0]+SH['lw'][1]*(y-SH['lw'][2])
rw=lambda y: SH['rw'][0]+SH['rw'][1]*(y-SH['rw'][2])
tw=lambda x: SH['tw'][0]+SH['tw'][1]*(x-SH['tw'][2])
T=lambda p: (float(p[0]),float(p[1]))
A,D2,C2,B2,P1,P2,P3=[T(SH[k]) for k in ('A','D2','C2','B2','P1','P2','P3')]
BLD=[T(p) for p in SH['BLD']]; CORE=[T(p) for p in SH['CORE']]; SLAB=[T(p) for p in SH['SLAB']]
HOIST=[T(p) for p in SH['HOIST']]; DUCT=[T(p) for p in SH['DUCT']]; LAND=[T(p) for p in SH['LAND']]
STRIP1=[T(p) for p in SH['STRIP1']]; STRIP2=[T(p) for p in SH['STRIP2']]
XL=lw(4.05)                                                   # neighbour line at the projection front (about -12.53)
XR=rw(4.05)                                                   # 6 m street line at the projection front (about -2.07)
SK=math.hypot(1,SH['rw'][1]); NRM=(1/SK,-SH['rw'][1]/SK)     # outward normal of the 6 m street wall
def sh(p,d): return (p[0]+NRM[0]*d,p[1]+NRM[1]*d)              # a point pushed d metres out over the 6 m street
def rw2(y,d): return rw(y)+d*SK                                # the 6 m street wall line pushed out d metres
PROJ=[(XL,4.05),(XR,4.05),D2,C2,B2,A]                 # floor-2 outline with the 1.80 projection
F2=[(XL,4.05),(XR,4.05),D2,P1,P2,P3,B2,A]
def area(p): return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))/2
G_AREA=area(SLAB)-area(DUCT); F2_AREA=area(F2)-1.2*3.4-area(HOIST)-area(DUCT)

# ---- 5 Oct 2026, his ask, proposal 2 only. 2D only: the 3D page still reads the old layout from data3d.js.
# The balconies stay exactly as they were (4.6 / 4.2 x 1.80): he asked not to touch them.
CB5=12.73+(-5.0+5.03)*(11.5-12.73)/(-0.185+5.03)
def edit_p2(p):
    R={r['n']:r for r in p['rooms']}; W={r['n']:r for r in p['rows']}
    lv,ln=R['صالة']['p'],R['غسيل']['p']
    R['صالة']['p']=lv[:3]+ln[1:]                                   # the laundry corner joins the living room
    W['صالة']['a']=area([T(q) for q in R['صالة']['p']]); W['صالة']['dim']='٦.٤ × ٣.٢ + ٢ × ١'
    x_core=P2[0]+(14.9-P2[1])*(P3[0]-P2[0])/(P3[1]-P2[1])
    R['منور']['p']=[[-7.0,14.9],[x_core,14.9],list(P3),[-7.0,tw(-7.0)]]   # the pantry joins the light well: 2.5 wide, open up to the back neighbour's wall
    W['منور'].update(w=2.5,h=1.1,a=area([T(q) for q in R['منور']['p']]),c=[-5.8,15.45])
    p['rooms']=[r for r in p['rooms'] if r['n'] not in ('غسيل','كرار')]
    p['rows']=[r for r in p['rows'] if r['n'] not in ('غسيل','كرار')]
    for w in p['walls']:
        if w['a'][1]==12.4 and w['b'][1]==12.4:                    # living/hall wall: drop the part that closed the laundry
            d=-8.6-w['a'][0]; w['a']=[-8.6,12.4]
            for op in w['op']: op['u0']-=d; op['u1']-=d
    p['walls']=[w for w in p['walls'] if not (w['a']==[-5.5,14.9] or w['a']==[-7.0,15.9])]   # pantry wall + old light-well back wall
    W['حمام']['c']=[-5.75,14.5]; W['هول']['c']=[-7.8,12.9]          # labels moved off the door swings
    # private hall for the bedrooms (his asks, 5 Oct): 1.0 m wide, straight from the entrance hall down to the 12 m facade;
    # bedroom 1 widens 0.5 m to reach it, bedroom 2 gives 1.5 m to it, and all three bedrooms open off it
    b1,b2,lv,hl=R['نوم ١']['p'],R['نوم ٢']['p'],R['صالة']['p'],R['هول']['p']
    R['نوم ١']['p']=[b1[0],[-6.0,5.85],[-6.0,9.2],b1[3]]
    R['نوم ٢']['p']=[[-5.0,5.85],b2[1],b2[2],[-5.0,9.2]]
    R['صالة']['p']=[lv[0],[-6.0,9.2],[-6.0,12.4]]+lv[3:]
    R['هول']['p']=[hl[0],[-6.0,12.4],[-6.0,5.85],[-5.0,5.85]]+hl[2:]
    for n in ('نوم ١','نوم ٢','صالة','هول'): W[n]['a']=area([T(q) for q in R[n]['p']])
    W['نوم ١'].update(dim='٥.٧ × ٣.٤',c=[-9.0,7.4]); W['نوم ٢'].update(dim='٣.٨ × ٣.٤',c=[-3.2,7.4])
    W['صالة']['dim']='٥ × ٣.٢ + ٢ × ١'; W['هول']['dim']='المدخل + هول النوم'
    p['walls']=[w for w in p['walls'] if w['a'] not in ([-11.235,9.2],[-6.5,5.959])]       # old walls around bedrooms 1 and 2
    p['walls']+=[{'a':[-11.235,9.2],'b':[-6.0,9.2],'t':0.12,'op':[]},                       # bedroom 1 | living room
                 {'a':[-5.0,9.2],'b':[-0.888,9.2],'t':0.12,'op':[]},                        # bedroom 2 | bedroom 3
                 {'a':[-6.0,5.96],'b':[-6.0,12.4],'t':0.12,'op':[{'u0':1.84,'u1':2.74,'z0':0,'z1':2.1,'k':'door'}]},   # hall | bedroom 1 + living; bedroom 1's side door
                 {'a':[-5.0,5.96],'b':[-5.0,9.2],'t':0.12,'op':[{'u0':2.24,'u1':3.14,'z0':0,'z1':2.1,'k':'door'}]}]    # hall | bedroom 2; bedroom 2's door
    for w in p['walls']:
        if w['a']==[-8.6,12.4] and w['b'][1]==12.4: w['op'].append({'u0':2.6,'u1':3.6,'z0':0,'z1':2.1,'k':'open'})   # entrance hall opens into the bedroom hall
        if w['a']==[-5.0,9.2] and w['b'][0]==-5.0: w['op'].append({'u0':1.3,'u1':2.2,'z0':0,'z1':2.1,'k':'door'})  # bedroom 3's door
    p['leaves']=[l for l in p['leaves'] if l['h'] not in ([-9.45,9.2],[-6.15,9.2])]
    p['leaves']+=[{'h':[-6.0,8.7],'along':[0,-1],'out':[-1,0],'w':0.9},                     # bedroom 1
                  {'h':[-5.0,9.1],'along':[0,-1],'out':[1,0],'w':0.9},                      # bedroom 2
                  {'h':[-5.0,11.4],'along':[0,-1],'out':[1,0],'w':0.9}]                     # bedroom 3
    p['front'][1].update(u0=7.22,u1=10.02)                                                  # bedroom 2's balcony door moves off the hall end
    # balconies 1.0 deep instead of 1.80 (his ask); the back 0.80 of each balcony joins the bedroom behind it, so bedrooms 1 and 2
    # come forward 0.80 m. Balcony 2 drops the 1.2 m that sat in front of the hall end (4.2 -> 3.0 long).
    p['balc']=[[-11.6,-7.0],[-5.0,-2.0]]; p['balc_d']=1.0; p['balc_y0']=5.05
    p['bays']=[[-11.6,-7.0,5.05],[-5.0,-2.0,5.05]]
    b1,b2=R['نوم ١']['p'],R['نوم ٢']['p']
    R['نوم ١']['p']=[b1[0],[-11.6,5.85],[-11.6,5.05],[-7.0,5.05],[-7.0,5.85]]+b1[1:]
    R['نوم ٢']['p']=[[-5.0,5.05],[-2.0,5.05],[-2.0,5.85]]+b2[1:]
    W['نوم ١'].update(a=area([T(q) for q in R['نوم ١']['p']]),dim='٥.٧ × ٣.٤ + ٤.٦ × ٠.٨')
    W['نوم ٢'].update(a=area([T(q) for q in R['نوم ٢']['p']]),dim='٣.٨ × ٣.٤ + ٣ × ٠.٨')
    for op in p['front']: op['y']=5.05                                                      # balcony doors sit on the new room fronts
    # balcony 2 goes (his ask): bedroom 2 comes out over it to the old balcony edge, with a 1.50 window in the new front
    p['balc']=[[-11.6,-7.0]]; p['bays']=[[-11.6,-7.0,5.05],[-5.0,-1.62,4.05]]                # bedroom 2 runs out right to the street corner
    R['نوم ٢']['p']=[[-5.0,4.05],[-1.62,4.05]]+R['نوم ٢']['p'][3:]
    W['نوم ٢'].update(a=area([T(q) for q in R['نوم ٢']['p']]),dim='٣.٨ × ٣.٤ + ٣.٤ × ١.٨')
    p['front'][1].update(u0=8.06,u1=9.56,y=4.05,k='win')                                    # window centred on the new front
    # the open roof piece between them (x -7.0 -> -5.0) comes out too, split between the two bedrooms (his pick):
    # bedroom 1 takes x -7.0 -> -6.0, bedroom 2 takes x -6.0 -> -5.0 (in front of the bedroom hall's end)
    p['bays']=[[-11.6,-7.0,5.05],[-7.0,-1.62,4.05]]
    p['outline3']=[A,[-11.6,5.85],[-11.6,5.05],[-7.0,5.05],[-7.0,4.05],[-1.62,4.05],D2,C2,B2]
    b1=R['نوم ١']['p']; i=b1.index([-7.0,5.85]); R['نوم ١']['p']=b1[:i]+[[-7.0,4.05],[-6.0,4.05]]+b1[i+2:]
    R['نوم ٢']['p']=[[-6.0,4.05]]+R['نوم ٢']['p'][1:]+[[-5.0,5.85],[-6.0,5.85]]
    W['نوم ١'].update(a=area([T(q) for q in R['نوم ١']['p']]),dim='٥.٧ × ٣.٤ + البروز')
    W['نوم ٢'].update(a=area([T(q) for q in R['نوم ٢']['p']]),dim='٣.٨ × ٣.٤ + البروز')
    for w in p['walls']:
        if w['a']==[-6.0,5.96]:                                                             # bedroom 1 / hall wall runs on out to the new front
            w['a']=[-6.0,4.05]
            for op in w['op']: op['u0']+=1.91; op['u1']+=1.91
    p['walls'].append({'a':[-6.0,5.85],'b':[-5.0,5.85],'t':0.12,'op':[]})                  # end of the bedroom hall
    p['front'][1].update(u0=7.56,u1=9.06)                                                   # bedroom 2's window re-centred on its wider front
    # the 0.52 m strip by the left neighbour comes out too (his ask) and joins bedroom 1; balcony 1 is now recessed, open only to the street
    p['bays']=[[-12.12,-11.6,4.05],[-11.6,-7.0,5.05],[-7.0,-1.62,4.05]]
    p['outline3']=[A,[-12.12,4.05],[-11.6,4.05],[-11.6,5.05],[-7.0,5.05],[-7.0,4.05],[-1.62,4.05],D2,C2,B2]
    b1=R['نوم ١']['p']; R['نوم ١']['p']=[[-12.12,4.05],[-11.6,4.05]]+b1[2:]+[b1[0]]
    W['نوم ١']['a']=area([T(q) for q in R['نوم ١']['p']])
    # balcony 1 becomes 2.5 long x 1.5 deep (his ask), centred where the old one was; the rest of the old balcony joins bedroom 1
    p['balc']=[[-10.55,-8.05]]; p['balc_d']=1.5; p['balc_y0']=5.55
    p['bays']=[[-12.12,-10.55,4.05],[-10.55,-8.05,5.55],[-8.05,-1.62,4.05]]
    p['outline3']=[A,[XL,4.05],[-10.55,4.05],[-10.55,5.55],[-8.05,5.55],[-8.05,4.05],[-1.62,4.05],D2,C2,B2]
    R['نوم ١']['p']=[[XL,4.05],[-10.55,4.05],[-10.55,5.55],[-8.05,5.55],[-8.05,4.05],[-6.0,4.05],[-6.0,9.2],[-11.355,9.2],[-12.12,5.85]]
    W['نوم ١']['a']=area([T(q) for q in R['نوم ١']['p']])
    p['front'][0].update(u0=1.82,u1=3.82,y=5.55)                                            # balcony door 2.0, centred in the balcony
    # the forward part's right wall follows the slanted 6 m street facade too (no kink at the street corner)
    fix=lambda pts:[[XR,4.05] if list(q)==[-1.62,4.05] else q for q in pts]
    p['outline3']=fix(p['outline3']); R['نوم ٢']['p']=fix(R['نوم ٢']['p'])
    W['نوم ٢']['a']=area([T(q) for q in R['نوم ٢']['p']])
    p['front'][1].update(u0=7.33,u1=8.83)                                                   # bedroom 2's window re-centred
    # 1.20 m out over the 6 m street from floor 2 up (his ask): all of it goes into bedrooms 2 and 3 and the stair box
    d=1.2; p['side']=d
    p['outline3']=[q for q in p['outline3'] if list(q) not in ([XR,4.05],list(D2),list(C2))]
    i=[list(q) for q in p['outline3']].index([-8.05,4.05]); p['outline3'][i+1:i+1]=[[rw2(4.05,d),4.05],list(sh(C2,d))]
    R['نوم ٢']['p']=[[-6.0,4.05],[rw2(4.05,d),4.05],[rw2(9.2,d),9.2],[-5.0,9.2],[-5.0,7.7],[-6.0,7.7]]
    R['نوم ٣']['p']=[[-5.0,9.2],[rw2(9.2,d),9.2],list(sh(P1,d)),[-5.0,CB5]]
    for n in ('نوم ٢','نوم ٣'): W[n]['a']=area([T(q) for q in R[n]['p']])
    W['نوم ٣']['dim']='٤.٨ × ٣.٥ + البروز'
    for w in p['walls']:
        if w['a']==[-5.0,9.2] and w['b'][1]==9.2: w['b']=[rw2(9.2,d),9.2]                   # bedroom 2 | bedroom 3 wall runs out to the new wall
    p['front'][1].update(u0=7.95,u1=9.45)                                                   # bedroom 2's front window re-centred again
    # labels: just length x width (his ask), the averaged sizes for the rooms with slanted walls
    for n,dm in (('نوم ١','٦ × ٥.٢'),('نوم ٢','٥.٤ × ٥.٢'),('نوم ٣','٥.٧ × ٢.٨'),('صالة','٥ × ٣.٢'),('مطبخ','٣ × ٣.٣'),('حمام','٢.٥ × ١.٥')): W[n]['dim']=dm
    # the bedroom hall stops just past the doors of bedrooms 1 and 2 (y 7.7); the rest of it joins bedroom 2 (his ask)
    R['نوم ٢']['p']=[q for q in R['نوم ٢']['p'] if q not in ([-5.0,5.85],[-6.0,5.85])]+[[-5.0,7.7],[-6.0,7.7]]
    hl=R['هول']['p']; R['هول']['p']=[[-6.0,7.7] if q==[-6.0,5.85] else [-5.0,7.7] if q==[-5.0,5.85] else q for q in hl]
    for n in ('نوم ٢','هول'): W[n]['a']=area([T(q) for q in R[n]['p']])
    p['walls']=[w for w in p['walls'] if w['a']!=[-6.0,5.85]]                              # old end of the hall
    p['walls'].append({'a':[-6.0,7.7],'b':[-5.0,7.7],'t':0.12,'op':[]})                    # new end of the hall
    for w in p['walls']:
        if w['a']==[-5.0,5.96]:                                                             # hall | bedroom 2 wall now starts at the new hall end
            w['a']=[-5.0,7.7]
            for op in w['op']: op['u0']-=1.74; op['u1']-=1.74
    p['extra_labels']=[{'t':'هول النوم','x':-5.5,'y':10.4,'rot':-90}]
edit_p2(PLANS[2])
# ---- proposal 2b (his ask, 5 Oct): proposal 2 with no wall between the entrance hall and the living room -> a reception guests walk straight into
import copy
def edit_open(p):
    R={r['n']:r for r in p['rooms']}; W={r['n']:r for r in p['rows']}
    R['صالة']['p']=[[-11.355,9.2],[-6.0,9.2],[-6.0,13.4],[-10.396,13.4]]                 # living + the old hall in front of kitchen and bath
    R['هول']['p']=[[-6.0,7.7],[-5.0,7.7],[-5.0,12.73],[-4.784,13.712],[-5.384,13.712],[-5.384,13.4],[-6.0,13.4]]
    for n in ('صالة','هول'): W[n]['a']=area([T(q) for q in R[n]['p']])
    W['صالة'].update(n='صالة استقبال',dim='٤.٩ × ٤.٢',c=[-8.7,11.2]); W['هول']['c']=[-5.5,12.55]
    p['walls']=[w for w in p['walls'] if not (w['a']==[-8.6,12.4] and w['b'] in ([-8.6,13.4],[-5.0,12.4]))]
    p['leaves']=[l for l in p['leaves'] if l['h']!=[-6.95,12.4]]
    for w in p['walls']:                       # and no wall between the living room and the bedroom hall (his second ask); bedroom 1's side wall stays
        if w['a']==[-6.0,4.05] and w['b']==[-6.0,12.4]: w['b']=[-6.0,9.2]
    # the living room takes the whole open strip too (his ask): from the flat door down to bedroom 3; only a 1 x 1.5 m passage
    # stays in front of the doors of bedrooms 1 and 2. Bedroom 3 now opens straight onto the living room.
    R['صالة']['p']=[[-11.355,9.2],[-5.0,9.2],[-5.0,12.73],[-4.784,13.712],[-5.384,13.712],[-5.384,13.4],[-10.396,13.4]]
    R['هول']['p']=[[-6.0,7.7],[-5.0,7.7],[-5.0,9.2],[-6.0,9.2]]
    for n in ('صالة','هول'): W[n]['a']=area([T(q) for q in R[n]['p']])
    W['صالة']['dim']='٥.٨ × ٤.٢'; W['هول'].update(n='ممر',c=[-5.5,8.45],dim='١ × ١.٥'); p['extra_labels']=[]
    # bedroom 3 grows to 20 m2 by taking from bedroom 2 (his ask): the wall between them moves from y 9.2 to y0;
    # bedroom 2's door moves to the end of the passage (y 7.7)
    d=p['side']; y0=9.2-0.7426
    R['نوم ٣']['p']=[[-5.0,y0],[rw2(y0,d),y0],list(sh(P1,d)),[-5.0,CB5]]
    R['نوم ٢']['p']=[[-6.0,4.05],[rw2(4.05,d),4.05],[rw2(y0,d),y0],[-5.0,y0],[-5.0,7.7],[-6.0,7.7]]
    for n in ('نوم ٢','نوم ٣'): W[n]['a']=area([T(q) for q in R[n]['p']])
    W['نوم ٣']['dim']='٥.٦ × ٣.٦'; W['نوم ٢']['dim']='٥.٤ × ٤.٥'
    for w in p['walls']:
        if w['a']==[-5.0,9.2] and w['b'][1]==9.2: w['a'],w['b']=[-5.0,y0],[rw2(y0,d),y0]          # bedroom 2 | bedroom 3
        elif w['a']==[-5.0,7.7]: w['op']=[]                                                       # no door on the passage's side now
        elif w['a']==[-6.0,7.7] and w['b']==[-5.0,7.7]: w['op']=[{'u0':0.05,'u1':0.95,'z0':0,'z1':2.1,'k':'door'}]   # door at the passage end
    p['leaves']=[l for l in p['leaves'] if l['h']!=[-5.0,9.1]]+[{'h':[-5.95,7.7],'along':[1,0],'out':[0,-1],'w':0.9}]
    p['title']='اقتراح ٢ب: الصالة مفتوحة على المدخل والهول'
    p['desc']='زي ترشيح ٢ بالظبط، بس الصالة واخدة المدخل والهول من غير حيطان: الضيف بيدخل من باب الشقة على الصالة على طول، ونوم ٣ بتفتح عليها.'
PLANS[7]=copy.deepcopy(PLANS[2]); edit_open(PLANS[7])
# ---- new proposal 3 (his ask, 5 Oct): proposal 2b, but bedrooms 1 + 2 become three rooms side by side on the 12 m street
#      (left ~17, middle ~14, corner ~17 with the balcony), all off a passage behind them; the rest of the flat unchanged
def edit_three(p):
    R={r['n']:r for r in p['rooms']}; W={r['n']:r for r in p['rows']}
    d=p['side']; y0=R['نوم ٣']['p'][0][1]; xr=rw2(4.05,d); bx0,bx1=-4.17,-1.67
    R['نوم ١']['p']=[[XL,4.05],[-8.6,4.05],[-8.6,9.2],[-11.355,9.2]]
    R['نوم ٢']['p']=[[-8.6,4.05],[-5.0,4.05],[-5.0,7.2],[-6.0,7.2],[-6.0,8.2],[-8.6,8.2]]
    R['هول']['p']=[[-8.6,8.2],[-6.0,8.2],[-6.0,7.2],[-5.0,7.2],[-5.0,9.2],[-8.6,9.2]]
    p4=[[-5.0,4.05],[bx0,4.05],[bx0,5.55],[bx1,5.55],[bx1,4.05],[xr,4.05],[rw2(y0,d),y0],[-5.0,y0]]
    p['rooms'].append({'n':'نوم ٤','cls':'c-blue','p':p4})
    W4=dict(W['نوم ٣']); W4.update(n='نوم ٤',c=[-3.0,7.0],dim='٤.٧ × ٤.٤'); p['rows'].insert(p['rows'].index(W['نوم ٣'])+1,W4)
    R['نوم ٤']=p['rooms'][-1]; W['نوم ٤']=W4
    for rn,wn in (('نوم ١','نوم ١'),('نوم ٢','نوم ٢'),('هول','ممر'),('نوم ٤','نوم ٤')): W[wn]['a']=area([T(q) for q in R[rn]['p']])   # the hall row is called 'ممر' in 2b
    W['نوم ١'].update(dim='٣.٤ × ٥.٢',c=[-10.0,7.3]); W['نوم ٢'].update(dim='٣.٣ × ٤.٢',c=[-7.3,6.85]); W['ممر'].update(c=[-7.3,8.7],dim='')
    keep=[]
    for w in p['walls']:
        if w['a'] in ([-6.0,4.05],[-6.0,7.7],[-5.0,7.7]): continue                          # old walls of bedrooms 1 / 2 and the short passage
        keep.append(w)
    p['walls']=keep+[
        {'a':[-8.6,4.05],'b':[-8.6,9.2],'t':0.12,'op':[{'u0':4.2,'u1':5.1,'z0':0,'z1':2.1,'k':'door'}]},    # bedroom 1 | bedroom 2 + passage; bedroom 1's door
        {'a':[-8.6,8.2],'b':[-6.0,8.2],'t':0.12,'op':[{'u0':0.9,'u1':1.8,'z0':0,'z1':2.1,'k':'door'}]},     # passage | bedroom 2; bedroom 2's door
        {'a':[-6.0,7.2],'b':[-6.0,8.2],'t':0.12,'op':[]},{'a':[-6.0,7.2],'b':[-5.0,7.2],'t':0.12,'op':[]},  # passage | bedroom 2 (its strip)
        {'a':[-5.0,4.05],'b':[-5.0,9.2],'t':0.12,'op':[{'u0':3.25,'u1':4.15,'z0':0,'z1':2.1,'k':'door'}]}]   # bedroom 2 | bedroom 4, passage | bedroom 4; bedroom 4's door
    p['leaves']=[l for l in p['leaves'] if l['h'] not in ([-6.0,8.7],[-5.95,7.7])]+[
        {'h':[-8.6,9.15],'along':[0,-1],'out':[-1,0],'w':0.9},{'h':[-7.7,8.2],'along':[1,0],'out':[0,-1],'w':0.9},
        {'h':[-5.0,8.2],'along':[0,-1],'out':[1,0],'w':0.9}]
    p['balc']=[[bx0,bx1]]
    i=[list(q) for q in p['outline3']].index([-10.55,4.05]); p['outline3'][i:i+4]=[[bx0,4.05],[bx0,5.55],[bx1,5.55],[bx1,4.05]]
    p['front']=[{'u0':0.62,'u1':2.02,'z0':0.9,'z1':2.2,'k':'win','y':4.05},{'u0':4.42,'u1':5.62,'z0':0.9,'z1':2.2,'k':'win','y':4.05},
                {'u0':bx0+0.25+12.12,'u1':bx1-0.25+12.12,'z0':0.02,'z1':2.25,'k':'slide','y':5.55}]
    p['title']='اقتراح ٣: ٤ أوض نوم، تلاتة منهم على شارع ١٢'
    p['desc']='زي ترشيح ٢ب، بس مكان نوم ١ ونوم ٢ بقى ٣ أوض جنب بعض على شارع ١٢، وكلهم بيفتحوا على ممر وراهم.'
def edit_three_open(p):
    # his next ask: no passage — the reception is the way into all three front rooms; the passage's space goes to bedroom 2
    # (behind it) and to bedroom 4 (a small entry nook with its door on the reception); the balcony moves to bedroom 2
    R={r['n']:r for r in p['rooms']}; W={r['n']:r for r in p['rows']}
    d=p['side']; y0=R['نوم ٣']['p'][0][1]; xr=rw2(4.05,d); bx0,bx1=-8.55,-6.05
    R['نوم ٢']['p']=[[-8.6,4.05],[bx0,4.05],[bx0,5.55],[bx1,5.55],[bx1,4.05],[-4.2,4.05],[-4.2,7.2],[-6.0,7.2],[-6.0,9.2],[-8.6,9.2]]
    R['نوم ٤']['p']=[[-4.2,4.05],[xr,4.05],[rw2(y0,d),y0],[-5.0,y0],[-5.0,9.2],[-6.0,9.2],[-6.0,7.2],[-4.2,7.2]]
    p['rooms']=[r for r in p['rooms'] if r['n']!='هول']; p['rows']=[r for r in p['rows'] if r['n']!='ممر']
    for n in ('نوم ٢','نوم ٤'): W[n]['a']=area([T(q) for q in R[n]['p']])
    W['نوم ٢'].update(dim='٣.٧ × ٤.٢',c=[-7.3,7.6]); W['نوم ٤'].update(dim='٤.٦ × ٤.٤',c=[-2.7,6.5])
    keep=[]
    for w in p['walls']:
        if w['a'] in ([-8.6,8.2],[-6.0,7.2],[-5.0,4.05]): continue                           # passage walls and the old bedroom 2 | bedroom 4 wall
        if w['a']==[-8.6,4.05]: w['op']=[]                                                    # bedroom 1 | bedroom 2: no door now
        if w['a']==[-11.235,9.2] and w['b']==[-6.0,9.2]:                                     # rooms | reception: runs to x -5.0, three doors
            w['b']=[-5.0,9.2]; w['op']=[{'u0':u,'u1':u+0.9,'z0':0,'z1':2.1,'k':'door'} for u in (0.635,3.335,5.285)]
        keep.append(w)
    p['walls']=keep+[{'a':[-6.0,7.2],'b':[-6.0,9.2],'t':0.12,'op':[]},{'a':[-6.0,7.2],'b':[-4.2,7.2],'t':0.12,'op':[]},
                     {'a':[-4.2,4.05],'b':[-4.2,7.2],'t':0.12,'op':[]},{'a':[-5.0,y0],'b':[-5.0,9.2],'t':0.12,'op':[]}]
    p['leaves']=[l for l in p['leaves'] if l['h'] not in ([-8.6,9.15],[-7.7,8.2],[-5.0,8.2])]+[
        {'h':[x,9.2],'along':[1,0],'out':[0,-1],'w':0.9} for x in (-10.6,-7.9,-5.95)]
    i=[list(q) for q in p['outline3']].index([p['balc'][0][0],4.05]); p['outline3'][i:i+4]=[[bx0,4.05],[bx0,5.55],[bx1,5.55],[bx1,4.05]]
    p['balc']=[[bx0,bx1]]
    p['front']=[{'u0':0.62,'u1':2.02,'z0':0.9,'z1':2.2,'k':'win','y':4.05},
                {'u0':3.77,'u1':5.22,'z0':0.02,'z1':2.25,'k':'slide','y':5.55},                 # balcony door left of the old facade column
                {'u0':8.87,'u1':10.37,'z0':0.9,'z1':2.2,'k':'win','y':4.05}]
    p['title']='اقتراح ٣: ٤ أوض نوم بتفتح على صالة الاستقبال'
    p['desc']='زي ترشيح ٢ب، بس مكان نوم ١ ونوم ٢ بقى ٣ أوض جنب بعض على شارع ١٢، بيفتحوا على صالة الاستقبال على طول من غير ممر، والبلكونة في نوم ٢.'
def edit_three_line(p):
    # his next ask: bedroom 3's front wall goes back to the reception's line (y 9.2), one straight wall; bedroom 4 takes the strip
    R={r['n']:r for r in p['rooms']}; W={r['n']:r for r in p['rows']}
    d=p['side']; y0=R['نوم ٣']['p'][0][1]; xr=rw2(4.05,d)
    R['نوم ٣']['p']=[[-5.0,9.2],[rw2(9.2,d),9.2],list(sh(P1,d)),[-5.0,CB5]]
    R['نوم ٤']['p']=[[-4.2,4.05],[xr,4.05],[rw2(9.2,d),9.2],[-6.0,9.2],[-6.0,7.2],[-4.2,7.2]]
    for n in ('نوم ٣','نوم ٤'): W[n]['a']=area([T(q) for q in R[n]['p']])
    W['نوم ٣']['dim']='٥.٧ × ٢.٨'; W['نوم ٤']['dim']='٤.٧ × ٥.٢'
    keep=[]
    for w in p['walls']:
        if w['a']==[-5.0,y0] and w['b']==[-5.0,9.2]: continue                                 # nook | bedroom 3: inside bedroom 4 now
        if w['a']==[-5.0,y0] and w['b'][1]==y0: w['a'],w['b']=[-5.0,9.2],[rw2(9.2,d),9.2]     # bedroom 3 | bedroom 4 on the reception's line
        keep.append(w)
    p['walls']=keep
def edit_three_lobby(p):
    # his pick (idea 2): one 1 x 1 m lobby off the reception, open to it, with the doors of bedrooms 2 and 4 facing each other;
    # the small pocket under the lobby goes to bedroom 2
    R={r['n']:r for r in p['rooms']}; W={r['n']:r for r in p['rows']}
    d=p['side']; xr=rw2(4.05,d); bx0,bx1=p['balc'][0]
    R['نوم ٢']['p']=[[-8.6,4.05],[bx0,4.05],[bx0,5.55],[bx1,5.55],[bx1,4.05],[-4.2,4.05],[-4.2,7.2],[-5.0,7.2],[-5.0,8.2],[-6.0,8.2],[-6.0,9.2],[-8.6,9.2]]
    R['نوم ٤']['p']=[[-4.2,4.05],[xr,4.05],[rw2(9.2,d),9.2],[-5.0,9.2],[-5.0,7.2],[-4.2,7.2]]
    p['rooms'].append({'n':'دخلة','cls':'c-gray','p':[[-6.0,8.2],[-5.0,8.2],[-5.0,9.2],[-6.0,9.2]]})
    p['rows'].append({'n':'دخلة','w':1.0,'h':1.0,'a':1.0,'c':[-5.5,8.7],'lbl':False})
    for n in ('نوم ٢','نوم ٤'): W[n]['a']=area([T(q) for q in R[n]['p']])
    W['نوم ٢']['dim']='٣.٩ × ٤.٢'; W['نوم ٤']['dim']='٤.٤ × ٥.١'
    keep=[]
    for w in p['walls']:
        if w['a']==[-6.0,7.2]: continue                                                       # old nook walls
        if w['a']==[-11.235,9.2] and w['b']==[-5.0,9.2]:                                     # reception wall: bedroom 1's door + the lobby opening
            w['op']=[{'u0':0.635,'u1':1.535,'z0':0,'z1':2.1,'k':'door'},{'u0':5.235,'u1':6.235,'z0':0,'z1':2.1,'k':'open'}]
        keep.append(w)
    p['walls']=keep+[{'a':[-6.0,8.2],'b':[-6.0,9.2],'t':0.12,'op':[{'u0':0.05,'u1':0.95,'z0':0,'z1':2.1,'k':'door'}]},   # lobby | bedroom 2
                     {'a':[-5.0,7.2],'b':[-5.0,9.2],'t':0.12,'op':[{'u0':1.05,'u1':1.95,'z0':0,'z1':2.1,'k':'door'}]},   # bedroom 2 pocket + lobby | bedroom 4
                     {'a':[-6.0,8.2],'b':[-5.0,8.2],'t':0.12,'op':[]},{'a':[-5.0,7.2],'b':[-4.2,7.2],'t':0.12,'op':[]}]
    p['leaves']=[l for l in p['leaves'] if l['h'] not in ([-7.9,9.2],[-5.95,9.2])]+[
        {'h':[-6.0,9.15],'along':[0,-1],'out':[-1,0],'w':0.9},{'h':[-5.0,9.15],'along':[0,-1],'out':[1,0],'w':0.9}]
    p['desc']='زي ترشيح ٢ب، بس مكان نوم ١ ونوم ٢ بقى ٣ أوض جنب بعض على شارع ١٢. نوم ١ بتفتح على الصالة، ونوم ٢ ونوم ٤ بيفتحوا على دخلة صغيرة من الصالة، والبلكونة في نوم ٢.'
def edit_three_straight(p):
    # his next ask: the bedroom 2 | bedroom 4 wall runs straight down from the lobby to the facade (x -5.0); bedroom 4 takes the step
    R={r['n']:r for r in p['rooms']}; W={r['n']:r for r in p['rows']}
    d=p['side']; xr=rw2(4.05,d); bx0,bx1=p['balc'][0]
    R['نوم ٢']['p']=[[-8.6,4.05],[bx0,4.05],[bx0,5.55],[bx1,5.55],[bx1,4.05],[-5.0,4.05],[-5.0,8.2],[-6.0,8.2],[-6.0,9.2],[-8.6,9.2]]
    R['نوم ٤']['p']=[[-5.0,4.05],[xr,4.05],[rw2(9.2,d),9.2],[-5.0,9.2]]
    for n in ('نوم ٢','نوم ٤'): W[n]['a']=area([T(q) for q in R[n]['p']])
    W['نوم ٢']['dim']='٣.٦ × ٥.٢'; W['نوم ٤']['dim']='٤.٨ × ٥.٢'
    keep=[]
    for w in p['walls']:
        if w['a'] in ([-4.2,4.05],) or (w['a']==[-5.0,7.2] and w['b']==[-4.2,7.2]): continue   # the old step
        if w['a']==[-5.0,7.2] and w['b']==[-5.0,9.2]:                                        # one straight wall from the facade to the reception
            w['a']=[-5.0,4.05]
            for op in w['op']: op['u0']+=3.15; op['u1']+=3.15
        keep.append(w)
    p['walls']=keep
    for op in p['front']:
        if op['k']=='win' and op['u0']>8: op.update(u0=8.45,u1=9.95)                       # bedroom 4's window re-centred
PLANS[8]=copy.deepcopy(PLANS[7]); edit_three(PLANS[8]); edit_three_open(PLANS[8]); edit_three_line(PLANS[8]); edit_three_lobby(PLANS[8]); edit_three_straight(PLANS[8])
core=SH['core']; whst=SH['whst']
U=T(core['U']); V=T(core['V'])
def cp(s,t): return (P2[0]+U[0]*s+V[0]*t, P2[1]+U[1]*s+V[1]*t)
wd=T(whst['d']); wn=T(whst['n']); wA=T(whst['A'])
def wp(s,o): return (wA[0]+wd[0]*s+wn[0]*o, wA[1]+wd[1]*s+wn[1]*o)
def upt(a,b,u):
    L=math.hypot(b[0]-a[0],b[1]-a[1]); return (a[0]+(b[0]-a[0])*u/L, a[1]+(b[1]-a[1])*u/L)
def mid(a,b,dx=0,dy=0): return ((a[0]+b[0])/2+dx,(a[1]+b[1])/2+dy)

# ---------------- svg primitives ----------------
class Frame:
    def __init__(s_,x0,y1,s,ox,oy): s_.x0,s_.y1,s_.s,s_.ox,s_.oy=x0,y1,s,ox,oy
    def X(s_,x): return s_.ox+(x-s_.x0)*s_.s
    def Y(s_,y): return s_.oy+(s_.y1-y)*s_.s
    def P(s_,p): return f'{s_.X(p[0]):.1f},{s_.Y(p[1]):.1f}'
    def pts(s_,poly): return ' '.join(s_.P(p) for p in poly)
FR=Frame(-13.4,18.0,38,40,36)      # building pages: 680 x 650 viewBox
def line(F,a,b,color,w,dash=None,cap='butt',marker=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''; m=f' marker-end="url(#{marker})"' if marker else ''
    return f'<line x1="{F.X(a[0]):.1f}" y1="{F.Y(a[1]):.1f}" x2="{F.X(b[0]):.1f}" y2="{F.Y(b[1]):.1f}" stroke="{color}" stroke-width="{w:.1f}" stroke-linecap="{cap}"{d}{m}/>'
def poly(F,p,fill='none',stroke='#1d2126',sw=1,dash=None,op=None):
    at=f' fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(f' fill-opacity="{op}"' if op else '')
    return f'<polygon points="{F.pts(p)}"{at}/>'
def text(F,t,x,y,cls='t',anchor='middle',rot=None,fill=None,dy=0):
    X,Y=F.X(x),F.Y(y)+dy; tr=f' transform="rotate({rot:.1f} {X:.1f} {Y:.1f})"' if rot else ''
    fl=f' fill="{fill}"' if fill else ''
    return f'<text x="{X:.1f}" y="{Y:.1f}" class="{cls}" text-anchor="{anchor}" dominant-baseline="central"{tr}{fl}>{t}</text>'
def rot_along(a,b):
    ang=-math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
    if ang>90: ang-=180
    if ang<-90: ang+=180
    return ang
def rect_rot(F,x,y,w,h,ang,fill):
    W,H=w*F.s,h*F.s; X,Y=F.X(x),F.Y(y)
    return f'<rect x="{X-W/2:.1f}" y="{Y-H/2:.1f}" width="{W:.1f}" height="{H:.1f}" fill="{fill}" transform="rotate({-math.degrees(ang):.1f} {X:.1f} {Y:.1f})"/>'
DOOR='#F76707'                     # every door is orange with a thick line (his ask, 5 Oct 2026)
def win(F,a,b): return line(F,a,b,'#ffffff',4.5)+line(F,a,b,'#1F5FBF',2)
def slide(F,a,b):
    m=mid(a,b); return line(F,a,b,'#ffffff',6)+line(F,a,b,DOOR,3.4)+line(F,(a[0],a[1]+0.14),(m[0],m[1]+0.14),DOOR,2.4)
def leaf(F,h,along,out,w):
    p_open=(h[0]+out[0]*w,h[1]+out[1]*w)
    a0=math.atan2(along[1],along[0]); a1=math.atan2(out[1],out[0]); d=a1-a0
    while d>math.pi: d-=2*math.pi
    while d<=-math.pi: d+=2*math.pi
    arc=[(h[0]+math.cos(a0+d*i/10)*w, h[1]+math.sin(a0+d*i/10)*w) for i in range(11)]
    return line(F,h,p_open,DOOR,3.4,cap='round')+f'<polyline points="{F.pts(arc)}" fill="none" stroke="{DOOR}" stroke-width="1.8" stroke-dasharray="5 3"/>'
DEFS='<defs><marker id="arw" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#B3261E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker><marker id="arg" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#3a414b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>'
CLS={'c-amber':('#F7E1A8','#C9A23A'),'c-blue':('#D7E6F7','#1F5FBF'),'c-green':('#DDEFD9','#4C8C4A'),'c-purple':('#E8DDF2','#7A4FA3'),'c-gray':('#ECEEF1','#9AA1AB'),'c-teal':('#E1F0F0','#2A8C8C')}
COL_WALL='#1F5FBF'; COL_CORE='#2A8C8C'; COL_IN='#B3261E'
def is_core_corner(x,y): return any(abs(x-q[0])<0.02 and abs(y-q[1])<0.02 for q in CORE)

# ---------------- building pieces ----------------
def site(F):
    return [poly(F,LAND,fill='#f4f1ea',stroke='#c9ccd2',sw=0.6),poly(F,STRIP1,fill='#f9efe9',stroke='#e0c9bd',sw=0.5),poly(F,STRIP2,fill='#fbf5e3',stroke='#e6d7a8',sw=0.5)]
def dims(F,fl,side=0):
    if fl>=2 and side:                 # floors with both projections: the real lengths of the four outer walls
        fr,c3=(rw2(4.05,side),4.05),sh(C2,side); L=lambda a,b: math.hypot(b[0]-a[0],b[1]-a[1])
        t12,t6,tl,tr=fr[0]-XL,L(fr,c3),L((XL,4.05),B2),L(B2,c3)
        o=[text(F,f'الواجهة {ar(t12,2)} م — شارع ١٢ م',(A[0]+D2[0])/2,3.35,cls='t')]
        o.append(text(F,f'≈ {ar(t6,2)} م — شارع ٦ م',*sh(mid(D2,C2,0.75,-0.15),side),cls='t',rot=rot_along(D2,C2)))
        o.append(text(F,f'الجار الشمال — {ar(tl,2)} م',*mid(A,B2,-0.6,0),cls='t',rot=rot_along(A,B2)))
        o.append(text(F,f'الجار — ≈ {ar(tr,2)} م',*mid(B2,C2,0,0.55),cls='t',rot=rot_along(B2,C2)))
        return o
    o=[text(F,'الواجهة ١٠.٥٠ م — شارع ١٢ م',(A[0]+D2[0])/2,3.35 if fl>=2 else 5.2,cls='t')]
    o.append(text(F,'≈ ٨.٨٥ م — شارع ٦ م',*sh(mid(D2,C2,0.75,-0.15),side),cls='t',rot=rot_along(D2,C2)))
    o.append(text(F,'الجار الشمال — ١١.٤٠ م',*mid(A,B2,-0.6,0),cls='t',rot=rot_along(A,B2)))
    o.append(text(F,'الجار — ≈ ١٠.٤٥ م',*mid(B2,C2,0,0.55),cls='t',rot=rot_along(B2,C2)))
    return o
def columns(F,plan,fl):
    o=[]; shrink=0 if fl<=2 else 0.1
    for x,y,w,h,ang in plan['cols_out']:
        o.append(rect_rot(F,x,y,max(0.3,w-shrink),max(0.3,h-shrink),ang,COL_CORE if is_core_corner(x,y) else COL_WALL))
    for x,y in plan['cols_in']:
        s_=0.4 if fl<=2 else 0.3; o.append(rect_rot(F,x,y,s_,s_,0,COL_IN))
    return o
def legend(plan):
    n_out=len(plan['cols_out']); n_core=sum(1 for c in plan['cols_out'] if is_core_corner(c[0],c[1])); n_in=len(plan['cols_in'])
    o=[f'<text x="668" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="{COL_WALL}">■ عمود في حيطة خارجية ({ar(n_out-n_core,0)})</text>',
       f'<text x="505" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="{COL_CORE}">■ ركن بيت السلم ({ar(n_core,0)})</text>']
    o.append(f'<text x="365" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="{COL_IN}">■ عمود جوه المخزن ({ar(n_in,0)})</text>' if n_in else '<text x="365" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="#B3261E">مفيش عمود جوه المخزن</text>')
    o.append('<text x="215" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="#8A4B12">▬ كمرة (المتقطع = تحويل)</text>')
    o.append(f'<text x="100" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="{DOOR}" font-weight="700">▬ باب</text>')
    o.append('<text x="55" y="16" class="ts" text-anchor="start" dominant-baseline="central" fill="#1F5FBF">▬ شباك</text>')
    return o
def beams(F,plan,fl):
    o=[]
    if plan.get('transfer'):
        if fl==2:
            for a,b in plan['tbeams']: o.append(line(F,T(a),T(b),'#8A4B12',5,dash='9 5',cap='round'))
    else:
        for c in plan['cols_in']:
            o.append(line(F,(c[0],5.85),(c[0],tw(c[0])),'#8A4B12',2.5,cap='round'))
            o.append(line(F,(lw(c[1]),c[1]),(rw(c[1]),c[1]),'#8A4B12',2.5,cap='round'))
    return o
def wall_lines(F,plan):
    o=[]
    for w in plan['walls']:
        a,b=T(w['a']),T(w['b']); L=math.hypot(b[0]-a[0],b[1]-a[1]); ux,uy=(b[0]-a[0])/L,(b[1]-a[1])/L
        segs=[]; u=0
        for op in sorted(w['op'],key=lambda q:q['u0']):
            segs.append((u,op['u0'],'wall')); segs.append((op['u0'],op['u1'],op['k'])); u=op['u1']
        segs.append((u,L,'wall'))
        for u0,u1,k in segs:
            if u1-u0<0.01: continue
            p=(a[0]+ux*u0,a[1]+uy*u0); q=(a[0]+ux*u1,a[1]+uy*u1)
            if k=='wall': o.append(line(F,p,q,'#1d2126',w['t']*F.s))
            elif k=='win': o.append(line(F,p,q,'#1F5FBF',1.5))
    return o
def ring(F,plan,fl):
    bays=plan.get('bays') or ([plan['bay']] if plan.get('bay') else [])
    if fl>=3 and plan.get('outline3'): out=[T(q) for q in plan['outline3']]
    elif fl>=3 and bays:                 # rooms that come forward of the 12 m facade
        out=[A]+[q for x0,x1,y in sorted(bays) for q in ((x0,5.85),(x0,y),(x1,y),(x1,5.85))]+[D2,C2,B2]
    elif fl==2 and plan.get('side'): d=plan['side']; out=[(XL,4.05),(rw2(4.05,d),4.05),sh(C2,d),B2,A]
    else: out=PROJ if fl==2 else BLD
    ds=plan.get('side',0) if fl>=2 else 0
    o=[poly(F,out,fill='none',stroke='#1d2126',sw=3)]
    if fl==2: o.append(line(F,A,D2,'#1d2126',1,dash='6 4'))
    if fl==2 and ds: o.append(line(F,D2,C2,'#1d2126',1,dash='6 4'))
    if fl==1:
        x0,x1=plan['whdoor']; o.append(line(F,(x0,5.85),(x1,5.85),'#ffffff',4)); o.append(line(F,(x0,5.85),(x1,5.85),DOOR,6,dash='10 5'))
        o.append(text(F,f'باب المخزن {ar(x1-x0)} م (رول)',(x0+x1)/2,6.45,cls='ts',fill=DOOR))
    if fl in (1,2):
        for u0,u1 in ((1.2,2.4),(3.4,4.6)): o.append(win(F,sh(upt(D2,C2,u0),ds),sh(upt(D2,C2,u1),ds)))
    if fl==2:
        for x0,x1 in ((-11.2,-9.2),(-7.9,-5.9),(-4.6,-2.6)): o.append(win(F,(x0,4.05),(x1,4.05)))
    if fl>=3:
        for op in plan['front']: o.append((win if op.get('k')=='win' else slide)(F,(A[0]+op['u0'],op.get('y',5.85)),(A[0]+op['u1'],op.get('y',5.85))))
        for op in plan['right']: o.append(win(F,sh(upt(D2,C2,op['u0']),ds),sh(upt(D2,C2,op['u1']),ds)))
    return o
def core_svg(F,fl,plan):
    dc=plan.get('side',0) if fl>=2 else 0
    o=[poly(F,[sh(C2,dc),sh(P1,dc),P2,P3] if dc else CORE,fill=CLS['c-teal'][0],stroke='#1d2126',sw=3)]
    S0,S1,TR=core['S0'],core['S1'],core['TR']
    for ta,tb in (core['sideA'],core['sideB']):
        for i in range(9): o.append(line(F,cp(S0+i*TR,ta),cp(S0+i*TR,tb),'#556070',0.8))
        o.append(poly(F,[cp(S0,ta),cp(S1,ta),cp(S1,tb),cp(S0,tb)],fill='none',stroke='#556070',sw=0.8))
    for s0,s1 in (core['land_back'],(core['land_street'][0],core['land_street'][1]+dc)):
        o.append(poly(F,[cp(s0,0.25),cp(s1,0.25),cp(s1,2.75),cp(s0,2.75)],fill='none',stroke='#556070',sw=0.8,dash='3 2'))
    ta,tb=core['sideA']; tm=(ta+tb)/2; rot=rot_along(cp(S1,tm),cp(S0,tm))
    o.append(line(F,cp(S1+0.15,tm),cp(S0-0.1,tm),'#B3261E',1.5,marker='arw'))
    o.append(text(F,'طالع',*cp((S0+S1)/2,tm),cls='ts',rot=rot,fill='#B3261E',dy=-9))
    if fl>=2:
        tb0,tb1=core['sideB']; tm2=(tb0+tb1)/2
        o.append(line(F,cp(S0-0.1,tm2),cp(S1+0.15,tm2),'#3a414b',1.2,marker='arg'))
        o.append(text(F,'نازل',*cp((S0+S1)/2,tm2),cls='ts',rot=rot,fill='#3a414b',dy=-9))
    o.append(text(F,f'بيت السلم ٣ × {ar(5+dc) if dc else "٥"}',*cp(2.5,1.5),cls='t',rot=rot,dy=0))
    if fl<=2: o.append(text(F,'مقفول على المخزن',*cp(2.5,1.5),cls='ts',rot=rot,dy=12))
    if fl>=3:
        e=plan['entry']; a=cp(0,e['t0']); b=cp(0,e['t1'])
        o.append(line(F,a,b,'#ffffff',4)); o.append(leaf(F,a,V,(-U[0],-U[1]),e['t1']-e['t0']))
        o.append(text(F,'باب الشقة ٠.٩٠',*cp(0.55,(e['t0']+e['t1'])/2),cls='ts',rot=rot_along(P2,P3),fill=DOOR))
    return o
def wh_stair(F):
    o=[]; s_bot,s_top=whst['s_bot'],whst['s_top']; o0,o1=whst['off0'],whst['off1']; om=(o0+o1)/2
    o.append(poly(F,[wp(s_bot,o0),wp(s_bot,o1),wp(s_top-1.2,o1),wp(s_top-1.2,o0)],fill=CLS['c-gray'][0],stroke='#1d2126',sw=1))
    for i in range(whst['NR']): o.append(line(F,wp(s_bot-i*whst['tread'],o0),wp(s_bot-i*whst['tread'],o1),'#556070',0.8))
    o.append(line(F,wp(s_top,o0),wp(s_top,o1),'#1d2126',1.5))
    o.append(line(F,wp(s_bot+0.05,om),wp(s_top-0.35,om),'#B3261E',1.5,marker='arw'))
    r=rot_along(wp(s_bot,om),wp(s_top,om))
    o.append(text(F,'سلم المخزن: ٢٢ درجة × ١٧ سم، عرض ١.٢٠ م',*wp((s_bot+s_top)/2,o1+0.5),cls='ts',rot=r))
    o.append(text(F,'بسطة',*wp(s_top-0.6,om),cls='ts',rot=r))
    o.append(text(F,'تحت السلم: تخزين',*wp(s_bot-1.6,om),cls='ts',rot=r,fill='#3a414b',dy=0))
    return o
def f2_openings(F):
    h0,h1=whst['hole']; o0,o1=whst['off0'],whst['off1']; om=(o0+o1)/2; r=rot_along(wp(h0,0),wp(h1,0))
    o=[poly(F,[wp(h0,o0),wp(h1,o0),wp(h1,o1),wp(h0,o1)],fill=CLS['c-gray'][0],stroke='#556070',sw=1,dash='4 3')]
    o.append(text(F,'فتحة السلم ١.٢ × ٣.٤',*wp((h0+h1)/2,om),cls='ts',rot=r))
    o.append(poly(F,[wp(h0-1.2,o0),wp(h0,o0),wp(h0,o1),wp(h0-1.2,o1)],fill='none',stroke='#556070',sw=0.8,dash='3 2'))
    o.append(text(F,'وصول السلم',*wp(h0-0.6,om),cls='ts',rot=r))
    o.append(poly(F,HOIST,fill=CLS['c-purple'][0],stroke=CLS['c-purple'][1],sw=1))
    cx=sum(p[0] for p in HOIST)/4; cy=sum(p[1] for p in HOIST)/4
    o.append(text(F,'فتحة ونش ١.٢ × ١.٢',cx,cy-0.95,cls='ts',fill=CLS['c-purple'][1]))
    return o
def duct(F):
    return [poly(F,DUCT,fill='#1d2126',stroke='#1d2126',sw=0.5),text(F,'→ مجرى مواسير ٤٠ × ٦٠',DUCT[0][0]-1.75,DUCT[0][1]+0.3,cls='ts')]

# ---------------- pages ----------------
def svg_open(vb='0 0 680 650',title=''): return f'<svg viewBox="{vb}" role="img"><title>{title}</title>{DEFS}'
def f2_poly(plan):
    d=plan.get('side',0)
    return [(XL,4.05),(rw2(4.05,d),4.05),sh(P1,d),P2,P3,B2,A] if d else F2
def f2_area(plan): return area(f2_poly(plan))-1.2*3.4-area(HOIST)-area(DUCT)
def wh_svg(plan,fl):
    F=FR; o=[svg_open(title='مسقط المخزن')]+site(F)
    d=plan.get('side',0)
    o.append(poly(F,SLAB if fl==1 else f2_poly(plan),fill='#ffffff',stroke='none'))
    if fl==2:
        o.append(poly(F,[(XL,4.05),(rw2(4.05,d),4.05),sh(C2,d),C2,D2,A] if d else [(XL,4.05),(XR,4.05),D2,A],fill='#E6F0E6',stroke='#4C8C4A',sw=0.8))
        o.append(text(F,'بروز ١.٨٠ م فوق شارع ١٢' if d else 'بروز ١.٨٠ م فوق الشارع',(A[0]+D2[0])/2,4.95,cls='ts',fill='#2f6b2f'))
        if d: o.append(text(F,f'بروز {ar(d,2)} م فوق شارع ٦',*sh(mid(D2,C2),d/2),cls='ts',rot=rot_along(D2,C2),fill='#2f6b2f'))
    o+=beams(F,plan,fl)
    o+=ring(F,plan,fl); o+=core_svg(F,fl,plan)
    if fl==1:                          # flats' street door, drawn over the stair box so its swing shows
        sd=core['street_door']; a=upt(P1,C2,sd['t0']); b=upt(P1,C2,sd['t1'])
        o.append(line(F,a,b,'#ffffff',4)); o.append(leaf(F,a,upt((0,0),(C2[0]-P1[0],C2[1]-P1[1]),1),(-U[0],-U[1]),sd['t1']-sd['t0']))
        o.append(text(F,'مدخل الشقق ١.١٠',*mid(a,b,0.9,-0.1),cls='ts',rot=rot_along(P1,C2),fill=DOOR))
    o+=wh_stair(F) if fl==1 else f2_openings(F)
    o+=duct(F); o+=columns(F,plan,fl)
    o.append(text(F,f'مساحة فاضية ≈ {ar(G_AREA if fl==1 else f2_area(plan),0)} م²',-6.6,10.6,cls='th'))
    o.append(text(F,'ارتفاع ٣.٧٥ م',-6.6,10.6,cls='ts',dy=16))
    if plan.get('transfer') and fl==2: o.append(text(F,'كمرات تحويل ٣٠ × ١٠٠ سم تحت حيطان الشقة',-6.6,7.4,cls='ts',fill='#8A4B12'))
    o+=dims(F,fl,plan.get('side',0) if fl>=2 else 0); o+=legend(plan); o.append('</svg>'); return '\n'.join(o)
def flat_svg(plan,fl):
    F=FR; o=[svg_open(title='مسقط الشقة')]+site(F)
    if fl==3: o.append(poly(F,[(XL,4.05),(XR,4.05),(-1.62,5.85),(-12.12,5.85)],fill='#f1f1ec',stroke='#b9bec7',sw=0.6,dash='3 2'))
    else: o.append(line(F,(XL,4.05),(XR,4.05),'#b9bec7',0.8,dash='3 2'))
    for r in plan['rooms']:
        fill,stroke=CLS.get(r['cls'],CLS['c-gray']); o.append(poly(F,[T(p) for p in r['p']],fill=fill,stroke=stroke,sw=0.8))
    bd=plan.get('balc_d',1.8); by=plan.get('balc_y0',5.85)
    for x1,x2 in plan['balc']:
        o.append(poly(F,[(x1,by),(x2,by),(x2,by-bd),(x1,by-bd)],fill='#ECEEF1',stroke='#1d2126',sw=1.6))
        o.append(text(F,f'بلكونة {ar(x2-x1)} × {ar(bd,2)}',(x1+x2)/2,by-bd/2,cls='ts'))
    if fl==3:                          # label the open parts of the warehouse projection roof (not under a balcony or a room)
        cov=sorted({tuple(b) for b in plan['balc']}|{(b[0],b[1]) for b in (plan.get('bays') or [])})
        xs=[-12.12]+[x for b in cov for x in b]+[-1.62]
        for i in range(0,len(xs),2):
            if xs[i+1]-xs[i]>0.6: o.append(text(F,'سطح البروز',(xs[i]+xs[i+1])/2,4.95,cls='ts',fill='#8a8f99'))
    o+=wall_lines(F,plan); o+=ring(F,plan,fl); o+=core_svg(F,fl,plan); o+=columns(F,plan,fl)
    for l in plan['leaves']: o.append(leaf(F,T(l['h']),T(l['along']),T(l['out']),l['w']))
    for r in plan['rows']:
        cx,cy=r['c']
        if r['n']=='منور': o.append(text(F,'منور ١ × ١.٥' if abs(r['w']-1.5)<0.01 else f"منور {ar(r['w'])} × {ar(r['h'])}",cx,cy,cls='ts')); continue
        if r['lbl']:
            o.append(text(F,r['n'],cx,cy,cls='t',dy=-7)); o.append(text(F,f"{r.get('dim') or ar(r['w'])+' × '+ar(r['h'])} ≈ {ar(r['a'],0)} م²",cx,cy,cls='ts',dy=8))
        else: o.append(text(F,r['n'],cx,cy,cls='ts'))
    for t in plan.get('extra_labels',[]): o.append(text(F,t['t'],t['x'],t['y'],cls='ts',rot=t.get('rot')))
    if plan.get('outline3'):           # where the facade used to be: everything in front of it is taken over the street strip
        o.append(line(F,A,D2,'#B3261E',2.2,dash='8 5'))
        o.append(f'<text x="{F.X(-10.75):.1f}" y="{F.Y(6.12):.1f}" text-anchor="middle" dominant-baseline="central" style="fill:#B3261E;font-size:9px;font-weight:700">خط الواجهة القديم</text>')
        # how far we went out over the street, written next to the street corner: a red dimension 1.80 + the area per floor
        taken=area([(XL,4.05),(XR,4.05),D2,A]); xd=XL-0.45; d=plan.get('side',0)
        def red(t,x,y,sz=10): return f'<text x="{F.X(x):.1f}" y="{F.Y(y):.1f}" text-anchor="middle" dominant-baseline="central" style="fill:#B3261E;font-size:{sz}px;font-weight:700">{t}</text>'
        def arrow(a,b): return f'<line x1="{F.X(a[0]):.1f}" y1="{F.Y(a[1]):.1f}" x2="{F.X(b[0]):.1f}" y2="{F.Y(b[1]):.1f}" stroke="#B3261E" stroke-width="1.4" marker-start="url(#arw)" marker-end="url(#arw)"/>'
        o.append(line(F,A,(xd-0.1,5.85),'#B3261E',0.8,dash='3 2')); o.append(line(F,(XL,4.05),(xd-0.1,4.05),'#B3261E',0.8,dash='3 2'))
        o.append(arrow((xd,5.85),(xd,4.05))); o.append(red(f'شارع ١٢: طلعنا ١.٨٠ م ≈ {ar(taken,0)} م²',-10.2,2.85))
        if d:                          # the 6 m street side: old wall dashed, arrow across the new strip, amount outside
            side=area([(XR,4.05),(rw2(4.05,d),4.05),sh(C2,d),C2])
            o.append(line(F,D2,C2,'#B3261E',2.2,dash='8 5'))
            p0=(rw(6.6),6.6); o.append(arrow(p0,sh(p0,d)))
            o.append(red(f'شارع ٦: طلعنا {ar(d,2)} م',1.45,7.0)); o.append(red(f'≈ {ar(side,0)} م² في الدور',1.45,6.5))
    o+=dims(F,fl,plan.get('side',0)); o+=legend(plan); o.append('</svg>'); return '\n'.join(o)

NT,TR,NR,RISE,SW=21,0.27,22,3.75,1.2
def stair_svg():
    s=44; o=[svg_open('0 0 680 560','تفاصيل سلم المخزن')]
    ox,oy=60,70; L=NT*TR
    o.append('<text x="340" y="30" class="th" text-anchor="middle" dominant-baseline="central">مسقط السلم من فوق</text>')
    x0=ox; x1=ox+s*1.2; y0=oy; y1=oy+s*SW
    o.append(f'<rect x="{x0}" y="{y0}" width="{s*1.2:.0f}" height="{s*SW:.0f}" fill="#ECEEF1" stroke="#9AA1AB" stroke-width="1"/>')
    o.append(f'<text x="{x0+s*0.6:.0f}" y="{y0+s*SW/2:.0f}" class="ts" text-anchor="middle" dominant-baseline="central">بسطة ١.٢</text>')
    for i in range(NT+1):
        xx=x1+s*TR*i; o.append(f'<line x1="{xx:.1f}" y1="{y0}" x2="{xx:.1f}" y2="{y1}" stroke="#556070" stroke-width="1"/>')
    xe=x1+s*L
    o.append(f'<rect x="{x0}" y="{y0}" width="{xe-x0:.1f}" height="{s*SW:.0f}" fill="none" stroke="#1d2126" stroke-width="2"/>')
    o.append(f'<line x1="{xe-8}" y1="{y0+s*SW/2:.0f}" x2="{x1+10}" y2="{y0+s*SW/2:.0f}" stroke="#B3261E" stroke-width="1.5" marker-end="url(#arw)"/>')
    o.append(f'<text x="{(x1+xe)/2:.0f}" y="{y0+s*SW/2-12:.0f}" class="ts" text-anchor="middle" dominant-baseline="central">٢١ نائمة × ٢٧ سم = {ar(L)} م</text>')
    o.append(f'<line x1="{x0}" y1="{y1+18}" x2="{xe:.1f}" y2="{y1+18}" stroke="#3a414b" stroke-width="1" marker-start="url(#arg)" marker-end="url(#arg)"/>')
    o.append(f'<text x="{(x0+xe)/2:.0f}" y="{y1+32}" class="t" text-anchor="middle" dominant-baseline="central">الطول الكلي {ar(L+1.2)} م، موازي لحيطة الجار الشمال</text>')
    o.append(f'<line x1="{xe+18:.1f}" y1="{y0}" x2="{xe+18:.1f}" y2="{y1}" stroke="#3a414b" stroke-width="1" marker-start="url(#arg)" marker-end="url(#arg)"/>')
    o.append(f'<text x="{xe+36:.1f}" y="{(y0+y1)/2:.0f}" class="t" text-anchor="middle" dominant-baseline="central" transform="rotate(-90 {xe+36:.1f} {(y0+y1)/2:.0f})">عرض ١.٢٠ م</text>')
    o.append(f'<text x="{x0}" y="{y0-14}" class="ts" text-anchor="end" dominant-baseline="central">الدور الثاني ↑</text>')
    o.append(f'<text x="{xe:.0f}" y="{y0-14}" class="ts" text-anchor="start" dominant-baseline="central">↓ الأرضي (ناحية الضهر)</text>')
    oy2=250; base=oy2+s*RISE+20
    o.append(f'<text x="340" y="{oy2-20}" class="th" text-anchor="middle" dominant-baseline="central">قطاع في السلم</text>')
    path='M'+' L'.join(f'{px:.1f} {py:.1f}' for px,py in [(xe,base)]+[p for q in [((xe-s*TR*i, base-s*(RISE/NR)*i),(xe-s*TR*i, base-s*(RISE/NR)*(i+1))) for i in range(NR)] for p in q])
    o.append(f'<path d="{path}" fill="none" stroke="#1d2126" stroke-width="2"/>')
    top=base-s*RISE; slab_end=xe-s*TR*NR
    o.append(f'<rect x="{x0-30}" y="{top-2}" width="{slab_end-(x0-30):.1f}" height="10" fill="#BFB8AC" stroke="#1d2126" stroke-width="1"/>')
    o.append(f'<rect x="{slab_end+s*3.4:.1f}" y="{top-2}" width="{xe+40-(slab_end+s*3.4):.1f}" height="10" fill="#BFB8AC" stroke="#1d2126" stroke-width="1"/>')
    o.append(f'<text x="{slab_end+s*1.7:.0f}" y="{top-34}" class="ts" text-anchor="middle" dominant-baseline="central">فتحة في سقف الأرضي ٣.٤ م تبدأ من آخر درجة</text>')
    hx=slab_end+s*3.4; hy_step=base-s*(RISE/NR)*(NR-3.4/TR)
    o.append(f'<line x1="{hx:.1f}" y1="{top+8}" x2="{hx:.1f}" y2="{hy_step:.1f}" stroke="#3a414b" stroke-width="1" stroke-dasharray="3 2" marker-start="url(#arg)" marker-end="url(#arg)"/>')
    o.append(f'<text x="{hx+14:.1f}" y="{(top+hy_step)/2:.0f}" class="ts" text-anchor="end" dominant-baseline="central">ارتفاع صافي ≥ ٢.١٠ م</text>')
    o.append(f'<line x1="{x0-30}" y1="{base}" x2="{xe+40:.1f}" y2="{base}" stroke="#1d2126" stroke-width="2.5"/>')
    o.append(f'<line x1="{xe+24:.1f}" y1="{base}" x2="{xe+24:.1f}" y2="{top}" stroke="#3a414b" stroke-width="1" marker-start="url(#arg)" marker-end="url(#arg)"/>')
    o.append(f'<text x="{xe+40:.1f}" y="{(base+top)/2:.0f}" class="t" text-anchor="middle" dominant-baseline="central" transform="rotate(-90 {xe+40:.1f} {(base+top)/2:.0f})">٢٢ قائمة × ١٧ سم = ٣.٧٥ م</text>')
    o.append(f'<line x1="{xe:.1f}" y1="{base-s*0.9}" x2="{slab_end:.1f}" y2="{top-s*0.9}" stroke="#556070" stroke-width="2"/>')
    o.append(f'<text x="{(xe+slab_end)/2:.0f}" y="{(base+top)/2-s*0.9-10:.0f}" class="ts" text-anchor="middle" dominant-baseline="central" transform="rotate(-33 {(xe+slab_end)/2:.0f} {(base+top)/2-s*0.9-10:.0f})">درابزين ٩٠ سم</text>')
    o.append(f'<text x="{x0+10}" y="{top-30}" class="ts" text-anchor="end" dominant-baseline="central">أرضية الدور الثاني</text>')
    o.append(f'<text x="{xe-10:.0f}" y="{base+16}" class="ts" text-anchor="start" dominant-baseline="central">أرضية المخزن</text>')
    o.append(f'<text x="{x0+s*1.5:.0f}" y="{base-s*1.2:.0f}" class="ts" text-anchor="middle" dominant-baseline="central">تحت السلم: تخزين</text>')
    o.append('</svg>'); return '\n'.join(o)
def columns_svg(k):
    o=[svg_open('0 0 680 300','قطاعات العمدان')]; sc=120
    def col(x,y,w,h,label,sub,fill):
        W,H=w*sc,h*sc
        return (f'<rect x="{x-W/2:.0f}" y="{y-H/2:.0f}" width="{W:.0f}" height="{H:.0f}" fill="{fill}" stroke="#1d2126" stroke-width="1"/>'
                f'<text x="{x}" y="{y+H/2+16:.0f}" class="t" text-anchor="middle" dominant-baseline="central">{label}</text>'
                f'<text x="{x}" y="{y+H/2+32:.0f}" class="ts" text-anchor="middle" dominant-baseline="central">{sub}</text>')
    tr=k in (1,6); wall12=(0.3,0.8) if tr else (0.25,0.7); wall34=(0.25,0.6); inn12=(0.4,0.4); inn34=(0.3,0.3)
    o.append('<text x="510" y="24" class="th" text-anchor="middle" dominant-baseline="central">الدور الأول والثاني (المخزن)</text>')
    o.append('<text x="170" y="24" class="th" text-anchor="middle" dominant-baseline="central">الدور الثالث والرابع (الشقق)</text>')
    o.append('<line x1="340" y1="40" x2="340" y2="290" stroke="#b9bec7" stroke-width="1" stroke-dasharray="4 3"/>')
    o.append(col(430,130,*wall12,f'عمود حيطة {ar(wall12[0]*100,0)} × {ar(wall12[1]*100,0)}','مخفي في سمك الحيطة',COL_WALL))
    o.append(col(560,130,*inn12,'عمود ٤٠ × ٤٠','أركان بيت السلم' if tr else 'جوه المخزن وأركان بيت السلم',COL_CORE if tr else COL_IN))
    o.append(col(100,130,*wall34,'عمود حيطة ٢٥ × ٦٠','مخفي في سمك الحيطة',COL_WALL))
    o.append(col(230,130,*inn34,'عمود ٣٠ × ٣٠','في تقاطع الحيطان وأركان بيت السلم',COL_CORE if tr else COL_IN))
    o.append('<text x="340" y="280" class="ts" text-anchor="middle" dominant-baseline="central">المقاسات بالسنتيمتر، والرسم بمقياس واحد للمقارنة. نفس العمود بيكمل من الأساس للسطح وبيصغر فوق سقف المخزن.</text>')
    o.append('</svg>'); return '\n'.join(o)

COLINFO={
1:('نظام الكمرات المحوّلة','١٢ عمود: كلهم في الحيطان الخارجية وأركان بيت السلم. صفر عمود جوه المخزن. ٣ كمرات تحويل ٣٠ × ١٠٠ سم في سقف الدور الثاني بتشيل حيطان الشقق.','عمدان الحيطان ٣٠ × ٨٠ في المخزن (حمل أكبر بسبب كمرات التحويل) وبتصغر لـ ٢٥ × ٦٠ في الشقق.'),
2:('نظام الشبكة العادية','١٣ عمود: ٨ في الحيطان الخارجية، ٤ أركان بيت السلم، وعمود واحد جوه المخزن عند ٣.٤ م من الواجهة و ٥.٧ م من الجار الشمال.','عمدان الحيطان ٢٥ × ٧٠ في المخزن وبتصغر لـ ٢٥ × ٦٠ في الشقق. العمود الداخلي ٤٠ × ٤٠ في المخزن و ٣٠ × ٣٠ في الشقق.'),
3:('نظام الشبكة العادية','١٣ عمود: زي ترشيح ٢، والعمود الداخلي عند ٦.٩ م من ركن الشارعين على خط حيطة نوم ١.','عمدان الحيطان ٢٥ × ٧٠ في المخزن و ٢٥ × ٦٠ في الشقق. العمود الداخلي ٤٠ × ٤٠ ثم ٣٠ × ٣٠.'),
4:('نظام الشبكة العادية','١٣ عمود: زي ترشيح ٣، مع عمود الحيطة الشمال عند ١٢.٦ م.','عمدان الحيطان ٢٥ × ٧٠ في المخزن و ٢٥ × ٦٠ في الشقق. العمود الداخلي ٤٠ × ٤٠ ثم ٣٠ × ٣٠.'),
5:('نظام الشبكة العادية','١٣ عمود: مطابق لترشيح ٢ حرفيًا.','عمدان الحيطان ٢٥ × ٧٠ في المخزن و ٢٥ × ٦٠ في الشقق. العمود الداخلي ٤٠ × ٤٠ ثم ٣٠ × ٣٠.'),
6:('نظام الكمرات المحوّلة','١٢ عمود: كلهم في الحيطان الخارجية وأركان بيت السلم على خطوط حيطان ترشيح ٢. صفر عمود جوه المخزن. ٣ كمرات تحويل ٣٠ × ١٠٠ سم في سقف الدور الثاني بتشيل حيطان الشقة.','عمدان الحيطان ٣٠ × ٨٠ في المخزن (حمل أكبر بسبب كمرات التحويل) وبتصغر لـ ٢٥ × ٦٠ في الشقق.'),
}
WELL_NOTE={1:'نوم ٢ على المنور',2:'الصالة من غير شباك',3:'نوم ٣ على المنور',4:'نوم ٣ على المنور',5:'الصالة من غير شباك',6:'الصالة من غير شباك'}
COLINFO[7]=COLINFO[2]; WELL_NOTE[7]='الصالة مفتوحة على المدخل (استقبال)'
COLINFO[8]=COLINFO[2]; WELL_NOTE[8]='الصالة مفتوحة على المدخل (استقبال)، و٤ أوض نوم'
CSS='''
@page{size:A4;margin:12mm 12mm 14mm}
html,body{margin:0;padding:0;background:#fff;color:#1d2126;font-family:"Geeza Pro","Al Nile","Noto Naskh Arabic","Arial",sans-serif;font-size:3.5mm;line-height:1.6}
.page{width:186mm;height:269mm;page-break-after:always;position:relative;overflow:hidden}
.page:last-child{page-break-after:auto}
.hdr{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:0.5mm solid #1F5FBF;padding-bottom:2mm;margin-bottom:3mm}
h1{font-size:6.2mm;margin:0;font-weight:700;line-height:1.3} h2{font-size:5.2mm;margin:0;font-weight:700}
.sub{color:#5b6472;font-size:3.1mm;margin:1mm 0 0} .pg{font-size:3mm;color:#5b6472;white-space:nowrap}
table{border-collapse:collapse;width:100%;font-size:3.3mm} th,td{border:0.2mm solid #b9bec7;padding:1.2mm 1.8mm;text-align:right} th{background:#eef2f9;font-weight:700} td.n,th.n{text-align:left;white-space:nowrap;font-variant-numeric:tabular-nums}
.big svg{width:186mm;height:auto;display:block;margin:0 auto 2mm} .mid svg{width:186mm;height:153mm;display:block;margin:0 auto 2mm} .small svg{width:186mm;height:82mm;display:block;margin:0 auto 2mm}
.fact{border:0.3mm solid #b9bec7;border-radius:2mm;padding:2mm 3mm;margin:2mm 0;font-size:3.2mm} .fact b{color:#1F5FBF}
.rules{border:0.3mm solid #1F5FBF;border-radius:2mm;padding:2.5mm 3mm;margin:0 0 3mm;background:#f2f6fc;font-size:3.3mm} .rules ol{padding:0 5mm 0 0;margin:0} .rules li{margin:1mm 0}
h3{font-size:4.2mm;margin:4mm 0 2mm;font-weight:700;color:#1F5FBF}
.legend{font-size:3mm;color:#5b6472;margin:2mm 0 0}
.kv{display:grid;grid-template-columns:1fr 1fr;gap:2mm 4mm;font-size:3.2mm}
.foot{position:absolute;bottom:0;left:0;right:0;border-top:0.2mm solid #b9bec7;padding-top:1.5mm;font-size:2.8mm;color:#5b6472;display:flex;justify-content:space-between}
svg .t{font-size:11px;fill:#1d2126} svg .ts{font-size:9px;fill:#3a414b} svg .th{font-size:13px;font-weight:700;fill:#1d2126}
'''
def build(k):
    pl=PLANS[k]; title=pl['title'].split(': ',1)[1]; sysname,cnt,sizes=COLINFO[k]; N=7; KN={7:'٢ب',8:'٣'}.get(k,ar(k,0))
    rows=[r for r in pl['rows'] if r['n']!='منور']
    big=[r for r in rows if r['a']>=5]; small=[r for r in rows if r['a']<5]
    tr=''.join(f'<tr><td>{r["n"]}</td><td class="n">{r.get("dim") or ar(r["w"])+" × "+ar(r["h"])}</td><td class="n">{ar(r["a"])}</td></tr>' for r in big)
    bd=pl.get('balc_d',1.8); bal=' و '.join(f'{ar(x2-x1)} × {ar(bd,2)}' for x1,x2 in pl['balc'])
    if small: tr+=f'<tr><td>{" + ".join(dict.fromkeys(r["n"] for r in small))}</td><td class="n">—</td><td class="n">{ar(sum(r["a"] for r in small))}</td></tr>'
    tot=sum(r['a'] for r in rows); dw=pl['whdoor'][1]-pl['whdoor'][0]
    taken=area([(XL,4.05),(XR,4.05),D2,A]); bd0=pl.get('balc_d',1.8)
    tbal=sum((x2-x1)*bd0 for x1,x2 in pl['balc']) if pl.get('outline3') else 0
    sd_=pl.get('side',0); tside=area([(XR,4.05),(rw2(4.05,sd_),4.05),sh(C2,sd_),C2]) if sd_ else 0
    street=(f' · <b>اللي اتاخد من الشارع (قدام الخط الأحمر):</b> من شارع ١٢ ≈ {ar(taken,0)} م² (منهم {ar(tbal,1)} م² بلكونة)'+(f' ومن شارع ٦ ≈ {ar(tside,0)} م²' if sd_ else '')+f' · المجموع ≈ {ar(taken+tside,0)} م² في الدور' if pl.get('outline3') else '')
    def foot(i): return f'<div class="foot"><span>ترشيح {KN}: {title} · {DATE}</span><span>صفحة {ar(i,0)} من {ar(N,0)}</span></div>'
    def hdr(t,sub,i,h1=False): return f'<div class="hdr"><div>{"<h1>" if h1 else "<h2>"}{t}{"</h1>" if h1 else "</h2>"}<p class="sub">{sub}</p></div><div class="pg">صفحة {ar(i,0)} من {ar(N,0)}</div></div>'
    pages=[]
    pages.append(f'''<div class="page">{hdr(f'ترشيح {KN}: {title}','العمارة كاملة: مخزن دورين + شقتين · أرض ناصية على شارع ١٢ م وشارع ٦ م · الجزء المبني ١٠٥ م² · '+DATE,1,True)}
<div class="rules"><b>اللي في الملف ده:</b><ol>
<li><b>الدور الأول (الأرضي):</b> مخزن فاضي ≈ {ar(G_AREA,0)} م²، باب رول {ar(dw)} م على شارع الـ ١٢، سلم داخلي للدور الثاني، ومجرى مواسير ٤٠ × ٦٠ في الضهر. مفيش منور.</li>
<li><b>الدور الثاني:</b> مخزن كامل ≈ {ar(f2_area(pl),0)} م² مع بروز ١.٨٠ م فوق شارع ١٢{(' و '+ar(pl['side'],2)+' م فوق شارع ٦') if pl.get('side') else ''}، فتحة السلم ١.٢ × ٣.٤ وفتحة ونش ١.٢ × ١.٢.</li>
<li><b>الدور الثالث والرابع:</b> شقة في كل دور بنفس التقسيم (≈ {ar(tot,0)} م² صافي).</li>
<li><b>العمدان:</b> {sysname}. {cnt}</li>
<li><b>سلم المخزن:</b> مستقيم ٢٢ درجة، عرض ١.٢٠ م، طول ٦.٩ م موازي لحيطة الجار الشمال.</li></ol></div>
<h3>مساحات الشقة (الدور الثالث = الرابع)</h3>
<table><tr><th>الأوضة</th><th>المقاس (م)</th><th>م²</th></tr>{tr}<tr><th>الصافي</th><th></th><th class="n">≈ {ar(tot,0)}</th></tr></table>
<div class="fact" style="margin-top:4mm"><b>الرموز:</b> <span style="color:{COL_WALL}">■</span> عمود مخفي في حيطة خارجية · <span style="color:{COL_CORE}">■</span> ركن بيت السلم · <span style="color:{COL_IN}">■</span> عمود جوه المخزن · <span style="color:#8A4B12">▬</span> كمرة (المتقطع = كمرة تحويل) · <span style="color:{DOOR}"><b>▬</b></span> باب (القوس المتقطع = اتجاه الفتح، والخط المزدوج = باب زجاج منزلق، والمتقطع العريض = باب المخزن الرول) · <span style="color:#1F5FBF">▬</span> شباك · أخضر = بروز الدور الثاني · رمادي = فتحة السلم · بنفسجي = فتحة الونش.</div>
<div class="fact"><b>التعديلات عن النسخة الأولى:</b> باب الشقة بقى ٠.٩٠ بجوغ ٦٠ سم في حيطة الحمام · سلم المخزن موازي لحيطة الجار المايلة (مش على محور الورقة) · فتحة السلم في سقف الأرضي بتبدأ من آخر درجة وترجع ٣.٤ م زي القطاع.</div>
{'<div class="fact"><b>التعديلات الجديدة (٥ أكتوبر):</b> شلنا الغسيل (دخل في الصالة) والكرار (دخل في المنور، بقى عرضه ٢.٥ م) · هول خاص للنوم من المدخل لحد الواجهة، والتلات أوض بيفتحوا عليه · واجهة الشقة كلها طلعت لقدام ١.٨٠ م ودخلت في نوم ١ ونوم ٢ · بلكونة واحدة ٢.٥ × ١.٥ في نوم ١، ونوم ٢ ليها شباك · الأبواب برتقالي بخط عريض.'+(' · الصالة واخدة المدخل والهول من غير حيطان (≈ ٢٥ م²)، علشان الضيوف يدخلوا عليها من باب الشقة على طول.' if k in (7,8) else '')+(' · مكان نوم ١ ونوم ٢ بقى ٣ أوض جنب بعض على شارع ١٢ (≈ ١٧ و ١٤ و ٢٥ م²)، نوم ١ بتفتح على الصالة، ونوم ٢ ونوم ٤ على دخلة صغيرة ١ × ١ م من الصالة، والبلكونة في نوم ٢ · حيطة نوم ٣ على نفس خط الصالة (نوم ٣ ≈ ١٦ م²).' if k==8 else '')+'</div>' if k in (2,7,8) else ''}
<p class="legend">{'البلكونة ١.٥ م وبروز الأوض ١.٨٠ م والمنور ٢.٥ × ١.١ حسب طلبك. القانون بيسمح ببلكونة ١.٢٠ م وبروز مقفول ٦٠ سم بس، ومنور المطبخ أقل حاجة ٢.٥ × ٣ م.' if k in (2,7,8) else 'البروز ١.٨٠ م والمنور ١ × ١.٥ حسب طلبك، والقانون بيسمح ببروز مفتوح ١.٢٥ م ومنور ٢.٥ م عرض.'} المقاسات تقريبية والحساب الإنشائي النهائي للمهندس الإنشائي.</p>
{foot(1)}</div>''')
    for fl,ttl in ((1,'الدور الأول: مخزن'),(2,'الدور الثاني: مخزن كامل + بروز')):
        pages.append(f'''<div class="page">{hdr(ttl,f'ترشيح {KN} · {sysname} · نفس عمدان الشقق فوق',fl+1)}
<div class="big">{wh_svg(pl,fl)}</div>
<div class="fact"><b>المساحة الفاضية:</b> ≈ {ar(G_AREA if fl==1 else f2_area(pl),0)} م² · <b>الارتفاع:</b> ٣.٧٥ م · <b>العمدان:</b> {cnt}</div>
{foot(fl+1)}</div>''')
    for fl in (3,4):
        pages.append(f'''<div class="page">{hdr(f'الدور {"الثالث" if fl==3 else "الرابع"}: شقة',pl['desc'],fl+1)}
<div class="big">{flat_svg(pl,fl)}</div>
<div class="fact"><b>الصافي:</b> ≈ {ar(tot,0)} م² · <b>الأبواب (برتقالي):</b> {ar(len(pl['leaves'])+1,0)} عادية (٠.٩٠ × ٢.١٠) + {ar(sum(1 for op in pl['front'] if op.get('k')!='win'),0)} منزلق · <b>البلكونات:</b> عرض {ar(bd,2)} م على شارع الـ ١٢ ·{"نفس تقسيم الدور الثالث بالظبط، الحمامات والمطابخ فوق بعض." if fl==4 else WELL_NOTE[k]}{street}</div>
{foot(fl+1)}</div>''')
    pages.append(f'''<div class="page">{hdr('تفاصيل العمدان',f'ترشيح {KN} · {sysname}',6)}
<div class="small">{columns_svg(k)}</div>
<div class="fact"><b>العدد والأماكن:</b> {cnt}</div>
<div class="fact"><b>المقاسات:</b> {sizes}</div>
<div class="fact"><b>الكمرات:</b> {"كمرات تحويل ٣٠ × ١٠٠ سم تحت الشقق (٣ كمرات)، وباقي الكمرات ٢٥ × ٦٠." if k in (1,6) else "كمرات ٢٥ × ٦٠ سم في المخزن (بحر ٥.٧ م)، و ٢٥ × ٥٠ في الشقق. كمرة بروز الدور الثاني ٢٥ × ٧٠ كابولي ١.٨٠ م."}</div>
<div class="fact"><b>الأسقف:</b> بلاطة ١٥ سم في المخزن (حمل تخزين ٥٠٠ كجم/م²) و ١٢ سم في الشقق.</div>
<div class="fact"><b>ليه العمدان واحدة في الأربع أدوار:</b> كل عمود بينزل في خط واحد من السطح للأساس. اللي بيتغير بس المقاس: أكبر في المخزن لأنه شايل الأدوار اللي فوقه، وأصغر في الشقق. ده أرخص وأأمن من أي تحويل حمل.</div>
{foot(6)}</div>''')
    pages.append(f'''<div class="page">{hdr('تفاصيل سلم المخزن (الأول ← الثاني)','مستقيم، لازق في حيطة الجار الشمال، في ضهر المخزن',7)}
<div class="mid">{stair_svg()}</div>
<div class="kv"><div class="fact"><b>الدرجات:</b> ٢٢ قائمة × ١٧ سم = ٣.٧٥ م ارتفاع</div><div class="fact"><b>النوائم:</b> ٢١ × ٢٧ سم = {ar(NT*TR)} م + بسطة ١.٢٠ م</div>
<div class="fact"><b>العرض:</b> ١.٢٠ م صافي، درابزين ٩٠ سم</div><div class="fact"><b>فتحة السقف:</b> ١.٢٠ × ٣.٤٠ م، ارتفاع صافي فوق أي درجة ≥ ٢.١٠ م</div>
<div class="fact"><b>اللي بياخده من الأرضي:</b> صفر، تحته تخزين</div><div class="fact"><b>اللي بياخده من الدور الثاني:</b> ≈ ٤ م² (الفتحة)</div></div>
{foot(7)}</div>''')
    html='<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>ترشيح %s</title><style>'%KN+CSS+'</style></head><body>'+''.join(pages)+'</body></html>'
    hp=os.path.join(OUT,f'set{k}.html'); open(hp,'w',encoding='utf-8').write(html)
    pdf=os.path.join(OUT,f'ترشيح{ {7:"2ب",8:"3-الجديد"}.get(k,k) }.pdf')
    r=subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--disable-gpu','--no-sandbox','--no-pdf-header-footer','--print-to-pdf='+pdf,'file://'+hp],capture_output=True,text=True,timeout=180)
    d=open(pdf,'rb').read() if os.path.exists(pdf) else b''
    npg=len(re.findall(rb"/Type\s*/Page[^s]",d))
    print(f'plan {k}: pdf {len(d)} bytes, pages {npg}')
if __name__=='__main__':
    print(f'G_AREA {G_AREA:.1f}  F2_AREA {F2_AREA:.1f}')
    import sys
    ks=[int(a) for a in sys.argv[1:]] or sorted(PLANS)
    for k in ks: build(k)
