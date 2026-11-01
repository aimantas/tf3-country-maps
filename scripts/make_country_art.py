"""Render listing art (1920x1080): cover with flag, logo and full country shape, a relief render, and captioned in-game shots.
Usage: make_country_art.py <id>   (needs shots/<id>/*.png, output/<id>/relief.png, assets/tf3-logo.png)"""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'configs' / f'{sys.argv[1]}.json').read_text())
SH = ROOT / 'shots' / CFG['id']; OUT = ROOT / 'art' / CFG['id']; OUT.mkdir(parents=True, exist_ok=True)
RELIEF = ROOT / 'output' / CFG['id'] / 'relief-crop.png'
def _crop_relief():  # square crop around the land, with a sea margin
    from PIL import Image, ImageChops
    im = Image.open(ROOT / 'output' / CFG['id'] / 'relief.png').convert('RGB')
    sea = Image.new('RGB', im.size, (69, 124, 150))
    box = ImageChops.difference(im, sea).convert('L').point(lambda v: 255 if v > 24 else 0).getbbox()
    x0, y0, x1, y1 = box; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; half = max(x1 - x0, y1 - y0) / 2 * 1.12
    half = min(half, cx, cy, im.size[0] - cx, im.size[1] - cy)
    im.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half))).resize((1500, 1500)).save(RELIEF)
_crop_relief()
LOGO = ROOT / 'assets' / 'tf3-logo.png'
FONTS = ROOT / 'assets' / 'fonts'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CSS = f"""
@font-face{{font-family:Literata;src:url('file://{FONTS}/Literata.ttf')}}
@font-face{{font-family:Manrope;src:url('file://{FONTS}/Manrope.ttf')}}
@font-face{{font-family:Mono;src:url('file://{FONTS}/JetBrainsMono.ttf')}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1920px;height:1080px;overflow:hidden;position:relative;background:#14130f;font-family:Manrope;color:#F3F0E8}}
.bg{{position:absolute;inset:0;background-size:cover;background-position:var(--pos,center)}}
.shade{{position:absolute;inset:0}}
.mark{{position:absolute;right:72px;bottom:56px;font:800 38px Manrope;letter-spacing:-.04em}}.mark i{{color:#E0603C;font-style:normal}}
.eyebrow{{display:inline-block;font:700 26px Mono;letter-spacing:.12em;text-transform:uppercase;color:#14130f;background:#F3F0E8;padding:10px 18px;border-radius:6px}}
h1{{font:800 124px/0.95 Manrope;letter-spacing:-.055em}}
.sub{{font:500 44px/1.25 Manrope;letter-spacing:-.01em;opacity:.94;max-width:740px}}
.chips{{display:flex;gap:16px;flex-wrap:wrap}}
.chip{{font:700 28px Manrope;padding:14px 24px;border-radius:999px;background:rgba(243,240,232,.14);border:2px solid rgba(243,240,232,.38)}}
.left{{position:absolute;left:84px;top:84px;bottom:96px;display:flex;flex-direction:column;justify-content:space-between;width:900px}}
.cap{{position:absolute;left:0;right:0;bottom:0;padding:130px 84px 64px;background:linear-gradient(0deg,rgba(14,13,10,.92),rgba(14,13,10,0))}}
.cap .k{{font:700 24px Mono;letter-spacing:.14em;text-transform:uppercase;color:#F6A17E}}
.cap .t{{font:700 84px/1.05 Literata;letter-spacing:-.02em;margin-top:8px}}
.cap .d{{font:500 36px Manrope;opacity:.92;margin-top:10px}}
"""
def page(name, body, bg=None, pos='center', shade=None, extra=''):
    bgd = f'<div class="bg" style="background-image:url(\'file://{bg}\');--pos:{pos}"></div>' if bg else ''
    sh = f'<div class="shade" style="background:{shade}"></div>' if shade else ''
    f = OUT / f'{name}.html'
    f.write_text(f'<!doctype html><meta charset=utf-8><style>{CSS}{extra}</style><body>{bgd}{sh}{body}<div class="mark">Aimantas<i>.</i></div></body>')
    out = OUT / f'{name}.png'
    for attempt in range(4):
      r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1', f'--screenshot={out}',
                    '--window-size=1920,1080', '--virtual-time-budget=4000', f'file://{f}'], capture_output=True)
      if r.returncode == 0 and out.exists(): break
      import time; time.sleep(3)
    else: raise SystemExit('chrome failed for ' + name)
