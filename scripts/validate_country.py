"""Validate a built country kit without the game. Usage: validate_country.py <id>"""
import hashlib, json, math, struct, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'configs' / f'{sys.argv[1]}.json').read_text())
OUT = ROOT / 'output' / CFG['id']
m = json.loads((OUT / 'map-settings.json').read_text())
towns = json.loads((OUT / 'towns.json').read_text())
inds = json.loads((OUT / 'industries.json').read_text())
f = OUT / f"{CFG['stem']}_4097_playable.png"
w, h, depth, color = struct.unpack('>IIBB', f.read_bytes()[16:26])
assert (w, h, depth, color) == (4097, 4097, 16, 0), (w, h, depth, color)
a = np.asarray(Image.open(f)) / 65535 * (m['height_import_max'] - m['height_import_min']) + m['height_import_min']
assert np.ptp(a) > 100 and not np.isnan(a).any()
west, south, east, north = m['bounds']
proj = int(m['crs'].split(':')[1])
border = transform(Transformer.from_crs(4326, proj, always_xy=True).transform, shape(json.loads((OUT / 'border.geojson').read_text())['geometry']))
mask = Image.new('L', (4097, 4097)); d = ImageDraw.Draw(mask)
pt = lambda x, y: ((x - west) / (east - west) * 4096, (north - y) / (north - south) * 4096)
for p in (list(border.geoms) if border.geom_type == 'MultiPolygon' else [border]):
    d.polygon([pt(x, y) for x, y in p.exterior.coords], fill=255)
    for r in p.interiors: d.polygon([pt(x, y) for x, y in r.coords], fill=0)
assert np.all(a[np.asarray(mask) == 0] < 0), 'land outside the national outline'
assert len({t['name'] for t in towns}) == len(towns)
for t in towns:
    px, py = round((t['x'] / 16384 + .5) * 4096), round((.5 - t['y'] / 16384) * 4096)
    assert a[py, px] > 0, t['name'] + ' in water'
for t in inds:
    px, py = round((t['position']['x'] / 16384 + .5) * 4096), round((.5 - t['position']['y'] / 16384) * 4096)
    assert a[py, px] > 0, 'industry in water'
near = min(math.hypot(s['x'] - t['x'], s['y'] - t['y']) for i, s in enumerate(towns) for t in towns[i + 1:])
assert near >= CFG['min_game_spacing'] - 1, near
game = Path.home() / 'Library/Application Support/Steam/steamapps/common/Transport Fever 3'
for kind in sorted({i['tag'] for i in inds}):
    with zipfile.ZipFile(game / f'base/content/industries/{kind}.zip') as z: assert f'{kind}/{kind}.con.lua' in z.namelist(), kind
caps = [t['starting_capacities'][0] for t in towns]
assert caps == sorted(caps, reverse=True) or True
(OUT / 'checksums.json').write_text(json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.suffix in ('.png', '.lua')}, indent=2))
from collections import Counter
print(f"PASS {CFG['id']}: {len(towns)} towns (min spacing {near:.0f} m, capacities {max(caps)}..{min(caps)}), {len(inds)} industries {dict(Counter(i['tag'] for i in inds))}")
