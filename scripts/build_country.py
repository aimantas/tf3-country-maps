"""Build a Transport Fever 3 country island kit (heightmap, town and industry presets) from open geodata.

Usage: python3 scripts/build_country.py <config id>
Inputs: configs/<id>.json, data/ (Natural Earth outline, rivers, lakes; OSM places in data/osm/<ISO2>.json),
        AWS Terrain Tiles fetched on demand into data/tiles.
Outputs: output/<id>/ ...
"""
import io, json, math, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import requests
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy.ndimage import map_coordinates, gaussian_filter, distance_transform_edt
from shapely.geometry import shape, Point
from shapely.ops import transform

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'configs' / f'{sys.argv[1]}.json').read_text())
DATA = ROOT / 'data'
OUT = ROOT / 'output' / CFG['id']
OUT.mkdir(parents=True, exist_ok=True)
PIXELS, GAME = 4097, 16384
REAL = CFG['real_m']
MIN_H, MAX_H = -12.0, 180.0
ZOOM = CFG.get('zoom', 9)
STEM = CFG['stem']
TO_PROJ = Transformer.from_crs(4326, CFG['crs'], always_xy=True)
TO_LONLAT = Transformer.from_crs(CFG['crs'], 4326, always_xy=True)

def lua(v):
    if isinstance(v, str): return '"' + ''.join('\\%03d' % b for b in v.encode('utf-8')) + '"'
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, (int, float)): return str(v)
    if isinstance(v, list): return '{' + ','.join(lua(x) for x in v) + '}'
    if isinstance(v, dict): return '{' + ','.join('[' + lua(k) + ']=' + lua(x) for k, x in v.items()) + '}'
    raise TypeError(v)

countries = json.loads((DATA / 'countries.geojson').read_text())
country = next(f for f in countries['features'] if f['properties']['ADM0_A3'] == CFG['iso'])
border_ll = shape(country['geometry'])
border = transform(TO_PROJ.transform, border_ll)
x0, y0, x1, y1 = border.bounds
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
west, south, east, north = cx - REAL / 2, cy - REAL / 2, cx + REAL / 2, cy + REAL / 2
assert x1 - x0 < REAL * .97 and y1 - y0 < REAL * .97, f'country does not fit the square ({x1-x0:.0f} x {y1-y0:.0f} m)'

def pixel(lon, lat):
    x, y = TO_PROJ.transform(lon, lat)
    return (x - west) / REAL * (PIXELS - 1), (north - y) / REAL * (PIXELS - 1)

def slippy(lon, lat):
    n = 2 ** ZOOM
    return (lon + 180) / 360 * n, (1 - np.arcsinh(np.tan(np.deg2rad(lat))) / np.pi) / 2 * n

print('terrain tiles...', flush=True)
xx, yy = np.meshgrid(np.linspace(west, east, PIXELS, dtype='float32'), np.linspace(north, south, PIXELS, dtype='float32'))
lon, lat = TO_LONLAT.transform(xx, yy)
sx, sy = slippy(lon, lat)
tx0, tx1, ty0, ty1 = int(np.floor(sx.min())), int(np.floor(sx.max())), int(np.floor(sy.min())), int(np.floor(sy.max()))
cache = DATA / 'tiles'; cache.mkdir(exist_ok=True)
tile_ids = [(x, y) for y in range(ty0, ty1 + 1) for x in range(tx0, tx1 + 1)]

def tile(item):
    x, y = item
    f = cache / f'{ZOOM}-{x}-{y}.png'
    if not f.exists():
        url = f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{ZOOM}/{x}/{y}.png'
        for attempt in range(4):
            try:
                r = requests.get(url, timeout=25); r.raise_for_status()
                assert Image.open(io.BytesIO(r.content)).size == (256, 256)
                f.write_bytes(r.content); break
            except Exception as e:
                last = e; time.sleep(attempt + 1)
        else: raise last
    a = np.asarray(Image.open(f).convert('RGB'), dtype='float32')
    return x, y, a[:, :, 0] * 256 + a[:, :, 1] + a[:, :, 2] / 256 - 32768

