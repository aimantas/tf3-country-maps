"""Render a data preview (relief, outline, towns). Not an in-game image. Usage: preview_country.py <id>"""
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, LinearSegmentedColormap
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'configs' / f'{sys.argv[1]}.json').read_text())
OUT = ROOT / 'output' / CFG['id']
meta = json.loads((OUT / 'map-settings.json').read_text())
h = np.load(OUT / 'preview-height.npy')
towns = json.loads((OUT / 'towns.json').read_text())
inds = json.loads((OUT / 'industries.json').read_text())
cmap = LinearSegmentedColormap.from_list('land', ['#bdcaa5', '#a8b78d', '#d7cca5', '#c0ae87', '#e3d9c2'])
rgb = LightSource(azdeg=310, altdeg=45).shade(np.maximum(h, 0), cmap, vert_exag=.7, dx=16, dy=16, blend_mode='soft')
rgb[h < 0] = [.27, .49, .59, 1]
fig, ax = plt.subplots(figsize=(12, 12), dpi=125)
fig.patch.set_facecolor('#457c96')
ax.imshow(rgb, extent=[-8192, 8192, -8192, 8192])
west, south, east, north = meta['bounds']
tr = Transformer.from_crs(4326, int(meta['crs'].split(':')[1]), always_xy=True)
cx, cy, real = (west + east) / 2, (south + north) / 2, meta['real_coverage_m']
def conv(x, y, z=None):
    x, y = tr.transform(x, y); return (np.asarray(x) - cx) / real * 16384, (np.asarray(y) - cy) / real * 16384
border = transform(conv, shape(json.loads((OUT / 'border.geojson').read_text())['geometry']))
for p in (list(border.geoms) if border.geom_type == 'MultiPolygon' else [border]):
    x, y = p.exterior.xy; ax.plot(x, y, color='#faf8ee', lw=1.4, alpha=.95)
for i, t in enumerate(towns):
    big = i < CFG['major_labels']
    ax.scatter(t['x'], t['y'], s=26 if big else 8, color='#173126', edgecolor='#fff8e8', linewidth=.8, zorder=4)
    if big:
        ax.annotate(t['name'], (t['x'], t['y']), xytext=(6, 5), textcoords='offset points', fontsize=9, color='#10261f',
                    bbox=dict(boxstyle='round,pad=.15', fc='#f6f1df', ec='none', alpha=.85), zorder=5)
ax.set_xlim(-8192, 8192); ax.set_ylim(-8192, 8192); ax.axis('off')
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
fig.savefig(OUT / 'relief.png', facecolor=fig.get_facecolor())
print(OUT / 'relief.png')
