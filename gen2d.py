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
PROJ=[(-12.12,4.05),(-1.62,4.05),D2,C2,B2,A]                 # floor-2 outline with the 1.80 projection
F2=[(-12.12,4.05),(-1.62,4.05),D2,P1,P2,P3,B2,A]
def area(p): return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))/2
G_AREA=area(SLAB)-area(DUCT); F2_AREA=area(F2)-1.2*3.4-area(HOIST)-area(DUCT)

# ---- 5 Oct 2026, his ask, proposal 2 only. 2D only: the 3D page still reads the old layout from data3d.js ----
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
    # closed bay 0.60 deep over the middle 5.0 m of the 12 m facade (law: closed projection <= 5% of street width and <= half the facade);
    # the two balconies (2.0 long x 1.50 deep) move to the ends: one 1.5 m clear of the left neighbour, one at the street corner
    BX0,BX1,BY=-8.62,-3.62,5.25; p['bay']=[BX0,BX1,BY]
    b1,b2=R['نوم ١']['p'],R['نوم ٢']['p']
    R['نوم ١']['p']=[b1[0],[BX0,5.85],[BX0,BY],[-6.5,BY]]+b1[2:]
    R['نوم ٢']['p']=[[-6.5,BY],[BX1,BY],[BX1,5.85]]+b2[1:]
    W['نوم ١'].update(a=area([T(q) for q in R['نوم ١']['p']]),dim='٥.٦ × ٣.٤ + ٢.١ × ٠.٦')
    W['نوم ٢'].update(a=area([T(q) for q in R['نوم ٢']['p']]),dim='٥.٧ × ٣.٤ + ٢.٩ × ٠.٦')
    for w in p['walls']:
        if w['a']==[-6.5,5.959]: w['a']=[-6.5,BY]           # the wall between bedrooms 1 and 2 runs out to the bay front
    p['balc']=[[-10.62,-8.62],[BX1,-1.62]]; p['balc_d']=1.5
    p['front'][0].update(u0=1.70,u1=3.30); p['front'][1].update(u0=8.62,u1=10.12)   # sliding doors 1.60 and 1.50 inside the balconies
    W['حمام']['c']=[-5.75,14.5]; W['هول']['c']=[-7.8,12.9]          # labels moved off the door swings
edit_p2(PLANS[2])
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
def dims(F,fl):
    o=[text(F,'الواجهة ١٠.٥٠ م — شارع ١٢ م',(A[0]+D2[0])/2,3.35 if fl>=2 else 5.2,cls='t')]
    o.append(text(F,'≈ ٨.٨٥ م — شارع ٦ م',*mid(D2,C2,0.75,-0.15),cls='t',rot=rot_along(D2,C2)))
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
    if fl>=3 and plan.get('bay'):
        x0,x1,y=plan['bay']; out=[A,(x0,5.85),(x0,y),(x1,y),(x1,5.85),D2,C2,B2]
    else: out=PROJ if fl==2 else BLD
    o=[poly(F,out,fill='none',stroke='#1d2126',sw=3)]
    if fl==2: o.append(line(F,A,D2,'#1d2126',1,dash='6 4'))
    if fl==1:
        x0,x1=plan['whdoor']; o.append(line(F,(x0,5.85),(x1,5.85),'#ffffff',4)); o.append(line(F,(x0,5.85),(x1,5.85),DOOR,6,dash='10 5'))
        o.append(text(F,f'باب المخزن {ar(x1-x0)} م (رول)',(x0+x1)/2,6.45,cls='ts',fill=DOOR))
    if fl in (1,2):
        for u0,u1 in ((1.2,2.4),(3.4,4.6)): o.append(win(F,upt(D2,C2,u0),upt(D2,C2,u1)))
    if fl==2:
        for x0,x1 in ((-11.2,-9.2),(-7.9,-5.9),(-4.6,-2.6)): o.append(win(F,(x0,4.05),(x1,4.05)))
    if fl>=3:
        for op in plan['front']: o.append(slide(F,(A[0]+op['u0'],5.85),(A[0]+op['u1'],5.85)))
        for op in plan['right']: o.append(win(F,upt(D2,C2,op['u0']),upt(D2,C2,op['u1'])))
    return o
