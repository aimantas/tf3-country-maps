"""Listing cover v2 (in-game shot, big country name, outline, four towns). Usage: make_listing_v2.py <country-id>  -> art/<id>/listing-v2/cover.png (1920x1080)"""
import json, math, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]; ID = sys.argv[1]; SAVE = len(sys.argv) > 2 and sys.argv[2] == 'save'
CFG = json.load(open(R/'configs'/f'{ID}.json')); OUT = R/'art'/ID/('listing-save' if SAVE else 'listing-v2'); OUT.mkdir(parents=True, exist_ok=True)
S = {  # per-country: label, accent, chip text colour, background shot + focus, towns, flag html
 'germany': dict(name='GERMANY', sub='Real terrain,<br>real rivers.', acc='#FFCE00', ink='#111', bg='hamburg', pos='60% 50%', towns=['Berlin','Hamburg','München','Köln']),
 'switzerland': dict(name='SWITZERLAND', sub='Real Alps,<br>real lakes.', acc='#FF4B3E', ink='#fff', bg='zuerich', pos='55% 50%', towns=['Zürich','Genève','Lugano','Bern']),
 'austria': dict(name='AUSTRIA', sub='Real Alps,<br>the Danube.', acc='#FF5A66', ink='#fff', bg='wien', pos='55% 50%', towns=['Wien','Salzburg','Innsbruck','Graz']),
 'hungary': dict(name='HUNGARY', sub='Real terrain,<br>Lake Balaton.', acc='#6FD98A', ink='#111', bg='budapest', pos='55% 50%', towns=['Budapest','Debrecen','Szeged','Pécs']),
 'netherlands': dict(name='NETHERLANDS', sub='Flat land,<br>big rivers.', acc='#FF8A1F', ink='#111', bg='amsterdam', pos='55% 50%', towns=['Amsterdam','Groningen','Eindhoven','Den Haag']),
}[ID]
g = json.load(open(R/'output'/ID/'border.geojson'))
g = g.get('geometry', g); polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
towns = {t['name']: t for t in json.load(open(R/'output'/ID/'towns.json'))}
lat0 = sum(t['lat'] for t in towns.values())/len(towns); k = math.cos(math.radians(lat0))
pts = [p for poly in polys for p in poly[0]]
x0, x1 = min(p[0]*k for p in pts), max(p[0]*k for p in pts); y0, y1 = min(-p[1] for p in pts), max(-p[1] for p in pts)
W, H = {'germany':560,'switzerland':660,'austria':900,'hungary':800,'netherlands':700}[ID], 960
LEFT = {'germany':{'Berlin'},'hungary':{'Budapest','Pécs'},'austria':{'Salzburg','Innsbruck'},'switzerland':{'Genève','Bern'},'netherlands':{'Den Haag','Groningen'}}[ID]; PAD = 40
def proj(lon, lat):
    s = min((W-2*PAD)/(x1-x0), (H-2*PAD)/(y1-y0)); return (W-(x1-x0)*s)/2+(lon*k-x0)*s, (H-(y1-y0)*s)/2+(-lat-y0)*s
step = max(1, len(pts)//1500)
path = ''.join('M'+'L'.join('%.1f,%.1f' % proj(*p) for p in poly[0][::step])+'Z' for poly in polys if len(poly[0]) >= 12)
dots = ''
for n in S['towns']:
    x, y = proj(towns[n]['lon'], towns[n]['lat']); left = n in LEFT
    tx = x-24 if left else x+24
    dots += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="14" fill="#fff" stroke="#111" stroke-width="4"/><text text-anchor="{"end" if left else "start"}" x="{tx:.0f}" y="{y+13:.0f}" font-family="Manrope" font-weight="800" font-size="44" fill="#fff" stroke="#111" stroke-width="8" paint-order="stroke">{n}</text>'
fl = CFG['flag']
flag = ('<div style="width:110px;height:110px;background:#DA291C;border-radius:8px;position:relative"><i style="position:absolute;left:44px;top:20px;width:22px;height:70px;background:#fff"></i><i style="position:absolute;left:20px;top:44px;width:70px;height:22px;background:#fff"></i></div>'
        if isinstance(fl,str) else
        '<div style="display:flex;height:22px;width:380px;border-radius:4px;overflow:hidden;outline:1px solid #555">'+''.join(f'<i style="flex:1;background:{c}"></i>' for c in fl)+'</div>')
size = {7:215,8:215}.get(len(S['name']), 150 if len(S['name'])>=11 else 200)
html = f"""<!doctype html><meta charset=utf-8><style>@font-face{{font-family:Manrope;src:url('file://{R}/assets/fonts/Manrope.ttf')}}
*{{margin:0;box-sizing:border-box}}body{{width:1920px;height:1080px;overflow:hidden;position:relative;background:#111;font-family:Manrope;color:#fff}}
.bg{{position:absolute;inset:0;background-size:cover}}</style><body>
<div class="bg" style="background-image:url('file://{R}/shots/{ID}/{S['bg']}.png');background-position:{S['pos']}"></div>
<div class="bg" style="background:linear-gradient(90deg,rgba(10,10,10,.94) 0%,rgba(10,10,10,.74) 42%,rgba(10,10,10,.1) 72%)"></div>
<img src="file://{R}/assets/tf3-logo.png" style="position:absolute;left:96px;top:66px;height:117px;filter:drop-shadow(0 4px 14px rgba(0,0,0,.6))">
<div style="position:absolute;left:96px;top:252px">{flag}
<div style="font:800 {size}px/.9 Manrope;letter-spacing:-.05em;margin-top:36px;text-shadow:0 8px 40px rgba(0,0,0,.55)">{S['name']}</div>
<div style="font:700 69px/1.15 Manrope;margin-top:30px">{S['sub']}</div>
<div style="display:inline-block;font:800 51px Manrope;padding:18px 33px;border-radius:15px;background:{S['acc']};color:{S['ink']};margin-top:51px">{'READY TO PLAY' if SAVE else str(CFG['towns'])+' REAL TOWNS'}</div>{'<div style="font:700 40px Manrope;margin-top:22px;opacity:.92">'+str(CFG['towns'])+' real towns. Just start a new game.</div>' if SAVE else ''}</div>
<svg style="position:absolute;right:110px;top:60px;overflow:visible" width="{W}" height="{H}"><path d="{path}" fill="rgba(0,0,0,.35)" stroke="{S['acc']}" stroke-width="8" stroke-linejoin="round"/>{dots}</svg>
<div style="position:absolute;right:51px;bottom:39px;font:800 39px Manrope;letter-spacing:-.04em;opacity:.9">Aimantas<i style="color:#E0603C;font-style:normal">.</i></div></body>"""
f = OUT/'cover.html'; f.write_text(html)
subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1',f'--screenshot={OUT}/cover.png','--window-size=1920,1080','--virtual-time-budget=3000',f'file://{f}'], capture_output=True, check=True)
subprocess.run(['sips','-s','format','jpeg','-s','formatOptions','88',str(OUT/'cover.png'),'--out',str(OUT/'g01-cover.jpg')], capture_output=True, check=True)
print(OUT/'g01-cover.jpg')
