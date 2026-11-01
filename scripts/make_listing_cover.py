"""Render the mod.io listing cover (outline style): in-game shot, headline, country outline with the big four towns.
Usage: make_listing_cover.py <out_dir> [scale]   (Germany only for now; 1280x720 times scale)"""
import json, math, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]; OUT = Path(sys.argv[1]); SCALE = sys.argv[2] if len(sys.argv) > 2 else '1'
F = R/'assets'/'fonts'; SH = R/'shots'/'germany'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
g = json.load(open(R/'output/germany/border.geojson'))['geometry']['coordinates']
towns = {t['name']: t for t in json.load(open(R/'output/germany/towns.json'))}
k = math.cos(math.radians(51.2))
pts = [p for poly in g for p in poly[0]]
x0, x1 = min(p[0]*k for p in pts), max(p[0]*k for p in pts); y0, y1 = min(-p[1] for p in pts), max(-p[1] for p in pts)
def proj(lon, lat, W, H, pad=0):
    s = min((W-2*pad)/(x1-x0), (H-2*pad)/(y1-y0)); ox = (W-(x1-x0)*s)/2; oy = (H-(y1-y0)*s)/2
    return ox+(lon*k-x0)*s, oy+(-lat-y0)*s
def path(W, H, pad=0):
    return ''.join('M' + 'L'.join('%.1f,%.1f' % proj(lon, lat, W, H, pad) for lon, lat in poly[0][::2]) + 'Z' for poly in g if len(poly[0]) >= 20)
LEFT = {'Berlin'}
def dots(W, H, names, pad=0, r=9, size=30):
    s = ''
    for n in names:
        x, y = proj(towns[n]['lon'], towns[n]['lat'], W, H, pad); left = n in LEFT
        anc = 'end' if left else 'start'; tx = x-r-8 if left else x+r+8
        s += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" stroke="#111" stroke-width="3"/>'
        s += f'<text text-anchor="{anc}" x="{tx:.0f}" y="{y+size*0.35:.0f}" font-family="Manrope" font-weight="800" font-size="{size}" fill="#fff" stroke="#111" stroke-width="6" paint-order="stroke">{n}</text>'
    return s
W, H = 470, 640
html = f"""<!doctype html><meta charset=utf-8><style>@font-face{{font-family:Manrope;src:url('file://{F}/Manrope.ttf')}}
*{{margin:0;box-sizing:border-box}}body{{width:1280px;height:720px;overflow:hidden;position:relative;background:#111;font-family:Manrope;color:#fff}}
.bg{{position:absolute;inset:0;background-size:cover;background-position:center}}
.flag{{display:flex;height:14px;width:260px;border-radius:3px;overflow:hidden}}.flag i{{flex:1}}.flag i:nth-child(1){{background:#000;outline:1px solid #555}}.flag i:nth-child(2){{background:#DD0000}}.flag i:nth-child(3){{background:#FFCE00}}
.big{{font:800 150px/.9 Manrope;letter-spacing:-.05em;text-shadow:0 6px 30px rgba(0,0,0,.55)}}
.chip{{display:inline-block;font:800 34px Manrope;padding:12px 22px;border-radius:10px;background:#FFCE00;color:#111}}
.mark{{position:absolute;right:34px;bottom:26px;font:800 26px Manrope;letter-spacing:-.04em;opacity:.9}}.mark i{{color:#E0603C;font-style:normal}}</style><body>
<div class="bg" style="background-image:url('file://{SH}/hamburg.png');background-position:60% 50%"></div>
<div class="bg" style="background:linear-gradient(90deg,rgba(10,10,10,.92) 0%,rgba(10,10,10,.7) 42%,rgba(10,10,10,.1) 70%)"></div>
<img src="file://{R}/assets/tf3-logo.png" style="position:absolute;left:64px;top:44px;height:78px;filter:drop-shadow(0 3px 10px rgba(0,0,0,.6))">
<div style="position:absolute;left:64px;top:168px"><div class="flag"><i></i><i></i><i></i></div><div class="big" style="margin-top:26px">GERMANY</div>
<div style="font:700 46px/1.15 Manrope;margin-top:20px;max-width:600px">Real terrain,<br>real rivers.</div>
<div class="chip" style="margin-top:34px">60 REAL TOWNS</div></div>
<svg style="position:absolute;right:40px;top:40px" width="{W}" height="{H}"><path d="{path(W,H,20)}" fill="rgba(0,0,0,.35)" stroke="#FFCE00" stroke-width="6" stroke-linejoin="round"/>{dots(W,H,['Berlin','Hamburg','München','Köln'],20)}</svg>
<div class="mark">Aimantas<i>.</i></div></body>"""
OUT.mkdir(parents=True, exist_ok=True); f = OUT/'cover.html'; f.write_text(html)
subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--force-device-scale-factor={SCALE}', f'--screenshot={OUT}/cover.png',
                '--window-size=1280,720', '--virtual-time-budget=3000', f'file://{f}'], capture_output=True, check=True)
print(OUT/'cover.png')