if isinstance(CFG['flag'], str) and CFG['flag'].startswith('cross:'):
    col = CFG['flag'].split(':')[1]
    FLAG = f'<div style="width:114px;height:114px;border-radius:12px;overflow:hidden;position:relative;background:{col};box-shadow:0 14px 34px rgba(0,0,0,.55);border:2px solid rgba(243,240,232,.5)"><div style="position:absolute;left:46px;top:20px;width:22px;height:74px;background:#fff"></div><div style="position:absolute;left:20px;top:46px;width:74px;height:22px;background:#fff"></div></div>'
else:
    c1, c2, c3 = CFG['flag']
    FLAG = f'<div style="width:190px;height:114px;border-radius:12px;overflow:hidden;box-shadow:0 14px 34px rgba(0,0,0,.55);border:2px solid rgba(243,240,232,.5);display:flex;flex-direction:column"><div style="flex:1;background:{c1}"></div><div style="flex:1;background:{c2}"></div><div style="flex:1;background:{c3}"></div></div>'
chips = ''.join(f'<span class="chip">{x}</span>' for x in CFG['chips'])
page('0-cover', f'''<div style="position:absolute;right:36px;top:40px;width:1000px;height:1000px;background:url('file://{RELIEF}') center/cover;border-radius:50%;box-shadow:0 0 0 3px rgba(243,240,232,.25),0 60px 120px -20px rgba(0,0,0,.7)"></div>
<div class="left"><div style="display:flex;align-items:center;gap:28px"><img src="file://{LOGO}" style="height:128px"><span class="eyebrow">Map</span></div>
<div>{FLAG}<h1 style="margin-top:34px">{CFG['title']}</h1><p class="sub" style="margin-top:22px">{CFG['tagline']}</p></div><div class="chips">{chips}</div></div>''',
     bg=SH / f"{CFG['cover_bg']}.png", shade='linear-gradient(90deg,rgba(14,13,10,.97) 0%,rgba(14,13,10,.94) 45%,rgba(14,13,10,.85) 100%)')
page('1-relief', f'''<div style="position:absolute;left:0;top:0;width:1080px;height:1080px;background:url('file://{RELIEF}') center/cover"></div>
<div style="position:absolute;left:36px;bottom:36px;font:700 24px Mono;letter-spacing:.1em;text-transform:uppercase;background:#24231F;color:#F3F0E8;padding:10px 16px;border-radius:6px">Data render · not in-game</div>
<div style="position:absolute;left:1080px;top:0;bottom:0;right:0;background:#24231F;padding:96px 84px;display:flex;flex-direction:column;justify-content:center;gap:34px">
<span class="eyebrow" style="align-self:flex-start">The whole country</span>
<div style="font:700 84px/1.05 Literata;letter-spacing:-.02em">Built from real data</div>
<div style="font:500 34px/1.4 Manrope;opacity:.9">Elevation tiles, OpenStreetMap towns and rivers, squeezed into one Very Large map. The coast follows the national border, so it plays as an island.</div>
<div class="chips"><span class="chip">{CFG['towns']} towns</span><span class="chip">{CFG['english']}</span></div></div>''')
for i, g in enumerate(CFG['gallery'], 2):
    page(f"{i}-{g['file']}", f'<div class="cap"><div class="k">{g["kicker"]}</div><div class="t">{g["title"]}</div><div class="d">{g["desc"]}</div></div>', bg=SH / f"{g['file']}.png", pos=g.get('pos', 'center'))
print('rendered', sorted(p.name for p in OUT.glob('*.png')))
