#!/bin/bash
# The pictures behind brochure3d.py: the 3D page served on http://localhost:4617 (index.html), proposal ريسبشن ٢,
# clean view (?ui=0), fixed cameras (?cam=x,y,z,tx,ty,tz in world metres: x, height, -plan_y).
# ./render3d_shots.sh <out folder>   (then: python3 brochure3d.py <out folder>)
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; OUT="$1"; mkdir -p "$OUT"
shot(){ "$CH" --headless=new --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader --hide-scrollbars --window-size=1600,1000 --force-device-scale-factor=2 --virtual-time-budget=15000 --screenshot="$OUT/$1.png" "http://localhost:4617/?p=r2&cols=0&ui=0&$2" >/dev/null 2>&1; echo "$1"; }
shot cover      "labels=0&cam=10,13,15,-1.5,6,-11"
shot front12    "labels=0&cam=-5,11.5,20,-6,7.5,-8"
shot side6      "labels=0&cam=17,17,-7,-4,6.5,-10"
shot flat3      "f=2&cam=-2.5,26,-3,-6.5,7.5,-10.5"
shot dh_rec     "f=2&labels=0&cam=-9.8,18,2,-9.6,7.5,-10"
shot dh_corner  "f=2&labels=0&cam=4,16,0,-5.5,7.5,-9"
shot bed2       "f=2&labels=0&cam=-4.6,9.1,-8.4,-0.8,8.3,-4.8"
shot wh1        "f=0&labels=0&cam=-6,12,1.5,-6,1.5,-10"
shot wh2        "f=1&labels=0&cam=-6,15,1.5,-6,5,-10"