def core_svg(F,fl,plan):
    o=[poly(F,CORE,fill=CLS['c-teal'][0],stroke='#1d2126',sw=3)]
    S0,S1,TR=core['S0'],core['S1'],core['TR']
    for ta,tb in (core['sideA'],core['sideB']):
        for i in range(9): o.append(line(F,cp(S0+i*TR,ta),cp(S0+i*TR,tb),'#556070',0.8))
        o.append(poly(F,[cp(S0,ta),cp(S1,ta),cp(S1,tb),cp(S0,tb)],fill='none',stroke='#556070',sw=0.8))
    for s0,s1 in (core['land_back'],core['land_street']):
        o.append(poly(F,[cp(s0,0.25),cp(s1,0.25),cp(s1,2.75),cp(s0,2.75)],fill='none',stroke='#556070',sw=0.8,dash='3 2'))
    ta,tb=core['sideA']; tm=(ta+tb)/2; rot=rot_along(cp(S1,tm),cp(S0,tm))
    o.append(line(F,cp(S1+0.15,tm),cp(S0-0.1,tm),'#B3261E',1.5,marker='arw'))
    o.append(text(F,'طالع',*cp((S0+S1)/2,tm),cls='ts',rot=rot,fill='#B3261E',dy=-9))
    if fl>=2:
        tb0,tb1=core['sideB']; tm2=(tb0+tb1)/2
        o.append(line(F,cp(S0-0.1,tm2),cp(S1+0.15,tm2),'#3a414b',1.2,marker='arg'))
        o.append(text(F,'نازل',*cp((S0+S1)/2,tm2),cls='ts',rot=rot,fill='#3a414b',dy=-9))
    o.append(text(F,'بيت السلم ٣ × ٥',*cp(2.5,1.5),cls='t',rot=rot,dy=0))
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
def wh_svg(plan,fl):
    F=FR; o=[svg_open(title='مسقط المخزن')]+site(F)
    o.append(poly(F,SLAB if fl==1 else F2,fill='#ffffff',stroke='none'))
    if fl==2: o.append(poly(F,[(-12.12,4.05),(-1.62,4.05),D2,A],fill='#E6F0E6',stroke='#4C8C4A',sw=0.8)); o.append(text(F,'بروز ١.٨٠ م فوق الشارع',(A[0]+D2[0])/2,4.95,cls='ts',fill='#2f6b2f'))
    o+=beams(F,plan,fl)
    o+=ring(F,plan,fl); o+=core_svg(F,fl,plan)
    if fl==1:                          # flats' street door, drawn over the stair box so its swing shows
        sd=core['street_door']; a=upt(P1,C2,sd['t0']); b=upt(P1,C2,sd['t1'])
        o.append(line(F,a,b,'#ffffff',4)); o.append(leaf(F,a,upt((0,0),(C2[0]-P1[0],C2[1]-P1[1]),1),(-U[0],-U[1]),sd['t1']-sd['t0']))
        o.append(text(F,'مدخل الشقق ١.١٠',*mid(a,b,0.9,-0.1),cls='ts',rot=rot_along(P1,C2),fill=DOOR))
    o+=wh_stair(F) if fl==1 else f2_openings(F)
    o+=duct(F); o+=columns(F,plan,fl)
    o.append(text(F,f'مساحة فاضية ≈ {ar(G_AREA if fl==1 else F2_AREA,0)} م²',-6.6,10.6,cls='th'))
    o.append(text(F,'ارتفاع ٣.٧٥ م',-6.6,10.6,cls='ts',dy=16))
    if plan.get('transfer') and fl==2: o.append(text(F,'كمرات تحويل ٣٠ × ١٠٠ سم تحت حيطان الشقة',-6.6,7.4,cls='ts',fill='#8A4B12'))
    o+=dims(F,fl); o+=legend(plan); o.append('</svg>'); return '\n'.join(o)
