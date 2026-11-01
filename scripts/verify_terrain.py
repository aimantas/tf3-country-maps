"""Print expected terrain heights (from the heightmap) at sample game coordinates as JSON, for the bridge check. Usage: verify_terrain.py <id>"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
O = Path(__file__).resolve().parents[1] / 'output' / sys.argv[1]
m = json.loads((O / 'map-settings.json').read_text())
a = np.asarray(Image.open(next(O.glob('*_4097_playable.png')))) / 65535 * (m['height_import_max'] - m['height_import_min']) + m['height_import_min']
pts = [(0, 0), (3000, 2000), (-3000, -2000), (-6000, 5000), (6000, -5000), (1500, -6500), (-4500, 3500), (7000, 7000), (-7000, -7000), (2500, 4500)]
out = []
for x, y in pts:
    px, py = round((x / 16384 + .5) * 4096), round((.5 - y / 16384) * 4096); out.append([x, y, round(float(a[py, px]), 2)])
print(json.dumps(out))