mosaic = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), dtype='float32')
with ThreadPoolExecutor(max_workers=8) as pool:
    for i, (x, y, a) in enumerate(pool.map(tile, tile_ids), 1):
        mosaic[(y - ty0) * 256:(y - ty0 + 1) * 256, (x - tx0) * 256:(x - tx0 + 1) * 256] = a
        if i % 40 == 0: print(f'  tiles {i}/{len(tile_ids)}', flush=True)
dem = map_coordinates(mosaic, [(sy - ty0) * 256 - .5, (sx - tx0) * 256 - .5], order=1, mode='nearest').astype('float32')
del xx, yy, lon, lat, sx, sy, mosaic

# Border mask: land inside the national outline, shelf outside.
outline = Image.new('L', (PIXELS, PIXELS)); od = ImageDraw.Draw(outline)
def bp(x, y): return ((x - west) / REAL * (PIXELS - 1), (north - y) / REAL * (PIXELS - 1))
for poly in (list(border.geoms) if border.geom_type == 'MultiPolygon' else [border]):
    od.polygon([bp(x, y) for x, y in poly.exterior.coords], fill=255)
    for ring in poly.interiors: od.polygon([bp(x, y) for x, y in ring.coords], fill=0)
island = np.asarray(outline) > 0

# Compress relief softly so lowlands keep character and the highest peaks fit the 180 m range.
e = gaussian_filter(dem, 1.1)
land = 1.0 + (MAX_H - 1.0) * (1 - np.exp(-np.maximum(e, 0) / CFG['height_scale']))
natural = np.where(island, np.maximum(land, 1.0), np.clip(e * .5, MIN_H, 0)).astype('float32')

# Rivers and lakes carved to the shared sea level.
water_img = Image.new('L', (PIXELS, PIXELS)); wd = ImageDraw.Draw(water_img)
used = set()
for f in json.loads((DATA / 'rivers.geojson').read_text())['features']:
    nm = f['properties'].get('name') or ''
    if nm not in CFG['rivers']: continue
    g = shape(f['geometry'])
    if not g.intersects(border_ll): continue
    for line in (list(g.geoms) if g.geom_type == 'MultiLineString' else [g]):
        wd.line([pixel(x, y) for x, y, *_ in line.coords], fill=255, width=10 if nm in CFG['big_rivers'] else 6)
    used.add(nm)
for f in json.loads((DATA / 'lakes.geojson').read_text())['features']:
    nm = f['properties'].get('name') or ''
    if nm not in CFG['lakes']: continue
    g = shape(f['geometry'])
    for poly in (list(g.geoms) if g.geom_type == 'MultiPolygon' else [g]):
        wd.polygon([pixel(x, y) for x, y, *_ in poly.exterior.coords], fill=255)
    used.add(nm)
water = (np.asarray(water_img) > 0) & island
d = distance_transform_edt(~water)
wgt = np.exp(-(d / 14) ** 2).astype('float32')
playable = natural * (1 - wgt) + (-3.0) * wgt
playable[water] = -3
inside = distance_transform_edt(island); outside = distance_transform_edt(~island)
playable = np.where(island, np.minimum(playable, np.where(water, -3, inside * .9 + 1)), -np.clip(outside * .5, .5, 12)).astype('float32')
del d, wgt, inside, outside

# Towns: biggest OSM places inside the border, spaced for the game scale, on dry sites.
def pop_of(el):
    p = el['tags'].get('population', '').replace(',', '').replace('.', '').replace(' ', '')
    return int(p) if p.isdigit() else 0