def flat_svg(plan,fl):
    F=FR; o=[svg_open(title='مسقط الشقة')]+site(F)
    if fl==3: o.append(poly(F,[(-12.12,4.05),(-1.62,4.05),(-1.62,5.85),(-12.12,5.85)],fill='#f1f1ec',stroke='#b9bec7',sw=0.6,dash='3 2'))
    else: o.append(line(F,(-12.12,4.05),(-1.62,4.05),'#b9bec7',0.8,dash='3 2'))
    for r in plan['rooms']:
        fill,stroke=CLS.get(r['cls'],CLS['c-gray']); o.append(poly(F,[T(p) for p in r['p']],fill=fill,stroke=stroke,sw=0.8))
    bd=plan.get('balc_d',1.8)
    for x1,x2 in plan['balc']:
        o.append(poly(F,[(x1,5.85),(x2,5.85),(x2,5.85-bd),(x1,5.85-bd)],fill='#ECEEF1',stroke='#1d2126',sw=1.6))
        o.append(text(F,f'بلكونة {ar(x2-x1)} × {ar(bd,2)}',(x1+x2)/2,5.85-bd/2,cls='ts'))
    if fl==3:
        xs=[-12.12]+[x for b in plan['balc'] for x in b]+[-1.62]
        for i in range(0,len(xs),2):
            if xs[i+1]-xs[i]>1.2: o.append(text(F,'سطح البروز',(xs[i]+xs[i+1])/2,4.95,cls='ts',fill='#8a8f99'))
    o+=wall_lines(F,plan); o+=ring(F,plan,fl); o+=core_svg(F,fl,plan); o+=columns(F,plan,fl)
    for l in plan['leaves']: o.append(leaf(F,T(l['h']),T(l['along']),T(l['out']),l['w']))
    for r in plan['rows']:
        cx,cy=r['c']
        if r['n']=='منور': o.append(text(F,f"منور {ar(r['w'])} × {ar(r['h'])}",cx,cy,cls='ts')); continue
        if r['lbl']:
            o.append(text(F,r['n'],cx,cy,cls='t',dy=-7)); o.append(text(F,f"{r.get('dim') or ar(r['w'])+' × '+ar(r['h'])} ≈ {ar(r['a'],0)} م²",cx,cy,cls='ts',dy=8))
        else: o.append(text(F,r['n'],cx,cy,cls='ts'))
    o+=dims(F,fl); o+=legend(plan); o.append('</svg>'); return '\n'.join(o)

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
    pl=PLANS[k]; title=pl['title'].split(': ',1)[1]; sysname,cnt,sizes=COLINFO[k]; N=7
    rows=[r for r in pl['rows'] if r['n']!='منور']
    big=[r for r in rows if r['a']>=5]; small=[r for r in rows if r['a']<5]
    tr=''.join(f'<tr><td>{r["n"]}</td><td class="n">{r.get("dim") or ar(r["w"])+" × "+ar(r["h"])}</td><td class="n">{ar(r["a"])}</td></tr>' for r in big)
    bd=pl.get('balc_d',1.8); bal=' و '.join(f'{ar(x2-x1)} × {ar(bd,2)}' for x1,x2 in pl['balc'])
    if small: tr+=f'<tr><td>{" + ".join(dict.fromkeys(r["n"] for r in small))}</td><td class="n">—</td><td class="n">{ar(sum(r["a"] for r in small))}</td></tr>'
    tot=sum(r['a'] for r in rows); dw=pl['whdoor'][1]-pl['whdoor'][0]
    def foot(i): return f'<div class="foot"><span>ترشيح {ar(k,0)}: {title} · {DATE}</span><span>صفحة {ar(i,0)} من {ar(N,0)}</span></div>'
    def hdr(t,sub,i,h1=False): return f'<div class="hdr"><div>{"<h1>" if h1 else "<h2>"}{t}{"</h1>" if h1 else "</h2>"}<p class="sub">{sub}</p></div><div class="pg">صفحة {ar(i,0)} من {ar(N,0)}</div></div>'
    pages=[]
    pages.append(f'''<div class="page">{hdr(f'ترشيح {ar(k,0)}: {title}','العمارة كاملة: مخزن دورين + شقتين · أرض ناصية على شارع ١٢ م وشارع ٦ م · الجزء المبني ١٠٥ م² · '+DATE,1,True)}
<div class="rules"><b>اللي في الملف ده:</b><ol>
<li><b>الدور الأول (الأرضي):</b> مخزن فاضي ≈ {ar(G_AREA,0)} م²، باب رول {ar(dw)} م على شارع الـ ١٢، سلم داخلي للدور الثاني، ومجرى مواسير ٤٠ × ٦٠ في الضهر. مفيش منور.</li>
<li><b>الدور الثاني:</b> مخزن كامل ≈ {ar(F2_AREA,0)} م² مع بروز ١.٨٠ م فوق الشارع، فتحة السلم ١.٢ × ٣.٤ وفتحة ونش ١.٢ × ١.٢.</li>
<li><b>الدور الثالث والرابع:</b> شقة في كل دور بنفس التقسيم (≈ {ar(tot,0)} م² صافي).</li>
<li><b>العمدان:</b> {sysname}. {cnt}</li>
<li><b>سلم المخزن:</b> مستقيم ٢٢ درجة، عرض ١.٢٠ م، طول ٦.٩ م موازي لحيطة الجار الشمال.</li></ol></div>
<h3>مساحات الشقة (الدور الثالث = الرابع)</h3>
<table><tr><th>الأوضة</th><th>المقاس (م)</th><th>م²</th></tr>{tr}<tr><th>الصافي</th><th></th><th class="n">≈ {ar(tot,0)}</th></tr></table>
<div class="fact" style="margin-top:4mm"><b>الرموز:</b> <span style="color:{COL_WALL}">■</span> عمود مخفي في حيطة خارجية · <span style="color:{COL_CORE}">■</span> ركن بيت السلم · <span style="color:{COL_IN}">■</span> عمود جوه المخزن · <span style="color:#8A4B12">▬</span> كمرة (المتقطع = كمرة تحويل) · <span style="color:{DOOR}"><b>▬</b></span> باب (القوس المتقطع = اتجاه الفتح، والخط المزدوج = باب زجاج منزلق، والمتقطع العريض = باب المخزن الرول) · <span style="color:#1F5FBF">▬</span> شباك · أخضر = بروز الدور الثاني · رمادي = فتحة السلم · بنفسجي = فتحة الونش.</div>
{'<div class="fact"><b>التعديلات الجديدة (٥ أكتوبر):</b> شلنا الغسيل ومكانه دخل في الصالة (بقت ≈ ٢١ م² بدل ١٩) · شلنا الكرار ومكانه دخل في المنور (بقى عرضه ٢.٥ م) · البلكونتين بقوا ٢ × ١.٥٠ بدل ٤.٦ و ٤.٢ × ١.٨٠، واتنقلوا على الجنبين · بروز مقفول ٠.٦٠ × ٥ م في نص الواجهة، دخل منه ١.٣ م² في نوم ١ و ١.٧ م² في نوم ٢ · الأبواب كلها بقت برتقالي بخط عريض.</div>' if k==2 else ''}
<div class="fact"><b>التعديلات عن النسخة الأولى:</b> باب الشقة بقى ٠.٩٠ بجوغ ٦٠ سم في حيطة الحمام · سلم المخزن موازي لحيطة الجار المايلة (مش على محور الورقة) · فتحة السلم في سقف الأرضي بتبدأ من آخر درجة وترجع ٣.٤ م زي القطاع.</div>
<p class="legend">{'البلكونة ٢ × ١.٥٠ والمنور ٢.٥ م عرض حسب طلبك. القانون: البلكونة المفتوحة على شارع ١٢ أقصاها ١.٢٠ م، والبروز المقفول أقصاه ٠.٦٠ م وعلى نص الواجهة بس، والمنور اللي عليه مطبخ أقل حاجة ٢.٥ × ٣ م.' if k==2 else 'البروز ١.٨٠ م والمنور ١ × ١.٥ حسب طلبك، والقانون بيسمح ببروز مفتوح ١.٢٥ م ومنور ٢.٥ م عرض.'} المقاسات تقريبية والحساب الإنشائي النهائي للمهندس الإنشائي.</p>
{foot(1)}</div>''')
    for fl,ttl in ((1,'الدور الأول: مخزن'),(2,'الدور الثاني: مخزن كامل + بروز')):
        pages.append(f'''<div class="page">{hdr(ttl,f'ترشيح {ar(k,0)} · {sysname} · نفس عمدان الشقق فوق',fl+1)}
<div class="big">{wh_svg(pl,fl)}</div>
<div class="fact"><b>المساحة الفاضية:</b> ≈ {ar(G_AREA if fl==1 else F2_AREA,0)} م² · <b>الارتفاع:</b> ٣.٧٥ م · <b>العمدان:</b> {cnt}</div>
{foot(fl+1)}</div>''')
    for fl in (3,4):
        pages.append(f'''<div class="page">{hdr(f'الدور {"الثالث" if fl==3 else "الرابع"}: شقة',pl['desc'],fl+1)}
<div class="big">{flat_svg(pl,fl)}</div>
<div class="fact"><b>الصافي:</b> ≈ {ar(tot,0)} م² · <b>الأبواب (برتقالي):</b> {ar(len(pl['leaves'])+1,0)} عادية (٠.٩٠ × ٢.١٠) + {ar(len(pl['front']),0)} منزلق · <b>البلكونات:</b> {bal} م على شارع الـ ١٢ ·{"نفس تقسيم الدور الثالث بالظبط، الحمامات والمطابخ فوق بعض." if fl==4 else WELL_NOTE[k]}</div>
{foot(fl+1)}</div>''')
    pages.append(f'''<div class="page">{hdr('تفاصيل العمدان',f'ترشيح {ar(k,0)} · {sysname}',6)}
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
    html='<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>ترشيح %s</title><style>'%ar(k,0)+CSS+'</style></head><body>'+''.join(pages)+'</body></html>'
    hp=os.path.join(OUT,f'set{k}.html'); open(hp,'w',encoding='utf-8').write(html)
    pdf=os.path.join(OUT,f'ترشيح{k}.pdf')
    r=subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--disable-gpu','--no-sandbox','--no-pdf-header-footer','--print-to-pdf='+pdf,'file://'+hp],capture_output=True,text=True,timeout=180)
    d=open(pdf,'rb').read() if os.path.exists(pdf) else b''
    npg=len(re.findall(rb"/Type\s*/Page[^s]",d))
    print(f'plan {k}: pdf {len(d)} bytes, pages {npg}')
if __name__=='__main__':
    print(f'G_AREA {G_AREA:.1f}  F2_AREA {F2_AREA:.1f}')
    import sys
    ks=[int(a) for a in sys.argv[1:]] or sorted(PLANS)
    for k in ks: build(k)