places = []
for el in json.loads((DATA / 'osm' / f"{CFG['iso2']}.json").read_text())['elements']:
    lo, la = el.get('lon', el.get('center', {}).get('lon')), el.get('lat', el.get('center', {}).get('lat'))
    if lo is None or not el['tags'].get('name') or not border_ll.contains(Point(lo, la)): continue
    p = pop_of(el)
    if p > 0: places.append((p, el, lo, la))
places.sort(key=lambda t: -t[0])
land_dist = distance_transform_edt(playable > 0)
towns, records = [], []
def gxy(px, py): return (px / (PIXELS - 1) - .5) * GAME, (.5 - py / (PIXELS - 1)) * GAME
for p, el, lo, la in places:
    if len(towns) >= CFG['towns']: break
    px, py = (round(v) for v in pixel(lo, la))
    ox, oy = px, py
    cand = [(dx * dx + dy * dy, px + dx, py + dy) for dy in range(-36, 37, 4) for dx in range(-36, 37, 4)
            if 0 <= px + dx < PIXELS and 0 <= py + dy < PIXELS and playable[py + dy, px + dx] > 3 and land_dist[py + dy, px + dx] > 10]
    if not cand: continue
    _, px, py = min(cand)
    x, y = gxy(px, py)
    if any(math.hypot(x - t['position']['x'], y - t['position']['y']) < CFG['min_game_spacing'] for t in towns): continue
    cap = max(CFG['min_capacity'], round(p / CFG['pop_divisor']))
    name = el['tags']['name']
    towns.append({'name': name, 'position': {'x': round(x, 2), 'y': round(y, 2)}, 'sizeFactors': [cap / 100] * 3,
                  'initialLandUseCapacities': [cap] * 3,
                  'landUse2CargoNeedsCategories': {'com': [['vegetables', 1]], 'ind': [['planks', 1]]}})
    records.append({'name': name, 'osm_id': el['id'], 'lon': lo, 'lat': la, 'x': x, 'y': y, 'game_offset_m': round(math.hypot(px - ox, py - oy) * 4, 1),
                    'population_reference': p, 'population_date': el['tags'].get('population:date', 'unknown'), 'starting_capacities': [cap] * 3})
    r = 24; patch = playable[py - r:py + r + 1, px - r:px + r + 1]; gy, gx = np.mgrid[-r:r + 1, -r:r + 1]
    blend = np.clip((r - np.hypot(gx, gy)) / 12, 0, 1).astype('float32'); blend[patch <= 0] = 0
    level = float(np.median(patch[patch > 0])); patch[:] = patch * (1 - blend) + level * blend
assert len(towns) >= CFG['towns'] * .9, f'only {len(towns)} towns placed'

# Industries: clusters of working chains placed around anchors (game design, not real businesses).
def px_of(x, y): return round((x / GAME + .5) * (PIXELS - 1)), round((.5 - y / GAME) * (PIXELS - 1))
def far_apart(points, k, first):
    chosen = [first]
    while len(chosen) < k:
        best = max(points, key=lambda p: min(math.hypot(p[0] - c[0], p[1] - c[1]) for c in chosen))
        chosen.append(best)
    return chosen
industries = []
def free(wx, wy):
    px, py = px_of(wx, wy)
    if not (60 < px < PIXELS - 60 and 60 < py < PIXELS - 60): return False
    patch = playable[py - 4:py + 5, px - 4:px + 5]
    return (playable[py, px] > 3 and land_dist[py, px] > 20 and np.ptp(patch) < 9
            and all(math.hypot(wx - t['position']['x'], wy - t['position']['y']) > 150 for t in towns)
            and all(math.hypot(wx - i['position']['x'], wy - i['position']['y']) > 140 for i in industries))
def place(kind, ax, ay, rmin=250, rmax=900):
    for r in range(rmin, rmax, 40):
        for k in range(16):
            a = (k * 137.5) % 360 * math.pi / 180
            wx, wy = ax + r * math.cos(a), ay + r * math.sin(a)
            if free(wx, wy):
                industries.append({'position': {'x': round(wx, 2), 'y': round(wy, 2)}, 'angle': 0, 'onWater': False, 'fileName': f'::/industries/{kind}/{kind}.con', 'tag': kind})
                return True
    return False
mid = [(t['position']['x'], t['position']['y']) for t in towns[5:]]
agri = far_apart(mid, 5, mid[len(mid) // 2])
hi = [(gxy(px, py)) for py in range(200, PIXELS - 200, 80) for px in range(200, PIXELS - 200, 80)
      if island[py, px] and natural[py, px] > 70 and land_dist[py, px] > 40 and playable[py, px] > 3]
hills = far_apart(hi, 3, max(hi, key=lambda p: -abs(p[0]) - abs(p[1]))) if hi else []
chains = [(a, ['farm', 'farm', 'food_factory', 'brewery']) for a in agri] + [(h, ['forest', 'forest', 'saw_mill', 'furniture_factory']) for h in hills]
for tt, kinds in ((towns[1], ['forest', 'paper_mill']), (towns[2], ['forest', 'printing_press'])):
    chains.append(((tt['position']['x'], tt['position']['y']), kinds))
for (ax, ay), kinds in chains:
    for kind in kinds:
        if not place(kind, ax, ay): place(kind, ax, ay, 700, 1800)
industries = [i for i in industries if not any(math.hypot(i['position']['x'] - x, i['position']['y'] - y) < 5 for x, y in CFG.get('drop_industries', []))]  # sites the game refused during the live import
assert len(industries) >= 30, f'only {len(industries)} industries placed'

def write_height(name, h):
    px = np.round((np.clip(h, MIN_H, MAX_H) - MIN_H) / (MAX_H - MIN_H) * 65535).astype('uint16')
    Image.fromarray(px).save(OUT / name); assert Image.open(OUT / name).size == (PIXELS, PIXELS)
write_height(f'{STEM}_4097_playable.png', playable)
np.save(OUT / 'preview-height.npy', playable[::4, ::4])
(OUT / f'{STEM}_{len(towns)}_towns.lua').write_text('function data()\nreturn ' + lua({'towns': towns, 'industries': []}) + '\nend\n')
(OUT / f'{STEM}_{len(towns)}_towns_starter_industries.lua').write_text('function data()\nreturn ' + lua({'towns': towns, 'industries': industries}) + '\nend\n')
(OUT / 'towns.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
(OUT / 'industries.json').write_text(json.dumps(industries, ensure_ascii=False, indent=2))
(OUT / 'border.geojson').write_text(json.dumps(country, ensure_ascii=False))
manifest = {'name': STEM, 'english': CFG['english'], 'pixels': PIXELS, 'game_size_m': GAME, 'real_coverage_m': REAL, 'crs': f"EPSG:{CFG['crs']}",
            'bounds': [west, south, east, north], 'height_import_min': MIN_H, 'height_import_max': MAX_H, 'water_level': 0,
            'horizontal_compression': REAL / GAME, 'height_scale_m': CFG['height_scale'], 'source_zoom': ZOOM, 'source_tiles': len(tile_ids),
            'towns': len(towns), 'industries': len(industries), 'waterways': sorted(used), 'population_divisor': CFG['pop_divisor'],
            'minimum_residential_capacity': CFG['min_capacity'], 'height_range_playable': [float(playable.min()), float(playable.max())],
            'population_source': 'OpenStreetMap population tags; mixed or unknown dates; approximate relative sizes, not census counts.',
            'caveat': 'Fictional island following the national border. Relief compressed, rivers widened and lowered to sea level. Industry sites are game design.'}
(OUT / 'map-settings.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps({k: manifest[k] for k in ['towns', 'industries', 'waterways', 'height_range_playable', 'horizontal_compression']}, indent=1))
print('biggest:', [(t['name'], t['initialLandUseCapacities'][0]) for t in towns[:8]])
